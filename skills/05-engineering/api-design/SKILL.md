---
id: api-design
name: API Design
description: "Contract-first API design — resources, verbs, errors, versioning, validation — with contract verification."
category: 05-engineering
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [repo.search, shell.write]
risk_level: medium
cost_level: low
dependencies: [architecture, backend-engineering]
compatible_agents: [backend-lead, software-architect]
tags: [api, design, rest, contract]
contract:
  prerequisites:
    - "the clients and use cases the API must serve"
  preferred_agents: [backend-lead, software-architect]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "API decisions traceable to client use cases"
  artifact_contract:
    - "API contract (endpoints, schemas, errors, versioning)"
  quality_gates:
    - "resources named by nouns; actions by methods or sub-resources"
    - "consistent error schema"
    - "versioning strategy stated"
    - "validation rules defined per field"
  verification:
    - "validate the contract against the implementation"
  failure_modes:
    rpc_style: "re-model around resources unless the action is genuinely verb-like"
    error_inconsistency: "define one error schema and use it everywhere"
  escalation:
    - "breaking contract changes with live consumers"
  handoff_in:
    - "use cases"
    - "clients"
  handoff_out:
    - "API contract for implementation"
  evaluation:
    - "resource modeling quality"
    - "error schema consistency"
  observability:
    - "record the contract as a project artifact"
  related_skills: [backend-engineering, architecture, api-evaluation]
---

# API Design

## Purpose
Design contract-first APIs: resources, verbs, consistent errors,
versioning, and per-field validation — traceable to the clients that will
consume them.

## When to use / When NOT to use
- use: new endpoints, new services, public APIs
- avoid: one-off internal calls (keep them simple); avoid designing in a
  vacuum without knowing the clients

## Inputs & assumptions
- inputs: use cases, clients
- assumptions: client types (web/mobile/third-party) and scale assumed
  unless stated

## Workflow
1. List the use cases and clients.
2. Model resources (nouns) and their operations; only add verb-like
  endpoints when the action is genuinely not a resource operation.
3. Define schemas with validation rules per field.
4. Define the error schema once: consistent shape, codes, and docs.
5. Choose versioning (URL/path, header, content) and state it.
6. Write the contract; validate it against implementation.

## Evidence requirements
- API decisions traceable to client use cases.

## Artifact contract
- `api-contract`: resources, endpoints, schemas, error schema, versioning,
  validation rules.

## Quality gates (definition of done)
- [ ] Resources noun-based; actions mapped deliberately
- [ ] One consistent error schema
- [ ] Versioning strategy stated
- [ ] Validation defined per field
- [ ] Contract validated against implementation

## Verification
- Validate the written contract against the running implementation.

## Failure & recovery
| failure | recovery |
|---|---|
| RPC-style modeling | re-model around resources |
| inconsistent errors | adopt the single error schema |
| breaking change | version it; escalate if live consumers exist |

## Escalation
- Breaking changes with live consumers — escalate the migration decision.

## Handoff
- receives: use cases, clients
- passes: API contract to backend implementation

## Evaluation
The org evaluates this skill by resource-modeling quality and error-schema
consistency.

## Observability
- Record the contract as a project artifact.

## References
- references/patterns.md — resource modeling and error schemas