---
id: implementation-review
name: Implementation Review
description: Verify an implementation against its spec — requirements met, tests real, quality gates.
category: 06-testing
version: 1.0.0
source: agent-os core library (Superpowers implementation review)
license: MIT
capability_type: skill
required_tools: [filesystem.read]
risk_level: low
cost_level: low
tags: [review, implementation, verification]
compatible_agents: [code-reviewer, qa-director, project-manager]
---

# Implementation Review

## Purpose
Verify that implemented work actually satisfies the task/PRD before it's
accepted — requirement by requirement, with evidence.

## Process
1. **Requirements checklist** — list every requirement/acceptance criterion;
   mark each: met / not met / partially met / untestable.
2. **Run the evidence** — tests executed (output), build/typecheck passed,
   artifacts exist at the claimed paths. No evidence = not met.
3. **Quality gates** — lint/format, security scan, review findings resolved.
4. **Edge cases** — the criteria's failure paths exercised, not assumed.
5. **Verdict** — pass, pass-with-changes (list them), or fail (why, what's
   missing).
6. **Record** — review outcome on the task; failures return to the queue.

## Rules
- "It should work" is not a review. Execute or mark unverified.
- Review the *implementation*, not the author: findings on the work.
- Partial credit is a finding list, not a pass.