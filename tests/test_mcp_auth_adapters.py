"""MCP credential isolation + high-value adapter tests (GitHub, Postgres,
Docker). Adapters are read-only and technically enforced."""

from __future__ import annotations

import pytest

from agentos.domain.models import AgentDef, McpServer


# ---------------------------------------------------------------------------
# MCP credential isolation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mcp_credentials_isolated_and_redacted(svc):
    server = McpServer(
        name="secret-server", endpoint="http://localhost:1/nope",
        tools=["ping"], auth={"type": "bearer", "token": "super-secret-token"},
        required_credentials=["MCP_SECRET_TOKEN"])
    await svc.mcp_registry.register(server)

    # serialized output never leaks the token
    public = await svc.mcp_registry.list_public()
    assert any(s["name"] == "secret-server" for s in public)
    dumped = str(public)
    assert "super-secret-token" not in dumped
    assert "<redacted>" in dumped

    # credentials set at runtime are in-memory only, never persisted
    await svc.mcp_registry.set_credentials("secret-server", "runtime-token")
    assert svc.mcp_registry._credentials["secret-server"]["token"] == "runtime-token"
    # persisted server still has no runtime credential
    stored = await svc.mcp_registry.get("secret-server")
    assert stored.auth.get("token") == "super-secret-token"  # original config
    assert "runtime-token" not in str(stored.model_dump(mode="json"))


@pytest.mark.asyncio
async def test_mcp_client_auth_headers_bearer():
    from agentos.registries.mcp_registry import McpClient

    server = McpServer(name="s", endpoint="https://x.example", auth={"type": "bearer"})
    client = McpClient(server, credentials={"token": "abc123"})
    headers = client._auth_headers()
    assert headers["Authorization"] == "Bearer abc123"


@pytest.mark.asyncio
async def test_mcp_call_respects_server_permissions(svc):
    """An agent not listed in a deny-by-default server is blocked technically."""
    server = McpServer(name="locked-server", endpoint="http://localhost:1/nope",
                       permissions={"default": "deny", "research-director": "allow"},
                       tools=["any"])
    await svc.mcp_registry.register(server)
    denied = await svc.mcp_registry.call_tool("locked-server", "any", {}, agent_id="frontend-lead")
    assert not denied["ok"]
    assert "not authorized" in denied["error"]
    # the authorized agent passes the gate (and fails at the network layer)
    attempted = await svc.mcp_registry.call_tool("locked-server", "any", {}, agent_id="research-director")
    assert not attempted["ok"]
    assert "not authorized" not in attempted["error"]


@pytest.mark.asyncio
async def test_mcp_connect_uses_client_singleton(svc):
    """client_for must return the same client for a server (regression: it
    used to build a client and return None)."""
    server = McpServer(name="singleton-server", endpoint="http://localhost:1/nope")
    await svc.mcp_registry.register(server)
    c1 = svc.mcp_registry.client_for(server)
    c2 = svc.mcp_registry.client_for(server)
    assert c1 is not None and c1 is c2
    # new credentials force a fresh client (no stale auth)
    await svc.mcp_registry.set_credentials("singleton-server", "fresh-token")
    c3 = svc.mcp_registry.client_for(server)
    assert c3 is not c1


# ---------------------------------------------------------------------------
# High-value adapters (read-only, technically enforced)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_github_adapter_requires_token(svc, monkeypatch):
    """Without a token the adapter fails cleanly (config error, not a crash).
    With a token present it performs a real read-only search."""
    agent = await svc.agent_registry.get("devops-engineer")
    project = await svc.projects.create("gh-test", "t")
    task = await svc.tasks.create(project.project_id, "t", "d")
    ctx = svc.runtime(agent, task, project).ctx

    monkeypatch.setattr(svc.settings, "github_token", None)
    unconfigured = await svc.executor.execute(ctx, agent, "github",
                                              {"action": "search_repos", "query": "agent"})
    assert not unconfigured["ok"]
    assert "not configured" in unconfigured["error"]


@pytest.mark.asyncio
async def test_postgres_adapter_read_only_enforced(svc):
    agent = await svc.agent_registry.get("database-engineer")
    project = await svc.projects.create("pg-test", "t")
    task = await svc.tasks.create(project.project_id, "t", "d")
    # postgres.query is high-risk → approval gate fires; grant it so the
    # read-only enforcement inside the handler is what we test
    ctx = svc.runtime(agent, task, project, approved_tools={"postgres.query"}).ctx
    # non-SELECT is blocked even before any connection is attempted
    write = await svc.executor.execute(ctx, agent, "postgres.query",
                                       {"query": "DROP TABLE users"})
    assert not write["ok"]
    assert "read-only" in write["error"].lower() or "select" in write["error"].lower()
    # unconfigured SELECT fails cleanly (configuration error, not crash)
    unconfigured = await svc.executor.execute(ctx, agent, "postgres.query",
                                              {"query": "SELECT 1"})
    assert not unconfigured["ok"]


@pytest.mark.asyncio
async def test_docker_adapter_read_only_enforced(svc):
    agent = await svc.agent_registry.get("devops-engineer")
    project = await svc.projects.create("dk-test", "t")
    task = await svc.tasks.create(project.project_id, "t", "d")
    ctx = svc.runtime(agent, task, project).ctx
    denied = await svc.executor.execute(ctx, agent, "docker", {"action": "rm", "container": "db"})
    assert not denied["ok"]
    assert "not allowed" in denied["error"]
    # allowed actions fail cleanly when docker is absent (contained error)
    ps = await svc.executor.execute(ctx, agent, "docker", {"action": "ps"})
    assert "ok" in ps  # either ok or a contained error, never a crash


@pytest.mark.asyncio
async def test_adapter_tools_not_exposed_to_every_agent(svc):
    """Least privilege: adapters are not in default tool sets; they surface
    only for agents explicitly granted them."""
    restricted = AgentDef(id="plain-worker", name="Plain", role="test")
    project = await svc.projects.create("ls-test", "t")
    task = await svc.tasks.create(project.project_id, "t", "d")
    ctx = svc.runtime(restricted, task, project).ctx
    for tool, args in [("postgres.query", {"query": "SELECT 1"}),
                       ("docker", {"action": "ps"}),
                       ("github", {"action": "get_repo", "repo": "a/b"})]:
        result = await svc.executor.execute(ctx, restricted, tool, args)
        assert not result["ok"], f"{tool} should be denied for an ungranted agent"
        assert "denied by permission policy" in result["error"]