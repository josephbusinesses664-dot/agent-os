"""In-memory implementations — used for tests, demos and offline mode."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Optional

from .base import KVStore, Queue, Repository


class MemoryRepository(Repository):
    def __init__(self) -> None:
        self._docs: dict[str, dict[str, dict]] = {}

    async def put(self, collection: str, key: str, doc: dict) -> None:
        self._docs.setdefault(collection, {})[key] = doc

    async def get(self, collection: str, key: str) -> Optional[dict]:
        return self._docs.get(collection, {}).get(key)

    async def delete(self, collection: str, key: str) -> None:
        self._docs.get(collection, {}).pop(key, None)

    async def query(self, collection: str, predicate: Optional[dict] = None) -> list[dict]:
        docs = list(self._docs.get(collection, {}).values())
        if predicate:
            docs = [d for d in docs if all(d.get(k) == v for k, v in predicate.items())]
        return docs

    async def count(self, collection: str, predicate: Optional[dict] = None) -> int:
        return len(await self.query(collection, predicate))

    async def health(self) -> bool:
        return True


class MemoryKV(KVStore):
    def __init__(self) -> None:
        self._data: dict[str, tuple[str, Optional[float]]] = {}

    async def get(self, key: str) -> Optional[str]:
        item = self._data.get(key)
        if not item:
            return None
        value, expires = item
        if expires is not None and time.monotonic() > expires:
            self._data.pop(key, None)
            return None
        return value

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        expires = time.monotonic() + ttl if ttl else None
        self._data[key] = (value, expires)

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)

    async def incr(self, key: str, amount: int = 1) -> int:
        current = await self.get(key)
        value = int(current) + amount if current else amount
        await self.set(key, str(value))
        return value

    async def expire(self, key: str, ttl: int) -> None:
        item = self._data.get(key)
        if item:
            self._data[key] = (item[0], time.monotonic() + ttl)

    async def health(self) -> bool:
        return True


class MemoryQueue(Queue):
    def __init__(self, maxsize: int = 10_000) -> None:
        self._q: asyncio.Queue = asyncio.Queue(maxsize=maxsize)

    async def enqueue(self, item: dict) -> None:
        await self._q.put(item)

    async def dequeue(self, timeout: float = 1.0) -> Optional[dict]:
        try:
            return await asyncio.wait_for(self._q.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def size(self) -> int:
        return self._q.qsize()