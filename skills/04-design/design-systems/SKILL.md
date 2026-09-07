---
id: design-systems
name: Design Systems
description: Build and maintain design systems — tokens, components, documentation, governance.
category: 04-design
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [design-system, tokens, components]
compatible_agents: [design-systems-engineer, ui-designer, frontend-lead]
---

# Design Systems

## Purpose
Create a system where consistency is the default: tokens → primitives →
components → patterns, all documented.

## Layers
1. **Tokens** — color, type, spacing, radius, shadow, motion. Single source of
   truth; dark mode = token swap.
2. **Primitives** — button, input, card, badge, tooltip — no business logic.
3. **Components** — composed primitives with domain meaning (UserCard, MetricTile).
4. **Patterns** — page templates and flows (empty state pattern, error pattern).

## Governance
- Additions need: purpose, usage, do/don't examples, a11y notes, API spec.
- Naming: semantic (surface, text-muted), never visual (blue, light-gray).
- Versioning: semantic versioning for breaking changes.

## Rules
- If a component exists, use it — no drift variants.
- Deprecate loudly, remove cleanly.
- Document the "why" of each decision, not just the "what".