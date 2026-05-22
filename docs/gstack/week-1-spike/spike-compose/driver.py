"""Spike-time message relay between Nextcloud Talk and per-agent Letta servers.

Purpose: in v1, Roster CLI polls Talk and triggers agents on new messages. The
spike doesn't have that runtime yet, so this script stands in for it for the
duration of Run 1 / Run 2. It is not part of v1 — kill it after the run.

Loop (default 30s tick):
  For each watched room:
    Fetch messages > last_seen_id for that room (admin OCS, includes all actors).
    For each agent that's a participant of the room:
      Among those new messages, keep ones whose actor != that agent.
      If any remain, POST one wake to the agent's Letta /v1/agents/<id>/messages
      with a "new-message" digest (room + sender + truncated body, one line per
      new message, capped at ~6 lines). Update last_seen_id per (room, agent).

State file: `driver-state.local` — gitignored; just last-seen IDs per (room, agent).
Log file:  `driver.log` — every wake event + every poll error.

Cap: 1h hard wall (Run 1 cap). Sigterm / KeyboardInterrupt also stops cleanly.
"""

import json
import os
import pathlib
import signal
import sys
import time
import urllib.error
import urllib.request

SPIKE = pathlib.Path(__file__).parent
LETTA_TOKEN = (SPIKE / "letta.local").read_text().strip()
AGENTS = json.loads((SPIKE / "run1-agents.local").read_text())
NEXTCLOUD = "http://127.0.0.1:8080"
# Admin pw is the Run-1 sentinel by default ("__smoke__", documented in
# t5-env-manifest.md "Change log" under "Pre-Run 1 (post-swap)"). Override at
# runtime via the NEXTCLOUD_ADMIN_PASSWORD env var (e.g., sourced by
# bring-up.sh from .env or a sibling .local file). Must be rotated before
# anything past the spike.
ADMIN_AUTH = ("admin", os.environ.get("NEXTCLOUD_ADMIN_PASSWORD", "__smoke__"))
STATE_PATH = SPIKE / "driver-state.local"
LOG_PATH = SPIKE / "driver.log"

# Rooms to relay, with the set of participant agents that should be woken.
# Room tokens come from t5-env-manifest.md "Talk rooms" line. Founder (operator)
# is not an agent — only the agent participants are listed below.
ROOMS = [
    {"token": "vzyiva4u", "name": "#team",         "agent_actors": {"em", "researcher"}},
    {"token": "z4n3425w", "name": "EM-Researcher", "agent_actors": {"em", "researcher"}},
]

POLL_INTERVAL_S = 30
HARD_CAP_S = int(os.environ.get("HARD_CAP_S", "3600"))  # 1h default; overridable for time-boxed re-runs


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(line: str) -> None:
    with LOG_PATH.open("a") as f:
        f.write(f"{now()} | {line}\n")
    print(f"{now()} | {line}", flush=True)


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text())


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def ocs_get_chat(token: str, last_id: int) -> list[dict]:
    """Fetch chat messages with id > last_id. Returns oldest-first."""
    url = (
        f"{NEXTCLOUD}/ocs/v2.php/apps/spreed/api/v1/chat/{token}"
        f"?lookIntoFuture=0&limit=50&setReadMarker=0"
    )
    import base64
    user, pw = ADMIN_AUTH
    auth = "Basic " + base64.b64encode(f"{user}:{pw}".encode()).decode()
    req = urllib.request.Request(
        url,
        headers={
            "OCS-APIRequest": "true",
            "Accept": "application/json",
            "Authorization": auth,
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = json.loads(resp.read())
    msgs = body.get("ocs", {}).get("data", [])
    # OCS returns newest-first; we want chronological + filter by id > last_id.
    msgs = sorted(msgs, key=lambda m: m.get("id", 0))
    return [m for m in msgs if int(m.get("id", 0)) > last_id and not m.get("systemMessage")]


def wake_agent(agent_id: str, letta_url: str, digest: str) -> tuple[int, str]:
    body = {
        "messages": [{"role": "user", "content": digest, "name": "founder"}],
    }
    req = urllib.request.Request(
        f"{letta_url}/v1/agents/{agent_id}/messages",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {LETTA_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            payload = resp.read()
            return resp.status, payload.decode()[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]
    except Exception as e:  # pragma: no cover
        return 0, repr(e)[:200]


def build_digest(room_name: str, msgs: list[dict]) -> str:
    """Compact one-line-per-message digest. Cap at 6 lines."""
    lines = []
    for m in msgs[:6]:
        actor = m.get("actorId", "?")
        body = (m.get("message") or "").replace("\n", " ").strip()
        if len(body) > 200:
            body = body[:200] + "…"
        lines.append(f"- {actor}: {body}")
    extra = ""
    if len(msgs) > 6:
        extra = f"\n(+{len(msgs) - 6} more — use talk_get_messages to read the rest.)"
    return (
        f"New messages in {room_name} since you last acted. "
        f"Check the room and reply if any are addressed to you:\n"
        + "\n".join(lines)
        + extra
    )


_stop = False


def _sig(*_):
    global _stop
    _stop = True
    log("signal received; stopping after current tick.")


def main() -> int:
    signal.signal(signal.SIGINT, _sig)
    signal.signal(signal.SIGTERM, _sig)
    state = load_state()
    started = time.time()
    log(f"driver started — watching {[r['name'] for r in ROOMS]} for {list(AGENTS)} (cap {HARD_CAP_S}s).")
    tick = 0
    while not _stop:
        tick += 1
        if time.time() - started > HARD_CAP_S:
            log("hard cap reached; stopping.")
            break
        for room in ROOMS:
            token, room_name, room_agents = room["token"], room["name"], room["agent_actors"]
            for agent_actor in room_agents:
                if agent_actor not in AGENTS:
                    continue  # this run doesn't include that agent
                key = f"{token}:{agent_actor}"
                last_id = int(state.get(key, 0))
                try:
                    new_msgs = ocs_get_chat(token, last_id)
                except Exception as e:
                    log(f"poll error {room_name} for {agent_actor}: {e!r}")
                    continue
                # Drop messages authored by the agent itself.
                relevant = [m for m in new_msgs if m.get("actorId") != agent_actor]
                if new_msgs:
                    state[key] = max(int(m.get("id", 0)) for m in new_msgs)
                if not relevant:
                    continue
                digest = build_digest(room_name, relevant)
                info = AGENTS[agent_actor]
                log(f"wake {agent_actor} — {len(relevant)} new msg(s) in {room_name} (ids: {[m.get('id') for m in relevant]})")
                status, snippet = wake_agent(info["agent_id"], info["letta_url"], digest)
                log(f"  -> letta HTTP {status} ({snippet!r})")
                save_state(state)
        # Sleep between ticks; check stop signal often.
        for _ in range(POLL_INTERVAL_S):
            if _stop:
                break
            time.sleep(1)
    save_state(state)
    log("driver stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
