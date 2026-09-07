---
id: webhooks
name: Webhooks
description: Receive and send webhooks reliably — verification, idempotency, retries, replay.
category: 20-integrations
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: []
risk_level: medium
cost_level: low
tags: [webhooks, events, integration]
compatible_agents: [backend-lead, ai-engineer]
---

# Webhooks

## Purpose
Move events between systems reliably: delivery is at-least-once, so receivers
must be idempotent and verifiable.

## Receiving
1. **Verification** — authenticate senders (signature/secret); reject
   unverified payloads (spoofing is a real threat).
2. **Schema** — validate payloads at the boundary; version the event schema.
3. **Idempotency** — dedupe by event id (Redis/DB unique index); handlers are
   safe to re-run.
4. **Fast ack** — ack 2xx quickly, process async (queue); never do heavy work
   in the webhook handler.
5. **Replay** — handle out-of-order and duplicates; use event time, not
   arrival time, where order matters.

## Sending
- Retry with exponential backoff on non-2xx; dead-letter after limits;
- include an event id and signature; document retry cadence.

## Rules
- A webhook without signature verification is an open door — fix that first.
- Assume every webhook can arrive twice and out of order.