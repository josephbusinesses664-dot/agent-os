---
id: market-research
name: Market Research
description: Evidence-oriented market research — sizing, trends, segments, demand validation and customer language.
category: 01-discovery
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape, api.call]
risk_level: low
cost_level: low
tags: [market, research, sizing, segments]
compatible_agents: [market-researcher, product-researcher, research-director]
---

# Market Research

## Purpose
Produce decision-grade market understanding: size, trends, segments, demand,
customer language — each claim labeled with evidence and confidence.

## Workflow
1. **Define questions** — what decision does this research inform?
2. **Gather** — web search + scrape primary sources (vendor pages, forums, job posts,
   review sites, public datasets). Prefer multiple independent sources.
3. **Organize evidence** — one row per claim: claim | source | date | confidence.
4. **Cross-check** — find contradicting evidence; report disagreements explicitly.
5. **Synthesize** — market size (TAM/SAM/SOM with assumptions shown), trend direction,
   segment map, demand signals, customer language (exact phrases users use).
6. **Report uncertainty** — what we don't know and what would change the conclusion.

## Customer language
Quote users verbatim: their words for the problem, the job-to-be-done and
current workarounds. Marketing and product copy must use *their* language.

## Rules
- Distinguish observed evidence from inference.
- Show your assumptions for any sizing math.
- Never fabricate sources.