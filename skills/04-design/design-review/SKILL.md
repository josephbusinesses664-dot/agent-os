---
id: design-review
name: Design Review
description: "Structured design critique — against goals and principles, severity-ranked, with concrete fixes."
category: 04-design
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [browser.open, browser.snapshot]
risk_level: low
cost_level: low
dependencies: [design-quality, ux-design]
compatible_agents: [design-director, ui-designer, frontend-lead]
tags: [design, review, critique]
contract:
  prerequisites:
    - "design or built interface"
    - "the goals it must achieve"
  preferred_agents: [design-director, ui-designer]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "findings tied to goals or principles with locations"
  artifact_contract:
    - "design review (findings ranked by severity, fixes)"
  quality_gates:
    - "reviewed against goals, not in a vacuum"
    - "findings severity-ranked"
  verification:
    - "verify each finding in the actual interface"
  failure_modes:
    vague_feedback: "re-anchor each point to a goal or principle"
    goal_unknown: "ask for the goals before reviewing"
  escalation:
    - "goal-blocking issues"
  handoff_in:
    - "design"
    - "goals"
  handoff_out:
    - "design review with ranked findings and fixes"
  evaluation:
    - "goal-anchored critique"
    - "actionable fixes"
  observability:
    - "record the review outcome"
  related_skills: [design-quality, ux-design, ui-design]
---

# Design Review

## Purpose
Critique a design against its goals — not in a vacuum — producing
severity-ranked, actionable findings.

## When to use / When NOT to use
- use: before design sign-off, when a designer asks for review
- avoid: without knowing the goals (ask first); avoid rubber-stamp reviews

## Inputs & assumptions
- inputs: design or built interface, goals
- assumptions: goals are the review contract — restate them so the review
  is judged against them

## Workflow
1. Restate the goals the design must achieve.
2. Walk the design against goals: does it accomplish each?
3. Walk the quality dimensions (see design-quality): hierarchy, spacing,
   typography, color, motion, states.
4. Record findings as (element, goal/principle violated, severity, fix).
5. Rank by severity: critical (blocks a goal) / major / minor.
6. Produce the review.

## Evidence requirements
- Every finding names the element, the goal/principle, and a concrete fix.

## Artifact contract
- `design-review`: goals restated, findings ranked (severity, element,
  principle, fix), verdict.

## Quality gates (definition of done)
- [ ] Goals restated
- [ ] Findings severity-ranked
- [ ] Every finding actionable
- [ ] Verified against the actual interface

## Verification
- Confirm each finding in the real interface (browser).

## Failure & recovery
| failure | recovery |
|---|---|
| vague feedback | re-anchor to goal or principle |
| unknown goals | ask before reviewing |
| conflicting goals | surface the conflict to the decision-maker |

## Escalation
- Goal-blocking issues — escalate with the finding and fix.

## Handoff
- receives: design, goals
- passes: design review with ranked findings and fixes

## Evaluation
The org evaluates this skill by goal-anchored critique and actionable fixes.

## Observability
- Record the review verdict and findings in the project audit trail.

## References
- references/checklist.md — review walkthrough by quality dimension