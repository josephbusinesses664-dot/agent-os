"""Tool Executor.

Enforces least-privilege: every tool call is checked against the agent's
permission map before the handler runs. High-risk tools require an approval
record for (task, tool) before they execute — no approval, no execution.
All calls are logged to the audit trail.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from agentos.domain.models import ApprovalRequest, Task
from agentos.registries.tool_registry import ToolRegistry
from agentos.security.approvals import ApprovalService
from agentos.security.audit import AuditLog

logger = logging.getLogger("agentos.tools")


class ToolDeniedError(PermissionError):
    pass


class ToolExecutor:
    def __init__(self, tools: ToolRegistry, approvals: ApprovalService,
                 audit: AuditLog, require_approval_risk: str = "high") -> None:
        self.tools = tools
        self.approvals = approvals
        self.audit = audit
        self.require_approval_risk = require_approval_risk

    async def execute(self, ctx: Any, agent: Any, tool_name: str, args: dict) -> dict:
        """Execute a tool for an agent. Returns a result dict, never raises
        for normal failures (those are reported in the dict)."""
        tool = await self.tools.get(tool_name)
        if tool is None or not tool.enabled:
            return {"ok": False, "error": f"unknown or disabled tool: {tool_name}"}
        permission_key = tool.permission_key or tool.name
        if not agent.allows(permission_key):
            await self.audit.record(agent.id, "tool.denied", target=tool_name,
                                    project_id=ctx.project.project_id if ctx.project else None,
                                    task_id=ctx.task.task_id if ctx.task else None,
                                    tool=tool_name, result="denied",
                                    details={"reason": "permission policy"})
            return {"ok": False, "error": f"tool {tool_name} denied by permission policy for {agent.id}"}

        # Approval gate for high-risk tools
        if tool.risk_level == self.require_approval_risk and tool.risk_level == "high":
            granted = await self._tool_approved(ctx, tool_name)
            if not granted:
                approval = await self.approvals.request(
                    agent.id, agent.name, f"tool:{tool_name}",
                    task_id=ctx.task.task_id if ctx.task else None,
                    project_id=ctx.project.project_id if ctx.project else None,
                    risk_level="high",
                    reason=f"{agent.name} wants to call {tool_name} with args {str(args)[:300]}",
                )
                await self.audit.record(agent.id, "tool.approval_requested", target=tool_name,
                                        project_id=ctx.project.project_id if ctx.project else None,
                                        task_id=ctx.task.task_id if ctx.task else None,
                                        tool=tool_name, result="pending",
                                        details={"approval_id": approval.approval_id})
                return {"ok": False, "pending_approval": approval.approval_id,
                        "error": f"tool {tool_name} requires human approval "
                                 f"({approval.approval_id}) — awaiting decision"}

        handler = self.tools.handler(tool_name)
        if handler is None:
            return {"ok": False, "error": f"no handler registered for {tool_name}"}
        try:
            result = await handler(ctx, args)
        except Exception as exc:  # noqa: BLE001
            logger.exception("tool %s failed", tool_name)
            result = {"ok": False, "error": f"{tool_name} failed: {exc}"}
        await self.audit.record(agent.id, "tool.called", target=tool_name,
                                project_id=ctx.project.project_id if ctx.project else None,
                                task_id=ctx.task.task_id if ctx.task else None,
                                tool=tool_name, result="ok" if result.get("ok") else "error",
                                details={"args": {k: str(v)[:200] for k, v in args.items()},
                                         "result": str(result)[:500]})
        return result

    async def _tool_approved(self, ctx: Any, tool_name: str) -> bool:
        task_id = ctx.task.task_id if ctx.task else "none"
        if ctx.approved_tools is not None and tool_name in ctx.approved_tools:
            return True
        pending = await self.approvals.pending()
        for approval in pending:
            if approval.task_id == task_id and approval.action == f"tool:{tool_name}":
                return False  # already awaiting
        # fall back to memory marker set when an approval was granted
        if ctx.services.memory is not None:
            entries = await ctx.services.memory.recall("task", task_id, query=f"approve {tool_name}", limit=5)
            for entry in entries:
                if entry.kind == "approval" and f"approve:{tool_name}" in entry.content:
                    return True
        return False