---
id: rag-patterns
name: RAG Patterns
description: When and how to use retrieval — chunking, indexing, grounding, citations.
category: 15-ai
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [rag, retrieval, memory]
compatible_agents: [ai-engineer]
---

# RAG Patterns

## Purpose
Ground model outputs in retrieved evidence — and know when retrieval is the
wrong tool.

## When RAG helps
- Answers depend on a corpus that changes (docs, code, tickets, policies).
- Factual accuracy matters and the model can cite sources.
- The corpus is too large for context.

## When it doesn't
- The knowledge fits context and is stable — just include it.
- The question needs reasoning over data (compute, don't retrieve).
- The corpus is tiny — retrieval overhead isn't justified.
- You need determinism — retrieval adds variance; code/DB queries are exact.

## Design
1. **Chunking** — by semantic unit (section, function, ticket), not fixed
   byte counts; keep context/answer together.
2. **Metadata** — source, date, version, permissions; filter before ranking.
3. **Indexing** — keyword + embeddings where needed; hybrid ranking; rerank
   top-k when quality demands.
4. **Grounding** — the model must answer only from retrieved chunks and cite
   them; hold-out evals for hallucination.
5. **Freshness** — index invalidation/refresh policy; stale retrievals mislead.

## Rules
- Evaluate retrieval quality (recall@k, answer accuracy) before scaling.
- Never retrieve more than context needs: top-k is a cost and a noise budget.