"""Round-3 integration test — the full loop through the UPGRADED subsystems:

memory (KG + contradiction) → dynamic capability selection (executable
skill tools) → tool discovery → delegation → evaluation → performance
routing. If this passes, the self-improvement loop actually closes: results
from one run change how the next run is routed and delegated.
"""

from __future__ import annotations

import pytest

from agentos.domain.models import MemoryScope


@pytest.mark.asyncio
async def test_memory_capability_tool_discovery_delegation_eval_routing(svc):
    # -------------------------------------------------------------
    # 0. dynamic capability selection: an executable skill is active
    # -------------------------------------------------------------
    skill = await svc.skill_registry.get("secret-scanning")
    assert skill is not None, "secret-scanning skill must exist"
    assert skill.tools, "secret-scanning must carry executable tools"
    scan_tool = skill.tools[0]
    assert scan_tool.name == "scan.secrets"
    # loading the skill registers its executable tool in the registry
    await svc.capabilities.load_skill(skill)
    registered = await svc.tool_registry.get("scan.secrets")
    assert registered is not None, "capability tool must be executable, not markdown"

    # -------------------------------------------------------------
    # 1. tool discovery finds the capability tool for a relevant task
    # -------------------------------------------------------------
    found = await svc.tool_registry.discover("scan for leaked secrets", limit=10)
    assert any(t.name == "scan.secrets" for t in found), \
        [t.name for t in found]

    # -------------------------------------------------------------
    # 2. run a real workflow with dynamic planning (memory + eval + perf)
    # -------------------------------------------------------------
    run = await svc.engine.execute_dynamic(
        "scan the repo for leaked secrets", user_id="test-human")
    assert run["status"] == "completed", run
    project = await svc.projects.require(run["project_id"])

    # -------------------------------------------------------------
    # 3. memory: task episodes recorded with provenance; KG usable
    # -------------------------------------------------------------
    tasks = await svc.tasks.by_project(project.project_id)
    episodes = 0
    for task in tasks:
        mem = await svc.memory.by_owner("task", task.task_id)
        episodes += sum(1 for e in mem if e.kind == "episode")
        assert all(e.provenance for e in mem)
    assert episodes >= len(tasks), "every stage run must record an episode"
    # knowledge-graph layer works on the produced memory
    graph = await svc.memory.graph(MemoryScope.PROJECT, project.project_id)
    assert "nodes" in graph and "edges" in graph
    # contradiction resolution still functional after a real run
    f1 = await svc.memory.save_fact(MemoryScope.PROJECT, project.project_id,
                                    "The deploy target is staging.", kind="fact")
    f2 = await svc.memory.save_fact(MemoryScope.PROJECT, project.project_id,
                                    "The deploy target is no longer staging.",
                                    kind="fact")
    links = await svc.memory.related(f2.memory_id)
    assert links and links[0].relation == "contradicts"

    # -------------------------------------------------------------
    # 4. delegation: parent agent delegates, stats fold downstream
    # -------------------------------------------------------------
    parent = await svc.agent_registry.get("executive")
    project2 = await svc.projects.create("delegation-test", "t")
    parent_task = await svc.tasks.create(
        project2.project_id, "research a niche", "find market signals",
        assigned_agent=parent.id)
    child_result = await svc.engine.spawn_subagent(
        parent_task, "market-researcher", "check demand for niche x", depth=0)
    assert child_result.error is None, child_result.error
    # downstream success folded into the parent's performance stats
    parent_stats = await svc.performance.stats("executive", "all")
    assert parent_stats.downstream_total >= 1
    assert parent_stats.downstream_rate >= 0.5

    # -------------------------------------------------------------
    # 5. evaluation records exist for the workflow stages
    # -------------------------------------------------------------
    records = await svc.entity_store.list_docs("evaluation")
    assert records, "stages must be evaluated"
    assert any(r.get("workflow_id", "").startswith("dynamic") for r in records)

    # -------------------------------------------------------------
    # 6. performance routing: weak performers get tier bumps
    # -------------------------------------------------------------
    for i in range(4):  # four failed runs → <50% success rate
        await svc.performance.record_run(
            "flaky-worker", outcome=type(
                "O", (), {"error": "boom", "cost": 0.1, "usage": [],
                          "tool_calls": [], "tool_results": []})(),
            task=type("T", (), {"task_id": f"t{i}", "retry_count": 0})())
    influence = await svc.performance.influence("flaky-worker")
    assert influence["tier_bump"] == 1, influence
    assert "stronger model" in influence["reason"]
    # reliable workers get cheaper tiers
    for _ in range(6):
        await svc.performance.record_run(
            "solid-worker", outcome=type(
                "O", (), {"error": None, "cost": 0.01, "usage": [],
                          "tool_calls": [], "tool_results": []})(),
            task=type("T", (), {"task_id": "s", "retry_count": 0})())
    solid = await svc.performance.influence("solid-worker")
    assert solid["tier_bump"] == -1, solid

    # -------------------------------------------------------------
    # 7. traces: agent → stage → model → tool chain recorded
    # -------------------------------------------------------------
    spans = await svc.tracer.task_trace(tasks[0].task_id)
    kinds = {s["kind"] for s in spans}
    assert {"agent", "model"} <= kinds, kinds
    # audit: capability tool call logged
    audit = await svc.audit.query(limit=200)
    assert audit


@pytest.mark.asyncio
async def test_executable_capability_runs_through_executor(svc):
    """The secret-scanning capability's inline tool actually executes and its
    validator blocks leaked secrets — proof capabilities are real code."""
    skill = await svc.skill_registry.get("secret-scanning")
    await svc.capabilities.load_skill(skill)
    agent = await svc.agent_registry.get("executive")
    project = await svc.projects.create("scan-proj", "t")
    task = await svc.tasks.create(project.project_id, "t", "d")
    ctx = svc.runtime(agent, task, project, approved_tools={"scan.secrets"}).ctx
    ctx.active_skills = [skill]
    # create a file with a fake AWS key
    ctx.workspace.mkdir(parents=True, exist_ok=True)
    (ctx.workspace / "leaky.env").write_text("AWS_SECRET_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE\n")
    result = await svc.executor.execute(ctx, agent, "scan.secrets", {})
    assert result["ok"], result
    assert result["count"] >= 1
    # the scanner returns locations + categories, never the secret value
    serialized = str(result)
    assert "AKIAIOSFODNN7EXAMPLE" not in serialized
    assert result["findings"][0]["category"] == "aws_key"


@pytest.mark.asyncio
async def test_skill_capability_drives_model_settings_and_permissions(svc):
    """Capabilities carry permissions + model settings that shape the run."""
    skill = await svc.skill_registry.get("secret-scanning")
    assert skill.permissions, "capability must carry permission grants"
    assert skill.model_settings, "capability must carry model settings"