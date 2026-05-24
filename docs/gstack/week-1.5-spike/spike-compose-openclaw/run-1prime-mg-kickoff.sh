#!/usr/bin/env bash
# Run 1' rerun (multi-gateway) — 2 OpenClaw gateways + Talk bridge, hard 15-min cap.
#
# Differences vs run-1prime-kickoff.sh:
#   * Boots docker-compose.2agent-multigateway.yml (em gateway + researcher
#     gateway + bridge sidecar).
#   * Kickoff is sent as a Talk message in #team from the admin user, then the
#     bridge delivers it to em — same path real traffic would take. (Old
#     kickoff did `docker exec ... openclaw agent` directly; that bypassed
#     the bridge, which we now want to exercise end-to-end.)
#   * The engagement spec is baked into the kickoff message (F-O-6 fix).
#   * Snapshot teardown grabs both gateways' agents/, bridge state, and the
#     final Talk transcript.

set -euo pipefail
cd "$(dirname "$0")"

HARD_CAP_SECONDS="${HARD_CAP_SECONDS:-900}"
SNAPSHOT_DIR="./run-1prime-mg-snapshot/$(date -u +%Y-%m-%dT%H-%M-%SZ)"
LOG_FILE="$SNAPSHOT_DIR/run.log"

[ -r .env.run1prime ] || { echo "missing .env.run1prime"; exit 1; }

mkdir -p "$SNAPSHOT_DIR"
echo "▶ Run 1' multi-gateway kickoff at $(date -u +%FT%TZ)"
echo "  snapshot dir: $SNAPSHOT_DIR"

COMPOSE="docker compose --env-file .env.run1prime -f docker-compose.2agent-multigateway.yml"

# Clean slate.
$COMPOSE down -v >/dev/null 2>&1 || true

# Build + up.
$COMPOSE up -d --build

# Phase 1 — nextcloud-init must exit 0 (cold boot ~2-4 min).
echo "▶ Waiting for nextcloud-init (up to 6 min)…"
for i in $(seq 1 360); do
  state=$(docker inspect -f '{{.State.Status}}/{{.State.ExitCode}}' \
                nextcloud-init-run1prime-mg 2>/dev/null || echo unknown)
  case "$state" in
    exited/0) echo "✓ nextcloud-init OK"; break ;;
    exited/*) echo "✗ nextcloud-init failed: $state"
              docker logs nextcloud-init-run1prime-mg | tail -50; exit 1 ;;
  esac
  sleep 1
done

# Phase 2 — both gateways must reach "[gateway] ready".
for G in openclaw-em-run1prime-mg openclaw-researcher-run1prime-mg; do
  echo "▶ Waiting for $G gateway ready…"
  for i in $(seq 1 120); do
    if docker logs "$G" 2>&1 | grep -q '\[gateway\] ready'; then
      echo "✓ $G ready (${i}s)"
      break
    fi
    sleep 1
  done
  docker logs "$G" 2>&1 | grep -q '\[gateway\] ready' \
    || { echo "✗ $G never reported ready"; docker logs "$G" | tail -30; exit 1; }
done

# Phase 3 — bridge must be running.
sleep 3
if ! docker ps --filter name=nextcloud-talk-bridge-run1prime-mg --filter status=running -q | grep -q .; then
  echo "✗ bridge not running"; docker logs nextcloud-talk-bridge-run1prime-mg | tail -30; exit 1
fi
echo "✓ bridge running"

# Stream logs in background.
docker logs -f openclaw-em-run1prime-mg               >"$SNAPSHOT_DIR/gateway-em.log" 2>&1 &
LOG_PIDS=($!)
docker logs -f openclaw-researcher-run1prime-mg       >"$SNAPSHOT_DIR/gateway-rx.log" 2>&1 &
LOG_PIDS+=($!)
docker logs -f nextcloud-talk-bridge-run1prime-mg     >"$SNAPSHOT_DIR/bridge.log" 2>&1 &
LOG_PIDS+=($!)

# Live-snapshot loop for /agents writes (F-O-2 — agents write outside workspace mount).
(
  while docker ps --filter name=openclaw-em-run1prime-mg --filter status=running -q | grep -q .; do
    mkdir -p "$SNAPSHOT_DIR/em-writes-live" "$SNAPSHOT_DIR/rx-writes-live"
    docker cp openclaw-em-run1prime-mg:/agents/.            "$SNAPSHOT_DIR/em-writes-live/" 2>/dev/null || true
    docker cp openclaw-researcher-run1prime-mg:/agents/.    "$SNAPSHOT_DIR/rx-writes-live/" 2>/dev/null || true
    sleep 60
  done
) >/dev/null 2>&1 &
LOG_PIDS+=($!)

# Kick off by posting the engagement brief as the admin user into #team.
# The bridge will deliver it to em.
echo "▶ Posting kickoff into #team (admin → bridge → em)…"
NC_ADMIN_USER=$(grep ^NC_ADMIN_USER= .env.run1prime | cut -d= -f2-)
NC_ADMIN_PASSWORD=$(grep ^NC_ADMIN_PASSWORD= .env.run1prime | cut -d= -f2-)
EM_PASSWORD=$(grep ^NEXTCLOUD_PASSWORD_EM= .env.run1prime | cut -d= -f2-)

TEAM_TOKEN=$(docker run --rm --network spike-compose-openclaw_run1prime-mg alpine:3.20 sh -c \
  "apk add --no-cache curl jq >/dev/null && curl -s 'http://nextcloud/ocs/v2.php/apps/spreed/api/v4/room' -H 'OCS-APIRequest: true' -H 'Accept: application/json' -u em:$EM_PASSWORD | jq -r '.ocs.data[] | select(.name==\"team\") | .token'")
echo "  #team token: $TEAM_TOKEN"

# Engagement brief, baked in (fix for F-O-6).
KICKOFF_BRIEF='@em Engagement brief: US mid-market vertical-SaaS firm ($1-10M ARR), product is operational SaaS for SMB logistics operators (3PLs, freight forwarders, asset-light dispatch/billing/doc automation). CEO is asking: should we enter Indonesia as a direct market in 2026 — yes/no, and if yes how (direct, partner-led, channel, JV, acquisition)? Deliverable: a decision brief by the time we wrap. Working hard cap 15 minutes from now. Team: you (EM, synthesis) and @researcher (sourced evidence). Drive the engagement.'

docker run --rm --network spike-compose-openclaw_run1prime-mg alpine:3.20 sh -c \
  "apk add --no-cache curl >/dev/null && curl -sf -u '$NC_ADMIN_USER:$NC_ADMIN_PASSWORD' -H 'OCS-APIRequest: true' -H 'Accept: application/json' -X POST 'http://nextcloud/ocs/v2.php/apps/spreed/api/v1/chat/$TEAM_TOKEN' --data-urlencode 'message=$KICKOFF_BRIEF'" \
  > "$SNAPSHOT_DIR/kickoff-post.json" 2>&1
echo "✓ kickoff posted to #team"

echo "▶ Agents now self-driving via Talk + bridge. Sleeping ${HARD_CAP_SECONDS}s…"
sleep "$HARD_CAP_SECONDS"

echo "⏱  Hard cap reached — bringing stack down."

# Snapshot before teardown.
docker cp openclaw-em-run1prime-mg:/root/.openclaw/agents              "$SNAPSHOT_DIR/agents-em" 2>/dev/null || true
docker cp openclaw-researcher-run1prime-mg:/root/.openclaw/agents      "$SNAPSHOT_DIR/agents-rx" 2>/dev/null || true
docker cp openclaw-em-run1prime-mg:/agents                             "$SNAPSHOT_DIR/em-writes" 2>/dev/null || true
docker cp openclaw-researcher-run1prime-mg:/agents                     "$SNAPSHOT_DIR/rx-writes" 2>/dev/null || true
docker cp nextcloud-talk-bridge-run1prime-mg:/state/bridge-state.json  "$SNAPSHOT_DIR/bridge-state.json" 2>/dev/null || true
docker cp researcher-web-mcp-run1prime-mg:/var/log/researcher-web      "$SNAPSHOT_DIR/researcher-audit" 2>/dev/null || true

# Talk transcripts for both rooms.
for ROOM in team EM-Researcher; do
  TOKEN=$(docker run --rm --network spike-compose-openclaw_run1prime-mg alpine:3.20 sh -c \
    "apk add --no-cache curl jq >/dev/null && curl -s 'http://nextcloud/ocs/v2.php/apps/spreed/api/v4/room' -H 'OCS-APIRequest: true' -H 'Accept: application/json' -u em:$EM_PASSWORD | jq -r '.ocs.data[] | select(.name==\"$ROOM\") | .token'")
  docker run --rm --network spike-compose-openclaw_run1prime-mg alpine:3.20 sh -c \
    "apk add --no-cache curl jq >/dev/null && curl -s 'http://nextcloud/ocs/v2.php/apps/spreed/api/v1/chat/$TOKEN?lookIntoFuture=0&limit=200' -H 'OCS-APIRequest: true' -H 'Accept: application/json' -u em:$EM_PASSWORD | jq -r '.ocs.data | reverse | .[] | \"[\(.timestamp|todate)] \(.actorDisplayName): \(.message)\"'" \
    > "$SNAPSHOT_DIR/talk-$ROOM.txt" 2>&1
done

for pid in "${LOG_PIDS[@]}"; do kill "$pid" 2>/dev/null || true; done

$COMPOSE down

# Merge the two gateway snapshots into a single `agents/` tree so scrape-usage.py
# (which globs `agents/*/sessions/*.jsonl`) sees both.
mkdir -p "$SNAPSHOT_DIR/agents"
[ -d "$SNAPSHOT_DIR/agents-em/em" ] && cp -r "$SNAPSHOT_DIR/agents-em/em" "$SNAPSHOT_DIR/agents/" 2>/dev/null || true
[ -d "$SNAPSHOT_DIR/agents-rx/researcher" ] && cp -r "$SNAPSHOT_DIR/agents-rx/researcher" "$SNAPSHOT_DIR/agents/" 2>/dev/null || true

echo "▶ Cost rollup:"
uv run --no-project --python 3.13 scrape-usage.py "$SNAPSHOT_DIR" 2>&1 | tee "$SNAPSHOT_DIR/cost-rollup.txt"
echo "✓ Snapshot at $SNAPSHOT_DIR"
