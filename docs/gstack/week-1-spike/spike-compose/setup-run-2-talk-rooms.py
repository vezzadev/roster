"""Provision the Run-2 Talk rooms + add analyst participants to #team.

Creates 5 group rooms (EM-A, EM-B, A-B, A-Researcher, B-Researcher) via the
Spreed v4 OCS API as admin, adds the right participants to each, and writes
the resulting tokens into ./rooms.local so driver.py can consume them.

Also ensures analyst-a + analyst-b are members of the existing #team room
(token from rooms.local.example or current rooms.local — the existing
ygeug4an from Run 1-anthropic-direct).

Idempotent:
  - If rooms.local already has a non-placeholder token for a room name,
    verifies the room still exists via GET /room/{token}. Reuses if alive,
    recreates if 404.
  - Participant adds are skipped if the user is already in the room (the
    OCS endpoint returns 200 either way, but we check first to keep
    output clean).

Prereqs:
  - Nextcloud is up; Talk app is installed.
  - Users em, analyst-a, analyst-b, researcher all exist (run
    provision-analyst-b.sh first if analyst-b is missing).
  - Admin password matches $NEXTCLOUD_ADMIN_PASSWORD or the sentinel.
"""

import base64
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

SPIKE = pathlib.Path(__file__).parent
ROOMS_PATH = SPIKE / "rooms.local"
EXAMPLE_PATH = SPIKE / "rooms.local.example"

NEXTCLOUD = "http://127.0.0.1:8080"
ADMIN_USER = "admin"
ADMIN_PASSWORD = os.environ.get("NEXTCLOUD_ADMIN_PASSWORD", "__smoke__")

# Rooms to provision for Run 2 (4-agent). The existing #team + EM-Researcher
# are not in this list — they're already populated in rooms.local.example with
# the Run-1-anthropic-direct tokens, so we only need to ensure analysts are
# added to #team. The other rooms below get created fresh.
RUN2_DM_ROOMS = [
    {"name": "EM-A",          "participants": ["em", "analyst-a"]},
    {"name": "EM-B",          "participants": ["em", "analyst-b"]},
    {"name": "A-B",           "participants": ["analyst-a", "analyst-b"]},
    {"name": "A-Researcher",  "participants": ["analyst-a", "researcher"]},
    {"name": "B-Researcher",  "participants": ["analyst-b", "researcher"]},
]

TEAM_ROOM_NAME = "#team"
TEAM_ADDITIONAL_MEMBERS = ["analyst-a", "analyst-b"]


def ocs(method: str, path: str, form: dict | None = None) -> dict:
    """Admin OCS call. Returns the parsed `ocs.data` block; raises on non-2xx
    or non-100 OCS status code."""
    auth = base64.b64encode(f"{ADMIN_USER}:{ADMIN_PASSWORD}".encode()).decode()
    headers = {
        "OCS-APIRequest": "true",
        "Accept": "application/json",
        "Authorization": f"Basic {auth}",
    }
    data = urllib.parse.urlencode(form).encode() if form is not None else None
    if data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(f"{NEXTCLOUD}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"  OCS {method} {path} → HTTP {e.code}: {e.read().decode()[:300]}")
    ocs_block = body.get("ocs", {})
    status = ocs_block.get("meta", {}).get("statuscode")
    if status not in (100, 200):
        raise SystemExit(f"  OCS {method} {path} → status {status}: {ocs_block.get('meta', {}).get('message')}")
    return ocs_block.get("data", {})


def get_room(token: str) -> dict | None:
    """Return room info or None if the room doesn't exist."""
    try:
        return ocs("GET", f"/ocs/v2.php/apps/spreed/api/v4/room/{token}")
    except SystemExit:
        return None


def create_room(name: str, first_invite: str) -> str:
    """Create a type=2 (group) room with `name`, inviting `first_invite`.
    Returns the new token. Additional participants are added separately."""
    data = ocs("POST", "/ocs/v2.php/apps/spreed/api/v4/room", {
        "roomType": "2",
        "roomName": name,
        "invite": first_invite,
    })
    token = data.get("token")
    if not token:
        raise SystemExit(f"  create_room({name!r}) returned no token: {data!r}")
    return token


def list_participants(token: str) -> set[str]:
    data = ocs("GET", f"/ocs/v2.php/apps/spreed/api/v4/room/{token}/participants")
    return {p.get("actorId") for p in data if p.get("actorType") == "users"}


def add_participant(token: str, user: str) -> None:
    ocs("POST", f"/ocs/v2.php/apps/spreed/api/v4/room/{token}/participants",
        {"newParticipant": user, "source": "users"})


def load_existing_rooms() -> dict[str, dict]:
    """Return name -> room dict, drawing from rooms.local if present else
    rooms.local.example. Placeholder tokens (<<...>>) are treated as absent."""
    src = ROOMS_PATH if ROOMS_PATH.exists() else EXAMPLE_PATH
    if not src.exists():
        raise SystemExit(f"  neither {ROOMS_PATH.name} nor {EXAMPLE_PATH.name} exists")
    rooms = json.loads(src.read_text())
    return {r["name"]: r for r in rooms}


def ensure_room(name: str, participants: list[str], existing: dict[str, dict]) -> str:
    """Return the token for the room with `name`, creating + populating it
    if needed. participants is the canonical set the room should hold."""
    prior = existing.get(name)
    token = prior["token"] if prior and "<<" not in prior.get("token", "") else None

    if token:
        info = get_room(token)
        if info is None:
            print(f"  {name}: prior token {token} 404s; recreating")
            token = None
        else:
            print(f"  {name}: reusing existing token {token}")

    if token is None:
        token = create_room(name, participants[0])
        print(f"  {name}: created token {token} (invited {participants[0]})")

    # Add any missing participants. The room creator (admin) may also be
    # listed — we leave admin in. We only enforce that the named participants
    # are members.
    current = list_participants(token)
    for user in participants:
        if user in current:
            continue
        try:
            add_participant(token, user)
            print(f"  {name}: added participant {user}")
        except SystemExit as e:
            # Some Talk versions return statuscode 102 ("participant already
            # in") when the user is already a participant of the parent
            # conversation. Treat as success.
            print(f"  {name}: add_participant({user}) — {e}")

    return token


def write_rooms_local(rooms_by_name: dict[str, dict]) -> None:
    # Preserve order from rooms.local.example for stable diffs.
    template = json.loads(EXAMPLE_PATH.read_text())
    out = []
    for tpl in template:
        name = tpl["name"]
        r = rooms_by_name.get(name, tpl)
        out.append({
            "name": r["name"],
            "token": r["token"],
            "agent_actors": r["agent_actors"],
        })
    ROOMS_PATH.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nwrote {ROOMS_PATH.name}")


def main() -> int:
    existing = load_existing_rooms()

    print("==> creating Run-2 DM rooms")
    rooms_by_name = dict(existing)
    for spec in RUN2_DM_ROOMS:
        token = ensure_room(spec["name"], spec["participants"], existing)
        rooms_by_name[spec["name"]] = {
            "name": spec["name"],
            "token": token,
            "agent_actors": spec["participants"],
        }

    print()
    print(f"==> adding analyst-a + analyst-b to {TEAM_ROOM_NAME}")
    team_entry = rooms_by_name.get(TEAM_ROOM_NAME)
    if not team_entry or "<<" in team_entry.get("token", ""):
        raise SystemExit(
            f"  {TEAM_ROOM_NAME} has no real token in rooms.local "
            "(expected the Run-1-anthropic-direct token ygeug4an). "
            "Populate it before re-running this script."
        )
    team_token = team_entry["token"]
    if get_room(team_token) is None:
        raise SystemExit(
            f"  {TEAM_ROOM_NAME} token {team_token} 404s — Talk rooms from "
            "the prior run were deleted. Re-run with a fresh #team token in "
            "rooms.local before continuing."
        )
    current_team = list_participants(team_token)
    for user in TEAM_ADDITIONAL_MEMBERS:
        if user in current_team:
            print(f"  {TEAM_ROOM_NAME}: {user} already a member")
            continue
        try:
            add_participant(team_token, user)
            print(f"  {TEAM_ROOM_NAME}: added {user}")
        except SystemExit as e:
            print(f"  {TEAM_ROOM_NAME}: add_participant({user}) — {e}")

    print()
    write_rooms_local(rooms_by_name)

    print()
    print("done. Sanity check:")
    print(f"  python3 -c \"import json; [print(r) for r in json.load(open('{ROOMS_PATH.name}'))]\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
