"""Human Approval System.

High-risk actions (deployments, destructive operations, financial actions,
external communications) require explicit human approval before they run.
Approvals are persisted, surface in Mattermost and the admin UI, and can be
granted/rejected/requested-changes from either.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from agentos.db.store import EntityStore
from agentos.domain.models import ApprovalRequest, ApprovalStatus


class ApprovalService:
    def __init__(self, store: EntityStore) -> None:
        self.store = store
        self._collection = "approvals"

    async def request(self, agent_id: str, agent_name: str, action: str,
                      *, task_id: Optional[str] = None, project_id: Optional[str] = None,
                      risk_level: str = "high", reason: str = "") -> ApprovalRequest:
        approval = ApprovalRequest(agent_id=agent_id, agent_name=agent_name,
                                   task_id=task_id, project_id=project_id,
                                   action=action, risk_level=risk_level, reason=reason)
        await self.store.save(self._collection, approval)
        return approval

    async def pending(self) -> list[ApprovalRequest]:
        approvals = await self.store.list(self._collection, ApprovalRequest,
                                          predicate={"status": ApprovalStatus.PENDING.value})
        approvals.sort(key=lambda a: a.created_at)
        return approvals

    async def get(self, approval_id: str) -> Optional[ApprovalRequest]:
        return await self.store.get(self._collection, approval_id, ApprovalRequest)

    async def decide(self, approval_id: str, decision: str, decided_by: str,
                     note: str = "") -> ApprovalRequest:
        approval = await self.get(approval_id)
        if not approval:
            raise KeyError(f"approval {approval_id} not found")
        if approval.status != ApprovalStatus.PENDING:
            raise ValueError(f"approval {approval_id} already decided")
        approval.status = ApprovalStatus(decision)
        approval.decided_by = decided_by
        approval.decided_at = datetime.now(timezone.utc)
        approval.decision_note = note
        await self.store.save(self._collection, approval)
        return approval

    async def all(self, limit: int = 100) -> list[ApprovalRequest]:
        approvals = await self.store.list(self._collection, ApprovalRequest)
        approvals.sort(key=lambda a: a.created_at, reverse=True)
        return approvals[:limit]