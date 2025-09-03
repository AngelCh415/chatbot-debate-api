"""In-memory conversation store and history utilities."""

from __future__ import annotations

from app.models.chat import ConversationState, Message


class MemoryStore:
    """Minimal in-memory store keyed by conversation_id."""

    def __init__(self) -> None:
        """Initialize an empty store."""
        self._data: dict[str, ConversationState] = {}

    def get(self, cid: str) -> ConversationState | None:
        """Return conversation by id or None if missing."""
        return self._data.get(cid)

    def set(self, cid: str, state: ConversationState) -> None:
        """Create or replace a conversation state."""
        self._data[cid] = state


def trim_history(messages: list[Message], max_per_side: int = 5) -> list[Message]:
    """Trim the history keeping at most `max_per_side` for each role.

    The function preserves chronological order, returning the most recent messages last.

    Args:
        messages (List[Message]): Full chronological history.
        max_per_side (int): Max messages to keep per role.

    Returns:
        List[Message]: Trimmed chronological history.
    """
    # Walk from the end to count recent messages per role.
    kept: list[Message] = []
    count_user = 0
    count_bot = 0

    for msg in reversed(messages):
        if msg.role == "user":
            if count_user < max_per_side:
                kept.append(msg)
                count_user += 1
        else:
            if count_bot < max_per_side:
                kept.append(msg)
                count_bot += 1

    kept.reverse()
    return kept
