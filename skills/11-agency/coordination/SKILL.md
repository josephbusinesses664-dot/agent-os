---
id: coordination
name: Coordination
description: "Multi-agent coordination — delegation, handoffs, blocker surfacing — with structured messages."
category: 11-agency
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [agent.delegate]
risk_level: medium
cost_level: low
dependencies: []
compatible_agents: [chief-of-staff, project-manager, operations-director]
tags: [coordination, delegation, handoffs]
contract:
  prerequisites:
    - "a task and the agents available to do it"
  preferred_agents: [chief-of-staff, project-manager]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "delegations carry task, constraints, and required handoff fields"
  artifact_contract:
    - "coordination log (delegations, handoffs, blockers)"
  quality_gates:
    - "task assigned with clear acceptance criteria"
    - "handoff fields explicit (what the next agent needs)"
    - "blockers surfaced, not absorbed"
  verification:
    - "check every delegation returned a structured result"
  failure_modes:
    vague_delegation: "assign acceptance criteria or the result is unverifiable"
    blocker_silence: "surface blockers; do not silently stall"
  escalation:
    - "blockers the coordinator cannot resolve"
  handoff_in:
    - "task"
    - "agent roster"
  handoff_out:
    - "delegation results with handoffs"
  evaluation:
    - "acceptance criteria quality per delegation"
    - "blocker surfacing"
  observability:
    - "record delegations and outcomes"
  related_skills: [task-decomposition, status-reporting, project-planning]
---

# Coordination

## Purpose
Coordinate work across agents: delegate with acceptance criteria, hand off
structured results, and surface blockers — never silently stall.

## When to use / When NOT to use
- use: any multi-agent effort
- avoid: delegating without acceptance criteria; avoid absorbing blockers

## Inputs & assumptions
- inputs: task, agent roster
- assumptions: agent capabilities assumed from the registry — verify
  against it

## Workflow
1. Decompose the task into delegable pieces (see task-decomposition).
2. Assign each piece with: task, constraints, acceptance criteria, required
   handoff fields.
3. Monitor; surface blockers to the right level.
4. Collect results; verify against acceptance criteria.
5. Hand off the next stage with the fields it needs.

## Evidence requirements
- Delegations carry acceptance criteria; results verified against them.

## Artifact contract
- `coordination-log`: delegations (task, criteria, result), handoffs,
  blockers.

## Quality gates (definition of done)
- [ ] Every delegation has acceptance criteria
- [ ] Handoff fields explicit
- [ ] Blockers surfaced
- [ ] Results verified against criteria

## Verification
- Check every delegation returned a structured result.

## Failure & recovery
| failure | recovery |
|---|---|
| vague delegation | add acceptance criteria |
| blocker silence | surface it |
| failed subagent | reassign or escalate with context |

## Escalation
- Blockers the coordinator cannot resolve.

## Handoff
- receives: task, agent roster
- passes: delegation results with handoffs

## Evaluation
The org evaluates this skill by acceptance-criteria quality and blocker
surfacing.

## Observability
- Record delegations and outcomes in the audit trail.

## References
- references/patterns.md — delegation and handoff field sets