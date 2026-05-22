"""Wire Run 1 agents (EM + Researcher) into Letta.

Run 1 is the 2-agent ablation. Per the swap recorded in t5-system-prompts.md
Change log, the smoke uses EM + Researcher (not the original EM + Analyst A
pairing) so the web-fetch path + contamination guard get live exercise before
Run 2 brings in the full 4-agent team.

Pre-boot gates (any failure halts before agent create):
  1. SHA-256 of each prompt body (fenced-block contents) matches the value
     recorded in t5-system-prompts.md.
  2. Banned-token grep over each prompt body returns 0 hits.

Then for each of EM + Researcher:
  - Resolve the agent's MCP servers by server_name (registered earlier via
    docker compose + Letta /v1/mcp-servers/ POST).
  - Filter each server's tools to the subset that role needs.
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
    "Engagement Manager (EM)": "e966a65548025d0dfe65ac52a24e4a855ec103de3a2223a966757f304f0ad40f",
    "Researcher": "2fff77b9103e233e7a7eea4728e90d668a42fd3e9e3d402c6ac7a86d29435d24",
}

BANNED_TOKENS = [
    "mckinsey", "bcg", "boston consulting", "bain", "strategy&",
    "roland berger", "monitor deloitte", "oliver wyman", "l.e.k.", "kearney",
    "top-tier strategy", "big-3 strategy", "big-3", "analyst-grade",
    "big-3-quality", "top strategy firm", "1-5 scale", "rubric", "grading",
    "ai panel", "vietnam: a global engine", "beating the odds",
    "changing your orbit", "foreign e-tailers", "ahead of the curve",
]

# Talk + Files tools the spike needs from each nextcloud-mcp container. Agents
# don't need the other 119 tools (calendar, contacts, cookbook, news, tables,
# deck, etc.) — keeping the attached set tight reduces context bloat.
NEXTCLOUD_SPIKE_TOOLS = {
    "talk_list_conversations", "talk_get_conversation", "talk_get_messages",
    "talk_send_message", "talk_list_participants", "talk_mark_as_read",
    "nc_webdav_read_file", "nc_webdav_write_file", "nc_webdav_list_directory",
    "nc_webdav_find_by_name", "nc_webdav_search_files",
    "nc_webdav_create_directory", "nc_webdav_delete_resource",
    "nc_webdav_copy_resource", "nc_webdav_move_resource",
}

# researcher-web wrapper tools (Firecrawl-backed, blocklist-enforced).
RESEARCHER_WEB_TOOLS = {"web_search", "web_scrape"}

# Each role lists (mcp_server_name, expected_tool_subset) pairs. Server names
# are resolved to IDs at runtime via /v1/mcp-servers/ to avoid hardcoding IDs
# that change every time docker compose down/up cycles the MCP containers.
ROLES = [
    {
        "title": "Engagement Manager (EM)",
        "name": "em",
        "model": "openrouter/anthropic/claude-opus-4.7",
        "mcps": [("nextcloud-em", NEXTCLOUD_SPIKE_TOOLS)],
    },
    {
        "title": "Researcher",
        "name": "researcher",
        "model": "openrouter/anthropic/claude-sonnet-4.6",
        "mcps": [
            ("nextcloud-researcher", NEXTCLOUD_SPIKE_TOOLS),
            ("researcher-web", RESEARCHER_WEB_TOOLS),
        ],
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


def resolve_mcp_server_id(name: str) -> str:
    servers = http("GET", "/v1/mcp-servers/?limit=100")
    for s in servers:
        if s.get("server_name") == name:
            return s["id"]
    raise SystemExit(f"  MCP server not registered with Letta: {name!r}")


def main():
    prompts_text = PROMPTS_PATH.read_text()
    agent_ids = {}

    for role in ROLES:
        title = role["title"]
        print(f"\n=== {title} ===")
        body = extract_prompt(prompts_text, title)

        gate_hash(title, body)
        gate_banned_tokens(title, body)

        tool_ids: list[str] = []
        for server_name, expected_tools in role["mcps"]:
            server_id = resolve_mcp_server_id(server_name)
            tools = http("GET", f"/v1/mcp-servers/{server_id}/tools")
            ids_for_server = [t["id"] for t in tools if t["name"] in expected_tools]
            missing = expected_tools - {t["name"] for t in tools}
            if missing:
                raise SystemExit(f"  MISSING TOOLS on {server_name!r}: {sorted(missing)}")
            print(f"  {server_name}: attached {len(ids_for_server)} of {len(expected_tools)} expected (server has {len(tools)} total)")
            tool_ids.extend(ids_for_server)

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
        print(f"  agent created: {agent_id} ({len(tool_ids)} MCP tools + Letta base)")

    out = pathlib.Path(__file__).parent / "run1-agents.local"
    out.write_text(json.dumps(agent_ids, indent=2) + "\n")
    print(f"\nagent IDs saved to {out.name}")
    print(json.dumps(agent_ids, indent=2))


if __name__ == "__main__":
    main()
