---
id: technical-research
name: Technical Research
description: Documentation research, tool evaluation, technical deep dives with sources.
category: 10-research
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
tags: [technical, research, docs]
compatible_agents: [technical-researcher, ai-engineer]
---

# Technical Research

## Purpose
Answer technical questions with authoritative, current sources — official
docs first, community corroboration second.

## Process
1. **Frame** — the decision the research informs; what "answered" means.
2. **Primary sources** — official docs, changelogs, RFCs, source code.
3. **Corroboration** — real-world usage (issues, blog posts, benchmarks) —
   but official docs win disagreements.
4. **Current version reality** — check dates; APIs change; examples rot.
5. **Hands-on where cheap** — a minimal repro/benchmark beats reading.
6. **Synthesize** — answer + evidence + confidence + open questions.

## Output
```markdown
## Question
## Answer (with confidence)
## Evidence
- <claim> — <source>, <date>
## Alternatives considered
## Open questions
```

## Rules
- Cite sources with dates; distinguish docs from opinion.
- If the answer changed across versions, say so.
- Never invent API signatures — verify against actual docs.