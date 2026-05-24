#!/usr/bin/env bash
# nextcloud-init sidecar — runs once, exits after provisioning.
#
# Idempotent: re-running with existing state is safe. POSTs may return
# 409 "user exists"/"room exists" — those are treated as success.

set -euo pipefail

ADMIN="${NC_ADMIN_USER:-admin}"
PASS="${NC_ADMIN_PASSWORD:?NC_ADMIN_PASSWORD missing}"
BASE="${NEXTCLOUD_HOST:-http://nextcloud}"

EM_USER="${NEXTCLOUD_USERNAME_EM:-em}"
EM_PWD="${NEXTCLOUD_PASSWORD_EM:?NEXTCLOUD_PASSWORD_EM missing}"
RX_USER="${NEXTCLOUD_USERNAME_RESEARCHER:-researcher}"
RX_PWD="${NEXTCLOUD_PASSWORD_RESEARCHER:?NEXTCLOUD_PASSWORD_RESEARCHER missing}"

H_OCS=(-H 'OCS-APIRequest: true' -H 'Accept: application/json')

echo "▶ Waiting for Nextcloud at ${BASE}…"
until curl -sf "${BASE}/status.php" >/dev/null 2>&1; do sleep 2; done
echo "  …reachable. Waiting for installed=true…"
until curl -sf "${BASE}/status.php" | grep -q '"installed":true'; do sleep 2; done
echo "✓ Nextcloud installed"

echo "▶ Waiting for Talk (spreed) app to be enabled (postinstall hook)…"
for i in $(seq 1 60); do
  if curl -sf -u "${ADMIN}:${PASS}" "${H_OCS[@]}" \
       "${BASE}/ocs/v2.php/apps/spreed/api/v4/room" >/dev/null 2>&1; then
    echo "✓ Talk reachable"; break
  fi
  sleep 2
done

create_user () {
  local uid="$1" pwd="$2"
  echo "▶ Creating user ${uid}"
  resp=$(curl -sf -u "${ADMIN}:${PASS}" "${H_OCS[@]}" -X POST \
    "${BASE}/ocs/v1.php/cloud/users" \
    --data-urlencode "userid=${uid}" \
    --data-urlencode "password=${pwd}" 2>&1) || true
  if echo "$resp" | grep -q '"statuscode":102'; then
    echo "  user already exists — resetting password"
    curl -sf -u "${ADMIN}:${PASS}" "${H_OCS[@]}" -X PUT \
      "${BASE}/ocs/v1.php/cloud/users/${uid}" \
      --data-urlencode "key=password" --data-urlencode "value=${pwd}" >/dev/null
  fi
  echo "  ✓ ${uid}"
}

create_room () {
  local user="$1" pwd="$2" name="$3" type="$4"   # type: 2=group, 1=one-to-one
  # Status echoes go to stderr so the function's stdout is only the room token,
  # which lets us safely capture it via $(create_room …).
  echo "▶ Creating room '${name}' as ${user}" >&2
  resp=$(curl -sf -u "${user}:${pwd}" "${H_OCS[@]}" -X POST \
    "${BASE}/ocs/v2.php/apps/spreed/api/v4/room" \
    --data-urlencode "roomType=${type}" \
    --data-urlencode "roomName=${name}")
  token=$(echo "$resp" | jq -r '.ocs.data.token')
  echo "  token=${token}" >&2
  echo "$token"
}

add_participant () {
  local owner_user="$1" owner_pwd="$2" room_token="$3" new_uid="$4"
  echo "▶ Adding ${new_uid} to room ${room_token}"
  curl -sf -u "${owner_user}:${owner_pwd}" "${H_OCS[@]}" -X POST \
    "${BASE}/ocs/v2.php/apps/spreed/api/v4/room/${room_token}/participants" \
    --data-urlencode "newParticipant=${new_uid}" \
    --data-urlencode "source=users" >/dev/null
}

# 1. Users
create_user "${EM_USER}" "${EM_PWD}"
create_user "${RX_USER}" "${RX_PWD}"

# 2. Rooms — #team (group, both members + admin as operator) + EM-Researcher
#    Admin joins #team so external kickoff/operator messages can be posted as
#    a regular Talk participant (mirrors a human operator in real deployments).
TEAM_TOKEN=$(create_room "${EM_USER}" "${EM_PWD}" "team" 2)
add_participant "${EM_USER}" "${EM_PWD}" "${TEAM_TOKEN}" "${RX_USER}"
add_participant "${EM_USER}" "${EM_PWD}" "${TEAM_TOKEN}" "${ADMIN}"

EM_RX_TOKEN=$(create_room "${EM_USER}" "${EM_PWD}" "EM-Researcher" 2)
add_participant "${EM_USER}" "${EM_PWD}" "${EM_RX_TOKEN}" "${RX_USER}"

# 3. Persist room tokens so agents can rediscover them via MCP nc_talk_list_rooms
#    and operator scripts can grep them post-run.
mkdir -p /provision-output
cat > /provision-output/rooms.json <<EOF
{
  "team":          { "name": "#team",         "token": "${TEAM_TOKEN}" },
  "em-researcher": { "name": "EM-Researcher", "token": "${EM_RX_TOKEN}" }
}
EOF
echo "✓ provision complete — rooms.json written to /provision-output"
cat /provision-output/rooms.json
