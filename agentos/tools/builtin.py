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
    provenance = ""
    if ctx.agent is not None:
        provenance += f"agent:{ctx.agent.id}"
    if ctx.task is not None:
        provenance += f" task:{ctx.task.task_id}"
    entry = await ctx.services.memory.save(
        scope=args.get("scope", "project"),
        owner_id=args.get("owner_id") or (ctx.project.project_id if ctx.project else "org"),
        kind=args.get("kind", "fact"),
        content=args["content"],
        importance=args.get("importance", 3),
        source=args.get("source", "agent"),
        provenance=provenance.strip(),
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


async def _h_repo_search(ctx: Any, args: dict) -> dict:
    """Search file contents under the workspace (simple recursive scan)."""
    pattern = args["pattern"].lower()
    max_results = min(int(args.get("max_results", 20)), 100)
    matches: list[dict] = []
    for path in ctx.workspace.rglob("*"):
        if path.is_dir() or not _is_text_file(path):
            continue
        try:
            text = path.read_text(errors="replace")[:100_000]
        except OSError:
            continue
        if pattern in text.lower():
            matches.append({"path": str(path.relative_to(ctx.workspace)),
                            "matches": text.lower().count(pattern)})
            if len(matches) >= max_results:
                break
    return {"ok": True, "pattern": pattern, "matches": matches,
            "count": len(matches)}


def _is_text_file(path: Path) -> bool:
    try:
        with open(path, "rb") as fh:
            return b"\x00" not in fh.read(4096)
    except OSError:
        return False


async def _h_repo_tree(ctx: Any, args: dict) -> dict:
    depth = min(int(args.get("depth", 3)), 6)
    root = ctx.workspace
    lines: list[str] = []

    def walk(directory: Path, level: int) -> None:
        if level > depth:
            return
        for child in sorted(directory.iterdir()):
            if child.name.startswith("."):
                continue
            lines.append("  " * level + ("📁 " if child.is_dir() else "📄 ") + child.name)
            if child.is_dir():
                walk(child, level + 1)

    walk(root, 0)
    return {"ok": True, "tree": lines[:300]}


async def _h_db_query(ctx: Any, args: dict) -> dict:
    """Run a read-only SQL query against a SQLite database in the workspace."""
    import sqlite3

    db_path = _path_inside(ctx.workspace, args["db"])
    if not db_path.exists():
        return {"ok": False, "error": f"database {db_path} does not exist"}
    query = args["query"].strip()
    if query.lower().lstrip().startswith(("insert", "update", "delete", "drop", "create", "alter")):
        return {"ok": False, "error": "only read-only queries allowed"}
    try:
        conn = sqlite3.connect(str(db_path))
        try:
            cur = conn.execute(query)
            columns = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchmany(min(int(args.get("limit", 50)), 200))
            return {"ok": True, "columns": columns, "rows": rows,
                    "row_count": len(rows)}
        finally:
            conn.close()
    except sqlite3.Error as exc:
        return {"ok": False, "error": f"query failed: {exc}"}


async def _h_file_patch(ctx: Any, args: dict) -> dict:
    """Apply a unified diff to a file inside the workspace (targets validated
    inside the workspace; hunks must match context exactly)."""
    target = _path_inside(ctx.workspace, args["path"])
    if not target.exists():
        return {"ok": False, "error": f"{target} does not exist"}
    patch = args.get("patch", "")
    old_lines = target.read_text(errors="replace").splitlines(keepends=True)
    try:
        new_lines = _apply_unified_diff(old_lines, patch)
    except ValueError as exc:
        return {"ok": False, "error": f"patch failed: {exc}"}
    target.write_text("".join(new_lines))
    return {"ok": True, "path": str(target), "bytes": sum(len(l) for l in new_lines)}


def _apply_unified_diff(original: list[str], patch: str) -> list[str]:
    """Apply a unified diff positionally; raise ValueError on any mismatch.

    Walks the original file forward, consuming context/removed lines exactly
    and inserting added lines — a strict three-way apply that never silently
    corrupts a file.
    """
    new_lines: list[str] = []
    idx = 0
    for hunk in _parse_hunks(patch.splitlines(keepends=True)):
        start = hunk["start"]
        if start < idx or start > len(original):
            raise ValueError("hunk start out of range/order")
        new_lines.extend(original[idx:start])
        idx = start
        for op, content in hunk["ops"]:
            if op in (" ", "-"):
                if idx >= len(original):
                    raise ValueError("patch wants more lines than the file has")
                if original[idx].rstrip("\n") != content.rstrip("\n"):
                    raise ValueError(f"line mismatch at {idx + 1}: "
                                     f"expected {original[idx].rstrip()!r}, got {content.rstrip()!r}")
                if op == " ":
                    new_lines.append(original[idx])
                idx += 1
            else:  # "+"
                new_lines.append(content)
    new_lines.extend(original[idx:])
    return new_lines


def _parse_hunks(diff_lines: list[str]) -> list[dict]:
    """Parse `@@ -a,b +c,d @@` hunks into {start, ops: [(op, content), ...]}."""
    hunks: list[dict] = []
    current: Optional[dict] = None
    for line in diff_lines:
        if line.startswith("@@"):
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            start = int(m.group(1)) - 1 if m else 0
            if current:
                hunks.append(current)
            current = {"start": max(start, 0), "ops": []}
        elif current is not None and line[:1] in (" ", "-", "+"):
            current["ops"].append((line[:1], line[1:]))
    if current:
        hunks.append(current)
    return hunks


async def _h_json_query(ctx: Any, args: dict) -> dict:
    """Query a JSON file in the workspace with a dotted path."""
    target = _path_inside(ctx.workspace, args["path"])
    if not target.exists():
        return {"ok": False, "error": f"{target} does not exist"}
    try:
        data = json.loads(target.read_text(errors="replace"))
    except json.JSONDecodeError as exc:
        return {"ok": False, "error": f"invalid JSON: {exc}"}
    path = [p for p in args.get("path_expr", "").split(".") if p]
    node: Any = data
    for part in path:
        if isinstance(node, dict) and part in node:
            node = node[part]
        elif isinstance(node, list) and part.isdigit() and int(part) < len(node):
            node = node[int(part)]
        else:
            return {"ok": False, "error": f"path segment {part} not found"}
    return {"ok": True, "result": node}


async def _h_web_scrape(ctx: Any, args: dict) -> dict:
    """Fetch a URL and return its visible text (network tool, permission-gated)."""
    import httpx

    url = args["url"]
    if not url.startswith(("http://", "https://")):
        return {"ok": False, "error": "url must be http(s)"}
    try:
        async with httpx.AsyncClient(timeout=25, follow_redirects=True,
                                     headers={"User-Agent": "agent-os/0.1"}) as client:
            resp = await client.get(url)
            resp.raise_for_status()
        text = re.sub(r"<script.*?</script>|<style.*?</style>", "", resp.text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return {"ok": True, "url": url, "status": resp.status_code,
                "text": text[:12_000], "truncated": len(text) > 12_000}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"scrape failed: {exc}"}


async def _h_git(ctx: Any, args: dict) -> dict:
    """Read-only git introspection inside the workspace."""
    import asyncio

    cmd = args.get("command", "status")
    allowed = ("status", "log", "diff", "branch", "remote", "show")
    if cmd not in allowed:
        return {"ok": False, "error": f"git.{cmd} not allowed (read-only: {', '.join(allowed)})"}
    proc = await asyncio.create_subprocess_exec(
        "git", cmd, "--no-pager" if cmd in ("log", "diff") else None,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        cwd=str(ctx.workspace),
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=30)
    except asyncio.TimeoutError:
        proc.kill()
        return {"ok": False, "error": "git command timed out"}
    return {"ok": proc.returncode == 0, "exit_code": proc.returncode,
            "stdout": out.decode(errors="replace")[-12_000:],
            "stderr": err.decode(errors="replace")[-3000:]}


async def _h_tool_discover(ctx: Any, args: dict) -> dict:
    """Discover tools relevant to a capability need (keeps tool lists small)."""
    tools = await ctx.services.tools.discover(
        args.get("query", ""), agent=ctx.agent, limit=args.get("limit", 10))
    return {"ok": True, "tools": [
        {"name": t.name, "description": t.description, "risk": t.risk_level}
        for t in tools
    ]}


async def _h_tool_health(ctx: Any, args: dict) -> dict:
    report = await ctx.services.tools.health(args.get("tool", ""))
    return {"ok": True, "report": report}


async def _h_agent_delegate(ctx: Any, args: dict) -> dict:
    """Delegate a subtask to a child agent. Bounded by engine spawn limits
    (depth, parallelism, budget, duplicate detection)."""
    child = args.get("agent", "")
    description = args.get("description", "")
    if not child or not description:
        return {"ok": False, "error": "agent and description are required"}
    if ctx.task is None:
        return {"ok": False, "error": "delegation requires a parent task"}
    # only the child's parent (or an explicitly permitted agent) may delegate.
    # The permission must be EXPLICIT — the default-allow policy does not
    # apply to delegation.
    child_def = await ctx.agent_registry.get(child)
    if child_def is None:
        return {"ok": False, "error": f"unknown agent {child}"}
    permitted = (child_def.parent_agent == ctx.agent.id
                 or ctx.agent.permissions.get("agent.delegate", "deny") == "allow")
    if not permitted:
        return {"ok": False, "error": f"{ctx.agent.id} may not delegate to {child}"}
    try:
        child_result = await ctx.services.engine.spawn_subagent(
            ctx.task, child, description, depth=ctx.spawn_depth + 1)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"delegation failed: {exc}"}
    return {"ok": True, "child": child, "result": child_result.content[:4000],
            "error": child_result.error, "artifacts": child_result.artifacts,
            "cost": child_result.cost}


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
    ToolDef(name="repo.search", description="Search file contents under the project workspace.",
            permission_key="repo.search", risk_level="low", category="capability"),
    ToolDef(name="repo.tree", description="List the project workspace file tree.",
            permission_key="repo.tree", risk_level="low", category="capability"),
    ToolDef(name="db.query", description="Run a read-only SQL query against a SQLite DB in the workspace.",
            permission_key="db.query", risk_level="medium", category="capability"),
    ToolDef(name="file.patch", description="Apply a unified diff to a file inside the workspace (must apply cleanly).",
            permission_key="file.patch", risk_level="medium", category="capability"),
    ToolDef(name="json.query", description="Query a JSON file in the workspace with a dotted path.",
            permission_key="json.query", risk_level="low", category="capability"),
    ToolDef(name="web.scrape", description="Fetch a URL and extract visible text (network).",
            permission_key="web.scrape", risk_level="medium", category="capability"),
    ToolDef(name="git.status", description="Read-only git introspection (status/log/diff/branch).",
            permission_key="git.status", risk_level="low", category="capability"),
    ToolDef(name="tool.discover", description="Discover which tools suit a capability need.",
            permission_key="tool.discover", risk_level="low", category="system"),
    ToolDef(name="tool.health", description="Check a tool's health/availability.",
            permission_key="tool.health", risk_level="low", category="system"),
    ToolDef(name="agent.delegate", description="Delegate a bounded subtask to a child agent (depth/parallel/budget limited).",
            permission_key="agent.delegate", risk_level="medium", category="system"),
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
    "repo.search": _h_repo_search,
    "repo.tree": _h_repo_tree,
    "db.query": _h_db_query,
    "file.patch": _h_file_patch,
    "json.query": _h_json_query,
    "web.scrape": _h_web_scrape,
    "git.status": _h_git,
    "tool.discover": _h_tool_discover,
    "tool.health": _h_tool_health,
    "agent.delegate": _h_agent_delegate,
}


def load_builtin_defs() -> dict[str, ToolDef]:
    return {t.name: t for t in BUILTIN_TOOLS}