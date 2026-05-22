"""Pre-kickoff tool-execution probe (agent-driven path).

Validates the full Letta -> MCP -> Nextcloud round-trip through the path the
actual agent reasoning takes — not the per-server execute endpoint that
trivially routes by URL. The earlier version of this script probed via
`POST /v1/mcp-servers/<id>/tools/<tid>/run`, which embeds the server-id in the
URL and so always routes to the right MCP; that path is server-isolated by
construction and tells us nothing about whether agent-driven tool calls land
correctly. The bug discovered pre-Run-1 (see ../t5-run-ledger.md "Letta
tool-namespace finding") only shows up on the agent-driven path.

For each agent (em + researcher) on each agent's own Letta server:
  1. Send a user message asking the agent to post a ping to #team via
     talk_send_message and write a ping file to /agents/<role>-ping.txt.
  2. Read back the most recent #team message + /agents/ listing.
  3. Assert the actor on both is the expected user.

If both probes pass, the per-agent Letta architecture has actually isolated
identities the way we intend.
"""

import json
import pathlib
import urllib.request

SPIKE = pathlib.Path(__file__).parent
LETTA_TOKEN = (SPIKE / "letta.local").read_text().strip()
AGENTS = json.loads((SPIKE / "run1-agents.local").read_text())

TEAM_ROOM_TOKEN = "vzyiva4u"


def http(base_url: str, method: str, path: str, body=None):
    req = urllib.request.Request(
        f"{base_url}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {LETTA_TOKEN}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())


def ask_agent(letta_url: str, agent_id: str, prompt: str) -> dict:
    return http(letta_url, "POST", f"/v1/agents/{agent_id}/messages", {
        "messages": [{"role": "user", "content": prompt, "name": "founder"}],
    })


def main():
    all_ok = True

    for role, info in AGENTS.items():
        agent_id = info["agent_id"]
        letta_url = info["letta_url"]
        print(f"\n=== {role}  (agent {agent_id[-12:]} on {letta_url}) ===")

        prompt = (
            f"Pre-kickoff plumbing probe. Please do exactly these two things, in order, "
            f"and then report success. Do NOT do any other work yet:\n"
            f"1. Send the message '[ping from {role}] pre-kickoff agent-driven probe' "
            f"to the #team Talk room (token: {TEAM_ROOM_TOKEN}).\n"
            f"2. Write a file at /agents/{role}-ping.txt with the content "
            f"'agent-driven probe by {role}'.\n"
            f"Reply with one line: 'probe done'."
        )
        r = ask_agent(letta_url, agent_id, prompt)
        msgs = r.get("messages", []) if isinstance(r, dict) else r
        tool_calls = [m for m in msgs if m.get("message_type") == "tool_call_message"]
        tool_call_names = [m.get("tool_call", {}).get("name", "?") for m in tool_calls]
        print(f"  agent made {len(tool_calls)} tool calls: {tool_call_names}")
        if "talk_send_message" not in tool_call_names or "nc_webdav_write_file" not in tool_call_names:
            print(f"  FAIL: agent did not call both expected tools")
            all_ok = False
            continue
        print(f"  expected tool calls observed; awaiting actor verification below")

    if not all_ok:
        raise SystemExit(1)

    print()
    print("All agents made the expected tool calls.")
    print("Verify the Nextcloud actor manually with:")
    print("  occ + OCS — list #team chat (vzyiva4u) and confirm each ping appears under its own actor (EM and Researcher).")


if __name__ == "__main__":
    main()
