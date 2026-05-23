#!/usr/bin/env bash
# Provision the analyst-b Nextcloud user and emit an app token for
# nextcloud-mcp-analyst-b.
#
# Idempotent:
#   - If the user already exists in Nextcloud, the user:add step is skipped.
#   - If ./analyst-b-token.local is non-empty, the app-password step is skipped.
#
# Prereqs:
#   - Nextcloud is up: `./bring-up.sh up -d nc-db nc-redis nextcloud`.
#   - Admin OCS works: $NEXTCLOUD_ADMIN_PASSWORD (env) matches the running
#     admin pw, OR fall through to the sentinel "__smoke__".
#
# Post: analyst-b-token.local exists. Bring up the sidecar with:
#   ./bring-up.sh up -d nextcloud-mcp-analyst-b

set -euo pipefail
cd "$(dirname "$0")"

USER=analyst-b
DISPLAY_NAME="Senior Analyst B"
SENTINEL_PW="analyst-b-pw-smoke"   # rotate before non-spike use; see env-manifest precedent
TOKEN_FILE=analyst-b-token.local
ADMIN_PW="${NEXTCLOUD_ADMIN_PASSWORD:-__smoke__}"

echo "==> checking if user ${USER} exists in Nextcloud"
if docker compose exec -T --user www-data nextcloud php occ user:list --output=json \
        | grep -q "\"${USER}\""; then
    echo "    user ${USER} already exists; skipping create"
else
    echo "    creating user ${USER}"
    OC_PASS="${SENTINEL_PW}" docker compose exec -T --user www-data \
        -e OC_PASS \
        nextcloud \
        php occ user:add --password-from-env --display-name="${DISPLAY_NAME}" "${USER}"
fi

echo "==> generating app password for ${USER}"
if [ -s "${TOKEN_FILE}" ]; then
    bytes=$(wc -c < "${TOKEN_FILE}")
    echo "    ${TOKEN_FILE} already populated (${bytes} bytes); skipping"
else
    # OCS /core/getapppassword: must auth AS the user (basic auth, the user's
    # real password), not as admin. Returns the app password in the response
    # body. We request JSON for easy parsing.
    response=$(curl -fsS \
        -u "${USER}:${SENTINEL_PW}" \
        -H "OCS-APIRequest: true" \
        -H "Accept: application/json" \
        "http://127.0.0.1:8080/ocs/v2.php/core/getapppassword")

    # Pull .ocs.data.apppassword. Avoid jq dependency — use python.
    token=$(python3 -c "import json, sys; print(json.loads(sys.argv[1])['ocs']['data']['apppassword'])" "${response}")

    if [ -z "${token}" ]; then
        echo "    ERROR: empty token in OCS response: ${response}" >&2
        exit 1
    fi

    printf '%s' "${token}" > "${TOKEN_FILE}"
    chmod 600 "${TOKEN_FILE}"
    echo "    wrote ${TOKEN_FILE} ($(wc -c < "${TOKEN_FILE}") bytes)"
fi

echo
echo "done. Next steps:"
echo "  ./bring-up.sh up -d nextcloud-mcp-analyst-b"
echo "  python3 setup-run-2-talk-rooms.py    # creates 5 DM rooms + adds analysts to #team"
