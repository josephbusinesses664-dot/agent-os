---
id: coordination
name: Coordination
description: Coordinate departments and agents — handoffs, dependencies, communication hygiene.
category: 11-agency
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [coordination, handoff, communication]
compatible_agents: [chief-of-staff, operations-director, project-manager]
---

# Coordination

## Purpose
Make handoffs between agents/departments clean: context travels, nothing is
lost, and dependencies are explicit.

## Handoff protocol
Every handoff carries:
1. **State** — what exists, where (paths/ids), what works.
2. **Context** — decisions made, constraints, terms used.
3. **Open items** — what's unresolved and who owns it.
4. **Next steps** — what the receiving agent should do first.

## Communication hygiene
- Structured messages for task/status/decisions; chat for discussion.
- Decisions are recorded in the project decision log, not just discussed.
- Blockers escalate through the chain: worker → lead → director → executive,
  with a message (not silence).

## Rules
- If it takes more than one sentence to explain a handoff, the state isn't
  being persisted — fix the state, not the explanation.
- Duplicate work = failed coordination: check the task list before starting.