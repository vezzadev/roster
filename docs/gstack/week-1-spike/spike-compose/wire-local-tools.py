"""Register CUSTOM `web_search` + `web_scrape` Letta tools on the Researcher's
Letta server, running in Letta's local sandbox (subprocess + venv). Replaces
the researcher-web-mcp MCP transport without introducing Modal.

Why this exists: Run 1-anthropic-direct halted because Letta's bundled
`mcp.client.streamable_http` SSE parser discards MCP responses whose chunk
boundaries split escaped unicode sequences (a ​ zero-width space in a
Firecrawl-returned Indonesian e-commerce page; see t5-run-ledger.md Run
1-anthropic-direct row). Replacing the streamable-HTTP MCP path with direct
Python tools sidesteps the broken parser entirely.

Why local sandbox and not Modal: Letta 0.16.8's Modal deploy path fails with
`cannot pickle 'PyCapsule' object` when invoked from the FastAPI request
context (cloudpickle 3.0 + Pydantic v2.11 + OTel-populated sys.modules
interaction; deploys cleanly from a fresh subprocess but not from the live
server). Local sandbox executes tools via subprocess + auto-created venv in
the Letta container — no isolation against tool authors, but the spike's
tools are written by us and only call Firecrawl. Sandboxing-against-third-
party-tool-authors is a v1 concern.

Architecture:
  PATCH /v1/sandbox-config/<local_id>   → configure the LOCAL sandbox with
                                          use_venv=true and firecrawl-py in
                                          pip_requirements. Letta creates the
                                          venv once and reuses it across
                                          tool invocations.
  POST .../environment-variable         → register FIRECRAWL_API_KEY on the
                                          local sandbox config. _gather_env_vars
                                          in tool_sandbox/base.py layers the
                                          DB-stored sandbox env vars on top of
                                          the container's os.environ.
  POST /v1/tools/                       → upload source for web_scrape +
                                          web_search as tool_type=custom. No
                                          modal-sandbox header, so they
                                          dispatch through local_sandbox.py's
                                          subprocess path.
  PATCH /v1/agents/<id>                 → attach both tool IDs to the
                                          Researcher and detach the
                                          researcher-web-mcp tools.

The script is idempotent on re-run: sandbox config by `type`, env vars by
`key`, tools by `name`. Agent tool-set is recomputed from a single source-of
-truth set at the bottom.
"""

import json
import pathlib
import textwrap
import urllib.error
import urllib.request

SPIKE = pathlib.Path(__file__).parent
LETTA_TOKEN = (SPIKE / "letta.local").read_text().strip()
FIRECRAWL_KEY = (SPIKE / "firecrawl.local").read_text().strip()
AGENTS = json.loads((SPIKE / "run-2-agents.local").read_text())
RESEARCHER = AGENTS["researcher"]  # {agent_id, letta_url}

LETTA_URL = RESEARCHER["letta_url"]
RESEARCHER_ID = RESEARCHER["agent_id"]


def http(method: str, path: str, body=None, timeout=60, extra_headers=None):
    headers = {
        "Authorization": f"Bearer {LETTA_TOKEN}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(
        f"{LETTA_URL}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            return resp.status, (json.loads(data) if data else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:500]


# ─────────────────────────────────────────────────────────────────────────────
# 1. Sandbox config (Modal) — pre-create so env vars can be registered first
# ─────────────────────────────────────────────────────────────────────────────

def ensure_local_sandbox_config() -> str:
    """Return the LOCAL sandbox config id, configured to auto-create a venv
    with firecrawl-py installed.

    Letta ships a default LOCAL config (no venv, no pip requirements). For
    our tools to import firecrawl-py we need either (a) the container's main
    Python to have it installed or (b) `use_venv=True` + `pip_requirements`
    so Letta creates and caches a per-sandbox venv on first tool exec.
    Option (b) survives container rebuilds and stays inside Letta's tool
    model. The venv is created once under sandbox_dir and reused.

    Pydantic-union pitfall: `pip_requirements` on E2BSandboxConfig is
    `Optional[List[str]]`, on LocalSandboxConfig is `List[PipRequirement]`
    (list of `{"name", "version"}` dicts). Sending a list-of-dicts here
    makes E2B fail validation and pushes the structural match to Local.
    """
    status, configs = http("GET", "/v1/sandbox-config/")
    if status != 200:
        raise SystemExit(f"  list sandbox configs failed: HTTP {status} {configs}")
    local = next((c for c in configs if c.get("type") == "local"), None)
    pip_reqs = [{"name": "firecrawl-py", "version": None}]
    body = {
        "config": {
            "use_venv": True,
            "pip_requirements": pip_reqs,
        }
    }
    if local is None:
        status, created = http("POST", "/v1/sandbox-config/", body)
        if status not in (200, 201):
            raise SystemExit(f"  create local sandbox config failed: HTTP {status} {created}")
        if created.get("type") != "local":
            raise SystemExit(f"  ERROR: server interpreted shape as {created.get('type')}, not local")
        print(f"  sandbox config created: {created['id']} (use_venv=True, firecrawl-py pinned)")
        return created["id"]
    status, updated = http("PATCH", f"/v1/sandbox-config/{local['id']}", body)
    if status != 200:
        raise SystemExit(f"  PATCH local sandbox config failed: HTTP {status} {updated}")
    print(f"  sandbox config updated: {local['id']} (use_venv=True, firecrawl-py pinned)")
    return local["id"]


def reset_existing_web_tools(researcher_id: str) -> None:
    """Detach + delete pre-existing tools named web_search/web_scrape/fetch_webpage.

    The Researcher comes pre-wired with an `external_mcp` web_scrape (from
    researcher-web-mcp) and `letta_builtin` web_search + fetch_webpage
    (Exa-backed built-ins, see constants.BUILTIN_TOOLS in tool_manager).
    These take precedence over any same-name CUSTOM tool we'd create — Letta
    enforces unique names per organization AND auto-classifies any tool
    matching a reserved built-in name as letta_builtin (dropping the
    source_code). That's why our custom Firecrawl-search is named
    `firecrawl_search` instead of `web_search`. Strategy:
      1. PATCH agent.tool_ids to drop both tool ids (avoids orphan refs)
      2. DELETE the tools entirely so the names are free
      3. Create fresh CUSTOM tools (caller does this) with non-reserved names

    Idempotent: missing tools / already-detached are tolerated.
    """
    status, all_tools = http("GET", "/v1/tools/?limit=500")
    if status != 200:
        raise SystemExit(f"  list tools failed: HTTP {status} {all_tools}")
    targets = [
        t for t in all_tools
        if t.get("name") in {"web_search", "web_scrape", "fetch_webpage"}
        and t.get("tool_type") in {"external_mcp", "letta_builtin"}
    ]
    if not targets:
        print("  no pre-existing web_search/web_scrape tools to reset")
        return

    # Step 1: detach from agent
    status, agent = http("GET", f"/v1/agents/{researcher_id}")
    if status != 200:
        raise SystemExit(f"  get researcher failed: HTTP {status} {agent}")
    target_ids = {t["id"] for t in targets}
    new_ids = [t["id"] for t in agent.get("tools", []) if t["id"] not in target_ids]
    if len(new_ids) != len(agent.get("tools", [])):
        status, _ = http("PATCH", f"/v1/agents/{researcher_id}", {"tool_ids": new_ids})
        print(f"  detached {len(agent.get('tools', [])) - len(new_ids)} pre-existing web tool(s) from researcher (HTTP {status})")

    # Step 2: delete tools so name slots free up
    for t in targets:
        status, resp = http("DELETE", f"/v1/tools/{t['id']}")
        print(f"  deleted {t['name']} ({t['tool_type']}, {t['id']}) — HTTP {status}")


def ensure_sandbox_env_var(sandbox_config_id: str, key: str, value: str) -> None:
    status, vars_ = http("GET", f"/v1/sandbox-config/{sandbox_config_id}/environment-variable")
    if status != 200:
        raise SystemExit(f"  list env vars failed: HTTP {status} {vars_}")
    for v in vars_:
        if v.get("key") == key:
            # Update if value changed (PATCH /v1/sandbox-config/environment-variable/<id>)
            if v.get("value") != value:
                status, _ = http("PATCH", f"/v1/sandbox-config/environment-variable/{v['id']}",
                                 {"value": value})
                print(f"  env var {key} updated (HTTP {status})")
            else:
                print(f"  env var {key} already set")
            return
    status, created = http(
        "POST",
        f"/v1/sandbox-config/{sandbox_config_id}/environment-variable",
        {"key": key, "value": value, "description": f"{key} for Letta sandboxed tools"},
    )
    if status not in (200, 201):
        raise SystemExit(f"  create env var {key} failed: HTTP {status} {created}")
    print(f"  env var {key} registered")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Tool source code — declared inline so Letta hashes them deterministically.
#    Each tool has:
#      - type hints on params + return (Letta auto-generates JSON schema)
#      - a Google-style docstring (becomes the tool description for the LLM)
#      - pip_requirements list (Letta passes to modal.Image.debian_slim.pip_install)
#    Tool names match the previous MCP versions exactly so the Researcher's
#    system prompt + memory blocks remain valid without re-hashing.
# ─────────────────────────────────────────────────────────────────────────────

WEB_SCRAPE_SOURCE = textwrap.dedent('''
    def web_scrape(url: str) -> str:
        """Fetch a single URL via Firecrawl and return its content as Markdown.

        Use when you have a specific URL and need its full text content. Returns
        the page rendered to Markdown (Firecrawl handles JS rendering, paywalls,
        and noise stripping). For broader discovery, use web_search instead.

        Args:
            url: The fully-qualified URL to fetch (https://...). Must be a single URL.

        Returns:
            The page content as Markdown text. If the fetch fails, returns a
            short error string starting with "ERROR:" so the agent can decide
            whether to retry, try a different URL, or move on.
        """
        import os
        try:
            from firecrawl import Firecrawl
        except ImportError as e:
            return f"ERROR: firecrawl-py not installed in sandbox: {e!r}"

        api_key = os.environ.get("FIRECRAWL_API_KEY")
        if not api_key:
            return "ERROR: FIRECRAWL_API_KEY not set in sandbox environment"

        try:
            fc = Firecrawl(api_key=api_key)
            doc = fc.scrape(url=url, formats=["markdown"])
        except Exception as e:
            return f"ERROR: Firecrawl scrape failed for {url!r}: {e!r}"

        # firecrawl-py 4.x returns a Document with .markdown set when the
        # markdown format is requested. Fall back to a nested .data dict for
        # older SDK shapes; bail to repr on unexpected types.
        md = getattr(doc, "markdown", None)
        if not md:
            data = getattr(doc, "data", None)
            if isinstance(data, dict):
                md = data.get("markdown")
        if not md:
            return f"ERROR: Firecrawl returned no markdown for {url!r}; raw={doc!r}"
        return md
''').strip()

WEB_SEARCH_SOURCE = textwrap.dedent('''
    def firecrawl_search(query: str, limit: int = 5) -> str:
        """Run a web search via Firecrawl and return the top results.

        Use when you need to discover candidate URLs for a topic, before
        scraping specific pages. Each result line is `[N] TITLE — URL` followed
        by a short snippet, formatted so the model can pick which to scrape.

        Args:
            query: Plain search query (e.g. "Indonesia ecommerce SMB logistics 2025").
            limit: Number of results to return (1-10). Default 5.

        Returns:
            Newline-separated result list as a single string. On failure,
            returns a short error string starting with "ERROR:".
        """
        import os
        try:
            from firecrawl import Firecrawl
        except ImportError as e:
            return f"ERROR: firecrawl-py not installed in sandbox: {e!r}"

        api_key = os.environ.get("FIRECRAWL_API_KEY")
        if not api_key:
            return "ERROR: FIRECRAWL_API_KEY not set in sandbox environment"

        limit = max(1, min(int(limit), 10))
        try:
            fc = Firecrawl(api_key=api_key)
            res = fc.search(query=query, limit=limit)
        except Exception as e:
            return f"ERROR: Firecrawl search failed for {query!r}: {e!r}"

        # firecrawl-py 4.x returns SearchData with .data: list[SearchResultWeb]
        # (Pydantic models, not dicts — no .get attribute).
        items = getattr(res, "data", None) or getattr(res, "web", None) or []
        if not items:
            return f"ERROR: Firecrawl search returned no results for {query!r}"

        lines = []
        for i, item in enumerate(items, start=1):
            d = item.model_dump() if hasattr(item, "model_dump") else (item if isinstance(item, dict) else {})
            title = d.get("title") or ""
            url = d.get("url") or ""
            snippet = d.get("description") or ""
            lines.append(f"[{i}] {title} — {url}")
            if snippet:
                lines.append(f"    {snippet}")
        return "\\n".join(lines)
''').strip()


TOOLS = [
    {
        "name": "web_scrape",
        "source_code": WEB_SCRAPE_SOURCE,
        "pip_requirements": [{"name": "firecrawl-py", "version": None}],
        "description_for_log": "Firecrawl scrape (Markdown) via Letta local sandbox",
    },
    {
        "name": "firecrawl_search",
        "source_code": WEB_SEARCH_SOURCE,
        "pip_requirements": [{"name": "firecrawl-py", "version": None}],
        "description_for_log": "Firecrawl search via Letta local sandbox",
    },
]


def ensure_tool(name: str, source_code: str, pip_requirements) -> str:
    """Return the tool id, creating or upserting if necessary.

    Only PATCH a tool if it's already CUSTOM and Modal-tagged — otherwise
    delete + recreate. Letta's PATCH does not change `tool_type` (an MCP or
    builtin tool stays MCP/builtin even after a source_code PATCH), so
    PATCHing a non-CUSTOM tool corrupts its definition without changing
    dispatch. The dispatcher continues to route through MCP / the builtin,
    and the new source_code is dead weight.
    """
    status, tools = http("GET", f"/v1/tools/?name={name}")
    if status != 200:
        raise SystemExit(f"  list tools failed: HTTP {status} {tools}")
    if tools:
        existing = tools[0]
        if existing.get("tool_type") == "custom":
            body = {"source_code": source_code, "pip_requirements": pip_requirements}
            status, updated = http("PATCH", f"/v1/tools/{existing['id']}", body, timeout=120)
            if status != 200:
                raise SystemExit(f"  PATCH tool {name} failed: HTTP {status} {updated}")
            print(f"  tool {name}: updated ({existing['id']})")
            return existing["id"]
        # Non-CUSTOM existing tool with the same name — delete and recreate.
        status, _ = http("DELETE", f"/v1/tools/{existing['id']}")
        print(f"  deleted non-CUSTOM tool {name} ({existing['tool_type']}, {existing['id']}) — HTTP {status}")
    body = {
        "source_code": source_code,
        "source_type": "python",
        "pip_requirements": pip_requirements,
    }
    status, created = http("POST", "/v1/tools/", body, timeout=120)
    if status not in (200, 201):
        raise SystemExit(f"  POST tool {name} failed: HTTP {status} {created}")
    print(f"  tool {name}: created ({created['id']}, type={created.get('tool_type')})")
    return created["id"]


# ─────────────────────────────────────────────────────────────────────────────
# 3. Researcher tool-set update
# ─────────────────────────────────────────────────────────────────────────────

def update_researcher_tools(new_tool_ids: list[str]) -> None:
    status, agent = http("GET", f"/v1/agents/{RESEARCHER_ID}")
    if status != 200:
        raise SystemExit(f"  get researcher failed: HTTP {status} {agent}")
    current_tools = {t["id"]: t for t in agent.get("tools", [])}

    # Drop pre-existing web tools we're replacing: the original MCP-sourced
    # web_search/web_scrape and any letta_builtin web_search/fetch_webpage
    # that Letta auto-attached. Keep everything else (NC tools, conversation
    # search, core memory, etc.).
    stale_names = {"web_search", "web_scrape", "fetch_webpage"}
    to_keep, to_drop = [], []
    for tid, tool in current_tools.items():
        if tool["name"] in stale_names and tid not in new_tool_ids:
            to_drop.append(tid)
        else:
            to_keep.append(tid)
    new_set = list(set(to_keep + new_tool_ids))

    body = {"tool_ids": new_set}
    status, updated = http("PATCH", f"/v1/agents/{RESEARCHER_ID}", body)
    if status != 200:
        raise SystemExit(f"  PATCH researcher tools failed: HTTP {status} {updated}")
    print(f"  researcher tools updated: dropped {len(to_drop)} stale web tool(s), "
          f"attached {len(new_tool_ids)} CUSTOM tool(s). New tool count: {len(new_set)}.")


def main():
    print("=== 1. Local sandbox config + Firecrawl env var ===")
    sandbox_id = ensure_local_sandbox_config()
    ensure_sandbox_env_var(sandbox_id, "FIRECRAWL_API_KEY", FIRECRAWL_KEY)

    print()
    print("=== 2. Reset pre-existing web_search / web_scrape tools (MCP + builtin) ===")
    reset_existing_web_tools(RESEARCHER_ID)

    print()
    print("=== 3. Register CUSTOM web tools (local sandbox dispatch) ===")
    tool_ids = []
    for spec in TOOLS:
        tid = ensure_tool(spec["name"], spec["source_code"], spec["pip_requirements"])
        tool_ids.append(tid)

    print()
    print("=== 4. Researcher agent tool-set ===")
    update_researcher_tools(tool_ids)

    print()
    print("Done. First web_search / web_scrape invocation will trigger venv")
    print("creation under /root/.letta/tool_execution_dir/venv inside the")
    print("Letta container (one-time, ~30-60s). Subsequent calls are fast.")


if __name__ == "__main__":
    main()
