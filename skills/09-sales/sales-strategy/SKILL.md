---
id: sales-strategy
name: Sales Strategy
description: "Sales strategy — ICP, motion, pipeline, objections, metrics — evidence-driven with testable assumptions."
category: 09-sales
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search]
risk_level: low
cost_level: low
dependencies: [prospect-analysis, sales-analysis]
compatible_agents: [sales-director, sales-analyst]
tags: [sales, strategy, pipeline]
contract:
  prerequisites:
    - "the product, offer, and current pipeline data"
  preferred_agents: [sales-director, sales-analyst]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "strategy decisions tied to pipeline evidence"
  artifact_contract:
    - "sales strategy (ICP, motion, pipeline, objections, metrics)"
  quality_gates:
    - "ICP defined with evidence"
    - "sales motion matched to deal size"
    - "objection handling grounded in real objections"
    - "metrics defined"
  verification:
    - "check the strategy against pipeline data"
  failure_modes:
    assumption_fog: "label assumptions; test them"
    no_pipeline_link: "tie every lever to a pipeline stage"
  escalation:
    - "pipeline problems that are product problems"
  handoff_in:
    - "product, offer"
    - "pipeline data"
  handoff_out:
    - "sales strategy with metrics"
  evaluation:
    - "evidence-pipeline alignment"
    - "assumption labeling"
  observability:
    - "record strategy and assumptions"
  related_skills: [sales-analysis, pipeline-analysis, prospect-analysis]
---

# Sales Strategy

## Purpose
Decide how to sell: ICP, sales motion, pipeline levers, objection handling,
metrics — grounded in pipeline evidence with labeled assumptions.

## When to use / When NOT to use
- use: sales planning, motion changes, pipeline underperformance
- avoid: strategy without pipeline data (or the explicit gap); avoid
  inventing objection lists

## Inputs & assumptions
- inputs: product, offer, pipeline data
- assumptions: every assumption labeled; test before scaling

## Workflow
1. Define the ICP from evidence (who buys, who churns).
2. Choose the motion: self-serve / low-touch / high-touch by deal size and
   cycle.
3. Map pipeline levers: lead gen → qualification → demo → close; find the
   leakiest stage from data.
4. Objection handling from real objections (call notes, churn data) — not
   invented.
5. Metrics: pipeline coverage, conversion per stage, cycle time, CAC.
6. Produce the strategy with the plan to test assumptions.

## Evidence requirements
- Decisions tied to pipeline evidence; assumptions labeled.

## Artifact contract
- `sales-strategy`: ICP, motion, pipeline levers, objection map, metrics,
  assumptions.

## Quality gates (definition of done)
- [ ] ICP evidence-defined
- [ ] Motion matched to deal size
- [ ] Objections real (sourced)
- [ ] Metrics defined

## Verification
- Check the strategy against pipeline data.

## Failure & recovery
| failure | recovery |
|---|---|
| assumption fog | label and test |
| no pipeline link | tie levers to stages |
| invented objections | source them from data |

## Escalation
- Pipeline problems that are really product problems — escalate with
  evidence.

## Handoff
- receives: product, offer, pipeline data
- passes: sales strategy with metrics

## Evaluation
The org evaluates this skill by evidence-pipeline alignment and assumption
labeling.

## Observability
- Record the strategy and assumptions in the project.

## References
- references/patterns.md — motion selection and lever mapping