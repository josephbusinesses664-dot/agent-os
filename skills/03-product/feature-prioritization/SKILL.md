---
id: feature-prioritization
name: Feature Prioritization
description: "Prioritize features on explicit weighted criteria — value, cost, risk, dependencies — with evidence per score."
category: 03-product
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
dependencies: [prioritization, roadmap-planning]
compatible_agents: [product-manager, product-director]
tags: [prioritization, features, roadmap]
contract:
  prerequisites:
    - "candidate features with descriptions and rough size"
    - "agreed prioritization criteria for this decision"
  preferred_agents: [product-manager, product-director]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "each score justified by evidence (demand, cost inputs) or labeled estimate"
  artifact_contract:
    - "prioritized feature list (criteria, scores, rationale, ordering)"
  quality_gates:
    - "criteria and weights stated before scoring"
    - "no feature scored without a rationale"
    - "dependency ordering respected"
  verification:
    - "recompute totals; check ordering follows scores"
  failure_modes:
    scoring_bias: "re-read scores against evidence — check the pet feature did not win on vibes"
    missing_dependency: "check every feature's dependencies are ordered earlier"
  escalation:
    - "features with strong scores but cross-cutting architectural impact"
  handoff_in:
    - "candidate features"
    - "criteria and weights"
  handoff_out:
    - "prioritized features with rationale for roadmap planning"
  evaluation:
    - "reproducible ordering from stated criteria"
    - "dependency correctness"
  observability:
    - "record criteria, scores, and ordering in the project"
  related_skills: [prioritization, roadmap-planning, opportunity-scoring]
---

# Feature Prioritization

## Purpose
Produce a defensible feature ordering from explicit weighted criteria —
value, cost, risk, dependencies — with a rationale per score.

## When to use / When NOT to use
- use: roadmap slicing, release scoping, when capacity < demand
- avoid: before candidates exist; avoid prioritizing by gut feeling alone
  without recording criteria

## Inputs & assumptions
- inputs: candidate features (description + rough size), agreed criteria
- assumptions: weights are a policy choice — record them and who set them

## Criteria (default)
1. **Value** — evidence of demand/pain addressed.
2. **Cost** — rough build size (labeled estimate).
3. **Risk** — technical and market risk.
4. **Dependencies** — what it unblocks or waits on.
5. **Strategic fit** — alignment with the current strategy.

## Workflow
1. State criteria and weights before scoring.
2. Score each feature 1-5 per criterion with a one-line justification.
3. Compute weighted totals and sort.
4. Reorder to respect dependencies (a feature cannot ship before its
   dependencies).
5. Review the top of the list against evidence — check for bias toward the
   exciting but unproven.

## Evidence requirements
- Every score has a rationale; demand scores cite evidence where it exists
  and say "estimate" otherwise.

## Artifact contract
- `prioritized-features`: feature, per-criterion scores, weights, total,
  rationale, final order.

## Quality gates (definition of done)
- [ ] Criteria and weights stated before scoring
- [ ] No feature scored without a rationale
- [ ] Dependency ordering respected
- [ ] Totals recomputed and consistent with the order

## Verification
- Recompute totals from the table.
- Check each feature's dependencies appear earlier in the order.

## Failure & recovery
| failure | recovery |
|---|---|
| scoring bias | re-read scores against evidence; adjust with justification |
| missing dependency | add it and re-order |
| ties | tie-break by value evidence and note it |

## Escalation
- High-scoring features with cross-cutting architectural impact — escalate
  for an explicit architecture review before committing.

## Handoff
- receives: candidate features, criteria and weights
- passes: prioritized features with rationale to roadmap planning

## Evaluation
The org evaluates this skill by reproducibility (ordering derivable from the
stated criteria) and dependency correctness.

## Observability
- Record criteria, scores, and final order in the project decision log.

## References
- references/methodology.md — scoring calibration and bias checks