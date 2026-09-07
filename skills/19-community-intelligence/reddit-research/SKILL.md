---
id: reddit-research
name: Reddit Research
description: "Research subreddits systematically — signal classification, buying-intent separation, evidence lineage, ethics."
category: 19-community-intelligence
version: 1.1.0
source: agent-os core library (Reddit community research methodology)
license: MIT
capability_type: skill
required_tools: [web.search, api.call]
risk_level: low
cost_level: low
dependencies: [market-research, demand-validation]
compatible_agents: [community-researcher, market-researcher]
tags: [reddit, research, communities, demand-signals]
contract:
  prerequisites:
    - "a research question or product hypothesis"
    - "target niche/vertical named"
  preferred_agents: [community-researcher]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "every claim carries verbatim quotes + thread links"
    - "signal counts include thread dates and community sizes"
    - "contradicting threads preserved, not discarded"
  artifact_contract:
    - "signal ledger (quote, link, subreddit, date, engagement, signal type)"
    - "theme frequency table with recency"
    - "intent classification with confidence"
  quality_gates:
    - "complaints separated from buying intent"
    - "no market-size claim from subreddit samples"
    - "each theme traced to >=2 independent threads where claimed as recurring"
    - "small samples labeled"
  verification:
    - "re-open sampled links; confirm quotes and dates match"
    - "recount theme frequencies from the ledger"
  failure_modes:
    no_relevant_threads: "broaden query; try adjacent subreddits; lower confidence; do not invent"
    small_sample: "label sample size; recommend wider harvest before conclusions"
    astroturf_signal: "down-weight suspiciously uniform praise; note it"
    tool_failure: "retry once; switch to web.search fallback; escalate if both fail"
  escalation:
    - "findings will drive pricing/positioning decisions (human review)"
  handoff_in:
    - "research question / hypothesis"
    - "competitor names if known"
  handoff_out:
    - "pain themes with evidence for demand-validation"
    - "intent-classified signals for opportunity-scoring"
  evaluation:
    - "complaint vs buying-intent separation"
    - "evidence lineage preserved (quote -> link -> date)"
    - "no unsupported generalization from small samples"
  observability:
    - "record queries used, subreddits searched, thread counts"
  related_skills: [community-intelligence, sentiment-analysis, market-research, demand-validation]
---

# Reddit Research

## Purpose
Gather community evidence from Reddit: what users struggle with, ask for, and
buy — systematically and respectfully. This skill produces *evidence*, not
conclusions: every downstream claim must trace back to a verbatim quote and a
thread link.

## When to use / When NOT to use
- use: demand discovery, pain-point mining, competitor weakness research,
  voice-of-customer language for marketing
- avoid: market sizing (a subreddit is never a market), satisfaction surveys,
  support analytics (use first-party data)

## Process
1. **Find the subreddits** — search for the topic/niche; note size and
   activity (posts/day); include adjacent communities (competitors, jobs,
   support). Record which communities were searched even if empty-handed.
2. **Harvest** — top posts (week/month/year) + search results for the
   question (pain, alternatives, tool, recommendation).
3. **Extract** — for each relevant thread: the ask/complaint, verbatim quotes,
   thread engagement (upvotes/comments as interest signal), date.
4. **Classify** — apply the signal taxonomy below. Do not skip this step.
5. **Analyze** — cluster themes, count recurrences, weight by specificity
   (detailed workflows > vague complaints).
6. **Report** — themes with quotes+links, frequency table, sentiment, and
   what this implies for the product.

## Signal taxonomy (classify every extracted item)
One post can carry several signals; record each separately.

| Signal | What it looks like | Weight |
|---|---|---|
| complaint | "this app keeps crashing" | low unless recurring |
| frustration | repeated emotional language, ALL CAPS, "I give up" | low-medium |
| recurring pain | same complaint across threads/months | high |
| workflow problem | describes their multi-step process breaking | high |
| workaround | manual spreadsheet/script to fill the gap | very high |
| feature request | "it should also do X" | medium |
| product dissatisfaction | "switched from X because…" | high |
| competitor weakness | X can't do Y / support is terrible | high |
| replacement intent | "looking for an alternative to X" | very high |
| purchase intent | "where do I buy / what's the price" | very high |
| willingness to pay | states a number: "$50/mo is fine" | very high |
| urgency | "tomorrow", "deadline" | medium (context) |
| frequency | "every day I have to…" | high |
| recommendation request | "what do you use for…?" | medium |
| curiosity / hype / trend | "have you seen this?" | low |

## The core distinction
Do NOT treat these the same:

- "I wish someone made X." → complaint, zero proven commitment.
- "I've tried 5 products, none work, I'd pay $50/month for something that
  solves this." → recurring pain + replacement intent + willingness to pay.

Loud ≠ valuable. Before scoring demand, classify the population:
- **loud minority** — few posters, many comments; check if posters repeat.
- **recurring population-level problem** — different authors, same pain,
  spread over months.
- **high-engagement / low-intent topic** — upvoted drama, no buying signal.
- **low-engagement / high-value pain** — quiet thread, detailed workflow
  problem with a stated budget; often the best lead.

## Scoring a theme (only when the artifact demands ranking)
Score 0–2 on each: pain severity, frequency, urgency, workaround cost,
stated spend, replacement intent, purchase intent, willingness to pay,
market breadth (number of distinct communities), evidence confidence
(multiple independent threads? dated? verifiable?). A theme needs
evidence confidence ≥1 on multiple axes before it can be called "strong".

## Evidence rules
- Every claim carries: quote, link, subreddit, date, engagement.
- Never convert a subreddit sample into a market-size statement.
- Preserved contradictions: if thread A loves tool X and thread B hates it,
  both go in the report.
- If evidence is thin: say so, lower confidence, harvest more, or recommend
  an experiment — never fill the gap with inference that reads like fact.

## Ethics & rules
- Public data only; no private DMs; no brigading; no astroturfing.
- Respect subreddit rules; read-only participation.
- Small sample: label it as such; don't extrapolate from 3 threads.
- Never quote a user by username in marketing material without care — quote
  the sentiment, link the thread.

## References (load on demand)
- `references/signal-examples.md` — labeled examples of each signal type
- `references/scoring-worked-example.md` — a full theme-scoring walkthrough
