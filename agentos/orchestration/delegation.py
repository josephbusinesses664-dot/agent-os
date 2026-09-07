"""Delegation engine — purposeful, explainable, hierarchy-safe agent selection.

Answers: "Who is actually best suited AND authorized to perform this?" —
not merely "who is next in the chart".

Selection is transparent: every candidate gets an explainable score with
per-factor reasons, and the result records why X was chosen over Y.

Hard safety properties (enforced, not advisory):
- HIERARCHY: only the agent's allowed children (or explicit
  `agent.delegate` permission holders) are candidates.
- PERMISSION CONTAINMENT: a parent cannot delegate an action requiring a
  permission it does not itself hold (no capability laundering).
- SECURITY ABOVE AUTHORITY: candidates are filtered through the same
  permission map used at execution; delegation never grants anything.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional

# role keywords per archetype — matches task vocabulary to agent cognition
ARCHETYPE_TASK_AFFINITY: dict[str, list[str]] = {
    "executive": ["strategy", "prioritize", "portfolio", "resource", "budget decision", "goal", "worth", "decide"],
    "architect": ["architecture", "design system", "boundary", "schema", "data model", "integration", "tradeoff", "scalability"],
    "researcher": ["research", "evidence", "market", "competitor", "community", "reddit", "sentiment", "validate", "sizing"],
    "product": ["requirement", "prd", "user story", "acceptance", "roadmap", "prioritization", "feature", "scope"],
    "designer": ["ux", "ui", "design", "accessibility", "animation", "motion", "visual", "wireframe", "layout"],
    "engineer": ["implement", "build", "code", "api", "frontend", "backend", "database", "bug", "refactor", "test", "deploy", "migration"],
    "qa": ["test", "verify", "review", "quality", "regression", "edge case", "coverage", "vulnerability scan", "performance review"],
    "security": ["security", "threat", "vulnerability", "abuse", "privilege", "secret", "injection", "attack surface", "audit"],
    "operations": ["monitor", "deploy", "incident", "reliability", "runbook", "backup", "infrastructure", "documentation", "schedule"],
    "sales": ["prospect", "lead", "icp", "outreach", "pipeline", "deal", "qualification"],
    "marketing": ["seo", "content", "campaign", "audience", "social", "growth", "keyword", "copywriting", "landing"],
}


@dataclass
class DelegationCandidate:
    """One candidate agent with its explainable scorecard."""

    agent_id: str
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)
    disqualifications: list[str] = field(default_factory=list)

    @property
    def eligible(self) -> bool:
        return not self.disqualifications


@dataclass
class DelegationDecision:
    """The outcome of purposeful selection — explainable."""

    task_description: str
    requester: str
    selected: Optional[str] = None
    reason: str = ""
    candidates: list[DelegationCandidate] = field(default_factory=list)

    def explanation(self) -> str:
        lines = [f"delegation for '{self.task_description[:80]}' by {self.requester}"]
        for c in self.candidates:
            status = "selected" if c.agent_id == self.selected else (
                "eligible" if c.eligible else "disqualified: " + "; ".join(c.disqualifications))
            lines.append(f"  {c.agent_id}: {c.score:.1f} [{status}] {'; '.join(c.reasons[:3])}")
        return "\n".join(lines)


class DelegationEngine:
    """Purposeful delegation: expertise + performance + workload + authority.

    Works over the existing AgentRegistry (hierarchy + permissions),
    PerformanceTracker (history) and AgentInstance (workload). Selection
    widens nothing: the candidate pool is bounded by hierarchy and every
    factor is filtered by the same permissions the executor enforces.
    """

    def __init__(self, agent_registry: Any, performance: Any = None,
                 instances: Any = None) -> None:
        self.agents = agent_registry
        self.performance = performance
        self.instances = instances

    # -- candidate pool ------------------------------------------------------
    async def _candidates(self, requester: str) -> list[Any]:
        """Hierarchy-safe pool: the requester's allowed children, plus — only
        when the requester explicitly holds `agent.delegate` — cross-tree
        specialists. Never the whole org."""
        requester_def = await self.agents.get(requester)
        if requester_def is None:
            return []
        pool: list[Any] = []
        seen: set[str] = set()
        for child_id in requester_def.allowed_children:
            child = await self.agents.get(child_id)
            if child and child.enabled and child_id not in seen:
                pool.append(child)
                seen.add(child_id)
        if requester_def.permissions.get("agent.delegate", "deny") == "allow":
            for agent in await self.agents.list(enabled_only=True):
                if agent.id not in seen and agent.id != requester:
                    pool.append(agent)
                    seen.add(agent.id)
        return pool

    # -- factors -------------------------------------------------------------
    async def _expertise(self, agent: Any, description: str) -> tuple[float, list[str]]:
        """Task↔agent fit: declared skills (registry-backed) + archetype
        affinity with the task vocabulary."""
        reasons: list[str] = []
        score = 0.0
        terms = set(re.findall(r"[a-z0-9]+", description.lower()))
        skill_hits = [s for s in agent.skills
                      if any(t in s.replace("-", " ") for t in terms if len(t) > 3)]
        if skill_hits:
            score += 3.0
            reasons.append(f"declared skills match: {', '.join(skill_hits[:3])}")
        archetype = agent.identity.archetype if agent.identity else "engineer"
        affinity_words = ARCHETYPE_TASK_AFFINITY.get(archetype, [])
        affinity = sum(1 for w in affinity_words if w in description.lower())
        if affinity:
            score += min(affinity * 1.5, 4.5)
            reasons.append(f"{archetype} affinity ({affinity} signals)")
        return score, reasons

    async def _performance(self, agent_id: str) -> tuple[float, list[str]]:
        if self.performance is None:
            return 0.0, []
        try:
            stats = await self.performance.stats(agent_id)
        except Exception:  # noqa: BLE001
            return 0.0, []
        if stats.runs < 3:
            return 0.0, []  # no evidence either way
        reasons: list[str] = []
        score = 0.0
        if stats.success_rate >= 0.9:
            score += 2.0
            reasons.append(f"track record {stats.success_rate:.0%} over {stats.runs} runs")
        elif stats.success_rate < 0.6:
            score -= 2.0
            reasons.append(f"weak track record {stats.success_rate:.0%}")
        if stats.avg_review_score >= 0.8 and stats.review_count >= 2:
            score += 1.0
            reasons.append(f"review quality {stats.avg_review_score:.2f}")
        return score, reasons

    async def _workload(self, agent_id: str) -> tuple[float, list[str]]:
        if self.instances is None:
            return 0.0, []
        try:
            inst = await self.instances.instance(agent_id)
        except Exception:  # noqa: BLE001
            return 0.0, []
        from agentos.domain.models import AgentStatus
        if inst.status in (AgentStatus.OFFLINE, AgentStatus.FAILED):
            return -100.0, ["agent offline/failed"]
        if inst.status in (AgentStatus.WORKING, AgentStatus.AWAITING_APPROVAL,
                           AgentStatus.AWAITING_REVIEW):
            return -1.5, ["currently busy"]
        return 0.0, []

    def _permission_containment(self, requester: Any, candidate: Any,
                                description: str) -> list[str]:
        """A parent cannot launder capabilities it lacks: if the task text
        explicitly names a protected action, the requester must hold that
        permission too. Security policy always outranks org authority."""
        protected = {
            "deploy": "deploy", "shell": "shell", "database query": "postgres.query",
            "github": "github", "docker": "docker", "payment": "api.call",
        }
        problems: list[str] = []
        low = description.lower()
        for phrase, perm in protected.items():
            if phrase in low:
                if requester.permissions.get(perm, "deny") != "allow":
                    problems.append(f"requester lacks '{perm}' — cannot delegate it")
                elif candidate.permissions.get(perm, "deny") != "allow":
                    problems.append(f"candidate lacks required '{perm}' permission")
        return problems

    # -- selection -------------------------------------------------------------
    async def select(self, requester: str, task_description: str, *,
                     task_type: str = "") -> DelegationDecision:
        """Pick the best eligible candidate with an explainable decision."""
        decision = DelegationDecision(task_description=task_description,
                                      requester=requester)
        requester_def = await self.agents.get(requester)
        if requester_def is None:
            decision.reason = f"unknown requester {requester}"
            return decision
        for agent in await self._candidates(requester):
            cand = DelegationCandidate(agent_id=agent.id)
            # authority containment (hard disqualifier)
            for problem in self._permission_containment(requester_def, agent,
                                                        task_description):
                cand.disqualifications.append(problem)
            # expertise
            s, r = await self._expertise(agent, task_description)
            cand.score += s
            cand.reasons += r
            # historical performance
            s, r = await self._performance(agent.id)
            cand.score += s
            cand.reasons += r
            # workload / availability
            s, r = await self._workload(agent.id)
            cand.score += s
            cand.reasons += r
            # risk alignment: minimal-risk agents favored for high-risk tasks
            if any(w in task_description.lower() for w in
                   ("production", "deploy", "security", "irreversible", "migration")):
                tolerance = agent.identity.risk_tolerance if agent.identity else "moderate"
                if tolerance == "minimal":
                    cand.score += 1.5
                    cand.reasons.append("minimal risk tolerance suits high-risk work")
                elif tolerance == "high":
                    cand.score -= 1.0
                    cand.reasons.append("high risk tolerance mismatched for risky task")
            decision.candidates.append(cand)
        eligible = [c for c in decision.candidates if c.eligible]
        if not eligible:
            decision.reason = "no eligible candidate (hierarchy + permission bounds)"
            return decision
        eligible.sort(key=lambda c: c.score, reverse=True)
        best = eligible[0]
        decision.selected = best.agent_id
        decision.reason = "; ".join(best.reasons) if best.reasons else "best available in hierarchy"
        return decision
