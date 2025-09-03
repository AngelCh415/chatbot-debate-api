"""Initialization for storage backends."""

from __future__ import annotations

import os

from .base import BaseStore
from .memory import MemoryStore
from .redis_store import RedisStore


def get_store() -> BaseStore:
    """Factory to get the appropriate storage backend based on environment variables."""
    backend = (os.getenv("STORE_BACKEND") or "memory").lower()
    if backend == "redis":
        return RedisStore(
            url=os.getenv("REDIS_URL"),
            ttl_days=int(os.getenv("REDIS_TTL_DAYS", "7")),
        )
    return MemoryStore()
