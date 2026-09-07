# Installation

## Requirements

- Python 3.10+ (developed on 3.11)
- Optional: Docker + Docker Compose (PostgreSQL 16, Redis 7)
- Optional: a Mattermost server with a bot account (personal access token)

## Local install

```bash
git clone <repo-url> agent-os && cd agent-os
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env     # fill in keys (optional)
agent-os seed            # registries + demo project
agent-os demo            # offline end-to-end demo (no keys)
agent-os start           # control plane + worker + Mattermost listener
```

Open http://localhost:8300 for the admin UI.

## With Docker

```bash
cp .env.example .env     # add Mattermost/model keys as desired
docker compose up --build -d
docker compose ps        # app, worker, postgres, redis
```

The `app` service serves the API/admin UI on :8300; the `worker` service
consumes the Redis-backed task queue; PostgreSQL persists everything.

## First run checklist

1. `agent-os health` → all green (Mattermost will show ❌ until configured).
2. `agent-os demo` → workflow completes, artifacts in `workspace/`.
3. `agent-os ask "…"` → project + workflow created; track via admin UI.
4. Mattermost: set `MATTERMOST_URL` / `MATTERMOST_TOKEN`, restart, and the
   listener creates the workspace channels automatically.

## Production notes

- Always set `DATABASE_URL` + `REDIS_URL` in production.
- Run the app behind a reverse proxy (TLS); the admin UI has no auth by
  default — protect it with a proxy/basic auth or keep it on a private
  network (see SECURITY.md).
- Scale workers horizontally: each `worker` container consumes the queue.
- Back up PostgreSQL; workspaces live on the mounted volume.