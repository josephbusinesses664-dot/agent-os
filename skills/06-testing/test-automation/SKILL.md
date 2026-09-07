---
id: test-automation
name: Test Automation
description: Automate test execution, CI wiring, and quality gates.
category: 06-testing
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [filesystem.read, filesystem.write, shell]
risk_level: low
cost_level: low
tags: [automation, ci, quality-gates]
compatible_agents: [test-engineer, devops-engineer]
---

# Test Automation

## Purpose
Make running the quality gates cheap and automatic, so they actually run on
every change.

## Setup
1. **One command** — `test` runs unit + integration + e2e with clear output;
   `check` runs typecheck + lint + tests (the full gate).
2. **CI wiring** — the gate runs on every push/PR; failure blocks merge.
3. **Fast feedback** — unit tests in seconds; e2e in minutes; parallelize
   shards where useful.
4. **Reporting** — JUnit-style output so failures link to the failing test.

## Quality gates (Superpowers-style)
Before merge: typecheck ✓, lint ✓, unit ✓, integration ✓, review ✓.
Before deploy: + e2e ✓, security scan ✓.

## Rules
- If a gate fails on a real change, fix forward — never disable the gate
  to "unblock".
- Tests must be deterministic: same commit → same result.