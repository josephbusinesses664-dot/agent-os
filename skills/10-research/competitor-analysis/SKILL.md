---
id: competitor-analysis
name: Competitor Analysis
description: "Evidence-based competitor analysis — positioning, gaps, weaknesses — with sources and dates."
category: 10-research
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [research-planning, evidence-synthesis]
compatible_agents: [competitor-analyst, market-researcher]
tags: [competitors, analysis, intelligence]
contract:
  prerequisites:
    - "the market and the decision the analysis informs"
  preferred_agents: [competitor-analyst, market-researcher]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "claims about competitors sourced with retrieval dates"
    - "pricing/product claims verified against current pages"
  artifact_contract:
    - "competitor analysis (positioning, strengths, weaknesses, gaps)"
  quality_gates:
    - "every claim cited"
    - "gaps derived from evidence, not wishes"
    - "stale claims labeled with vintage"
  verification:
    - "re-verify load-bearing claims against competitor pages"
  failure_modes:
    stale_intel: "label vintage; re-check pricing/features"
    gossip: "distinguish observed from inferred competitor behavior"
  escalation:
    - "competitor moves that change the market"
  handoff_in:
    - "market"
    - "decision"
  handoff_out:
    - "competitor analysis with gaps for strategy"
  evaluation:
    - "claim sourcing"
    - "gap quality"
  observability:
    - "record sources and dates per claim"
  related_skills: [evidence-synthesis, market-research, positioning]
---

# Competitor Analysis

## Purpose
Produce evidence-based competitive intelligence: what competitors actually
do, their strengths and weaknesses, and the gaps — with sources and dates,
never gossip.

## When to use / When NOT to use
- use: positioning, strategy, feature decisions
- avoid: unsourced claims about competitors; avoid assuming a competitor's
  behavior from one signal

## Inputs & assumptions
- inputs: market, decision
- assumptions: competitor strategy inferred from observed behavior —
  labeled inferred, not observed

## Workflow
1. List the competitors the decision cares about.
2. Gather evidence per competitor: product, pricing, positioning,
   reviews, community sentiment, hiring/funding signals.
3. Verify pricing/product claims against current pages.
4. Distill strengths and weaknesses from evidence.
5. Identify gaps: needs unmet by the set (evidence-backed).
6. Produce the analysis with sources and dates.

## Evidence requirements
- Every claim carries source + retrieval date.
- Load-bearing claims verified against current pages.

## Artifact contract
- `competitor-analysis`: per-competitor profile (evidence), strengths/
  weaknesses, gaps, sources.

## Quality gates (definition of done)
- [ ] Every claim cited
- [ ] Gaps evidence-derived
- [ ] Stale claims labeled
- [ ] Observed vs inferred distinguished

## Verification
- Re-verify load-bearing claims against competitor pages.

## Failure & recovery
| failure | recovery |
|---|---|
| stale intel | label vintage; re-fetch |
| gossip | distinguish observed vs inferred |
| weak gap evidence | mark the gap low-confidence |

## Escalation
- Competitor moves that change the market — escalate with evidence.

## Handoff
- receives: market, decision
- passes: competitor analysis with gaps to strategy/positioning

## Evaluation
The org evaluates this skill by claim sourcing and gap quality.

## Observability
- Record sources and dates per claim in the audit trail.

## References
- references/patterns.md — evidence collection per competitor type