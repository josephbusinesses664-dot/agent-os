---
id: ui-design
name: UI Design
description: Visual UI design — typography, color systems, spacing, grids, components, states.
category: 04-design
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [ui, visual, components]
compatible_agents: [ui-designer, design-director, frontend-lead]
---

# UI Design

## Purpose
Produce visual design that is polished, consistent and buildable — not
"template-looking".

## Foundations
- **Type scale**: 3-5 sizes from a base (e.g. 14/16/20/28/36), fluid where useful.
- **Color tokens**: background/surface/text/muted/border/accent/success/warning/
  danger; use semantic tokens, not raw hexes, in code.
- **Spacing**: 4px base scale (4,8,12,16,24,32,48,64). No off-grid values.
- **Radii/borders/shadows**: tokenized (sm/md/lg); shadows imply elevation only.
- **Components**: consistent anatomy (padding, radius, typography per component
  type); a button looks like a button everywhere.

## States (mandatory)
hover, active/focus-visible (visible focus ring), disabled, loading, empty,
error. Missing states are the #1 sign of template UI.

## Dark & light
Design both unless explicitly told otherwise; use tokens so switching is trivial.

## Rules
- Real content in mockups (no lorem ipsum for decisions).
- Density matters: dashboards should be information-dense but scannable.
- Build in the actual stack when possible; verify in-browser.