---
id: security-review
name: Security Review
description: "Rigorous security review — attack surface, threat model, mitigations verified — with evidence per finding."
category: 07-security
version: 1.1.0
source: agent-os core library (Addy Osmani / Superpowers security methodology)
license: MIT
capability_type: skill
required_tools: [repo.search, shell.write, web.search]
risk_level: high
cost_level: low
dependencies: [threat-modeling, secret-scanning]
compatible_agents: [security-reviewer, qa-director]
tags: [security, review, audit]
contract:
  prerequisites:
    - "the system/change under review"
    - "permission to inspect the code"
  preferred_agents: [security-reviewer]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: medium
  expected_latency: hours
  evidence_requirements:
    - "each finding: threat → exploit path → impact → mitigation → verification"
  artifact_contract:
    - "security review (findings with exploit paths and verified mitigations)"
  quality_gates:
    - "attack surface examined (auth, injection, secrets, data exposure, SSRF, etc.)"
    - "every finding has exploit path and impact"
    - "mitigations verified where feasible"
    - "false positives minimized"
  verification:
    - "attempt the exploit path in the code/tests; confirm the mitigation blocks it"
  failure_modes:
    false_positive: "verify exploitability before reporting"
    missed_high: "cover the full attack surface, not just the obvious"
  escalation:
    - "critical exploitable findings — immediately"
  handoff_in:
    - "system/change"
  handoff_out:
    - "security review with findings and verified mitigations"
  evaluation:
    - "correct vulnerability identification"
    - "low false-positive rate"
    - "valid mitigations"
  observability:
    - "record findings with severity and verification status"
  related_skills: [threat-modeling, secret-scanning, code-review]
---

# Security Review

## Purpose
Review systems for security rigorously: examine the attack surface, build
threat → exploit path → impact → mitigation → verification for every
finding, and verify mitigations where feasible.

## When to use / When NOT to use
- use: before release, on any change touching auth/data/network, before
  merging security-sensitive work
- avoid: reporting without verifying exploitability; avoid skipping the
  attack surface sweep

## Attack surface checklist
- authentication and session handling
- authorization (every endpoint/action checked)
- least privilege (over-granted permissions)
- secrets management
- injection (SQL, command, template)
- XSS/CSRF/SSRF
- path traversal
- data exposure and logging leakage
- dependency risk
- tenant isolation
- unsafe tools/MCP/browser permissions/agent delegation
- prompt injection and untrusted content (can untrusted content manipulate
  the agent into invoking a privileged tool?)

## Workflow
1. Map the attack surface from the checklist to the actual code.
2. For each candidate issue: threat → exploit path → impact.
3. Verify exploitability before reporting (false positives are findings
  too — of sloppy review).
4. Propose mitigations; verify where feasible.
5. Rank by severity; write the report.

## Evidence requirements
- Every finding has a concrete exploit path and impact.
- Mitigations verified (test, code check) or marked unverified.

## Artifact contract
- `security-review`: attack-surface map, findings (threat, exploit path,
  impact, mitigation, verification), severity ranking.

## Quality gates (definition of done)
- [ ] Attack surface examined per checklist
- [ ] Every finding has exploit path + impact
- [ ] Mitigations verified where feasible
- [ ] False positives minimized

## Verification
- Attempt the exploit path in code/tests; confirm the mitigation blocks it.

## Failure & recovery
| failure | recovery |
|---|---|
| false positive | verify before reporting |
| missed surface | sweep the full checklist |
| unverified mitigation | mark it unverified; recommend a test |

## Escalation
- Critical exploitable findings — escalate immediately.

## Handoff
- receives: system/change
- passes: security review with findings and verified mitigations

## Evaluation
The org evaluates this skill by correct vulnerability identification, low
false-positive rate, and valid mitigations.

## Observability
- Record findings with severity and verification status in the audit trail.

## References
- references/checklist.md — the full attack-surface walkthrough