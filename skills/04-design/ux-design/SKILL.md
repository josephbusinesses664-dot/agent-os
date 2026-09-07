---
id: ux-design
name: UX Design
description: UX design — flows, IA, usability, feedback, error recovery, mobile UX.
category: 04-design
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [ux, flows, usability]
compatible_agents: [ux-designer, product-manager, design-director]
---

# UX Design

## Purpose
Design flows users can complete without instructions: obvious next steps,
clear feedback, and graceful recovery from errors.

## Method
1. **User journey** — map entry → first value → habit. Design the whole arc.
2. **Task flows** — step-by-step for the 3-5 core tasks; count the clicks/steps
   and minimize.
3. **Information architecture** — organize by user mental model; label with
   user language; test findability.
4. **Feedback** — every action has a visible result within 100ms (optimistic UI)
   or a clear loading/error state.
5. **Error recovery** — errors say what happened, why, and how to fix; never
   dead-end; preserve input.
6. **Mobile** — thumb zones, 44px targets, no hover dependency, offline states.

## Principles
- Don't make users remember: show state and choices.
- Defaults are decisions made for users; choose them carefully.
- Progressive disclosure for advanced features.

## Rules
- Test the flow as a fresh user (no institutional knowledge). If you can't
  complete it without guessing, redesign.
- Every screen answers: where am I, what can I do, where can I go?