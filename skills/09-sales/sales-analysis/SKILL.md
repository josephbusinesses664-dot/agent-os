---
id: sales-analysis
name: Sales Analysis
description: "Sales performance analysis — conversion, win/loss, cohort, CAC — with computed evidence."
category: 09-sales
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [db.query]
risk_level: low
cost_level: low
dependencies: [pipeline-analysis]
compatible_agents: [sales-analyst]
tags: [sales, analysis, metrics]
contract:
  prerequisites:
    - "sales data (deals, stages, outcomes)"
  preferred_agents: [sales-analyst]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "every metric computed and recorded with data vintage"
  artifact_contract:
    - "sales analysis (metrics, win/loss, cohorts, recommendations)"
  quality_gates:
    - "win/loss reasons sourced from data"
    - "CAC/payback computed, not assumed"
    - "recommendations tied to computed findings"
  verification:
    - "recompute the headline metrics"
  failure_modes:
    cherry_pick: "report the full distribution, not just the flattering slice"
    no_cause: "correlate, then propose a test"
  escalation:
    - "deteriorating unit economics"
  handoff_in:
    - "sales data"
  handoff_out:
    - "sales analysis with recommendations"
  evaluation:
    - "metric correctness"
    - "recommendation grounding"
  observability:
    - "record metrics and vintage"
  related_skills: [pipeline-analysis, sales-strategy, analytics]
---

# Sales Analysis

## Purpose
Analyze sales performance with computed evidence: conversion, win/loss,
cohorts, CAC — and recommendations grounded in the numbers.

## When to use / When NOT to use
- use: performance reviews, unit-economics checks
- avoid: reporting without computing; avoid cherry-picking flattering
  slices

## Inputs & assumptions
- inputs: sales data
- assumptions: data vintage and definitions recorded

## Workflow
1. Load the data; define each metric before computing.
2. Compute: conversion per stage, win/loss by reason (from deal notes),
   cohort retention, CAC and payback.
3. Report distributions, not just averages.
4. Correlate causes; propose tests for causality.
5. Produce recommendations tied to findings.

## Evidence requirements
- Every metric computed with data vintage; win/loss reasons sourced.

## Artifact contract
- `sales-analysis`: metrics, win/loss table, cohort view, CAC/payback,
  recommendations.

## Quality gates (definition of done)
- [ ] Metrics computed from data
- [ ] Win/loss reasons sourced
- [ ] CAC/payback computed
- [ ] Recommendations tied to findings

## Verification
- Recompute the headline metrics.

## Failure & recovery
| failure | recovery |
|---|---|
| cherry-pick | report the full distribution |
| correlation as cause | propose a test |
| sparse data | label sparsity; widen the window |

## Escalation
- Deteriorating unit economics — escalate with the numbers.

## Handoff
- receives: sales data
- passes: sales analysis with recommendations

## Evaluation
The org evaluates this skill by metric correctness and recommendation
grounding.

## Observability
- Record metrics and vintage in the audit trail.

## References
- references/patterns.md — cohort and unit-economics methods