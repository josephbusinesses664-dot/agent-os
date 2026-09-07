---
id: threat-modeling
name: Threat Modeling
description: Lightweight threat modeling for features and systems — assets, attackers, attack surface.
category: 07-security
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [threat, security, risk]
compatible_agents: [security-reviewer, software-architect]
---

# Threat Modeling

## Purpose
Identify what could go wrong before building, so security is designed in.

## Method (STRIDE-lite)
For each trust boundary, ask:
- **S**poofing — can an attacker pretend to be someone/something?
- **T**ampering — can data be modified in transit or at rest?
- **R**epudiation — can actions be denied without a trace? (audit logs)
- **I**nformation disclosure — what leaks to whom?
- **D**enial of service — can the feature be overwhelmed?
- **E**levation of privilege — can a low-priv user gain more?

## Process
1. Draw the data flow (actors, components, boundaries, data).
2. List assets and their sensitivity.
3. Enumerate threats per boundary via STRIDE.
4. Rank: likelihood × impact; address high first.
5. Define mitigations and verification (tests/checks).
6. Record residual risk explicitly.

## Rules
- Threat model at design time for anything touching auth, money, PII, or
  destructive operations.
- A threat with no mitigation and no accepted-risk decision is an open issue.