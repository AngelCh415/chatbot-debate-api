"""Tests for the in-memory store and history trimming."""

from app.core.store import ConversationState, MemoryStore, trim_history
from app.models.chat import Message


def test_store_get_set_exists() -> None:
    """Test the basic functionality of MemoryStore."""
    s = MemoryStore()
    cid = "abc"
    state = ConversationState(topic="t", stance="pro", thesis="th")
    assert s.get(cid) is None
    s.set(cid, state)
    assert s.get(cid) is state


def test_trim_history_caps_5_per_side_and_keeps_order() -> None:
    """Test that trim_history keeps at most 5 messages per role and preserves order."""
    msgs = []
    for i in range(6):
        msgs.append(Message(role="user", message=f"u{i}"))
        msgs.append(Message(role="bot", message=f"b{i}"))

    trimmed = trim_history(msgs, max_per_side=5)
    assert len(trimmed) == 10

    user_count = sum(1 for m in trimmed if m.role == "user")
    bot_count = sum(1 for m in trimmed if m.role == "bot")
    assert user_count == 5 and bot_count == 5
    assert trimmed[-2].role == "user"
    assert trimmed[-1].role == "bot"
