---
id: seo
name: SEO
description: SEO fundamentals — keyword research, on-page, technical SEO, structured data, local SEO.
category: 08-marketing
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [web.search]
risk_level: low
cost_level: low
tags: [seo, keywords, structured-data]
compatible_agents: [seo-agent]
---

# SEO

## Purpose
Make pages findable for the searches real customers make.

## Keyword research
- Start from customer language and the product's job-to-be-done.
- Target: head terms (awareness) + long-tail terms (intent) mapped to pages.
- Check difficulty/competition signals; pick winnable queries first.

## On-page
- One primary keyword per page; title ≤ 60 chars with the keyword early;
- meta description ≤ 155 chars, actionable; H1 unique and descriptive.
- Content answers the query fully (use the actual question in headings);
- internal links with descriptive anchors; image alt text meaningful.

## Technical
- Crawlable: clean URLs, sitemap.xml, robots.txt, canonical tags, no orphan
  pages; fast (Core Web Vitals); mobile-friendly; HTTPS.
- Structured data: JSON-LD (LocalBusiness/Product/Article/FAQ as applicable)
  with accurate geo, hours, ratings, OrderAction.

## Rules
- SEO content must be genuinely useful first; keyword stuffing is penalized.
- No fake reviews, no doorway pages, no thin content farms.
- Verify with actual tools: page fetch, index checks.