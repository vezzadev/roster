# Researcher workspace

OpenClaw Gateway for the **Researcher** identity — sole holder of web tools
(`web_scrape`, `firecrawl_search`). Feeds Senior A and Senior B via Nextcloud
Talk + Files.

Workspace files (seeded by `../wire-openclaw.sh researcher`): see
`../_template/` for the canonical 5.

Primary model: Sonnet 4.6.

**Contamination-guard exposure:** highest among the four agents because of
direct web access. The domain blocklist enforced by `researcher-web-mcp`
applies before any Firecrawl call lands. Per-fetch URLs are logged for the
post-run Layer 2 audit.

Frozen prompt source: `../../../../week-1-spike/t5-system-prompts.md`
§Researcher.
