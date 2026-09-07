"""Agent Registry.

Agents are definitions (persisted) plus runtime instances (status). Agents can
be created, modified, disabled, versioned and assigned skills/tools/model
policies — all through the registry.
"""

from __future__ import annotations

from typing import Optional

from agentos.agents.hierarchy import ORG_AGENTS
from agentos.db.store import EntityStore
from agentos.domain.models import AgentDef, AgentInstance, AgentStatus


class AgentRegistry:
    def __init__(self, store: EntityStore) -> None:
        self.store = store
        self._collection = "agents"
        self._instances = "agent_instances"

    # -- seeding ------------------------------------------------------------
    async def seed_defaults(self) -> int:
        """Load built-in org chart; YAML files in registry/agents override."""
        existing = await self.list()
        if existing:
            return len(existing)
        for agent in ORG_AGENTS.values():
            await self.store.save(self._collection, agent)
        return len(ORG_AGENTS)

    # -- CRUD ---------------------------------------------------------------
    async def get(self, agent_id: str) -> Optional[AgentDef]:
        return await self.store.get(self._collection, agent_id, AgentDef)

    async def list(self, enabled_only: bool = False) -> list[AgentDef]:
        agents = await self.store.list(self._collection, AgentDef)
        agents.sort(key=lambda a: a.id)
        return [a for a in agents if a.enabled or not enabled_only]

    async def create(self, agent: AgentDef) -> AgentDef:
        await self.store.save(self._collection, agent)
        return agent

    async def update(self, agent: AgentDef) -> AgentDef:
        existing = await self.get(agent.id)
        if not existing:
            raise KeyError(f"agent {agent.id} not found")
        agent.version = existing.version + 1
        await self.store.save(self._collection, agent)
        return agent

    async def disable(self, agent_id: str, enabled: bool = False) -> AgentDef:
        agent = await self.get(agent_id)
        if not agent:
            raise KeyError(f"agent {agent_id} not found")
        agent.enabled = enabled
        await self.store.save(self._collection, agent)
        return agent

    async def delete(self, agent_id: str) -> None:
        await self.store.delete(self._collection, agent_id)

    # -- hierarchy ----------------------------------------------------------
    def children_of(self, agent_id: str) -> list[AgentDef]:
        return [a for a in ORG_AGENTS.values() if a.parent_agent == agent_id]

    # -- runtime status -----------------------------------------------------
    async def instance(self, agent_id: str) -> AgentInstance:
        inst = await self.store.get(self._instances, agent_id, AgentInstance)
        if inst is None:
            inst = AgentInstance(agent_id=agent_id)
            await self.store.save(self._instances, inst)
        return inst

    async def set_status(
        self, agent_id: str, status: AgentStatus, *, task_id: str | None = None,
        project_id: str | None = None, model: str | None = None,
        action: str = "", error: str | None = None,
    ) -> AgentInstance:
        inst = await self.instance(agent_id)
        inst.status = status
        inst.current_task_id = task_id
        inst.current_project_id = project_id
        inst.model = model
        inst.latest_action = action
        inst.error = error
        if status in (AgentStatus.WORKING, AgentStatus.AWAITING_APPROVAL, AgentStatus.AWAITING_REVIEW):
            inst.started_at = inst.started_at or None
        if status in (AgentStatus.IDLE, AgentStatus.FAILED, AgentStatus.OFFLINE):
            inst.started_at = None
        await self.store.save(self._instances, inst)
        return inst

    async def list_instances(self) -> list[AgentInstance]:
        return await self.store.list(self._instances, AgentInstance)