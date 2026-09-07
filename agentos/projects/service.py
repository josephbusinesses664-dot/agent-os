"""Project Service.

A project carries objective, requirements, roadmap (workflow), tasks, agents,
decisions, artifacts and its own memory. Agents can always inspect project
state; nothing about a project lives only in a chat.
"""

from __future__ import annotations

from typing import Optional

from agentos.db.store import EntityStore
from agentos.domain.models import DecisionRecord, Project, ProjectStatus, new_id


class ProjectService:
    def __init__(self, store: EntityStore) -> None:
        self.store = store
        self._collection = "projects"
        self._decisions = "decisions"

    async def create(self, name: str, objective: str = "", *,
                     created_by: str = "executive",
                     workflow_id: Optional[str] = None,
                     budget: float = 0.0) -> Project:
        project = Project(project_id=new_id("prj"), name=name, objective=objective,
                          created_by=created_by, workflow_id=workflow_id, budget=budget)
        await self.store.save(self._collection, project)
        return project

    async def get(self, project_id: str) -> Optional[Project]:
        return await self.store.get(self._collection, project_id, Project)

    async def require(self, project_id: str) -> Project:
        project = await self.get(project_id)
        if not project:
            raise KeyError(f"project {project_id} not found")
        return project

    async def list(self) -> list[Project]:
        projects = await self.store.list(self._collection, Project)
        projects.sort(key=lambda p: p.created_at, reverse=True)
        return projects

    async def update(self, project: Project) -> None:
        project.touch()
        await self.store.save(self._collection, project)

    async def set_status(self, project_id: str, status: ProjectStatus, stage: str = "") -> Project:
        project = await self.require(project_id)
        project.status = status
        if stage:
            project.stage = stage
        await self.update(project)
        return project

    async def add_requirement(self, project_id: str, requirement: str) -> Project:
        project = await self.require(project_id)
        project.requirements.append(requirement)
        await self.update(project)
        return project

    async def add_artifact(self, project_id: str, artifact: str) -> Project:
        project = await self.require(project_id)
        if artifact not in project.artifacts:
            project.artifacts.append(artifact)
        await self.update(project)
        return project

    # -- decisions ----------------------------------------------------------
    async def record_decision(self, project_id: str, decision: str, *,
                              alternatives: Optional[list[str]] = None,
                              reasoning: str = "", decided_by: str = "executive",
                              reversible: bool = True) -> DecisionRecord:
        record = DecisionRecord(project=project_id, decision=decision,
                                alternatives=alternatives or [],
                                reasoning_summary=reasoning, decided_by=decided_by,
                                reversible=reversible)
        await self.store.save(self._decisions, record)
        project = await self.get(project_id)
        if project:
            project.decisions.append(record.decision_id)
            await self.update(project)
        return record

    async def decisions(self, project_id: str) -> list[DecisionRecord]:
        records = await self.store.list(self._decisions, DecisionRecord,
                                        predicate={"project": project_id})
        records.sort(key=lambda r: r.date)
        return records

    async def delete(self, project_id: str) -> None:
        await self.store.delete(self._collection, project_id)