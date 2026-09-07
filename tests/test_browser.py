"""Browser automation tests (Playwright-powered, Browser-Use patterns).

These exercise the real executable browser tools through the executor and the
permission system, against local file:// pages — no network required. Skipped
if Playwright/Chromium is not installed.
"""

from __future__ import annotations

import pytest

playwright = pytest.importorskip("playwright")

from pathlib import Path

from agentos.domain.models import AgentDef, ToolDef  # noqa: E402


def _browser_agent() -> AgentDef:
    return AgentDef(id="browser-tester", name="Browser Tester", role="test",
                    permissions={
                        "browser.open": "allow",
                        "browser.snapshot": "allow",
                        "browser.click": "allow",
                        "browser.type": "allow",
                        "browser.screenshot": "allow",
                        "browser.close": "allow",
                    })


@pytest.fixture
def local_page(tmp_path) -> Path:
    page = tmp_path / "index.html"
    page.write_text(
        "<!doctype html><html><head><title>Agent OS Test Page</title></head>"
        "<body><h1>Hello Agent</h1><a href='/about'>About</a>"
        "<button id='go'>Click me</button>"
        "<input id='name' placeholder='Your name'>"
        "<p>Secret payload: 42</p></body></html>")
    return page


@pytest.mark.asyncio
async def test_browser_session_open_snapshot_click(svc, local_page):
    from agentos.integrations.browser import BrowserSession

    session = BrowserSession(svc.workspace, timeout_ms=15000)
    result = await session.open(f"file://{local_page}")
    assert result["ok"], result
    assert result["title"] == "Agent OS Test Page"
    assert "Hello Agent" in result["headings"]

    snap = await session.snapshot()
    assert any("About" in l for l in snap["links"])
    assert snap["buttons"] == ["Click me"]
    assert "Secret payload: 42" in snap["text"]

    typed = await session.type_text("#name", "Buffy")
    assert typed["ok"]
    clicked = await session.click("#go")
    assert clicked["ok"]
    await session.close()


@pytest.mark.asyncio
async def test_browser_tools_via_executor_with_permissions(svc, local_page):
    """Browser tools flow through the executor: permitted agent works,
    denied agent is blocked technically."""
    agent = _browser_agent()
    project = await svc.projects.create("browser-proj", "t")
    task = await svc.tasks.create(project.project_id, "t", "d")
    ctx = svc.runtime(agent, task, project).ctx

    opened = await svc.executor.execute(ctx, agent, "browser.open",
                                        {"url": f"file://{local_page}"})
    assert opened["ok"], opened
    snap = await svc.executor.execute(ctx, agent, "browser.snapshot", {})
    assert snap["ok"] and "Hello Agent" in snap.get("text", "")
    await svc.executor.execute(ctx, agent, "browser.close", {})

    # denied agent: browser tools are denied by default (least privilege)
    denied = AgentDef(id="no-browser", name="No Browser", role="test")
    denied_project = await svc.projects.create("denied-proj", "t")
    denied_task = await svc.tasks.create(denied_project.project_id, "t", "d")
    denied_ctx = svc.runtime(denied, denied_task, denied_project).ctx
    blocked = await svc.executor.execute(denied_ctx, denied, "browser.open",
                                         {"url": f"file://{local_page}"})
    assert not blocked["ok"]
    assert "denied by permission policy" in blocked["error"]


@pytest.mark.asyncio
async def test_browser_session_scoped_to_run_and_closed(svc, local_page):
    """The runtime closes the browser when the run ends — no session outlives
    its task (isolation)."""
    agent = _browser_agent()
    project = await svc.projects.create("browser-scope", "t")
    task = await svc.tasks.create(
        project.project_id, "inspect a page",
        f"PLANNED_TOOL_CALLS: [{{\"tool\":\"browser.open\","
        f"\"args\":{{\"url\":\"file://{local_page}\"}}}}]",
        assigned_agent=agent.id)
    runtime = svc.runtime(agent, task, project)
    ctx = runtime.ctx
    outcome = await runtime.run(task)
    # the run executed the browser.open tool call → session was created…
    assert any(c.get("tool") == "browser.open" for c in outcome.tool_calls)
    # …and closed when the run ended
    assert getattr(ctx, "browser", None) is None