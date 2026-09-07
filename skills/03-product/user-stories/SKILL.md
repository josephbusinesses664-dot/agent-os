---
id: user-stories
name: User Stories
description: "User stories with value rationale, acceptance criteria, edge cases and failure behavior — ready for engineering."
category: 03-product
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
dependencies: [acceptance-criteria, requirements-analysis]
compatible_agents: [product-manager, requirements-analyst]
tags: [user-stories, agile, requirements]
contract:
  prerequisites:
    - "a requirement or feature to express as user stories"
    - "the user whose story this is"
  preferred_agents: [product-manager, requirements-analyst]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "story value grounded in user need, not feature habit"
  artifact_contract:
    - "user stories with acceptance criteria and edge cases"
  quality_gates:
    - "each story expresses value, not just behavior"
    - "acceptance criteria attached per story"
  verification:
    - "read the story from the user's perspective — does it deliver the job?"
  failure_modes:
    feature_phrasing: "rewrite as job-to-be-done, not feature spec"
    story_bloat: "split stories that bundle multiple user goals"
  escalation:
    - "stories whose value rationale contradicts research"
  handoff_in:
    - "requirement or feature"
    - "target user"
  handoff_out:
    - "user stories with acceptance criteria and edge cases"
  evaluation:
    - "value clarity per story"
    - "acceptance criteria coverage"
  observability:
    - "link stories to the requirement and task"
  related_skills: [acceptance-criteria, requirements-analysis, prd-writing]
---

# User Stories

## Purpose
Express requirements as user stories that carry value rationale, acceptance
criteria and edge cases — so engineering and QA can execute without
guesswork.

## When to use / When NOT to use
- use: translating requirements into implementable slices
- avoid: for system/technical work with no user actor (write technical
  requirements instead); avoid stories written from the feature's
  perspective

## Inputs & assumptions
- inputs: requirement/feature, target user
- assumptions: the user's job and context are assumed unless evidenced —
  label the assumption

## Workflow
1. Identify the user and their job (not the feature).
2. Write the story: "As a [user], I want [action] so that [value]."
3. Verify the value clause — if the value is tautological ("so I can use
   the feature"), the story is feature-phrased; rewrite.
4. Attach acceptance criteria (given/when/then) per story.
5. Add edge cases and failure behavior.
6. Split stories that bundle multiple user goals.
7. Review from the user's perspective.

## Evidence requirements
- Story value grounded in user need; the value clause must be meaningful.

## Artifact contract
- `user-stories`: story, value, acceptance criteria, edge cases, failure
  behavior, priority.

## Quality gates (definition of done)
- [ ] Each story expresses value, not just behavior
- [ ] Acceptance criteria attached per story
- [ ] Edge cases present for risky inputs
- [ ] No bundled multi-goal stories

## Verification
- Read from the user's perspective: does this deliver the job?
- Check the value clause would convince a skeptical stakeholder.

## Failure & recovery
| failure | recovery |
|---|---|
| feature phrasing | rewrite around the job-to-be-done |
| story bloat | split into single-goal stories |
| missing edge cases | add the risky-input cases before handoff |

## Escalation
- Stories whose value rationale contradicts research — escalate with the
  evidence.

## Handoff
- receives: requirement, target user
- passes: user stories with acceptance criteria and edge cases to
  engineering and QA

## Evaluation
The org evaluates this skill by value clarity per story and acceptance
criteria coverage.

## Observability
- Link stories to the requirement and task so QA verifies against the same
  set.

## References
- references/patterns.md — story splitting and value-clause checks