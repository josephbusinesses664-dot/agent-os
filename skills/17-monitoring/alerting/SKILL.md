---
id: alerting
name: Alerting
description: Design alerts that demand action — thresholds, severities, runbooks.
category: 17-monitoring
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [alerting, alerts, oncall]
compatible_agents: [monitoring-agent, operations-director]
---

# Alerting

## Purpose
Alert on the symptoms that require action — early enough, rarely enough that
alerts still mean something.

## Design
1. **Alert on symptoms** — "task failed 3× in 10 min", "queue depth > 500",
   "budget at 90%", "provider errors rising" — not on raw noise.
2. **Severity** — critical (pages), warning (ticket), info (log). Match the
   response to the blast radius.
3. **Thresholds** — set from real baselines; review monthly; every alert has
   a stated false-positive tolerance.
4. **Runbooks** — each alert links to: symptoms, likely causes, first actions,
   escalation. No alert without a runbook.
5. **Silencing** — maintenance windows and duplicate suppression; deliberate,
   logged.

## Rules
- Alert fatigue is caused by alert design, not by users: if alerts are
  ignored, reduce or fix them.
- Test alerts: fire them in staging; an untested alert path is a lie.