---
id: status-reporting
name: Status Reporting
description: Concise, honest status reports — progress, blockers, decisions needed, next steps.
category: 11-agency
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [status, reporting, communication]
compatible_agents: [chief-of-staff, project-manager, operations-director]
---

# Status Reporting

## Purpose
Keep humans and agents aligned with a report that takes 30 seconds to read:
what changed, what's blocked, what's needed.

## Format
```markdown
## Status — <project/org> (<date>)
### Progress
- ✅ <completed, with evidence>
- 🔄 <in progress, % where known>
### Blockers
- ⛔ <blocker + what would unblock it + who owns it>
### Decisions needed
- ❓ <decision + deadline + options>
### Next
- <the next 3 concrete steps with owners>
```

## Rules
- Report reality: a blocked task is a blocker, not "in progress".
- No filler ("working hard", "made great progress") — specifics only.
- Blocker owners and deadlines are mandatory, not optional.