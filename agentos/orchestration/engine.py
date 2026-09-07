"""Orchestration Engine.

The engine drives workflows through the LangGraph state machine, executes
individual stages (instantiating the assigned agent for the duration of the
stage), enforces spawning limits, records usage/cost and handles approvals,
retries and failure recovery.

Spawning limits (defense against agent storms):
  * max recursion depth per agent chain
  * max parallel agents
  * budget checks per task
  * duplicate-task detection while a task is active
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from agentos.agents.runtime import AgentRunResult
from agentos.domain.models import (
    AgentStatus,
    ApprovalStatus,
    BudgetScope,
    Project,
    StageResult,
    Task,
    TaskStatus,
    UsageRecord,
    WorkflowDef,
    WorkflowStage,
    new_id,
)
from agentos.orchestration.state import new_state
from agentos.services import Services

logger = logging.getLogger("agentos.engine")

TRANSIENT_CLASSES = {"transient", "provider"}


class SpawnLimitError(Exception):
    pass


class OrchestratorEngine:
    def __init__(self, svc: Services) -> None:
        self.svc = svc
        self._graph = None
        self._active_runs: dict[str, dict] = {}
        self._active_task_hashes: dict[str, str] = {}  # task hash -> task id
        self._parallel_count = 0

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------
    async def execute_goal(self, goal: str, user_id: str = "human",
                           workflow_id: str = "zero_to_hundred",
                           project_name: Optional[str] = None) -> dict:
        """Executive flow: create a project and run a workflow on it."""
        name = project_name or _slug(goal)[:60] or "New Project"
        project = await self.svc.projects.create(name, objective=goal, created_by=user_id,
                                                 workflow_id=workflow_id)
        await self.svc.events.publish("project.created", {"name": name, "goal": goal},
                                      project_id=project.project_id, source="executive")
        run = await self.run_workflow(workflow_id, project.project_id)
        return {"project_id": project.project_id, "run_id": run["run_id"],
                "status": run["status"]}

    async def execute_dynamic(self, goal: str, user_id: str = "human",
                              stages: Optional[list[str]] = None,
                              expand_full: bool = False) -> dict:
        """Autonomous planning: the planner selects the required stages from
        the goal (explicit PLANNED_STAGES marker, keyword scoring, or the full
        pipeline on request), then runs them through the same engine."""
        plan = self.svc.planner.plan_summary(goal) if stages is None else {
            "stages": stages, "count": len(stages)}
        workflow = self.svc.planner.build_workflow(goal, stages=stages) \
            if stages is not None else self.svc.planner.build_workflow(goal)
        if expand_full and stages is None:
            workflow = self.svc.planner.build_workflow(
                goal, stages=self.svc.planner.plan_stages(goal, expand_full=True))
        name = _slug(goal)[:60] or "New Project"
        project = await self.svc.projects.create(
            name, objective=goal, created_by=user_id, workflow_id=workflow.workflow_id)
        await self.svc.events.publish(
            "workflow.planned",
            {"goal": goal[:200], "stages": plan["stages"],
             "agents": plan.get("agents", []), "workflow": workflow.workflow_id},
            project_id=project.project_id, source="executive")
        run = await self.run_workflow_obj(workflow, project.project_id)
        return {"project_id": project.project_id, "run_id": run["run_id"],
                "status": run["status"], "planned_stages": plan["stages"]}

    async def run_workflow(self, workflow_id: str, project_id: str,
                           entry_stage: Optional[str] = None) -> dict:
        workflow = await self.svc.workflow_registry.get(workflow_id)
        if workflow is None:
            raise KeyError(f"workflow {workflow_id} not found")
        return await self.run_workflow_obj(workflow, project_id, entry_stage)

    async def run_workflow_obj(self, workflow: WorkflowDef, project_id: str,
                               entry_stage: Optional[str] = None) -> dict:
        project = await self.svc.projects.require(project_id)
        run_id = new_id("run")
        state = new_state(run_id, workflow.workflow_id, project_id,
                          entry_stage or workflow.entry_stage,
                          [s.model_dump() for s in workflow.stages])
        self._active_runs[run_id] = {"workflow": workflow, "state": state}
        await self.svc.events.publish("workflow.started",
                                      {"workflow_id": workflow.workflow_id, "run_id": run_id},
                                      project_id=project_id, source="orchestrator")
        final = await self._invoke(run_id, state)
        return final

    async def resume(self, run_id: str, approval_decision: str, note: str = "",
                     decided_by: str = "human") -> dict:
        """Resume a paused run after a human approval decision."""
        entry = self._active_runs.get(run_id)
        if entry is None:
            raise KeyError(f"unknown run {run_id}")
        state = dict(entry["state"])
        state["approval_decision"] = approval_decision
        state["approval_note"] = note
        state["status"] = "running"
        final = await self._invoke(run_id, state)
        return final

    async def approve(self, approval_id: str, decision: str, decided_by: str = "human",
                      note: str = "") -> Optional[dict]:
        """Human decides an approval; resume the paused workflow run if any."""
        approval = await self.svc.approvals.get(approval_id)
        if approval is None:
            return None
        if approval.status.value == "pending":
            await self.svc.approvals.decide(approval_id, decision, decided_by, note=note)
        # find a run paused on this approval
        for run_id, entry in self._active_runs.items():
            state = entry.get("state", {})
            if state.get("pending_approval_id") == approval_id and state.get("status") == "awaiting_approval":
                decision_map = {"approved": "approved", "rejected": "rejected",
                                "changes_requested": "rejected"}
                return await self.resume(run_id, decision_map.get(decision, "rejected"),
                                         note=note, decided_by=decided_by)
        return {"status": "no_paused_run", "approval_id": approval_id}

    async def run_single_task(self, task_id: str) -> AgentRunResult:
        """Execute one task (worker path). Returns the agent run result."""
        task = await self.svc.tasks.require(task_id)
        if not task.assigned_agent:
            raise ValueError(f"task {task_id} has no assigned agent")
        agent = await self.svc.agent_registry.get(task.assigned_agent)
        if not agent or not agent.enabled:
            raise ValueError(f"agent {task.assigned_agent} unavailable")
        project = await self.svc.projects.get(task.project_id)
        # drain structured messages so the agent starts with full context
        try:
            for message in await self.svc.messages.inbox(agent.id, unread_only=True, limit=10):
                await self.svc.messages.mark_delivered(message.message_id)
        except Exception:  # noqa: BLE001
            pass
        return await self._run_agent_for_task(agent, task, project)

    # ------------------------------------------------------------------
    # Stage execution
    # ------------------------------------------------------------------
    async def execute_stage_work(self, workflow: WorkflowDef, stage: WorkflowStage,
                                 project: Project, run_id: str) -> StageResult:
        """Instantiate the stage's agent and run the stage's task."""
        result = StageResult(stage_id=stage.stage_id, agent_id=stage.agent_role)
        agent = await self.svc.agent_registry.get(stage.agent_role)
        if agent is None or not agent.enabled:
            result.status = "failed"
            result.error = f"stage agent {stage.agent_role} unavailable"
            return result

        task = await self.svc.tasks.create(
            project.project_id, title=f"{stage.name} ({stage.stage_id})",
            description=stage.description or f"Execute workflow stage {stage.name}.",
            assigned_agent=agent.id, created_by="orchestrator",
            priority="high" if stage.requires_approval else "normal",
        )
        result.task_id = task.task_id
        await self.svc.tasks.set_status(task.task_id, TaskStatus.RUNNING)
        await self.svc.agent_registry.set_status(
            agent.id, AgentStatus.WORKING, task_id=task.task_id,
            project_id=project.project_id, model=result.model or "",
            action=f"stage {stage.stage_id}")
        result.started_at = task.created_at

        tracer = getattr(self.svc, "tracer", None)
        span = None
        span_cm = None
        if tracer is not None:
            span_cm = tracer.span(
                kind="stage", name=f"stage:{stage.stage_id}", trace_id=run_id,
                agent_id=agent.id, task_id=task.task_id,
                project_id=project.project_id, payload={"workflow": workflow.workflow_id})
            span = await span_cm.__aenter__()
        run = self.svc.runtime(agent, task, project)
        outcome = await run.run(task)
        result.model = outcome.model
        result.cost = outcome.cost
        result.error = outcome.error
        result.reflection = outcome.reflection
        result.artifacts = outcome.artifacts
        result.output = outcome.content
        if span is not None and span_cm is not None:
            span.status = "ok" if not outcome.error else "error"
            span.error = outcome.error
            span.model = outcome.model
            span.cost = outcome.cost
            span.result_summary = (outcome.content or "")[:200]
            await span_cm.__aexit__(None, None, None)

        # persist artifacts against the task + project
        for artifact in outcome.artifacts:
            await self.svc.tasks.record_artifact(task.task_id, artifact)
            await self.svc.projects.add_artifact(project.project_id, artifact)
        await self._record_usage(task, outcome)

        # every stage outcome gets evaluated (deterministic) + recorded
        try:
            record = await self.svc.evaluation.deterministic.evaluate(task, outcome)
            record.workflow_id = workflow.workflow_id
            record.skill_id = stage.stage_id
            await self.svc.entity_store.save("evaluation", record)
            await self.svc.performance.record_evaluation(record)
        except Exception:  # noqa: BLE001
            pass

        # structured handoff to the agent's parent (multi-agent visibility)
        try:
            if agent.parent_agent:
                await self.svc.messages.send_handoff(
                    agent.id, agent.parent_agent,
                    artifacts=outcome.artifacts,
                    note=f"stage {stage.stage_id} finished: "
                         f"{'ok' if not outcome.error else 'failed'}",
                    task_id=task.task_id, project_id=project.project_id)
        except Exception:  # noqa: BLE001
            pass

        if outcome.error and outcome.fail_class not in TRANSIENT_CLASSES:
            result.status = "failed"
            await self.svc.tasks.set_status(task.task_id, TaskStatus.FAILED, error=outcome.error)
            await self.svc.agent_registry.set_status(agent.id, AgentStatus.FAILED,
                                                     task_id=task.task_id,
                                                     project_id=project.project_id,
                                                     error=outcome.error)
            return result

        if outcome.error and outcome.fail_class in TRANSIENT_CLASSES:
            result.status = "failed"
            result.error = outcome.error
            await self.svc.tasks.set_status(task.task_id, TaskStatus.FAILED, error=outcome.error)
            await self.svc.agent_registry.set_status(agent.id, AgentStatus.BLOCKED,
                                                     task_id=task.task_id,
                                                     error=outcome.error)
            return result

        result.status = "completed"
        await self.svc.tasks.set_status(task.task_id, TaskStatus.COMPLETED,
                                        result=outcome.content[:4000])
        await self.svc.agent_registry.set_status(agent.id, AgentStatus.IDLE)
        await self.svc.events.publish("stage.completed", {"stage": stage.stage_id},
                                      project_id=project.project_id, task_id=task.task_id,
                                      agent_id=agent.id)
        return result

    # ------------------------------------------------------------------
    # Agent spawning (delegation)
    # ------------------------------------------------------------------
    async def spawn_subagent(self, parent_task: Task, child_agent_id: str,
                             description: str, depth: int = 0) -> AgentRunResult:
        """Run a child agent for a delegated subtask, with hard limits and
        strategy-change recovery: a transient failure is retried once with a
        stronger model before escalating to the parent."""
        settings = self.svc.settings
        if depth >= settings.max_agent_depth:
            raise SpawnLimitError(
                f"agent depth limit reached ({settings.max_agent_depth}) for {child_agent_id}")
        if self._parallel_count >= settings.max_parallel_agents:
            raise SpawnLimitError(f"parallel agent limit reached ({settings.max_parallel_agents})")
        hash_key = f"{parent_task.task_id}:{child_agent_id}:{description[:80]}"
        if hash_key in self._active_task_hashes:
            raise SpawnLimitError(f"duplicate active task detected: {child_agent_id} for {description[:60]}")

        agent = await self.svc.agent_registry.get(child_agent_id)
        if agent is None or not agent.enabled:
            raise SpawnLimitError(f"child agent {child_agent_id} unavailable")

        child = await self.svc.tasks.create(
            parent_task.project_id, title=f"{agent.name}: {description[:100]}",
            description=description, assigned_agent=child_agent_id,
            parent_task=parent_task.task_id, created_by=parent_task.assigned_agent or "executive",
        )
        self._active_task_hashes[hash_key] = child.task_id
        self._parallel_count += 1
        forced = None
        try:
            project = await self.svc.projects.get(parent_task.project_id)
            result = await self._run_agent_for_task(agent, child, project, depth=depth)
            # recoverable failure → retry once with a strategy change (stronger
            # model for this run only), then escalate to the parent.
            if result.error and result.fail_class in TRANSIENT_CLASSES and depth <= settings.max_agent_depth:
                await self.svc.events.publish(
                    "agent.retry_strategy_changed",
                    {"agent": agent.id, "task": child.task_id,
                     "reason": f"{result.fail_class} failure — retrying with stronger model"},
                    project_id=parent_task.project_id, task_id=child.task_id,
                    agent_id=agent.id, severity="warning")
                forced = await self._stronger_model(agent)
                result = await self._run_agent_for_task(agent, child, project, depth=depth,
                                                        force_model=forced)
            if result.error:
                await self.svc.messages.send(
                    "escalation", agent.id, parent_task.assigned_agent or "executive",
                    {"task_id": child.task_id, "error": str(result.error)[:500],
                     "fail_class": result.fail_class,
                     "parent_task": parent_task.task_id,
                     "retried_with": forced},
                    project_id=parent_task.project_id, task_id=child.task_id,
                    priority="high", requires_response=True)
            # downstream-success tracking: delegation outcomes fold back into
            # the parent agent's performance record (self-improvement signal)
            try:
                if parent_task.assigned_agent:
                    await self.svc.performance.record_downstream(
                        parent_task.assigned_agent, result.error is None)
            except Exception:  # noqa: BLE001
                pass
            return result
        finally:
            self._parallel_count -= 1
            self._active_task_hashes.pop(hash_key, None)

    async def _stronger_model(self, agent: Any) -> Optional[str]:
        """Pick a model one tier above the agent's policy (strategy change)."""
        tier = agent.model_policy.get("tier", "t2")
        stronger = {"t1": "t2", "t2": "t3"}.get(tier, "t3")
        model_id = await self.svc.router.pick_for_provider(stronger)
        if model_id:
            return model_id
        return await self.svc.router.pick_for_provider("t3") or await self.svc.router.pick_for_provider("t2")

    async def pick_child(self, parent: Any, description: str) -> Optional[str]:
        """Performance-aware delegation: among a parent's enabled children,
        prefer the one with the best track record for this kind of work."""
        children = [a for a in await self.svc.agent_registry.list(enabled_only=True)
                    if a.parent_agent == parent.id]
        if not children:
            return None
        ranked = []
        for child in children:
            stats = await self.svc.performance.stats(child.id, "all")
            ranked.append((child, stats))
        ranked.sort(key=lambda pair: (pair[1].success_rate, -pair[1].avg_cost,
                                      pair[1].runs), reverse=True)
        best, stats = ranked[0]
        if stats.runs >= self.svc.settings.perf_min_runs_for_influence:
            return best.id
        return children[0].id

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    async def _run_agent_for_task(self, agent: Any, task: Task, project: Optional[Project],
                                  depth: int = 0,
                                  force_model: Optional[str] = None) -> AgentRunResult:
        await self.svc.tasks.set_status(task.task_id, TaskStatus.RUNNING)
        await self.svc.agent_registry.set_status(
            agent.id, AgentStatus.WORKING, task_id=task.task_id,
            project_id=task.project_id, action=f"depth {depth}")
        run = self.svc.runtime(agent, task, project, spawn_depth=depth)
        outcome = await run.run(task, force_model=force_model)
        task = await self.svc.tasks.get(task.task_id)  # refresh
        if task:
            task.model_used = outcome.model
            task.cost = outcome.cost
            for artifact in outcome.artifacts:
                if artifact not in task.artifacts:
                    task.artifacts.append(artifact)
            if outcome.error:
                task.error = outcome.error
                task.status = TaskStatus.FAILED
                await self.svc.agent_registry.set_status(agent.id, AgentStatus.FAILED,
                                                         task_id=task.task_id, error=outcome.error)
            else:
                task.status = TaskStatus.COMPLETED
                task.result = outcome.content[:4000]
                await self.svc.agent_registry.set_status(agent.id, AgentStatus.IDLE)
            await self.svc.tasks.save(task)
            await self._record_usage(task, outcome)
        await self.svc.events.publish(
            "task.completed" if not outcome.error else "task.failed",
            {"task": task.title if task else "", "agent": agent.id},
            project_id=task.project_id, task_id=task.task_id, agent_id=agent.id,
            severity="error" if outcome.error else "info")
        return outcome

    async def _record_usage(self, task: Task, outcome: AgentRunResult) -> None:
        for usage in outcome.usage:
            await self.svc.budgets.record(usage)
            await self.svc.entity_store.save("usage", usage)
        if not outcome.model:
            return
        await self.svc.events.publish(
            "model.completed",
            {"model": outcome.model, "cost": outcome.cost,
             "calls": len(outcome.usage)},
            project_id=task.project_id, task_id=task.task_id,
            agent_id=task.assigned_agent)

    # -- graph invocation ---------------------------------------------------
    async def _invoke(self, run_id: str, state: dict) -> dict:
        graph = self.get_graph()
        config = {"configurable": {"thread_id": run_id}, "recursion_limit": 200}
        try:
            final = await graph.ainvoke(state, config=config)
        except Exception as exc:  # noqa: BLE001
            logger.exception("workflow run %s crashed", run_id)
            state["status"] = "failed"
            state["error"] = f"workflow crash: {exc}"
            final = state
        self._active_runs[run_id]["state"] = final
        return final

    def get_graph(self):
        if self._graph is None:
            from agentos.orchestration.graph import build_graph

            self._graph = build_graph(self)
        return self._graph

    # -- worker loop --------------------------------------------------------
    async def worker_loop(self, stop_event: Optional[asyncio.Event] = None) -> None:
        """Consume the task queue and run tasks (with graceful shutdown)."""
        logger.info("worker started")
        while True:
            if stop_event and stop_event.is_set():
                break
            item = await self.svc.queue.dequeue(timeout=1.0)
            if item is None:
                continue
            task_id = item.get("task_id")
            if not task_id:
                continue
            try:
                await self.run_single_task(task_id)
            except Exception as exc:  # noqa: BLE001
                logger.exception("task %s failed in worker", task_id)
                task = await self.svc.tasks.get(task_id)
                if task:
                    await self.svc.tasks.set_status(task_id, TaskStatus.FAILED, error=str(exc))
        logger.info("worker stopped")


def _slug(text: str) -> str:
    import re

    slug = re.sub(r"[^a-z0-9\s-]", "", text.lower()).strip()
    return re.sub(r"\s+", "-", slug)[:60] or "project"