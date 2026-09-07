---
id: web-seo-jsonld
name: Web SEO & Structured Data
description: On-page SEO and JSON-LD structured data for local-business and product sites.
category: 08-marketing
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [filesystem.read, filesystem.write]
risk_level: low
cost_level: low
tags: [seo, jsonld, structured-data]
compatible_agents: [seo-agent]
---

# Web SEO & Structured Data

## Purpose
Optimize a static site for search and local discovery: location-keyworded
titles, meta, canonical, Open Graph, JSON-LD, sitemap, robots.

## On-page checklist
- Title: `Primary Keyword — Brand | Location` ≤ 60 chars, keyword early.
- Meta description ≤ 155 chars, specific, with the location keyword.
- Canonical URL on every page (self-referencing).
- Open Graph + Twitter cards (title, description, image, type).
- One H1 per page; semantic headings.

## JSON-LD
Local business / product / article schemas as applicable:
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "...", "address": {...}, "geo": {...},
  "openingHours": "...", "telephone": "...",
  "aggregateRating": {...}   // only real ratings
}
```
Include OrderAction / Offer where the business takes orders. Validate with
the Rich Results Test before shipping.

## Files
- `sitemap.xml` — every indexable URL, lastmod, priority.
- `robots.txt` — allow crawl, reference sitemap, block nothing useful.

## Rules
- Structured data must match the actual page content; fabricated ratings are a
  penalty risk and dishonest.