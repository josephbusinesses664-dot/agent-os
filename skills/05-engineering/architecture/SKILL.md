---
id: architecture
name: Software Architecture
description: "Staff-grade architecture — boundaries, interfaces, data flow, trade-offs, ADRs — grounded in the actual codebase."
category: 05-engineering
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [repo.search, repo.tree]
risk_level: low
cost_level: low
dependencies: [tech-decision, backend-engineering]
compatible_agents: [cto, software-architect]
tags: [architecture, design, tradeoffs]
contract:
  prerequisites:
    - "requirements/context for the system or change"
    - "access to the codebase being architected (or a greenfield note)"
  preferred_agents: [cto, software-architect]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: medium
  expected_latency: hours
  evidence_requirements:
    - "architecture grounded in actual code (repo.search) where code exists"
    - "trade-offs explicit with alternatives"
  artifact_contract:
    - "architecture (boundaries, interfaces, data flow, ADRs)"
  quality_gates:
    - "boundaries and interfaces named"
    - "data flow drawn"
    - "alternatives considered; trade-offs recorded"
    - "failure modes discussed"
  verification:
    - "check the architecture against the codebase reality"
  failure_modes:
    ivory_tower: "ground every layer in the actual code before finalizing"
    missing_alternatives: "document at least one rejected alternative"
  escalation:
    - "architecture conflicts with product constraints"
  handoff_in:
    - "requirements"
    - "codebase"
  handoff_out:
    - "architecture with boundaries, interfaces, ADRs"
  evaluation:
    - "correct boundary identification"
    - "trade-off quality"
    - "failure-mode coverage"
  observability:
    - "record ADRs in the project decision log"
  related_skills: [tech-decision, backend-engineering, api-design, database-design]
tools:
  - name: arch.explore
    description: "Search file contents under the project workspace to ground architecture decisions in the actual codebase."
    handler_ref: repo.search
    permission_key: repo.search
    risk_level: low
  - name: arch.tree
    description: "List the project workspace file tree to understand module boundaries."
    handler_ref: repo.tree
    permission_key: repo.tree
    risk_level: low
---

# Software Architecture

## Purpose
Produce staff-grade architecture: named boundaries and interfaces, drawn
data flow, explicit trade-offs, recorded decisions (ADRs), and failure-mode
analysis — grounded in the actual codebase.

## When to use / When NOT to use
- use: new systems, major refactors, any change with cross-module impact
- avoid: single-file changes (design inline); avoid architecture documents
  detached from the code

## Inputs & assumptions
- inputs: requirements, codebase
- assumptions: every assumption about scale/traffic labeled; architecture
  built on assumed scale inherits the label

## Workflow
1. **Understand** — read the requirements; explore the actual code
   (arch.explore/arch.tree) to find existing boundaries.
2. **Boundaries** — name the modules/components and their responsibilities.
3. **Interfaces** — the contracts between boundaries (APIs, events, types).
4. **Data flow** — how data moves through the system; where it is stored.
5. **Alternatives** — at least one rejected alternative per significant
   choice, with why.
6. **Trade-offs** — record what each choice gives up (consistency, latency,
   simplicity).
7. **Failure modes** — what breaks, how the system degrades, recovery.
8. **ADRs** — write the decisions as ADRs with status.

## Evidence requirements
- Architecture grounded in code reality where code exists.
- Trade-offs explicit; alternatives documented.

## Artifact contract
- `architecture`: boundaries, interfaces, data flow, alternatives,
  trade-offs, failure modes, ADRs.

## Quality gates (definition of done)
- [ ] Boundaries and interfaces named
- [ ] Data flow drawn
- [ ] ≥1 rejected alternative documented
- [ ] Trade-offs explicit
- [ ] Failure modes discussed with recovery

## Verification
- Check each boundary against the codebase: does reality match the plan?
- Walk a primary flow through the architecture end-to-end.

## Failure & recovery
| failure | recovery |
|---|---|
| ivory-tower design | ground layers in actual code before finalizing |
| missing alternatives | document the rejected alternative and why |
| boundary mismatch | adjust boundaries to code reality or plan the refactor |

## Escalation
- Architecture conflicting with product constraints — escalate with both.

## Handoff
- receives: requirements, codebase
- passes: architecture (boundaries, interfaces, data flow, ADRs) to
  backend/frontend leads

## Evaluation
The org evaluates this skill by correct boundary identification, trade-off
quality, and failure-mode coverage — not by diagram volume.

## Observability
- Record ADRs in the project decision log.

## References
- references/methodology.md — boundary identification and ADR format