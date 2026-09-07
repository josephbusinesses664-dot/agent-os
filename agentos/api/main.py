"""Control-plane REST API and admin UI.

Services resolve through a module-level holder so the same route definitions
work for the CLI server (services passed directly) and the uvicorn entry
point (services built in lifespan and stashed in the holder).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agentos.domain.models import AgentDef, McpServer, TaskStatus
from agentos.observability.health import HealthChecker

svc_holder: dict[str, Any] = {"svc": None}


class ApprovalDecision(BaseModel):
    decision: str  # approved | rejected | changes_requested
    decided_by: str = "human"
    note: str = ""


class GoalRequest(BaseModel):
    goal: str
    workflow_id: str = "zero_to_hundred"
    project_name: Optional[str] = None


class TaskCreate(BaseModel):
    project_id: str
    title: str
    description: str = ""
    assigned_agent: Optional[str] = None
    dependencies: list[str] = []
    priority: str = "normal"


class AgentCreate(BaseModel):
    id: str
    name: str
    role: str
    description: str = ""
    parent_agent: Optional[str] = None


def create_app(svc: Any) -> FastAPI:
    if svc is not None:
        svc_holder["svc"] = svc

    def S() -> Any:
        if svc_holder["svc"] is None:
            raise RuntimeError("services not initialized (start the control plane)")
        return svc_holder["svc"]

    app = FastAPI(title="Agent OS Control Plane", version="0.1.0")

    # -- health -------------------------------------------------------------
    @app.get("/api/health")
    async def health():
        reports = await HealthChecker(S()).check_all()
        return {"status": "ok", "services": [r.model_dump() for r in reports],
                "overall": HealthChecker(S()).overall(reports)}

    @app.get("/api/status")
    async def status():
        svc = S()
        agents = await svc.agent_registry.list(enabled_only=True)
        instances = await svc.agent_registry.list_instances()
        budgets = await svc.budgets.summary()
        return {
            "agents": {
                "available": len(agents),
                "active": sum(1 for i in instances if i.status.value in
                              ("working", "awaiting_approval", "awaiting_review", "blocked")),
                "instances": [i.model_dump(mode="json") for i in instances],
            },
            "skills": len(await svc.skill_registry.list()),
            "tools": len(await svc.tool_registry.list()),
            "models": len(await svc.model_registry.list()),
            "mcp": len(await svc.mcp_registry.list()),
            "apis": len(await svc.api_registry.list()),
            "workflows": len(await svc.workflow_registry.list()),
            "projects": len(await svc.projects.list()),
            "tasks": len(await svc.tasks.list()),
            "approvals_pending": len(await svc.approvals.pending()),
            "budget_spent_month": round(sum(b.get("spent_month", 0) for b in budgets), 4),
            "mattermost": bool(svc.mattermost and svc.mattermost.available),
        }

    # -- agents -------------------------------------------------------------
    @app.get("/api/agents")
    async def list_agents(enabled: bool = True):
        return [a.model_dump(mode="json") for a in
                await S().agent_registry.list(enabled_only=enabled)]

    @app.post("/api/agents")
    async def create_agent(body: AgentCreate):
        agent = AgentDef(id=body.id, name=body.name, role=body.role,
                         description=body.description, parent_agent=body.parent_agent)
        await S().agent_registry.create(agent)
        return agent.model_dump(mode="json")

    @app.patch("/api/agents/{agent_id}/enabled")
    async def set_agent_enabled(agent_id: str, enabled: bool):
        try:
            agent = await S().agent_registry.disable(agent_id, enabled=enabled)
        except KeyError as exc:
            raise HTTPException(404, str(exc)) from exc
        return agent.model_dump(mode="json")

    @app.get("/api/agent-instances")
    async def agent_instances():
        return [i.model_dump(mode="json") for i in await S().agent_registry.list_instances()]

    # -- tasks --------------------------------------------------------------
    @app.get("/api/tasks")
    async def list_tasks(project_id: Optional[str] = None, status: Optional[str] = None,
                         limit: int = 200):
        status_enum = TaskStatus(status) if status else None
        return [t.model_dump(mode="json") for t in
                await S().tasks.list(status=status_enum, project_id=project_id, limit=limit)]

    @app.post("/api/tasks")
    async def create_task(body: TaskCreate):
        task = await S().tasks.create(body.project_id, body.title, body.description,
                                      assigned_agent=body.assigned_agent,
                                      dependencies=body.dependencies, priority=body.priority)
        return task.model_dump(mode="json")

    @app.post("/api/tasks/{task_id}/run")
    async def run_task(task_id: str):
        await S().queue.enqueue({"task_id": task_id})
        return {"queued": task_id}

    # -- projects -----------------------------------------------------------
    @app.get("/api/projects")
    async def list_projects():
        return [p.model_dump(mode="json") for p in await S().projects.list()]

    @app.post("/api/projects")
    async def create_project(name: str, objective: str = ""):
        project = await S().projects.create(name, objective)
        return project.model_dump(mode="json")

    @app.get("/api/projects/{project_id}")
    async def get_project(project_id: str):
        svc = S()
        project = await svc.projects.get(project_id)
        if not project:
            raise HTTPException(404, "project not found")
        tasks = [t.model_dump(mode="json") for t in await svc.tasks.by_project(project_id)]
        return {"project": project.model_dump(mode="json"), "tasks": tasks}

    # -- goals / workflows --------------------------------------------------
    @app.post("/api/goals")
    async def execute_goal(body: GoalRequest):
        try:
            return await S().engine.execute_goal(body.goal, user_id="api",
                                                 workflow_id=body.workflow_id,
                                                 project_name=body.project_name)
        except KeyError as exc:
            raise HTTPException(404, str(exc)) from exc

    @app.get("/api/workflows")
    async def list_workflows():
        return [w.model_dump(mode="json") for w in await S().workflow_registry.list()]

    # -- skills / tools / mcp / apis / models -------------------------------
    @app.get("/api/skills")
    async def list_skills(category: Optional[str] = None):
        return [s.model_dump(mode="json") for s in
                await S().skill_registry.list(category=category)]

    @app.get("/api/tools")
    async def list_tools():
        return [t.model_dump(mode="json") for t in await S().tool_registry.list()]

    @app.get("/api/mcp")
    async def list_mcp():
        return [s.model_dump(mode="json") for s in await S().mcp_registry.list()]

    @app.post("/api/mcp")
    async def register_mcp(server: McpServer):
        await S().mcp_registry.register(server)
        return server.model_dump(mode="json")

    @app.get("/api/apis")
    async def list_apis():
        svc = S()
        return [{"api": a.model_dump(mode="json"), "evaluation": svc.api_registry.evaluate(a)}
                for a in await svc.api_registry.list()]

    @app.get("/api/models")
    async def list_models():
        return [m.model_dump(mode="json") for m in await S().model_registry.list()]

    # -- budget / usage -----------------------------------------------------
    @app.get("/api/budget")
    async def budget():
        return {"budgets": await S().budgets.summary()}

    @app.get("/api/usage")
    async def usage(limit: int = 200):
        records = await S().entity_store.list("usage", dict)
        records.sort(key=lambda r: r.get("ts", ""), reverse=True)
        return records[:limit]

    # -- events / audit -----------------------------------------------------
    @app.get("/api/events")
    async def events(limit: int = 100, event_type: Optional[str] = None):
        return [e.to_dict() for e in
                await S().events.recent(limit=limit, event_type=event_type)]

    @app.get("/api/audit")
    async def audit(limit: int = 100):
        return [e.model_dump(mode="json") for e in await S().audit.query(limit=limit)]

    # -- approvals ----------------------------------------------------------
    @app.get("/api/approvals")
    async def approvals(pending_only: bool = True):
        svc = S()
        if pending_only:
            return [a.model_dump(mode="json") for a in await svc.approvals.pending()]
        return [a.model_dump(mode="json") for a in await svc.approvals.all()]

    @app.post("/api/approvals/{approval_id}/decide")
    async def decide(approval_id: str, body: ApprovalDecision):
        try:
            result = await S().engine.approve(approval_id, body.decision,
                                              decided_by=body.decided_by, note=body.note)
        except (KeyError, ValueError) as exc:
            raise HTTPException(400, str(exc)) from exc
        return {"approval_id": approval_id, "result": result}

    # -- memory / messages --------------------------------------------------
    @app.get("/api/memory")
    async def memory(limit: int = 100):
        return [m.model_dump(mode="json") for m in await S().memory.all(limit=limit)]

    @app.get("/api/messages")
    async def messages(limit: int = 100):
        return [m.model_dump(mode="json") for m in await S().messages.recent(limit=limit)]

    # -- admin UI -----------------------------------------------------------
    static_dir = Path(__file__).resolve().parent.parent / "admin" / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    async def admin_ui():
        return FileResponse(str(static_dir / "index.html"))

    return app