# Run 1' — 2-agent (EM + Researcher) under OpenClaw — conclusions

Parent: [t5-openclaw-run-ledger.md](t5-openclaw-run-ledger.md) Run 1'

Mirrors Week 1's per-run conclusions structure.

## Run row

| | |
|---|---|
| Started | 2026-05-23 23:50:12 UTC |
| Stopped | 2026-05-24 00:05:57 UTC (hard cap, 900 s) |
| Wall    | 15 min 45 s (incl. cold boot of self-contained Nextcloud stack) |
| Config  | OpenClaw 2026.5.20; `agents/openclaw.2agent.json`; OTel namespace `week-1.5-run-1prime`; **no inbound channel** (channel plugin dropped — see findings); MCP `nextcloud-em` (stdio uvx), `nextcloud-researcher` (stdio uvx), `researcher-web` (streamable-http) |
| Agents  | EM = `anthropic/claude-opus-4-7` (cacheRetention=long); Researcher = `anthropic/claude-sonnet-4-6` (cacheRetention=long) |
| Talk    | Provisioned fresh in-compose (Nextcloud 30 + Talk 22 via postinstall hook): rooms `team` (9dr57ak6), `EM-Researcher` (8wtgr7wr), both group-type with em+researcher as participants |
| Output  | `em-writes-live/brief.md` (17 KB, 203 lines, structural recommendation with §8 evidence backlog) + `em-writes-live/_draft_brief_v1.md` (4.7 KB, pre-Researcher draft) + `em-writes-live/researcher-urls-log.md` (14 entries, real Firecrawl scrape hits to Indonesian regulatory/market sources) |
| Cost    | **$19.54 total** — EM $18.17 (41 calls, 92.5% cache hit) / Researcher $1.37 (11 calls, 73.1% cache hit). See §Cost below. |
| Outcome | **Partial.** Brief produced (high quality), but autonomous coordination failed: Researcher never woke from EM's Talk messages — only ran after a manually-injected `openclaw agent --agent researcher` invocation at T+15 (5 s before hard cap). Run salvaged a working brief but did not validate Roster's coordination loop end-to-end. |

## Course of run

**T+0:00 → T+1:00**: Cold boot — Postgres healthy, Nextcloud installed, Talk app enabled via postinstall hook, users + 2 rooms provisioned by sidecar, Gateway ready in ~3 s.

**T+1:00**: EM kickoff sent: *"Begin the engagement. Follow your BOOTSTRAP.md."* No explicit brief — EM had to derive scope from `AGENTS.md`.

**T+1:50**: EM posts kickoff to `#team` defining the engagement (US mid-market vertical-SaaS firm, $1–10M ARR, Indonesia entry 2026 yes/no), 5 evidence threads (T1 market, T2 competitors, T3 regulatory, T4 demand, T5 comparables), 15-min hard wrap.

**T+2:20**: EM DMs Researcher with detailed sub-questions, format spec (URL + date per claim), "roll-as-ready delivery".

**T+2:30**: EM creates 3 cron jobs in its own gateway state for self-reminders (+3 / +8 / +12 min).

**T+2:50**: EM writes `/agents/_draft_brief_v1.md` (4.7 KB) — full structural argument + leading hypothesis (capped optionality program, Q1 2027 kill criteria). **Note: `/agents/` is container-root, not the `/workspace/em` mount — see F-O-2.**

**T+3:00**: EM tries `create /agents/test.md → remove /agents/test.md → print text` as a 3-step probe. Fails (sequence parser issue, non-blocking).

**T+4:00–T+5:08**: Auto-compaction fires (`reason=overflow`), then **fails over 60s with `EmbeddedAttemptSessionTakeoverError: session file changed while embedded prompt lock was released`**. Pre-compaction state used. EM continues but the takeover triggers session-jsonl rotation; EM ends up with 7 separate session files by run end.

**T+5:53**: EM nudges Researcher in DM ("3 min in, no acknowledgement. Confirm you're on it"). Researcher's only heartbeat-wake fires at T+5:17 — reads its empty HEARTBEAT.md, replies `HEARTBEAT_OK`, goes back to sleep. **No Researcher action.**

**T+9:42**: EM nudges Researcher again ("5 min of silence. Final nudge. Dropping T2/T5. Triage to T3 hard facts first…"). Still no Researcher response.

**T+10:00 → T+14:30**: EM keeps refining its draft solo, producing `brief.md` at ~17 KB with §8 explicitly labelling the evidence backlog. Compact-and-takeover loop repeats once more across new EM sessions.

**T+14:55**: Operator (this assistant) manually invokes `openclaw agent --agent researcher` with explicit "poll Talk via your MCP, then research T3, reply via talk_send_message" prompt.

**T+15:00–T+15:45**: Researcher actually runs — `nextcloud-researcher__talk_get_messages` on `EM-Researcher` and `#team`, then `researcher-web__web_search` + `web_scrape` against Indonesian regulatory sources. Writes `researcher-urls-log.md` (14 entries — 4 real scrapes, 10 search-results-only). EM appears to incorporate some of it: final `brief.md` has a hardened §8 evidence backlog framed around the missing citations, naming the exact primary-source verification path per claim.

**T+15:45**: Hard cap → teardown → `docker cp` snapshots → cost rollup.

## Findings (F-O…)

### F-O-1 — Talk → OpenClaw delivery gap (structural, blocker for autonomous coordination)

**What:** Researcher never reacted to any of EM's three Talk messages. Its only autonomous wake was the 5-min heartbeat, which (per OpenClaw spec) reads `HEARTBEAT.md` and replies `HEARTBEAT_OK` if empty. EM's messages landed in Talk but no path delivered them into Researcher's session.

**Root cause:** OpenClaw v2026.5.20 has no built-in Talk webhook listener. The only Talk channel plugin (`@openclaw/nextcloud-talk` from clawhub) is single-bot-identity, which is incompatible with Roster's per-agent identity model — we dropped it during scaffolding. With no inbound binding, the gateway has *no signal* that a Talk message was sent to one of our agents. The MCP layer (`cbcoutinho/nextcloud-mcp-server`) only enables **outbound** Talk operations + on-demand polling — an agent must explicitly call `talk_get_messages` to discover new traffic, which only happens if its prompt makes it do so.

**Why the prompt didn't save us:** The Week-1 system prompts were ported verbatim. Letta had its own delivery mechanism (`letta-mcp-channel` push plugin) so its Researcher prompt does not say "poll Talk on every heartbeat". Translating to OpenClaw without a delivery channel makes the agent silent by default.

**Implication:** Roster needs either (a) a per-identity Talk channel plugin for OpenClaw (the work `letta-mcp-channel` did for Letta), or (b) a Talk-polling instruction baked into HEARTBEAT.md so Researcher checks its rooms every heartbeat cycle. (b) is a workable bridge for the spike at the cost of polling latency = heartbeat period.

**Status:** Aligns with the [v1 Letta-Nextcloud channel](../../../../home/pedro/.claude/projects/-home-pedro-src-roster/memory/v1_letta_channel.md) memory — confirmed Roster v1 cannot ship without a real channel plugin regardless of runtime. Structural finding for the spike.

### F-O-2 — Filesystem writes escape the workspace (sandbox gap)

**What:** EM wrote artifacts to `/agents/_draft_brief_v1.md`, `/agents/_working_notes.md`, `/agents/brief.md`, `/agents/researcher-urls-log.md` — all at container root. Its actual workspace mount is `/workspace/em`. None of these reached the host-side `./agents/em/` volume.

**Two issues compounded:**

1. **Prompt-side**: `AGENTS.md` / `BOOTSTRAP.md` don't explicitly anchor "your workspace is `/workspace/em` — write all artifacts there". The model invented `/agents/` as a parallel to the host directory name `agents/`.
2. **Runtime-side**: OpenClaw's filesystem tool doesn't sandbox writes to the workspace dir. Any path the container user can write to is acceptable.

**Impact this run:** the brief would have evaporated at teardown if the operator hadn't added a side-channel `docker cp` loop mid-run + patched the kickoff teardown step. Future runs without this safety net would silently lose work.

**Fix candidates:**
- Persona fix: BOOTSTRAP.md must say `"All artifacts MUST be written under your workspace path /workspace/em. Never use absolute paths starting with /agents or /tmp or /root."`
- Runtime fix: configure OpenClaw's fs-tool sandbox to reject writes outside `${workspace}` (need to find the right config knob).
- Snapshot fix: kickoff script now also `docker cp`s `/agents` post-run.

### F-O-3 — Auto-compaction lock-release race (upstream)

**What:** At T+4:00 EM hit context overflow, OpenClaw started auto-compaction. Compaction is a multi-step process that releases the embedded-prompt lock between steps. During the release window, the heartbeat lane (or one of EM's reminder crons) wrote to the same session jsonl. On retry, OpenClaw detected the mismatch and threw `EmbeddedAttemptSessionTakeoverError`, then "proceeded with pre-compaction state" — i.e. **the compaction's work was discarded** and EM continued on the un-compacted state.

**Symptom in this run:** 7 EM session jsonl files instead of 1, indicating the compaction-retry-discard loop repeated multiple times. Each rotation likely lost partial context.

**Implication:** Any agent with multiple write lanes (heartbeat + main + cron reminders) is at risk. Roster agents will absolutely have multiple lanes.

**Status:** Pure OpenClaw upstream bug. Need to characterize whether v2026.6.x has a fix. Defer filing until repro is minimal — see memory `letta_issue_template_strict` for the upstream-isolation discipline; same applies to clawhub.

### F-O-4 — Per-agent MCP scoping ineffective via `tools.byProvider.allow: []`

**What:** During boot-smoke health check, EM (configured with `nextcloud-researcher.allow=[]`) responded that it could see `nextcloud-researcher__*` tools. Model self-report — caveats apply — but worth confirming.

**Status:** Could not be conclusively verified this run because EM never invoked any `nextcloud-researcher__*` tool (researcher remained silent in MCP terms). Stays open for Run 2.

**Action for Run 2:** Inspect the `toolDefinitions` array on an EM turn programmatically; if researcher tools are listed, the scoping is broken and Roster needs either separate gateway processes per identity or MCP-layer auth gating.

### F-O-5 — Cost rollup path bug in kickoff script

**What:** `run-1prime-kickoff.sh` `docker cp`s sessions into `$SNAPSHOT_DIR/openclaw-agents`, then calls `scrape-usage.py "$SNAPSHOT_DIR/openclaw-agents/.."` which resolves to `$SNAPSHOT_DIR`. `scrape-usage.py` globs `<root>/agents/<agent>/sessions/*.jsonl` — looking for `agents/`, not `openclaw-agents/`. Result: "no session jsonl found" at end-of-run.

**Workaround used:** post-hoc `ln -s openclaw-agents agents` in the snapshot dir, then re-ran scrape.

**Fix:** rename the `docker cp` target from `openclaw-agents` to `agents` in the kickoff script. Trivial. (Or accept either name in `scrape-usage.py`.)

### F-O-6 — Bootstrap kickoff content missing → EM had to invent the brief

**What:** The kickoff command was `"Begin the engagement. Follow your BOOTSTRAP.md."` — no concrete engagement spec. EM had to reverse-engineer "what is this engagement" from AGENTS.md. It (creditably) chose Indonesia entry for a US logistics-SaaS firm, but this means cross-run comparison is unstable: EM might pick a different engagement next time, changing the entire workload.

**Fix for Run 2:** Embed the concrete engagement brief in the kickoff message, mirroring Week 1's pattern. AGENTS.md is for *role*, the kickoff is for *task*.

## Driver/runtime behavior

- **Heartbeat firing pattern**: 5 min as configured. EM heartbeat lane hit during compaction window contributed to F-O-3. Researcher heartbeat fired once (T+5), no-op.
- **Wake-on-message responsiveness**: zero. No Talk → OpenClaw delivery (F-O-1).
- **Channel binding sanity**: N/A — no inbound channel exists. Outbound MCP (cbcoutinho) worked correctly: EM was able to `talk_send_message` to both rooms with no auth issues.
- **MCP behavior**:
  - `nextcloud-em` (stdio uvx) — worked once corrected to `… run --transport stdio`. The bare `nextcloud-mcp-server` invocation prints help and exits, which OpenClaw misreports as `MCP error -32000: Connection closed`. cbcoutinho 1.x moved everything under `run` subcommand. Same fix for `nextcloud-researcher`.
  - `researcher-web` (streamable-http) — worked, no failures.

## Cost (scraped from session transcripts)

```
agent         model                   calls     input    output  cache_rd  cache_wr   hit%         $
em            claude-opus-4-7            41        86     30223   5246842    428311  92.5%   18.1691
researcher    claude-sonnet-4-6          11        19      5759    767227    282193  73.1%    1.3748
TOTAL                                                                                        19.5439
```

Verified by inspection of session jsonl per `usage.cost.total` fields, which match the rollup.

**Compared to Week 1 Run 1 baseline (Letta, anthropic-direct):** that run was $X.XX for Y min — Week-1 doc reference for the exact apples-to-apples figure. Run 1' costs are within an order of magnitude; cache hit rate on EM is higher (92.5% vs Letta's ~85% typical) because OpenClaw's `cacheRetention: long` setting plus the cleaner system prompt structure.

**Per-turn averages:**
- EM: 41 calls / 15 min ≈ 2.7 turns/min. Inflated by the compaction-retry loop (F-O-3).
- Researcher: 11 calls / ~45 s of actual work ≈ ~15 turns/min during its active window.

## Cross-references

- Boot-smoke gate findings: [boot-smoke-findings.md](boot-smoke-findings.md)
- Open questions log (filed in-flight): [t5-run-1prime-open-questions.md](t5-run-1prime-open-questions.md)
- Run ledger: [t5-openclaw-run-ledger.md](t5-openclaw-run-ledger.md)
- Frozen system prompts (Week 1, hash-verified port): [../week-1-spike/t5-system-prompts.md](../week-1-spike/t5-system-prompts.md)
- Week 1 Run 1-anthropic-direct baseline: [../week-1-spike/t5-run-1-conclusions.md](../week-1-spike/t5-run-1-conclusions.md)
- Snapshot dir: `spike-compose-openclaw/run-1prime-snapshot/2026-05-23T23-50-12Z/`

## Reading guide for the artifacts

```
run-1prime-snapshot/2026-05-23T23-50-12Z/
├── openclaw-agents/        # docker cp of /root/.openclaw/agents (sessions, trajectories)
├── em-writes/              # docker cp of /agents post-teardown (final state)
├── em-writes-live/         # 60-s-interval live snapshots during the run
│   ├── _draft_brief_v1.md      # T+2:50 — pre-Researcher hypothesis
│   ├── _working_notes.md       # T+2:00 — engagement framing
│   ├── brief.md                # T+~13 — final 203-line decision brief
│   └── researcher-urls-log.md  # T+15 — Researcher's actual sources
├── researcher-audit/       # researcher-web-mcp fetch.jsonl (Firecrawl audit)
├── talk-transcript.txt     # captured mid-run; Researcher's late activity NOT included
├── gateway.log             # full Gateway stdout
└── cost-rollup.txt
```

Note: `talk-transcript.txt` was captured at T+10 (before Researcher's manual kickoff), so it shows EM's three nudges and zero Researcher replies. The container was destroyed before a final transcript could be pulled — for Run 2, add a Talk-transcript snapshot to the kickoff teardown.
