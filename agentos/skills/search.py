"""Capability search — the progressive-disclosure front door.

Agents never load every skill into context. A task triggers a search; only the
top-k relevant skills are loaded into the agent's context.

Scoring is a lightweight lexical/coverage model (title, tags and description
matter most). It is deliberately simple, deterministic and testable; swapping
in an embedding-based retriever later must not change the registry contract.
"""

from __future__ import annotations

import re
from typing import Iterable

from agentos.domain.models import SkillDef

STOPWORDS = {"the", "a", "an", "and", "or", "for", "of", "to", "in", "on", "with",
             "is", "are", "how", "what", "build", "make", "do"}


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9][a-z0-9\-_+.]*", text.lower()) if t not in STOPWORDS]


def _score(skill: SkillDef, terms: set[str]) -> float:
    score = 0.0
    name_terms = set(tokenize(skill.name))
    id_terms = set(tokenize(skill.id.replace("_", "-")))
    tag_terms = set(tokenize(" ".join(skill.tags)))
    desc_terms = set(tokenize(skill.description))
    body_terms = set(tokenize(skill.body[:4000]))
    for term in terms:
        if term in id_terms:
            score += 5.0
        elif term in name_terms:
            score += 4.0
        elif term in tag_terms:
            score += 3.0
        elif term in desc_terms:
            score += 2.0
        elif term in body_terms:
            score += 1.0
    return score


def search_skills(skills: Iterable[SkillDef], query: str, limit: int = 8) -> list[tuple[SkillDef, float]]:
    terms = set(tokenize(query))
    if not terms:
        return [(s, 0.0) for s in list(skills)[:limit]]
    ranked = [(s, _score(s, terms)) for s in skills if s.enabled]
    ranked.sort(key=lambda pair: pair[1], reverse=True)
    return [(s, sc) for s, sc in ranked if sc > 0][:limit]