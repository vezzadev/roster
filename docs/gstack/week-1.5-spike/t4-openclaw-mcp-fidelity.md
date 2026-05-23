# T4' — OpenClaw MCP fidelity check

Parent: [README.md](README.md) §T4' (spike-blocker)

**Purpose:** verify that the two MCP servers that Week 1's Letta runtime
talked to (`cbcoutinho/nextcloud-mcp-server` + the in-repo
`researcher-web-mcp` Firecrawl wrapper) work under OpenClaw with the **same
fidelity** Letta got — not just "connects," but identical response shapes
across the call surface the agents actually use.

This is a hard gate. If OpenClaw's MCP client has its own framing bug (as
F-O1 in [t2-openclaw-fallback.md](t2-openclaw-fallback.md) anticipates), the
spike conclusion is "MCP layer is the bottleneck, not the runtime," and we
don't proceed to T5'.

Status: ⏳ not started.

## Acceptance criteria

| # | Server | Tools to exercise | Pass condition |
|---|---|---|---|
| 1 | `cbcoutinho/nextcloud-mcp-server` | `talk_send_message`, `talk_list_messages`, `files_create`, `files_read`, `files_list` (all 5 used in Week 1 runs) | Response shape byte-equivalent to Letta-captured payload after stripping IDs/timestamps |
| 2 | `researcher-web-mcp` | `web_scrape` (Firecrawl scrape), `firecrawl_search` | Same — including handling of the Indonesian e-commerce page that broke Letta (the zero-width-space chunk-split case) |

The Indonesian e-commerce page test is **non-negotiable** — that exact payload
hung Letta's MCP client. If OpenClaw's client also hangs or chunks it
incorrectly, the spike aborts.

## Verification protocol

For each server:

1. **Bring server up alone** under the existing Letta `spike-compose` setup; capture 5 representative tool-call responses to `fidelity-baseline/<server>/<tool>-<N>.json` after redacting IDs/timestamps.
2. **Switch to OpenClaw**: connect the same MCP server to a single OpenClaw Gateway via the chat REPL.
3. **Drive the same 5 calls** with the same arguments.
4. **Diff** against the baseline. Any structural delta (missing fields, type changes, truncated content) is a fail.
5. **Run the unicode chunk-split repro** specifically:
   - Capture the offending Indonesian e-commerce URL from `../week-1-spike/t5-researcher-urls.md` (search for the F-2 entry that hung Run-1-anthropic-direct)
   - Issue a `firecrawl_search` against the same query that returned it
   - Issue a `web_scrape` against the same URL
   - **Pass:** response returns cleanly within 60s
   - **Fail:** response hangs, errors, or truncates → abort spike per F-O1 escalation chain

## Transport decision matrix

Resolved against [docs.openclaw.ai/cli/mcp](https://docs.openclaw.ai/cli/mcp)
and [openclaw#55087](https://github.com/openclaw/openclaw/issues/55087) — see
[openclaw-facts.md](openclaw-facts.md) §"Open question 1":

| Transport | OpenClaw version | Maturity | Decision |
|---|---|---|---|
| **stdio** | always supported | high — broad test coverage | **Default for T4'.** Both Nextcloud-MCP and Firecrawl-MCP are spawned as stdio child processes via openclaw.json `mcp.servers[].command` |
| **streamable-http** | shipped 2026.3.31 (~7 weeks before this spike) | medium — newer code path | Test second, only if stdio has a structural issue |
| **SSE** | shipped earlier | medium-high | Test third — semantically similar to streamable-http but older transport |

**Decision: stdio for T4'.** Rationale — Week 1's Letta hang was in
`mcp.client.streamable_http`'s SSE-parse. If the upstream MCP SDK has a
class-level bug there, OpenClaw's streamable-http path (also 7 weeks old)
could share the risk. Stdio bypasses that entirely.

## Outputs

- `fidelity-baseline/` — Letta-side captured responses (5 per tool × 5 tools = 25 files)
- `fidelity-openclaw/` — OpenClaw-side captured responses (same count)
- `fidelity-diff.md` — line-by-line diff summary, pass/fail per tool
- Verdict line at the top of this file once run, with a one-sentence "proceed/abort" call

## Cross-references

- Week 1 MCP investigation that landed on `cbcoutinho/nextcloud-mcp-server`: [../week-1-spike/t4-mcp-investigation.md](../week-1-spike/t4-mcp-investigation.md)
- The streamable-http SSE-parse bug Letta surfaced: [../week-1-spike/t5-run-1-conclusions.md](../week-1-spike/t5-run-1-conclusions.md) (search "SSE-parse")
- Fallback if this fails: [t2-openclaw-fallback.md](t2-openclaw-fallback.md) F-O1
