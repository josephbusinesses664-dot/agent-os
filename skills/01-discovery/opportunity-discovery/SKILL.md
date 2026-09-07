---
id: opportunity-discovery
name: Opportunity Discovery
description: Structured idea and opportunity discovery — trends, gaps, pain points, niches — with evidence.
category: 01-discovery
version: 1.0.0
source: agent-os core library (adapted from Superpowers discovery methodology)
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
required_models: [deepseek-pro]
risk_level: low
cost_level: low
tags: [discovery, opportunity, trends, niche]
compatible_agents: [executive, market-researcher, product-researcher]
---

# Opportunity Discovery

## Purpose
Find and rank opportunities (ideas, niches, product gaps) with **evidence**,
not vibes. Output is a structured opportunity brief.

## Workflow
1. **Frame** — write the goal as a question: "What underserved need exists for X?"
2. **Scan** — search for trends, complaints, requests, communities around the space.
3. **Extract signals** — pain points, feature requests, buying intent, recurring complaints.
4. **Cluster** — group signals into opportunity themes.
5. **Score** — for each theme score: demand evidence (0-5), competition (0-5, lower=better),
   willingness-to-pay signals (0-5), execution fit (0-5), market timing (0-5).
6. **Recommend** — top 3 opportunities with evidence links and open questions.

## Output format
```markdown
## Opportunity Brief
### Opportunity: <name>
- Evidence: <links/snippets>
- Demand score: x/5 (why)
- Competition: x/5 (who)
- Willingness to pay: x/5 (signals)
- Fit: x/5
- Timing: x/5
- Risk: <top risks>
- Open questions: <what we still don't know>
```

## Rules
- Never present a hypothesis as a finding. Label confidence: **observed / inferred / assumed**.
- Cite sources for every claim that matters.
- If evidence is thin, say so — do not pad with filler.