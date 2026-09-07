---
id: observability
name: Observability
description: Structured logs, events, metrics and traces across agents, tasks, models, tools.
category: 17-monitoring
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [observability, logs, events, tracing]
compatible_agents: [monitoring-agent, devops-engineer]
---

# Observability

## Purpose
Make every significant action answerable: what happened, when, in which
run/task/project, at what cost.

## Layers
1. **Events** — domain events (agent.started, task.completed, model.requested,
   approval.granted) with project/task/agent context; queryable.
2. **Logs** — structured (JSON), contextual (run_id, task_id), classified
   severity; no silent swallows.
3. **Metrics** — counters/gauges: task success rate, queue depth, spend,
   latency, error rate by type.
4. **Traces** — one request/run's path through providers/tools with timing.

## Correlation
One id per run/task flows through every log line and event: `run_id`,
`task_id`, `project_id`. Without correlation ids, logs are noise.

## Rules
- Log what you'd want during an incident, not everything.
- Dashboards answer the questions ops actually asks (who's working, what's
  stuck, what's costing money).