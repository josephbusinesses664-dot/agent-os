---
id: project-planning
name: Project Planning
description: Turn goals into milestones, tasks, dependencies and assignments.
category: 12-operations
version: 1.0.0
source: agent-os core library (Superpowers planning adapted)
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [planning, milestones, project]
compatible_agents: [project-manager, operations-director]
---

# Project Planning

## Purpose
Convert a goal into a plan the system can execute: milestones → tasks →
dependencies → assignments → reviews.

## Method
1. **Goal → outcomes** — what must be true when done (measurable).
2. **Milestones** — 2-6 checkpoints, each with a definition of done.
3. **Task decomposition** — break milestones into tasks sized for one agent
   run; each task: description, acceptance, dependencies.
4. **Dependency graph** — order tasks; identify the critical path; parallel
   work where independent.
5. **Assignment** — match tasks to agent roles by capability + permission
   (never assign a tool an agent can't use).
6. **Budget & risk** — per-milestone budget; top risks with mitigations.
7. **Reviews** — gates after high-risk milestones (see quality gates).

## Rules
- Tasks must be independently verifiable — "done" is defined per task.
- Plan the plan: record it in the project, revisit at milestones.
- Unblock automatically: dependencies complete → tasks queue (the system
  handles this; the plan must declare the dependencies).