---
id: data-modeling
name: Data Modeling
description: Domain modeling — entities, relationships, invariants, event data.
category: 14-data
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [data, modeling, domain]
compatible_agents: [database-engineer, software-architect]
---

# Data Modeling

## Purpose
Model the domain so the data structure expresses the business rules and
survives change.

## Method
1. **Entities & relationships** — from the domain language: nouns and their
   relations (1:N, M:N, optional/required).
2. **Invariants** — the rules that must always hold (a task can't be completed
   before it's started); express as constraints or code — and test them.
3. **Identities** — stable primary keys; natural vs. surrogate with rationale.
4. **State machines** — entities with status (task pending → running → done)
   modeled explicitly with legal transitions.
5. **History** — when do you need auditability? (decisions, money, permissions)
   → append-only tables/events.
6. **Change** — schemas evolve: versioned migrations, additive changes by
   default, no silent data reinterpretation.

## Rules
- Model behavior, not just storage: invariants belong in the model.
- Ambiguity in the data model = bugs in every consumer. Resolve it in the model.