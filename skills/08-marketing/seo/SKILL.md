---
id: seo
name: SEO
description: "Intent-driven SEO — keyword demand, content alignment, technical health — with evidence, not stuffing."
category: 08-marketing
version: 1.1.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [content-strategy, web-seo-jsonld]
compatible_agents: [seo-agent, content-agent]
tags: [seo, keywords, search]
contract:
  prerequisites:
    - "the product and the pages/topics to optimize"
  preferred_agents: [seo-agent, content-agent]
  preferred_models: []
  minimum_model_capability: t2
  expected_cost: low
  expected_latency: hours
  evidence_requirements:
    - "keyword choices backed by demand signals (search results, intent)"
  artifact_contract:
    - "SEO plan (keywords, page mapping, technical fixes, metrics)"
  quality_gates:
    - "keywords matched to intent, not stuffed"
    - "title/meta/canonical per page"
    - "technical health checked (indexability, speed)"
    - "measurement defined (rankings, traffic)"
  verification:
    - "check pages render and metadata is correct"
  failure_modes:
    stuffing: "write for intent; keywords follow naturally"
    duplicate: "canonicalize or merge near-duplicate pages"
  escalation:
    - "technical issues blocking indexing"
  handoff_in:
    - "product"
    - "pages/topics"
  handoff_out:
    - "SEO plan with keywords and fixes"
  evaluation:
    - "intent-keyword alignment"
    - "technical correctness"
  observability:
    - "record keyword evidence and fixes"
  related_skills: [content-strategy, web-seo-jsonld, analytics]
---

# SEO

## Purpose
Improve organic visibility with intent-driven optimization: keywords backed
by demand evidence, page-level metadata, technical health — measurement
defined.

## When to use / When NOT to use
- use: content pages, product pages, site launches
- avoid: keyword stuffing; avoid SEO work with no defined metric

## Inputs & assumptions
- inputs: product, pages/topics
- assumptions: search demand is evidence to gather, not to guess

## Workflow
1. For each topic, gather demand evidence: how people phrase the query,
   what intent it carries, what ranks.
2. Map keywords to pages by intent match.
3. Optimize per page: title, meta description, canonical, heading
   structure, content alignment.
4. Check technical health: indexability, speed, structured data.
5. Define measurement: rankings, impressions, clicks.

## Evidence requirements
- Keyword choices backed by demand signals; never stuffed.

## Artifact contract
- `seo-plan`: keyword→page mapping (with intent), metadata fixes,
  technical fixes, metrics.

## Quality gates (definition of done)
- [ ] Keywords matched to intent
- [ ] Title/meta/canonical per page
- [ ] Technical health checked
- [ ] Measurement defined

## Verification
- Check pages render and metadata is correct in the browser.

## Failure & recovery
| failure | recovery |
|---|---|
| stuffing | write for intent |
| duplicate pages | canonicalize or merge |
| indexing blocked | fix and verify robots/sitemap |

## Escalation
- Technical issues blocking indexing — escalate with the specifics.

## Handoff
- receives: product, pages/topics
- passes: SEO plan with keywords, fixes, metrics

## Evaluation
The org evaluates this skill by intent-keyword alignment and technical
correctness.

## Observability
- Record keyword evidence and fixes in the project.

## References
- references/patterns.md — intent classification and metadata rules