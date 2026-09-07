---
id: requirements-analysis
name: Requirements Analysis
description: Extract precise, testable requirements from goals, research and stakeholder input.
category: 03-product
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [requirements, analysis]
compatible_agents: [requirements-analyst, product-manager]
---

# Requirements Analysis

## Purpose
Turn fuzzy goals into precise, testable, unambiguous requirements.

## Method
1. **Clarify** — restate the goal; list assumptions; flag contradictions.
2. **Decompose** — break into functional, data, UX, performance, security,
   compliance and integration requirement areas.
3. **Write testable statements** — "The system SHALL <behavior> when <condition>."
   Reject vague words: fast, easy, nice, robust, many.
4. **Define acceptance criteria** — observable, pass/fail checks per requirement.
5. **Prioritize** — Must/Should/Could (MoSCoW) with rationale.
6. **Validate** — trace each requirement to a stated need; drop orphans.

## Common traps
- Requirements that describe implementation ("use Redis") instead of behavior.
- Requirements nobody can test.
- Implicit assumptions (scale, users, permissions) — make them explicit.

## Output
Requirements list with IDs (REQ-01…) so later artifacts can trace to them.