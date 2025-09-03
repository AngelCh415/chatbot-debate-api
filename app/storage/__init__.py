"""Storage backend selection and initialization."""

import os
from typing import cast

from app.storage.base import Store
from app.storage.memory import MemoryStore
from app.storage.redis_store import RedisStore


def get_store() -> Store:
    """Return the configured storage backend."""
    backend = (os.getenv("STORE_BACKEND") or "memory").lower()
    if backend == "redis":
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        return cast(Store, RedisStore(url))
    return cast(Store, MemoryStore())
