"""Capability system tests: skills carry executable tools, inline code
compiles safely, validators reject bad tool results."""

from __future__ import annotations

import pytest

from agentos.capabilities import compile_handler
from agentos.domain.models import CapabilityTool, SkillDef


@pytest.mark.asyncio
async def test_inline_capability_code_compiles_and_runs(svc):
    code = """
async def handler(ctx, args):
    return {"ok": True, "doubled": args["value"] * 2}
"""
    handler = compile_handler(code, "test-double")
    result = await handler(None, {"value": 21})
    assert result == {"ok": True, "doubled": 42}


@pytest.mark.asyncio
async def test_inline_code_has_no_host_builtins(svc):
    """Untrusted capability code must not reach file/eval host builtins."""
    code = """
async def handler(ctx, args):
    data = open("/etc/passwd").read()
    return {"ok": True, "data": data}
"""
    handler = compile_handler(code, "escape-test")
    with pytest.raises(NameError):
        await handler(None, {})
    # eval is also unavailable
    code2 = """
async def handler(ctx, args):
    return {"ok": True, "x": eval("1+1")}
"""
    handler2 = compile_handler(code2, "eval-test")
    with pytest.raises(NameError):
        await handler2(None, {})


@pytest.mark.asyncio
async def test_skill_tools_register_into_tool_registry(svc):
    skill = SkillDef(
        id="test-cap", name="Test Capability", description="executable skill",
        category="testing", body="# body",
        tools=[CapabilityTool(
            name="cap.double", description="double a number",
            handler_ref="calculator")],
    )
    await svc.capabilities.load_skill(skill)
    tool = await svc.tool_registry.get("cap.double")
    assert tool is not None
    assert tool.risk_level == "low"
    assert svc.tool_registry.handler("cap.double") is not None


@pytest.mark.asyncio
async def test_validator_can_reject_tool_result(svc):
    skill = SkillDef(
        id="strict-cap", name="Strict", description="validates results",
        category="testing", body="# body",
        validators=["""
async def validate(ctx, result):
    if result.get("ok") and "secret" in str(result.get("content", "")):
        return {"ok": False, "error": "result leaks secrets"}
    return {"ok": True}
"""],
    )
    await svc.capabilities.load_skill(skill)
    result = await svc.capabilities.validate_result(
        [skill], None, "some.tool",
        {"ok": True, "content": "here is a secret token"})
    assert result["ok"] is False
    assert "leaks secrets" in result["error"]


@pytest.mark.asyncio
async def test_skill_with_inline_code_and_validator_runs(svc):
    """The secret-scanning skill ships an executable tool + validator."""
    skill = await svc.skill_registry.get("secret-scanning")
    assert skill is not None
    assert len(skill.tools) == 1
    assert len(skill.validators) == 1
    await svc.capabilities.load_skill(skill)
    project = await svc.projects.create("scan-test", "t")
    workspace = svc.workspace / project.project_id
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "config.py").write_text('API_KEY = "sk-live-1234567890abcdef"')
    from agentos.domain.models import Task

    agent = await svc.agent_registry.get("security-reviewer")
    task = Task(task_id="t1", project_id=project.project_id, title="scan", description="")
    ctx = svc.runtime(agent, task, project).ctx
    ctx.workspace = workspace
    result = await svc.executor.execute(ctx, agent, "scan.secrets", {})
    assert result["ok"]
    assert result["count"] >= 1
    assert "sk-live" not in str(result)  # redacted by design
    # validator blocks results that leak the secret value
    leak = await svc.capabilities.validate_result(
        [skill], None, "scan.secrets",
        {"ok": True, "findings": [{"value": "sk-live-x"}]})
    assert leak["ok"] is False


@pytest.mark.asyncio
async def test_repo_search_and_db_query_executable(svc, tmp_workspace):
    project = await svc.projects.create("cap-test", "test")
    workspace = svc.workspace / project.project_id
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "notes.txt").write_text("the answer is 42 and the magic word is agent")
    import sqlite3

    conn = sqlite3.connect(str(workspace / "data.db"))
    conn.execute("CREATE TABLE items (name TEXT)")
    conn.execute("INSERT INTO items VALUES ('alpha'), ('beta')")
    conn.commit()
    conn.close()

    from agentos.domain.models import Task

    task = Task(task_id="t1", project_id=project.project_id, title="explore", description="")
    agent = await svc.agent_registry.get("executive")
    runtime = svc.runtime(agent, task, project)
    ctx = runtime.ctx
    ctx.workspace = workspace

    search = await svc.executor.execute(ctx, agent, "repo.search", {"pattern": "magic"})
    assert search["ok"] and search["count"] >= 1

    query = await svc.executor.execute(ctx, agent, "db.query",
                                       {"db": "data.db", "query": "SELECT name FROM items ORDER BY name"})
    assert query["ok"]
    assert query["rows"] == [("alpha",), ("beta",)]


@pytest.mark.asyncio
async def test_file_patch_applies_cleanly(svc, tmp_workspace):
    project = await svc.projects.create("patch-test", "test")
    workspace = svc.workspace / project.project_id
    workspace.mkdir(parents=True, exist_ok=True)
    target = workspace / "app.py"
    target.write_text("def hello():\n    return 'old'\n")
    agent = await svc.agent_registry.get("executive")
    task = await svc.tasks.create(project.project_id, "patch", "apply diff")
    ctx = svc.runtime(agent, task, project).ctx

    patch = (
        "@@ -1,3 +1,3 @@\n"
        " def hello():\n"
        "-    return 'old'\n"
        "+    return 'new'\n"
    )
    result = await svc.executor.execute(ctx, agent, "file.patch",
                                        {"path": "app.py", "patch": patch})
    assert result["ok"], result
    assert "new" in target.read_text()

    bad = await svc.executor.execute(ctx, agent, "file.patch",
                                     {"path": "app.py",
                                      "patch": "@@ -1,3 +1,3 @@\n def hello():\n-    return 'nope'\n+    return 'x'\n"})
    assert not bad["ok"]
    assert "mismatch" in bad["error"]