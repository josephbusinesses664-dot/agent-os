# Agent OS on the fleet box — setup notes (updated 2026-09-07)

## Services
- `~/agent-os` — docker compose (app :8300, worker, postgres, redis) on network `agentos-net`
- `~/mattermost` — Mattermost team edition :8065 + `mmdb` postgres, same network
- Admin UI: http://100.99.209.83:8300 (Tailscale-only)
- Mattermost web: http://100.99.209.83:8065 (Tailscale-only)
- Credentials: `~/agent-os/.env` (600), agent PATs in `~/agent-os/agent-tokens.env` (600)

## The AI agency in Mattermost
- 41 agent MEMBER ACCOUNTS (username = persona.role, e.g. alex.ceo, jordan.cto,
  riley.product-manager) — each with its own PAT, member of its branch channel
- 9 branch channels: branch-executive/product/engineering/design/research/
  marketing/sales/qa/operations — agents talk there in their own names
- The `ai-agency` bot account runs the listener/system posts
- Humans talk in town-square: casual chat gets a personal reply from Alex;
  work requests (build/create/plan/fix/...) become projects
- Execs (executive + 9 directors) run on deepseek-pro; all workers on deepseek-flash
- All approval gates greenlit (YAML requires_approval=false, REQUIRE_APPROVAL_RISK=medium)
- Dynamic planning + director gate: only stages the branch directors keep actually run

## Code patches on the box (NOT in the agent_os2 GitHub repo — fold in via DeepSeek)
1. bootstrap.py: MattermostService wired with on_command=await on_mattermost_command(svc);
   message mirror (inbox -> branch channels, full payloads); executive chat reply
2. integrations/mattermost/client.py: posts_after since in MILLISECONDS; get_user_by_username
3. integrations/mattermost/service.py: town-square/general/off-topic registered for polling;
   chat-vs-goal routing (WORK_TRIGGERS); agent-user-id filtering (no self-echo loops);
   post_as_user (per-agent accounts); branch channels in CHANNEL_LAYOUT; persona identities
4. orchestrations/engine.py: execute_goal defaults to DYNAMIC planning (not zero_to_hundred);
   _director_filter (directors gate their branch's stages); full stage-output mirroring
5. agents/personas.py (NEW): PERSONAS, USERNAMES, BRANCH_OF, branch channels, token loader
6. agents/hierarchy.py: execs preferred_models=[deepseek-pro], workers [deepseek-flash]
7. cli/main.py: approvals reject maps reject->rejected
8. workflows/*.yaml: requires_approval: false everywhere
9. docker-compose.override.yml: agent-os start command, agent-tokens.env, restart policies,
   REQUIRE_APPROVAL_RISK=medium, sitecustomize.py logging
10. tests updated to greenlit/dynamic semantics (240 passed, 2 skipped)

## Ops
- Rebuild: `cd ~/agent-os && docker compose build app && docker compose up -d`
- Logs: `docker logs -f agent-os-app-1`
- CLI: `docker exec agent-os-app-1 agent-os <cmd>`
- Old box patches preserved: git stash + box-fixes-backup.patch (first session)

## Home Terminal (Prem's direct line to Claude Code) — 2026-09-07
- Mattermost channel `home-terminal` (team ai-agency), bot account `claude-code`
- Bridge: `~/home-terminal-bridge/bridge.py` (nohup + @reboot cron) polls the
  channel, keeps full history in `history.md`, answers via headless
  `claude -p --model deepseek-v4-pro[1m]` with the full history in context
- Bot PAT: `~/home-terminal-token.txt` (600)
- Logs: `~/home-terminal-bridge/bridge.log`
- MCP servers registered for the agency: context7 (docs), github (guarded)
- Deploy keys: GITHUB_TOKEN (OpenClaw's), RENDER_API_KEY + RENDER_OWNER in .env;
  deploy.github/render.manage guarded against Bellam & Kaaram / QueSnack
