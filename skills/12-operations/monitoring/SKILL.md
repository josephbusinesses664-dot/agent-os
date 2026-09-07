---
id: monitoring
name: Monitoring
description: Health checks, metrics, alerting and observability discipline.
category: 12-operations
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [shell]
risk_level: low
cost_level: low
tags: [monitoring, health, alerts]
compatible_agents: [monitoring-agent, devops-engineer, operations-director]
---

# Monitoring

## Purpose
Know the system is healthy and know *first* when it isn't — with actionable
alerts, not noise.

## Coverage
1. **Health checks** — dependency checks (DB, Redis, Mattermost, providers)
   with status and latency (see `agent-os health`).
2. **Metrics** — the numbers that matter: task success rate, queue depth,
   agent failures, model spend, latency, error rate.
3. **Logs** — structured, searchable, with run/task/project context.
4. **Alerts** — rule on real symptoms (task failed N times, queue backed up,
   budget crossed 90%, provider errors); every alert has a runbook.

## Alert design
- Alert on symptoms that require action, not on everything.
- Each alert: name, condition, severity, runbook link, silence policy.
- No alert fatigue: if an alert fires and nobody acts, fix the alert.

## Rules
- Dashboards answer questions; metrics without owners drift.
- Monitor the monitoring: alert failures alert.