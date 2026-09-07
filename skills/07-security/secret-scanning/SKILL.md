---
id: secret-scanning
name: Secret Scanning
description: Scan workspace files for exposed credentials (API keys, tokens, passwords) with an executable scanner tool and a validator that blocks results leaking secrets back into the agent output.
category: 07-security
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [repo.search]
risk_level: low
cost_level: low
tags: [security, secrets, scanning, credentials]
compatible_agents: [security-reviewer, devops-engineer]
model_settings:
  temperature: 0.2
  max_tokens: 2048
permissions:
  scan.secrets: allow
tools:
  - name: scan.secrets
    description: "Scan the workspace for exposed secrets (API keys, tokens, passwords). Returns file paths and the matched pattern category — never the secret value."
    permission_key: scan.secrets
    risk_level: low
    code: |
      # note: `re` is provided by the sandbox namespace; `import` is not
      # available to untrusted capability code.
      _PATTERNS = {
          "api_key": r"(?i)(api[_-]?key|token|secret)\s*[=:]\s*[\"']?[A-Za-z0-9_\-]{16,}",
          "aws_key": r"AKIA[0-9A-Z]{16}",
          "private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
          "password": r"(?i)(password|passwd|pwd)\s*[=:]\s*[\"']?[^\s\"']{6,}",
      }

      async def handler(ctx, args):
          pattern = args.get("pattern", "")
          max_files = min(int(args.get("max_files", 50)), 200)
          findings = []
          for path in ctx.workspace.rglob("*"):
              if path.is_dir() or path.name.startswith("."):
                  continue
              try:
                  text = path.read_text(errors="replace")
              except OSError:
                  continue
              for category, regex in _PATTERNS.items():
                  if pattern and pattern not in category:
                      continue
                  for match in re.finditer(regex, text):
                      findings.append({
                          "path": str(path.relative_to(ctx.workspace)),
                          "category": category,
                          "line": text[:match.start()].count("\n") + 1,
                          # redacted: never return the matched secret value
                          "length": match.end() - match.start(),
                      })
                      if len(findings) >= max_files * 2:
                          break
                  if len(findings) >= max_files * 2:
                      break
              if len(findings) >= max_files * 2:
                  break
          return {"ok": True, "findings": findings, "count": len(findings)}
validators:
  - |
    async def validate(ctx, result):
        # never allow a scanner result to carry the secret itself back
        if result.get("ok") and any("value" in f or "secret" in f for f in result.get("findings", [])):
            return {"ok": False, "error": "scanner returned secret values — redact before returning"}
        return {"ok": True}
tests:
  - |
    async def test(ctx):
        result = await ctx.services.tools.handler("scan.secrets")(ctx, {})
        return {"ok": result.get("ok"), "detail": f"scan ran, {result.get('count', 0)} findings"}
---

# Secret Scanning

## Purpose
Find exposed credentials in the project workspace *before* they reach review,
deployment or a public repo. The scanner is executable — it actually scans —
and its results are redacted by design.

## Method
1. **Run the scanner** — `scan.secrets` over the workspace.
2. **Triage** — real findings vs. test fixtures; check git history for
   previously-committed secrets (read-only `git.status`/`git.log`).
3. **Remediate** — rotate the credential, remove the hardcoded value, add it
   to `.gitignore`/`.env.example` instead.
4. **Verify** — re-run the scan; findings for that file must be gone.
5. **Record** — save a project memory entry with the outcome and provenance.

## Rules
- The scanner never returns secret values, only locations + pattern categories.
- Never commit credentials, mock or real — mock secrets still train bad habits.
- If a real secret was exposed, treat it as compromised: rotate, don't edit.