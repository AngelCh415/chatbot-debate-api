"""Memory-based storage implementation."""

from __future__ import annotations

from collections import deque
from typing import Any, cast

from app.models.chat import ConversationState, Message

from .base import BaseStore


class MemoryStore(BaseStore):
    """In-memory store — útil para desarrollo y tests."""

    def __init__(self) -> None:
        """Initialize the in-memory store."""
        self._db: dict[str, dict[str, Any]] = {}

    def _to_dict(self, st: ConversationState | dict[str, Any]) -> dict[str, Any]:
        """Convert ConversationState or dict to a serializable dict."""
        if isinstance(st, dict):
            d = dict(st)
        elif hasattr(st, "model_dump"):
            d = cast(dict[str, Any], st.model_dump())  # pydantic v2
        elif hasattr(st, "dict"):
            d = cast(dict[str, Any], st.dict())  # pydantic v1
        else:
            d = {
                "topic": getattr(st, "topic", ""),
                "stance": getattr(st, "stance", ""),
                "thesis": getattr(st, "thesis", ""),
                "history": [
                    {
                        "role": getattr(m, "role", ""),
                        "message": getattr(m, "message", ""),
                    }
                    for m in getattr(st, "history", [])
                ],
            }
        hist = d.get("history", [])
        d["history"] = [
            (
                h
                if isinstance(h, dict)
                else {
                    "role": getattr(h, "role", ""),
                    "message": getattr(h, "message", ""),
                }
            )
            for h in hist
        ]
        return d

    def set(self, cid: str, payload: ConversationState | dict[str, Any]) -> None:
        """Set the conversation state for a given conversation ID."""
        self._db[cid] = self._to_dict(payload)

    def get(self, cid: str) -> ConversationState | None:
        """Get the conversation state for a given conversation ID."""
        data = self._db.get(cid)
        if not data:
            return None
        hist: deque[Message] = deque(
            [
                Message(**m) if isinstance(m, dict) else m
                for m in data.get("history", [])
            ]
        )
        return ConversationState(
            topic=cast(str, data.get("topic", "")),
            stance=cast(str, data.get("stance", "")),
            thesis=cast(str, data.get("thesis", "")),
            history=hist,
        )

    def exists(self, cid: str) -> bool:
        """Check if a conversation ID exists in the store."""
        return cid in self._db

    def delete(self, cid: str) -> None:
        """Delete a conversation state by its ID."""
        self._db.pop(cid, None)

    def trim(self, cid: str, *, max_per_side: int = 5) -> ConversationState | None:
        """Trim the conversation history to keep at most messages per role."""
        state = self.get(cid)
        if state is None:
            return None

        items: list[Message] = list(state.history)
        keep: list[Message] = []
        count = {"user": 0, "bot": 0}

        for m in reversed(items):
            r = m.role
            if r in count and count[r] < max_per_side:
                keep.append(m)
                count[r] += 1

        keep.reverse()
        state.history = deque(keep)
        self.set(cid, state)
        return state
