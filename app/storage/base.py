"""Base storage protocol for conversation states."""

from __future__ import annotations

from typing import Protocol

from app.models.chat import Message
from app.storage.memory import ConversationState


class Store(Protocol):
    """Protocol for conversation state storage."""

    def get(self, cid: str) -> ConversationState | None:
        """Return conversation by id or None if missing."""
        ...

    def set(self, cid: str, state: ConversationState) -> None:
        """Create or replace a conversation state."""
        ...

    def exists(self, cid: str) -> bool:
        """Return True if conversation id exists."""
        ...

    def append(self, cid: str, msg: Message) -> None:
        """Append a message to the conversation history."""
        ...

    def trim(self, cid: str, max_per_side: int = 5) -> None:
        """Trim the conversation history to at most `max_per_side` per role."""
        ...
