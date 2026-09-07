---
id: docker
name: Docker & Compose
description: Containerize apps and orchestrate services with Docker Compose.
category: 16-deployment
version: 1.0.0
source: agent-os core library
license: MIT
capability_type: skill
required_tools: [shell]
risk_level: low
cost_level: low
tags: [docker, compose, containers]
compatible_agents: [devops-engineer, deployment-agent]
---

# Docker & Compose

## Dockerfile rules
- Pin base images by digest or major.minor; multi-stage builds (build deps
  don't ship).
- Non-root user; read-only root filesystem where feasible; minimal layers.
- No secrets in images (ARG/ENV for build-time only; runtime via env).
- Healthcheck instruction matching the app's health endpoint.

## Compose rules
- Named services: app, worker, postgres, redis (per project conventions).
- Volume for persistent data; healthchecks with depends_on condition.
- Env from `.env` file (never committed); secrets via env, not files in the
  image.
- Resource limits (memory/cpu) per service; restart policies.

## Operations
- `docker compose up -d` for the stack; `docker compose logs -f` for logs;
- verify with health endpoints, not just "container running".
- Image tags match commits; rollback = redeploy previous tag.

## Rules
- A container that can't be health-checked is a black box — fix that first.
- Compose reflects production as closely as practical; drift causes surprises.