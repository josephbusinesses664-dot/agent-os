---
id: operations-strategy
name: Operations Strategy
description: "Operations planning — reliability, capacity, runbooks, cost — with evidence and priorities."
category: 12-operations
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
dependencies: [monitoring, incident-response]
compatible_agents: [operations-director, devops-engineer]
tags: [operations, reliability, planning]
contract:
  prerequisites:
    - "current ops state (incidents, monitoring, capacity)"
  preferred_agents: [operations-director]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "priorities tied to incident/ops evidence"
  artifact_contract:
    - "operations strategy (reliability, capacity, runbooks, cost)"
  quality_gates:
    - "priorities ranked by impact evidence"
    - "runbook coverage for known failure modes"
    - "cost decisions explicit"
  verification:
    - "check priority list against recent incident data"
  failure_modes:
    reactive_only: "balance firefighting with prevention"
    runbook_gap: "runbooks for every known failure mode"
  escalation:
    - "reliability debt blocking growth"
  handoff_in:
    - "current ops state"
  handoff_out:
    - "operations strategy with priorities"
  evaluation:
    - "evidence-based prioritization"
    - "runbook coverage"
  observability:
    - "record the strategy"
  related_skills: [monitoring, incident-response, deployment]
---

# Operations Strategy

## Purpose
Plan operations deliberately: reliability priorities from incident
evidence, capacity planning, runbook coverage, and explicit cost trade-offs.

## When to use / When NOT to use
- use: ops planning, reliability reviews, capacity crises
- avoid: prioritizing on opinion when incident data exists

## Inputs & assumptions
- inputs: current ops state
- assumptions: capacity forecasts assumed unless modeled — label them

## Workflow
1. Review the incident and monitoring evidence.
2. Rank reliability priorities by impact (frequency × severity).
3. Plan capacity with labeled forecasts and trigger points.
4. Ensure runbook coverage for every known failure mode.
5. Make cost trade-offs explicit (redundancy vs budget).
6. Produce the strategy.

## Evidence requirements
- Priorities tied to incident/ops evidence.

## Artifact contract
- `operations-strategy`: reliability priorities (evidence), capacity plan,
  runbook coverage, cost trade-offs.

## Quality gates (definition of done)
- [ ] Priorities ranked by impact evidence
- [ ] Runbook coverage for known failure modes
- [ ] Cost trade-offs explicit

## Verification
- Check the priority list against recent incident data.

## Failure & recovery
| failure | recovery |
|---|---|
| reactive only | balance firefighting with prevention |
| runbook gap | write runbooks for known failures |
| capacity guess | model it or label the assumption |

## Escalation
- Reliability debt blocking growth — escalate with evidence.

## Handoff
- receives: current ops state
- passes: operations strategy with priorities

## Evaluation
The org evaluates this skill by evidence-based prioritization and runbook
coverage.

## Observability
- Record the strategy in the project.

## References
- references/patterns.md — reliability priority frameworks