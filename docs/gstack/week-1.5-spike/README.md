# Week 1.5 Spike — OpenClaw runtime swap

Parent: [../week-1-spike/README.md](../week-1-spike/README.md) · Origin: Run-2-4agent halt
at T+67 (F-7 share gap + F-8 OTel anthropic-wrap summarizer crash) +
Run-1-anthropic-direct halt on MCP streamable-http SSE-parse bug.

**Status:** **closed 2026-05-23**, see [spike-conclusions.md](spike-conclusions.md).
Verdict — Nextcloud Talk viable for agent comms; OpenClaw is the runtime
(Letta retired); cost optimization is the gating Week 2 prerequisite.
Run 2' (4-agent SC#5 artifact) deferred until cost-opt lands.

## Why a 1.5 (not pivot, not Week 2)

Week 1 has now produced **four distinct upstream-Letta failures** blocking the
SC#5 4-agent run:

| # | Bug | Impact | Disposition |
|---|---|---|---|
| 1 | OpenRouter `cache_control` not injected ([letta-ai/letta#3351](https://github.com/letta-ai/letta/issues/3351)) | 0% cache hit, $57.87 Run 1 cost | Sidestepped via native Anthropic |
| 2 | MCP streamable-http SSE chunk-split on escaped unicode | Researcher hangs permanently | Halted Run 1-anthropic-direct |
| 3 | F-7 share gap — producer messages not surfaced to consumer | EM-Researcher coordination breaks | Driver-side patch pending |
| 4 | F-8 summarizer crash under OTel anthropic instrumentation | Letta crashes mid-run when context fills | Halted Run-2-4agent at T+67 |

The empirical conclusion is structural, not transient: **Letta's request-driven
agent model + bundled MCP client + summarizer + observability wrap form a
brittle stack on this workload.** Each fix has exposed the next bug.

OpenClaw inverts the model — **heartbeat-driven** rather than request-driven,
**file-backed** memory rather than block/archival, **Node.js Gateway** rather
than Python container, and **MCP through a different client.** Different bugs,
maybe; different category of bugs, possibly. Worth one structured swap before
either (a) shipping another round of Letta patches upstream or (b) declaring
the runtime unfit per T2 fallback bullets.

## What stays identical (the "same benchmark" contract)

The whole point of a 1.5 is that **the gate doesn't move**. Anything Week 1
authored that defines what "pass" means is reused verbatim:

- **SC#5 (4-agent team produces analyst-grade brief)** — unchanged
- **SC#6 ($200/mo budget)** — unchanged
- **Workload** — Indonesia 3PL market-entry brief, same prompt frozen
- **Grading rubric** — [../week-1-spike/t1-grading-rubric.md](../week-1-spike/t1-grading-rubric.md), reused verbatim
- **AI opinion panel** — same prompts, same reviewers, same blind protocol
- **Contamination guard** — three-layer threat model + Researcher domain blocklist + Nextcloud folder split, all unchanged
- **Team composition** — EM (Opus 4.7) + 2 Senior Analysts (Sonnet 4.6) + Researcher (Sonnet 4.6)
- **Inter-agent channel** — Nextcloud Talk via `cbcoutinho/nextcloud-mcp-server` (Talk is a tool to OpenClaw, same as it was to Letta)
- **Researcher tools** — Firecrawl-backed `researcher-web-mcp`, unchanged
- **Model provider** — native Anthropic (sidesteps #3351, validated in Run 1-anthropic-direct)
- **Cost backend** — Azure App Insights + KQL queries under `spike-compose/kql/`, reused unchanged

## What changes (the substitution map)

Verified against [openclaw-facts.md](openclaw-facts.md) — the substitution map
below replaces the first-draft version, which incorrectly assumed 4 separate
Gateway containers.

| Layer | Week 1 (Letta) | Week 1.5 (OpenClaw) |
|---|---|---|
| **Process topology** | 4 Letta containers + driver + MCP sidecars | **1 Gateway** hosting 4 agents via `agents.list` + MCP sidecars (no driver) |
| **Agent identity** | Per-container Postgres + system prompt | Per-agent `id` + `workspace` in `openclaw.json`; one Gateway routes all |
| **Memory** | Core blocks + archival + recall (LLM tool-managed) | Per-agent workspace dir (file layout is convention, not spec) — optional Mem0 skill if F-O3 escalates |
| **Wake model** | Request-driven + sleep-time compute + driver poll | **Message-driven** (channel events trigger turns) + heartbeat as fallback |
| **Agent kickoff** | `wire-run-N.py` + `driver.py` Talk relay | Render `openclaw.json` from template, mount, start Gateway |
| **MCP client** | Bundled `mcp.client.streamable_http` (the bug) | OpenClaw 2026.3.31+ supports stdio + SSE + streamable-http; T4' tests stdio first |
| **Prompt caching** | Custom patches; only `anthropic_client.py` path works | **Structural** — auto-on for Anthropic API-key auth, `cacheRetention: "short"\|"long"\|"none"` per model |
| **Cancel surface** | `DELETE /v1/runs/<id>` (broken under SSE hangs) | Gateway stop / kill; workspace files survive |
| **Blast radius on crash** | One container = one agent down | One Gateway crash = all 4 agents down → T6' more consequential |

The driver replacement is still the biggest structural delta. Letta needed
`driver.py` to poll Talk and forward messages because Letta agents only act on
request. OpenClaw agents are message-driven: an inbound Talk message triggers
an immediate agent turn, and the heartbeat is only the fallback for self-checks
when nothing's inbound. The Talk room remains the coordination substrate.

## Gating decision (unchanged from Week 1)

If the 4-agent OpenClaw team produces a brief that scores ≥ the rubric's pass
threshold under the AI opinion panel, **proceed to Week 2** with OpenClaw as
the v1 runtime (Letta optional fallback for memory-rich identities). If it
fails, the conclusion across both runtimes is that *runtime choice was not the
bottleneck*, and Week 1's [t2-fallback-bullets.md](../week-1-spike/t2-fallback-bullets.md)
applies — pivot or stop.

## Observability parity (the "same level of onset ability" requirement)

OpenClaw's Gateway is Node 22+, not Python. Letta's OTel instrumentation
(`spike-compose/Dockerfile.letta` + `spike-compose/docker-compose.otel.yml`)
relies on `opentelemetry-instrument` Python auto-wrap. The Node equivalent is
`@opentelemetry/auto-instrumentations-node` loaded via `--require`. **T9'
exists specifically to validate** that the Node path produces the same span
schema the existing KQL queries already consume.

Required parity matrix:

| Signal | KQL query | Source | Status |
|---|---|---|---|
| Per-agent token cost rollup | `kql/03-per-agent-cost.kql` | `gen_ai.usage.input_tokens`, `gen_ai.usage.cache_read_input_tokens` | T9' validates |
| Cache hit rate | `kql/03-per-agent-cost.kql` derived | same | T9' validates |
| Tool-call latency histogram | `kql/04-tool-latency.kql` (to author) | `mcp.tool.name` + duration | T9' validates |
| Inter-agent message trace | event timeline reconstruction | Talk MCP spans | T9' validates |
| Heartbeat firing pattern | new query | OpenClaw-specific span name TBD | T9' validates |

**Hard requirement:** if `kql/03-per-agent-cost.kql` returns rows with
populated cache_read columns for OpenClaw runs, observability parity is
declared. If not, T9' is the spike-blocker and we don't kick off T5'.

## Task → file map

| Task | Effort (human / CC) | Owning file | Status |
|------|---------------------|-------------|--------|
| T1' | 0h / 0min | reuse [../week-1-spike/t1-grading-rubric.md](../week-1-spike/t1-grading-rubric.md) | ✅ no change needed |
| T2' | 30min / 5min | [t2-openclaw-fallback.md](t2-openclaw-fallback.md) | ✅ drafted (revised against verified facts) |
| T3' | 2h / 30min | this folder + [spike-compose-openclaw/](spike-compose-openclaw/) | 🟡 skeleton landed; final config pending |
| T4' | 1d / 2h | [t4-openclaw-mcp-fidelity.md](t4-openclaw-mcp-fidelity.md) | ⏳ blocker for T5' |
| T5' | 2d / 4h | [t5-openclaw-run-ledger.md](t5-openclaw-run-ledger.md) + per-run conclusion files | ⏳ blocked on T4' + T9' |
| T6' | 30min / 5min | [t5-openclaw-run-ledger.md](t5-openclaw-run-ledger.md) "Forced SPOF" section | ⏳ during T5' Run 2' |
| T7' | 1h / 15min | [t7-openclaw-cost.md](t7-openclaw-cost.md) + exports | ⏳ produced by T5' |
| T8' | 2h / 30min | [t8-openclaw-brief.md](t8-openclaw-brief.md) + AI panel review | ⏳ post-Run-2' |
| **T9'** | 1d / 3h | [t9-otel-parity.md](t9-otel-parity.md) | ⏳ **spike-blocker** |
| — | 1h / 30min | [openclaw-facts.md](openclaw-facts.md) | ✅ done — docs-anchored verification of all 5 open questions |

## Task summaries

### T1' — Grading rubric

No change. Same rubric, same panel, same blind protocol. If the 1.5 brief
beats Run 1's `run1-artifacts/brief.md` on the same dimensions, the swap is
justified. If it doesn't, runtime was not the bottleneck.

End-to-end check execution (self-grade + URL audit + AI panel + 7-gram):
[t1-checks-report.md](t1-checks-report.md). Headline so far — Letta Run 1
clears the strong-positive gate; OpenClaw Run 1'-mg fails on D6 (risks
without paired mitigations). Run 2' must re-run all four checks before any
architecture verdict.

### T2' — Fallback bullets (OpenClaw-specific)

30-min pre-spike exercise mirroring Week 1's T2. Anticipated OpenClaw failure
modes:

- **F-O1**: MCP client in OpenClaw has its own SSE/streamable-http bugs (different from Letta's, but possible) → fallback: pin MCP servers to stdio transport only
- **F-O2**: Heartbeat scheduler can't be made fast enough for inter-agent latency targets → fallback: lower heartbeat to 5 min, accept token cost increase
- **F-O3**: Memory fidelity gap — Markdown + Mem0 misses what Letta core blocks captured → fallback: add a "scribe" skill that summarizes into structured YAML on every turn
- **F-O4**: Skills can't be authored fast enough to match Letta tool surface → fallback: shell out to existing MCP servers via `mcp-cli`, treat OpenClaw as MCP host only

Each with a terminal exit per the T2 motivated-reasoning trap mitigation.

### T3' — Folder scaffold + compose

Create:
- `spike-compose-openclaw/docker-compose.yml` — 4 OpenClaw Gateway services + Nextcloud + MCP sidecars + OTel collector (reuse `../week-1-spike/spike-compose/otel-collector/`)
- `spike-compose-openclaw/Dockerfile.openclaw` — Node 22+ base + OpenClaw install + `@opentelemetry/auto-instrumentations-node`
- `spike-compose-openclaw/wire-openclaw.sh` — per-agent workspace seed (AGENTS.md, SOUL.md, MEMORY.md, HEARTBEAT.md, TOOLS.md) replacing Letta's `wire-run-N.py`
- Per-agent workspaces under `spike-compose-openclaw/agents/{em,senior-a,senior-b,researcher}/`

Pin OpenClaw to **≥ 2026.1.29** to avoid CVE-2026-25253. Bind Gateway control
plane (`:18789`) to the docker network only, not host. No public exposure.

### T4' — OpenClaw MCP fidelity check (spike-blocker)

Two MCP servers from Week 1 must work under OpenClaw with the same fidelity:

1. `cbcoutinho/nextcloud-mcp-server` — Talk send/read + Files CRUD
2. `researcher-web-mcp` — Firecrawl scrape + search with Run 1's domain blocklist

Verification protocol:
- Connect each MCP server to a single OpenClaw Gateway via the same transport Letta used (streamable-http if supported, stdio fallback)
- Drive 20 calls per server from the OpenClaw chat REPL
- Compare response shapes byte-for-byte against the Letta-side captures in `../week-1-spike/spike-compose/run-2-4agent/` artifacts
- If OpenClaw's MCP client also chunk-splits unicode the way Letta's does, **abort the spike** — that's a category-level bug, not a runtime-specific one

This is the gate. If T4' passes, T5' can boot. If it fails, the spike conclusion
is that the MCP layer (not Letta or OpenClaw) is the bottleneck, and Week 1.5
ends with that finding.

### T5' — Spike runs

Same numbered-run + frozen-prompt protocol as Week 1's T5:

- **Run 1' — 2-agent smoke (45 min hard cap)** — EM + Researcher only, same ablation control Week 1 ran. Success criterion: at least one full turn-cycle without F-O1/F-O2 surfacing.
- **Run 2' — 4-agent main spike (2h hard cap)** — full team. Produces `t8-openclaw-brief.md`. This is the SC#5 artifact.

Reuse the per-run frozen prompts from
[../week-1-spike/t5-system-prompts.md](../week-1-spike/t5-system-prompts.md)
**verbatim** with two mechanical edits: (a) channel-tool name references
swapped to whatever OpenClaw exposes, (b) the "send messages on a tick" line
removed since OpenClaw heartbeats provide it structurally.

### T6' — Forced SPOF

During Run 2', `kill -9` one OpenClaw Gateway mid-flight. Observe:
- File-backed state survives (expected — `~/.openclaw/` and workspace Markdown are durable)
- Heartbeat resumes on Gateway restart
- Outstanding tool calls are not orphaned (open question — Letta's were postgres-orphaned and uncancellable)

Land verdict in `t5-openclaw-run-ledger.md` "Forced SPOF" section.

### T7' — Cost tracking

Reuse Run-1-anthropic-direct's per-call instrumentation. Pulls cost rollup
via the same KQL query. Expected: 4-agent team at the same cache hit rate as
Run-1-anthropic-direct (91.8%) lands in SC#6 budget. Heartbeat overhead is the
new unknown — every fired heartbeat is a model call even when the checklist
returns `HEARTBEAT_OK`. Track separately as `heartbeat_tokens` so we can
disentangle "work" vs "polling" cost.

### T8' — Gate decision

**Closed**, see [spike-conclusions.md](spike-conclusions.md). Verdict: Nextcloud
viable; OpenClaw is the runtime; cost optimization is the gating Week 2
prerequisite. Run 2' deferred until cost optimization lands —
running it on current per-agent-hour rate would burn ~$240 producing an
artifact whose runtime verdict is already settled.

### T9' — Observability parity (new, spike-blocker)

OpenClaw is Node, Week 1's OTel wrap was Python. Validate that:

1. `@opentelemetry/auto-instrumentations-node` produces spans with the
   `gen_ai.*` semantic conventions the KQL queries already consume
2. Anthropic SDK calls from Node emit `gen_ai.usage.cache_read_input_tokens`
   (the field that lights up Run-1-anthropic-direct's 91.8% cache hit rate)
3. MCP tool-call spans carry `mcp.tool.name` + duration

Acceptance test: run a 5-minute single-agent OpenClaw session against
Anthropic + one MCP server, then run `kql/03-per-agent-cost.kql` unchanged.
If rows return with populated cache columns, **declare parity and unblock T5'**.
If not, T9' is the spike's actual deliverable — author whatever shim closes
the gap, and that shim becomes the v1 observability prerequisite.

## Calendar

5 working days target. Breakdown:

| Day | Work |
|---|---|
| D1 | T2' + T3' scaffold + T9' first-pass |
| D2 | T4' MCP fidelity check (gate — abort here if MCP layer is bottleneck) |
| D3 | T5' Run 1' smoke |
| D4 | T5' Run 2' main spike + T6' SPOF + T7' cost |
| D5 | T8' founder self-grade + multi-AI panel + gate decision |

If T9' isn't parity-validated by end of D1, it absorbs D2 and T4' slips to D3
— that's the realistic risk.

## Open questions — resolved

All five open questions have been answered against docs.openclaw.ai —
see [openclaw-facts.md](openclaw-facts.md) for the audit trail.

1. **MCP transport** — ✅ stdio + SSE + streamable-http (streamable-http shipped 2026.3.31). T4' tests stdio first.
2. **Wake latency** — ✅ message-driven, not heartbeat-bound. F-O2 reframed.
3. **Memory hand-off** — ✅ fresh-start (recommendation stands; no upstream constraint either way).
4. **Skill catalog** — ✅ built-in tools + 2 MCP servers cover the workload; no community skills.
5. **Anthropic auth** — ✅ API key. Prompt caching is structural and on-by-default for API-key auth.

Remaining unverified:
- **CVE-2026-25253 patched-version pin** — needs CHANGELOG check before T3' finalize. Scaffold currently pins `≥ 2026.4.x`.
- **MCP tool-call span emission** — T9' validates empirically.
- **`HEARTBEAT.md` as a literal file** — possibly convention rather than runtime contract; T3' to verify.

## Cross-references

- Week 1 parent: [../week-1-spike/README.md](../week-1-spike/README.md)
- Failure trace that motivated this spike: [../week-1-spike/t5-run-2-conclusions.md](../week-1-spike/t5-run-2-conclusions.md) F-7 + F-8
- Run that proved cost path works on Anthropic native: [../week-1-spike/t5-run-1-conclusions.md](../week-1-spike/t5-run-1-conclusions.md) C-6
- Rubric (unchanged): [../week-1-spike/t1-grading-rubric.md](../week-1-spike/t1-grading-rubric.md)
- Fallback bullets (unchanged spirit, OpenClaw-specific instances in T2'): [../week-1-spike/t2-fallback-bullets.md](../week-1-spike/t2-fallback-bullets.md)
