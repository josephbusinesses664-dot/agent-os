"""Registry tests."""

import pytest

from agentos.domain.models import AgentDef, ApiDef, McpServer, ModelDef, SkillDef, ToolDef


@pytest.mark.asyncio
async def test_agent_registry_crud(svc):
    reg = svc.agent_registry
    agent = AgentDef(id="test-agent", name="Test Agent", role="tester",
                     parent_agent="executive")
    await reg.create(agent)
    found = await reg.get("test-agent")
    assert found is not None and found.role == "tester"
    await reg.disable("test-agent", enabled=False)
    assert (await reg.get("test-agent")).enabled is False
    disabled = [a for a in await reg.list(enabled_only=True) if a.id == "test-agent"]
    assert disabled == []


@pytest.mark.asyncio
async def test_org_hierarchy_seeded(svc):
    agents = await svc.agent_registry.list()
    assert len(agents) >= 12
    ids = {a.id for a in agents}
    for required in ("executive", "cto", "project-manager", "frontend-lead",
                     "test-engineer", "security-reviewer", "deployment-agent"):
        assert required in ids
    executive = await svc.agent_registry.get("executive")
    assert executive.parent_agent is None
    # children of executive include the directors
    children = {a.id for a in svc.agent_registry.children_of("executive")}
    assert {"cto", "design-director", "qa-director"}.issubset(children)


@pytest.mark.asyncio
async def test_skill_registry_search_ranking(svc):
    hits = await svc.skill_registry.search("market research demand validation",
                                           agent_id="market-researcher", limit=5)
    ids = [s.id for s in hits]
    assert "market-research" in ids
    assert "demand-validation" in ids
    # the most relevant skill ranks first
    assert ids[0] == "market-research"


@pytest.mark.asyncio
async def test_skill_progressive_loading(svc):
    loaded = await svc.skill_registry.load_for_agent("community-researcher",
                                                     "reddit pain points community", limit=4)
    ids = [s.id for s in loaded]
    assert "community-intelligence" in ids
    for skill in loaded:
        assert skill.body  # full bodies loaded only for selected skills


@pytest.mark.asyncio
async def test_skill_enable_disable(svc):
    skill = await svc.skill_registry.enable("market-research", enabled=False)
    assert skill.enabled is False
    hits = await svc.skill_registry.search("market research")
    assert "market-research" not in [s.id for s in hits]
    await svc.skill_registry.enable("market-research", enabled=True)


@pytest.mark.asyncio
async def test_skill_categories_cover_20_branches(svc):
    categories = await svc.skill_registry.categories()
    assert len(categories) >= 20, categories


@pytest.mark.asyncio
async def test_tool_registry(svc):
    tool = await svc.tool_registry.get("web.search")
    assert tool is not None and tool.permission_key == "web.search"
    assert svc.tool_registry.handler("calculator") is not None
    # register a custom tool
    await svc.tool_registry.register(
        ToolDef(name="echo.test", description="test"), handler=None)
    assert await svc.tool_registry.get("echo.test") is not None


@pytest.mark.asyncio
async def test_model_registry_tiers(svc):
    models = await svc.model_registry.list()
    tiers = {m.tier for m in models}
    assert {"t0", "t1", "t2", "t3"}.issubset(tiers)
    t1 = await svc.model_registry.by_tier("t1")
    assert all(m.tier == "t1" for m in t1)
    # echo always available (offline)
    echo = await svc.model_registry.get("echo")
    assert echo is not None


@pytest.mark.asyncio
async def test_api_registry_evaluation(svc):
    apis = await svc.api_registry.list()
    assert len(apis) >= 5
    hn = await svc.api_registry.get("hackernews")
    assert hn is not None
    ev = svc.api_registry.evaluate(hn)
    assert ev["score"] > 3 and ev["verdict"] in ("recommended", "conditional")


@pytest.mark.asyncio
async def test_mcp_registry(svc):
    await svc.mcp_registry.register(McpServer(name="mock", transport="streamable-http",
                                              endpoint="http://localhost:1/mcp"))
    assert await svc.mcp_registry.get("mock") is not None
    # unknown server call fails gracefully
    result = await svc.mcp_registry.call_tool("nope", "x", {})
    assert result["ok"] is False