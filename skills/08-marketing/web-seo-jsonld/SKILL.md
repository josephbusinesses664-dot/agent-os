---
id: web-seo-jsonld
name: Web SEO & JSON-LD
description: "Local-business SEO — title, meta, canonical, Open Graph, JSON-LD, sitemap, robots — with validation."
category: 08-marketing
version: 1.1.0
source: agent-os core library (prem-ium.inc house pattern)
license: MIT
capability_type: skill
required_tools: [repo.search, web.scrape]
risk_level: low
cost_level: low
dependencies: [seo, frontend-engineering]
compatible_agents: [seo-agent, frontend-lead]
tags: [seo, jsonld, structured-data, local-business]
contract:
  prerequisites:
    - "the site/pages and their business details"
  preferred_agents: [seo-agent, frontend-lead]
  preferred_models: []
  minimum_model_capability: t1
  expected_cost: low
  expected_latency: minutes
  evidence_requirements:
    - "structured data validated (schema correctness, not just presence)"
  artifact_contract:
    - "SEO implementation (meta, JSON-LD, sitemap, robots) + validation"
  quality_gates:
    - "location-keyworded title + meta description"
    - "canonical present on every page"
    - "Open Graph + Twitter cards present"
    - "JSON-LD validates against schema"
    - "sitemap.xml + robots.txt present and correct"
  verification:
    - "validate the rendered page metadata and JSON-LD"
  failure_modes:
    invalid_jsonld: "validate against schema; fix types/required fields"
    missing_canonical: "add per-page canonical"
  escalation:
    - "structured-data conflicts with platform requirements"
  handoff_in:
    - "site"
    - "business details"
  handoff_out:
    - "SEO implementation with validation evidence"
  evaluation:
    - "metadata correctness"
    - "JSON-LD validity"
  observability:
    - "record validation results"
  related_skills: [seo, frontend-engineering, content-strategy]
---

# Web SEO & JSON-LD

## Purpose
Wire on-page SEO and structured data — location-keyworded title/meta,
canonical, Open Graph, JSON-LD, sitemap, robots — and validate the result.

## When to use / When NOT to use
- use: local-business sites, marketing pages, launches
- avoid: claiming SEO done without validating metadata and structured data

## Inputs & assumptions
- inputs: site/pages, business details
- assumptions: business facts (address, hours, geo) assumed from the
  client unless verified — flag verification status

## Workflow
1. Per page: location-keyworded title, meta description, canonical,
   Open Graph + Twitter cards.
2. Add JSON-LD: LocalBusiness/Restaurant schema (address, geo, rating,
   hours, OrderAction where applicable).
3. Add sitemap.xml and robots.txt.
4. Validate: rendered metadata, JSON-LD against schema, sitemap entries
   resolve.
5. Record validation evidence.

## Evidence requirements
- Structured data validated — presence alone is not enough.

## Artifact contract
- `seo-implementation`: per-page metadata, JSON-LD, sitemap/robots,
  validation results.

## Quality gates (definition of done)
- [ ] Title/meta location-keyworded
- [ ] Canonical on every page
- [ ] OG + Twitter cards present
- [ ] JSON-LD validates
- [ ] sitemap + robots correct

## Verification
- Validate rendered page metadata and JSON-LD (web.scrape the page).

## Failure & recovery
| failure | recovery |
|---|---|
| invalid JSON-LD | validate and fix schema fields |
| missing canonical | add per page |
| sitemap 404s | regenerate from actual routes |

## Escalation
- Structured-data conflicts with platform requirements.

## Handoff
- receives: site, business details
- passes: SEO implementation with validation evidence

## Evaluation
The org evaluates this skill by metadata correctness and JSON-LD validity.

## Observability
- Record validation results in the audit trail.

## References
- references/patterns.md — JSON-LD recipes per business type