"""Show the recent reasoning trace for an agent (em, researcher, analyst-a, analyst-b).

Usage:
    python3 show-trace.py em            # last 30 messages from EM agent
    python3 show-trace.py researcher 60 # last 60 messages from Researcher

Pulls from Letta's `GET /v1/agents/<id>/messages` on the role's own Letta.
Reads agent_id + letta_url out of run-2-agents.local. Token from letta.local.
Output groups reasoning + tool_call + tool_return chronologically.
"""

import base64
import json
import pathlib
import sys
import urllib.request

SPIKE = pathlib.Path(__file__).parent
LETTA_TOKEN = (SPIKE / "letta.local").read_text().strip()
AGENTS = json.loads((SPIKE / "run-2-agents.local").read_text())

WIDTH = 110


def http_get(letta_url: str, path: str):
    req = urllib.request.Request(
        f"{letta_url}{path}",
        headers={"Authorization": f"Bearer {LETTA_TOKEN}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def truncate(s: str, n: int) -> str:
    s = (s or "").replace("\n", "\\n")
    return s if len(s) <= n else s[:n] + "…"


def render(messages: list[dict]) -> None:
    for m in messages:
        t = m.get("message_type")
        date = (m.get("date") or "")[11:19]  # HH:MM:SS
        if t == "reasoning_message":
            text = m.get("reasoning", "") or ""
            print(f"[{date}] reasoning: {truncate(text, WIDTH)}")
        elif t == "user_message":
            text = m.get("content", "") or ""
            if isinstance(text, list):
                text = " ".join(c.get("text", "") for c in text if isinstance(c, dict))
            name = m.get("name") or "user"
            print(f"[{date}] USER ({name}): {truncate(str(text), WIDTH)}")
        elif t == "tool_call_message":
            tc = m.get("tool_call", {})
            name = tc.get("name", "?")
            args = tc.get("arguments", "")
            print(f"[{date}] tool_call  {name}({truncate(args, WIDTH - 30)})")
        elif t == "tool_return_message":
            ret = m.get("tool_return", "")
            status = m.get("status", "?")
            print(f"[{date}] tool_ret  status={status}  {truncate(str(ret), WIDTH - 30)}")
        elif t == "assistant_message":
            text = m.get("content", "") or ""
            if isinstance(text, list):
                text = " ".join(c.get("text", "") for c in text if isinstance(c, dict))
            print(f"[{date}] ASSISTANT: {truncate(str(text), WIDTH)}")
        elif t == "system_message":
            text = m.get("content", "")
            print(f"[{date}] system: {truncate(str(text), WIDTH)}")
        else:
            print(f"[{date}] {t}: {list(m.keys())}")


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in AGENTS:
        print(f"Usage: {sys.argv[0]} {{{ '|'.join(AGENTS) }}} [limit=30]", file=sys.stderr)
        return 2
    role = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    info = AGENTS[role]
    agent_id = info["agent_id"]
    letta_url = info["letta_url"]
    msgs = http_get(letta_url, f"/v1/agents/{agent_id}/messages?limit={limit}")
    # Letta returns oldest-first when sorted by date; sort just to be safe.
    msgs = sorted(msgs, key=lambda m: m.get("date", ""))
    print(f"# {role}  ({agent_id})  on {letta_url}")
    print(f"# {len(msgs)} messages (most recent first cap = {limit})")
    print("-" * WIDTH)
    render(msgs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
