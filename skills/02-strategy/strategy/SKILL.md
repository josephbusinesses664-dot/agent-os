---
id: strategy
name: Strategy
description: "Core strategy reasoning — where to play, how to win, what to stop doing — with explicit assumptions."
category: 02-strategy
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search]
risk_level: low
cost_level: low
dependencies: [business-strategy]
compatible_agents: [executive, chief-of-staff, product-director]
tags: [strategy, where-to-play, how-to-win]
contract:
  prerequisites:
    - "a defined competitive context and objective"
    - "willingness to make and record trade-offs"
  preferred_agents: [executive, chief-of-staff]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "choices backed by evidence or labeled assumptions"
    - "explicit discussion of what the strategy gives up"
  artifact_contract:
    - "strategy (where-to-play, how-to-win, trade-offs, stop-doing list)"
  quality_gates:
    - "strategy states what it will NOT do"
    - "trade-offs explicit"
    - "assumptions listed and reviewable"
  verification:
    - "re-read: could an outsider identify the strategy from the trade-offs?"
  failure_modes:
    everything_strategy: "force prioritization — a strategy that does everything decides nothing"
    hidden_assumption: "surface it and test it"
  escalation:
    - "strategy depending on an untested load-bearing assumption"
  handoff_in:
    - "competitive context"
    - "objective"
  handoff_out:
    - "strategy with trade-offs, stop-doing list, assumptions"
  evaluation:
    - "clarity of choices"
    - "explicitness of trade-offs"
  observability:
    - "record the strategy and its trade-offs as project decisions"
  related_skills: [business-strategy, positioning, product-strategy]
---

# Strategy

## Purpose
Make and record the core choices: where to play, how to win — and what the
organization will deliberately stop doing. A strategy that does not say no is
not a strategy.

## When to use / When NOT to use
- use: direction-setting, annual planning, before major investment
- avoid: for tactical execution questions; avoid producing a strategy without
  a context and objective

## Inputs & assumptions
- inputs: competitive context, objective
- assumptions: every load-bearing assumption listed separately and labeled

## Core framework
1. **Where to play** — segments, markets, channels chosen and rejected.
2. **How to win** — the chosen basis of competition (cost, differentiation,
   network, speed).
3. **Trade-offs** — what this choice forces the organization to give up.
4. **Stop-doing list** — activities explicitly deprioritized.
5. **Assumptions** — the load-bearing beliefs, each with a test.

## Workflow
1. Restate the objective and context.
2. Generate 2-3 candidate plays; compare on evidence of fit and win-ability.
3. Pick one; state the trade-offs it imposes.
4. Write the stop-doing list — this is the part that makes the strategy
   real.
5. List assumptions with tests; flag untested load-bearing ones.

## Evidence requirements
- Choices grounded in evidence or explicitly labeled assumptions.
- Where evidence is absent for a load-bearing belief, the strategy must say
  so and name the test.

## Artifact contract
- `strategy`: objective, where-to-play, how-to-win, trade-offs,
  stop-doing list, assumptions with tests.

## Quality gates (definition of done)
- [ ] Strategy states what it will NOT do
- [ ] Trade-offs explicit
- [ ] Load-bearing assumptions listed with tests
- [ ] An outsider could identify the strategy from the trade-offs alone

## Verification
- Re-read the trade-offs: are they real (someone would disagree)?
- Confirm the stop-doing list is specific enough to enforce.

## Failure & recovery
| failure | recovery |
|---|---|
| "do everything" strategy | force prioritization; rank and cut |
| hidden assumption | surface it, label it, add a test |
| no trade-offs visible | ask what the strategy gives up; if nothing, it is not strategic |

## Escalation
- Strategy depending on an untested load-bearing assumption — escalate with
  the assumption and a proposed cheap test.

## Handoff
- receives: competitive context, objective
- passes: strategy (where-to-play, how-to-win, trade-offs, stop-doing,
  assumptions with tests)

## Evaluation
The org evaluates this skill by clarity of choices and explicitness of
trade-offs — a strategy is judged by what it refuses.

## Observability
- Record the strategy and trade-offs in the project decision log.

## References
- references/methodology.md — trade-off analysis and assumption testing