"""Memory System.

Persistent memory at five levels: agent, project, org, user, task. PostgreSQL
is the durable store; recall is keyword/tag-based (vector search is only added
where it demonstrably helps — never vectorize everything blindly).

Agents must distinguish temporary context from durable memory: only entries
explicitly saved (decisions, lessons, preferences, important facts) persist.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from agentos.db.store import EntityStore
from agentos.domain.models import MemoryEntry, MemoryScope


class MemoryStore:
    def __init__(self, store: EntityStore) -> None:
        self.store = store
        self._collection = "memory"

    async def save(self, scope: MemoryScope | str, owner_id: str, content: str,
                   *, kind: str = "fact", importance: int = 3,
                   tags: Optional[list[str]] = None) -> MemoryEntry:
        entry = MemoryEntry(scope=MemoryScope(scope), owner_id=owner_id, kind=kind,
                            content=content, importance=max(1, min(5, importance)),
                            tags=tags or [])
        await self.store.save(self._collection, entry)
        return entry

    async def recall(self, scope: MemoryScope | str, owner_id: str,
                     query: Optional[str] = None, limit: int = 10) -> list[MemoryEntry]:
        entries = await self.store.list(
            self._collection, MemoryEntry,
            predicate={"scope": MemoryScope(scope).value, "owner_id": owner_id},
        )
        if query:
            terms = {t for t in query.lower().split() if len(t) > 2}
            scored: list[tuple[MemoryEntry, int]] = []
            for e in entries:
                haystack = f"{e.content} {' '.join(e.tags)} {e.kind}".lower()
                score = sum(1 for t in terms if t in haystack)
                if score:
                    scored.append((e, score))
            scored.sort(key=lambda pair: (pair[1], pair[0].importance), reverse=True)
            entries = [e for e, _ in scored]
        else:
            entries.sort(key=lambda e: (e.importance, e.updated_at), reverse=True)
        return entries[:limit]

    async def delete(self, memory_id: str) -> None:
        await self.store.delete(self._collection, memory_id)

    async def all(self, limit: int = 200) -> list[MemoryEntry]:
        entries = await self.store.list(self._collection, MemoryEntry)
        entries.sort(key=lambda e: e.updated_at, reverse=True)
        return entries[:limit]

    async def remember_if_important(self, scope: MemoryScope | str, owner_id: str,
                                    content: str, importance: int) -> MemoryEntry | None:
        """Save only when importance warrants it (memory hygiene rule)."""
        if importance < 2:
            return None
        return await self.save(scope, owner_id, content, importance=importance)