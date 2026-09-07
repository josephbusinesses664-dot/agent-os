---
id: task-decomposition
name: Task Decomposition
description: Break large work into bounded, verifiable tasks for agents.
category: 12-operations
version: 1.0.0
source: agent-os core library (Superpowers task decomposition adapted)
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [decomposition, tasks, planning]
compatible_agents: [project-manager, product-manager]
---

# Task Decomposition

## Purpose
Split work into tasks that are small enough to verify, independent enough to
parallelize, and big enough to be meaningful.

## Rules of thumb
- A task fits one agent run (minutes, not hours of tool calls).
- Each task has a clear output/artifact and pass/fail.
- Dependencies are explicit; tasks with no dependency can run in parallel.
- Risk and uncertainty get decomposed *further*, not less.

## Method
1. Start from the outcome; list the deliverables.
2. For each deliverable: what must exist, what proves it works.
3. Split by responsibility boundaries (research ≠ design ≠ build ≠ test),
   not by artificial steps.
4. Check each task: could an agent do this without asking questions?
   (If no, add context or split more.)
5. Verify the graph: every task has a path to the goal; no orphan work.

## Output
Task list with: title, description, assigned role, dependencies, acceptance
— ready for the task service.