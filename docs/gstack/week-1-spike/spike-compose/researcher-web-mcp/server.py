#!/usr/bin/env python3
# Researcher web-fetch wrapper MCP. Sits between Letta's Researcher agent and
# the Firecrawl SaaS API so the contamination blocklist from
# ../../t4-mcp-investigation.md "Researcher domain blocklist" is enforced
# server-side. Without this wrapper, an agent calling firecrawl_scrape with
# a blocked URL bypasses every other contamination guard (the Firecrawl /scrape
# endpoint has no excludeDomains parameter — only /search does, per the API
# reference at https://docs.firecrawl.dev/api-reference/endpoint/scrape).
#
# Two tools exposed to the Researcher:
#   - web_search: forwards to /v2/search with excludeDomains always injected
#                 from the hostname entries in the blocklist.
#   - web_scrape: parses the URL, matches against host + pattern entries,
#                 rejects blocked URLs without round-tripping to Firecrawl.
#
# Every call (allowed or blocked) is appended to AUDIT_PATH as one JSON line.
# The audit log is the post-run verification trail for the contamination check
# and feeds ../../t5-researcher-urls.md after Run 2.

import json
import os
import pathlib
import re
import time
import urllib.parse

import httpx
from mcp.server.fastmcp import FastMCP

FIRECRAWL_API_KEY = os.environ["FIRECRAWL_API_KEY"]
BLOCKLIST_PATH = os.environ.get("BLOCKLIST_PATH", "/etc/researcher-web/blocklist.txt")
AUDIT_PATH = os.environ.get("AUDIT_PATH", "/var/log/researcher-web/fetch.jsonl")
FIRECRAWL_BASE = os.environ.get("FIRECRAWL_BASE", "https://api.firecrawl.dev")


def _load_blocklist() -> tuple[list[str], list[str]]:
    p = pathlib.Path(BLOCKLIST_PATH)
    if not p.exists():
        return [], []
    hosts: list[str] = []
    patterns: list[str] = []
    for raw in p.read_text().splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if "*" in s or "/" in s:
            patterns.append(s.lower())
        else:
            hosts.append(s.lower())
    return hosts, patterns


BLOCK_HOSTS, BLOCK_PATTERNS = _load_blocklist()


def _audit(event: dict) -> None:
    p = pathlib.Path(AUDIT_PATH)
    p.parent.mkdir(parents=True, exist_ok=True)
    event["ts"] = time.time()
    with p.open("a") as f:
        f.write(json.dumps(event, default=str) + "\n")


def _host_block_hit(host: str) -> str | None:
    h = host.lower()
    for entry in BLOCK_HOSTS:
        if h == entry or h.endswith("." + entry):
            return entry
    return None


def _pattern_block_hit(url: str, host: str, path: str) -> str | None:
    candidates = [url.lower(), (host + path).lower()]
    for entry in BLOCK_PATTERNS:
        regex = re.escape(entry).replace(r"\*", ".*")
        for c in candidates:
            if re.search(regex, c):
                return entry
    return None


def _url_block_hit(url: str) -> str | None:
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower()
    if not host:
        return "invalid-url"
    hit = _host_block_hit(host)
    if hit:
        return f"host:{hit}"
    hit = _pattern_block_hit(url, host, parsed.path or "")
    if hit:
        return f"pattern:{hit}"
    return None


mcp = FastMCP("researcher-web", host="0.0.0.0", port=8000)


@mcp.tool()
def web_search(query: str, limit: int = 10, country: str = "US") -> dict:
    """Search the web. Returns title/description/url for each result.

    A standing list of consulting-firm domains is excluded server-side
    (Firecrawl's excludeDomains parameter). The Researcher cannot
    override this filter.
    """
    limit = max(1, min(int(limit), 50))
    body = {
        "query": query,
        "limit": limit,
        "country": country,
        "excludeDomains": BLOCK_HOSTS,
    }
    _audit({"op": "search", "query": query, "limit": limit, "excludeDomains": BLOCK_HOSTS})
    r = httpx.post(
        f"{FIRECRAWL_BASE}/v2/search",
        headers={
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=90,
    )
    r.raise_for_status()
    return r.json()


@mcp.tool()
def web_scrape(url: str, only_main_content: bool = True) -> dict:
    """Fetch a single URL and return its markdown content.

    Blocked domains (consulting-firm primary sites + known mirrors/archives)
    are rejected before any network call. Allowed URLs are fetched via
    Firecrawl with onlyMainContent on by default.
    """
    block = _url_block_hit(url)
    if block:
        _audit({"op": "scrape", "url": url, "blocked": block})
        return {
            "error": "blocked_by_contamination_guard",
            "rule": block,
            "url": url,
            "note": "This domain is on the Researcher contamination blocklist. Pick a different source.",
        }
    body = {
        "url": url,
        "formats": ["markdown"],
        "onlyMainContent": bool(only_main_content),
    }
    _audit({"op": "scrape", "url": url, "allowed": True})
    r = httpx.post(
        f"{FIRECRAWL_BASE}/v2/scrape",
        headers={
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
