"""Memory System (layered, provenance-aware).

Five layers, all persisted: task (working), project, agent, org, user. One
store, one schema — the layered behavior comes from scope + owner_id, not
from five competing subsystems.

Design (Letta/Mem0/Graphiti-inspired, dependency-free):

* Semantic retrieval — TF-IDF cosine ranking over candidate entries, blended
  with importance and recency. Deterministic, offline, no vector DB needed;
  an embedding provider can be swapped in behind the same interface later.
* Provenance — every entry records source (agent/tool/human/evaluation) and
  a provenance chain ("agent:frontend-lead task:task_x").
* Versioned facts — saving a fact with the same (scope, owner, kind, topic)
  supersedes the previous one (old entry archived with `supersedes` link).
* Episodes — completed tasks become retrievable episodic memory.
* Consolidation — stale, low-access entries are archived; near-duplicate
  facts are merged. Forgetting archives, it never silently deletes.
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from agentos.db.store import EntityStore
from agentos.domain.models import MemoryEntry, MemoryLink, MemoryScope

_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    words = _WORD_RE.findall(text.lower())
    words = [w for w in words if len(w) > 2]
    bigrams = [f"{words[i]}_{words[i + 1]}" for i in range(len(words) - 1)]
    return words + bigrams


def _tfidf_rank(query: str, entries: list[MemoryEntry]) -> dict[str, float]:
    """Score entries by cosine similarity of TF-IDF vectors (query vs doc)."""
    q_terms = _tokenize(query)
    if not q_terms:
        return {}
    doc_terms = [_tokenize(f"{e.content} {' '.join(e.tags)} {e.kind}") for e in entries]
    n = max(len(entries), 1)
    df: dict[str, int] = {}
    for terms in doc_terms:
        for term in set(terms):
            df[term] = df.get(term, 0) + 1
    idf = {t: math.log((n + 1) / (df.get(t, 0) + 1)) + 1 for t in q_terms}
    q_vec = {t: q_terms.count(t) * idf[t] for t in q_terms}
    q_norm = math.sqrt(sum(v * v for v in q_vec.values())) or 1.0
    scores: dict[str, float] = {}
    for entry, terms in zip(entries, doc_terms):
        d_vec: dict[str, float] = {}
        for term in terms:
            if term in idf:
                d_vec[term] = d_vec.get(term, 0) + idf[term]
        dot = sum(q_vec.get(t, 0) * d_vec.get(t, 0) for t in q_vec)
        d_norm = math.sqrt(sum(v * v for v in d_vec.values())) or 1.0
        scores[entry.memory_id] = dot / (q_norm * d_norm)
    return scores


_CHANGE_WORDS = {"updated", "changed", "changing", "now", "new", "current",
                  "latest", "previous", "final", "revised", "was", "were",
                  "becomes", "becoming", "is", "are", "will", "the", "this",
                  "not", "longer", "no", "still"}

_NEG_MARKERS = (" not ", "never", "no longer", "isn't", "doesn't", "rejected",
                "abandoned", "blocked", "no ")
_CONTRAST_MARKERS = ("instead", "rather than", "changed to", "replaced",
                     "switched", "moved away", "no longer")


def _topic_key(kind: str, content: str) -> str:
    """Stable topic for fact versioning: kind + content words up to the first
    change/negation marker, so restating a changed fact ("deploy target is no
    longer staging") maps to the same topic as the original ("deploy target is
    staging") and supersedes it instead of creating a parallel fact."""
    words = _WORD_RE.findall(content.lower())
    words = [w for w in words if len(w) > 1]
    # skip leading change words ("the", "this", ...) before reading the subject
    idx = 0
    while idx < len(words) and words[idx] in _CHANGE_WORDS:
        idx += 1
    key_words: list[str] = []
    for w in words[idx:]:
        if w in _CHANGE_WORDS:
            break
        key_words.append(w)
    if not key_words:
        key_words = words[:4]
    return f"{kind}:{' '.join(key_words[:6])}"


def _contradicts(a: str, b: str) -> bool:
    """Conservative contradiction signal: the newer statement (b) explicitly
    negates or replaces the prior one (a). Plain evolution ('staging' →
    'production') is recorded as a supersede, not a contradiction — the old
    version is archived and linked either way, so history is never lost."""
    lb = b.lower()
    return (any(m in lb for m in _NEG_MARKERS)
            or any(m in lb for m in _CONTRAST_MARKERS))


class MemoryStore:
    def __init__(self, store: EntityStore, *, fact_ttl_days: int = 30) -> None:
        self.store = store
        self._collection = "memory"
        self.fact_ttl_days = fact_ttl_days

    # ------------------------------------------------------------------
    # Basic CRUD
    # ------------------------------------------------------------------
    async def save(self, scope: MemoryScope | str, owner_id: str, content: str,
                   *, kind: str = "fact", importance: int = 3,
                   tags: Optional[list[str]] = None,
                   source: str = "agent", provenance: str = "",
                   confidence: float = 0.8,
                   supersedes: Optional[str] = None,
                   valid_from: Optional[datetime] = None,
                   valid_to: Optional[datetime] = None) -> MemoryEntry:
        entry = MemoryEntry(
            scope=MemoryScope(scope), owner_id=owner_id, kind=kind,
            content=content, importance=max(1, min(5, importance)),
            tags=tags or [], source=source, provenance=provenance,
            confidence=max(0.0, min(1.0, confidence)), supersedes=supersedes,
            valid_from=valid_from, valid_to=valid_to,
        )
        await self.store.save(self._collection, entry)
        return entry

    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        return await self.store.get(self._collection, memory_id, MemoryEntry)

    async def delete(self, memory_id: str) -> None:
        await self.store.delete(self._collection, memory_id)

    async def all(self, limit: int = 500) -> list[MemoryEntry]:
        entries = await self.store.list(self._collection, MemoryEntry)
        entries.sort(key=lambda e: e.updated_at, reverse=True)
        return entries[:limit]

    async def by_owner(self, scope: MemoryScope | str, owner_id: str) -> list[MemoryEntry]:
        return await self.store.list(
            self._collection, MemoryEntry,
            predicate={"scope": MemoryScope(scope).value, "owner_id": owner_id},
        )

    # ------------------------------------------------------------------
    # Semantic recall
    # ------------------------------------------------------------------
    async def recall(self, scope: MemoryScope | str, owner_id: str,
                     query: Optional[str] = None, limit: int = 10,
                     kinds: Optional[list[str]] = None) -> list[MemoryEntry]:
        """Retrieve the most relevant entries for `query` under (scope, owner).

        Ranking = 0.6 * semantic similarity + 0.3 * importance/5 + 0.1 * recency,
        with a small boost for higher confidence. Archived entries never surface.
        """
        entries = await self.by_owner(scope, owner_id)
        entries = [e for e in entries if not e.archived]
        now = datetime.now(timezone.utc)
        # lazy temporal expiry: a fact whose validity window has passed is
        # archived (never silently deleted) and excluded from recall
        expired = [e for e in entries if not e.is_valid(now)]
        for e in expired:
            e.archived = True
            e.updated_at = now
            await self.store.save(self._collection, e)
        entries = [e for e in entries if not e.archived]
        if kinds:
            entries = [e for e in entries if e.kind in kinds]
        if not entries:
            return []
        if query:
            scores = _tfidf_rank(query, entries)
            by_id = {e.memory_id: e for e in entries}

            def rank(e: MemoryEntry) -> float:
                semantic = scores.get(e.memory_id, 0.0)
                recency = max(0.0, 1.0 - (now - e.updated_at).total_seconds() / (90 * 86400))
                return (0.6 * semantic + 0.3 * (e.importance / 5.0)
                        + 0.1 * recency + 0.05 * e.confidence)

            ranked = sorted(entries, key=rank, reverse=True)
        else:
            ranked = sorted(entries, key=lambda e: (e.importance, e.updated_at), reverse=True)
        for e in ranked[:limit]:
            e.access_count += 1
            e.updated_at = now
            await self.store.save(self._collection, e)
        return ranked[:limit]

    async def recall_for_task(self, task: Any, agent_id: str,
                              limit: int = 12) -> list[MemoryEntry]:
        """Automatic retrieval: the entries an agent needs to start a task.

        Pulls from project, agent and org layers (and task episodes), all
        ranked against the task text — context management without dumping
        every history into the prompt.
        """
        query = f"{task.title} {task.description}"
        scopes: list[tuple[MemoryScope, str]] = [
            (MemoryScope.TASK, task.task_id),
            (MemoryScope.PROJECT, task.project_id),
            (MemoryScope.AGENT, agent_id),
            (MemoryScope.ORG, "org"),
        ]
        seen: dict[str, MemoryEntry] = {}
        for scope, owner in scopes:
            for entry in await self.recall(scope, owner, query=query, limit=4):
                seen[entry.memory_id] = entry
        merged = list(seen.values())
        merged.sort(key=lambda e: (e.importance, e.updated_at), reverse=True)
        return merged[:limit]

    # ------------------------------------------------------------------
    # Fact extraction & versioned facts
    # ------------------------------------------------------------------
    _FACT_MARKERS = {
        "decision": ("Decision:", "DECISION", "decided to", "we decided"),
        "lesson": ("Lesson:", "LESSON", "learned that", "lesson learned"),
        "preference": ("Preference:", "PREFERENCE", "prefers", "preference"),
        "fact": ("Fact:", "FACT:", "important fact", "key finding"),
        "instruction": ("Instruction:", "INSTRUCTION", "must always", "never "),
    }

    async def extract_facts(self, task: Any, outcome: Any,
                            agent_id: str) -> list[MemoryEntry]:
        """Extract durable facts from a run's text (deterministic markers).

        Only explicit, marked statements become memory — conversation noise
        does not. Returns the saved entries.
        """
        text = f"{outcome.content or ''}\n{outcome.reflection or ''}"
        saved: list[MemoryEntry] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            for kind, markers in self._FACT_MARKERS.items():
                if any(line.startswith(m) or m in line[:60] for m in markers):
                    content = line.split(":", 1)[-1].strip() if ":" in line else line
                    if len(content) < 12:
                        continue
                    entry = await self.save_fact(
                        MemoryScope.PROJECT, task.project_id, content,
                        kind=kind, source="agent",
                        provenance=f"agent:{agent_id} task:{task.task_id}",
                    )
                    saved.append(entry)
                    break
        return saved

    async def save_fact(self, scope: MemoryScope | str, owner_id: str, content: str,
                        *, kind: str = "fact", importance: int = 3,
                        tags: Optional[list[str]] = None,
                        source: str = "agent", provenance: str = "",
                        confidence: float = 0.8,
                        valid_from: Optional[datetime] = None,
                        valid_to: Optional[datetime] = None) -> MemoryEntry:
        """Save a fact with contradiction resolution and versioning:
        * same topic + same content → refresh importance (no-op-ish),
        * same topic + contradicting content → archive old, link `contradicts`,
        * same topic + evolution → archive old, link `supersedes`.
        History is never silently overwritten (Graphiti-style)."""
        topic = _topic_key(kind, content)
        existing = await self.by_owner(scope, owner_id)
        prior = None
        for e in existing:
            if e.kind == kind and not e.archived and _topic_key(kind, e.content) == topic:
                prior = e
                break
        if prior is not None and prior.content == content:
            prior.importance = max(prior.importance, importance)
            prior.updated_at = datetime.now(timezone.utc)
            await self.store.save(self._collection, prior)
            return prior
        relation = "supersedes"
        if prior is not None and _contradicts(prior.content, content):
            relation = "contradicts"
        supersedes = prior.memory_id if prior else None
        if prior is not None:
            prior.archived = True
            prior.updated_at = datetime.now(timezone.utc)
            await self.store.save(self._collection, prior)
        entry = await self.save(scope, owner_id, content, kind=kind,
                                importance=importance, tags=tags,
                                source=source, provenance=provenance,
                                confidence=confidence, supersedes=supersedes,
                                valid_from=valid_from, valid_to=valid_to)
        if prior is not None:
            await self.link(entry.memory_id, prior.memory_id, relation,
                            payload={"topic": topic})
        return entry

    # ------------------------------------------------------------------
    # Knowledge-graph links (relationships between memory entries)
    # ------------------------------------------------------------------
    async def link(self, source_id: str, target_id: str, relation: str = "related",
                   payload: Optional[dict] = None) -> MemoryLink:
        link = MemoryLink(source_id=source_id, target_id=target_id,
                          relation=relation, payload=payload or {})
        await self.store.save("memory_links", link)
        return link

    async def unlink(self, link_id: str) -> None:
        await self.store.delete("memory_links", link_id)

    async def related(self, memory_id: str, relation: Optional[str] = None,
                      limit: int = 30) -> list[MemoryLink]:
        links = await self.store.list("memory_links", MemoryLink)
        out = [l for l in links if l.source_id == memory_id or l.target_id == memory_id]
        if relation:
            out = [l for l in out if l.relation == relation]
        out.sort(key=lambda l: l.created_at, reverse=True)
        return out[:limit]

    async def neighbors(self, memory_id: str, relation: Optional[str] = None,
                        limit: int = 20) -> list[tuple[str, MemoryEntry]]:
        """Entries connected to `memory_id` via any (or a specific) relation."""
        links = await self.related(memory_id, relation=relation)
        ids = {l.target_id if l.source_id == memory_id else l.source_id
               for l in links}
        entries = []
        for mem_id in ids:
            entry = await self.get(mem_id)
            if entry and not entry.archived:
                entries.append((mem_id, entry))
        return entries[:limit]

    async def graph(self, scope: MemoryScope | str, owner_id: str,
                    limit: int = 80) -> dict:
        """Knowledge-graph view of an owner's active memory:
        {"nodes": [...], "edges": [...]} for visualization/analysis."""
        entries = await self.by_owner(scope, owner_id)
        active = [e for e in entries if not e.archived]
        ids = {e.memory_id for e in active}
        links = [l for l in await self.store.list("memory_links", MemoryLink)
                 if l.source_id in ids and l.target_id in ids]
        return {
            "nodes": [{"id": e.memory_id, "kind": e.kind,
                       "content": e.content[:120], "importance": e.importance,
                       "scope": e.scope.value} for e in active[:limit]],
            "edges": [{"source": l.source_id, "target": l.target_id,
                       "relation": l.relation} for l in links],
        }

    async def timeline(self, scope: MemoryScope | str, owner_id: str,
                       limit: int = 100) -> list[MemoryEntry]:
        """Temporal view: entries ordered by when they became valid."""
        entries = await self.by_owner(scope, owner_id)
        entries.sort(key=lambda e: (e.valid_from or e.created_at))
        return entries[-limit:]

    # ------------------------------------------------------------------
    # Episodes (task history as retrievable memory)
    # ------------------------------------------------------------------
    async def record_episode(self, task: Any, outcome: Any,
                             agent_id: str) -> MemoryEntry:
        summary = (
            f"[episode] {task.title}: {'completed' if not outcome.error else 'failed'} "
            f"via {outcome.model or 'no model'}; artifacts: {', '.join(outcome.artifacts or []) or 'none'}; "
            f"{'error: ' + str(outcome.error) if outcome.error else 'no error'}"
        )
        return await self.save(
            MemoryScope.TASK, task.task_id, summary,
            kind="episode", importance=2, source="system",
            provenance=f"agent:{agent_id} task:{task.task_id}",
        )

    # ------------------------------------------------------------------
    # Consolidation / forgetting
    # ------------------------------------------------------------------
    async def consolidate(self, scope: MemoryScope | str, owner_id: str,
                          *, max_age_days: Optional[int] = None,
                          min_access: int = 2) -> dict[str, int]:
        """Archive stale low-access entries and merge near-duplicate facts.

        Returns counts: {"archived": n, "merged": n}. Archiving is reversible
        (entries are flagged, not deleted); nothing here runs automatically —
        the orchestrator calls it periodically.
        """
        ttl = max_age_days or self.fact_ttl_days
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=ttl)
        entries = await self.by_owner(scope, owner_id)
        archived = 0
        for e in entries:
            if e.archived:
                continue
            expired = e.expires_at is not None and e.expires_at < now
            stale = e.updated_at < cutoff and e.access_count < min_access and e.importance < 4
            if expired or stale:
                e.archived = True
                e.updated_at = now
                await self.store.save(self._collection, e)
                archived += 1
        # merge exact-duplicate content within the same owner
        merged = 0
        for e in entries:
            if e.archived:
                continue
            for other in entries:
                if other.memory_id == e.memory_id or other.archived:
                    continue
                if (other.owner_id == e.owner_id and other.kind == e.kind
                        and other.content.strip().lower() == e.content.strip().lower()):
                    if other.importance >= e.importance:
                        continue
                    other.importance = e.importance
                    other.tags = sorted(set(other.tags + e.tags))
                    other.updated_at = now
                    e.archived = True
                    e.updated_at = now
                    await self.store.save(self._collection, e)
                    await self.store.save(self._collection, other)
                    merged += 1
                    break
        return {"archived": archived, "merged": merged}

    async def archive(self, memory_id: str) -> MemoryEntry:
        entry = await self.get(memory_id)
        if entry:
            entry.archived = True
            entry.updated_at = datetime.now(timezone.utc)
            await self.store.save(self._collection, entry)
        return entry  # type: ignore[return-value]

    async def stats(self, scope: MemoryScope | str, owner_id: str) -> dict[str, int]:
        entries = await self.by_owner(scope, owner_id)
        return {
            "total": len(entries),
            "archived": sum(1 for e in entries if e.archived),
            "by_kind": {k: sum(1 for e in entries if e.kind == k) for k in
                        sorted({e.kind for e in entries})},
        }

    async def remember_if_important(self, scope: MemoryScope | str, owner_id: str,
                                    content: str, importance: int) -> MemoryEntry | None:
        """Save only when importance warrants it (memory hygiene rule)."""
        if importance < 2:
            return None
        return await self.save(scope, owner_id, content, importance=importance)