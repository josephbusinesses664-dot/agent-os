"""Rollback / compensation ledger (Phase 14 of the master spec).

Tracks state-mutating actions with three honest classifications:

- reversible:    a compensation is recorded and can be executed
- compensating:  no true undo exists, but a compensation reduces harm
                 (e.g. publish a correction, disable a key, restore from
                 the last checkpoint)
- irreversible:  no compensation known — recorded so the system can gate
                 and warn BEFORE acting, not apologize after

The ledger never claims more than it knows: if a handler provides no
compensation, the action is classified irreversible, not silently assumed
reversible. Compensation handlers are named registry entries (idempotent,
safe to re-run). Secrets never enter the ledger (args are redacted).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from agentos.tools.executor import redact_args

logger = logging.getLogger("agentos.rollback")

# tools that mutate state outside the sandbox and therefore require entries
MUTATIVE_TOOLS = {"shell", "api.call", "mcp.call", "mattermost.post", "deploy",
                  "github", "docker", "filesystem.write", "file.patch"}

# tools whose writes stay inside the per-project workspace: rollback =
# deleting/patching the file it wrote (native undo exists)
SANDBOXED_TOOLS = {"filesystem.write", "file.patch"}


@dataclass
class RollbackEntry:
    entry_id: str
    tool: str
    args_redacted: dict
    agent_id: str = ""
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    reversibility: str = "irreversible"   # reversible | compensating | irreversible
    compensation_name: str = ""           # registered compensation handler
    compensation_args: dict = field(default_factory=dict)
    status: str = "active"                # active | rolled_back | failed
    rolled_back_at: str = ""
    note: str = ""


class RollbackLedger:
    """Records mutative actions and executes compensations."""

    def __init__(self, audit: Any = None, event_bus: Any = None) -> None:
        self._entries: dict[str, RollbackEntry] = {}
        self._order: list[str] = []
        self._compensations: dict[str, Any] = {}  # name -> async (entry) -> dict
        self.audit = audit
        self.event_bus = event_bus

    # -- compensation registry ------------------------------------------------
    def register_compensation(self, name: str, handler: Any) -> None:
        self._compensations[name] = handler

    def compensation_names(self) -> list[str]:
        return sorted(self._compensations)

    # -- recording --------------------------------------------------------------
    def record(self, *, tool: str, args: dict, agent_id: str = "",
               task_id: Optional[str] = None, project_id: Optional[str] = None,
               reversibility: Optional[str] = None,
               compensation_name: str = "",
               compensation_args: Optional[dict] = None,
               note: str = "") -> RollbackEntry:
        """Record one mutative action. Reversibility is explicit-or-worst:
        callers must classify honestly; unknown = irreversible."""
        entry_id = f"rb_{len(self._order) + 1:06d}_{tool.replace('.', '_')}"
        if reversibility is None:
            reversibility = "reversible" if compensation_name in self._compensations \
                else "irreversible"
        entry = RollbackEntry(
            entry_id=entry_id, tool=tool, args_redacted=redact_args(args or {}),
            agent_id=agent_id, task_id=task_id, project_id=project_id,
            reversibility=reversibility,
            compensation_name=compensation_name if reversibility in (
                "reversible", "compensating") else "",
            compensation_args=redact_args(compensation_args or {}),
            note=note)
        self._entries[entry_id] = entry
        self._order.append(entry_id)
        return entry

    # -- queries ------------------------------------------------------------------
    def get(self, entry_id: str) -> Optional[RollbackEntry]:
        return self._entries.get(entry_id)

    def active(self, project_id: Optional[str] = None) -> list[RollbackEntry]:
        out = [self._entries[i] for i in self._order
               if self._entries[i].status == "active"
               and (project_id is None or self._entries[i].project_id == project_id)]
        out.reverse()  # most recent first
        return out

    def stats(self) -> dict:
        by_rev = {"reversible": 0, "compensating": 0, "irreversible": 0}
        for e in self._entries.values():
            by_rev[e.reversibility] = by_rev.get(e.reversibility, 0) + 1
        return {"total": len(self._entries),
                "active": sum(1 for e in self._entries.values() if e.status == "active"),
                "rolled_back": sum(1 for e in self._entries.values() if e.status == "rolled_back"),
                "by_reversibility": by_rev}

    # -- compensation ----------------------------------------------------------------
    async def rollback(self, entry_id: str, *, operator: str = "system") -> dict:
        """Execute the recorded compensation for one entry (idempotent:
        already-rolled-back entries are no-ops)."""
        entry = self._entries.get(entry_id)
        if entry is None:
            return {"ok": False, "error": f"unknown rollback entry {entry_id}"}
        if entry.status == "rolled_back":
            return {"ok": True, "already_done": True, "entry_id": entry_id}
        if entry.status == "failed":
            return {"ok": False, "error": "prior rollback attempt failed; manual recovery required"}
        if not entry.compensation_name:
            return {"ok": False,
                    "error": f"action {entry.tool} is {entry.reversibility}; no compensation recorded"}
        handler = self._compensations.get(entry.compensation_name)
        if handler is None:
            return {"ok": False, "error": f"compensation {entry.compensation_name} not registered"}
        try:
            result = await handler(entry)
        except Exception as exc:  # noqa: BLE001
            entry.status = "failed"
            logger.warning("rollback %s failed: %s", entry_id, exc)
            await self._emit(entry, operator, ok=False, error=str(exc))
            return {"ok": False, "error": f"compensation failed: {exc}"}
        entry.status = "rolled_back"
        from datetime import datetime, timezone
        entry.rolled_back_at = datetime.now(timezone.utc).isoformat()
        await self._emit(entry, operator, ok=True)
        return {"ok": True, "entry_id": entry_id,
                "compensation": entry.compensation_name, "result": result}

    async def rollback_task(self, task_id: str, *, operator: str = "system") -> dict:
        """Roll back every active mutative action from one task, newest first.
        Stops at the first failure (ordered compensation)."""
        entries = [self._entries[i] for i in reversed(self._order)
                   if self._entries[i].task_id == task_id
                   and self._entries[i].status == "active"]
        results = []
        for e in entries:
            r = await self.rollback(e.entry_id, operator=operator)
            results.append({"entry": e.entry_id, "tool": e.tool, **r})
            if not r.get("ok") and not r.get("already_done"):
                break
        return {"ok": all(r.get("ok", False) or r.get("already_done") for r in results),
                "task_id": task_id, "count": len(results), "results": results}

    async def _emit(self, entry: RollbackEntry, operator: str, *, ok: bool,
                    error: str = "") -> None:
        if self.event_bus is not None:
            try:
                await self.event_bus.publish(
                    "action.rollback" if ok else "action.rollback_failed",
                    {"entry_id": entry.entry_id, "tool": entry.tool,
                     "operator": operator, "reversibility": entry.reversibility,
                     **({"error": error} if error else {})},
                    severity="info" if ok else "warning")
            except Exception:  # noqa: BLE001
                pass


# ---------------------------------------------------------------------------
# Built-in compensations for sandboxed writes (native undo exists)
# ---------------------------------------------------------------------------

async def compensate_filesystem_write(entry: RollbackEntry) -> dict:
    """Undo a workspace write: remove the file it created. The write's base
    directory is recorded at execution time (compensation_args['workspace']);
    relative paths are resolved against it, never against the rollback
    process's CWD. Confined to that recorded base."""
    from pathlib import Path
    raw = entry.args_redacted.get("path", "")
    if not raw:
        return {"ok": False, "error": "no path recorded"}
    base = Path(entry.compensation_args.get("workspace", "."))
    p = Path(str(raw).split(":")[-1])  # redaction never touches 'path'
    if not p.is_absolute():
        p = base / p
    # confinement: refuse to act outside the recorded workspace base
    try:
        p.resolve().relative_to(base.resolve())
    except ValueError:
        return {"ok": False, "error": f"path escapes recorded workspace: {p}"}
    try:
        if p.exists() and p.is_file():
            p.unlink()
            return {"ok": True, "removed": str(p)}
        return {"ok": True, "noop": "file absent (already undone?)"}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}
