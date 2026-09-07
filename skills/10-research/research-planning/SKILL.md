---
id: research-planning
name: Research Planning
description: "Decision-driven research plans — questions, query expansion, source classes, stopping rules."
category: 10-research
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search]
risk_level: low
cost_level: low
dependencies: [evidence-synthesis]
compatible_agents: [research-director, market-researcher, technical-researcher]
tags: [research, planning, methodology]
contract:
  prerequisites:
    - "the decision the research must inform"
  preferred_agents: [research-director, market-researcher]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "plan states the decision, questions, sources, and stopping rule"
  artifact_contract:
    - "research plan (decision, questions, queries, sources, stopping rule)"
  quality_gates:
    - "decision stated"
    - "questions decomposed and ranked"
    - "source classes matched to question type"
    - "stopping rule defined (diminishing returns)"
  verification:
    - "check each question maps to a query set and source class"
  failure_modes:
    browse_research: "stop when information gain diminishes; the decision defines done"
    source_mismatch: "match source classes to the question type"
  escalation:
    - "questions whose answers are unknowable with available sources"
  handoff_in:
    - "decision"
  handoff_out:
    - "research plan for execution"
  evaluation:
    - "decision-to-question mapping"
    - "stopping rule quality"
  observability:
    - "record the plan"
  related_skills: [evidence-synthesis, market-research, technical-research]
---

# Research Planning

## Purpose
Turn a decision into a research plan: decomposed questions, query expansion,
matched source classes, and a stopping rule — so research ends when the
decision has enough evidence, not when time runs out.

## When to use / When NOT to use
- use: before any non-trivial research effort
- avoid: "browse the web and summarize" — that is not research planning;
  avoid plans without a decision behind them

## Inputs & assumptions
- inputs: decision
- assumptions: the decision is the contract — every question must serve it

## Workflow
1. Restate the decision this research informs.
2. Decompose into questions; rank by decision impact.
3. For each question, generate query expansions (multiple phrasings).
4. Match source classes to question type (primary docs for facts, community
   for pains, filings for financials).
5. Define the stopping rule: diminishing information gain per additional
   source.
6. Produce the plan.

## Evidence requirements
- Plan states decision, questions, queries, sources, stopping rule.

## Artifact contract
- `research-plan`: decision, questions (ranked), query sets, source
  classes, stopping rule.

## Quality gates (definition of done)
- [ ] Decision stated
- [ ] Questions decomposed and ranked
- [ ] Source classes matched to question type
- [ ] Stopping rule defined

## Verification
- Check each question maps to queries and sources.

## Failure & recovery
| failure | recovery |
|---|---|
| browse research | apply the stopping rule |
| source mismatch | re-match source classes |
| unknowable question | flag it; recommend an experiment or escalation |

## Escalation
- Questions whose answers are unknowable with available sources.

## Handoff
- receives: decision
- passes: research plan for execution

## Evaluation
The org evaluates this skill by decision-to-question mapping and stopping
rule quality.

## Observability
- Record the plan in the project.

## References
- references/patterns.md — query expansion and source-class mapping