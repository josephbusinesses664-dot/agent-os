---
id: release-management
name: Release Management
description: Plan and execute releases — versions, changelogs, gates, coordination.
category: 16-deployment
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: medium
cost_level: low
tags: [release, versioning, changelog]
compatible_agents: [deployment-agent, operations-director]
---

# Release Management

## Purpose
Ship releases that stakeholders can trust: known contents, tested, recorded,
and reversible.

## Process
1. **Contents** — merge the intended changes; freeze scope.
2. **Version** — semantic versioning: MAJOR (breaking), MINOR (feature),
   PATCH (fix). Pre-release tags for staging.
3. **Changelog** — user-facing changes, not commit dumps: Added/Changed/Fixed/
   Removed with issue links.
4. **Gates** — tests, security, review pass (real evidence) before release.
5. **Approval** — production release approved by a human (approval system).
6. **Deploy & verify** — per deployment skill; monitor post-release metrics.
7. **Record** — release notes + result in the event/audit trail.

## Rules
- If you can't state what's in a release in one paragraph, it's not ready.
- Hotfixes still pass gates (abbreviated but never skipped).
- Every release is rollback-able; rehearse the rollback before production.