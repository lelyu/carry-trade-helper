import asyncio
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CacheEntry:
    data: Any
    expires_at: float
    is_stale: bool = False


class InMemoryCache:
    def __init__(self, default_ttl: int = 3600):
        self._cache: dict[str, CacheEntry] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._default_ttl = default_ttl

    def _get_lock(self, key: str) -> asyncio.Lock:
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    def _is_expired(self, entry: CacheEntry) -> bool:
        return time.time() > entry.expires_at

    def get(self, key: str) -> CacheEntry | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        if self._is_expired(entry):
            entry.is_stale = True
            return entry
        return entry

    def set(self, key: str, data: Any, ttl: int | None = None) -> None:
        ttl = ttl if ttl is not None else self._default_ttl
        self._cache[key] = CacheEntry(
            data=data,
            expires_at=time.time() + ttl,
            is_stale=False,
        )

    async def get_or_fetch(
        self,
        key: str,
        fetcher: Any,
        ttl: int | None = None,
    ) -> tuple[Any, bool]:
        lock = self._get_lock(key)
        entry = self.get(key)

        if entry is not None and not entry.is_stale:
            return entry.data, False

        async with lock:
            entry = self.get(key)
            if entry is not None and not entry.is_stale:
                return entry.data, False

            data = await fetcher()
            self.set(key, data, ttl)
            return data, True


cache = InMemoryCache(default_ttl=3600)