"""Agent Runtime.

Instantiates an agent definition for one task: composes its system prompt
(role + project context + memory + relevant skills + tools + constraints +
output format), routes a model, runs the model/tool loop, records usage and
produces a structured result with reflection. No fake autonomy: everything an
agent claims must trace to tools that actually ran.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from agentos.domain.models import (
    AgentDef,
    ModelResponse,
    Project,
    Task,
    UsageRecord,
)
from agentos.tools.executor import ToolExecutor
from agentos.models.router import ModelRouter
from agentos.tools.executor import ToolExecutor

logger = logging.getLogger("agentos.runtime")

MAX_TOOL_ROUNDS = 6
TOOL_CALL_RE = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.DOTALL)


@dataclass
class RuntimeContext:
    """Everything a tool handler may touch, scoped to one agent run."""

    agent: AgentDef
    task: Optional[Task]
    project: Optional[Project]
    workspace: Any  # Path
    services: Any  # Services bundle
    executor: ToolExecutor
    router: ModelRouter
    prompts: Any  # PromptLibrary
    skill_registry: Any
    agent_registry: Any
    event_bus: Any
    budget_manager: Any
    approved_tools: set[str] = field(default_factory=set)


@dataclass
class AgentRunResult:
    content: str = ""
    artifacts: list[str] = field(default_factory=list)
    tool_calls: list[dict] = field(default_factory=list)
    model: Optional[str] = None
    cost: float = 0.0
    usage: list[UsageRecord] = field(default_factory=list)
    error: Optional[str] = None
    fail_class: Optional[str] = None  # transient | configuration | provider | permission | logic
    reflection: dict[str, Any] = field(default_factory=dict)


def classify_error(error: str) -> str:
    low = error.lower()
    if any(k in low for k in ("timeout", "timed out", "connection", "reset", "502", "503", "temporarily")):
        return "transient"
    if any(k in low for k in ("permission", "denied", "unauthorized", "not authorized")):
        return "permission"
    if any(k in low for k in ("not configured", "no api key", "no search api")):
        return "configuration"
    if any(k in low for k in ("provider", "model")):
        return "provider"
    return "logic"


def parse_tool_calls(response: ModelResponse) -> list[dict]:
    calls = list(response.tool_calls)
    for block in TOOL_CALL_RE.findall(response.content or ""):
        try:
            parsed = json.loads(block)
            if isinstance(parsed, dict) and "tool" in parsed:
                calls.append(parsed)
        except json.JSONDecodeError:
            continue
    return calls


class AgentRuntime:
    def __init__(self, ctx: RuntimeContext) -> None:
        self.ctx = ctx
        self.agent = ctx.agent

    # -- prompt composition -------------------------------------------------
    async def _build_prompt(self, task: Task) -> tuple[str, str]:
        ctx = self.ctx
        project = ctx.project
        project_context = "No project context."
        if project:
            project_context = (
                f"Project: {project.name}\n"
                f"Objective: {project.objective}\n"
                f"Status: {project.status.value} (stage: {project.stage or 'none'})\n"
                f"Requirements: {'; '.join(project.requirements[-5:]) or 'none recorded'}\n"
                f"Budget spent: ${project.cost:.3f}"
            )
        memory_ctx = "No relevant memory."
        try:
            entries = await ctx.services.memory.recall("project", project.project_id if project else "org",
                                                       query=task.description, limit=6)
            if entries:
                memory_ctx = "\n".join(f"- [{e.kind}] {e.content}" for e in entries)
        except Exception:  # noqa: BLE001
            pass

        skills_ctx = "None loaded."
        try:
            skills = await ctx.skill_registry.load_for_agent(self.agent.id, task.description, limit=5)
            if skills:
                skills_ctx = "\n\n".join(
                    f"### {s.name} ({s.id})\n{s.body[:3000]}" for s in skills
                )
        except Exception:  # noqa: BLE001
            pass

        tools_ctx = "\n".join(
            f"- {t.name}: {t.description}"
            for t in await ctx.services.tools.list()
            if self.agent.allows(t.permission_key or t.name)
        ) or "No tools permitted."

        context = {
            "agent_id": self.agent.id,
            "role": self.agent.role,
            "name": self.agent.name,
            "description": self.agent.description,
            "responsibilities": f"Parent: {self.agent.parent_agent or 'none'}. "
                                f"Escalate unresolved issues to your parent agent.",
            "project_context": project_context,
            "task": task.description or task.title,
            "skills": skills_ctx,
            "tools": tools_ctx,
            "extra_constraints": (
                f"- Model policy tier: {self.agent.model_policy.get('tier', 't2')}.\n"
                f"- Risk level: {self.agent.risk_level}.\n"
                f"- You may delegate to sub-agents only by requesting a new task from "
                f"your parent; do not simulate other agents."
            ),
            "output_format": (
                "Write your final answer as a concise report with concrete "
                "artifacts (file paths under the project workspace when "
                "applicable). Never invent test/deploy evidence."
            ),
        }
        system = ctx.prompts.render(self.agent.id, context)
        user = (f"Task: {task.title}\n\n{task.description or ''}\n\n"
                f"Task id: {task.task_id}\nProject id: {task.project_id}")
        return system, user

    # -- model loop ---------------------------------------------------------
    async def run(self, task: Task, *, force_model: Optional[str] = None,
                  approved_tools: Optional[set[str]] = None) -> AgentRunResult:
        """Execute one task with this agent. Returns a result (never raises
        for ordinary failures; provider outages classify as transient)."""
        ctx = self.ctx
        if approved_tools:
            ctx.approved_tools |= approved_tools
        result = AgentRunResult()
        system, user = await self._build_prompt(task)

        model_id, reason = await ctx.router.route(self.agent, task, project_id=task.project_id,
                                                  force_model=force_model)
        if model_id is None:
            result.error = f"model routing rejected: {reason}"
            result.fail_class = "configuration"
            return result
        result.model = model_id

        messages: list[dict] = [{"role": "user", "content": user}]
        try:
            response = await self._call_with_failover(model_id, system, messages, task)
        except Exception as exc:  # noqa: BLE001
            result.error = str(exc)
            result.fail_class = classify_error(str(exc))
            return result

        executed_signatures: set[str] = set()
        for round_index in range(MAX_TOOL_ROUNDS):
            if response.error:
                result.error = response.error
                result.fail_class = classify_error(response.error)
                break
            await self._track_usage(response, task, result)
            calls = parse_tool_calls(response)
            # never re-execute an identical tool call (prevents model tool loops)
            fresh_calls = []
            for call in calls:
                args = call.get("args", {}) if isinstance(call.get("args"), dict) else {}
                # signature ignores volatile content fields so a re-emitted call
                # with regenerated text is still recognized as a duplicate
                sig_args = {k: v for k, v in args.items() if k != "content"}
                signature = call.get("tool", "") + json.dumps(sig_args, sort_keys=True)
                if signature in executed_signatures:
                    continue
                executed_signatures.add(signature)
                fresh_calls.append(call)
            if not fresh_calls:
                result.content = response.content or ""
                break
            result.tool_calls.extend(fresh_calls)
            await ctx.event_bus.publish("agent.tool_calls", {"agent": self.agent.id,
                                                             "task": task.task_id,
                                                             "calls": [c.get("tool") for c in fresh_calls]},
                                        agent_id=self.agent.id, task_id=task.task_id,
                                        project_id=task.project_id)
            for call in fresh_calls:
                tool_name = call.get("tool", "")
                args = call.get("args", {}) if isinstance(call.get("args"), dict) else {}
                tool_result = await ctx.executor.execute(ctx, self.agent, tool_name, args)
                if tool_result.get("ok") and tool_name in ("filesystem.write", "api.call", "shell"):
                    for path in self._extract_artifacts(tool_result):
                        if path not in result.artifacts:
                            result.artifacts.append(path)
                messages.append({
                    "role": "user",
                    "content": f"[tool result for {tool_name}]\n{json.dumps(tool_result)[:4000]}",
                })
                if tool_result.get("pending_approval"):
                    result.error = f"awaiting approval {tool_result['pending_approval']}"
                    result.fail_class = "human_required"
                    return result
            try:
                response = await self._call_with_failover(model_id, system, messages, task)
            except Exception as exc:  # noqa: BLE001
                result.error = str(exc)
                result.fail_class = classify_error(str(exc))
                return result
        else:
            result.error = f"exceeded {MAX_TOOL_ROUNDS} tool rounds"
            result.fail_class = "logic"

        result.reflection = self._build_reflection(result, task)
        return result

    async def _call_with_failover(self, model_id: str, system: str,
                                  messages: list[dict], task: Task) -> ModelResponse:
        ctx = self.ctx
        request = await self._make_request(model_id, system, messages, task)
        current = model_id
        used: set[str] = set()
        for attempt in range(3):
            used.add(current)
            model_def = await ctx.router.registry.get(current)
            provider = None
            if model_def:
                provider = ctx.services.providers.get(model_def.provider)
            if provider is None:
                fallback, reason = await ctx.router.failover(current, "no provider for model")
                if fallback and fallback not in used:
                    current = fallback
                    await ctx.event_bus.publish("model.failover",
                                                {"from": model_id, "to": current, "reason": reason},
                                                project_id=task.project_id, task_id=task.task_id,
                                                severity="warning")
                    request.model_id = current
                    continue
                return ModelResponse(request_id=request.request_id, model_id=current,
                                     error=f"no provider for {current}")
            request.model_id = current
            response = await provider.complete(request)
            if not response.error:
                return response
            fallback, reason = await ctx.router.failover(current, response.error)
            if fallback and fallback not in used:
                current = fallback
                await ctx.event_bus.publish("model.failover",
                                            {"from": model_id, "to": current, "reason": reason},
                                            project_id=task.project_id, task_id=task.task_id,
                                            severity="warning")
            else:
                return response
        return response

    async def _make_request(self, model_id: str, system: str,
                            messages: list[dict], task: Task) -> Any:
        from agentos.domain.models import ModelRequest

        return ModelRequest(model_id=model_id, system=system, messages=messages,
                            project_id=task.project_id, agent_id=self.agent.id,
                            task_id=task.task_id)

    async def _track_usage(self, response: ModelResponse, task: Task, result: AgentRunResult) -> None:
        model_def = await self.ctx.router.registry.get(response.model_id)
        provider = model_def.provider if model_def else "unknown"
        record = UsageRecord(
            provider=provider,
            model=response.model_id,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            estimated_cost=response.estimated_cost,
            project_id=task.project_id,
            agent_id=self.agent.id,
            task_id=task.task_id,
            request_id=response.request_id,
        )
        result.usage.append(record)
        result.cost += response.estimated_cost

    def _extract_artifacts(self, tool_result: dict) -> list[str]:
        paths: list[str] = []
        raw = json.dumps(tool_result)
        for m in re.finditer(r"\"?path\"?\s*:\s*\"([^\"]+)\"", raw):
            p = m.group(1)
            if p.startswith(("workspace", "artifacts", "./", "/")) or "." in p:
                paths.append(p)
        return paths[:20]

    def _build_reflection(self, result: AgentRunResult, task: Task) -> dict[str, Any]:
        return {
            "asked": task.title,
            "done": result.content[:500] if result.content else "",
            "worked": [c.get("tool") for c in result.tool_calls],
            "failed": result.error or None,
            "remains": "verification by a senior agent" if result.error else "none",
            "next_agent_note": f"task {task.task_id} run by {self.agent.id} "
                               f"using {result.model}; cost ${result.cost:.4f}",
        }