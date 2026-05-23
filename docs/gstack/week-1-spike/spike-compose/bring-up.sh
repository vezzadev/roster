#!/usr/bin/env bash
# Wraps `docker compose` for the Week 1 spike. Loads OpenRouter + Letta
# secrets from gitignored ./openrouter.local and ./letta.local so they
# never live in .env (which is also gitignored, but used for less-sensitive
# Nextcloud admin credentials).
#
# Usage: ./bring-up.sh up -d nc-db nc-redis nextcloud
#        ./bring-up.sh up -d letta nextcloud-mcp
#        ./bring-up.sh down
#        ./bring-up.sh logs -f letta
#        ./bring-up.sh exec --user www-data nextcloud php occ app:install spreed

set -euo pipefail

cd "$(dirname "$0")"

[ -r openrouter.local ] || { echo "missing ./openrouter.local (raw OpenRouter API key, one line)"; exit 1; }
[ -r letta.local ]      || { echo "missing ./letta.local (raw Letta server token, one line)"; exit 1; }

# `tr -d '\n'` guards against trailing newlines if the file was edited in a text editor
export OPENROUTER_API_KEY
export LETTA_SERVER_PASSWORD
OPENROUTER_API_KEY="$(tr -d '\n' < openrouter.local)"
LETTA_SERVER_PASSWORD="$(tr -d '\n' < letta.local)"

# Per-agent Nextcloud app tokens. Optional at first bring-up — the agent users
# don't exist yet so the tokens haven't been generated. The compose definitions
# guard each MCP service with `${VAR:?...}`, so a missing token only fails that
# specific service.
export EM_APP_TOKEN ANALYST_A_APP_TOKEN ANALYST_B_APP_TOKEN RESEARCHER_APP_TOKEN
EM_APP_TOKEN="$([ -r em-token.local ] && tr -d '\n' < em-token.local || true)"
ANALYST_A_APP_TOKEN="$([ -r analyst-a-token.local ] && tr -d '\n' < analyst-a-token.local || true)"
ANALYST_B_APP_TOKEN="$([ -r analyst-b-token.local ] && tr -d '\n' < analyst-b-token.local || true)"
RESEARCHER_APP_TOKEN="$([ -r researcher-token.local ] && tr -d '\n' < researcher-token.local || true)"

# Firecrawl API key for the researcher-web-mcp wrapper. Same tolerant pattern
# as the per-agent tokens — missing file means only that service fails fast.
export FIRECRAWL_API_KEY
FIRECRAWL_API_KEY="$([ -r firecrawl.local ] && tr -d '\n' < firecrawl.local || true)"

# Application Insights connection string for the optional OTel overlay. One
# line: "InstrumentationKey=...;IngestionEndpoint=...;LiveEndpoint=...".
# Tolerant: only required when docker-compose.otel.yml is in the -f chain.
export AZURE_MONITOR_CONNECTION_STRING
AZURE_MONITOR_CONNECTION_STRING="$([ -r azure-appinsights.local ] && tr -d '\n' < azure-appinsights.local || true)"

# Anthropic API key for the native-Anthropic-client unblock path (C-6 option b
# in ../t5-run-1-conclusions.md). Tolerant: only required when wire-run-1.py
# uses anthropic/claude-* handles instead of openrouter/anthropic/claude-*.
export ANTHROPIC_API_KEY
ANTHROPIC_API_KEY="$([ -r anthropic.local ] && tr -d '\n' < anthropic.local || true)"

# Modal credentials for Letta's tool-sandbox runtime. Both tokens must be present
# for `ToolSettings.modal_sandbox_enabled` to flip True; absent → falls back to
# `SandboxType.LOCAL` (in-Letta-process tool execution, no isolation). File is
# two lines (`MODAL_TOKEN_ID=…` + `MODAL_TOKEN_SECRET=…`), sourced rather than
# read line-by-line so we don't have to parse it ourselves. Tolerant: only
# required when registering Python tools that should run sandboxed (e.g. the
# web_scrape / web_search rewrite that retires researcher-web-mcp).
export MODAL_TOKEN_ID MODAL_TOKEN_SECRET
if [ -r modal.local ]; then
    set -a
    # shellcheck disable=SC1091
    . ./modal.local
    set +a
fi

exec docker compose "$@"
