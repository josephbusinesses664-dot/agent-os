---
id: outreach-drafting
name: Outreach Drafting
description: "Personalized outreach from prospect evidence — relevance, proof, one ask — approval-gated before sending."
category: 09-sales
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search]
risk_level: high
cost_level: low
dependencies: [prospect-analysis]
compatible_agents: [outreach-specialist, sales-analyst]
tags: [outreach, sales, messaging]
contract:
  prerequisites:
    - "prospect analysis with evidence"
    - "approval before any sending"
  preferred_agents: [outreach-specialist]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "personalization grounded in the prospect analysis"
    - "claims about the prospect true and verified"
  artifact_contract:
    - "outreach message (personalization, proof, ask) + approval status"
  quality_gates:
    - "message references evidence specific to the prospect"
    - "one clear ask"
    - "no fabricated prospect facts"
    - "approval gate: sending external messages requires human approval"
  verification:
    - "re-check every prospect claim against the analysis"
  failure_modes:
    template_flood: "personalize from evidence or do not send"
    fabricated_claim: "remove; verify every claim"
  escalation:
    - "outreach to regulated/high-visibility contacts"
  handoff_in:
    - "prospect analysis"
  handoff_out:
    - "outreach message with approval request"
  evaluation:
    - "personalization quality"
    - "claim accuracy"
  observability:
    - "record the message and approval status"
  related_skills: [prospect-analysis, copywriting, sales-strategy]
---

# Outreach Drafting

## Purpose
Draft personalized outreach from prospect evidence: specific relevance,
proof, one clear ask — and require human approval before any sending.

## When to use / When NOT to use
- use: any external outreach
- avoid: template floods; avoid any sending without approval — this is a
  high-risk, approval-gated action

## Inputs & assumptions
- inputs: prospect analysis
- assumptions: claims about the prospect come from the analysis — verify
  before use

## Workflow
1. Read the prospect analysis; pick the strongest evidence-backed pain and
   trigger.
2. Draft: opening referencing the specific evidence → relevance → proof →
   one ask.
3. Verify every prospect claim against the analysis; remove anything not
   evidenced.
4. Short, skimmable, one CTA.
5. Submit for human approval (sending external messages is gated).

## Evidence requirements
- Personalization grounded in evidence; zero fabricated prospect facts.

## Artifact contract
- `outreach-message`: message, evidence references, ask, approval status.

## Quality gates (definition of done)
- [ ] Personalization evidence-specific
- [ ] One clear ask
- [ ] No fabricated claims
- [ ] Approval obtained before sending

## Verification
- Check every prospect claim against the analysis.

## Failure & recovery
| failure | recovery |
|---|---|
| template flood | personalize or do not send |
| fabricated claim | remove and verify |
| approval pending | do not send; wait for decision |

## Escalation
- Outreach to regulated/high-visibility contacts — escalate for review.

## Handoff
- receives: prospect analysis
- passes: outreach message with an approval request

## Evaluation
The org evaluates this skill by personalization quality and claim
accuracy — and by never sending without approval.

## Observability
- Record the message and approval status in the audit trail.

## References
- references/patterns.md — personalization and ask patterns