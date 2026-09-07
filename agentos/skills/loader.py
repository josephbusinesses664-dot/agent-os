"""Loader for SKILL.md-compatible skill files.

A skill lives in a directory containing a SKILL.md file with YAML frontmatter
carrying the capability metadata required by the registry:

    ---
    id: market-research
    name: Market Research
    description: ...
    category: research
    version: 1.0.0
    source: ...
    license: ...
    capability_type: skill
    required_tools: [web.search]
    risk_level: low
    cost_level: low
    tags: [market, research]
    contract:
      prerequisites: ["a defined decision or hypothesis"]
      preferred_agents: [market-researcher]
      quality_gates: [...]
      ...
    ---
    # Body markdown follows — loaded lazily into agent context.

In addition to the frontmatter, the loader discovers a skill's progressive-
disclosure assets: `references/*.md` (deep material loaded only on demand)
and `evals/cases.yaml` (regression/evaluation cases consumed by the existing
benchmark runner).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

from agentos.domain.models import SkillContract, SkillDef


def _parse_contract(raw: object) -> SkillContract:
    """Tolerantly parse a `contract:` frontmatter block into a SkillContract.
    Unknown keys are dropped; a malformed block degrades to an empty
    contract rather than failing the whole skill."""
    if not isinstance(raw, dict):
        return SkillContract()
    known = SkillContract.model_fields.keys()
    cleaned = {k: v for k, v in raw.items() if k in known}
    try:
        return SkillContract(**cleaned)
    except Exception:  # noqa: BLE001
        return SkillContract()


def _discover_references(skill_dir: Path) -> list[str]:
    refs_root = skill_dir / "references"
    if not refs_root.exists():
        return []
    return sorted(p.name for p in refs_root.glob("*.md") if p.is_file())


def parse_skill_md(text: str, source_path: str = "") -> Optional[SkillDef]:
    if not text.startswith("---"):
        return None
    # closing delimiter must be `---` on its own line (frontmatter may contain
    # `---` inside code blocks, e.g. private-key markers)
    end = text.find("\n---", 3)
    if end == -1:
        return None
    meta_text = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    try:
        meta = yaml.safe_load(meta_text) or {}
    except yaml.YAMLError:
        return None
    if "id" not in meta:
        return None
    meta.setdefault("name", meta["id"])
    meta.setdefault("description", "")
    meta.setdefault("category", "uncategorized")
    meta.setdefault("version", "1.0.0")
    meta.setdefault("source", "")
    meta.setdefault("license", "")
    meta.setdefault("capability_type", "skill")
    meta.setdefault("required_tools", [])
    meta.setdefault("required_models", [])
    meta.setdefault("risk_level", "low")
    meta.setdefault("cost_level", "low")
    meta.setdefault("dependencies", [])
    meta.setdefault("compatible_agents", [])
    meta.setdefault("tags", [])
    meta.setdefault("enabled", True)
    # capability layer (executable tools, hooks, validators, ...)
    meta.setdefault("tools", [])
    meta.setdefault("hooks", {})
    meta.setdefault("validators", [])
    meta.setdefault("model_settings", {})
    meta.setdefault("permissions", {})
    meta.setdefault("examples", [])
    meta.setdefault("tests", [])
    # skill contract (machine-readable operational metadata)
    contract = _parse_contract(meta.pop("contract", None))
    skill_dir = Path(source_path).parent if source_path else Path()
    references = _discover_references(skill_dir)
    return SkillDef(body=body, source_path=source_path, contract=contract,
                    references=references, **meta)


def load_skill_dir(root: Path) -> list[SkillDef]:
    skills: list[SkillDef] = []
    if not root.exists():
        return skills
    for md in sorted(root.rglob("SKILL.md")):
        text = md.read_text(errors="replace")
        skill = parse_skill_md(text, source_path=str(md))
        if skill:
            skills.append(skill)
    return skills