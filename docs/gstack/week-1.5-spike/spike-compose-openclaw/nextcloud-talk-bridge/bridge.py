"""
Nextcloud Talk → OpenClaw bridge.

Polls each configured identity's joined Talk rooms via OCS long-poll and, on
each new message *not authored by the identity itself*, invokes
`openclaw agent` inside that identity's gateway container via docker exec.

This is the per-identity delivery path that the bundled @openclaw/nextcloud-talk
channel plugin cannot provide (its bot model is single-identity-per-gateway and
uses webhook bot accounts, not regular Nextcloud users — which would block
human takeover, per the Run 1' findings).

Spike scope: simple, synchronous, one thread per identity. Each thread loops:
  - list rooms
  - for each room: long-poll lookIntoFuture=1 timeout=20s with last-seen id
  - on returned messages: skip own, deliver others, advance last-seen
  - retry on transient network errors with bounded backoff

State (one JSON file under /state) survives restarts. Schema:
  {
    "<user>": {
      "<room-token>": { "lastKnownMessageId": <int> }
    }
  }
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import httpx

STATE_FILE = Path(os.environ.get("BRIDGE_STATE_FILE", "/state/bridge-state.json"))
NC_BASE = os.environ["NEXTCLOUD_HOST"].rstrip("/")
POLL_TIMEOUT_S = int(os.environ.get("BRIDGE_POLL_TIMEOUT", "20"))
LIST_ROOMS_EVERY_S = int(os.environ.get("BRIDGE_LIST_ROOMS_EVERY", "60"))
DELIVER_TIMEOUT_S = int(os.environ.get("BRIDGE_DELIVER_TIMEOUT", "180"))

OCS_HEADERS = {"OCS-APIRequest": "true", "Accept": "application/json"}

state_lock = threading.Lock()


def log(msg: str) -> None:
    print(f"[{time.strftime('%FT%TZ', time.gmtime())}] {msg}", flush=True)


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True))
    tmp.replace(STATE_FILE)


def list_rooms(client: httpx.Client) -> list[dict]:
    r = client.get(f"{NC_BASE}/ocs/v2.php/apps/spreed/api/v4/room", headers=OCS_HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()["ocs"]["data"]


def long_poll_room(client: httpx.Client, token: str, last_id: int) -> list[dict]:
    params = {
        "lookIntoFuture": 1,
        "timeout": POLL_TIMEOUT_S,
        "lastKnownMessageId": last_id,
        "includeLastKnown": 0,
        "limit": 50,
    }
    r = client.get(
        f"{NC_BASE}/ocs/v2.php/apps/spreed/api/v1/chat/{token}",
        headers=OCS_HEADERS,
        params=params,
        timeout=POLL_TIMEOUT_S + 10,
    )
    if r.status_code == 304:
        return []
    r.raise_for_status()
    data = r.json().get("ocs", {}).get("data", [])
    # Talk returns oldest→newest when lookIntoFuture=1; keep that order.
    return data if isinstance(data, list) else []


def deliver(container: str, agent_id: str, session_id: str, body: str) -> None:
    """docker exec into the agent's gateway and run an openclaw agent turn."""
    cmd = [
        "docker", "exec", container,
        "openclaw", "agent",
        "--agent", agent_id,
        "--session-id", session_id,
        "--message", body,
        "--json",
    ]
    log(f"  → docker exec {container} agent={agent_id} session={session_id} body[:80]={body[:80]!r}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=DELIVER_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        log(f"  ✗ delivery timeout after {DELIVER_TIMEOUT_S}s — message will be re-delivered next poll")
        raise
    if result.returncode != 0:
        log(f"  ✗ openclaw agent rc={result.returncode}")
        log(f"    stderr tail: {result.stderr[-400:]!r}")
        raise RuntimeError(f"openclaw agent failed rc={result.returncode}")
    log(f"  ✓ delivered ({len(result.stdout)} bytes back from gateway)")


def run_identity(identity: dict, state: dict) -> None:
    user = identity["user"]
    password = identity["password"]
    container = identity["container"]
    agent_id = identity["agent_id"]
    log(f"▶ identity={user} container={container} agent={agent_id} — starting")

    state.setdefault(user, {})

    with httpx.Client(auth=(user, password)) as client:
        last_room_list_at = 0.0
        rooms: list[dict] = []
        while True:
            now = time.time()
            if now - last_room_list_at > LIST_ROOMS_EVERY_S or not rooms:
                try:
                    rooms = list_rooms(client)
                    last_room_list_at = now
                    log(f"[{user}] rooms: {', '.join(r['name'] + '(' + r['token'] + ')' for r in rooms) or 'none'}")
                except Exception as e:
                    log(f"[{user}] list_rooms failed: {e!r} — retrying in 5s")
                    time.sleep(5)
                    continue

            for room in rooms:
                token = room["token"]
                # First sight of a room: anchor at the current head from list_rooms
                # rather than 0, otherwise the bridge replays the room's entire
                # backlog. Nextcloud auto-provisions a "Talk updates ✅" room for
                # every new user, pre-populated with ~20 release-notes messages —
                # without this anchor every fresh user wastes tokens on those.
                if token not in state[user]:
                    head = int((room.get("lastMessage") or {}).get("id") or 0)
                    state[user][token] = {"lastKnownMessageId": head}
                    log(f"[{user}] new room '{room.get('displayName', token)}' ({token}) — anchored at head id={head}")
                    save_state(state)
                room_state = state[user][token]
                last_id = int(room_state["lastKnownMessageId"])
                try:
                    msgs = long_poll_room(client, token, last_id)
                except httpx.HTTPError as e:
                    log(f"[{user}] poll {token} HTTP error: {e!r}")
                    time.sleep(2)
                    continue
                except Exception as e:
                    log(f"[{user}] poll {token} unexpected: {e!r}")
                    time.sleep(2)
                    continue

                if not msgs:
                    continue

                for msg in msgs:
                    msg_id = int(msg["id"])
                    actor = msg.get("actorId", "")
                    actor_type = msg.get("actorType", "")
                    body = msg.get("message", "")
                    system_message = msg.get("systemMessage", "")

                    # Skip system events ("X added Y", "conversation created").
                    if system_message:
                        with state_lock:
                            room_state["lastKnownMessageId"] = max(last_id, msg_id)
                            save_state(state)
                        last_id = max(last_id, msg_id)
                        continue

                    # Skip our own posts.
                    if actor_type == "users" and actor == user:
                        with state_lock:
                            room_state["lastKnownMessageId"] = max(last_id, msg_id)
                            save_state(state)
                        last_id = max(last_id, msg_id)
                        continue

                    # Skip empty bodies (file shares with no caption, etc.).
                    if not body:
                        with state_lock:
                            room_state["lastKnownMessageId"] = max(last_id, msg_id)
                            save_state(state)
                        last_id = max(last_id, msg_id)
                        continue

                    session_id = f"bridge-{agent_id}-{token}"
                    actor_display = msg.get("actorDisplayName", actor)
                    framed = f"[from {actor_display} in {room['displayName']}] {body}"

                    try:
                        deliver(container, agent_id, session_id, framed)
                    except Exception as e:
                        log(f"[{user}] deliver failed: {e!r} — NOT advancing lastKnownMessageId so it retries")
                        # Sleep so we don't hammer the gateway during a failure window.
                        time.sleep(5)
                        # Break room loop, top of outer loop will re-poll.
                        break

                    # Advance only on success.
                    with state_lock:
                        room_state["lastKnownMessageId"] = msg_id
                        save_state(state)
                    last_id = msg_id


def main() -> int:
    config_path = Path(os.environ.get("BRIDGE_CONFIG", "/etc/bridge/identities.json"))
    if not config_path.exists():
        log(f"BRIDGE_CONFIG file missing: {config_path}")
        return 2

    identities = json.loads(config_path.read_text())
    log(f"loaded {len(identities)} identities from {config_path}")

    state = load_state()
    log(f"loaded state for {len(state)} users: keys={list(state.keys())}")

    threads = []
    for ident in identities:
        t = threading.Thread(target=run_identity, args=(ident, state), name=f"bridge-{ident['user']}", daemon=True)
        t.start()
        threads.append(t)

    # Block forever; threads are daemons and will die with the process.
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        log("SIGINT — exiting")
        return 0


if __name__ == "__main__":
    sys.exit(main())
