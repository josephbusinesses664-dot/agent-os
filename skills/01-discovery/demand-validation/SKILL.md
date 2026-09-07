---
id: demand-validation
name: Demand Validation
description: Validate whether real demand exists before building — signals, willingness to pay, falsifiable tests.
category: 01-discovery
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape, api.call]
risk_level: low
cost_level: low
tags: [demand, validation, signals]
compatible_agents: [market-researcher, product-researcher, product-manager]
---

# Demand Validation

## Purpose
Determine whether enough people want this enough to pay, before committing
build resources. Prefer falsifiable checks over opinions.

## Signal hierarchy (strongest first)
1. **Money** — existing sales, pre-orders, paid tools solving adjacent problems.
2. **Behavior** — forum/community threads, upvotes, search volume trends, job posts.
3. **Explicit asks** — feature requests, "is there a tool for X" posts, intros.
4. **Complaints** — recurring pain with existing solutions.
5. **Attention** — engagement on related content (weakest but cheap signal).

## Workflow
1. List the core hypothesis: "People with <pain> will pay <price> for <solution>."
2. Gather signals per category above; record counts and sources.
3. Score demand: money(0-5) + behavior(0-5) + asks(0-5) + complaints(0-5).
4. Identify the cheapest falsifiable test (landing page, waitlist, manual concierge).
5. Recommend: **validate / iterate / kill**, with the reason tied to evidence.

## Rules
- A "good idea" is not demand. Demand = evidence people act.
- Report what would falsify the hypothesis.