---
id: ai-engineering
name: AI Engineering
description: "AI feature engineering — prompting, evals, guardrails, cost, observability — with real evaluation."
category: 05-engineering
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [repo.search, shell.write]
risk_level: medium
cost_level: medium
dependencies: [testing-strategy, evaluation]
compatible_agents: [ai-engineer, backend-lead]
tags: [ai, llm, prompting, evals]
contract:
  prerequisites:
    - "the feature behavior the LLM must deliver"
    - "a task/dataset to evaluate against"
  preferred_agents: [ai-engineer]
  preferred_models: []
  minimum_model_capability: t3
  expected_cost: medium
  expected_latency: hours
  evidence_requirements:
    - "evaluation results from a real eval run, not anecdote"
  artifact_contract:
    - "AI feature (prompt/system, eval set, results, cost notes)"
  quality_gates:
    - "eval set covers the core behaviors + edge cases"
    - "eval run executed with recorded pass rate"
    - "guardrails: prompt injection / unsafe output handled"
    - "cost per call estimated"
  verification:
    - "run the eval suite and record results"
  failure_modes:
    eval_gaming: "write evals that test behavior, not phrasing"
    injection: "treat external input as untrusted; add guardrails"
  escalation:
    - "LLM behavior that cannot be made reliable within budget"
  handoff_in:
    - "feature behavior"
    - "task/dataset"
  handoff_out:
    - "AI feature + eval results + cost notes"
  evaluation:
    - "eval pass rate (real runs)"
    - "guardrail coverage"
  observability:
    - "record eval results and cost in the audit trail"
  related_skills: [evaluation, prompt-engineering, model-selection, testing-strategy]
---

# AI Engineering

## Purpose
Ship AI features the way other features ship: defined behavior, guardrails,
a real eval set with recorded results, and cost awareness.

## When to use / When NOT to use
- use: any feature whose core is an LLM call
- avoid: shipping prompt changes without an eval; avoid hand-tuning on one
  example and calling it done

## Inputs & assumptions
- inputs: feature behavior, task/dataset
- assumptions: model choice and budget assumed unless routed deliberately

## Workflow
1. Define the behavior contract: inputs, outputs, failure behavior.
2. Build the eval set: core behaviors + edge cases + adversarial inputs.
3. Design the prompt/system around the contract.
4. Add guardrails: untrusted input handling, output validation, prompt
   injection awareness.
5. Run the eval; iterate until pass rate is acceptable.
6. Estimate cost per call and total; record.
7. Add observability: log inputs/outputs (redacted), latency, cost.

## Evidence requirements
- Evaluation results from an executed eval run with the pass rate recorded.

## Artifact contract
- `ai-feature`: prompt/system, eval set, eval results, guardrails, cost
  notes.

## Quality gates (definition of done)
- [ ] Eval set covers core behaviors + edges
- [ ] Eval run executed with recorded pass rate
- [ ] Guardrails in place (injection, unsafe output)
- [ ] Cost per call estimated

## Verification
- Run the eval suite; record the pass rate.

## Failure & recovery
| failure | recovery |
|---|---|
| eval gaming | test behavior, not phrasing |
| injection | treat external input as untrusted |
| unreliable behavior | strengthen prompt or route to stronger model |

## Escalation
- Behavior that cannot be made reliable within budget — escalate the
  model/cost trade.

## Handoff
- receives: feature behavior, task/dataset
- passes: AI feature, eval results, cost notes

## Evaluation
The org evaluates this skill by real eval pass rates and guardrail
coverage.

## Observability
- Record eval results and cost in the audit trail.

## References
- references/patterns.md — eval design and guardrail patterns