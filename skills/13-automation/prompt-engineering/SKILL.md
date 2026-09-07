---
id: prompt-engineering
name: Prompt Engineering
description: Write effective prompts for agent systems — role, context, constraints, output contracts.
category: 13-automation
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [prompts, llm, agents]
compatible_agents: [ai-engineer]
---

# Prompt Engineering

## Structure
A production prompt = role + authority + task + context + constraints +
output contract + failure behavior.

1. **Role** — who the model is, what its job is, what it must never do.
2. **Authority** — what it can do (tools/permissions), what requires escalation.
3. **Task** — the specific deliverable; one task per prompt.
4. **Context** — only what's needed (progressive disclosure); no history dumps.
5. **Constraints** — format, length, style, honesty rules ("never claim
   actions you didn't perform").
6. **Output contract** — exact structure (JSON schema, headings) that can be
   parsed and validated.
7. **Failure behavior** — what to do when tools fail, when uncertain, when
   blocked.

## Techniques
- Few-shot: 1-3 examples for hard formats (never for obvious ones).
- Chain-of-thought for reasoning tasks; require the reasoning in output when
  auditability matters.
- Enumerate edge cases explicitly instead of saying "handle edge cases".
- Ask for confidence and uncertainty on factual claims.

## Rules
- Prompts are versioned code: changes are reviewed and tested against evals.
- Test prompts on real inputs; a prompt that works on one example is a draft.