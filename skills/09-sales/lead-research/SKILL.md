---
id: lead-research
name: Lead Research
description: Find and qualify leads with evidence — fit signals, intent signals, contact paths.
category: 09-sales
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape, api.call]
risk_level: low
cost_level: low
tags: [leads, prospecting, qualification]
compatible_agents: [lead-researcher, sales-director]
---

# Lead Research

## Purpose
Build a qualified lead list: the right companies/people with evidence of fit
and intent, not a random directory dump.

## Fit signals
- ICP match: industry, size, stack, role, geography.
- Pain signals: job posts for the problem, tool mentions, budget signals.

## Intent signals (rank by strength)
1. Hiring for roles that imply the problem.
2. Using competitors / complaining about them publicly.
3. Asking for solutions in communities.
4. Recent funding/growth/expansion.
5. Engaged with your content/brand.

## Output per lead
```markdown
- Company / contact: ...
- Fit: x/5 (evidence)
- Intent: x/5 (evidence, with links)
- Best channel: <where they're reachable>
- Personalized angle: <one line from their actual situation>
```

## Rules
- Every qualified lead has cited evidence — no "this looks like a fit".
- Respect privacy: public signals only, no purchased data dumps.
- Outreach drafts built on this research still require review before sending.