---
id: workflow-automation
name: Workflow Automation
description: Automate repeatable workflows — triggers, steps, approvals, recovery.
category: 13-automation
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [automation, workflows, triggers]
compatible_agents: [operations-director, ai-engineer]
---

# Workflow Automation

## Purpose
Automate anything repeatable — but design workflows so failures are visible
and recoverable, not silent.

## Design rules
1. **Trigger** — a clear event/condition starts the workflow (message, task
   state, schedule, webhook).
2. **Steps** — each step has an owner (agent role or code) and a defined
   output; keep steps single-purpose.
3. **State** — progress persists; a crash resumes, never restarts blind.
4. **Errors** — every step defines: retry policy (transient), branch (failure
   path), and escalation (human for high-risk).
5. **Gates** — human approval where consequences are irreversible.
6. **Observability** — events and logs per run; a dashboard that shows the
   pipeline working.
7. **Idempotency** — re-running a workflow must not duplicate side effects.

## Rules
- Automate the 80% that's identical; keep judgment steps human/agent-reviewed.
- If a workflow needs babysitting, the automation is incomplete — fix it.