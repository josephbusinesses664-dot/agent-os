---
id: visual-hierarchy
name: Visual Hierarchy
description: Create clear visual hierarchy so users scan in the intended order.
category: 04-design
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [hierarchy, layout, visual]
compatible_agents: [ui-designer, ux-designer, design-director]
---

# Visual Hierarchy

## Purpose
Direct the eye: the user should perceive importance in the order you intend,
within ~3 seconds.

## Levers (strongest first)
1. **Position** — top-left → bottom-right reading order (or F/Z patterns).
2. **Size** — the most important element is the largest.
3. **Contrast** — darkness/density vs. background separates levels.
4. **Whitespace** — space around an element raises its importance.
5. **Color** — reserved accent for the primary action.
6. **Weight** — type weight differences over size differences when subtlety matters.

## Method
1. Sketch the content inventory; decide the 1-2 things the user must see.
2. Apply levers in order; check at arm's length — the hierarchy should read
   without reading words.
3. Test: blur the screen (or squint) — does the right thing pop first?
4. Balance: not everything can be level 1; demote aggressively.

## Rules
- One hero per viewport.
- Hierarchy supports the job (dashboard: status first; landing: value prop first).
- Never rely on color alone; combine with position/size/weight.