# Env Manifest

Versions of every component touched during the Week 1 spike. Captured at the start of each run and re-captured if anything changes.

Parent: [../design.md](../design.md) · Spec: [../design/07-refinements.md](../design/07-refinements.md) T4-C

## Why this file matters

When a spike result needs to be reproduced months later (or a regression appears), "Letta latest" or "Nextcloud current" is unactionable. Pin versions per run; re-pin if anything moves.

## Snapshot template

Repeat this block per run (Run 1, Run 2, …). Stamp the timestamp at the start of the run.

### Run _N_ — _timestamp_

#### Host

- OS: _e.g., Linux 6.6.x WSL2 / macOS 14.x_
- Docker: `docker --version`
- Docker Compose: `docker compose version`
- Architecture: _amd64 / arm64_

#### Containers

| Service | Image | Tag / digest | Notes |
|---------|-------|--------------|-------|
| Nextcloud | | | |
| Nextcloud DB (postgres / mariadb) | | | |
| Letta server | | | |
| Letta headless / worker | | | |
| MCP server (if separate container) | | | |

#### Letta config

- Letta version: `letta --version` or container tag
- Persistence backend: _sqlite / postgres / …_
- Agent runtime: _OpenRouter (Anthropic models) / proxy_ — direct Anthropic API is no longer the canonical path; v1 routes through OpenRouter

#### Nextcloud config

- Version: _from `occ status`_
- Apps enabled: _Talk, Files, …_
- Storage backend:

#### Models

Per design Cost Model: EM on Opus for synthesis (~3x Sonnet cost); other three roles on Sonnet. v1 routes inference through **OpenRouter** (the OpenRouter API key lives in `spike-compose/openrouter.local`, sourced into the Letta container by `spike-compose/bring-up.sh`). Letta exposes OpenRouter-routed models under handles prefixed `openrouter/`; the table below shows the Letta handles wired into the agent definitions. The bare OpenRouter ID (without the `openrouter/` prefix) applies only if you bypass Letta — e.g., the t2 raw-OpenRouter fallback.

Verified at smoke-test 2026-05-21: both handles below resolve in Letta's model registry against the live OpenRouter key (Letta synced 258 LLM models, two opus 4.7 variants — `:fast` is the alternative routing flag — and one sonnet 4.6).

| Role | Provider | Letta handle (use this in agent definitions) | OpenRouter ID (fallback if bypassing Letta) | Notes |
|------|----------|-----------------------------------------------|---------------------------------------------|-------|
| EM | OpenRouter | `openrouter/anthropic/claude-opus-4.7` | `anthropic/claude-opus-4.7` | Synthesis role; per design Cost Model |
| Senior Analyst A | OpenRouter | `openrouter/anthropic/claude-sonnet-4.6` | `anthropic/claude-sonnet-4.6` | |
| Senior Analyst B | OpenRouter | `openrouter/anthropic/claude-sonnet-4.6` | `anthropic/claude-sonnet-4.6` | |
| Researcher | OpenRouter | `openrouter/anthropic/claude-sonnet-4.6` | `anthropic/claude-sonnet-4.6` | |

OpenRouter pricing carries a markup over direct Anthropic — revisit SC#6 ($200/mo) math in [t7-spike-cost.md](t7-spike-cost.md) once the trendline lands.

#### MCP server(s)

- Source: _community repo + commit SHA / built-in MVP + commit SHA_
- Endpoints exposed: _list_

## Snapshots

### Run 1 — 2026-05-21 (2-agent smoke)

#### Host

- OS: Linux 6.6.114.1-microsoft-standard-WSL2 (WSL2 on Windows 11)
- Docker: Docker Engine 28.x (Docker Desktop)
- Docker Compose: v2
- Architecture: amd64

#### Containers

| Service | Image | Tag / digest | Notes |
|---------|-------|--------------|-------|
| Nextcloud | `nextcloud:30` | `sha256:fb966733647ea03f0446b0c22eac9733c8eb616d37b960caca9d4c3010e14a08` | spreed 20.1.11 installed (Talk app) |
| Nextcloud DB | `postgres:16-alpine` | `sha256:16bc17c64a573ef34162af9298258d1aec548232985b33ed7b1eac33ba35c229` | |
| Nextcloud Redis | `redis:7-alpine` | `sha256:6ab0b6e7381779332f97b8ca76193e45b0756f38d4c0dcda72dbb3c32061ab99` | session + lock cache |
| Letta server | `letta/letta:latest` | `sha256:aa66c3eeee13d2dfc40c650d709b550237ee31bfc91942a52fa488a13fa8c102` | v0.16.8; private-IP SSRF guard patched via bind-mount of `spike-compose/letta-patches/url_validation.py` |
| MCP (em) | `ghcr.io/cbcoutinho/nextcloud-mcp-server:latest` | `sha256:2056bb4cb8ca6674bb229fac24e904b39d098d1cf28622c7e00217108024929d` | v1.27.0; auth scoped to em via `NEXTCLOUD_USERNAME=em` |
| MCP (analyst-a) | `ghcr.io/cbcoutinho/nextcloud-mcp-server:latest` | `sha256:2056bb4cb8ca6674bb229fac24e904b39d098d1cf28622c7e00217108024929d` | same image; auth scoped to analyst-a |

#### Letta config

- Letta version: 0.16.8
- Persistence backend: default (sqlite in `/root/.letta`)
- Agent runtime: OpenRouter via `OPENROUTER_API_KEY` env (sourced from `spike-compose/openrouter.local` by `bring-up.sh`)
- Server password: `LETTA_SERVER_PASSWORD` (sourced from `letta.local`); bearer-auth required on all `/v1/*` paths

#### Nextcloud config

- Version: 30.0.17.2
- Apps enabled: Talk (spreed 20.1.11), Files (built-in), Notes/Tables/Deck (built-in)
- Storage backend: Nextcloud default (sqlite metadata + local files on `nc_data` Docker volume)
- Users: admin, em, analyst-a (Run 2 will add analyst-b, researcher)
- Folders: `/agents/` (rw shared with em + analyst-a, share IDs 1+2), `/founder/` (admin-only; verified invisible from agent accounts via PROPFIND)
- Talk rooms: `team` (token `vzyiva4u`, type=2), `EM-A` (token `eg72sheb`, type=2)

#### Models

| Agent | Letta handle | Model |
|-------|--------------|-------|
| em (agent-51e9d3e6) | `openrouter/anthropic/claude-opus-4.7` | Claude Opus 4.7 via OpenRouter |
| analyst-a (agent-5b04211a) | `openrouter/anthropic/claude-sonnet-4.6` | Claude Sonnet 4.6 via OpenRouter |

#### MCP server(s)

- Source: `ghcr.io/cbcoutinho/nextcloud-mcp-server:latest` (v1.27.0). One container per agent identity for hard-isolation (cannot impersonate the wrong agent).
- Endpoints exposed: 134 tools per server; the spike attaches only 15 (Talk send/list/get-messages/get-conv/list-participants/mark-as-read + WebDAV read/write/list/find/search/create/delete/copy/move) — see `spike-compose/wire-run-1.py` `SPIKE_TOOLS` for the canonical set.
- Letta MCP server IDs: `mcp_server-db172699-cf6e-4baf-9538-6ff9b3e6d471` (em), `mcp_server-a7916894-3272-41d4-959b-9078d13b5cdb` (analyst-a)

## Change log

| Run | Component | Change | Reason |
|-----|-----------|--------|--------|
| Pre-Run 1 | Letta | Bind-mounted `url_validation.py` patch to bypass private-IP SSRF guard | Stock validator rejected `http://nextcloud-mcp-em:8000` because the Docker bridge resolves to 172.x — Letta has no env to disable. Patch keeps blocked-hostname checks; only the IP-globality check is bypassed. TODO: upstream a trusted-hosts env. |
| Pre-Run 2 (built pre-Run 1) | new service `researcher-web-mcp` | Added FastMCP wrapper around Firecrawl SaaS exposing `web_search` + `web_scrape`. Image `spike-compose-researcher-web-mcp:latest` `sha256:cbebd3ca011e99590b4728dafc6dee60bd9c53b84fc7420146494faebd8b31a9` (locally built; not pushed). Letta MCP server `mcp_server-cfebe094-013e-4ba3-a244-6c77f56d5c59` server_name=`researcher-web`. | Firecrawl `/v2/scrape` exposes no `excludeDomains` parameter (only `/v2/search` does), so giving the Researcher raw firecrawl-mcp tools would bypass the consulting-firm blocklist on the dominant op. Wrapper enforces `blocklist.txt` server-side. End-to-end verified: Letta tool-run for `web_scrape("https://www.bcg.com/")` returns `blocked_by_contamination_guard` rule `host:bcg.com` with no network egress; `web_search` round-trips to Firecrawl with `excludeDomains` populated. |
