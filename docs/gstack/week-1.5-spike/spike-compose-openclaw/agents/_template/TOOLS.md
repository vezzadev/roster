# TOOLS.md (template)

Tools available to this agent. OpenClaw exposes both native built-ins and
MCP-server-backed tools through the same surface.

## Communication

- `talk_send_message` — Nextcloud Talk send (via `nextcloud-mcp`)
- `talk_list_messages` — Nextcloud Talk read

## Files

- `files_create`, `files_read`, `files_list` — Nextcloud Files CRUD
  (via `nextcloud-mcp`); writes are visible to all agents that have access to
  the target folder per the contamination guard ACL

## Web research (Researcher only)

- `web_scrape` — Firecrawl scrape (via `researcher-web-mcp`)
- `firecrawl_search` — Firecrawl search (via `researcher-web-mcp`)
- Domain blocklist applies — see
  `../../../../week-1-spike/spike-compose/researcher-web-mcp/audit/`

## Memory (if scribe skill is enabled — F-O3 #2)

- `memory_append` — append a fact / decision to MEMORY.md with structured tags
- `memory_query` — semantic search over MEMORY.md (only useful if F-O3 #3
  Mem0 bolt-on is enabled)
