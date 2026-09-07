---
id: prioritization
name: Prioritization
description: "General prioritization framework — criteria, weights, scoring, dependency handling — for any backlog."
category: 03-product
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
dependencies: []
compatible_agents: [product-manager, project-manager]
tags: [prioritization, backlog, decisions]
contract:
  prerequisites:
    - "a set of items to order and the decision the order serves"
  preferred_agents: [product-manager, project-manager]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "scores backed by stated reasons; estimates labeled"
  artifact_contract:
    - "prioritized list with criteria, scores, rationale"
  quality_gates:
    - "criteria stated before scoring"
    - "every item has a rationale"
  verification:
    - "recompute totals; order matches scores"
  failure_modes:
    hidden_criteria: "surface the real criterion (e.g. politics) and record it"
    analysis_paralysis: "cap scoring depth; ship a defensible order"
  escalation:
    - "orderings that would block a committed date without a conscious trade"
  handoff_in:
    - "items to order"
    - "decision context"
  handoff_out:
    - "ordered list with rationale"
  evaluation:
    - "reproducibility and explicitness of criteria"
  observability:
    - "record the criteria and final order"
  related_skills: [feature-prioritization, opportunity-scoring, roadmap-planning]
---

# Prioritization

## Purpose
Order any set of items (features, tasks, risks, ideas) using explicit
criteria and weights — so the order is explainable and reproducible.

## When to use / When NOT to use
- use: when capacity < demand and an order is needed
- avoid: when the set is tiny and the order is obvious (still record the
  reason); avoid letting prioritization substitute for strategy

## Inputs & assumptions
- inputs: items, decision context
- assumptions: weights encode policy — state whose policy and label assumed

## Workflow
1. State criteria and weights before looking at the items.
2. Score each item per criterion with a one-line reason.
3. Compute totals, sort, resolve dependencies.
4. Review the top for hidden criteria (the item that "should" win but
   doesn't — surface why).
5. Produce the ordered list with rationale.

## Evidence requirements
- Every score has a reason; estimates are labeled estimated.

## Artifact contract
- `prioritized-list`: item, per-criterion scores, weights, total, rationale,
  final order.

## Quality gates (definition of done)
- [ ] Criteria stated before scoring
- [ ] Every item scored with a rationale
- [ ] Order reproducible from the table

## Verification
- Recompute totals; confirm the order follows the scores.

## Failure & recovery
| failure | recovery |
|---|---|
| hidden criteria | surface and record the real criterion |
| analysis paralysis | cap depth, ship the defensible order, note sensitivity |
| ties | tie-break by evidence and note it |

## Escalation
- An order that blocks a committed date — escalate the trade consciously.

## Handoff
- receives: items, decision context
- passes: ordered list with rationale

## Evaluation
The org evaluates this skill by reproducibility and explicitness of the
criteria — not by whether the "obvious" item won.

## Observability
- Record criteria, weights, and final order in the project decision log.

## References
- references/methodology.md — scoring calibration and common biases