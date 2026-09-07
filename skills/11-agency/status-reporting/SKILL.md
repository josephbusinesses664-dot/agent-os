---
id: status-reporting
name: Status Reporting
description: "Evidence-based status reports — done, in progress, blocked, next — with verified claims."
category: 11-agency
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
dependencies: []
compatible_agents: [project-manager, operations-director, chief-of-staff]
tags: [status, reporting, communication]
contract:
  prerequisites:
    - "task/project state (from the task store)"
  preferred_agents: [project-manager]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "done claims traceable to verified results"
  artifact_contract:
    - "status report (done, in progress, blocked, next, risks)"
  quality_gates:
    - "done = verified, not claimed"
    - "blockers named with impact"
    - "next steps concrete"
  verification:
    - "check each done item against its acceptance criteria"
  failure_modes:
    claimed_done: "verify before reporting done"
    blocker_fog: "name the blocker and its impact"
  escalation:
    - "status that reveals a slipping commitment"
  handoff_in:
    - "task/project state"
  handoff_out:
    - "status report for stakeholders"
  evaluation:
    - "claim verification"
    - "blocker clarity"
  observability:
    - "record the report"
  related_skills: [coordination, monitoring, quality-gates]
---

# Status Reporting

## Purpose
Report status with evidence: what is verified-done, what is in progress,
what is blocked (with impact), and what is next.

## When to use / When NOT to use
- use: regular reporting, milestone checkpoints
- avoid: reporting "done" without verification; avoid blocker-fog

## Inputs & assumptions
- inputs: task/project state
- assumptions: reports are only as good as the state they read — use the
  task store

## Workflow
1. Pull task/project state.
2. Classify: verified-done (passed acceptance criteria), in progress,
   blocked, not started.
3. For each done item: evidence (test result, artifact).
4. For each blocker: name, impact, who can unblock.
5. Next steps with owners.
6. Produce the report.

## Evidence requirements
- Done claims traceable to verified results.

## Artifact contract
- `status-report`: done (with evidence), in progress, blocked (impact),
  next, risks.

## Quality gates (definition of done)
- [ ] Done = verified
- [ ] Blockers named with impact
- [ ] Next steps concrete

## Verification
- Check each done item against its acceptance criteria.

## Failure & recovery
| failure | recovery |
|---|---|
| claimed done | verify first |
| blocker fog | name it and its impact |
| slipping commitment | escalate with the report |

## Escalation
- Status revealing a slipping commitment — escalate with the report.

## Handoff
- receives: task/project state
- passes: status report to stakeholders

## Evaluation
The org evaluates this skill by claim verification and blocker clarity.

## Observability
- Record the report in the project.

## References
- references/patterns.md — report formats per audience