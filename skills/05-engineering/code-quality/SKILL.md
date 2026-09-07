---
id: code-quality
name: Code Quality
description: Engineering quality standards — clarity, type safety, error handling, naming, documentation.
category: 05-engineering
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [quality, clean-code]
compatible_agents: [frontend-lead, backend-lead, ai-engineer, code-reviewer]
---

# Code Quality

## Standards
1. **Clarity** — code reads like the intent; names say what and why; functions
   do one thing; no magic numbers/strings (named constants).
2. **Type safety** — types at boundaries; no silent `any`/`object`; models match
   reality (nullable where nullable).
3. **Error handling** — errors are typed/classified, logged with context,
   surfaced appropriately; no swallowed exceptions; no bare `except`.
4. **Structure** — small modules with clear interfaces; no god files; no
   duplicated logic (extract once, document).
5. **State** — explicit, minimal, immutable where practical; no hidden global
   state; no side effects in pure functions.
6. **Comments** — explain *why*, not *what*; comments that repeat code are noise.
7. **Docs** — public interfaces documented; README explains run/debug/test.
8. **No unnecessary abstraction** — a wrapper with one use is debt; add
   abstraction when the second caller appears or the seam is proven.

## Verification
- Lint + format clean; typecheck passes; tests pass with evidence.
- Complexity: if a reviewer needs a map to understand a function, split it.