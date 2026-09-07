---
id: e2e-testing
name: End-to-End Testing
description: Full-stack e2e tests through the real running system.
category: 06-testing
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [filesystem.read, filesystem.write, shell]
risk_level: low
cost_level: low
tags: [e2e, playright, workflows]
compatible_agents: [test-engineer]
---

# End-to-End Testing

## Purpose
Verify complete workflows through the running system — UI, API and
background jobs — proving the pieces integrate.

## Approach
1. **Pick critical paths** — the 2-5 flows that define the product (signup,
   core task, checkout, export…). Depth over breadth.
2. **Start the real system** — app + its dependencies; no mocks of the parts
   under test.
3. **Drive like a user** — clicks, typing, waits for conditions; assert on
   visible outcomes, not internals.
4. **Controlled data** — seed known state; clean up after; tests must be
   repeatable.
5. **Stability** — robust selectors (roles/labels), retries for flaky waits,
   no hard-coded sleeps.

## Report
- Which flows passed/failed, with screenshots/logs on failure.
- Evidence: the run log and pass/fail summary — never "it works" without it.

## Rules
- E2E covers integration risk, not unit logic — keep the suite small and fast.
- A flaky test is a bug: fix or delete.