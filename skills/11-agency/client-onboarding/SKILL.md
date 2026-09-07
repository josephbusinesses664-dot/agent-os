---
id: client-onboarding
name: Client Onboarding
description: "Structured client intake — goals, requirements, constraints, evidence — with handoff to proposals."
category: 11-agency
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: medium
cost_level: low
dependencies: [requirements-analysis]
compatible_agents: [project-manager, operations-director]
tags: [agency, onboarding, clients]
contract:
  prerequisites:
    - "client contact and the engagement type"
  preferred_agents: [project-manager]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "client statements captured, assumptions labeled"
  artifact_contract:
    - "onboarding brief (goals, requirements, constraints, decisions)"
  quality_gates:
    - "goals stated by the client, not inferred silently"
    - "constraints (budget, timeline, access) captured"
    - "unknowns listed for the proposal"
  verification:
    - "re-read the brief against the client's words"
  failure_modes:
    assumed_goals: "verify goals with the client before proposing"
    missing_constraints: "budget/timeline/access gaps block good proposals"
  escalation:
    - "scope requests beyond the engagement type"
  handoff_in:
    - "client contact"
    - "engagement type"
  handoff_out:
    - "onboarding brief to proposals"
  evaluation:
    - "goal fidelity (client's words preserved)"
    - "constraint coverage"
  observability:
    - "record the brief as a project artifact"
  related_skills: [proposals, requirements-analysis, project-planning]
---

# Client Onboarding

## Purpose
Capture the engagement cleanly: goals in the client's words, requirements,
constraints (budget, timeline, access), and decisions — so the proposal
starts from facts, not assumptions.

## When to use / When NOT to use
- use: at the start of any client engagement
- avoid: proposing without the onboarding brief; avoid silently inferring
  goals the client did not state

## Inputs & assumptions
- inputs: client contact, engagement type
- assumptions: every inference labeled; goals are the client's, not yours

## Workflow
1. Capture the client's stated goals verbatim where possible.
2. Elicit requirements and the problem behind them.
3. Capture constraints: budget, timeline, access, stakeholders, existing
   systems.
4. List open decisions and unknowns for the proposal.
5. Produce the onboarding brief; verify against the client's words.

## Evidence requirements
- Client statements preserved; assumptions labeled.

## Artifact contract
- `onboarding-brief`: goals, requirements, constraints, open decisions,
  unknowns.

## Quality gates (definition of done)
- [ ] Goals in the client's words
- [ ] Constraints captured (budget, timeline, access)
- [ ] Unknowns listed
- [ ] Brief verified against client statements

## Verification
- Re-read the brief against the client's words.

## Failure & recovery
| failure | recovery |
|---|---|
| assumed goals | verify with the client |
| missing constraints | surface the gap before proposing |
| scope mismatch | clarify the engagement type |

## Escalation
- Scope requests beyond the engagement type — clarify or escalate.

## Handoff
- receives: client contact, engagement type
- passes: onboarding brief to proposals

## Evaluation
The org evaluates this skill by goal fidelity and constraint coverage.

## Observability
- Record the brief as a project artifact.

## References
- references/patterns.md — intake question sets per engagement type