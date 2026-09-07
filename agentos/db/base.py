"""Storage abstractions.

`Repository` is a document store: every aggregate is stored as a JSON dict
under a (collection, key). This keeps the domain logic storage-agnostic —
swap the in-memory store for PostgreSQL (or anything else) without touching
business code.

`KVStore` is a small key/value store used for caching and counters.
`Queue` is a FIFO queue used for task distribution.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

COLLECTIONS = (
    "agents",
    "agent_instances",
    "tasks",
    "projects",
    "skills",
    "tools",
    "mcp",
    "models",
    "usage",
    "events",
    "audit",
    "memory",
    "memory_links",
    "approvals",
    "budgets",
    "messages",
    "decisions",
    "evaluations",
    "eval_runs",
    "performance",
    "traces",
    "workflows",
)


class Repository(ABC):
    """Document store contract."""

    @abstractmethod
    async def put(self, collection: str, key: str, doc: dict) -> None:
        """Insert or replace a document."""

    @abstractmethod
    async def get(self, collection: str, key: str) -> Optional[dict]:
        """Fetch a document or None."""

    @abstractmethod
    async def delete(self, collection: str, key: str) -> None:
        """Remove a document."""

    @abstractmethod
    async def query(self, collection: str, predicate: Optional[dict] = None) -> list[dict]:
        """List documents; equality-filtered by predicate (empty = all)."""

    @abstractmethod
    async def count(self, collection: str, predicate: Optional[dict] = None) -> int:
        ...

    @abstractmethod
    async def health(self) -> bool:
        ...


class KVStore(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[str]: ...

    @abstractmethod
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def incr(self, key: str, amount: int = 1) -> int: ...

    @abstractmethod
    async def expire(self, key: str, ttl: int) -> None: ...

    @abstractmethod
    async def health(self) -> bool: ...


class Queue(ABC):
    @abstractmethod
    async def enqueue(self, item: dict) -> None: ...

    @abstractmethod
    async def dequeue(self, timeout: float = 1.0) -> Optional[dict]: ...

    @abstractmethod
    async def size(self) -> int: ...