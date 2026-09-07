---
id: ui-qa
name: UI QA
description: Automated and manual QA over built UI — HTML validity, asset resolution, console errors, runtime behavior.
category: 06-testing
version: 1.0.0
source: agent-os core library (impeccable QA gate adapted)
license: MIT
capability_type: skill
required_tools: [filesystem.read, filesystem.write, shell]
risk_level: low
cost_level: low
tags: [qa, ui, browser]
compatible_agents: [test-engineer, frontend-lead]
---

# UI QA

## Purpose
Verify a built interface actually works in a browser — not just that the code
exists. Run the checks; the exit code is the verdict.

## Checks
1. **HTML validity** — parse the served HTML; no unclosed tags, no invalid
   nesting, no duplicate IDs.
2. **Asset resolution** — every referenced asset (CSS/JS/images/fonts) resolves
   (HTTP 200); no 404s in the network log.
3. **Runtime console** — zero console errors and unhandled rejections while
   exercising the main flows.
4. **Behavioral smoke** — primary flows execute: navigation, form submit,
   error states render, empty states render.
5. **Responsive** — key breakpoints render without horizontal overflow;
   interactions work at mobile width.
6. **Design check** — hierarchy, spacing, states, contrast per the design
   quality checklist.

## Output
- Pass/fail per check with evidence: console log, network statuses, screenshots
  on failure.
- Blocking (exit non-zero) when HTML invalid, assets 404, or console errors —
  even if the page "looks fine".