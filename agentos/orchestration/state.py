"""Workflow run state (LangGraph state schema)."""

from __future__ import annotations

from typing import TypedDict


class WorkflowState(TypedDict, total=False):
    run_id: str
    workflow_id: str
    project_id: str
    entry_stage: str
    stages: list[dict]
    current_stage: str
    stage_results: dict[str, dict]
    # control fields
    action: str  # continue | retry | approval | failed | complete
    status: str  # running | awaiting_approval | completed | failed
    error: str
    retry_count: int
    # approval fields
    pending_approval_id: str
    approval_decision: str  # "" | approved | rejected | changes_requested
    approval_note: str
    # bookkeeping
    total_steps: int


def new_state(run_id: str, workflow_id: str, project_id: str,
              entry_stage: str, stages: list[dict]) -> dict:
    return {
        "run_id": run_id,
        "workflow_id": workflow_id,
        "project_id": project_id,
        "entry_stage": entry_stage,
        "stages": stages,
        "current_stage": entry_stage,
        "stage_results": {},
        "action": "continue",
        "status": "running",
        "error": "",
        "retry_count": 0,
        "pending_approval_id": "",
        "approval_decision": "",
        "approval_note": "",
        "total_steps": 0,
    }