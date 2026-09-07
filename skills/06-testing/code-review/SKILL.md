---
id: code-review
name: Code Review
description: Structured code review — correctness, readability, architecture, security, performance, tests, maintainability.
category: 06-testing
version: 1.0.0
source: agent-os core library (Addy Osmani code-review methodology)
license: MIT
capability_type: skill
required_tools: [filesystem.read]
risk_level: low
cost_level: low
tags: [code-review, quality]
compatible_agents: [code-reviewer, qa-director]
---

# Code Review

## Purpose
Review changes against seven dimensions and produce structured findings —
not vague "looks good".

## Dimensions
1. **Correctness** — does it do what it claims? Edge cases, off-by-one,
   race conditions, error paths?
2. **Readability** — can a new engineer understand it? Names, structure,
   unnecessary cleverness.
3. **Architecture** — fits the system's boundaries; no duplicated logic; no
   misplaced responsibilities; change is proportionate.
4. **Security** — injection, secrets, authz, unsafe input/output, dangerous
   tools/commands.
5. **Performance** — obvious inefficiency (N+1, layout thrash, blocking I/O
   in hot paths); premature optimization flagged separately.
6. **Testing** — tests exist for the behavior, cover the failure paths, and
   actually run.
7. **Maintainability** — the next change to this code is cheap; state is
   explicit; docs match reality.

## Finding format
```yaml
severity: critical | high | medium | low | nit
file: path
location: function/line
problem: <what is wrong>
reason: <why it matters>
recommended_fix: <concrete>
```

## Rules
- Block on critical/high; discuss medium; nits are optional but collected.
- Review the diff with context (surrounding code, callers), not in isolation.
- Verify claims: if a test "passes", the run output should be visible.