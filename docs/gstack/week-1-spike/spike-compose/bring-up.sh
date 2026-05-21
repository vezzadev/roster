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

exec docker compose "$@"
