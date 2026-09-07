---
id: project-planning
name: Project Planning
description: "Project planning — goals, tasks, dependencies, milestones, risks — with realistic commitments."
category: 12-operations
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
dependencies: [task-decomposition, roadmap-planning]
compatible_agents: [project-manager, operations-director]
tags: [project, planning, milestones]
contract:
  prerequisites:
    - "goals and the roadmap/requirements"
  preferred_agents: [project-manager]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "estimates labeled; dependencies mapped"
  artifact_contract:
    - "project plan (tasks, dependencies, milestones, risks)"
  quality_gates:
    - "milestones tied to outcomes"
    - "dependency graph complete"
    - "commitments realistic (capacity checked)"
    - "risks with mitigations"
  verification:
    - "walk the dependency graph; check no task is orphaned"
  failure_modes:
    optimistic_commit: "label estimate confidence; check capacity"
    missing_dependency: "complete the graph"
  escalation:
    - "plans exceeding capacity"
  handoff_in:
    - "goals"
    - "roadmap/requirements"
  handoff_out:
    - "project plan for execution"
  evaluation:
    - "dependency correctness"
    - "estimate honesty"
  observability:
    - "record the plan"
  related_skills: [task-decomposition, roadmap-planning, coordination]
---

# Project Planning

## Purpose
Plan projects that can actually run: goals → tasks → dependencies →
milestones → risks, with realistic commitments and honest estimates.

## When to use / When NOT to use
- use: before execution of any multi-task effort
- avoid: optimistic dates without capacity checks; avoid plans with orphaned
  tasks

## Inputs & assumptions
- inputs: goals, roadmap/requirements
- assumptions: estimates labeled with confidence; capacity assumed unless
  checked

## Workflow
1. Derive tasks from requirements (see task-decomposition).
2. Map dependencies; complete the graph (no orphans).
3. Group into milestones tied to outcomes.
4. Estimate with confidence labels; check against capacity.
5. List risks with mitigations.
6. Produce the plan.

## Evidence requirements
- Estimates labeled; dependencies complete.

## Artifact contract
- `project-plan`: tasks (estimates, owners), dependency graph, milestones,
  risks.

## Quality gates (definition of done)
- [ ] Milestones tied to outcomes
- [ ] Dependency graph complete
- [ ] Commitments capacity-checked
- [ ] Risks with mitigations

## Verification
- Walk the dependency graph; check for orphaned tasks.

## Failure & recovery
| failure | recovery |
|---|---|
| optimistic commitment | label confidence; check capacity |
| missing dependency | complete the graph |
| scope drift | re-baseline against the plan |

## Escalation
- Plans exceeding capacity — escalate the scope trade.

## Handoff
- receives: goals, roadmap/requirements
- passes: project plan for execution

## Evaluation
The org evaluates this skill by dependency correctness and estimate
honesty.

## Observability
- Record the plan in the project.

## References
- references/patterns.md — estimation and dependency methods