---
id: code-review
name: Code Review
description: "Structured code review — correctness, architecture, security, performance, testing — with severity-ranked findings."
category: 06-testing
version: 1.1.0
source: agent-os core library (Addy Osmani review methodology)
license: MIT
capability_type: skill
required_tools: [repo.search, shell.write]
risk_level: low
cost_level: low
dependencies: [code-quality, security-review]
compatible_agents: [code-reviewer, qa-director]
tags: [review, code-quality]
contract:
  prerequisites:
    - "a diff or change to review"
    - "the requirements it implements"
  preferred_agents: [code-reviewer]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "each finding tied to a file/location and a concrete problem"
  artifact_contract:
    - "code review (severity-ranked findings with fixes)"
  quality_gates:
    - "dimensions covered: correctness, readability, architecture, security, performance, testing"
    - "findings machine-actionable (file, location, fix)"
  verification:
    - "run the tests/typecheck to check review claims"
  failure_modes:
    nit_flood: "rank by severity; skip trivial nits"
    unverified_claim: "run the code before asserting a bug"
  escalation:
    - "security-critical findings"
  handoff_in:
    - "diff"
    - "requirements"
  handoff_out:
    - "review with findings and approval recommendation"
  evaluation:
    - "finding precision (few false positives)"
    - "real issues caught"
  observability:
    - "record the review verdict and findings"
  related_skills: [implementation-review, code-quality, security-review]
---

# Code Review

## Purpose
Review changes structurally — correctness, readability, architecture,
security, performance, testing — producing severity-ranked, actionable
findings.

## When to use / When NOT to use
- use: before merge of any non-trivial change
- avoid: reviewing without the requirements (judge against intent);
  avoid nit-flooding instead of finding real issues

## Inputs & assumptions
- inputs: diff, requirements
- assumptions: stated requirements are the review contract

## Workflow
1. Read the requirements; read the diff in context.
2. Check each dimension: correctness (does it work, edge cases), readability,
   architecture (fits the system), security (authz, injection, secrets),
   performance (hot paths), testing (are behaviors covered).
3. For each finding: severity, file, location, problem, reason,
   recommended fix.
4. Verify load-bearing claims by running tests/typecheck where feasible.
5. Produce the review with an approval recommendation.

## Evidence requirements
- Findings are machine-actionable: file, location, problem, fix.
- Unverified claims are labeled as questions, not bugs.

## Artifact contract
- `code-review`: findings (severity, file, location, problem, reason,
  fix), verdict, approval recommendation.

## Quality gates (definition of done)
- [ ] All six dimensions covered
- [ ] Findings severity-ranked
- [ ] Load-bearing claims verified by execution
- [ ] Verdict matches the findings

## Verification
- Run tests/typecheck to confirm suspected bugs.

## Failure & recovery
| failure | recovery |
|---|---|
| nit flood | rank by severity; drop trivia |
| unverified bug claim | run it before asserting |
| unclear finding | add the concrete location and fix |

## Escalation
- Security-critical findings — escalate immediately with the evidence.

## Handoff
- receives: diff, requirements
- passes: review with findings and approval recommendation

## Evaluation
The org evaluates this skill by finding precision and real-issue
catch rate — a review full of style nits and no real bugs fails.

## Observability
- Record the review verdict and findings in the audit trail.

## References
- references/checklist.md — review walkthrough by dimension