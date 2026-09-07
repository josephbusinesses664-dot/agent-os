---
id: tech-decision
name: Technical Decision
description: "Technical decision-making — options, criteria, trade-offs, reversibility — with ADR-style records."
category: 05-engineering
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [repo.search, web.search]
risk_level: low
cost_level: low
dependencies: [architecture]
compatible_agents: [cto, software-architect, ai-engineer]
tags: [decisions, adr, tradeoffs]
contract:
  prerequisites:
    - "a decision to make and its context"
  preferred_agents: [cto, software-architect]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "each option evaluated against stated criteria"
    - "claims about options grounded (docs, code, benchmarks)"
  artifact_contract:
    - "decision record (options, criteria, trade-offs, verdict, reversibility)"
  quality_gates:
    - "≥2 options compared"
    - "criteria explicit"
    - "trade-offs recorded"
    - "reversibility assessed"
  verification:
    - "re-read: would the decision survive a challenge from each option's advocate?"
  failure_modes:
    favorite_option: "score options against criteria before declaring a favorite"
    stale_assumptions: "verify version/behavior claims against current docs"
  escalation:
    - "decisions with cross-team impact"
  handoff_in:
    - "decision"
    - "context"
  handoff_out:
    - "decision record"
  evaluation:
    - "option coverage"
    - "evidence grounding"
  observability:
    - "record the ADR in the project decision log"
  related_skills: [architecture, api-design, model-selection]
---

# Technical Decision

## Purpose
Make technical decisions transparently: options compared against explicit
criteria, trade-offs recorded, reversibility assessed — as an ADR.

## When to use / When NOT to use
- use: any non-trivial technology/architecture choice
- avoid: decisions that are trivially reversible (just pick and note it);
  avoid deciding on a favorite before comparing

## Inputs & assumptions
- inputs: decision, context
- assumptions: every assumption about scale, usage, or ecosystem labeled

## Workflow
1. State the decision and its context.
2. List ≥2 options (include "do nothing / keep current").
3. Define criteria: cost, complexity, ecosystem, risk, fit, reversibility.
4. Research each option against the criteria — verify claims against
   current docs/code (web.search/repo.search).
5. Score and compare; record trade-offs per option.
6. Assess reversibility and rollback path.
7. Write the decision record with a verdict and a trigger to revisit.

## Evidence requirements
- Claims about options grounded in docs/code/benchmarks — not memory.

## Artifact contract
- `decision-record`: decision, options, criteria, scores, trade-offs,
  verdict, reversibility, revisit trigger.

## Quality gates (definition of done)
- [ ] ≥2 options compared
- [ ] Criteria explicit
- [ ] Trade-offs recorded
- [ ] Reversibility assessed
- [ ] Verdict survives a challenge from the losing options

## Verification
- Re-read from each option's advocate perspective.

## Failure & recovery
| failure | recovery |
|---|---|
| favorite-option bias | score before declaring; adjust honestly |
| stale assumptions | verify against current docs |
| missing option | add the obvious alternative (including "do nothing") |

## Escalation
- Decisions with cross-team impact — record and route for review.

## Handoff
- receives: decision, context
- passes: decision record (ADR)

## Evaluation
The org evaluates this skill by option coverage and evidence grounding.

## Observability
- Record the ADR in the project decision log.

## References
- references/patterns.md — ADR format and criteria sets