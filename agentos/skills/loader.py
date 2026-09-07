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
    ---
    # Body markdown follows — loaded lazily into agent context.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

from agentos.domain.models import SkillDef

FRONTMATTER_RE = None  # replaced by manual split below


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
    return SkillDef(body=body, source_path=source_path, **meta)


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