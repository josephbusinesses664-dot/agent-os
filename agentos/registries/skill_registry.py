"""Skill Registry.

Supports discovery, metadata, categories, versioning, dependencies,
activation/deactivation, compatibility, model recommendations, cost/risk
classification and progressive loading (only relevant skills enter context).

Progressive disclosure (skill-contract upgrade): SKILL.md bodies stay compact;
deep material lives in `references/*.md` per skill and is loaded only on
demand via `load_reference`. Evaluation/regression cases live in
`evals/cases.yaml` per skill and feed the existing benchmark runner via
`load_evals`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from agentos.db.store import EntityStore
from agentos.domain.models import SkillDef
from agentos.evaluation.datasets import RegressionDataset
from agentos.skills.loader import load_skill_dir
from agentos.skills.search import search_skills


class SkillRegistry:
    def __init__(self, store: EntityStore, skills_root: Optional[Path] = None) -> None:
        self.store = store
        self.skills_root = skills_root or Path("skills")
        self._collection = "skills"

    async def load_from_disk(self) -> int:
        """Index SKILL.md files from the skills/ tree into the registry."""
        loaded = load_skill_dir(self.skills_root)
        for skill in loaded:
            await self.store.save(self._collection, skill)
        return len(loaded)

    async def list(self, enabled_only: bool = False, category: Optional[str] = None) -> list[SkillDef]:
        skills = await self.store.list(self._collection, SkillDef)
        skills.sort(key=lambda s: (s.category, s.id))
        if enabled_only:
            skills = [s for s in skills if s.enabled]
        if category:
            skills = [s for s in skills if s.category == category]
        return skills

    async def get(self, skill_id: str) -> Optional[SkillDef]:
        return await self.store.get(self._collection, skill_id, SkillDef)

    async def categories(self) -> list[str]:
        skills = await self.list()
        return sorted({s.category for s in skills})

    async def enable(self, skill_id: str, enabled: bool = True) -> SkillDef:
        skill = await self.get(skill_id)
        if not skill:
            raise KeyError(f"skill {skill_id} not found")
        skill.enabled = enabled
        await self.store.save(self._collection, skill)
        return skill

    async def register(self, skill: SkillDef) -> SkillDef:
        await self.store.save(self._collection, skill)
        return skill

    async def search(self, query: str, agent_id: Optional[str] = None, limit: int = 8) -> list[SkillDef]:
        """Progressive disclosure: return only the top-k relevant skills."""
        skills = await self.list(enabled_only=True)
        if agent_id:
            skills = [s for s in skills if not s.compatible_agents or agent_id in s.compatible_agents]
        ranked = search_skills(skills, query, limit=limit)
        return [s for s, _ in ranked]

    async def resolve_dependencies(self, skill_ids: list[str]) -> list[SkillDef]:
        """Expand a skill list including transitive dependencies."""
        out: dict[str, SkillDef] = {}
        queue = list(skill_ids)
        while queue:
            sid = queue.pop(0)
            if sid in out:
                continue
            skill = await self.get(sid)
            if not skill or not skill.enabled:
                continue
            out[sid] = skill
            queue.extend(skill.dependencies)
        return list(out.values())

    async def load_for_agent(self, agent_id: str, query: str, limit: int = 8) -> list[SkillDef]:
        """Return full skill bodies (progressive loading entry point)."""
        found = await self.search(query, agent_id=agent_id, limit=limit)
        return await self.resolve_dependencies([s.id for s in found])

    # ------------------------------------------------------------------
    # Progressive disclosure: references + evaluation cases
    # ------------------------------------------------------------------
    def _skill_dir(self, skill: SkillDef) -> Path:
        return Path(skill.source_path).parent

    async def list_references(self, skill_id: str) -> list[str]:
        """Names of deep reference files available for a skill (loaded on
        demand, never into the base context)."""
        skill = await self.get(skill_id)
        if not skill:
            return []
        return list(skill.references)

    async def load_reference(self, skill_id: str, name: str) -> Optional[str]:
        """Read one reference file for a skill. Returns None when the skill or
        the reference does not exist."""
        skill = await self.get(skill_id)
        if not skill or name not in skill.references:
            return None
        path = self._skill_dir(skill) / "references" / name
        if not path.exists():
            return None
        return path.read_text(errors="replace")

    async def load_evals(self, skill_id: str) -> Optional[RegressionDataset]:
        """Evaluation/regression cases for a skill from `evals/cases.yaml`.
        The returned dataset runs through the EXISTING benchmark runner — no
        second evaluation framework."""
        skill = await self.get(skill_id)
        if not skill:
            return None
        path = self._skill_dir(skill) / "evals" / "cases.yaml"
        if not path.exists():
            return None
        try:
            return RegressionDataset.load_yaml(path, fallback_name=f"skill:{skill_id}")
        except Exception:  # noqa: BLE001
            return None