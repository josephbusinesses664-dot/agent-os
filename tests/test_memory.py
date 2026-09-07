"""Layered memory tests: multi-entry storage, semantic recall, fact
extraction, versioned facts, episodes, consolidation."""

from __future__ import annotations

import pytest

from agentos.agents.runtime import AgentRunResult


@pytest.mark.asyncio
async def test_multiple_entries_per_owner(svc):
    """The old store kept ONE entry per (scope, owner) — regression guard."""
    await svc.memory.save("project", "prj1", "first fact", kind="fact")
    await svc.memory.save("project", "prj1", "second fact", kind="fact")
    await svc.memory.save("project", "prj1", "a decision", kind="decision")
    entries = await svc.memory.by_owner("project", "prj1")
    assert len(entries) == 3


@pytest.mark.asyncio
async def test_semantic_recall_ranks_relevant(svc):
    await svc.memory.save("project", "prj1", "We chose FastAPI for the API layer.", kind="decision", importance=4)
    await svc.memory.save("project", "prj1", "The marketing budget is 5k.", kind="fact", importance=2)
    await svc.memory.save("project", "prj1", "Lesson: pin dependencies in CI.", kind="lesson", importance=3)
    top = await svc.memory.recall("project", "prj1", query="which web framework did we pick", limit=1)
    assert len(top) == 1
    assert "FastAPI" in top[0].content


@pytest.mark.asyncio
async def test_versioned_facts_supersede(svc):
    await svc.memory.save_fact("project", "prj1", "Deploy target is staging now.", kind="fact")
    await svc.memory.save_fact("project", "prj1", "The deploy target is staging, updated.", kind="fact")
    entries = await svc.memory.by_owner("project", "prj1")
    active = [e for e in entries if not e.archived]
    archived = [e for e in entries if e.archived]
    assert len(active) == 1
    assert len(archived) == 1
    assert active[0].supersedes == archived[0].memory_id


@pytest.mark.asyncio
async def test_fact_extraction_from_markers(svc):
    task = await svc.tasks.create("prj1", "Build the landing page", "frontend work")
    outcome = AgentRunResult(
        content=("Completed. Decision: use Tailwind for styling.\n"
                 "Lesson: run Lighthouse before shipping."),
        artifacts=["landing/index.html"], model="echo")
    saved = await svc.memory.extract_facts(task, outcome, "frontend-lead")
    kinds = {e.kind for e in saved}
    assert "decision" in kinds
    assert "lesson" in kinds
    for entry in saved:
        assert "agent:frontend-lead" in entry.provenance


@pytest.mark.asyncio
async def test_episodes_recorded_and_retrievable(svc):
    task = await svc.tasks.create("prj1", "Implement auth", "add login flow")
    outcome = AgentRunResult(content="done", artifacts=["auth.py"], model="echo")
    episode = await svc.memory.record_episode(task, outcome, "backend-lead")
    assert episode.kind == "episode"
    found = await svc.memory.recall("task", task.task_id, query="implement auth", limit=3, kinds=["episode"])
    assert any("Implement auth" in e.content for e in found)


@pytest.mark.asyncio
async def test_recall_for_task_pulls_all_layers(svc):
    await svc.memory.save("project", "prj1", "Stack decision: React + FastAPI.", kind="decision", importance=4)
    await svc.memory.save("agent", "frontend-lead", "Prefers shadcn components.", kind="preference", importance=3)
    await svc.memory.save("org", "org", "Never commit secrets.", kind="instruction", importance=5)
    task = await svc.tasks.create("prj1", "Build settings page", "React frontend for user settings, no secrets")
    entries = await svc.memory.recall_for_task(task, "frontend-lead", limit=10)
    scopes = {e.scope.value for e in entries}
    assert scopes == {"project", "agent", "org"}
    contents = " ".join(e.content for e in entries).lower()
    assert "react" in contents


@pytest.mark.asyncio
async def test_consolidation_archives_stale_and_merges_dupes(svc):
    from datetime import datetime, timedelta, timezone

    await svc.memory.save("project", "prj1", "Old stale note.", kind="fact", importance=1)
    entries = await svc.memory.by_owner("project", "prj1")
    # age the first entry artificially
    old = entries[0]
    old.updated_at = datetime.now(timezone.utc) - timedelta(days=60)
    old.access_count = 0
    await svc.entity_store.save("memory", old)
    # exact duplicates
    await svc.memory.save("project", "prj1", "Use uv for python.", kind="fact", importance=4)
    await svc.memory.save("project", "prj1", "use uv for python.", kind="fact", importance=2)
    result = await svc.memory.consolidate("project", "prj1", max_age_days=30)
    assert result["archived"] >= 1
    assert result["merged"] >= 1
    # archived entries never surface in recall
    hits = await svc.memory.recall("project", "prj1", query="uv python", limit=10)
    assert all(not e.archived for e in hits)


@pytest.mark.asyncio
async def test_remember_if_important_hygiene(svc):
    assert await svc.memory.remember_if_important("org", "org", "noise", importance=1) is None
    entry = await svc.memory.remember_if_important("org", "org", "real lesson", importance=3)
    assert entry is not None