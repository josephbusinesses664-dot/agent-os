# Skills

## Architecture

Skills live under `skills/` as directories containing a `SKILL.md` with YAML
frontmatter. Frontmatter carries the capability metadata the registry needs:

```yaml
---
id: market-research
name: Market Research
description: Evidence-oriented market research — sizing, trends, demand…
category: 01-discovery
version: 1.0.0
source: agent-os core library        # provenance
license: MIT
capability_type: skill              # skill | agent | workflow | tool | prompt | hook
required_tools: [web.search, web.scrape]
required_models: [deepseek-pro]
risk_level: low
cost_level: low
dependencies: []
compatible_agents: [market-researcher]
tags: [market, research]
---
# Body — loaded into context only when this skill is selected.
```

## The 20 branches

```
01-discovery  02-strategy  03-product  04-design  05-engineering
06-testing    07-security  08-marketing 09-sales  10-research
11-agency     12-operations 13-automation 14-data  15-ai
16-deployment 17-monitoring 18-business-intelligence
19-community-intelligence 20-integrations
```

The default install ships 100 skills across all branches. Content is adapted
from the approved capability sources (Superpowers methodology, Addy Osmani
code review, MengTo design methodology, GSAP official guidance, Reddit
research practice, public-apis catalog) — provenance is kept in frontmatter
and licenses are respected.

## Progressive disclosure

Agents do **not** load every skill. A task triggers a capability search
(`skill_registry.search(query, agent_id)`), which scores skills on
id/name/tags/description/body coverage, applies compatibility filters, and
returns only the top-k. `load_for_agent` expands transitive dependencies and
returns full bodies — so the registry can grow to thousands of skills without
blowing up model context.

## Registry operations

```bash
agent-os skills list | search <query> | enable <id> | disable <id> | reload
```

New skills = drop a directory with a SKILL.md + `agent-os skills reload`
(no code changes). Skills that repeatedly fail can be disabled; the registry
supports evaluation and provenance tracking for every capability.