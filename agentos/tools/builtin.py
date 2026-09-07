"""Built-in tools available to agents.

Every tool has a name, description, permission key, risk level and a handler.
Handlers are async functions receiving (ctx, args) where ctx exposes the
runtime context: agent, project, task, workspace, stores, services.

New tools are pluggable: register a ToolDef + handler in the ToolRegistry.
"""

from __future__ import annotations

import ast
import json
import operator
import re
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional

from agentos.domain.models import ToolDef

ToolHandler = Callable[[Any, dict], Awaitable[dict]]


def _safe_math(expr: str) -> str:
    """Evaluate a small safe subset of Python arithmetic."""
    tree = ast.parse(expr, mode="eval")
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
               ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
               ast.USub, ast.UAdd)
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError(f"unsupported expression element: {type(node).__name__}")
    return str(eval(compile(tree, "<calc>", "eval"), {"__builtins__": {}}, {}))


def _path_inside(workspace: Path, rel: str) -> Path:
    candidate = (workspace / rel).resolve()
    if not str(candidate).startswith(str(workspace.resolve())):
        raise PermissionError("path escapes workspace")
    return candidate


async def _h_filesystem_read(ctx: Any, args: dict) -> dict:
    path = _path_inside(ctx.workspace, args["path"])
    if not path.exists():
        return {"ok": False, "error": f"{path} does not exist"}
    if path.is_dir():
        return {"ok": True, "entries": sorted(p.name for p in path.iterdir())}
    content = path.read_text(errors="replace")
    return {"ok": True, "content": content[:20_000], "truncated": len(content) > 20_000}


async def _h_filesystem_write(ctx: Any, args: dict) -> dict:
    path = _path_inside(ctx.workspace, args["path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(args["content"])
    return {"ok": True, "path": str(path), "bytes": path.stat().st_size}


async def _h_shell(ctx: Any, args: dict) -> dict:
    import asyncio

    cmd = args["command"]
    read_only = not re.search(r"(;|&&|\|\||>|rm |mv |mkdir|curl -X|git push|docker compose up)", cmd)
    if not read_only and not ctx.agent.allows("shell.write"):
        return {"ok": False, "error": "write shell commands denied by permission policy"}
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        cwd=str(ctx.workspace),
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=60)
    except asyncio.TimeoutError:
        proc.kill()
        return {"ok": False, "error": "command timed out after 60s"}
    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout": out.decode(errors="replace")[-20_000:],
        "stderr": err.decode(errors="replace")[-5000:],
    }


async def _h_web_search(ctx: Any, args: dict) -> dict:
    query = args["query"]
    if ctx.services.web_search is None:
        return {"ok": False, "error": "web_search not configured (no search API key)"}
    try:
        return {"ok": True, "results": await ctx.services.web_search(query, limit=args.get("limit", 5))}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"web_search failed: {exc}"}


async def _h_calculator(ctx: Any, args: dict) -> dict:
    try:
        return {"ok": True, "result": _safe_math(args["expression"])}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


async def _h_memory_recall(ctx: Any, args: dict) -> dict:
    entries = await ctx.services.memory.recall(
        scope=args.get("scope", "project"),
        owner_id=args.get("owner_id") or (ctx.project.project_id if ctx.project else "org"),
        query=args.get("query"),
        limit=args.get("limit", 10),
    )
    return {"ok": True, "entries": [e.model_dump() for e in entries]}


async def _h_memory_save(ctx: Any, args: dict) -> dict:
    entry = await ctx.services.memory.save(
        scope=args.get("scope", "project"),
        owner_id=args.get("owner_id") or (ctx.project.project_id if ctx.project else "org"),
        kind=args.get("kind", "fact"),
        content=args["content"],
        importance=args.get("importance", 3),
    )
    return {"ok": True, "memory_id": entry.memory_id}


async def _h_project_state(ctx: Any, args: dict) -> dict:
    project = await ctx.services.projects.get(ctx.project.project_id) if ctx.project else None
    tasks = await ctx.services.tasks.by_project(ctx.project.project_id) if ctx.project else []
    return {
        "ok": True,
        "project": project.model_dump() if project else None,
        "tasks": [
            {"task_id": t.task_id, "title": t.title, "status": t.status.value,
             "assigned_agent": t.assigned_agent}
            for t in tasks
        ],
    }


async def _h_mattermost_post(ctx: Any, args: dict) -> dict:
    if ctx.services.mattermost is None:
        return {"ok": False, "error": "mattermost not configured"}
    channel = args.get("channel", "agent-status")
    message = args.get("message", "")
    await ctx.services.mattermost.post_as_agent(ctx.agent, message, channel=channel)
    return {"ok": True, "channel": channel}


async def _h_api_call(ctx: Any, args: dict) -> dict:
    if ctx.services.api_catalog is None:
        return {"ok": False, "error": "api catalog not configured"}
    return await ctx.services.api_catalog.call_api(args["api"], args.get("path", ""), args.get("params", {}))


async def _h_mcp_call(ctx: Any, args: dict) -> dict:
    if ctx.services.mcp is None:
        return {"ok": False, "error": "mcp registry not configured"}
    return await ctx.services.mcp.call_tool(args["server"], args["tool"], args.get("args", {}))


BUILTIN_TOOLS: list[ToolDef] = [
    ToolDef(name="filesystem.read", description="Read a file or list a directory inside the project workspace.",
            permission_key="filesystem.read", risk_level="low"),
    ToolDef(name="filesystem.write", description="Write a file inside the project workspace.",
            permission_key="filesystem.write", risk_level="medium"),
    ToolDef(name="shell", description="Run a shell command inside the workspace (write commands need permission).",
            permission_key="shell", risk_level="high"),
    ToolDef(name="web.search", description="Search the web. Returns ranked results with titles/URLs/snippets.",
            permission_key="web.search", risk_level="low"),
    ToolDef(name="calculator", description="Evaluate a safe arithmetic expression.",
            permission_key="calculator", risk_level="low"),
    ToolDef(name="memory.recall", description="Recall persisted memory entries (agent/project/org/task scope).",
            permission_key="memory.recall", risk_level="low"),
    ToolDef(name="memory.save", description="Persist a memory entry (fact, decision, lesson, preference).",
            permission_key="memory.save", risk_level="low"),
    ToolDef(name="project.state", description="Inspect the current project and its task list.",
            permission_key="project.state", risk_level="low"),
    ToolDef(name="mattermost.post", description="Post a message to a Mattermost channel under this agent's identity.",
            permission_key="mattermost.post", risk_level="low"),
    ToolDef(name="api.call", description="Call a registered API from the API catalog (rate-limited, logged).",
            permission_key="api.call", risk_level="medium"),
    ToolDef(name="mcp.call", description="Call a tool on a configured MCP server.",
            permission_key="mcp.call", risk_level="medium"),
]

HANDLERS: dict[str, ToolHandler] = {
    "filesystem.read": _h_filesystem_read,
    "filesystem.write": _h_filesystem_write,
    "shell": _h_shell,
    "web.search": _h_web_search,
    "calculator": _h_calculator,
    "memory.recall": _h_memory_recall,
    "memory.save": _h_memory_save,
    "project.state": _h_project_state,
    "mattermost.post": _h_mattermost_post,
    "api.call": _h_api_call,
    "mcp.call": _h_mcp_call,
}


def load_builtin_defs() -> dict[str, ToolDef]:
    return {t.name: t for t in BUILTIN_TOOLS}