---
id: executive-briefing
name: Executive Briefing
description: Prepare concise executive briefs — situation, recommendation, options, risks.
category: 11-agency
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [executive, briefing, decision]
compatible_agents: [executive, chief-of-staff]
---

# Executive Briefing

## Purpose
Give the executive (human or agent) what they need to decide: the situation,
the recommendation, the options, the risks — in under 400 words.

## Structure
```markdown
## Briefing: <topic>
**Situation** — 2-3 sentences of current state (evidence).
**Recommendation** — the single suggested action.
**Options** — 2-3 alternatives with one-line trade-offs.
**Risks** — top 2-3 with mitigations.
**Decision needed** — the specific question and deadline.
**If no decision** — what happens by default (and its risk).
```

## Rules
- Lead with the recommendation, not the history.
- Every claim in the situation section is traceable to state/events.
- If the executive must read 3 pages to decide, the briefing failed.