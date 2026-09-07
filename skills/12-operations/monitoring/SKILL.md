---
id: monitoring
name: Monitoring
description: "Signal-first monitoring — what to watch, thresholds, alert coverage, dashboards — with verification."
category: 12-operations
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [tool.health]
risk_level: medium
cost_level: low
dependencies: [alerting, observability]
compatible_agents: [monitoring-agent, devops-engineer]
tags: [monitoring, metrics, health]
contract:
  prerequisites:
    - "the services/behaviors to monitor"
  preferred_agents: [monitoring-agent]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "alert coverage mapped to the risk surface"
  artifact_contract:
    - "monitoring plan (signals, thresholds, alerts, dashboards)"
  quality_gates:
    - "signals map to user-visible behavior"
    - "thresholds set from observed baselines"
    - "no alert fatigue (actionable alerts only)"
  verification:
    - "health checks executed"
  failure_modes:
    metric_dump: "each metric must drive an action or a decision"
    alert_fatigue: "review threshold; silence noise"
  escalation:
    - "unmonitored critical paths"
  handoff_in:
    - "services/behaviors"
  handoff_out:
    - "monitoring plan with alerts"
  evaluation:
    - "signal-action mapping"
    - "alert actionability"
  observability:
    - "record health check results"
  related_skills: [alerting, observability, incident-response]
---

# Monitoring

## Purpose
Decide what to monitor and alert on: signals mapped to user-visible
behavior, thresholds from observed baselines, and alerts that drive action
— with health checks actually executed.

## When to use / When NOT to use
- use: new services, launch readiness, incident follow-ups
- avoid: metric dumps no one acts on; avoid alert fatigue

## Inputs & assumptions
- inputs: services/behaviors
- assumptions: baselines assumed until measured — label them

## Workflow
1. Map the risk surface to signals (user-visible behavior first).
2. For each signal: metric, threshold (from baseline), alert, owner.
3. Check alert actionability: every alert implies a response.
4. Build dashboards for review, not just alerts.
5. Execute health checks (tool.health); record results.

## Evidence requirements
- Alert coverage mapped to the risk surface; thresholds baseline-based.

## Artifact contract
- `monitoring-plan`: signals (metric, threshold, alert, owner), dashboards,
  health results.

## Quality gates (definition of done)
- [ ] Signals map to user-visible behavior
- [ ] Thresholds from observed baselines
- [ ] No alert fatigue
- [ ] Health checks executed

## Verification
- Run health checks and record results.

## Failure & recovery
| failure | recovery |
|---|---|
| metric dump | tie each metric to an action |
| alert fatigue | raise thresholds; silence noise |
| unmonitored path | add coverage; escalate if critical |

## Escalation
- Unmonitored critical paths — escalate with the gap.

## Handoff
- receives: services/behaviors
- passes: monitoring plan with alerts

## Evaluation
The org evaluates this skill by signal-action mapping and alert
actionability.

## Observability
- Record health check results in the audit trail.

## References
- references/patterns.md — signal catalogs per service type