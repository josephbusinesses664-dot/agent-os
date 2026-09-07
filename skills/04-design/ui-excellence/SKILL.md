---
id: ui-excellence
name: UI Excellence (impeccable)
description: "Production-grade UI rules: WCAG contrast, typographic hierarchy, spacing scale, tap targets, motion restraint, and zero generic-AI-template styling. Every page ships through this gate."
category: 04-design
version: 1.0.0
source: prem-ium.inc house standard (impeccable detector methodology)
license: MIT
capability_type: skill
required_tools: [repo.tree, filesystem.read]
risk_level: low
cost_level: low
dependencies: []
compatible_agents: [design-director, ux-designer, ui-designer, frontend-lead, backend-lead]
tags: [design, ui, wcag, typography, css, quality]
contract:
  prerequisites:
    - "a concrete page to design or review"
  preferred_agents: [design-director, ux-designer, frontend-lead]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "every shipped page passes the gate below"
  artifact_contract:
    - "HTML/CSS that follows the rules; violations called out in the build report"
  quality_gates:
    - "contrast, type size, tap targets, spacing, hierarchy all pass"
---

# UI Excellence — the house gate

Every page an agent ships must pass these rules. Generic AI-template styling is
the specific failure this exists to prevent.

## Non-negotiables (WCAG floor)
- Body copy ≥ 16px; never ship 9–14px body text.
- Text contrast ≥ 4.5:1 (large text ≥ 3:1). Never gray-on-gray or white-on-lavender.
- Tap targets ≥ 44×44px; buttons have one explicit height per group (no
  border/line-height asymmetry drift).
- Visible focus states on all interactive elements.
- `max-width` containers, no horizontal body scroll at any viewport.

## Typography (make it look designed, not default)
- One display face + one text face max. Real hierarchy: step sizes by a
  consistent scale (1.25 or 1.333), not four near-identical sizes.
- Headlines tight (letter-spacing -0.01em to -0.03em), body relaxed
  (line-height 1.5–1.7). Measure: 55–75ch for reading text.
- No lorem ipsum. Real product copy with a point of view.

## Layout & spacing
- 8px-based spacing scale (8/12/16/24/32/48/64/96). Consistent section rhythm.
- One alignment language: align like elements alike; don't center paragraphs
  just to fill space.
- Real whitespace: sections breathe; cards never touch.

## Color
- A small token set: 1 accent + neutrals (e.g. 6-step gray). Define as CSS
  variables. No rainbow gradients-as-personality, no purple-on-dark-by-default.
- Dark mode via tokens, not a second palette.

## Motion
- 150–400ms ease transitions on hovers/entrances. Nothing spins or floats
  endlessly. No scroll-jacking.

## The generic-AI-template smell test
If it looks like it could be any startup's template — three cards, gradient
blob, glassmorphism everything, emoji icons as the entire visual system —
restart. Give the page ONE memorable signature element that only this product
could have.

## How to use (agents)
1. Before writing HTML: pick type pair, 3-color token set, and the one
   signature element.
2. Write the page.
3. Self-audit against every Non-negotiable above; list violations in the
   build report.
