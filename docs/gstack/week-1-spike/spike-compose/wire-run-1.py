"""Wire Run 1 agents (EM + Analyst A) into Letta.

Pre-boot gates (any failure halts before agent create):
  1. SHA-256 of each prompt body (fenced-block contents) matches the value
     recorded in t5-system-prompts.md.
  2. Banned-token grep over each prompt body returns 0 hits.

Then for each of EM + Analyst A:
  - List the tools on that agent's MCP server (registered earlier).
  - Filter to the Talk + WebDAV subset the spike needs (~15 tools).
  - POST /v1/agents/ with name + system + model + tool_ids.

Writes the resulting agent IDs to ./run1-agents.local (gitignored).

Idempotency: this script is intended to be run once per Run 1 boot. If an
agent already exists with the same name, the new create will succeed and
produce a duplicate — that's fine for the spike (Letta picks the most-recent
one when you message by ID, and the script writes the new ID either way).
"""

import hashlib
import json
import os
import pathlib
import re
import sys
import urllib.request

PROMPTS_PATH = pathlib.Path(__file__).resolve().parents[1] / "t5-system-prompts.md"
LETTA_URL = "http://127.0.0.1:8283"
LETTA_TOKEN = pathlib.Path(__file__).parent.joinpath("letta.local").read_text().strip()

EXPECTED_HASHES = {
    "Engagement Manager (EM)": "f41b83ba42cf5b5d62a4f93ef70f27e5e1760cdfa81be5e86f647db1a4a6a04a",
    "Senior Analyst A": "4f715306639f519af745e1df97455a5b99c9e99266069b60c5b01fdf8b01f447",
}

BANNED_TOKENS = [
    "mckinsey", "bcg", "boston consulting", "bain", "strategy&",
    "roland berger", "monitor deloitte", "oliver wyman", "l.e.k.", "kearney",
    "top-tier strategy", "big-3 strategy", "big-3", "analyst-grade",
    "big-3-quality", "top strategy firm", "1-5 scale", "rubric", "grading",
    "ai panel", "vietnam: a global engine", "beating the odds",
    "changing your orbit", "foreign e-tailers", "ahead of the curve",
]

# Talk + Files tools the spike needs. Agents don't need the other 119 tools
# (calendar, contacts, cookbook, news, tables, deck, etc.) — keeping the
# attached set tight reduces context bloat in the agent.
SPIKE_TOOLS = {
    "talk_list_conversations", "talk_get_conversation", "talk_get_messages",
    "talk_send_message", "talk_list_participants", "talk_mark_as_read",
    "nc_webdav_read_file", "nc_webdav_write_file", "nc_webdav_list_directory",
    "nc_webdav_find_by_name", "nc_webdav_search_files",
    "nc_webdav_create_directory", "nc_webdav_delete_resource",
    "nc_webdav_copy_resource", "nc_webdav_move_resource",
}

ROLES = [
    {
        "title": "Engagement Manager (EM)",
        "name": "em",
        "model": "openrouter/anthropic/claude-opus-4.7",
        "mcp_server_id": "mcp_server-db172699-cf6e-4baf-9538-6ff9b3e6d471",
    },
    {
        "title": "Senior Analyst A",
        "name": "analyst-a",
        "model": "openrouter/anthropic/claude-sonnet-4.6",
        "mcp_server_id": "mcp_server-a7916894-3272-41d4-959b-9078d13b5cdb",
    },
]


def http(method: str, path: str, body=None):
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


def extract_prompt(text: str, role_title: str) -> str:
    pattern = rf"## {re.escape(role_title)}\n.*?\n```\n(.*?)\n```"
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        raise RuntimeError(f"could not extract prompt for role: {role_title}")
    return m.group(1)


def gate_hash(role_title: str, body: str) -> None:
    actual = hashlib.sha256(body.encode()).hexdigest()
    expected = EXPECTED_HASHES[role_title]
    if actual != expected:
        raise SystemExit(f"HASH MISMATCH for {role_title}: actual={actual} expected={expected}")
    print(f"  hash OK: {actual}")


def gate_banned_tokens(role_title: str, body: str) -> None:
    # Word-boundary regex (case-insensitive) so "bain" doesn't match "Bahrain"
    # and "bcg" doesn't match a hypothetical word containing the trigram.
    # `re.escape` neutralizes the regex metacharacter in tokens like
    # "strategy&" and "l.e.k.". `(?:^|\W)…(?:\W|$)` is the word-boundary form
    # that works for tokens ending in non-word characters (\b doesn't).
    hits = []
    for tok in BANNED_TOKENS:
        pattern = rf"(?:^|\W){re.escape(tok)}(?:\W|$)"
        if re.search(pattern, body, re.IGNORECASE):
            hits.append(tok)
    if hits:
        raise SystemExit(f"BANNED TOKEN HIT in {role_title}: {hits}")
    print(f"  banned-token grep (word-boundary): 0 hits across {len(BANNED_TOKENS)} tokens")


def main():
    prompts_text = PROMPTS_PATH.read_text()
    agent_ids = {}

    for role in ROLES:
        title = role["title"]
        print(f"\n=== {title} ===")
        body = extract_prompt(prompts_text, title)

        gate_hash(title, body)
        gate_banned_tokens(title, body)

        # Pull tools for this agent's MCP server, filter to the spike subset
        tools = http("GET", f"/v1/mcp-servers/{role['mcp_server_id']}/tools")
        tool_ids = [t["id"] for t in tools if t["name"] in SPIKE_TOOLS]
        missing = SPIKE_TOOLS - {t["name"] for t in tools if t["name"] in SPIKE_TOOLS}
        if missing:
            raise SystemExit(f"  MISSING TOOLS on {role['mcp_server_id']}: {sorted(missing)}")
        print(f"  attached tools: {len(tool_ids)} of {len(tools)} available")

        # Create the agent
        created = http("POST", "/v1/agents/", {
            "name": role["name"],
            "system": body,
            "model": role["model"],
            "embedding": "letta/letta-free",
            "tool_ids": tool_ids,
            "include_base_tools": True,
        })
        agent_id = created["id"]
        agent_ids[role["name"]] = agent_id
        print(f"  agent created: {agent_id}")

    out = pathlib.Path(__file__).parent / "run1-agents.local"
    out.write_text(json.dumps(agent_ids, indent=2) + "\n")
    print(f"\nagent IDs saved to {out.name}")
    print(json.dumps(agent_ids, indent=2))


if __name__ == "__main__":
    main()
