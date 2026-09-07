---
id: opportunity-scoring
name: Opportunity Scoring
description: "Score opportunities on a transparent multi-factor model — evidence, pain, breadth, economics, competition."
category: 01-discovery
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search]
risk_level: low
cost_level: low
dependencies: [opportunity-discovery]
compatible_agents: [product-researcher, market-researcher, product-manager]
tags: [opportunity, scoring, prioritization]
contract:
  prerequisites:
    - "a candidate opportunity list (from opportunity-discovery or equivalent)"
    - "agreed scoring factors and weights for this decision"
  preferred_agents: [product-researcher, product-manager]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "each factor score justified by evidence, not vibes"
    - "unknown factors scored as unknown, not neutral"
  artifact_contract:
    - "scored opportunity table (factor scores, weights, total, rationale)"
  quality_gates:
    - "weights and scores visible and reproducible"
    - "no factor silently skipped"
    - "the scoring model itself stated before scores are assigned"
  verification:
    - "recompute totals from factor scores"
    - "check that the top-ranked opportunity has the strongest evidence"
  failure_modes:
    missing_factor: "score it unknown and flag it — never drop it"
    weight_disagreement: "surface the disagreement; default to the agreed weights"
  escalation:
    - "two opportunities within noise of each other at the top (tie-break by evidence quality)"
  handoff_in:
    - "candidate opportunities with signals and sources"
  handoff_out:
    - "ranked opportunities with factor scores and rationale"
    - "recommended next validation"
  evaluation:
    - "reproducibility of scores from evidence"
    - "correct treatment of unknown factors"
  observability:
    - "record the scoring model and per-factor evidence"
  related_skills: [opportunity-discovery, demand-validation, feature-prioritization]
---

# Opportunity Scoring

## Purpose
Turn a candidate list into a defensible ranking using a transparent
multi-factor model — so "why this one?" has an answer anyone can check.

## When to use / When NOT to use
- use: choosing between validated/discovered opportunities, portfolio
  decisions
- avoid: before discovery (nothing to score); avoid when a single candidate
  needs deep validation instead

## Inputs & assumptions
- inputs: candidate opportunities with signals, agreed factors and weights
- assumptions: weights encode strategy — record whose strategy they encode
  and note they are assumed, not derived

## Scoring model (default factors)
1. **Pain severity** — how disruptive is the problem (evidence-backed).
2. **Frequency/urgency** — how often and how urgently it recurs.
3. **Market breadth** — population affected (loud minority ≠ market).
4. **Willingness to pay** — strongest available evidence; unknown is scored
   unknown.
5. **Competitive weakness** — how poorly current alternatives solve it.
6. **Execution fit** — team capability and cost to serve.
7. **Evidence confidence** — quality of the underlying signals.

Score each 1-5 with a one-line justification from evidence. Compute a
weighted total. Never let a missing factor vanish — score it unknown and flag
it.

## Workflow
1. State the scoring model (factors + weights) before scoring.
2. Score each candidate factor-by-factor, citing evidence per score.
3. Compute totals; sort.
4. Ties or near-ties: break by evidence confidence, and say so.
5. Produce the table with rationale and the recommended validation order.

## Evidence requirements
- Every factor score has an evidence justification; unknowns are explicit.
- If a candidate's evidence is thin, its evidence-confidence factor must be
  low — the score must reflect the evidence, not enthusiasm.

## Artifact contract
- `opportunity-ranking`: candidate, per-factor scores, weights, total,
  rationale, recommended next validation.

## Quality gates (definition of done)
- [ ] Weights and scores visible and reproducible
- [ ] No factor silently skipped
- [ ] Top candidate's ranking justified by evidence
- [ ] Totals recomputed and correct

## Verification
- Recompute totals from the factor table.
- Confirm the ranking did not invert the evidence-confidence order.

## Failure & recovery
| failure | recovery |
|---|---|
| missing factor data | score unknown, flag it, adjust confidence |
| near-tie at top | tie-break by evidence confidence and note it |
| weight disagreement | surface both weight sets, use agreed weights, flag sensitivity |

## Escalation
- Near-ties at the top of a portfolio decision where budget commits follow.

## Handoff
- receives: candidates with signals and sources
- passes: ranked opportunities with factor scores and rationale,
  recommended validation order

## Evaluation
The org evaluates this skill by reproducibility (can a reviewer recompute
scores from the evidence?) and honest treatment of unknowns.

## Observability
- Record the scoring model and per-factor evidence in the trace so the
  ranking is auditable.

## References
- references/methodology.md — calibration rules and common scoring errors