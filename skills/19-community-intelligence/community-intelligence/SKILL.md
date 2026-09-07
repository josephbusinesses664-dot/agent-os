---
id: community-intelligence
name: Community Intelligence
description: Determine what communities actually want — pain points, requests, buying signals, language.
category: 19-community-intelligence
version: 1.0.0
source: agent-os core library (Reddit/community research methodology)
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape, api.call]
risk_level: low
cost_level: low
tags: [community, intelligence, signals]
compatible_agents: [community-researcher, market-researcher, product-researcher]
---

# Community Intelligence

## Purpose
Extract what users and communities actually want: recurring pain, feature
requests, buying intent, unmet demand, and their exact language. The system
supports multiple sources (Reddit, HN, forums, reviews) — no single provider
is load-bearing.

## Categories to extract
- **Pain points** — recurring problems with existing solutions.
- **Recurring complaints** — the same complaint across users = signal.
- **Feature requests** — explicit asks ("I wish X did Y").
- **Product requests** — "is there a tool that…" = unmet demand.
- **Competitor complaints** — users' issues with competitors = your wedge.
- **Buying-intent signals** — "recommend a tool for…", budget mentions.
- **Unmet demand** — questions no tool answers well.
- **Customer language** — verbatim phrases for the problem and the job.
- **Sentiment** — tone and trend around a topic/competitor.
- **Opportunity signals** — combinations of the above.

## Workflow
1. **Define the question** — what decision this informs.
2. **Gather** — search + source APIs for relevant threads/discussions.
3. **Extract** — pull the categories above with quotes and links.
4. **Cluster & count** — group into themes; count occurrences (frequency ≠
   truth, but frequency + specificity = signal).
5. **Synthesize** — top themes with evidence, confidence, and the exact
   customer language to reuse.

## Rules
- Quotes are verbatim with source links; never paraphrase into invention.
- Frequency is data, but sample size and source quality are reported too.
- Multiple sources corroborate; one loud post is an anecdote.