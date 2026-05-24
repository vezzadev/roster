#!/usr/bin/env bash
# Run 1' kickoff — 2-agent (EM + Researcher) validation, hard 15-min wall-clock cap.
#
# Steps:
#   1. Load secrets from `.env.run1prime` (gitignored).
#   2. Bring stack up with build if needed.
#   3. Stream Gateway logs in background.
#   4. Send EM the kickoff prompt via `openclaw agent`.
#   5. Sleep 15 min wall-clock — agents do their work autonomously via
#      heartbeat + Talk channel.
#   6. Bring stack down (gracefully) regardless of state.
#   7. Snapshot session transcripts to `./run-1prime-snapshot/`.
#   8. Run scrape-usage.py for the cost rollup.
#
# Idempotent: re-running tears down and starts fresh.

set -euo pipefail
cd "$(dirname "$0")"

HARD_CAP_SECONDS="${HARD_CAP_SECONDS:-900}"  # 15 min default
SNAPSHOT_DIR="./run-1prime-snapshot/$(date -u +%Y-%m-%dT%H-%M-%SZ)"
LOG_FILE="$SNAPSHOT_DIR/gateway.log"

[ -r .env.run1prime ] || { echo "missing .env.run1prime — copy values from week-1-spike/spike-compose/*.local"; exit 1; }

mkdir -p "$SNAPSHOT_DIR"
echo "▶ Run 1' kickoff at $(date -u +%FT%TZ), snapshot dir: $SNAPSHOT_DIR"

# Tear down any prior run state.
docker compose --env-file .env.run1prime -f docker-compose.2agent.yml down -v >/dev/null 2>&1 || true

# Up with build (Dockerfile may have been updated since boot-smoke).
docker compose --env-file .env.run1prime -f docker-compose.2agent.yml up -d --build

# Phase 1 — wait for nextcloud-init to exit cleanly (cold-boot is ~2-4 min:
# Nextcloud install + Talk app install + user/room provisioning).
echo "▶ Waiting for nextcloud-init to provision users + rooms (up to 6 min)…"
for i in $(seq 1 360); do
  state=$(docker inspect -f '{{.State.Status}}/{{.State.ExitCode}}' \
                nextcloud-init-run1prime 2>/dev/null || echo unknown)
  case "$state" in
    exited/0)
      echo "✓ nextcloud-init OK"; break ;;
    exited/*)
      echo "✗ nextcloud-init failed: $state"
      docker logs nextcloud-init-run1prime | tail -50; exit 1 ;;
  esac
  sleep 1
done

# Phase 2 — wait for Gateway readiness. Gateway only starts after nextcloud-init
# completes successfully (depends_on: service_completed_successfully).
echo "▶ Waiting for Gateway ready…"
for i in $(seq 1 120); do
  if docker logs openclaw-run-1prime 2>&1 | grep -q '\[gateway\] ready'; then break; fi
  sleep 1
done
docker logs openclaw-run-1prime 2>&1 | grep -q '\[gateway\] ready' \
  || { echo "✗ Gateway not ready after 120s"; docker logs openclaw-run-1prime | tail -50; exit 1; }
echo "✓ Gateway ready"

# Stream gateway logs to file in the background.
docker logs -f openclaw-run-1prime >"$LOG_FILE" 2>&1 &
LOG_PID=$!

# Kick off the EM. The actual brief is in agents/em/AGENTS.md; this message
# just nudges the EM to start its BOOTSTRAP ritual.
docker exec openclaw-run-1prime openclaw agent --agent em \
  --message "Begin the engagement. Follow your BOOTSTRAP.md, then drive the project. You have approximately 15 minutes." \
  --json >"$SNAPSHOT_DIR/kickoff-em.json" 2>&1 || true

echo "▶ EM kicked off; agents now self-driving via heartbeat + Talk. Sleeping ${HARD_CAP_SECONDS}s…"
sleep "$HARD_CAP_SECONDS"

echo "⏱  Hard cap reached — bringing stack down."
kill "$LOG_PID" 2>/dev/null || true
docker cp openclaw-run-1prime:/root/.openclaw/agents "$SNAPSHOT_DIR/agents" 2>/dev/null || true
docker cp researcher-web-mcp-run1prime:/var/log/researcher-web "$SNAPSHOT_DIR/researcher-audit" 2>/dev/null || true
# EM keeps writing artifacts to /agents at container root (not the mounted
# workspace at /workspace/em). Until BOOTSTRAP.md is tightened to anchor on
# the workspace, snapshot /agents explicitly or these writes evaporate at
# teardown. See t5-run-1prime-open-questions.md OQ-2.
docker cp openclaw-run-1prime:/agents "$SNAPSHOT_DIR/em-writes" 2>/dev/null || true
docker compose --env-file .env.run1prime -f docker-compose.2agent.yml down

echo "▶ Cost rollup:"
uv run --no-project --python 3.13 scrape-usage.py "$SNAPSHOT_DIR" 2>&1 | tee "$SNAPSHOT_DIR/cost-rollup.txt"
echo "✓ Snapshot at $SNAPSHOT_DIR"
