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

exec docker compose "$@"
