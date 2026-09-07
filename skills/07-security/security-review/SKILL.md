---
id: security-review
name: Security Review
description: Structured security review — secrets, injection, authz, unsafe commands, dependency risk.
category: 07-security
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [filesystem.read]
risk_level: low
cost_level: low
tags: [security, review, audit]
compatible_agents: [security-reviewer, qa-director]
---

# Security Review

## Purpose
Find security issues before they ship: secrets, injection, authz gaps,
unsafe commands, excessive permissions, supply-chain risk.

## Checklist
1. **Secrets** — hardcoded keys/tokens/passwords in code, configs, logs,
   artifacts, or frontend bundles. Any found = critical.
2. **Injection** — SQL/command/template/path injection; unsanitized input into
   queries, shells, HTML, or eval.
3. **AuthN** — weak/absent authentication; session handling; token storage.
4. **AuthZ** — missing or broken authorization checks; IDOR (accessing other
   users' resources); privilege escalation.
5. **Unsafe commands** — shell with user input; `eval`; arbitrary file writes
   outside sandboxes; unsafe deserialization.
6. **Dependencies** — known-vulnerable versions; unmaintained packages;
   unvetted sources.
7. **Permissions** — overly broad grants (DB, filesystem, IAM); default-allow
   tool permissions; secrets accessible to low-trust components.
8. **Data handling** — PII logged; missing input/output validation; TLS gaps.

## Finding format
```
severity: critical | high | medium | low
location: <file/endpoint>
vulnerability: <what>
exploit: <how it could be abused>
fix: <concrete remediation>
```

## Rules
- Treat third-party skills/tools as untrusted until reviewed (source, license,
  dependencies, permission demands).
- Do not deploy with unresolved critical/high findings.