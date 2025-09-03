"""Tests for RedisStore using fakeredis."""

from collections import deque

import fakeredis
import pytest
from pytest import MonkeyPatch

from app.models.chat import ConversationState, Message
from app.storage.redis_store import RedisStore


@pytest.fixture
def faux_redis(monkeypatch: MonkeyPatch) -> fakeredis.FakeRedis:
    """Patch redis.from_url to return a fakeredis instance."""
    m = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(
        "app.storage.redis_store.redis.from_url", lambda url, decode_responses=True: m
    )
    return m


def test_redis_store_roundtrip() -> None:
    """Test RedisStore set/get/exists/trim."""
    fake: fakeredis.FakeRedis = fakeredis.FakeRedis(decode_responses=True)
    store = RedisStore(url="redis://does-not-matter/0", client=fake, ttl_days=1)

    cid = "abc"
    history: deque[Message] = deque(
        [
            Message(role="user", message="hi"),
            Message(role="bot", message="hello"),
        ]
    )
    state = ConversationState(topic="t", stance="pro", thesis="th", history=history)

    store.set(cid, state)
    assert store.exists(cid)

    got = store.get(cid)
    assert got is not None and got.thesis == "th"

    store.trim(cid, max_per_side=1)
    trimmed = store.get(cid)
    assert trimmed is not None
    assert sum(1 for m in trimmed.history if m.role == "user") <= 1
    assert sum(1 for m in trimmed.history if m.role == "bot") <= 1
