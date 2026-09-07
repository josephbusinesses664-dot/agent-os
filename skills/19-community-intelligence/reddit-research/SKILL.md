---
id: reddit-research
name: Reddit Research
description: Research subreddits systematically — discovery, extraction, analysis, ethics.
category: 19-community-intelligence
version: 1.0.0
source: agent-os core library (Reddit community research methodology)
license: MIT
capability_type: skill
required_tools: [web.search, api.call]
risk_level: low
cost_level: low
tags: [reddit, research, communities]
compatible_agents: [community-researcher, market-researcher]
---

# Reddit Research

## Purpose
Gather community evidence from Reddit: what users struggle with, ask for, and
buy — systematically and respectfully.

## Process
1. **Find the subreddits** — search for the topic/niche; note size and
   activity (posts/day); include adjacent communities (competitors, jobs,
   support).
2. **Harvest** — top posts (week/month/year) + search results for the
   question (pain, alternatives, tool, recommendation).
3. **Extract** — for each relevant thread: the ask/complaint, verbatim quotes,
   thread engagement (upvotes/comments as interest signal), date.
4. **Analyze** — cluster themes, count recurrences, weight by specificity
   (detailed workflows > vague complaints).
5. **Report** — themes with quotes+links, frequency table, sentiment, and
   what this implies for the product.

## Ethics & rules
- Public data only; no private DMs; no brigading; no astroturfing.
- Respect subreddit rules; read-only participation.
- Small sample: label it as such; don't extrapolate from 3 threads.
- Never quote a user by username in marketing material without care — quote
  the sentiment, link the thread.