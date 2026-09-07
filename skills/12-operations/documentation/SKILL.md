---
id: documentation
name: Documentation
description: "Verified documentation — accurate, executable, maintained — with command verification."
category: 12-operations
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [shell.write, repo.search]
risk_level: low
cost_level: low
dependencies: []
compatible_agents: [documentation-agent, operations-director]
tags: [documentation, docs]
contract:
  prerequisites:
    - "the system/change to document"
  preferred_agents: [documentation-agent]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "commands in docs executed and verified"
  artifact_contract:
    - "documentation (accurate, verified commands)"
  quality_gates:
    - "commands executed, not guessed"
    - "docs match the current system"
    - "quick-start works from scratch"
  verification:
    - "run the documented commands end-to-end"
  failure_modes:
    guessed_commands: "execute before writing"
    stale_docs: "update with the change; flag drift"
  escalation:
    - "docs blocking usage (escalate the underlying gap)"
  handoff_in:
    - "system/change"
  handoff_out:
    - "verified documentation"
  evaluation:
    - "command accuracy (executed)"
    - "freshness"
  observability:
    - "record verification results"
  related_skills: [quality-gates, deployment, status-reporting]
---

# Documentation

## Purpose
Write documentation that is accurate and executable: every command run and
verified, every claim matching the current system.

## When to use / When NOT to use
- use: after changes, before handoffs, for onboarding
- avoid: guessing commands; avoid writing docs for systems you did not
  check

## Inputs & assumptions
- inputs: system/change
- assumptions: docs describe the current state — verify before writing

## Workflow
1. Explore the actual system (repo.search) and the change.
2. Draft: quick-start, usage, configuration, troubleshooting.
3. Execute every command in the docs; fix until they work.
4. Check the quick-start from a clean state.
5. Record verification evidence.

## Evidence requirements
- Commands executed with results; the quick-start works.

## Artifact contract
- `documentation`: quick-start, usage, configuration, troubleshooting,
  verification notes.

## Quality gates (definition of done)
- [ ] Commands executed
- [ ] Docs match the current system
- [ ] Quick-start works from scratch

## Verification
- Run the documented commands end-to-end.

## Failure & recovery
| failure | recovery |
|---|---|
| guessed command | execute before writing |
| stale docs | update; flag drift |
| missing setup step | add it; re-run the quick-start |

## Escalation
- Docs blocking usage — escalate the underlying gap.

## Handoff
- receives: system/change
- passes: verified documentation

## Evaluation
The org evaluates this skill by executed command accuracy and freshness.

## Observability
- Record verification results in the audit trail.

## References
- references/patterns.md — doc structures per type