"""Round-3 memory tests: knowledge-graph links, contradiction resolution,
temporal validity and consolidation (Graphiti/Mem0-inspired patterns)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from agentos.domain.models import MemoryScope


@pytest.mark.asyncio
async def test_contradiction_resolution_links(svc):
    """A newer statement that negates the old one archives the old entry and
    records a `contradicts` relationship (history is never silently lost)."""
    f1 = await svc.memory.save_fact(MemoryScope.PROJECT, "prj-x",
                                    "Deploy target is staging.", kind="fact",
                                    source="agent")
    f2 = await svc.memory.save_fact(MemoryScope.PROJECT, "prj-x",
                                    "Deploy target is no longer staging; it is production.",
                                    kind="fact", source="agent")
    # old archived, new linked
    old = await svc.memory.get(f1.memory_id)
    assert old.archived
    assert f2.supersedes == f1.memory_id
    links = await svc.memory.related(f2.memory_id)
    assert links and links[0].relation == "contradicts"
    # recall only surfaces the current fact
    hits = await svc.memory.recall(MemoryScope.PROJECT, "prj-x",
                                   query="where do we deploy", limit=5)
    assert len(hits) == 1
    assert "production" in hits[0].content


@pytest.mark.asyncio
async def test_evolution_is_supersede_not_contradiction(svc):
    """Plain evolution ('staging' → 'production') is a supersede, not a
    contradiction — the relation distinguishes the two cases."""
    f1 = await svc.memory.save_fact(MemoryScope.PROJECT, "prj-x",
                                    "Deploy target is staging.", kind="fact")
    f2 = await svc.memory.save_fact(MemoryScope.PROJECT, "prj-x",
                                    "Deploy target is now production.", kind="fact")
    links = await svc.memory.related(f2.memory_id)
    assert links and links[0].relation == "supersedes"
    assert f2.supersedes == f1.memory_id


@pytest.mark.asyncio
async def test_exact_restatement_refreshes_not_duplicates(svc):
    f1 = await svc.memory.save_fact(MemoryScope.PROJECT, "prj-x",
                                    "Use FastAPI for the API layer.", kind="decision",
                                    importance=3)
    f2 = await svc.memory.save_fact(MemoryScope.PROJECT, "prj-x",
                                    "Use FastAPI for the API layer.", kind="decision",
                                    importance=5)
    assert f2.memory_id == f1.memory_id
    active = [e for e in await svc.memory.by_owner("project", "prj-x")
              if not e.archived]
    assert len(active) == 1


@pytest.mark.asyncio
async def test_knowledge_graph_links_and_neighbors(svc):
    f1 = await svc.memory.save(MemoryScope.PROJECT, "prj-x",
                               "The API is deployed on staging.", kind="fact",
                               importance=4, source="agent")
    f2 = await svc.memory.save(MemoryScope.PROJECT, "prj-x",
                               "The database runs in the same VPC as staging.",
                               kind="fact", importance=3, source="tool")
    await svc.memory.link(f1.memory_id, f2.memory_id, "applies_to",
                          {"why": "shared environment"})
    neighbors = await svc.memory.neighbors(f1.memory_id)
    assert len(neighbors) == 1
    assert neighbors[0][0] == f2.memory_id
    graph = await svc.memory.graph(MemoryScope.PROJECT, "prj-x")
    assert len(graph["nodes"]) == 2
    assert graph["edges"] and graph["edges"][0]["relation"] == "applies_to"


@pytest.mark.asyncio
async def test_temporal_validity_filters_recall(svc):
    """Facts with a validity window are only recalled while valid; expired
    facts are archived (never silently deleted) and excluded from recall."""
    future = datetime.now(timezone.utc) + timedelta(days=30)
    past = datetime.now(timezone.utc) - timedelta(days=30)
    await svc.memory.save(MemoryScope.PROJECT, "prj-x",
                          "Launch window opens next month.", kind="fact",
                          importance=4, valid_from=future)
    await svc.memory.save(MemoryScope.PROJECT, "prj-x",
                          "Old pricing expires.", kind="fact",
                          importance=4, valid_to=past)
    await svc.memory.save(MemoryScope.PROJECT, "prj-x",
                          "Current stack is React.", kind="fact", importance=4)
    hits = await svc.memory.recall(MemoryScope.PROJECT, "prj-x", limit=10)
    contents = " ".join(e.content for e in hits)
    assert "Current stack is React" in contents
    assert "Launch window" not in contents
    assert "Old pricing" not in contents


@pytest.mark.asyncio
async def test_timeline_orders_by_validity(svc):
    await svc.memory.save(MemoryScope.PROJECT, "prj-x", "Phase 1 complete.",
                          kind="episode", importance=2)
    await svc.memory.save(MemoryScope.PROJECT, "prj-x", "Phase 2 complete.",
                          kind="episode", importance=2)
    timeline = await svc.memory.timeline(MemoryScope.PROJECT, "prj-x")
    contents = [e.content for e in timeline]
    assert contents.index("Phase 1 complete.") < contents.index("Phase 2 complete.")


@pytest.mark.asyncio
async def test_provenance_chain_preserved(svc):
    entry = await svc.memory.save_fact(
        MemoryScope.PROJECT, "prj-x", "The API contract is v2.",
        kind="fact", source="agent",
        provenance="agent:backend-lead task:task_abc")
    assert entry.source == "agent"
    assert "agent:backend-lead" in entry.provenance
    assert "task_abc" in entry.provenance