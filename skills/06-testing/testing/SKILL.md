---
id: testing
name: Testing
description: Write and RUN unit and integration tests. Evidence over claims.
category: 06-testing
version: 1.0.0
source: agent-os core library (Superpowers testing methodology)
license: MIT
capability_type: skill
required_tools: [filesystem.read, filesystem.write, shell]
risk_level: low
cost_level: low
tags: [testing, unit, integration]
compatible_agents: [test-engineer, qa-director]
---

# Testing

## Purpose
Prove behavior with executed tests. "It should work" is not a test result —
the test run output is the evidence.

## Pyramid
1. **Unit** — pure logic, fast, no I/O. Cover edge cases and error paths.
2. **Integration** — real components (DB, cache, HTTP clients) with test
   doubles only at true boundaries.
3. **E2E** — critical user paths through the real system.

## Writing rules
- One behavior per test; name = the behavior ("returns 404 for unknown id").
- Arrange-Act-Assert structure; assert on outcomes, not implementation.
- No sleeps: wait on conditions; no order dependence between tests.
- Test the failure paths — errors, timeouts, denied permissions — not just happy path.
- Fixtures minimal and explicit.

## Running
- Run the actual test command and capture output: pass/fail counts and
  failures verbatim.
- Report: `N passed, M failed` with failure details. Never report "tests
  passed" without the run.

## Rules
- A bug that has no test will return: add a regression test with the fix.
- Coverage is a signal, not a goal; target the behavior that matters.