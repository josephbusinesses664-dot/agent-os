---
id: ux-design
name: UX Design
description: "UX design — task flows, states, errors, onboarding — grounded in user jobs and verified by walkthrough."
category: 04-design
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [browser.open, browser.snapshot]
risk_level: low
cost_level: low
dependencies: [product-strategy]
compatible_agents: [ux-designer, product-manager]
tags: [ux, flows, usability]
contract:
  prerequisites:
    - "user jobs and the product intent"
  preferred_agents: [ux-designer, product-manager]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: medium
  expected_latency: hours
  evidence_requirements:
    - "flow decisions traceable to user jobs"
  artifact_contract:
    - "UX design (task flows, states, error handling, onboarding)"
  quality_gates:
    - "each top task has a flow with all states"
    - "error paths designed, not discovered"
    - "recovery and cancellation paths present"
  verification:
    - "walk each flow end-to-end; test error paths"
  failure_modes:
    happy_path_only: "design the error and edge paths explicitly"
    flow_overload: "split flows at decision points"
  escalation:
    - "flows that conflict with technical constraints"
  handoff_in:
    - "user jobs"
    - "product intent"
  handoff_out:
    - "UX design (flows, states, errors) to UI design"
  evaluation:
    - "flow completeness (all states)"
    - "error path quality"
  observability:
    - "record flow decisions and walkthrough results"
  related_skills: [ui-design, product-strategy, information-architecture]
---

# UX Design

## Purpose
Design task flows users can complete — including the error, edge and
recovery paths — grounded in user jobs and verified by walkthrough.

## When to use / When NOT to use
- use: before UI design, on any multi-step experience
- avoid: single-action controls (design the interaction directly); avoid
  designing flows with no user job behind them

## Inputs & assumptions
- inputs: user jobs, product intent
- assumptions: user skill level and context labeled unless researched

## Workflow
1. Restate the user jobs this experience must complete.
2. For each top task: draw the flow from entry to completion.
3. Design every state along the way: loading, empty, error, success.
4. Design the failure paths: validation errors, timeouts, retries,
   cancellation, recovery.
5. Onboarding: how a new user reaches first success.
6. Walk each flow; revise until each job completes.

## Evidence requirements
- Flow decisions traceable to user jobs; error paths designed, not left to
  runtime discovery.

## Artifact contract
- `ux-design`: task flows (all states), error/recovery paths, onboarding,
  walkthrough results.

## Quality gates (definition of done)
- [ ] Every top task has a complete flow
- [ ] Error and recovery paths designed
- [ ] Walkthroughs passed end-to-end
- [ ] Cancellation paths present where destructive

## Verification
- Walk each flow end-to-end in the built interface.
- Trigger error paths and confirm recovery works.

## Failure & recovery
| failure | recovery |
|---|---|
| happy-path-only design | add error and edge paths explicitly |
| flow overload | split at decision points |
| broken recovery | design the recovery step before shipping |

## Escalation
- Flows conflicting with technical constraints — escalate with both.

## Handoff
- receives: user jobs, product intent
- passes: UX design (flows, states, errors) to UI design

## Evaluation
The org evaluates this skill by flow completeness and error-path quality.

## Observability
- Record flow decisions and walkthrough results in the project.

## References
- references/patterns.md — error-state patterns and flow splitting rules