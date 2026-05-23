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

Per design Cost Model: EM on Opus for synthesis (~3x Sonnet cost); other three roles on Sonnet.

**Inference path changed after Run 1.** Run 1 routed through **OpenRouter** (key in `spike-compose/openrouter.local`); Run 1-anthropic-direct onward routes via **native Anthropic** (key in `spike-compose/anthropic.local`) per C-6 in [t5-run-1-conclusions.md](t5-run-1-conclusions.md) — the OpenRouter / OpenAI-compatible path in Letta does not emit `cache_control` markers (upstream [letta-ai/letta#3351](https://github.com/letta-ai/letta/issues/3351)), so OpenRouter routing pays full uncached list price. The native Anthropic client path in Letta (`anthropic_client.py`) emits `cache_control` correctly. `bring-up.sh` sources both keys tolerantly; whichever the agent handle resolves to is the one actually used.

Run-1-era handles (kept for historical reference; Run 1 row below uses these): `openrouter/anthropic/claude-opus-4.7` for EM; `openrouter/anthropic/claude-sonnet-4.6` for the Sonnet roles. Run-1-anthropic-direct + Run 2 handles (verified 2026-05-22 against the live Anthropic-keyed Letta model registry — 267 handles total, 9 native `anthropic/*`):

| Role | Provider | Letta handle (use this in agent definitions) | Notes |
|------|----------|-----------------------------------------------|-------|
| EM | Anthropic (native) | `anthropic/claude-opus-4-7` | Synthesis role; per design Cost Model. Note hyphen-not-dot: Anthropic's native model IDs use `4-7`; OpenRouter's use `4.7`. |
| Senior Analyst A | Anthropic (native) | `anthropic/claude-sonnet-4-6` | |
| Senior Analyst B | Anthropic (native) | `anthropic/claude-sonnet-4-6` | |
| Researcher | Anthropic (native) | `anthropic/claude-sonnet-4-6` | |

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
| Letta server (em) | `letta/letta:latest` | `sha256:aa66c3eeee13d2dfc40c650d709b550237ee31bfc91942a52fa488a13fa8c102` | v0.16.8; bound `127.0.0.1:8283`; volume `letta_em_data`; private-IP SSRF guard patched via bind-mount of `spike-compose/letta-patches/url_validation.py`. Per-agent Letta architecture (see [t5-run-ledger.md](t5-run-ledger.md) "Letta tool-namespace finding"). |
| Letta server (researcher) | `letta/letta:latest` | `sha256:aa66c3eeee13d2dfc40c650d709b550237ee31bfc91942a52fa488a13fa8c102` | same image; bound `127.0.0.1:8284`; volume `letta_researcher_data`; same SSRF-guard patch. |
| MCP (em) | `ghcr.io/cbcoutinho/nextcloud-mcp-server:latest` | `sha256:2056bb4cb8ca6674bb229fac24e904b39d098d1cf28622c7e00217108024929d` | v1.27.0; auth scoped to em via `NEXTCLOUD_USERNAME=em` |
| MCP (researcher) | `ghcr.io/cbcoutinho/nextcloud-mcp-server:latest` | `sha256:2056bb4cb8ca6674bb229fac24e904b39d098d1cf28622c7e00217108024929d` | same image; auth scoped to researcher (Run 1 pairing — post-swap from analyst-a) |
| MCP (researcher-web wrapper) | `spike-compose-researcher-web-mcp:latest` (locally built) | `sha256:cbebd3ca011e99590b4728dafc6dee60bd9c53b84fc7420146494faebd8b31a9` | Firecrawl-backed `web_search` + `web_scrape` with the contamination blocklist enforced server-side |
| MCP (analyst-a) | `ghcr.io/cbcoutinho/nextcloud-mcp-server:latest` | `sha256:2056bb4cb8ca6674bb229fac24e904b39d098d1cf28622c7e00217108024929d` | still running but unused in Run 1 post-swap; will be used in Run 2 |

#### Letta config

- Letta version: 0.16.8
- Persistence backend: default (sqlite in `/root/.letta`)
- Agent runtime: OpenRouter via `OPENROUTER_API_KEY` env (sourced from `spike-compose/openrouter.local` by `bring-up.sh`)
- Server password: `LETTA_SERVER_PASSWORD` (sourced from `letta.local`); bearer-auth required on all `/v1/*` paths

#### Nextcloud config

- Version: 30.0.17.2
- Apps enabled: Talk (spreed 20.1.11), Files (built-in), Notes/Tables/Deck (built-in)
- Storage backend: Nextcloud default (sqlite metadata + local files on `nc_data` Docker volume)
- Users: admin, em, analyst-a, researcher (Run 2 will add analyst-b)
- Folders: `/agents/` (rw shared with em + analyst-a + researcher, share IDs 1+2+3), `/founder/` (admin-only; verified invisible from agent accounts via PROPFIND)
- Talk rooms: `team` (token `vzyiva4u`, type=2; members em + analyst-a + researcher), `EM-A` (token `eg72sheb`, type=2), `EM-Researcher` (token `z4n3425w`, type=2)

#### Models

| Agent | Letta handle | Model |
|-------|--------------|-------|
| em (agent-0a9bce41 on letta-em) | `openrouter/anthropic/claude-opus-4.7` | Claude Opus 4.7 via OpenRouter. Singleton-era id `agent-414ea769…` retired by the per-agent Letta cutover. |
| researcher (agent-b4a10f8f on letta-researcher) | `openrouter/anthropic/claude-sonnet-4.6` | Claude Sonnet 4.6 via OpenRouter. Singleton-era id `agent-92367e4d…` retired. |

#### MCP server(s)

- Source: `ghcr.io/cbcoutinho/nextcloud-mcp-server:latest` (v1.27.0). One container per agent identity for hard-isolation (cannot impersonate the wrong agent).
- Endpoints exposed: 134 tools per server; the spike attaches only 15 (Talk send/list/get-messages/get-conv/list-participants/mark-as-read + WebDAV read/write/list/find/search/create/delete/copy/move) — see `spike-compose/wire-run-2.py` `NEXTCLOUD_SPIKE_TOOLS` for the canonical set.
- Researcher additionally attaches 2 tools from the `researcher-web` wrapper (`web_search`, `web_scrape`).
- Letta MCP server registrations (post per-agent cutover; each ID is scoped to its own Letta DB):
  - on `letta-em` (8283): `nextcloud-em`
  - on `letta-researcher` (8284): `nextcloud-researcher`, `researcher-web`
  - (`nextcloud-analyst-a` from the singleton run was discarded with the singleton Letta volume; Run 2 will register it on `letta-analyst-a`.)
- `wire-run-2.py` and `probe-tools.py` resolve these by `server_name` at runtime so the IDs are not hard-coded. Both scripts also carry a per-role `letta_url` so each role's MCP registration + agent creation lands on the role's own Letta.

## Change log

| Run | Component | Change | Reason |
|-----|-----------|--------|--------|
| Pre-Run 1 | Letta | Bind-mounted `url_validation.py` patch to bypass private-IP SSRF guard | Stock validator rejected `http://nextcloud-mcp-em:8000` because the Docker bridge resolves to 172.x — Letta has no env to disable. Patch keeps blocked-hostname checks; only the IP-globality check is bypassed. TODO: upstream a trusted-hosts env. |
| Pre-Run 2 (built pre-Run 1) | new service `researcher-web-mcp` | Added FastMCP wrapper around Firecrawl SaaS exposing `web_search` + `web_scrape`. Image `spike-compose-researcher-web-mcp:latest` `sha256:cbebd3ca011e99590b4728dafc6dee60bd9c53b84fc7420146494faebd8b31a9` (locally built; not pushed). Letta MCP server `mcp_server-cfebe094-013e-4ba3-a244-6c77f56d5c59` server_name=`researcher-web`. | Firecrawl `/v2/scrape` exposes no `excludeDomains` parameter (only `/v2/search` does), so giving the Researcher raw firecrawl-mcp tools would bypass the consulting-firm blocklist on the dominant op. Wrapper enforces `blocklist.txt` server-side. End-to-end verified: Letta tool-run for `web_scrape("https://www.bcg.com/")` returns `blocked_by_contamination_guard` rule `host:bcg.com` with no network egress; `web_search` round-trips to Firecrawl with `excludeDomains` populated. |
| Pre-Run 1 (post-swap) | Run 1 pairing changed | Run 1 swapped from EM+Analyst A to EM+Researcher. Provisioned Nextcloud user `researcher` with sentinel pw `researcher-pw-smoke` (rotate before any non-spike use) + an app token stored in the gitignored `spike-compose/researcher-token.local`. Brought up `nextcloud-mcp-researcher`. Created Talk DM `EM-Researcher` (token `z4n3425w`); added researcher to `#team`. Deleted old agents (`agent-51e9d3e6` em, `agent-5b04211a` analyst-a); recreated EM + Researcher with re-frozen prompts on the (then) singleton Letta. Tool-exec probe (per-server execute endpoint) passed — superseded by the architecture change below. | Better ablation for Run 1 — exercises the web-fetch path + contamination guard live before Run 2; analyst-synthesis loop deferred to Run 2 where analysts have peers to collaborate with. |
| Pre-Run-1-anthropic-direct (2026-05-22 ~18:30 UTC) | Inference path | Recreated `letta-em` + `letta-researcher` with `ANTHROPIC_API_KEY` env now sourced from `spike-compose/anthropic.local` by `bring-up.sh` (alongside the existing `OPENROUTER_API_KEY`, both passed tolerantly). Verified post-recreate: `GET /v1/models/` on each Letta now exposes 9 native `anthropic/*` handles (267 total) alongside the existing OpenRouter set. `wire-run-1.py` switched from `openrouter/anthropic/claude-{opus-4.7,sonnet-4.6}` to native `anthropic/claude-{opus-4-7,sonnet-4-6}`. Volumes (`letta_*_pgdata`, `letta_*_data`) untouched — Run 1's agent state still recoverable from the postgres mount. | C-6 in [t5-run-1-conclusions.md](t5-run-1-conclusions.md): switch to Letta's native Anthropic client path so `cache_control` markers actually get emitted (root cause C-3 / upstream letta-ai/letta#3351). |
| Pre-Run 1 (per-agent Letta cutover, 2026-05-22) | `letta` (singleton) → `letta-em` + `letta-researcher` (per-agent containers) | Discovered the singleton Letta dedupes MCP tool names globally; both sidecars' `talk_send_message` collapsed to the last-registered MCP server, so the EM agent's kickoff brief posted to `#team` as actor `researcher`. Replaced the singleton with one Letta container per agent (each with its own `letta_<role>_data` volume + the SSRF-guard patch bind-mount); `nextcloud-mcp-em` registered only on `letta-em`, `nextcloud-mcp-researcher` + `researcher-web` only on `letta-researcher`. Stubs for `letta-analyst-a` + `letta-analyst-b` commented into `docker-compose.yml` for Run 2. Re-wired agents on the new Lettas: EM `agent-0a9bce41-6b16-4db8-88fe-150ffd255ad6`, Researcher `agent-b4a10f8f-ce23-4ebd-a3c1-39d4af6ec7e8`. Old singleton-Letta agent IDs retired with the volume. `probe-tools.py` rewritten to use the agent-driven path (POST `/v1/agents/<id>/messages` asking for the tool call) instead of the per-server execute endpoint that bypassed the bug; new probe passes — EM posts as `em`, Researcher posts as `researcher`. | Letta has no per-MCP namespacing on tool names within a single instance; only structural isolation (separate Letta DBs) prevents the collision. See [t5-run-ledger.md](t5-run-ledger.md) "Letta tool-namespace finding" for the full diagnosis. |
