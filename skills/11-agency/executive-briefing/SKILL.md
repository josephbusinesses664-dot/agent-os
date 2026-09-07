---
id: executive-briefing
name: Executive Briefing
description: "Decision-grade briefings — situation, evidence, options, recommendation — with confidence labels."
category: 11-agency
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
dependencies: [evidence-synthesis]
compatible_agents: [chief-of-staff, executive]
tags: [briefing, executive, decisions]
contract:
  prerequisites:
    - "a decision and the evidence gathered"
  preferred_agents: [chief-of-staff]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "recommendation grounded in evidence with confidence"
  artifact_contract:
    - "executive briefing (situation, options, recommendation, risks)"
  quality_gates:
    - "decision stated at the top"
    - "options with trade-offs"
    - "recommendation with confidence"
    - "risks surfaced"
  verification:
    - "read as the decision-maker: can I decide from this alone?"
  failure_modes:
    burying_decision: "lead with the decision"
    false_certainty: "label confidence honestly"
  escalation:
    - "decisions needing human judgment beyond evidence"
  handoff_in:
    - "decision"
    - "evidence"
  handoff_out:
    - "executive briefing for the decision-maker"
  evaluation:
    - "decision clarity"
    - "confidence honesty"
  observability:
    - "record the briefing and decision"
  related_skills: [evidence-synthesis, status-reporting, business-strategy]
---

# Executive Briefing

## Purpose
Produce decision-grade briefings: the decision, the situation, options with
trade-offs, a recommendation with honest confidence, and risks — so the
decision-maker can decide from the briefing alone.

## When to use / When NOT to use
- use: decisions routed to leadership
- avoid: burying the decision in narrative; avoid false certainty

## Inputs & assumptions
- inputs: decision, evidence
- assumptions: confidence labels are the contract — never inflate

## Workflow
1. Lead with the decision to be made.
2. Situation in 3-5 lines.
3. Options with trade-offs (including "do nothing").
4. Recommendation with confidence and the evidence it rests on.
5. Risks and what would change the recommendation.
6. The ask: what the decision-maker must do.

## Evidence requirements
- Recommendation grounded in evidence; confidence labeled.

## Artifact contract
- `executive-briefing`: decision, situation, options, recommendation
  (confidence), risks, ask.

## Quality gates (definition of done)
- [ ] Decision at the top
- [ ] Options with trade-offs
- [ ] Recommendation with confidence
- [ ] Risks surfaced
- [ ] Decidable from the briefing alone

## Verification
- Read as the decision-maker: can I decide from this alone?

## Failure & recovery
| failure | recovery |
|---|---|
| buried decision | lead with it |
| false certainty | label confidence |
| missing option | add "do nothing" |

## Escalation
- Decisions needing human judgment beyond evidence — escalate with the
  briefing.

## Handoff
- receives: decision, evidence
- passes: executive briefing to the decision-maker

## Evaluation
The org evaluates this skill by decision clarity and confidence honesty.

## Observability
- Record the briefing and the resulting decision in the decision log.

## References
- references/patterns.md — briefing structures per decision type