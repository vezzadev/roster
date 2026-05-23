# Run 2 Conclusions Addendum — 2-agent re-runs with periodic-tick driver

Reads what the two 2-agent re-runs validated about the structural driver fix
(periodic-tick fallback shipped in PR #39) for the F-1 / F-2 coordination gaps
identified in [t5-run-2-conclusions.md](t5-run-2-conclusions.md), and what they
did and didn't tell us about the gating 4-agent Run 2.

Parent: [t5-run-2-conclusions.md](t5-run-2-conclusions.md) (F-1 producer-pings,
F-2 EM-yield, F-3 4-agent registry). Ledger rows: [t5-run-ledger.md](t5-run-ledger.md)
`2-2agent-tickfix-1` + `2-2agent-tickfix-2`.

## Topline

**Driver fix loaded; the failure mode it targets didn't recur; therefore not directly proven.**

The periodic-tick fallback (`TICK_PERIOD_S=600` in `driver.py`, PR #39) ran
without error across two 2-agent re-runs. The Run 2-local-sandbox silent-write
deadlock did not happen — but it also could not have, because both agents
posted Talk messages on every turn and never went 10 minutes idle. The
structural fix is wired and harmless on the happy path; its specific deadlock-
breaking behavior remains untested against the failure mode it was added for.

The second from-scratch run produced **~123 KB of consultancy content** (all 5
research items + EM-absorbed analyst workstream) in ~35 minutes for **$19.66**
at **87.1% cache hit**. No `brief.md` synthesis — cap hit while the EM was
still drafting `analysis_competitive_gtm.md`.

Two infrastructure fixes shipped during the run: `wire-run-2.py` dropped a
stale `researcher-web-mcp` MCP block (retired in PR #36, missed in PR #39's
4-agent expansion); `docker-compose.yml` loosened the analyst-b token
interpolation from `:?` to `:-` so the 2-agent subset can parse the compose
file without an `analyst-b-token.local` stub.

## Run 2-2agent-tickfix-1 — periodic-tick smoke (15 min, hit Firecrawl ceiling)

| | |
|---|---|
| Started | 2026-05-23 14:36:38 UTC (kickoff to EM `agent-157f9e97…`) |
| Stopped | 2026-05-23 14:55:19 UTC (SIGTERM after 15-min cap reached) |
| Wall   | ~19 min total (driver ran 14:39:56 → 14:55:19 ≈ 15:23) |
| Config | `HARD_CAP_S=900 TICK_PERIOD_S=600`, 2-agent ablation via `WIRE_AGENTS=em,researcher` |
| Agents | EM (Opus 4.7, reasoner off) + Researcher (Sonnet 4.6) on fresh per-agent Letta volumes |
| Talk   | Reused Run-1-anthropic-direct rooms (`ygeug4an` #team, `fz99hp5a` EM-Researcher); driver state seeded to max_id 331/330 to avoid replaying prior session history |
| Output | `/agents/research/A-indonesia-3pl-landscape.md` (10.4 KB) + `scaffold.md` (9.1 KB) + `researcher-urls-log.md` (2.7 KB) |

**Course of run.** EM detected `/agents/` was empty (had been wiped pre-run),
posted to `#team` calling out the file-persistence issue; Researcher
re-attempted Thread A with explicit write-then-read-back verification (201
write + 200 read, byte counts cited inline). Mid-run, Researcher exhausted the
Firecrawl key's monthly credit budget; reported it honestly in DM ("Both my
fetch tools — `web_scrape` and `firecrawl_search` — run on Firecrawl
infrastructure; no non-Firecrawl fallback"); EM acknowledged and escalated to
the founder via #team. Both agents stood down cleanly.

**Driver behavior.** Three urlopen-level 300 s timeouts during long agent
turns (Letta continued processing on its side; the driver moved to the next
poll cycle). Every Talk message produced a wake on the corresponding peer
agent. **No tick fired** — agents were chatty enough that idle-since-last-wake
stayed under 600 s the whole run.

**Cost data lost.** Both agents were deleted before token totals were
extracted; Letta's per-step usage is bound to the agent, so cancellation
removed the run history. Eyeball estimate from the second run's per-minute
rate (≈ $0.55/min): **~$8–9**.

## Run 2-2agent-tickfix-2 — from-scratch with new Firecrawl key (35 min)

| | |
|---|---|
| Started | 2026-05-23 14:57:49 UTC (kickoff to fresh EM `agent-ab07a6f6…`) |
| Stopped | 2026-05-23 15:34:52 UTC (driver hit `HARD_CAP_S=1800` then ran 5 min over while urlopens unwound) |
| Wall   | ~37 min |
| Config | `HARD_CAP_S=1800 TICK_PERIOD_S=600`, 2-agent ablation; new `firecrawl.local` key |
| Reset  | Letta agents deleted + recreated; `/agents/` wiped; `#team`/`EM-Researcher` rooms deleted + recreated (new tokens `28yo5khw` / `9t882cmz`); driver-state cleared; sandbox `FIRECRAWL_API_KEY` PATCHed via `wire-local-tools.py` |
| Agents | EM=`agent-ab07a6f6-6478-4f70-9670-dd2331d8f34c` (Opus 4.7, reasoner off); Researcher=`agent-fa7c8e2b-4c3f-4f46-897e-c8e5fcd98742` (Sonnet 4.6) |

**Output** (`/agents/`, 7 files, ~123 KB):

| File | Bytes | Owner |
|---|---:|---|
| `research_market_structure.md`  | 13,201 | Researcher (Item 1) |
| `research_competitive.md`       | 21,017 | Researcher (Item 2) |
| `research_buyside.md`           | 10,910 | Researcher (Item 3) |
| `research_regulatory.md`        | 19,510 | Researcher (Item 4) |
| `research_macro.md`             | 21,471 | Researcher (Item 5) |
| `analysis_competitive_gtm.md`   | 18,002 | **EM** (absorbed Analyst A's workstream — see F-4 below) |
| `researcher-urls-log.md`        | 14,840 | Researcher (citation log) |

**Course of run.** EM posted a detailed kickoff brief: framed the decision
question sharply ("does a sub-$10M ARR US SaaS company have a defensible path
to ≥$1M Indonesia ARR within 24 months at acceptable CAC payback"); split
workstreams across Researcher (5 items) and Analyst A (competitive/GTM);
paused for clarifying questions. Researcher acknowledged with two sensible
flags (ALFI sizing fuzziness, Waresix consolidation framing), then shipped
Items 1+2 → 3+4 → 5 in three batches, each followed by a Talk announcement and
the EM's read-and-integrate response. The EM identified Analyst A as
unresponsive after the kickoff dispatch ("Analyst A has gone silent through
three nudges. Treating them as unavailable. I'm absorbing the competitive/GTM
analysis workstream myself") and produced `analysis_competitive_gtm.md` itself
— recommendation: enter via EOR-led local sales (1 Bahasa-native AE + 1 SDR on
Deel/Remote) with a year-2 PT PMA trigger.

**Substantive findings emerging in messages** (sample, not exhaustive):

- PT PMA paid-up capital dropped IDR 10 B → 2.5 B (~USD 150 K) effective Oct
  2025 — flagged by EM as "materially moving working recommendation."
- Vietnam regulatory complexity is *higher* than Indonesia's, not lower
  (counterintuitive; supports Indonesia case vs ASEAN alternates).
- Indonesian SMB SaaS pricing anchor: Mekari Jurnal IDR 399 K–1.17 M/month
  (USD 24–71/month). Mekari Qontak CRM IDR 750 K/month base.
- Logistics costs: 14.1% GDP domestic + 8.98% export ≈ 23.08% total.
- PR 68/2025 SPP-TDLN tightening — regulatory trend is more enforcement, not
  less ("Day-1-compliance argument" in the brief).

**Driver behavior.** Four urlopen-level 300 s timeouts (same shape as Run 1).
17 substantive Talk messages exchanged in #team (`9t882cmz` DM unused all
run). No tick fired — same reason as Run 1, agents stayed chatty.

## Cost

Aggregated from Letta `/v1/runs/{run_id}/steps` (one row per LLM step,
includes Anthropic native-client `cached_input_tokens` /
`cache_write_tokens`). Prices per million tokens (native Anthropic billing):

| Model           | input | output | cache read | cache write |
|-----------------|------:|-------:|-----------:|------------:|
| Opus 4.7        | $15.00| $75.00 |     $1.50  |     $18.75  |
| Sonnet 4.6      |  $3.00| $15.00 |     $0.30  |      $3.75  |

| Agent | Model | Steps | cache_read | cache_write | fresh in | out | Cost |
|---|---|---:|---:|---:|---:|---:|---:|
| EM         | Opus 4.7   |  34 |  1,366,984 |   342,994 |  64 |  21,428 | $10.09 |
| Researcher | Sonnet 4.6 | 141 | 10,209,968 | 1,370,219 | 151 |  91,290 |  $9.57 |
| **Total**  |            | **175** | **11,576,952** | **1,713,213** | **215** | **112,718** | **$19.66** |

Cache hit (`cache_read` ÷ `prompt_tokens`): EM 79.9%, Researcher 88.2%, total
87.1%. Fresh-uncached input is single-digit tokens per step — every prompt
chunk lands in either the read or the write bucket because the Anthropic
client marks the whole context for caching.

Reference ratios:

- **`cache_read : in : out` = 103 : 15 : 1** (where `in` = `cache_write` +
  fresh; `cache_read` is the discounted bucket separate from those)
- **Input : output volume ≈ 118 : 1** (`prompt_tokens` ÷ `completion_tokens`)
- **Equivalent OpenRouter cost** (no cache discount, all `prompt_tokens`
  billed at full input rate): ~$220+. Native Anthropic + `cache_control`
  saved >90% on this workload.

Run 1's $1.66 (Run 1-anthropic-direct) used the same per-token economics but
ran for only ~23 minutes of compute before the MCP-framing halt; the 2-agent
rerun ran ~35 minutes against a substantially larger working set
(~123 KB output + 5 deep research bundles) and lands at a proportional
multiple.

## Findings

### F-4. EM persona absorbs missing-agent workstreams gracefully

The system-prompt frame is the 4-agent team. In 2-agent ablation mode the
Analysts simply never wake. The EM detected this ("Analyst A has gone silent
through three nudges. Treating them as unavailable") and reorganized the work
plan unilaterally — produced the analyst-grade `analysis_competitive_gtm.md`
itself rather than blocking on a teammate that doesn't exist. This is
emergent recovery, not a hard-coded persona rule. Worth keeping in mind for
the 4-agent gating run: if either Analyst is slow rather than absent, the EM
may absorb their workstream and reduce Analyst output rather than wait.

### F-5. urlopen 300 s timeouts on long agent turns are harmless but noisy

`driver.py:wake_agent` POSTs to `/v1/agents/<id>/messages` with `timeout=300`.
Long Opus turns (10–30 step kickoffs, 7K+ completion tokens) sometimes blow
through 300 s before Letta returns. The driver gives up the urlopen and
moves to the next poll cycle; Letta continues processing on its side and
returns whenever it's done (subsequent `talk_get_messages` polls see the
posted result). This produced 3 + 4 = 7 `HTTP 0 TimeoutError` lines across
the two runs. None broke the loop because the agent's response eventually
materialized in Talk and the driver woke the peer normally. Decision: leave
as-is for the spike; consider raising timeout to 600 s or moving wakes to a
fire-and-forget queue in v1.

### F-6. Periodic tick is structural insurance, not a behavior shaper

The original goal was to break Run 2-local-sandbox-style deadlocks (producer
writes silently, EM has nothing to poll). In both re-runs the producer always
posted on every write, so the tick was never needed. The fallback is wired
correctly (verified by `driver started — watching ... (cap 1800s, tick 600s).`
log line and by the load-rooms relevance filter handling the 2-agent subset)
but the deadlock-breaking behavior is unproven against the actual failure
mode. To validate it directly we'd need either (a) a forced-silence test
(post a "do not post Talk" instruction and observe the tick fire after 10
min) or (b) a much longer cap that includes natural quiet phases. Neither is
in scope for the current 2-agent ablation.

## Infrastructure fixes shipped mid-run

Both should land in a small follow-up PR before the 4-agent gating run:

1. **`wire-run-2.py`: drop `researcher-web-mcp` MCP block.** PR #36 retired
   the sidecar in favor of LOCAL-sandbox CUSTOM tools (`wire-local-tools.py`).
   Commit 27373ba removed the container but didn't update `wire-run-2.py`,
   which was created later by renaming `wire-run-1.py`. The Researcher's
   `mcps` list still pointed at `researcher-web` and the script errored with
   `MISSING TOOLS on 'researcher-web': ['web_scrape', 'web_search']`. Edit
   here drops the stale entry; `RESEARCHER_WEB_TOOLS` constant removed.

2. **`docker-compose.yml`: loosen `ANALYST_B_APP_TOKEN` interpolation.**
   Was `${ANALYST_B_APP_TOKEN:?run ./bring-up.sh — sources ./analyst-b-token.local}`,
   which fired at compose-parse time for any `up -d ...` command, regardless
   of whether the analyst-b service was being started. Changed to
   `${ANALYST_B_APP_TOKEN:-}` — fail-loud moves into the MCP container's
   own runtime (it will 401 on the first Nextcloud call if the token is
   empty). This lets the 2-agent subset bring up without `analyst-b-token.local`
   existing. `provision-analyst-b.sh` still writes the real token before the
   4-agent run.

## Open items for 4-agent Run 2 gating

1. **Commit the two infra fixes** above as a small PR (touched files:
   `docker-compose.yml`, `wire-run-2.py`).
2. **Run `provision-analyst-b.sh`** to create the analyst-b Nextcloud user and
   generate `analyst-b-token.local`.
3. **Run `setup-run-2-talk-rooms.py`** to create the 5 analyst-DM rooms
   (EM-A, EM-B, A-B, A-Researcher, B-Researcher) and add analysts to #team.
   Will recreate any 404'd tokens from prior runs.
4. **Bring up the 4-agent stack**: `letta-analyst-a`, `letta-analyst-b`,
   `nextcloud-mcp-analyst-a`, `nextcloud-mcp-analyst-b` (in addition to the
   2-agent subset already validated).
5. **Wire 4 agents** via `wire-run-2.py` without `WIRE_AGENTS` filter.
   `wire-local-tools.py` only attaches Firecrawl tools to the Researcher
   (correct by design — analysts shouldn't have web access).
6. **Set a longer cap** (`HARD_CAP_S=3600` minimum, possibly 5400) so the
   brief synthesis phase actually fires. The 2-agent rerun never reached
   `brief.md` because all 35 min were spent in research/analysis production.
7. **Decide on tick validation.** Either accept the structural fix as
   wired-but-unproven and move on, or schedule a deliberate forced-silence
   test before the gating run.

## Run 2-4agent-attempt-1 (halted 2026-05-23 18:24 UTC)

First 4-agent boot. Driver up 5400s cap / 600s tick, all 4 agents wired, native Anthropic, OTel-instrumented. Halted at T+67 min. Cap not reached.

**Decision (2026-05-23): halt entirely; do not restart until F-8 (originally suspected upstream, now reattributed to Roster-side OTel auto-instrumentation — see addendum below) is resolved.** F-7 share fix was applied + analyst work migrated into admin's `/agents/` so the analyses aren't lost. Letta + MCP + OTel containers stopped; Nextcloud + db left up for post-run review. The "Open items before Run 2-4agent-attempt-2" list below is a future-state checklist, not a here-and-now plan.

**Topline.** Tick mechanism proved itself in production — fired 11 times across all 4 agents (F-6 no longer "wired-but-unproven"). Both findings below are independent of the tick.

**F-7. `/agents/` is per-user, not shared across all 4 agent identities.**

Symptom: at halt, files were split across 3 separate Nextcloud user homes:

| User | Path | Content |
|---|---|---|
| admin | `/var/www/html/data/admin/files/agents/` | em_runplan (3KB), research_bundle1_logistics (7KB), research_bundle1_macro_digital (7KB), research_bundle1_regulatory (12.6KB), researcher-urls-log (2.4KB) |
| analyst-a | `/var/www/html/data/analyst-a/files/agents/` | analysis_competitive_gtm (17KB) |
| analyst-b | `/var/www/html/data/analyst-b/files/agents/` | analysis_entry_unit_econ (11.6KB) |
| em, researcher | (no `/agents/` folder of their own) | — |

Root cause: admin's `/agents/` was shared with em + researcher in the original Run 1 setup but the share was never extended to analyst-a + analyst-b. When their MCPs called `nc_webdav_write_file("/agents/...")`, the WebDAV `MKCOL` implicit in the write created a private `/agents/` directory in each analyst's own home. So analyst-a's competitive/GTM analysis (17KB) and analyst-b's unit-econ analysis (11.6KB) were invisible to EM, Researcher, and each other. The EM saw only Researcher bundles in its view of `/agents/`; both analysts saw only their own work.

This compounded the coordination tempo collapse: agents kept producing work locally, but each agent's WebDAV `nc_webdav_list_directory` returned a different file set, so cross-reads silently no-op'd. The tick mechanism kept agents moving but couldn't bridge the visibility gap.

Fix: extend the admin → em + researcher share to also include analyst-a + analyst-b with permission=31 (read+write+delete+share). One-shot via OCS Sharing API (no `occ share:create` exists). Pre-restart cleanup also needs to migrate the siloed work into admin's `/agents/`.

**F-8. Letta summarizer crash — `async_generator` not an async context manager (originally suspected upstream; addendum below reattributes to Roster-side OTel instrumentation).**

Symptom: `letta-researcher` + `letta-analyst-a` both crashed during context summarization (when conversation history grew large enough to trigger the summarizer):

```
File "/app/letta/interfaces/anthropic_parallel_tool_call_streaming_interface.py", line 249, in process
    async with stream:
TypeError: 'async_generator' object does not support the asynchronous context manager protocol
```

Stack: `summarizer._execute_summarizer_request` → `interface.process(stream)` → `async with stream:` where `stream` is an `async_generator` object (cannot be used with `async with` — needs to be an `AsyncContextManager`).

Affected: Letta 0.16.8 image (`spike-compose-letta-otel:latest` derived from upstream). Both Researcher and Analyst A hit it after ~30 min of conversation buildup. Analyst B and EM didn't trigger it within the window (smaller context).

Impact during the run: the agent loop crashed mid-step but Letta logged `Step Progression: FINISHED` and the run record persisted; subsequent ticks still hit Letta cleanly and returned partial results, but the agent could not compact its context (so kept growing it on every tick — costlier per call, and risks an eventual hard context-length exceeded).

### F-8 addendum (2026-05-23, post-halt isolation repro) — reattribution to Roster-side OTel

Per `run_failure_recovery_policy` the bug was first written up as upstream Letta. A standalone repro (`spike-compose/repro-f8.py`) ran the identical scenario against three images, single agent, `context_window_limit=32000`, 8 turns × ~12K-char filler each (~$1.20 burned over ~25 min):

| Image | `opentelemetry-instrumentation-anthropic` | Summarizer outcome |
|---|---|---|
| `letta/letta:latest` (vanilla, no OTel) | none | compacts cleanly — "Summarized 5: # Summary of Evicted Messages" |
| `spike-compose-letta-otel:latest` | `0.45.0` (Roster pin) | crash: `'async_generator' object does not support the asynchronous context manager protocol` |
| custom rebuild w/ instr bumped | `0.60.0` (latest) | crash: `'AnthropicAsyncStream' object does not support the asynchronous context manager protocol` |

Conclusion: the bug is **not** upstream Letta. It's `opentelemetry-instrumentation-anthropic` wrapping `client.beta.messages.create(stream=True)` such that the returned object no longer supports the `async with` protocol Letta's summarizer streaming interface requires. Bumping the instrumentation from 0.45.0 → 0.60.0 changed the wrapper type (`async_generator` → `AnthropicAsyncStream`) but did not restore the async-context-manager interface.

Vanilla `letta/letta:latest` — same Letta code, no OTel — handles the same workload cleanly. So this is a Roster-side observability-stack incompatibility, not a Letta-side defect.

Fix path (not applied in this PR per user direction): remove `opentelemetry-instrumentation-anthropic` from `Dockerfile.letta`; keep `opentelemetry-instrumentation-httpx` + `opentelemetry-instrumentation-fastapi`. Lose: Anthropic-specific `gen_ai.*` span attributes in App Insights. Keep: per-agent HTTP traces + FastAPI request spans. Restart Run 2 only after this lands.

Per `upstream_research_isolation` memory: not filing an issue upstream — there's nothing to file, the bug is on our side.

## Open items before Run 2-4agent-attempt-2

1. **Pre-restart: extend `/agents/` share to all 4 agent users** with permission=31 via OCS Sharing API, and migrate analyst-a + analyst-b's siloed work into admin's `/agents/` so the analyses aren't lost.
2. **Apply F-8 fix**: drop `opentelemetry-instrumentation-anthropic` from `Dockerfile.letta` (the F-8 addendum repro confirmed it's the OTel anthropic wrapper, not upstream Letta). httpx + fastapi instrumentation stays.
3. **Standardize provisioning**: extend `provision-analyst-b.sh` (or `setup-run-2-talk-rooms.py`) to also set up the share. Future runs shouldn't depend on Run 1-era share state surviving wipes.
4. **Run 1's share was admin → em + researcher.** Document this for any future bring-up: a Run 2 4-agent rerun from a clean Nextcloud needs the share created from scratch, not just extended.
