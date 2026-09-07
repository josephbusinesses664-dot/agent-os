---
id: secret-scanning
name: Secret Scanning
description: "Scan workspace files for exposed credentials (API keys, tokens, passwords) with an executable scanner tool and a validator that blocks results leaking secrets back into the agent output."
category: 07-security
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [repo.search]
risk_level: medium
cost_level: low
dependencies: [security-review]
compatible_agents: [security-reviewer, devops-engineer]
tags: [security, secrets, scanning, credentials]
model_settings:
  temperature: 0.2
  max_tokens: 2048
permissions:
  scan.secrets: allow
contract:
  prerequisites:
    - "a workspace path to scan"
  preferred_agents: [security-reviewer, devops-engineer]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "findings list file paths and pattern categories — never the secret values"
    - "false-positive review done before reporting"
  artifact_contract:
    - "secret scan report (findings, severity, remediation)"
  quality_gates:
    - "no secret values echoed in output"
    - "findings deduplicated and severity-ranked"
    - "remediation steps per finding"
  verification:
    - "re-scan after remediation to confirm findings cleared"
  failure_modes:
    false_positive: "review pattern matches against real context before reporting"
    leak_in_output: "the validator blocks secret values from agent output"
  escalation:
    - "live credentials found (rotate immediately)"
  handoff_in:
    - "workspace path"
  handoff_out:
    - "secret scan report with remediation"
  evaluation:
    - "correct identification of real secrets (few false positives)"
    - "no secret leakage in output"
  observability:
    - "record findings counts and remediation status"
  related_skills: [security-review, threat-modeling, deployment]
tools:
  - name: scan.secrets
    description: "Scan the workspace for exposed secrets (API keys, tokens, passwords). Returns file paths and the matched pattern category — never the secret value."
    permission_key: scan.secrets
    risk_level: medium
    code: |
      # sandbox namespace provides: re, Path, json, math, asyncio, datetime
      # (no `import`, `__import__` or `getattr` for untrusted capability code)
      _PATTERNS = {
          "api_key": r"(?i)(api[_-]?key|token|secret)\s*[=:]\s*[\"']?[A-Za-z0-9_\-]{16,}",
          "aws_key": r"AKIA[0-9A-Z]{16}",
          "private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
          "connection_string": r"(?i)(postgres|mysql|redis|mongodb)[a-z+]*://[^\s\"']+",
          "github_token": r"gh[pousr]_[A-Za-z0-9]{20,}",
      }
      async def handler(ctx, args):
          root = Path(str(args.get("path") or "."))
          if not args.get("path"):
              try:
                  root = Path(str(ctx.workspace))
              except Exception:
                  root = Path(".")
          findings = []
          for fp in sorted(root.rglob("*")):
              if not fp.is_file():
                  continue
              if ".git" in fp.relative_to(root).parts:  # defensive
                  continue
              try:
                  data = fp.read_text(errors="ignore")
              except Exception:
                  continue
              for category, pattern in _PATTERNS.items():
                  if re.search(pattern, data):
                      findings.append({"file": str(fp), "category": category})
                      break
          return {"ok": True, "count": len(findings), "findings": findings}
validators:
  - |
      async def validate(ctx, result):
          # Block any result that would leak a secret value back into the
          # agent output: findings may carry ONLY file paths and categories.
          # (`re` comes from the sandbox namespace — no import statements.)
          _ALLOWED_KEYS = {"file", "path", "category"}
          findings = result.get("findings") or []
          for f in findings:
              if not isinstance(f, dict):
                  return {"ok": False, "error": "refusing to emit secret values"}
              if set(f.keys()) - _ALLOWED_KEYS:
                  return {"ok": False, "error": "refusing to emit secret values"}
          return {"ok": True}
---

# Secret Scanning

## Purpose
Scan the workspace for exposed credentials and report them with remediation
— without ever echoing the secret values themselves.

## When to use / When NOT to use
- use: before commit/push, before deployment, on repository audits
- avoid: scanning files you are not authorized to read; avoid reporting
  matches without checking they are real secrets (false positives erode
  trust)

## Inputs & assumptions
- inputs: workspace path
- assumptions: the scan is read-only; findings are paths + pattern
  categories, never values

## Workflow
1. Run the executable scanner (scan.secrets) over the workspace.
2. Review findings for false positives (test fixtures, example code).
3. Deduplicate and rank by severity: live credentials > test keys >
   low-confidence matches.
4. Write remediation per finding (rotate, revoke, move to secret store).
5. Report; re-scan after remediation to confirm cleared.

## Evidence requirements
- Findings carry file path + pattern category + confidence.
- No secret values in any output (the validator enforces this).

## Artifact contract
- `secret-scan-report`: findings (file, category, severity, confidence),
  remediation steps, re-scan status.

## Quality gates (definition of done)
- [ ] No secret values in output (validator-verified)
- [ ] False positives reviewed
- [ ] Findings deduplicated and severity-ranked
- [ ] Remediation per finding

## Verification
- Re-scan after remediation; confirm cleared.

## Failure & recovery
| failure | recovery |
|---|---|
| false positive | check context before reporting |
| leak attempt | validator blocks it; confirm output clean |
| live credential | escalate rotation immediately |

## Escalation
- Live credentials — escalate immediately (rotation is time-sensitive).

## Handoff
- receives: workspace path
- passes: secret scan report with remediation to engineering/DevOps

## Evaluation
The org evaluates this skill by correct identification of real secrets
(low false-positive rate) and zero secret leakage in output.

## Observability
- Record finding counts and remediation status in the audit trail.

## References
- references/patterns.md — pattern tuning and false-positive review