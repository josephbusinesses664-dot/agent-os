---
id: conversion-optimization
name: Conversion Optimization
description: "Hypothesis-driven CRO — funnel analysis, experiments, measurement — with falsifiable tests."
category: 08-marketing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.scrape, browser.open]
risk_level: low
cost_level: low
dependencies: [marketing-strategy, landing-page-design]
compatible_agents: [growth-agent, marketing-director]
tags: [conversion, cro, experiments]
contract:
  prerequisites:
    - "a funnel with data (or the ability to instrument it)"
  preferred_agents: [growth-agent, marketing-director]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "each experiment has a falsifiable hypothesis and metric"
  artifact_contract:
    - "CRO plan (funnel analysis, hypotheses, experiments, metrics)"
  quality_gates:
    - "changes driven by funnel evidence, not vibes"
    - "each experiment isolates one variable"
    - "measurement defined before the change"
  verification:
    - "check the experiment could fail (falsifiable)"
  failure_modes:
    shotgun: "one variable per experiment"
    metric_gaming: "pick metrics tied to revenue, not vanity"
  escalation:
    - "funnel drop-offs requiring product changes"
  handoff_in:
    - "funnel data"
  handoff_out:
    - "CRO plan with experiments and metrics"
  evaluation:
    - "hypothesis quality"
    - "measurement discipline"
  observability:
    - "record hypotheses and results"
  related_skills: [marketing-strategy, landing-page-design, analytics]
---

# Conversion Optimization

## Purpose
Improve conversion through the funnel with evidence: analyze the funnel,
form falsifiable hypotheses, run one-variable experiments, measure.

## When to use / When NOT to use
- use: when funnel data exists and conversion is a priority
- avoid: redesigning pages on opinion; avoid experiments with no defined
  metric

## Inputs & assumptions
- inputs: funnel data
- assumptions: traffic volume and test duration assumed — label them
  (underpowered tests mislead)

## Workflow
1. Analyze the funnel: where do users drop?
2. Rank drop-off points by revenue impact.
3. For each, form a falsifiable hypothesis (why they drop, what change
   fixes it).
4. Design the experiment: one variable, a primary metric, a decision rule.
5. Define the measurement (sample size, duration) before changing.
6. Implement; measure; decide keep/revert.

## Evidence requirements
- Every experiment: hypothesis, variable, metric, decision rule.

## Artifact contract
- `cro-plan`: funnel analysis, ranked hypotheses, experiments (variable,
  metric, decision rule), results.

## Quality gates (definition of done)
- [ ] Changes driven by funnel evidence
- [ ] One variable per experiment
- [ ] Measurement defined before change
- [ ] Decision rule pre-committed

## Verification
- Check each experiment could fail — a hypothesis that cannot fail is not
  a hypothesis.

## Failure & recovery
| failure | recovery |
|---|---|
| shotgun changes | isolate one variable |
| vanity metrics | tie metrics to revenue |
| underpowered test | check sample size before running |

## Escalation
- Drop-offs requiring product changes — escalate with the funnel evidence.

## Handoff
- receives: funnel data
- passes: CRO plan with experiments and metrics

## Evaluation
The org evaluates this skill by hypothesis quality and measurement
discipline.

## Observability
- Record hypotheses and results in the project.

## References
- references/patterns.md — funnel analysis and experiment design