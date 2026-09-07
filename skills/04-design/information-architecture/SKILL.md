---
id: information-architecture
name: Information Architecture
description: "IA — structure, navigation, labeling, findability — grounded in user tasks and evidence, verified by walkthrough."
category: 04-design
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [browser.open, browser.snapshot]
risk_level: low
cost_level: low
dependencies: [ux-design]
compatible_agents: [ux-designer, information-architect, ui-designer]
tags: [information-architecture, navigation, findability]
contract:
  prerequisites:
    - "user tasks the product must support"
    - "content/inventory to organize"
  preferred_agents: [ux-designer, information-architect]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "structure justified by task frequency and user language"
    - "labeling uses user vocabulary, not internal terms"
  artifact_contract:
    - "IA spec (structure, navigation, labels, task paths)"
  quality_gates:
    - "top tasks reachable in ≤2 clicks from entry"
    - "no orphan content"
    - "labels unambiguous"
  verification:
    - "walk each top task through the structure"
  failure_modes:
    mirror_org_chart: "re-structure around user tasks, not departments"
    label_ambiguity: "rename using user language"
  escalation:
    - "IA conflicts with technical constraints (escalate with both)"
  handoff_in:
    - "user tasks"
    - "content inventory"
  handoff_out:
    - "IA spec with navigation and labels"
  evaluation:
    - "task-path correctness"
    - "label quality (user vocabulary)"
  observability:
    - "record IA decisions and rationale"
  related_skills: [ux-design, ui-design, product-strategy]
---

# Information Architecture

## Purpose
Structure content and navigation around user tasks and vocabulary — so
findability is designed, not accidental.

## When to use / When NOT to use
- use: product design, site redesigns, new feature areas with new content
- avoid: single-screen utilities with no navigation; avoid structuring by
  the org chart by default

## Inputs & assumptions
- inputs: user tasks, content inventory
- assumptions: task priority is assumed unless researched — label it

## Workflow
1. List the top tasks with relative frequency (evidence where available).
2. Inventory the content/features to organize.
3. Group by task flows, not by internal department.
4. Design navigation and labels using user vocabulary.
5. Walk each top task through the structure; adjust until reachable.
6. Produce the IA spec.

## Evidence requirements
- Structure justified by task frequency and user language — never by
  internal naming habits.

## Artifact contract
- `ia-spec`: structure map, navigation, labels, task paths, orphan check.

## Quality gates (definition of done)
- [ ] Top tasks reachable in ≤2 clicks from entry
- [ ] No orphan content
- [ ] Labels unambiguous to the user
- [ ] Task walkthroughs completed

## Verification
- Walk each top task through the structure.
- Check every content item is reachable.

## Failure & recovery
| failure | recovery |
|---|---|
| org-chart mirror | re-structure around tasks |
| ambiguous labels | rename from user vocabulary |
| task not reachable | revise structure or flag the conflict |

## Escalation
- IA conflicting with technical constraints — escalate with both sides.

## Handoff
- receives: user tasks, content inventory
- passes: IA spec (structure, navigation, labels, task paths) to UX/UI

## Evaluation
The org evaluates this skill by task-path correctness and label quality.

## Observability
- Record IA decisions and their rationale in the project.

## References
- references/patterns.md — navigation patterns and labeling rules