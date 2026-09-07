---
id: design-quality
name: Design Quality
description: The design-quality bar: hierarchy, typography, spacing, color, motion discipline. Design quality is an engineering requirement.
category: 04-design
version: 1.0.0
source: agent-os core library (adapted from MengTo/design methodology + impeccable review criteria)
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [design, quality, polish]
compatible_agents: [design-director, ui-designer, frontend-lead, motion-engineer]
---

# Design Quality

## Purpose
Define and apply the quality bar so interfaces read as one deliberate system
instead of default AI-template output.

## The checklist
1. **Hierarchy** — one primary action per screen; size/weight/color encode
   importance; nothing competes for attention by accident.
2. **Typography** — max 2 typefaces; consistent scale (modular, not arbitrary);
   line-height 1.4-1.6 for body; measure 45-75 chars.
3. **Spacing** — consistent spacing scale (4/8px base); whitespace is the
   cheapest design tool; group related elements.
4. **Color** — a small token palette; 60/30/10 balance; contrast ≥ 4.5:1 text;
   color never the only signal.
5. **Alignment & grids** — 8px grid discipline; consistent radii (tokenized).
6. **States** — hover, active, focus, disabled, empty, loading, error — every
   interactive element has all states.
7. **Copy** — concise, specific, human; buttons say what they do.
8. **Motion** — purposeful, brief (150-300ms), eased; never gratuitous;
   respect prefers-reduced-motion.

## Rules
- Polish is not decoration: it is removing the friction and noise that make
  UI feel generic. Every element must earn its place.
- When in doubt, simplify. A sparse, confident layout beats a busy one.
- Evaluate against this checklist before calling any UI "done".