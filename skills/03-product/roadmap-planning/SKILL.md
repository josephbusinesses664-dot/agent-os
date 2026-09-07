---
id: roadmap-planning
name: Roadmap Planning
description: "Outcome-sequenced roadmap — themes, dependencies, sequencing by risk and learning — with assumptions labeled."
category: 03-product
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
dependencies: [product-strategy, feature-prioritization]
compatible_agents: [product-manager, product-director]
tags: [roadmap, planning, sequencing]
contract:
  prerequisites:
    - "product strategy (outcomes, scope)"
    - "prioritized features"
  preferred_agents: [product-manager, product-director]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "sequencing justified by dependencies, risk, and learning needs"
  artifact_contract:
    - "roadmap (themes, phases, dependencies, metrics per phase)"
  quality_gates:
    - "each phase has an outcome and a dependency check"
    - "riskiest assumptions scheduled earliest"
  verification:
    - "walk the roadmap: can each phase start given prior phases?"
  failure_modes:
    date_theater: "prefer confidence ranges over fake precision"
    missing_learning: "ensure the roadmap includes the experiments outcomes depend on"
  escalation:
    - "roadmap commitments that exceed realistic capacity"
  handoff_in:
    - "product strategy"
    - "prioritized features"
  handoff_out:
    - "roadmap with phases, outcomes, dependencies"
  evaluation:
    - "dependency correctness"
    - "learning-first sequencing"
  observability:
    - "store the roadmap as a project artifact"
  related_skills: [product-strategy, feature-prioritization, project-planning]
---

# Roadmap Planning

## Purpose
Sequence work into an outcome-driven roadmap — themes, phases, dependency
handling — scheduling the riskiest assumptions earliest.

## When to use / When NOT to use
- use: after strategy and prioritization, before committing a plan
- avoid: without strategy (a roadmap without outcomes is a wishlist);
  avoid promising dates with false precision

## Inputs & assumptions
- inputs: product strategy, prioritized features
- assumptions: capacity and timing assumptions labeled estimated; revisit at
  each phase boundary

## Workflow
1. Group prioritized features into outcome themes.
2. Map dependencies across themes (technical, research, market).
3. Order phases by: what must be learned first (riskiest assumption
   earliest), what unblocks the most, what delivers an outcome.
4. Attach per-phase metrics and a decision checkpoint.
5. Add the experiments the outcomes depend on — a roadmap without learning
   is a schedule, not a strategy.
6. Review capacity honestly; if commitments exceed it, cut — do not stretch.

## Evidence requirements
- Sequencing justified by dependencies, risk, and learning needs — not by
  calendar habit.

## Artifact contract
- `roadmap`: themes, phases (with outcomes and metrics), dependency map,
  riskiest-assumption schedule, capacity notes.

## Quality gates (definition of done)
- [ ] Each phase has an outcome and a dependency check
- [ ] Riskiest assumptions scheduled earliest
- [ ] Experiments/learning included
- [ ] Capacity commitments realistic

## Verification
- Walk the roadmap: can each phase start given prior phases?
- Check the riskiest assumption has a date, not a hope.

## Failure & recovery
| failure | recovery |
|---|---|
| date theater | replace false precision with confidence ranges |
| missing learning | add the experiments outcomes depend on |
| capacity overcommit | cut scope consciously; escalate the trade |

## Escalation
- Commitments exceeding realistic capacity — escalate the scope cut
  decision.

## Handoff
- receives: product strategy, prioritized features
- passes: roadmap (phases, outcomes, dependencies) to project planning and
  task decomposition

## Evaluation
The org evaluates this skill by dependency correctness and learning-first
sequencing.

## Observability
- Store the roadmap as a project artifact linked to the project.

## References
- references/methodology.md — dependency mapping and phase checkpointing