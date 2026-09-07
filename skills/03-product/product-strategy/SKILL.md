---
id: product-strategy
name: Product Strategy
description: "Product-level strategy — vision, outcomes, scope discipline, sequencing — with explicit assumptions."
category: 03-product
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
dependencies: [strategy, product-strategy]
compatible_agents: [product-director, product-manager]
tags: [product, strategy, vision, scope]
contract:
  prerequisites:
    - "business strategy context (where-to-play, how-to-win)"
    - "research/opportunity evidence for the product direction"
  preferred_agents: [product-director, product-manager]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "outcomes chosen from evidence, not features"
    - "scope trade-offs explicit"
  artifact_contract:
    - "product strategy (vision, outcomes, scope, sequencing, metrics)"
  quality_gates:
    - "outcomes are measurable"
    - "scope discipline explicit (what is excluded)"
    - "sequencing justified by dependencies and risk"
  verification:
    - "re-read: could a PM execute this without asking what to do next?"
  failure_modes:
    feature_vision: "re-anchor on outcomes and the job to be done"
    scope_creep: "cut to the committed outcomes; move the rest to backlog"
  escalation:
    - "strategy requiring capabilities the org does not have"
  handoff_in:
    - "business strategy"
    - "research evidence"
  handoff_out:
    - "product strategy with outcomes, scope, sequencing"
  evaluation:
    - "outcome measurability"
    - "scope discipline"
  observability:
    - "record vision, outcomes, and scope as project decisions"
  related_skills: [strategy, roadmap-planning, prd-writing, product-strategy]
---

# Product Strategy

## Purpose
Define what the product is for, who it serves, and what it deliberately
excludes — as measurable outcomes and sequenced scope, not feature wishes.

## When to use / When NOT to use
- use: at product inception and major pivots; before roadmap commitment
- avoid: for single-feature scoping (use feature-prioritization); avoid a
  "product strategy" that is only a feature list

## Inputs & assumptions
- inputs: business strategy context, research evidence
- assumptions: label every market/user assumption; outcomes built on them
  inherit the label

## Workflow
1. **Vision** — one paragraph: the world this product creates.
2. **Outcomes** — 2-4 measurable outcomes (activation rate, time-to-value,
   retention) with how each is counted.
3. **Job & users** — the core job; who has it; who does not.
4. **Scope discipline** — the committed scope and the explicit exclusions.
5. **Sequencing** — order by dependencies and risk: what must be learned
   first, what unblocks everything.
6. **Metrics** — the outcome metrics and review cadence.
7. **Review** — challenge: is any "outcome" actually a feature in disguise?

## Evidence requirements
- Outcomes trace to user problems from research, not to features.
- Exclusions are deliberate and recorded.

## Artifact contract
- `product-strategy`: vision, outcomes (measurable), core job, scope +
  exclusions, sequencing, metrics.

## Quality gates (definition of done)
- [ ] Outcomes measurable and counted
- [ ] Scope exclusions explicit
- [ ] Sequencing justified by dependencies/risk
- [ ] An executor could proceed without asking "what next?"

## Verification
- Re-read: could a PM execute this directly?
- Check each outcome has a counting method.

## Failure & recovery
| failure | recovery |
|---|---|
| feature-list vision | re-anchor on outcomes and the job |
| scope creep | cut to committed outcomes; park the rest |
| unstated trade-off | surface it explicitly before proceeding |

## Escalation
- Strategy requiring capabilities the org lacks — escalate the capability
  decision rather than quietly assuming it.

## Handoff
- receives: business strategy, research evidence
- passes: product strategy (outcomes, scope, sequencing) to roadmap and PRD

## Evaluation
The org evaluates this skill by outcome measurability and scope discipline.

## Observability
- Record vision, outcomes, and scope exclusions in the project decision log.

## References
- references/methodology.md — outcome definition and scope discipline