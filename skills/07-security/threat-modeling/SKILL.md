---
id: threat-modeling
name: Threat Modeling
description: "Structured threat modeling — assets, trust boundaries, threats, mitigations — with verified coverage."
category: 07-security
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [repo.search]
risk_level: high
cost_level: low
dependencies: [security-review]
compatible_agents: [security-reviewer, software-architect]
tags: [security, threat-model]
contract:
  prerequisites:
    - "the system design or codebase"
  preferred_agents: [security-reviewer]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: medium
  expected_latency: hours
  evidence_requirements:
    - "threats tied to concrete assets and trust boundaries"
  artifact_contract:
    - "threat model (assets, boundaries, threats, mitigations)"
  quality_gates:
    - "assets enumerated"
    - "trust boundaries drawn"
    - "STRIDE applied per boundary"
    - "mitigations mapped to threats"
  verification:
    - "check each mitigation exists in the code"
  failure_modes:
    generic_threats: "tie every threat to this system's assets and boundaries"
    unmapped_mitigation: "every threat needs a mitigation or an accepted risk"
  escalation:
    - "unmitigable critical threats"
  handoff_in:
    - "system design or codebase"
  handoff_out:
    - "threat model with mitigations for security review"
  evaluation:
    - "threat specificity"
    - "mitigation coverage"
  observability:
    - "record threats and mitigation status"
  related_skills: [security-review, architecture, secret-scanning]
---

# Threat Modeling

## Purpose
Model threats against this system's actual assets and trust boundaries —
applying STRIDE per boundary and mapping every threat to a mitigation or an
accepted risk.

## When to use / When NOT to use
- use: new systems, major features touching trust boundaries
- avoid: generic threat lists pasted onto any system; avoid threat models
  with no mitigation mapping

## Inputs & assumptions
- inputs: system design or codebase
- assumptions: the deployment context (who can reach what) is assumed
  unless stated — record it

## Workflow
1. Enumerate assets (data, credentials, capabilities, money).
2. Draw trust boundaries (external users, services, admin, agents/tools).
3. Apply STRIDE per boundary: Spoofing, Tampering, Repudiation, Info
   disclosure, DoS, Elevation.
4. For each threat: asset, boundary, scenario, impact, likelihood.
5. Map mitigations; verify each exists in the code where feasible.
6. List accepted risks explicitly.

## Evidence requirements
- Threats tied to concrete assets and boundaries of THIS system.

## Artifact contract
- `threat-model`: assets, boundaries, STRIDE threats (scenario, impact),
  mitigations (verified/unverified), accepted risks.

## Quality gates (definition of done)
- [ ] Assets enumerated
- [ ] Trust boundaries drawn
- [ ] STRIDE applied per boundary
- [ ] Every threat has a mitigation or accepted-risk note
- [ ] Mitigations verified where feasible

## Verification
- Check each mitigation exists in the code.

## Failure & recovery
| failure | recovery |
|---|---|
| generic threats | tie to this system's assets/boundaries |
| unmapped mitigation | assign one or mark accepted risk |
| missed boundary | re-draw with the real deployment context |

## Escalation
- Unmitigable critical threats — escalate immediately.

## Handoff
- receives: system design or codebase
- passes: threat model with mitigations to security review

## Evaluation
The org evaluates this skill by threat specificity and mitigation coverage.

## Observability
- Record threats and mitigation status in the audit trail.

## References
- references/checklist.md — STRIDE walkthrough per boundary type