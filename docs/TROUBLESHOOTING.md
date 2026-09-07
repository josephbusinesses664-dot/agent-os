# Troubleshooting

## General

**"agent-os: command not found"** — activate the venv (`source .venv/bin/activate`)
or run `.venv/bin/agent-os …`.

**`agent-os start` exits immediately** — check `agent-os.log` / the terminal
output for a traceback; confirm port 8300 is free (`lsof -i :8300`).

**Everything is in-memory and my data vanished** — set `DATABASE_URL` +
`REDIS_URL`; the in-memory store resets on restart by design.

## Models

**All model calls fail** — no provider configured: routing falls back to the
`echo` provider (offline). Add `DEEPSEEK_API_KEY` / `ANTHROPIC_API_KEY` /
`GLM_API_KEY` and restart. Verify with `agent-os health` → model-providers.

**Provider errors in logs** — check the key is valid, the base URL is right
(region/endpoint), and outbound network access works. The router fails over
automatically; `model.failover` events appear in `agent-os events`.

**Costs show $0** — the echo provider is free by design; real providers
report token usage which is priced from the model table.

## Mattermost

**Mattermost shows ❌ in health** — `MATTERMOST_URL`/`MATTERMOST_TOKEN` unset
or the server is unreachable. The system still works (CLI/UI); only chat is
degraded.

**Bot doesn't create channels** — the token must belong to a user with
channel-create permission on the team; the team is created if missing.

**No replies to commands** — commands must be `@agent …`-prefixed (or the raw
`@approve <id>` shortcuts) and posted in a channel the bot polls
(town-square/general/executive/approvals/announcements by default).

## Database / Redis

**Postgres connection refused** — wrong host/credentials, or `init_db` failed;
check the URL scheme is `postgresql+asyncpg://`.

**Redis queue not consumed** — the worker must be running (`agent-os start`
starts one; Docker runs a dedicated `worker` service). `agent-os health` →
queue shows the depth.

## Workflows

**A run is stuck at `awaiting_approval`** — that's the approval gate, not a
bug. Approve via Mattermost/CLI/UI (`agent-os approvals list`).

**A run failed** — `agent-os events` and `agent-os audit` show the stage and
error; transient failures retry automatically (`MAX_TASK_RETRIES`). Fix the
cause and re-run (`agent-os workflows run …`).

## Tests

**Integration tests skipped** — expected: Postgres/Redis tests require the
env vars in `TESTING.md`. The MCP test always runs.