"""Redis storage for conversation state/messages."""

from __future__ import annotations

import json
import os
from collections import deque
from collections.abc import Iterable
from datetime import timedelta
from typing import Any, cast

import redis  # type: ignore[import-untyped]

from app.models.chat import ConversationState, Message


class RedisStore:
    """Persist conversation state/messages in Redis."""

    def __init__(
        self,
        url: str | None = None,
        *,
        ttl_days: int = 7,
        client: redis.Redis | None = None,
    ) -> None:
        """Init RedisStore."""
        self.ttl_seconds = int(timedelta(days=ttl_days).total_seconds())
        self.client = client or redis.from_url(
            url or os.getenv("REDIS_URL") or "redis://localhost:6379/0",
            decode_responses=True,
        )

    def _key(self, cid: str) -> str:
        """Key for conversation ID."""
        return f"conv:{cid}"

    def _msg_to_dict(self, m: Any) -> dict[str, Any]:
        """Transform Message (pydantic v2/v1) or dict / clase simple a dict plano."""
        # Pydantic v2
        if hasattr(m, "model_dump"):
            return cast(dict[str, Any], m.model_dump())
        # Pydantic v1
        if hasattr(m, "dict"):
            return cast(dict[str, Any], m.dict())
        # Dict ya listo
        if isinstance(m, dict):
            return m
        # Clase simple
        return {"role": getattr(m, "role", ""), "message": getattr(m, "message", "")}

    def _history_to_dicts(self, history: Iterable[Any] | None) -> list[dict[str, Any]]:
        """Transform list/Deque of Message (pydantic v2/v1) or dict."""
        items = [] if history is None else list(history)
        return [self._msg_to_dict(m) for m in items]

    def _to_dict(self, payload: Any) -> dict[str, Any]:
        """Transform ConversationState (pydantic v2/v1) or dict."""
        # Pydantic v2
        if hasattr(payload, "model_dump"):
            d = cast(dict[str, Any], payload.model_dump())
            if "history" in d:
                d["history"] = self._history_to_dicts(
                    cast(Iterable[Any] | None, d.get("history"))
                )
            return d
        # Pydantic v1
        if hasattr(payload, "dict"):
            d = cast(dict[str, Any], payload.dict())
            if "history" in d:
                d["history"] = self._history_to_dicts(
                    cast(Iterable[Any] | None, d.get("history"))
                )
            return d
        if isinstance(payload, dict):
            d = dict(payload)
            if "history" in d and isinstance(d["history"], list):
                d["history"] = self._history_to_dicts(cast(list[Any], d["history"]))
            return d
        d2: dict[str, Any] = {
            "topic": getattr(payload, "topic", ""),
            "stance": getattr(payload, "stance", ""),
            "thesis": getattr(payload, "thesis", ""),
            "history": self._history_to_dicts(getattr(payload, "history", [])),
        }
        if not d2["topic"] and not d2["thesis"] and not d2["history"]:
            raise TypeError("payload must be ConversationState or dict", type(payload))
        return d2

    def set(self, cid: str, payload: Any) -> None:
        """Set conversation state/messages for cid."""
        data = self._to_dict(payload)
        self.client.setex(self._key(cid), self.ttl_seconds, json.dumps(data))

    def get(self, cid: str) -> ConversationState | None:
        """Get conversation state/messages for cid."""
        raw = self.client.get(self._key(cid))
        if raw is None:
            return None
        data = cast(dict[str, Any], json.loads(raw))

        history_items: list[Message] = []
        for m in data.get("history", []):
            if isinstance(m, Message):
                history_items.append(m)
            elif isinstance(m, dict):
                history_items.append(Message(**m))
        hist_deque: deque[Message] = deque(history_items)

        return ConversationState(
            topic=cast(str, data.get("topic", "")),
            stance=cast(str, data.get("stance", "")),
            thesis=cast(str, data.get("thesis", "")),
            history=hist_deque,
        )

    def exists(self, cid: str) -> bool:
        """Check if conversation state/messages exist for cid."""
        return bool(self.client.exists(self._key(cid)))

    def delete(self, cid: str) -> None:
        """Delete conversation state/messages for cid."""
        self.client.delete(self._key(cid))

    def trim(self, cid: str, *, max_per_side: int = 5) -> ConversationState | None:
        """Trim history to max_per_side user/bot messages each, keeping order."""
        state = self.get(cid)
        if state is None:
            return None

        items = list(state.history)
        users = [m for m in items if m.role == "user"]
        bots = [m for m in items if m.role == "bot"]

        users_kept = users[-max_per_side:]
        bots_kept = bots[-max_per_side:]
        kept_ids = {id(m) for m in users_kept + bots_kept}

        trimmed_list: list[Message] = [m for m in items if id(m) in kept_ids]
        u = b = 0
        final_list: list[Message] = []
        for m in trimmed_list:
            if m.role == "user":
                if u < max_per_side:
                    final_list.append(m)
                    u += 1
            else:
                if b < max_per_side:
                    final_list.append(m)
                    b += 1

        state.history = deque(final_list)
        self.set(cid, state)
        return state
