---
id: design-review
name: Design Review
description: Structured critique of designs and interfaces against the quality bar.
category: 04-design
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [design, review, critique]
compatible_agents: [design-director, qa-director]
---

# Design Review

## Purpose
Review a design or shipped UI against explicit criteria and produce findings
ranked by severity — the design analogue of code review.

## Review dimensions
1. **Hierarchy** — does the primary action/信息 read first?
2. **Consistency** — tokens, components, spacing, radii used consistently?
3. **Typography** — scale, contrast, measure, line-height sane?
4. **States & feedback** — all interactive states present; errors recoverable?
5. **Accessibility** — keyboard, contrast, labels, reduced motion?
6. **Responsive** — mobile/tablet/desktop; no overflow, no hover-dependency?
7. **Performance & motion** — animations purposeful, bounded, GPU-cheap;
   no gratuitous effects?
8. **Copy** — concise, specific, action-oriented?

## Finding format
```
severity: critical | major | minor | nit
element: <where>
problem: <what is wrong>
why: <impact on user>
fix: <concrete recommendation>
```

## Rules
- Judge against the checklist, not taste. If it's taste, say so explicitly.
- "Looks generic/template-like" must come with a concrete cause (stock layout,
  default colors, missing states).
- Approve only when critical/major findings are resolved.