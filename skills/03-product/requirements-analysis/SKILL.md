---
id: requirements-analysis
name: Requirements Analysis
description: "Analyze and challenge requirements — clarify ambiguity, surface missing decisions, make requirements testable."
category: 03-product
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
dependencies: [acceptance-criteria]
compatible_agents: [requirements-analyst, product-manager]
tags: [requirements, analysis, clarification]
contract:
  prerequisites:
    - "raw requirements or a vague request to analyze"
  preferred_agents: [requirements-analyst, product-manager]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "every assumption about the requirement labeled"
    - "ambiguities resolved or explicitly listed as open questions"
  artifact_contract:
    - "analyzed requirements (clarified, prioritized, with open questions)"
  quality_gates:
    - "no remaining ambiguity silently assumed"
    - "each requirement has acceptance criteria or a stated testability gap"
  verification:
    - "re-read each requirement: does it describe behavior or a vague wish?"
  failure_modes:
    ambiguity: "resolve by inference when low-risk, otherwise flag"
    missing_decision: "surface it; do not pick silently"
  escalation:
    - "requirements conflicting with each other or with evidence"
  handoff_in:
    - "raw requirements"
  handoff_out:
    - "analyzed requirements + open questions + acceptance criteria"
  evaluation:
    - "correct identification of ambiguities"
    - "challenge quality (caught bad requirements)"
  observability:
    - "record open questions and resolutions"
  related_skills: [requirements-analysis, acceptance-criteria, user-stories, prd-writing]
---

# Requirements Analysis

## Purpose
Turn raw requirements into clear, testable, prioritized requirements — and
challenge the bad ones instead of implementing them blindly.

## When to use / When NOT to use
- use: before implementation of any non-trivial request
- avoid: for trivial, unambiguous changes; avoid rubber-stamping requirements
  because they arrived with authority

## Inputs & assumptions
- inputs: raw requirements or vague request
- assumptions: every inference made during clarification is labeled; if an
  inference is wrong the downstream work inherits a mislabeled assumption

## Workflow
1. Restate each requirement in observable behavior terms.
2. Identify and resolve ambiguity: infer when low-risk and reversible;
   flag when high-risk or irreversible.
3. Find missing decisions (permissions, error behavior, scope boundaries)
   and surface them — never pick silently.
4. Challenge each requirement: what problem does it solve? For whom? If the
   answer is "because someone asked", mark it for challenge.
5. Prioritize the clarified set.
6. Attach acceptance criteria (see acceptance-criteria skill) or state the
   testability gap.
7. Produce the analysis with open questions listed separately.

## Evidence requirements
- Ambiguities resolved or explicitly listed as open questions.
- Requirements that rest on assumptions carry the assumption label.

## Artifact contract
- `analyzed-requirements`: clarified requirements (with rationale/priority),
  open questions, acceptance criteria or testability gap.

## Quality gates (definition of done)
- [ ] No ambiguity silently assumed
- [ ] Missing decisions surfaced as open questions
- [ ] Requirements testable (or gap stated)
- [ ] Challenge pass done — bad requirements caught, not inherited

## Verification
- Re-read each requirement: does it describe observable behavior?
- Check the open-questions list is empty of items that were actually
  assumed away.

## Failure & recovery
| failure | recovery |
|---|---|
| ambiguity | infer if low-risk, else flag as an open question |
| missing decision | surface it with the options and a recommendation |
| conflicting requirements | present the conflict, escalate |

## Escalation
- Requirements that conflict with each other or with research evidence.

## Handoff
- receives: raw requirements
- passes: analyzed requirements, open questions, acceptance criteria

## Evaluation
The org evaluates this skill by how many real ambiguities and bad
requirements it catches — a quiet yes is not the goal.

## Observability
- Record open questions and how each was resolved.

## References
- references/patterns.md — ambiguity archetypes and challenge techniques