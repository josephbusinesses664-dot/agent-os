---
id: proposals
name: Proposals
description: "Evidence-based proposals — problem, approach, scope, deliverables, pricing, risks — with honest assumptions."
category: 11-agency
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: high
cost_level: low
dependencies: [client-onboarding, project-planning]
compatible_agents: [project-manager, operations-director]
tags: [agency, proposals, sales]
contract:
  prerequisites:
    - "onboarding brief (goals, constraints)"
  preferred_agents: [project-manager]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "scope and pricing grounded in the brief"
    - "assumptions and exclusions explicit"
  artifact_contract:
    - "proposal (problem, approach, scope, deliverables, pricing, risks)"
  quality_gates:
    - "scope matches the brief"
    - "deliverables concrete"
    - "exclusions stated"
    - "pricing tied to scope"
  verification:
    - "check scope against the brief line by line"
  failure_modes:
    vague_scope: "concrete deliverables or the proposal will fail later"
    hidden_exclusions: "state exclusions — silently missing work destroys trust"
  escalation:
    - "proposals whose scope exceeds capacity"
  handoff_in:
    - "onboarding brief"
  handoff_out:
    - "proposal for client review"
  evaluation:
    - "scope-brief alignment"
    - "exclusion clarity"
  observability:
    - "record the proposal and its status"
  related_skills: [client-onboarding, project-planning, status-reporting]
---

# Proposals

## Purpose
Write proposals that survive contact with the client: problem, approach,
concrete scope, deliverables, pricing tied to scope, and explicit
exclusions and risks.

## When to use / When NOT to use
- use: any client engagement
- avoid: proposing without the onboarding brief; avoid vague scope that
  defers every decision to change-requests

## Inputs & assumptions
- inputs: onboarding brief
- assumptions: everything not in scope is excluded — say so explicitly

## Workflow
1. Restate the client's problem and goals from the brief.
2. Choose the approach with a one-line rationale.
3. Define scope as concrete deliverables with acceptance notes.
4. State exclusions explicitly.
5. Price against scope; state what the price assumes (revisions, access,
   timeline).
6. List risks with mitigations.

## Evidence requirements
- Scope and pricing grounded in the brief; assumptions and exclusions
  explicit.

## Artifact contract
- `proposal`: problem, approach, deliverables, exclusions, pricing
  (assumptions), risks, timeline.

## Quality gates (definition of done)
- [ ] Scope matches the brief
- [ ] Deliverables concrete
- [ ] Exclusions stated
- [ ] Pricing tied to scope

## Verification
- Check scope against the brief line by line.

## Failure & recovery
| failure | recovery |
|---|---|
| vague scope | make deliverables concrete |
| hidden exclusions | state them |
| over-capacity | cut scope or escalate |

## Escalation
- Proposals whose scope exceeds capacity — escalate the scope decision.

## Handoff
- receives: onboarding brief
- passes: proposal for client review

## Evaluation
The org evaluates this skill by scope-brief alignment and exclusion
clarity.

## Observability
- Record the proposal and its status in the project.

## References
- references/patterns.md — deliverable phrasing and exclusion lists