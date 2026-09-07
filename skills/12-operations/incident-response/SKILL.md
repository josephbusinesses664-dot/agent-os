---
id: incident-response
name: Incident Response
description: Structured incident handling — detect, triage, contain, fix, learn.
category: 12-operations
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [shell]
risk_level: low
cost_level: low
tags: [incident, response, oncall]
compatible_agents: [monitoring-agent, operations-director]
---

# Incident Response

## Purpose
Handle failures in a way that minimizes damage and produces learning — with
a record, not a scramble.

## Stages
1. **Detect** — alert with evidence (what failed, when, impact).
2. **Triage** — severity (impact × scope), page vs. ticket, assign owner.
3. **Contain** — stop the bleeding before fixing the cause (rollback, disable,
   rate-limit). Containment first is not optional.
4. **Fix** — root cause with a verified remediation.
5. **Verify** — confirm recovery with real checks (not vibes).
6. **Learn** — postmortem: timeline, root cause, what worked/failed, action
   items with owners; no blame theater.

## Postmortem format
```markdown
## Incident: <id>
- Impact: ...
- Timeline: <detected → contained → fixed → verified>
- Root cause: ...
- Contributing factors: ...
- Actions: [ ] fix with owner, [ ] test with owner, [ ] monitoring with owner
```

## Rules
- Never lie in an incident: report the actual error output, not what you wish
  had happened.
- Every recurring incident gets a permanent fix or a documented decision to accept it.