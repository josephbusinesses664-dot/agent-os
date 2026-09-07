"""Skill-contract upgrade tests (Phase 22).

Covers: contract parsing, progressive-disclosure assets (references +
evals), malformed/incomplete skill metadata tolerance, compound-id search,
and executor propagation of capability validator failures.
"""

from __future__ import annotations

import textwrap

import pytest

from agentos.skills.loader import parse_skill_md
from agentos.skills.search import tokenize


# ---------------------------------------------------------------------------
# Frontmatter / contract parsing
# ---------------------------------------------------------------------------

def _skill_md(frontmatter: str, body: str = "# Body\n") -> str:
    return f"---\n{frontmatter}\n---\n\n{body}"


def test_contract_block_parses_into_skill_contract():
    text = _skill_md(textwrap.dedent("""\
        id: probe-skill
        name: Probe
        description: testing contract parsing
        category: testing
        contract:
          prerequisites: ["a question"]
          preferred_agents: [analyst]
          minimum_model_capability: t2
          quality_gates: ["done means done"]
          verification: ["check the artifacts"]
          failure_modes:
            no_evidence: "lower confidence"
          handoff_out: ["findings"]
          related_skills: [other-skill]
    """))
    skill = parse_skill_md(text, "skills/x/probe-skill/SKILL.md")
    assert skill is not None
    assert skill.contract.prerequisites == ["a question"]
    assert skill.contract.preferred_agents == ["analyst"]
    assert skill.contract.minimum_model_capability == "t2"
    assert skill.contract.failure_modes == {"no_evidence": "lower confidence"}
    assert skill.contract.related_skills == ["other-skill"]
    # unknown contract keys are dropped, not stored
    dumped = skill.contract.model_dump()
    assert dumped  # non-empty contract


def test_malformed_contract_degrades_to_empty():
    from agentos.domain.models import SkillContract
    text = _skill_md(textwrap.dedent("""\
        id: probe-skill
        name: Probe
        description: broken contract
        category: testing
        contract: 42
    """))
    skill = parse_skill_md(text)
    assert skill is not None
    assert skill.contract.model_dump() == SkillContract().model_dump()


def test_skill_without_contract_still_loads():
    from agentos.domain.models import SkillContract
    text = _skill_md("id: minimal\nname: Minimal\ndescription: x\ncategory: testing")
    skill = parse_skill_md(text)
    assert skill is not None
    assert skill.id == "minimal"
    assert skill.contract.model_dump() == SkillContract().model_dump()


def test_missing_id_rejects_skill():
    text = _skill_md("name: NoId\ndescription: x\ncategory: testing")
    assert parse_skill_md(text) is None


def test_broken_yaml_rejects_skill():
    assert parse_skill_md("---\nid: [unclosed\nname: x\n---\nbody") is None


def test_frontmatter_with_inner_dashes_survives():
    text = "---\nid: probe\ndescription: |\n  a\n  ---\n  b\nname: P\ncategory: t\n---\nbody"
    skill = parse_skill_md(text)
    assert skill is not None and skill.id == "probe"


def test_references_discovered_from_disk(tmp_path):
    d = tmp_path / "probe-skill"
    d.mkdir()
    (d / "references").mkdir()
    (d / "references" / "methodology.md").write_text("# m")
    (d / "references" / "pitfalls.md").write_text("# p")
    (d / "evals").mkdir()
    (d / "evals" / "cases.yaml").write_text("cases: []\n")
    skill = parse_skill_md(
        _skill_md("id: probe-skill\nname: P\ndescription: x\ncategory: t"),
        str(d / "SKILL.md"))
    assert skill.references == ["methodology.md", "pitfalls.md"]


# ---------------------------------------------------------------------------
# Search: compound ids and deterministic ranking
# ---------------------------------------------------------------------------

def test_tokenize_splits_compound_tokens():
    tokens = tokenize("demand-validation market-research")
    assert "demand-validation" in tokens
    assert "demand" in tokens and "validation" in tokens
    assert "market" in tokens and "research" in tokens


def test_tokenize_drops_stopwords():
    assert "the" not in tokenize("the market")
    assert "build" not in tokenize("build a thing")


@pytest.mark.asyncio
async def test_search_matches_hyphenated_ids_by_word(svc):
    """A query word must match a hyphenated skill id ('user stories' ->
    user-stories) — regression test for the dead id-weight bug."""
    hits = await svc.skill_registry.search("user stories", limit=3)
    assert hits, "no hits for 'user stories'"
    assert hits[0].id == "user-stories"


# ---------------------------------------------------------------------------
# Registry + progressive disclosure integration (real skills/ tree)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_seeded_skills_carry_contract_fields(svc):
    skill = await svc.skill_registry.get("reddit-research")
    assert skill is not None
    assert skill.contract.quality_gates, "reddit-research must define quality gates"
    assert skill.contract.failure_modes, "reddit-research must define failure modes"
    assert "demand-validation" in skill.dependencies


@pytest.mark.asyncio
async def test_progressive_disclosure_references_roundtrip(svc):
    names = await svc.skill_registry.list_references("reddit-research")
    assert "signal-examples.md" in names
    content = await svc.skill_registry.load_reference("reddit-research", "signal-examples.md")
    assert content and "Workaround" in content
    # unknown reference -> None, no crash
    assert await svc.skill_registry.load_reference("reddit-research", "nope.md") is None
    assert await svc.skill_registry.load_reference("no-such-skill", "x.md") is None


@pytest.mark.asyncio
async def test_skill_evals_load_through_existing_runner(svc):
    from agentos.evaluation.datasets import load_dataset
    ds = load_dataset("skill:reddit-research")
    assert ds is not None and len(ds.items) == 4
    titles = {c.title for c in ds.items}
    assert "Separate complaint from buying intent" in titles
    ds2 = load_dataset("skill:demand-validation")
    assert ds2 is not None and len(ds2.items) == 4
    assert await svc.skill_registry.load_evals("market-research") is not None


@pytest.mark.asyncio
async def test_unknown_skill_reference_never_loads(svc):
    skill = await svc.skill_registry.get("reddit-research")
    assert skill is not None
    from pathlib import Path
    missing = Path(skill.source_path).parent / "references" / "../evals/cases.yaml"
    # path traversal-ish name is not in the whitelist -> refused
    assert "../evals/cases.yaml" not in skill.references


# ---------------------------------------------------------------------------
# Validator failure propagates independently of execution success
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_capability_validator_failure_propagates(svc):
    """A failing validator must flip a successful tool result to failure."""
    from agentos.domain.models import SkillDef
    skill = SkillDef(
        id="guard-skill", name="Guard", description="validates",
        category="testing", body="# b",
        validators=["""async def validate(ctx, result):
    if result.get("ok"):
        return {"ok": False, "error": "blocked by guard"}
    return {"ok": True}"""])
    await svc.capabilities.load_skill(skill)
    result = await svc.capabilities.validate_result(
        [skill], None, "any.tool", {"ok": True, "data": 1})
    assert result["ok"] is False
    assert result["validation_failed"] is True
    assert "blocked by guard" in result["error"]


@pytest.mark.asyncio
async def test_validator_crash_fails_closed(svc):
    from agentos.domain.models import SkillDef
    skill = SkillDef(
        id="crash-skill", name="Crash", description="x",
        category="testing", body="# b",
        validators=["""async def validate(ctx, result):
    raise RuntimeError("boom")"""])
    await svc.capabilities.load_skill(skill)
    result = await svc.capabilities.validate_result([skill], None, "t", {"ok": True})
    assert result["ok"] is False
    assert "validator crashed" in result["error"]
