---
id: database-design
name: Database Design
description: Schema design, migrations, indexing, and query optimization.
category: 05-engineering
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [database, schema, sql, postgres]
compatible_agents: [database-engineer, software-architect, backend-lead]
---

# Database Design

## Schema discipline
1. **Model the domain** — tables represent entities/relationships; names
   plural, consistent; every table has a primary key.
2. **Normalize by default** — 3NF unless a real query pattern justifies
   denormalization (then document the trade).
3. **Constraints** — NOT NULL, CHECK, FK with ON DELETE policy decided
   explicitly; unique indexes for identity.
4. **Types** — use native types (timestamptz, uuid, jsonb); avoid strings for
   booleans/dates; money as numeric(12,2) or integer cents.
5. **Timestamps** — created_at/updated_at everywhere; updated_at maintained by
   trigger or app (choose one).

## Migrations
- Versioned, ordered, idempotent where possible; forward-only with rollback
   scripts for destructive changes.
- Never edit applied migrations — add new ones.

## Indexing & performance
- Index on FK and hot filter columns; composite indexes match filter order;
  partial indexes for sparse conditions; avoid over-indexing writes.
- `EXPLAIN` hot queries; avoid SELECT *; use LIMIT; watch for N+1.
- Vacuum/autovacuum tuned; monitoring for slow queries.

## Rules
- Constraints are cheaper than bugs: enforce integrity in the DB, not just the app.
- Document the reasoning for every non-obvious schema decision.