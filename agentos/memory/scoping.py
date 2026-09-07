"""Memory permission-scoping (Phase 16 of the master spec).

Memory authority rules — enforced in code at recall/save time, not by
prompt etiquette:

- TASK scope:    any participant agent of the task may read; only the
                 assigned agent (or its parent) may write.
- PROJECT scope: readable by any agent working in that project; writes
                 allowed for project participants.
- AGENT scope:   private to the agent; a parent may read a child's memory
                 (supervision), siblings may not.
- ORG scope:     readable by all agents; writes restricted to
                 executive/director-level agents (identity autonomy >= L4).
- USER scope:    private to the user; readable by the user's agents only
                 for scope='user' owner=<user>. Agents never read other
                 users' memories.

`can_read` / `can_write` are pure and testable; `scoped_recall` and
`scoped_save` wrap the MemoryStore and deny unauthorized access, audit the
denial, and never leak that a memory exists (denials look like empty
results to the caller — existence is not disclosed).
"""

from __future__ import annotations

from typing import Any, Optional

from agentos.domain.models import MemoryScope

# hierarchy ranks for org-write authority
_ORG_WRITE_MIN_AUTONOMY = 4  # L4+: executives and directors


def _rank(agent_def: Optional[Any]) -> int:
    """Autonomy rank from identity; workers default to L2."""
    ident = getattr(agent_def, "identity", None)
    if ident is None:
        return 2
    return {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5}.get(
        getattr(ident, "autonomy", "L2"), 2)


def _is_task_participant(agent_def: Optional[Any], task: Any) -> bool:
    """Is this agent a participant of `task`?

    Participants (enforced, not assumed):
    - the assigned agent
    - the assigned agent's parent (supervision of a child's task)
    - an agent whose parent is the assigned agent (collaborator working
      under the parent's task)

    An unassigned task has no participants. Possession of a task object
    is not participation.
    """
    agent_id = getattr(agent_def, "id", "") if agent_def else ""
    if not agent_id or task is None:
        return False
    assigned = getattr(task, "assigned_agent", None)
    if not assigned:
        return False
    if assigned == agent_id:
        return True
    if assigned in (getattr(agent_def, "allowed_children", None) or []):
        return True
    parent = getattr(agent_def, "parent_agent", "") or ""
    return bool(parent) and assigned == parent


def can_read(agent_def: Optional[Any], scope: MemoryScope | str,
             owner_id: str, *, task: Any = None, project_id: str = "") -> bool:
    """May this agent read memories under (scope, owner_id)?"""
    scope = MemoryScope(scope).value
    agent_id = getattr(agent_def, "id", "") if agent_def else ""

    if scope == "task":
        return (task is not None and task.task_id == owner_id
                and _is_task_participant(agent_def, task))
    if scope == "project":
        return bool(project_id) and project_id == owner_id
    if scope == "agent":
        if agent_id == owner_id:
            return True
        # supervision: a parent may read a child's private memory
        parent = getattr(agent_def, "parent_agent", "")
        children = getattr(agent_def, "allowed_children", []) or []
        return owner_id in children or (bool(parent) and owner_id == agent_id)
    if scope == "org":
        return True  # organizational memory is readable org-wide
    if scope == "user":
        # user memories are reachable only through explicit user-owned
        # sessions; agents access only the org/project layers instead
        return False
    return False


def can_write(agent_def: Optional[Any], scope: MemoryScope | str,
              owner_id: str, *, task: Any = None, project_id: str = "") -> bool:
    """May this agent save memories under (scope, owner_id)?"""
    scope = MemoryScope(scope).value
    agent_id = getattr(agent_def, "id", "") if agent_def else ""
    if not agent_id:
        return False

    if scope == "task":
        # writes: the assigned agent, or its parent on the child's behalf
        if task is None or task.task_id != owner_id:
            return False
        agent_children = getattr(agent_def, "allowed_children", None) or []
        assigned = getattr(task, "assigned_agent", None)
        return bool(assigned) and (assigned == agent_id
                                   or assigned in agent_children)
    if scope == "project":
        return bool(project_id) and project_id == owner_id
    if scope == "agent":
        return agent_id == owner_id
    if scope == "org":
        return _rank(agent_def) >= _ORG_WRITE_MIN_AUTONOMY
    if scope == "user":
        return False
    return False


class ScopedMemoryStore:
    """Permission-scoping wrapper around the MemoryStore. Denials return
    empty results (existence not disclosed) and are audit-logged."""

    def __init__(self, memory: Any, audit: Any = None) -> None:
        self.memory = memory
        self.audit = audit

    async def _deny(self, agent_def: Any, op: str, scope: str, owner_id: str,
                    task: Any = None) -> list:
        if self.audit is not None:
            try:
                await self.audit.record(
                    getattr(agent_def, "id", "unknown") if agent_def else "unknown",
                    f"memory.{op}_denied",
                    target=f"{scope}:{owner_id}",
                    result="denied",
                    details={"scope": scope})
            except Exception:  # noqa: BLE001
                pass
        return []

    async def scoped_recall(self, agent_def: Any, scope: MemoryScope | str,
                            owner_id: str, *, query: Optional[str] = None,
                            limit: int = 10, task: Any = None,
                            project_id: str = "") -> list:
        if not can_read(agent_def, scope, owner_id, task=task,
                        project_id=project_id):
            return await self._deny(agent_def, "recall", MemoryScope(scope).value,
                                    owner_id, task)
        return await self.memory.recall(scope, owner_id, query=query, limit=limit)

    async def scoped_save(self, agent_def: Any, scope: MemoryScope | str,
                          owner_id: str, content: str, *, task: Any = None,
                          project_id: str = "", **kw):
        if not can_write(agent_def, scope, owner_id, task=task,
                         project_id=project_id):
            await self._deny(agent_def, "save", MemoryScope(scope).value,
                             owner_id, task)
            return None
        return await self.memory.save(scope, owner_id, content, **kw)



