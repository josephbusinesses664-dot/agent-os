---
id: deployment
name: Deployment
description: Deployment discipline — repeatable, reversible, verified, gated by approval for production.
category: 16-deployment
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [shell, deploy]
risk_level: high
cost_level: low
tags: [deployment, release, production]
compatible_agents: [deployment-agent, devops-engineer]
---

# Deployment

## Purpose
Ship changes with repeatable, reversible, verified process — and explicit
human approval before production.

## Process
1. **Build** — artifact built from the exact commit; checksummed/versioned.
2. **Test gate** — tests + security scan pass on the artifact (real runs).
3. **Approval** — production deployments require human approval via the
   approval system (HIGH risk).
4. **Deploy** — incremental (canary/rolling) where possible; blue/green for
   big changes.
5. **Verify** — post-deploy health checks + smoke tests; the deployment is not
   done until verified.
6. **Rollback** — a one-command rollback path exists and is rehearsed.
7. **Record** — deployment result in the event log (started/completed/failed).

## Rules
- Never deploy untested or unreviewed code. No exceptions for "quick fixes".
- If verification fails, roll back first, debug second.
- Every deployment is logged with what, when, who, result — auditability is
  not optional for production.