---
id: research-planning
name: Research Planning
description: Plan research — questions, sources, method, budget — before gathering.
category: 10-research
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: low
cost_level: low
tags: [research, planning, method]
compatible_agents: [research-director, market-researcher, product-researcher]
---

# Research Planning

## Purpose
Define research before gathering: the decision it serves, the questions, the
evidence standard, and the budget. Prevents both vague wandering and
over-research.

## Plan template
```markdown
## Research brief
- Decision this informs: <what will change because of this?>
- Questions (3-5, answerable): ...
- Audience/sources: ...
- Evidence standard: <what counts as a finding — e.g. 2+ independent sources>
- Method: search → scrape → synthesize → report
- Budget: <time/tokens/cost cap>
- Output: <artifact and format>
- Deadline / checkpoints
```

## Rules
- Every question must be answerable and tied to the decision; drop others.
- Define "done" before starting — research that has no end state is a sink.
- Re-evaluate at checkpoints: stop early if the answer is already clear.