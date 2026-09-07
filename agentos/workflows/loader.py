"""Workflow loader.

Workflows are declarative YAML files (workflows/*.yaml) describing stages,
the agent role that runs each stage, dependencies and approval gates. The
LangGraph engine executes any loaded workflow — adding a new workflow is a
YAML file, not a code change.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

from agentos.db.store import EntityStore
from agentos.domain.models import WorkflowDef, WorkflowStage


def parse_workflow(data: dict, source_path: str = "") -> WorkflowDef:
    stages = [WorkflowStage(**s) for s in data.get("stages", [])]
    # link stages: infer `next` from declaration order when not explicit
    for i, stage in enumerate(stages):
        if stage.next is None and i + 1 < len(stages):
            if all(stages[i + 1].stage_id not in (d for d in stage.depends_on) or True for _ in [0]):
                pass
        if stage.next is None and i + 1 < len(stages):
            stage.next = stages[i + 1].stage_id
    return WorkflowDef(
        workflow_id=data["workflow_id"],
        name=data.get("name", data["workflow_id"]),
        description=data.get("description", ""),
        entry_stage=data["entry_stage"],
        stages=stages,
        version=data.get("version", "1.0.0"),
        source_path=source_path,
    )


class WorkflowRegistry:
    def __init__(self, store: EntityStore, workflows_root: Optional[Path] = None) -> None:
        self.store = store
        self.root = workflows_root or Path(__file__).resolve().parents[2] / "workflows"
        self._collection = "workflows"

    async def load_from_disk(self) -> int:
        count = 0
        if not self.root.exists():
            return 0
        for path in sorted(self.root.glob("*.yaml")):
            data = yaml.safe_load(path.read_text())
            if not data or "workflow_id" not in data:
                continue
            workflow = parse_workflow(data, source_path=str(path))
            await self.store.save(self._collection, workflow)
            count += 1
        return count

    async def get(self, workflow_id: str) -> Optional[WorkflowDef]:
        return await self.store.get(self._collection, workflow_id, WorkflowDef)

    async def list(self) -> list[WorkflowDef]:
        workflows = await self.store.list(self._collection, WorkflowDef)
        workflows.sort(key=lambda w: w.workflow_id)
        return workflows

    async def register(self, workflow: WorkflowDef) -> WorkflowDef:
        await self.store.save(self._collection, workflow)
        return workflow