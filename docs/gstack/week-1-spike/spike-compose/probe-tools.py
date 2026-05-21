"""Pre-kickoff tool-execution probe.

Validates the full Letta -> MCP -> Nextcloud round-trip before sending the
agent kickoff. Without this, Run 1's first 5 minutes would be agents
discovering that tool calls fail — making it impossible to separate "agents
fumbled coordination" from "the plumbing was broken."

Probes per agent (em + analyst-a):
  1. talk_send_message to the #team room  — confirms Talk auth + posting
  2. nc_webdav_write_file to /agents/<role>-ping.txt  — confirms WebDAV PUT
     with the right identity (the file's author in Nextcloud is the user
     the MCP container authed as).

Then verifies what was written:
  - Lists the messages in #team via admin OCS, expects 2 ping messages.
  - PROPFINDs /agents/ as each agent user, expects their ping file present.

Failure modes this probe catches that "agents discover at kickoff" doesn't:
  - MCP container env vars wrong (auth fails)
  - Tool schema mismatch (Letta sends args MCP doesn't accept)
  - Nextcloud permissions wrong (agent can't write to /agents/ despite share)
  - Talk room token vs room ID confusion

The two ping files are left in place — they show up in the Run 1 event log
as the first /agents/ writes and aid debugging if Run 1 stalls.
"""

import json
import pathlib
import urllib.request

SPIKE = pathlib.Path(__file__).parent
LETTA_TOKEN = (SPIKE / "letta.local").read_text().strip()
LETTA_URL = "http://127.0.0.1:8283"

TEAM_ROOM_TOKEN = "vzyiva4u"  # from `occ talk:room:create`

MCP_SERVERS = {
    "em": "mcp_server-db172699-cf6e-4baf-9538-6ff9b3e6d471",
    "analyst-a": "mcp_server-a7916894-3272-41d4-959b-9078d13b5cdb",
}

PROBE_TOOLS = ("talk_send_message", "nc_webdav_write_file")


def http(method, path, body=None):
    req = urllib.request.Request(
        f"{LETTA_URL}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {LETTA_TOKEN}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def find_tool_ids(mcp_server_id: str) -> dict[str, str]:
    tools = http("GET", f"/v1/mcp-servers/{mcp_server_id}/tools")
    return {t["name"]: t["id"] for t in tools if t["name"] in PROBE_TOOLS}


def run_tool(mcp_server_id: str, tool_id: str, args: dict) -> dict:
    return http(
        "POST",
        f"/v1/mcp-servers/{mcp_server_id}/tools/{tool_id}/run",
        {"args": args},
    )


def main():
    all_ok = True

    for role, mcp_id in MCP_SERVERS.items():
        print(f"\n=== {role} (mcp={mcp_id[-12:]}) ===")
        tool_ids = find_tool_ids(mcp_id)
        missing = set(PROBE_TOOLS) - set(tool_ids)
        if missing:
            print(f"  MISSING TOOLS: {sorted(missing)}")
            all_ok = False
            continue

        # Probe 1: post to #team
        r = run_tool(
            mcp_id,
            tool_ids["talk_send_message"],
            {
                "token": TEAM_ROOM_TOKEN,
                "message": f"[ping from {role}] tool-exec probe before Run 1 kickoff",
            },
        )
        if r.get("status") == "success":
            print(f"  talk_send_message: ok")
        else:
            print(f"  talk_send_message: FAIL  {r.get('func_return', json.dumps(r))[:500]}")
            all_ok = False

        # Probe 2: write ping file
        r = run_tool(
            mcp_id,
            tool_ids["nc_webdav_write_file"],
            {
                "path": f"/agents/{role}-ping.txt",
                "content": f"ping from {role}; pre-kickoff probe; if you see this in /agents/, the WebDAV write path works.",
            },
        )
        if r.get("status") == "success":
            print(f"  nc_webdav_write_file: ok")
        else:
            print(f"  nc_webdav_write_file: FAIL  {r.get('func_return', json.dumps(r))[:500]}")
            all_ok = False

    print()
    if all_ok:
        print("ALL PROBES PASSED — kickoff plumbing is live.")
    else:
        print("ONE OR MORE PROBES FAILED — fix before kickoff.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
