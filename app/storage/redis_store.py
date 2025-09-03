"""Redis-based storage backend for conversation states."""

from __future__ import annotations

import json
import os
from collections import deque
from datetime import timedelta
from typing import Any, cast

import redis  # type: ignore[import-untyped]

from app.models.chat import ConversationState, Message

from .base import BaseStore


class RedisStore(BaseStore):
    """Redis-backed store for conversation states."""

    def __init__(
        self,
        url: str | None = None,
        *,
        ttl_days: int = 7,
        client: redis.Redis | None = None,
    ) -> None:
        """Initialize the Redis store."""
        self.ttl_seconds = max(1, int(timedelta(days=ttl_days).total_seconds()))
        self.client = client or redis.from_url(
            url or os.getenv("REDIS_URL") or "redis://localhost:6379/0",
            decode_responses=True,
        )

    def _key(self, cid: str) -> str:
        """Generate the Redis key for a given conversation ID."""
        return f"conv:{cid}"

    # ---- helpers

    def _msg_to_dict(self, m: Any) -> dict[str, Any]:
        """Convert a Message or dict to a serializable dict."""
        if hasattr(m, "model_dump"):
            return cast(dict[str, Any], m.model_dump())  # pydantic v2
        if hasattr(m, "dict"):
            return cast(dict[str, Any], m.dict())  # pydantic v1
        if isinstance(m, dict):
            return m
        return {"role": getattr(m, "role", ""), "message": getattr(m, "message", "")}

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
                "history": getattr(st, "history", []),
            }
        hist = d.get("history", [])
        d["history"] = [self._msg_to_dict(m) for m in hist]
        return d

    def set(self, cid: str, payload: ConversationState | dict[str, Any]) -> None:
        """Set the conversation state for a given conversation ID."""
        data = self._to_dict(payload)
        self.client.setex(self._key(cid), self.ttl_seconds, json.dumps(data))

    def get(self, cid: str) -> ConversationState | None:
        """Get the conversation state for a given conversation ID."""
        raw = self.client.get(self._key(cid))
        if raw is None:
            return None
        data = cast(dict[str, Any], json.loads(raw))
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
        return bool(self.client.exists(self._key(cid)))

    def delete(self, cid: str) -> None:
        """Delete a conversation state by its ID."""
        self.client.delete(self._key(cid))

    def trim(self, cid: str, *, max_per_side: int = 5) -> ConversationState | None:
        """Trim the conversation history to keep messages per role."""
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
