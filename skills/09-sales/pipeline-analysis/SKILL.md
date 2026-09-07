---
id: pipeline-analysis
name: Pipeline Analysis
description: "Data-driven pipeline analysis — stage metrics, leak detection, forecast — with numbers, not impressions."
category: 09-sales
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [db.query]
risk_level: low
cost_level: low
dependencies: [sales-analysis]
compatible_agents: [sales-analyst]
tags: [pipeline, analysis, forecasting]
contract:
  prerequisites:
    - "pipeline data (CRM export or database access)"
  preferred_agents: [sales-analyst]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "every claim backed by a computed number"
  artifact_contract:
    - "pipeline analysis (stage metrics, leaks, forecast, risks)"
  quality_gates:
    - "stage conversion computed from data"
    - "leaks identified with numbers"
    - "forecast labeled with confidence"
  verification:
    - "recompute key metrics from the raw data"
  failure_modes:
    impression: "compute from data or do not claim"
    stale_data: "label data vintage"
  escalation:
    - "pipeline collapse risks"
  handoff_in:
    - "pipeline data"
  handoff_out:
    - "pipeline analysis for sales strategy"
  evaluation:
    - "metric correctness"
    - "leak identification"
  observability:
    - "record metrics and data vintage"
  related_skills: [sales-analysis, sales-strategy, analytics]
---

# Pipeline Analysis

## Purpose
Analyze the sales pipeline with computed numbers: stage conversion, leaks,
forecast — labeled with confidence and data vintage.

## When to use / When NOT to use
- use: pipeline reviews, forecast calls, leak hunting
- avoid: claiming metrics you did not compute from data

## Inputs & assumptions
- inputs: pipeline data
- assumptions: data vintage and coverage recorded; conclusions inherit
  them

## Workflow
1. Load the pipeline data (db.query over CRM data).
2. Compute stage conversion rates, cycle times, deal size distributions.
3. Find the leakiest stages with numbers.
4. Build the forecast with a confidence label (weighted by stage).
5. List risks (concentration, aging deals).

## Evidence requirements
- Every claim computed from the data with the data vintage recorded.

## Artifact contract
- `pipeline-analysis`: stage metrics, leaks, forecast (confidence),
  risks.

## Quality gates (definition of done)
- [ ] Stage conversion computed
- [ ] Leaks identified numerically
- [ ] Forecast confidence labeled
- [ ] Data vintage recorded

## Verification
- Recompute key metrics from the raw data.

## Failure & recovery
| failure | recovery |
|---|---|
| impression | compute from data |
| stale data | label vintage; refresh |
| sparse data | report the sparsity; widen the window |

## Escalation
- Pipeline collapse risks — escalate with the numbers.

## Handoff
- receives: pipeline data
- passes: pipeline analysis to sales strategy

## Evaluation
The org evaluates this skill by metric correctness and leak
identification.

## Observability
- Record metrics and data vintage in the audit trail.

## References
- references/patterns.md — funnel math and forecast weighting