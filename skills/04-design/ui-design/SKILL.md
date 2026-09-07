---
id: ui-design
name: UI Design
description: "Purpose-driven UI — hierarchy, states, responsive, accessible, consistent — with verification against intent."
category: 04-design
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [browser.open, browser.snapshot]
risk_level: low
cost_level: low
dependencies: [ux-design, visual-hierarchy]
compatible_agents: [ui-designer, frontend-lead]
tags: [ui, design, interface]
contract:
  prerequisites:
    - "the UX flow and product intent"
  preferred_agents: [ui-designer, frontend-lead]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: medium
  expected_latency: hours
  evidence_requirements:
    - "design decisions traceable to user goals"
  artifact_contract:
    - "UI design (screens, states, responsive behavior, accessibility notes)"
  quality_gates:
    - "every screen has all states: loading, empty, error, success"
    - "responsive breakpoints checked"
    - "hierarchy: one focal point per screen"
  verification:
    - "build/inspect each state; verify responsive behavior"
  failure_modes:
    template_look: "re-anchor on the product's unique job; avoid default framework styling"
    missing_states: "design all states before sign-off"
  escalation:
    - "designs that require impossible performance budgets"
  handoff_in:
    - "UX flow"
    - "product intent"
  handoff_out:
    - "UI design with states and specs for frontend"
  evaluation:
    - "state coverage"
    - "intent fidelity"
    - "responsive correctness"
  observability:
    - "record design decisions and state coverage"
  related_skills: [ux-design, visual-hierarchy, design-quality, frontend-engineering]
---

# UI Design

## Purpose
Produce purpose-driven interfaces: clear hierarchy, complete states,
responsive and accessible behavior — designed against the product's job,
never from a template.

## When to use / When NOT to use
- use: any interface design work
- avoid: designing without the UX flow or intent; avoid applying
  framework-default styling as a design

## Inputs & assumptions
- inputs: UX flow, product intent
- assumptions: audience and device assumptions labeled (mobile-first vs
  desktop, expertise level)

## Workflow
1. Translate the UX flow into screens; one clear focal action per screen.
2. Design all states per screen: loading, empty, error, success, hover,
   focus, disabled.
3. Apply visual hierarchy (see visual-hierarchy) and a consistent system
   (see design-systems).
4. Design responsive behavior at target breakpoints.
5. Check accessibility constraints (contrast, keyboard, reduced motion).
6. Produce specs that a frontend engineer can build without guessing.

## Evidence requirements
- Design decisions traceable to user goals — "because it looks nice" is not
  a rationale.

## Artifact contract
- `ui-design`: screens with states, responsive rules, accessibility notes,
  handoff specs.

## Quality gates (definition of done)
- [ ] All states designed per screen
- [ ] Responsive breakpoints checked
- [ ] One focal point per screen
- [ ] Accessibility constraints met in design

## Verification
- Inspect the built result in a browser per state.
- Resize through breakpoints and check behavior.

## Failure & recovery
| failure | recovery |
|---|---|
| template look | re-anchor on the unique job; customize deliberately |
| missing states | design all states before sign-off |
| impossible perf budget | simplify; escalate the trade |

## Escalation
- Designs requiring impossible performance budgets — escalate the trade
  consciously.

## Handoff
- receives: UX flow, product intent
- passes: UI design (states, responsive, accessibility, specs) to frontend

## Evaluation
The org evaluates this skill by state coverage, intent fidelity, and
responsive correctness — visual appeal alone does not pass.

## Observability
- Record design decisions and state coverage in the project.

## References
- references/patterns.md — state design and responsive rules