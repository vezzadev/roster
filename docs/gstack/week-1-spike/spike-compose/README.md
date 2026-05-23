# Spike runtime (compose)

Docker Compose plumbing for the Week 1 validation spike. Copy this directory to a runtime location outside the repo (e.g., `~/spike-runtime/`) before `docker compose up` — Nextcloud's `/agents/` and `/founder/` volumes live inside Docker-managed storage, but anything bind-mounted into containers should not be the repo working tree.

Parent: [../README.md](../README.md) · Spec: [../../design/05-implementation.md](../../design/05-implementation.md) Week 1

## Files

- `docker-compose.yml` — Postgres, Redis, Nextcloud (web + Talk), Letta server, per-agent cbcoutinho/nextcloud-mcp-server containers, `researcher-web-mcp` wrapper. Squid commented out (kept as an optional defensive layer; the wrapper enforces the Researcher contamination blocklist on its own — see "Researcher web-fetch wrapper" below).
- `bring-up.sh` — wrapper that loads `openrouter.local` + `letta.local` + per-agent `*-token.local` + `firecrawl.local` into env and execs `docker compose`. Use this instead of `docker compose` directly.
- `.env.example` — non-sensitive Nextcloud credentials template. Copy to `.env`, fill, `chmod 600`. **Never commit `.env`.**
- `openrouter.local` (gitignored) — raw OpenRouter API key, one line. The sensitive credentials are pulled out of `.env` so they sit in dedicated single-purpose files.
- `letta.local` (gitignored) — raw Letta server token, one line.
- `firecrawl.local` (gitignored) — raw Firecrawl API key for the `researcher-web-mcp` wrapper.
- `<role>-token.local` (gitignored) — per-agent Nextcloud app tokens (`em-token.local`, `analyst-a-token.local`, …).
- `letta-patches/url_validation.py` — bind-mounted into the Letta container to bypass its private-IP SSRF guard for in-network MCP servers. Spike-only; see file header.
- `researcher-web-mcp/` — FastMCP wrapper that exposes `web_search` + `web_scrape` to the Researcher. Built from the in-tree `Dockerfile`; forwards to Firecrawl SaaS while enforcing `blocklist.txt` server-side. See section below.
- `wire-run-1.py` / `probe-tools.py` — pre-boot prompt-hash + banned-token gate, per-agent Letta wiring, and synthetic tool-exec probe.
- `.gitignore` — keeps `.env`, `squid/` operational files, and `researcher-web-mcp/audit/` out of git. `*.local` is matched by the repo-root `.gitignore` (defense in depth).
- `squid/` (optional second-layer, not currently wired) — `squid.conf` + `blocklist.txt` if a future non-Firecrawl egress surface needs proxy-level enforcement on top of the wrapper.
- `Dockerfile.letta` — derived Letta image with OpenTelemetry auto-instrumentation for the Anthropic SDK (gen_ai.* spans including cache_creation_input_tokens and cache_read_input_tokens). Builds locally when the OTel overlay is used.
- `docker-compose.otel.yml` — optional overlay adding an OTel Collector and switching the Letta services to the derived image. Use via `./bring-up.sh -f docker-compose.yml -f docker-compose.otel.yml up -d ...`. Standalone-base usage (without `-f docker-compose.otel.yml`) gets the original behavior with zero observability overhead.
- `otel-collector/config.yaml` — Collector config fanning out to Azure Monitor (Application Insights connection string from `azure-appinsights.local`) and stdout for local debug. Strips `gen_ai.prompt` / `gen_ai.completion` content at the processor stage as defense-in-depth.
- `azure-appinsights.local` (gitignored) — full App Insights connection string, one line.
- `anthropic.local` (gitignored) — raw Anthropic API key for the C-6 native-Anthropic-client unblock path (recommended Run 2 wiring).
- `kql/` — App Insights KQL queries:
  - `01-verify-anthropic-events.kql` — smoke check after first request; confirms gen_ai.* spans land with cache token attributes.
  - `02-route-comparison.kql` — apples-to-apples union of OpenRouter Broadcast events with Anthropic-native OTel events. Adjust the OpenRouter branch's field names to whatever your Broadcast pipeline emits.
  - `03-per-agent-cost.kql` — per-`cloud_RoleName` token + cost breakdown derived from telemetry; mirrors the shape of [../t7-spike-cost.md](../t7-spike-cost.md) "Per-run cost".

## Researcher web-fetch wrapper

`researcher-web-mcp/` is the contamination-guard between the Researcher agent and Firecrawl SaaS (Run 2 only — no Researcher in Run 1). It exists because Firecrawl's `/v2/scrape` API has **no** `excludeDomains` parameter; only `/v2/search` does. Handing the agent raw Firecrawl tools would bypass the consulting-firm blocklist on the dominant operation.

- `server.py` — FastMCP server on port 8000 path `/mcp` (streamable_http transport). Two tools: `web_search` and `web_scrape`.
- `blocklist.txt` — checked into git (source of truth alongside [../t4-mcp-investigation.md](../t4-mcp-investigation.md) "Researcher domain blocklist"). Plain hostnames block host + all subdomains; lines with `*` or `/` are pattern-matched against the full URL (case-insensitive). Hostnames also become `excludeDomains` on every Firecrawl /v2/search call.
- `Dockerfile` — `python:3.12-slim` + `mcp` + `httpx`. Built locally via `./bring-up.sh build researcher-web-mcp`; no registry push.
- `audit/fetch.jsonl` (gitignored) — one JSON line per call (search and scrape, allowed and blocked). Post-run, this is the verification trail that gets copied to [../t5-researcher-urls.md](../t5-researcher-urls.md).

End-to-end verification (verified 2026-05-21 — see [../t4-mcp-investigation.md](../t4-mcp-investigation.md) "Verification checklist"):

```
LETTA_PW="$(tr -d '\n' < letta.local)"
curl -s -X POST http://127.0.0.1:8283/v1/mcp-servers/ \
  -H "Authorization: Bearer $LETTA_PW" -H "Content-Type: application/json" \
  -d '{"server_name":"researcher-web","config":{"mcp_server_type":"streamable_http","server_url":"http://researcher-web-mcp:8000/mcp"}}'
# then call /v1/mcp-servers/<id>/tools/<web_scrape-id>/run with {"args":{"url":"https://www.bcg.com/"}}
# → expect blocked_by_contamination_guard rule host:bcg.com
```

## Bring-up sequence

See the top of `docker-compose.yml` — the 10-step sequence is captured there inline. All `docker compose ...` invocations in that sequence go through `./bring-up.sh ...` instead, so OpenRouter + Letta secrets get loaded from the `.local` files.

Example:

```
./bring-up.sh up -d nc-db nc-redis nextcloud
./bring-up.sh exec --user www-data nextcloud php occ app:install spreed
./bring-up.sh up -d letta nextcloud-mcp
./bring-up.sh logs -f letta
./bring-up.sh down
```

## Observability overlay (optional — for Run 1-anthropic-direct + Run 2)

When the OTel overlay is in the `-f` chain, the two Letta containers are built from `Dockerfile.letta` (base + opentelemetry-instrumentation-anthropic + ancillary OTel) and an `otel-collector` service joins the `spike` network. Per-request `gen_ai.*` spans (including `gen_ai.usage.cache_read_input_tokens` and `gen_ai.usage.cache_creation_input_tokens`) flow OTel → Azure Monitor → App Insights — same destination as the OpenRouter Broadcast → OTel pipeline, so the KQL queries in `kql/` can union both routes for direct comparison.

```
# One-time: stash the App Insights connection string and Anthropic key
printf '%s' 'InstrumentationKey=...;IngestionEndpoint=https://...;LiveEndpoint=https://...' > azure-appinsights.local
printf '%s' 'sk-ant-...' > anthropic.local
chmod 600 azure-appinsights.local anthropic.local

# Build the derived Letta image
./bring-up.sh -f docker-compose.yml -f docker-compose.otel.yml build letta-em letta-researcher

# Bring up with OTel
./bring-up.sh -f docker-compose.yml -f docker-compose.otel.yml up -d \
    otel-collector letta-em letta-researcher \
    nextcloud-mcp-em nextcloud-mcp-researcher researcher-web-mcp

# After wire-run-1.py + first ping → verify in App Insights:
#   kql/01-verify-anthropic-events.kql  (expect 1+ rows, gen_ai.system=anthropic)
```

To revert to the no-OTel base, drop `-f docker-compose.otel.yml` from invocations — the base compose still works unchanged.

## Run 1 readiness gates (post-swap to EM + Researcher)

- [x] `.env` populated; `chmod 600 .env` applied.
- [x] `docker compose up -d nc-db nc-redis nextcloud` → all healthy.
- [x] Talk installed: `docker compose exec --user www-data nextcloud php occ app:install spreed`.
- [x] Users `em`, `researcher` created with sentinel passwords; one app-password each, stored in gitignored `em-token.local` / `researcher-token.local`.
- [x] `/agents/` and `/founder/` folders created; `/agents/` shared rw with em + researcher; `/founder/` invisible to both agent users (PROPFIND verified).
- [x] Talk rooms `#team` (em + researcher) and `EM-Researcher` created with the right participants.
- [x] `docker compose up -d letta nextcloud-mcp-em nextcloud-mcp-researcher researcher-web-mcp` → healthy.
- [x] Letta agents wired with frozen EM + Researcher prompts; SHA-256 hashes verify against [../t5-system-prompts.md](../t5-system-prompts.md) "Hash protocol".
- [x] Banned-token grep returns 0 hits across 25 tokens for both prompts.
- [x] Container image digests captured in [../t5-env-manifest.md](../t5-env-manifest.md) Run 1 row.
- [x] [../t5-run-ledger.md](../t5-run-ledger.md) Run 1 row opened with timestamp + frozen-hash + contamination-grep result + the documented "Run 1 brief is diagnostic, not rubric-gradable" note.
- [ ] Kickoff message `"Begin the engagement."` posted to EM agent.

## Run 2 extras (after Run 1 closes)

- [x] `firecrawl.local` populated with the Firecrawl API key.
- [x] `researcher-web-mcp` service builds + boots + contamination guard verified end-to-end (blocked URL via Letta returns `blocked_by_contamination_guard`).
- [x] User `researcher` exists (provisioned for Run 1).
- [ ] User `analyst-b` created; one app-password (the original `analyst-a` user is also available — its MCP container is already registered with Letta as `nextcloud-analyst-a` but unused in Run 1).
- [ ] DM rooms `EM-B`, `A-B`, `A-Researcher`, `B-Researcher` created (`EM-Researcher` already exists from Run 1; the original `EM-A` DM also still exists).
- [ ] `/agents/researcher-urls-log.md` initialized as an empty file in Nextcloud Files (Researcher appends to it; founder copies the contents to [../t5-researcher-urls.md](../t5-researcher-urls.md) post-run for the repo audit trail).
- [ ] Letta agents wired with frozen Analyst A + Analyst B prompts; hashes + contamination grep re-verified.
- [ ] (Already true from Run 1) Researcher agent attached to the `researcher-web` MCP server's `web_search` + `web_scrape` tools.

## What this does NOT include (deliberately)

- **Roster CLI** — Week 2 work. Spike is hand-config.
- **Provisioner** — Week 2. The manual steps above are what `roster up` will eventually automate.
- **Backup/restore** — beyond spike scope; volumes are ephemeral if you `docker compose down -v`.
- **Production hardening** — `127.0.0.1` binds are the only nod toward "do not expose to the internet". Do not run this stack on a public host.
