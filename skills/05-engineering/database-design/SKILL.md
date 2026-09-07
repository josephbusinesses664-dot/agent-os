---
id: database-design
name: Database Design
description: "Schema and query design — modeling, indexes, migrations, correctness — with migration safety verification."
category: 05-engineering
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [db.query, repo.search]
risk_level: medium
cost_level: low
dependencies: [architecture, backend-engineering]
compatible_agents: [database-engineer, backend-lead]
tags: [database, schema, sql, migrations]
contract:
  prerequisites:
    - "data model requirements"
    - "access to the database/schema"
  preferred_agents: [database-engineer, backend-lead]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "query plans/explains checked where performance matters"
    - "migration safety verified (expand-contract where live)"
  artifact_contract:
    - "schema design (model, indexes, migrations, verification notes)"
  quality_gates:
    - "normalization appropriate to the use case (not dogma)"
    - "indexes match the actual query patterns"
    - "migrations reversible or expand-contract"
    - "correctness verified against acceptance criteria"
  verification:
    - "run queries against the schema; check EXPLAIN for hot paths"
  failure_modes:
    migration_lock: "prefer expand-contract over destructive changes"
    missing_index: "add index matching the query pattern; re-check plan"
  escalation:
    - "destructive migrations on live data"
  handoff_in:
    - "requirements"
    - "schema access"
  handoff_out:
    - "schema design + migration plan + verification"
  evaluation:
    - "query correctness"
    - "migration safety"
  observability:
    - "record schema decisions and query checks"
  related_skills: [backend-engineering, data-modeling, architecture]
---

# Database Design

## Purpose
Design schemas and queries that are correct, indexed for the real query
patterns, and safe to migrate — verified by executing queries, not
asserting.

## When to use / When NOT to use
- use: schema creation/changes, hot-query tuning
- avoid: premature index-building on hypothetical queries; avoid destructive
  migrations on live data without approval

## Inputs & assumptions
- inputs: requirements, schema access
- assumptions: scale/volume assumed unless stated — schema trade-offs
  (normalization, denormalization) follow from it

## Workflow
1. Model the entities and relationships from requirements.
2. Choose normalization deliberately for the workload.
3. Map indexes to actual query patterns; check with EXPLAIN where hot.
4. Design the migration: expand-contract for live systems; reversible
   where possible.
5. Verify correctness: run representative queries against the schema.
6. Document decisions and verification notes.

## Evidence requirements
- Query plans checked for hot paths.
- Migration safety verified (not assumed).

## Artifact contract
- `schema-design`: model, indexes, migration plan, verification notes.

## Quality gates (definition of done)
- [ ] Normalization appropriate (not dogma)
- [ ] Indexes match real query patterns
- [ ] Migration reversible or expand-contract
- [ ] Representative queries executed correctly

## Verification
- Run representative queries; check EXPLAIN for hot paths.

## Failure & recovery
| failure | recovery |
|---|---|
| migration lock risk | expand-contract; escalate if destructive |
| missing index | add matching index; re-check the plan |
| correctness bug | reproduce, fix, re-verify |

## Escalation
- Destructive migrations on live data — approval gate before running.

## Handoff
- receives: requirements, schema access
- passes: schema design, migration plan, verification notes

## Evaluation
The org evaluates this skill by query correctness and migration safety.

## Observability
- Record schema decisions and query checks in the audit trail.

## References
- references/patterns.md — migration patterns and index selection