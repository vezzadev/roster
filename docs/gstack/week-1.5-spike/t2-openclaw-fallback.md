# T2' — OpenClaw fallback bullets

Parent: [README.md](README.md) §T2'

30-min pre-spike exercise mirroring Week 1's
[../week-1-spike/t2-fallback-bullets.md](../week-1-spike/t2-fallback-bullets.md):
**3-4 alternatives per likely OpenClaw failure mode, lightest-first, each with
a terminal "stop and call it" exit.** Pre-commits the exits so motivated
reasoning can't extend the spike past its useful life.

Status: ⏳ drafted, not pre-committed (commit happens by founder sign-off
before T5' kickoff).

## F-O1 — MCP client framing bug (mirror of Week 1's streamable-http SSE hang)

Risk: OpenClaw's bundled MCP client has its own chunk-handling implementation;
nothing guarantees it won't have the same class of bug Letta's
`mcp.client.streamable_http` had on escaped unicode.

| # | Bullet | Cost | Exit condition |
|---|---|---|---|
| 1 | Pin every MCP server to **stdio transport** (Nextcloud-MCP + Firecrawl-MCP both support it) | 30min config | Stays in if streamable-http hangs surface; otherwise unused |
| 2 | Add a chunked-aware proxy in front of MCP server (re-buffers before forwarding) | 2h | If stdio doesn't work for some MCP (e.g. needs http) |
| 3 | Drop Firecrawl-MCP and call Firecrawl REST directly from a custom OpenClaw skill | 4h | If both transports hang on Firecrawl payloads |
| **🛑** | **All three bullets fail** | — | **Terminal exit:** MCP layer is the bottleneck, not the runtime. Conclude the spike with that finding, file upstream issues, halt Week 1.5. |

## F-O2 — Talk-message wake latency

**Reframed against [openclaw-facts.md](openclaw-facts.md) §"Open question 2".**
OpenClaw is **message-driven**, not heartbeat-bound — inbound channel events
trigger turns immediately. The original "30-min lag" framing was wrong.

The real F-O2 risk is the *bridge* between Nextcloud Talk (not a native
OpenClaw channel) and the OpenClaw agent loop. Talk messages reach the agent
via the nextcloud-mcp server's `messages_list` tool, which is a **pull**, not
a push. The agent only knows about new messages when it polls the tool — and
that polling cadence is what `heartbeat.every` actually controls in our setup.

| # | Bullet | Cost | Exit condition |
|---|---|---|---|
| 1 | Heartbeat `every: 5m` triggers Talk polling 12× per hour per agent | 5min config | Default first attempt |
| 2 | Author a thin webhook bridge: Nextcloud Talk push → OpenClaw `hooks` endpoint → forced agent turn | 4h | If 5-min polling latency is unworkable |
| 3 | Use OpenClaw's native Slack channel and migrate Talk → Slack for inter-agent comms (breaks the "Talk is the substrate" decision but works) | 1d | If the webhook bridge can't be made reliable |
| **🛑** | **None of the above achieve sub-5-min inter-agent latency within SC#6 budget** | — | **Terminal exit:** Talk-as-MCP-tool integration is fundamentally too lossy. Conclude swap doesn't work, halt Week 1.5. |

## F-O3 — Memory fidelity gap (Markdown loses what Letta core blocks captured)

Risk: brief quality drops vs Week 1's runs because OpenClaw's Markdown-as-memory
doesn't surface the right facts at the right time — Letta's archival + recall
tool calls did targeted retrieval that flat Markdown doesn't replicate.

| # | Bullet | Cost | Exit condition |
|---|---|---|---|
| 1 | Use OpenClaw's built-in Markdown memory as-is — no augmentation | 0 | Baseline |
| 2 | Add a "scribe" skill: every turn, summarize key facts into structured YAML under `MEMORY.md`, query before each tool call | 1d | If baseline brief quality is below Run 1's |
| 3 | Bolt **Mem0** on as a memory skill: every assistant turn writes to Mem0, every user turn queries Mem0 first | 1.5d | If scribe approach undershoots — Mem0 has the LoCoMo numbers Letta competes against |
| **🛑** | **All three score below Run 1's `brief.md` on the AI panel rubric** | — | **Terminal exit:** OpenClaw can't match Letta on memory-sensitive workloads. Conclude runtime swap is net-negative, halt Week 1.5, keep Letta as v1 substrate with Letta-specific bug patches as Week 2 prerequisites. |

## F-O4 — Skill/tool gap (can't reach the Letta tool surface fast enough)

Risk: Letta agents had `archival_memory_insert`, `archival_memory_search`,
`core_memory_replace`, `send_message` plus the MCP servers. Reproducing each
under OpenClaw means authoring matching skills.

| # | Bullet | Cost | Exit condition |
|---|---|---|---|
| 1 | Use OpenClaw's built-in tools + the two existing MCP servers only — no custom skills | 0 | Baseline |
| 2 | Author a `nextcloud-mcp-host` skill that wraps the existing MCP server so it's reachable as a native OpenClaw tool (cosmetic, but reduces tool-call overhead) | 4h | If MCP-via-OpenClaw has detectable per-call latency penalty |
| 3 | Shell out to `mcp-cli` from within OpenClaw skills, treating OpenClaw as MCP host only and keeping all tool implementations in MCP servers | 1d | If skill authoring is the long pole |
| **🛑** | **Tool fidelity requires authoring >3 custom skills, each of which is a unaudited code path** | — | **Terminal exit:** the security review surface is too large; per the 26% community-skill vuln rate, this becomes a security spike, not a runtime spike. Halt Week 1.5, reconsider scope. |

## F-O5 — Cost blowout from heartbeat polling

Risk: every fired heartbeat is a model call even on `HEARTBEAT_OK`. Four
agents × 5-min heartbeat × 2h run = 96 polling calls per agent = 384 polling
calls across the team. At Opus Haiku pricing that's manageable; at Opus 4.7 for
the EM it isn't.

| # | Bullet | Cost | Exit condition |
|---|---|---|---|
| 1 | Use **Haiku 4.5** for all heartbeat-only checks (the "is anything in HEARTBEAT.md actionable?" yes/no), Opus/Sonnet only for actual work turns. Supported if OpenClaw allows per-call model override. | 1h | Default |
| 2 | Skip heartbeats entirely; rely on Talk-message wake (requires F-O2 #2 working) | 0 | If event-triggered runs work |
| 3 | Front-load most of the analysis into the 2 Senior Analysts (Sonnet) and downgrade the EM's heartbeat-check model only | 30min | Stopgap |
| **🛑** | **Heartbeat polling alone exceeds 30% of SC#6 budget** | — | **Terminal exit:** heartbeat economics make the swap structurally too expensive. Halt Week 1.5. |

## Cross-references

- Week 1 fallback that informed this structure: [../week-1-spike/t2-fallback-bullets.md](../week-1-spike/t2-fallback-bullets.md)
- Motivated-reasoning trap rationale (Codex T2): [../week-1-spike/t2-fallback-bullets.md](../week-1-spike/t2-fallback-bullets.md) preamble
