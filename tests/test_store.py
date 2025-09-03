"""Unit tests for RedisStore using fakeredis."""

from __future__ import annotations

from collections import deque
from typing import cast

import fakeredis
import pytest

from app.models.chat import ConversationState, Message
from app.storage.redis_store import RedisStore


@pytest.fixture()
def fake_client() -> fakeredis.FakeRedis:
    """Create a fakeredis client instance."""
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture()
def store(fake_client: fakeredis.FakeRedis) -> RedisStore:
    """Create a RedisStore instance using the fakeredis client."""
    return RedisStore(url="redis://does-not-matter/0", client=fake_client, ttl_days=1)


def test_get_nonexistent_returns_none(store: RedisStore) -> None:
    """Getting a non-existent conversation ID should return None."""
    assert store.get("nope") is None
    assert store.exists("nope") is False


def test_set_get_roundtrip(store: RedisStore, fake_client: fakeredis.FakeRedis) -> None:
    """Setting and then getting a conversation state should return the same data."""
    cid = "abc"
    history: deque[Message] = deque(
        [Message(role="user", message="hi"), Message(role="bot", message="hello")]
    )
    state = ConversationState(topic="t", stance="pro", thesis="th", history=history)

    store.set(cid, state)
    assert store.exists(cid) is True

    got = store.get(cid)
    assert got is not None
    assert got.topic == "t"
    assert got.stance == "pro"
    assert got.thesis == "th"
    assert list(m.message for m in got.history) == ["hi", "hello"]

    key = f"conv:{cid}"
    ttl_val = cast(int, fake_client.ttl(key))
    assert ttl_val > 0


def test_exists_and_delete(store: RedisStore) -> None:
    """Test the exists and delete methods."""
    cid = "to-del"
    state = ConversationState(
        topic="t",
        stance="pro",
        thesis="th",
        history=deque([Message(role="user", message="x")]),
    )
    store.set(cid, state)
    assert store.exists(cid) is True

    store.delete(cid)
    assert store.exists(cid) is False
    assert store.get(cid) is None


def test_set_accepts_plain_dict(store: RedisStore) -> None:
    """The set method should accept a plain dict as payload."""
    cid = "dict-payload"
    payload = {
        "topic": "energy",
        "stance": "pro",
        "thesis": "nuclear is beneficial",
        "history": [
            {"role": "user", "message": "start"},
            {"role": "bot", "message": "ok"},
        ],
    }
    store.set(cid, payload)
    got = store.get(cid)
    assert got is not None
    assert got.topic == "energy"
    assert list((m.role, m.message) for m in got.history) == [
        ("user", "start"),
        ("bot", "ok"),
    ]


def test_trim_keeps_max_per_side_and_preserves_order(store: RedisStore) -> None:
    """The trim method should keep at most messages per role and preserve order."""
    cid = "trim-1"
    msgs = deque(
        [
            Message(role="user", message="u1"),
            Message(role="bot", message="b1"),
            Message(role="user", message="u2"),
            Message(role="bot", message="b2"),
            Message(role="user", message="u3"),
            Message(role="bot", message="b3"),
            Message(role="user", message="u4"),
            Message(role="bot", message="b4"),
        ]
    )
    state = ConversationState(topic="t", stance="s", thesis="th", history=msgs)
    store.set(cid, state)

    trimmed = store.trim(cid, max_per_side=2)
    assert trimmed is not None

    users = [m for m in trimmed.history if m.role == "user"]
    bots = [m for m in trimmed.history if m.role == "bot"]
    assert len(users) <= 2
    assert len(bots) <= 2

    assert [m.message for m in users] == ["u3", "u4"]
    assert [m.message for m in bots] == ["b3", "b4"]

    assert [m.message for m in trimmed.history] == ["u3", "b3", "u4", "b4"]

    again = store.get(cid)
    assert again is not None
    assert [m.message for m in again.history] == ["u3", "b3", "u4", "b4"]
