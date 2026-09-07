---
id: growth-strategy
name: Growth Strategy
description: "Loop-based growth — acquisition, activation, retention, loops — with falsifiable experiments."
category: 08-marketing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search]
risk_level: low
cost_level: low
dependencies: [marketing-strategy, conversion-optimization]
compatible_agents: [growth-agent, marketing-director]
tags: [growth, loops, retention]
contract:
  prerequisites:
    - "the product and its current funnel"
  preferred_agents: [growth-agent, marketing-director]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "growth levers tied to funnel evidence"
  artifact_contract:
    - "growth strategy (levers, loops, experiments, metrics)"
  quality_gates:
    - "retention considered before acquisition"
    - "growth loops mapped"
    - "each lever has a falsifiable experiment"
  verification:
    - "check the loop logic: does each iteration feed the next?"
  failure_modes:
    vanity_growth: "acquisition without retention measurement"
    fake_loop: "a loop that does not actually feed itself"
  escalation:
    - "retention problems that acquisition cannot fix"
  handoff_in:
    - "product"
    - "funnel"
  handoff_out:
    - "growth strategy with experiments"
  evaluation:
    - "retention-first thinking"
    - "loop correctness"
  observability:
    - "record growth plan and experiments"
  related_skills: [marketing-strategy, conversion-optimization, analytics]
---

# Growth Strategy

## Purpose
Find and exploit growth levers: map acquisition → activation → retention →
loops, and design falsifiable experiments — retention first.

## When to use / When NOT to use
- use: growth planning, post-launch, scaling
- avoid: acquisition pushes without retention measurement (leaky bucket);
  avoid "growth loops" that do not actually loop

## Inputs & assumptions
- inputs: product, current funnel
- assumptions: funnel numbers assumed unless measured — label them

## Workflow
1. Map the funnel: acquisition, activation, retention, revenue.
2. Find the leakiest, highest-leverage stage from evidence.
3. Map growth loops (e.g. content → traffic → signups → content); verify
   each loop actually feeds itself.
4. For each lever, write a falsifiable experiment with a metric.
5. Sequence by leverage and cost.
6. Produce the strategy.

## Evidence requirements
- Levers tied to funnel evidence; loops verified to feed themselves.

## Artifact contract
- `growth-strategy`: funnel map, levers, loops (verified), experiments
  (hypothesis, metric, decision rule).

## Quality gates (definition of done)
- [ ] Retention considered before acquisition
- [ ] Loops mapped and self-feeding
- [ ] Every lever falsifiable
- [ ] Metrics countable

## Verification
- Trace each loop: does one iteration feed the next?

## Failure & recovery
| failure | recovery |
|---|---|
| vanity growth | measure retention before scaling acquisition |
| fake loop | fix or drop the loop |
| leaky funnel | fix retention before pushing more traffic |

## Escalation
- Retention problems acquisition cannot fix — escalate with evidence.

## Handoff
- receives: product, funnel
- passes: growth strategy with experiments and metrics

## Evaluation
The org evaluates this skill by retention-first thinking and loop
correctness.

## Observability
- Record the growth plan and experiments in the project.

## References
- references/patterns.md — loop mapping and leak finding