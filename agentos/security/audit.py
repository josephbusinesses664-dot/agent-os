"""Audit Log.

Every significant action (who, what, when, why, project, task, tool, model,
result) is recorded and queryable. This is the traceability backbone.
"""

from __future__ import annotations

from typing import Any, Optional

from agentos.db.store import EntityStore
from agentos.domain.models import AuditEntry


class AuditLog:
    def __init__(self, store: EntityStore) -> None:
        self.store = store
        self._collection = "audit"

    async def record(self, actor: str, action: str, *, target: str = "",
                     project_id: Optional[str] = None, task_id: Optional[str] = None,
                     tool: Optional[str] = None, model: Optional[str] = None,
                     result: str = "ok", details: Optional[dict[str, Any]] = None) -> AuditEntry:
        entry = AuditEntry(actor=actor, action=action, target=target,
                           project_id=project_id, task_id=task_id, tool=tool,
                           model=model, result=result, details=details or {})
        await self.store.save(self._collection, entry)
        return entry

    async def query(self, limit: int = 200, *, actor: Optional[str] = None,
                    action: Optional[str] = None, project_id: Optional[str] = None,
                    tool: Optional[str] = None) -> list[AuditEntry]:
        entries = await self.store.list(self._collection, AuditEntry)
        if actor:
            entries = [e for e in entries if e.actor == actor]
        if action:
            entries = [e for e in entries if e.action == action]
        if project_id:
            entries = [e for e in entries if e.project_id == project_id]
        if tool:
            entries = [e for e in entries if e.tool == tool]
        entries.sort(key=lambda e: e.ts, reverse=True)
        return entries[:limit]