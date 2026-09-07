---
id: incident-response
name: Incident Response
description: "Structured incident response — detect, triage, mitigate, postmortem — with evidence at every step."
category: 12-operations
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [shell.write, repo.search, web.search]
risk_level: high
cost_level: low
dependencies: [monitoring, alerting]
compatible_agents: [incident-agent, operations-director]
tags: [incident, response, oncall]
contract:
  prerequisites:
    - "an incident signal (alert, report, anomaly)"
  preferred_agents: [incident-agent]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: medium
  expected_latency: minutes
  evidence_requirements:
    - "timeline of actions with timestamps"
    - "root cause evidence, not guesses"
  artifact_contract:
    - "incident report (timeline, impact, root cause, mitigations, postmortem)"
  quality_gates:
    - "severity classified before action"
    - "mitigation verified (system stable)"
    - "root cause evidence-backed"
    - "postmortem with prevention actions"
  verification:
    - "confirm the mitigation held (stability window)"
  failure_modes:
    panic_fix: "triage first, then act"
    assumed_root_cause: "evidence before declaring root cause"
  escalation:
    - "critical incidents immediately"
  handoff_in:
    - "incident signal"
  handoff_out:
    - "incident report with postmortem actions"
  evaluation:
    - "timeline quality"
    - "root-cause evidence"
  observability:
    - "record every action with timestamps"
  related_skills: [monitoring, alerting, operations-strategy]
---

# Incident Response

## Purpose
Respond to incidents structurally: classify severity, triage, mitigate,
verify, then a postmortem with prevention actions — with evidence at every
step.

## When to use / When NOT to use
- use: any incident (alert, anomaly, outage)
- avoid: panic-fixing without triage; avoid declaring root cause without
  evidence

## Inputs & assumptions
- inputs: incident signal
- assumptions: severity classification drives the response — classify
  before acting

## Workflow
1. Classify severity (SEV1-4) and impact.
2. Triage: what is affected, what is the fastest safe mitigation.
3. Mitigate; verify the system is stable (monitoring window).
4. Investigate root cause with evidence (logs, traces, reproductions).
5. Write the incident report: timeline (timestamps), impact, root cause,
   mitigations.
6. Postmortem: prevention actions with owners.

## Evidence requirements
- Timeline of actions with timestamps; root cause backed by evidence.

## Artifact contract
- `incident-report`: severity, timeline, impact, root cause (evidence),
  mitigations (verified), postmortem actions.

## Quality gates (definition of done)
- [ ] Severity classified before action
- [ ] Mitigation verified (stability window)
- [ ] Root cause evidence-backed
- [ ] Postmortem with owners

## Verification
- Confirm the mitigation held over the stability window.

## Failure & recovery
| failure | recovery |
|---|---|
| panic fix | triage first |
| assumed root cause | gather evidence |
| mitigation rolled back | re-verify and escalate |

## Escalation
- Critical incidents — escalate immediately with the triage.

## Handoff
- receives: incident signal
- passes: incident report with postmortem actions

## Evaluation
The org evaluates this skill by timeline quality and root-cause evidence.

## Observability
- Record every action with timestamps in the audit trail.

## References
- references/patterns.md — severity classification and postmortem format