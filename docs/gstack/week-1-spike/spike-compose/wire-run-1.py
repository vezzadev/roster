"""Wire Run 1 agents (EM + Researcher) into per-agent Letta containers.

Run 1 is the 2-agent ablation. Per the swap recorded in t5-system-prompts.md
Change log, the smoke uses EM + Researcher so the web-fetch path + contamination
guard get live exercise before Run 2 brings in the full 4-agent team.

Architecture: one Letta container per agent (see ../t5-run-ledger.md "Letta
tool-namespace finding"). A singleton Letta dedupes MCP tools by name across
its registered MCP servers — so two per-agent MCP sidecars exposing the same
`talk_send_message` collapse onto a single tool binding pointing at whichever
MCP was registered last, breaking identity isolation. The fix is structural:
one Letta per agent, with the agent's MCP sidecars registered only on that
Letta. Each Letta only knows about its own MCPs, so tool names never collide.

Pre-create gates (any failure halts before agent create):
  1. SHA-256 of each prompt body (fenced-block contents) matches the value
     recorded in t5-system-prompts.md.
  2. Banned-token grep over each prompt body returns 0 hits.

Then for each of EM + Researcher:
  - Register the role's MCP sidecars with the role's Letta (idempotent —
    skips if a server with that server_name already exists).
  - Resolve the tool IDs Letta now exposes for each sidecar, filter to the
    expected subset.
  - POST /v1/agents/ with name + system + model + tool_ids on the role's Letta.

Writes the resulting (agent_id, letta_url) pairs to ./run1-agents.local
(gitignored).
"""

import hashlib
import json
import pathlib
import re
import urllib.request

PROMPTS_PATH = pathlib.Path(__file__).resolve().parents[1] / "t5-system-prompts.md"
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

# Talk + Files tools the spike needs from each nextcloud-mcp container.
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

# Seed memory blocks per role. Letta 0.16.8 no longer ships default `human` /
# `persona` blocks; without these, `memory_insert(label="human", …)` errors
# with `Block field human does not exist (available sections = ())` — see
# ../t5-run-1-conclusions.md C-2 + ../t5-run-ledger.md "Memory blocks absent".
# Kept terse on purpose: the system prompt is the immutable frame; these
# blocks are working memory the agent can refine with memory_insert /
# memory_replace as the engagement runs.
MEMORY_BLOCKS = {
    "em": [
        {
            "label": "persona",
            "value": (
                "I am the Engagement Manager. I coordinate the team, own "
                "/agents/brief.md (the final deliverable), pace work toward "
                "the deadline, and synthesize the Researcher's bundles into "
                "the brief. I do not source web material myself."
            ),
            "description": "My own role, responsibilities, and how I operate.",
        },
        {
            "label": "human",
            "value": (
                "The founder kicked off this engagement with "
                "'Begin the engagement.' and may post mid-run nudges. I "
                "communicate with the founder only via Talk rooms (#team) "
                "and direct Letta wakes — never DM."
            ),
            "description": "Who I am working for and how they communicate with me.",
        },
    ],
    "researcher": [
        {
            "label": "persona",
            "value": (
                "I am the Researcher. I source factual material via "
                "web_search and web_scrape (Firecrawl-backed, blocklist "
                "enforced) and write findings to /agents/_research-bundle-*.md "
                "for the EM to synthesize. I do not draft the final brief."
            ),
            "description": "My own role, responsibilities, and how I operate.",
        },
        {
            "label": "human",
            "value": (
                "I work under the Engagement Manager (EM). The EM directs "
                "what to research, in what order, and when to stop. The "
                "founder is upstream of the EM; I do not interact with the "
                "founder directly."
            ),
            "description": "Who I am working for and how they communicate with me.",
        },
    ],
}

# Each role has its own Letta server URL + MCP sidecars. Each MCP is
# (server_name, internal_server_url, expected_tool_subset). server_url is
# resolved over the Docker `spike` network — Letta and the MCP run on the same
# bridge so the hostname resolves to the sidecar's container IP.
ROLES = [
    {
        "title": "Engagement Manager (EM)",
        "name": "em",
        # Native Anthropic handle (Run 1-anthropic-direct + Run 2). Switched
        # from `openrouter/anthropic/claude-opus-4.7` per C-6 in
        # ../t5-run-1-conclusions.md — the OpenRouter / OpenAI-compatible
        # path in Letta does not emit `cache_control` markers (upstream
        # letta-ai/letta#3351), so cached input tokens were always 0 and
        # Run 1's $57.87 was uncached list price. The native Anthropic
        # client path in Letta (`anthropic_client.py`) emits cache_control
        # correctly. Requires `ANTHROPIC_API_KEY` env on the letta-em
        # container — bring-up.sh sources from ./anthropic.local.
        "model": "anthropic/claude-opus-4-7",
        "letta_url": "http://127.0.0.1:8283",
        "mcps": [
            ("nextcloud-em", "http://nextcloud-mcp-em:8000/mcp", NEXTCLOUD_SPIKE_TOOLS),
        ],
    },
    {
        "title": "Researcher",
        "name": "researcher",
        "model": "anthropic/claude-sonnet-4-6",
        "letta_url": "http://127.0.0.1:8284",
        "mcps": [
            ("nextcloud-researcher", "http://nextcloud-mcp-researcher:8000/mcp", NEXTCLOUD_SPIKE_TOOLS),
            ("researcher-web", "http://researcher-web-mcp:8000/mcp", RESEARCHER_WEB_TOOLS),
        ],
    },
]


def http(letta_url: str, method: str, path: str, body=None):
    req = urllib.request.Request(
        f"{letta_url}{path}",
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
    hits = []
    for tok in BANNED_TOKENS:
        pattern = rf"(?:^|\W){re.escape(tok)}(?:\W|$)"
        if re.search(pattern, body, re.IGNORECASE):
            hits.append(tok)
    if hits:
        raise SystemExit(f"BANNED TOKEN HIT in {role_title}: {hits}")
    print(f"  banned-token grep (word-boundary): 0 hits across {len(BANNED_TOKENS)} tokens")


def register_mcp_idempotent(letta_url: str, server_name: str, server_url: str) -> str:
    """Return the MCP server's id on this Letta, registering it if absent."""
    existing = http(letta_url, "GET", "/v1/mcp-servers/?limit=100")
    for s in existing:
        if s.get("server_name") == server_name:
            return s["id"]
    created = http(letta_url, "POST", "/v1/mcp-servers/", {
        "server_name": server_name,
        "config": {"mcp_server_type": "streamable_http", "server_url": server_url},
    })
    return created["id"]


def main():
    prompts_text = PROMPTS_PATH.read_text()
    agent_ids = {}

    for role in ROLES:
        title = role["title"]
        letta_url = role["letta_url"]
        print(f"\n=== {title}  (letta @ {letta_url}) ===")
        body = extract_prompt(prompts_text, title)

        gate_hash(title, body)
        gate_banned_tokens(title, body)

        tool_ids: list[str] = []
        for server_name, server_url, expected_tools in role["mcps"]:
            mcp_id = register_mcp_idempotent(letta_url, server_name, server_url)
            tools = http(letta_url, "GET", f"/v1/mcp-servers/{mcp_id}/tools")
            ids_for_server = [t["id"] for t in tools if t["name"] in expected_tools]
            missing = expected_tools - {t["name"] for t in tools}
            if missing:
                raise SystemExit(f"  MISSING TOOLS on {server_name!r}: {sorted(missing)}")
            print(f"  {server_name}: attached {len(ids_for_server)} of {len(expected_tools)} expected (server has {len(tools)} total)")
            tool_ids.extend(ids_for_server)

        created = http(letta_url, "POST", "/v1/agents/", {
            "name": role["name"],
            "system": body,
            "model": role["model"],
            "embedding": "letta/letta-free",
            "tool_ids": tool_ids,
            "include_base_tools": True,
            "memory_blocks": MEMORY_BLOCKS[role["name"]],
        })
        # Anthropic native `claude-opus-4-7` rejects `thinking.type.enabled`
        # mode (only `adaptive` is supported per Anthropic /v1/models). Letta
        # 0.16.8 emits `thinking.type.enabled` whenever `enable_reasoner=true`
        # and does not yet wire `adaptive` mode for Opus 4.7. The native run
        # therefore disables the reasoner on Opus only — Run 1 cost analysis
        # found reasoning tokens were 0.05% of total tokens (not a cost lever).
        # Quality impact is logged as a Run-1-anthropic-direct caveat. Sonnet
        # 4.6 still supports `enabled` so the Researcher keeps the reasoner on.
        # PATCH after create (create-time llm_config is rejected as 422 by
        # Letta 0.16.8 when partial; full shape required for create).
        if role["model"] == "anthropic/claude-opus-4-7":
            existing = http(letta_url, "GET", f"/v1/agents/{created['id']}")
            cfg = dict(existing["llm_config"])
            cfg["enable_reasoner"] = False
            http(letta_url, "PATCH", f"/v1/agents/{created['id']}", {"llm_config": cfg})
        agent_id = created["id"]
        agent_ids[role["name"]] = {"agent_id": agent_id, "letta_url": letta_url}
        print(f"  agent created: {agent_id} ({len(tool_ids)} MCP tools + Letta base)")

    out = pathlib.Path(__file__).parent / "run1-agents.local"
    out.write_text(json.dumps(agent_ids, indent=2) + "\n")
    print(f"\nagent IDs saved to {out.name}")
    print(json.dumps(agent_ids, indent=2))


if __name__ == "__main__":
    main()
