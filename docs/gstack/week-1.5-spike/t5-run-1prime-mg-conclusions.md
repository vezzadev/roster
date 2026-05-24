# Run 1'-mg — 2-agent multi-gateway under OpenClaw — conclusions

Parent: [t5-openclaw-run-ledger.md](t5-openclaw-run-ledger.md) Run 1'-mg

Re-run of Run 1' under the N-gateway architecture introduced after [t5-run-1prime-conclusions.md](t5-run-1prime-conclusions.md) flagged F-O-1 (Talk → OpenClaw delivery gap) as a structural blocker. The architecture pivot: one OpenClaw process per agent, each agent a regular Nextcloud user, with a sidecar daemon (`nextcloud-talk-bridge`) that long-polls each user's Talk rooms via OCS and `docker exec`s `openclaw agent` on the right gateway. Mirrors what `letta-mcp-channel` does for the Letta side of Week 1.

## Run row

| | |
|---|---|
| Started | 2026-05-24 01:03:57 UTC |
| Stopped | 2026-05-24 01:20:03 UTC (hard cap, 900 s sleep + ~70 s teardown/snapshot) |
| Wall    | 16 min 06 s (incl. cold boot of the full self-contained stack) |
| Config  | OpenClaw 2026.5.20; per-agent configs `agents/openclaw.em.json` + `agents/openclaw.researcher.json`; OTel namespace `week-1.5-run-1prime-mg`; **bridge-based inbound** (no channel plugin); MCP `nextcloud-em` (stdio uvx, EM only), `nextcloud-researcher` (stdio uvx, Researcher only), `researcher-web` (streamable-http, Researcher only) |
| Agents  | EM = `anthropic/claude-opus-4-7` (cacheRetention=long); Researcher = `anthropic/claude-sonnet-4-6` (cacheRetention=long) — separate processes (`openclaw-em-run1prime-mg`, `openclaw-researcher-run1prime-mg`) |
| Talk    | Provisioned fresh in-compose: rooms `team` (zqt8zfz5, group, em+researcher+admin) and `EM-Researcher` (sgugiqvk, group, em+researcher). Admin added to `#team` so an external operator can post kickoff messages as a regular Talk participant — first thing the bridge has to deliver. |
| Output  | `em-writes/brief.md` (22 KB, **163 lines, 20 cited sources** — McEasy/GetLatka pricing, BPS 2024, ILFA 2023, OECD 2021, World Bank LPI 2023, BKPM Reg 5/2025, UU PDP, PMSE registry, PwC WHT) + `em-writes/brief-skeleton.md` + `em-writes/notes-frame.md` |
| Cost    | **$16.37 total** — EM $12.24 (31 calls, 91.9 % cache hit) / Researcher $4.13 (47 calls, 88.8 % cache hit). $3 cheaper than Run 1' single-process *despite* the F-O-8 duplicate-delivery spend below. |
| Outcome | **Success.** Autonomous Talk-mediated coordination loop closed end-to-end. EM drove the engagement, Researcher batch-delivered evidence, EM produced the final brief with locked recommendation and explicit go/no-go trigger. F-O-1 (the Run 1' blocker) verified fixed by the bridge architecture. Two new findings (F-O-7, F-O-8) opened on bridge-side polling semantics. |

## Course of run

**T+0:00 → T+0:51**: Cold boot — Postgres healthy, Nextcloud + Talk installed, sidecar provisions em + researcher + admin-to-team participants, both gateways reach `[gateway] ready` in ~5 s (em) and ~1 s (researcher), bridge alive.

**T+0:51**: Admin (operator stand-in) posts the engagement brief into `#team` via OCS REST — the same path a human operator would use. This is the F-O-6 fix: kickoff brief is baked into the kickoff script, no derived scope.

**T+1:00**: Bridge picks up admin's message, fans out to both em and researcher via `docker exec ... openclaw agent --session-id bridge-<agent>-<roomToken>`.

**T+1:10 → T+2:36**: EM's first turn — MCP cold-start (~22 s prep stage), then EM reads the brief, posts acknowledgement to `#team`, creates the **EM-Researcher** DM room (em's MCP `talk_create_room`), DMs Researcher with full scope + sequencing (Q1-Q9 questions, format spec, hard cap), and yields with *"Now I'll yield to wait for the Researcher's batches — push-based, no polling."* — explicit confirmation that the structural fix lets the agent stop polling.

**T+2:36**: Researcher's first delivery (admin's brief in `#team`) is still in flight inside the container. Bridge declares 180s timeout (false alarm — agent is still working; see F-O-8) and re-enqueues. Meanwhile, bridge discovers `EM-Researcher` room as new and **anchors at head id=61** rather than replaying from 0 (F-O-7 fix). Delivers EM's DM brief to Researcher in the EM-Researcher session.

**T+3:00 → T+11:00**: Researcher does the real work. Multiple Firecrawl scrapes against primary sources — GetLatka (McEasy revenue), Antara News (McEasy product), Vynn Capital report (competitive landscape), ILFA annual report (3,521 freight forwarders, 43 % Java concentration), OECD 2021 (3,000 + 1,000 unregistered), World Bank LPI 2023 (61/139, infra 2.9/5.0), BPS 2024 (66.17 % under IDR 2B, 27.52 % in 2–15B band, 83.44 % IT adoption), BKPM Reg 5/2025 (PT PMA IDR 2.5B paid-up + IDR 10B investment plan), ICLG (UU PDP enforcement, penalties), PMSE DJT (foreign-vendor VAT registry), McEasy public layanan page (pricing tiers), Scribd quote (Plus tier ~IDR 415K/vehicle/month). Posts evidence batches into `EM-Researcher` framed as `Q1 — Market sizing ✅`, `Q3 — Regulatory ✅`, …, each with citations and brief domain commentary.

**T+9:00 → T+15:00**: EM sequences the engagement actively in `EM-Researcher`: *"Q4 (competitive landscape) is the highest-leverage open question. Push on Q4 next, then Q5 (talent/dev costs) and Q8-10."* — engagement-manager behavior. Researcher returns Q4 (McEasy + Waresix/Shipper/Kargo distinction; ALFI vs JNE/J&T BPS-denominator caveat — research-grade nuance), Q5, Q9.

**T+13:30**: EM's first synthesis lands in `#team`: *"Holding the brief you posted here as a draft; final brief live."*

**T+14:20**: EM produces `brief.md` (22 KB, 163 lines) in `/agents/` (F-O-2 unchanged — workspace mount still bypassed; mitigated by snapshot loop).

**T+14:30**: EM posts the **locked recommendation** to `#team`: partner-led channel entry in 2026, hard go/no-go at end-Q3, trigger to defer to 2027 if no signed channel partner by end-Q1. Three driver facts with citations + cited compliance economics. Final line: *"Senior Analysts A and B were absent for this engagement; I covered depth."* — EM noticed the SA gap, called it out, didn't fake the work.

**T+15:00 → T+16:06**: Hard cap → teardown → `docker cp` snapshots of both gateways' `/agents` + agent session jsonl trees → bridge state → Talk transcripts → cost rollup.

## Findings (F-O…)

### F-O-1 — RESOLVED (verified fixed)

The bridge sidecar closes the Talk → OpenClaw inbound gap. Both agents responded to Talk traffic without any operator intervention. 12 cross-room messages handled by the bridge (1 admin + 6 em + 2 researcher in `#team`; 5 em + 7 researcher in `EM-Researcher`). Researcher correctly used `NO_REPLY` convention to avoid duplicate posts on heartbeat-driven wakes.

Architecture confirmed viable for Run 2' (4 agents) modulo F-O-8 below.

### F-O-7 — Nextcloud auto-provisions a "Talk updates ✅" room with backlog (bridge replay hazard)

**What:** First boot attempt of the multi-gateway stack: bridge started with empty state (`lastKnownMessageId = 0` per room), listed each agent's joined rooms — and found a `Talk updates ✅` room with ~20 pre-populated release-notes messages. Bridge dutifully delivered all of them to both agents as if they were live traffic, burning ~17 turns of tokens before halt.

**Root cause:** Nextcloud Talk auto-creates a `Talk updates ✅` room for every newly-provisioned user, seeded with release notes for each Talk version installed. A naive long-poller initialized at id=0 will replay the whole backlog. Same hazard applies to any room where the bridge's state was lost (e.g. volume wipe with rooms preserved at the Talk DB level — won't happen in spike, would happen in production).

**Fix:** [`nextcloud-talk-bridge/bridge.py`](spike-compose-openclaw/nextcloud-talk-bridge/bridge.py): on first sight of a room (no state for that token), anchor `lastKnownMessageId` to the current head from the room-list response's `lastMessage.id`, not 0. Verified on retry: 8 rooms anchored at head, zero backlog replays.

**Severity:** low (one-time spike-only cost; structural fix is one line of code).

### F-O-8 — Bridge synchronous 180 s timeout is a false alarm during MCP-cold-start turns (causes duplicate deliveries)

**What:** Three of 11 deliveries during the run hit the bridge's 180 s `subprocess.run` timeout. In every case the `openclaw agent` process inside the container was *still alive* and *still doing work* (verified via `/proc/<pid>/comm`). The bridge interpreted the timeout as failure, did **not** advance `lastKnownMessageId`, and re-delivered the same message on the next poll cycle — spawning a *second* `openclaw agent` invocation on the same session-id.

**Why the underlying process survives:** `docker exec` is a thin client; killing the client (when Python's `subprocess.run` raises `TimeoutExpired`) does **not** signal the in-container process. The container-side `openclaw agent` keeps running, attached to dockerd. Result: orphan turns burning tokens in parallel with the bridge's re-delivery.

**Why first turns time out:** MCP cold-start adds ~22 s per agent (Node bundle + uvx-spawned MCP servers + tool-discovery handshake). Combined with the actual research turn (multiple Firecrawl scrapes for the researcher's first Talk reply), first turns can legitimately exceed 180 s. Subsequent turns hit the cache and stay under 60 s.

**Token cost of F-O-8 in this run:** 3 duplicate first-turn invocations, est. $3-5 of the $16.37 total (~25 % avoidable spend).

**Fixes considered:**
1. **Raise `DELIVER_TIMEOUT_S`** to e.g. 600 s — patches the symptom but leaves the bridge thread blocked, which serializes message delivery per identity. Bad for multi-message bursts.
2. **Fire-and-forget**: `docker exec -d` (detached). Decouples bridge from agent turn time. Loss: bridge can't observe per-message failures; relies on agent's own error handling.
3. **Per-session lock on bridge side**: serialize re-deliveries by session-id, but parallelize across sessions. Closest to "right" architecture but more code.
4. **Async harness**: spawn a worker pool, deliver to the worker, return immediately. Same shape as letta-mcp-channel's queue-based delivery.

**Decision for Run 2':** option 2 (detached exec) as the spike-minimal path — losing per-message error visibility is acceptable because the agent itself logs to OTel and prints to stdout; the bridge doesn't need to observe completion to do its job. Will land as a follow-up commit before Run 2'.

**Severity:** medium — wastes tokens and creates session-write races on duplicate deliveries (would intersect F-O-3 takeover-error path under heavier load).

### F-O-2 — UNCHANGED

EM still writes to `/agents/` at container root, not `/workspace/em`. Mitigation in kickoff (live snapshot loop + `docker cp` on teardown) caught everything. Same prompt + sandbox gap as Run 1' — not multi-gateway-specific.

### F-O-3 — NOT OBSERVED THIS RUN

No `EmbeddedAttemptSessionTakeoverError` in either gateway log. Possible reasons:
- Shorter turns (no overflow → no auto-compaction)
- Per-gateway isolation: only one agent per session-jsonl tree, so heartbeat lane + main lane are the only writers
- Run was shorter wall-clock than Run 1' (no compaction triggered)

Will re-test under Run 2's longer 2 h cap.

### F-O-4 — Per-agent MCP scoping verified by isolation

Each gateway has only its own MCP servers:
- `openclaw-em` config loads `nextcloud-em` only (no researcher-web, no nextcloud-researcher).
- `openclaw-researcher` loads `nextcloud-researcher` + `researcher-web` only.

Hard process-level isolation, no `tools.byProvider.allow:[]` acrobatics needed. The original OQ-1 ("does `allow:[]` actually hide that MCP?") is moot under N-gateway — the MCP simply isn't loaded.

### F-O-5, F-O-6 — RESOLVED

F-O-5 (cost rollup path bug) verified fixed: `scrape-usage.py` correctly read both em + researcher session jsonl trees after merge.

F-O-6 (kickoff lacks engagement spec) verified fixed: brief is baked into kickoff script, EM acted on it directly without scope derivation.

## Driver / runtime behavior

- **Bridge deliveries:** 11 attempts (8 success, 3 timeout-but-actually-completed). 8 rooms anchored at head on first sight. Bridge thread serialization per-identity is the cause of the 180 s blocking behavior — see F-O-8.
- **OpenClaw heartbeat:** every 5 min per agent (config default). Both agents respected the `NO_REPLY` convention when no new useful action.
- **Auto-compaction:** not triggered (turns stayed under context budget).
- **Cache hit rates:** EM 91.9 %, Researcher 88.8 % — both high. The cache-retention=long config is paying off.
- **Talk-room creation by agents:** EM created `EM-Researcher` via MCP `talk_create_room`. Bridge picked the new room up within one room-list cycle (60 s) and anchored at head correctly.

## Cost

```
agent         model                   calls     input    output  cache_rd  cache_wr   hit%         $
em            claude-opus-4-7            31        86     42097   2872021    254374  91.9%   12.2361
researcher    claude-sonnet-4-6          47        61     36101   4648096    585271  88.8%    4.1309
TOTAL                                                                                        16.3670
```

vs Run 1' single-process: $19.54 ($18.17 EM + $1.37 Researcher). The multi-gateway run is **17 % cheaper**, mostly because Researcher actually did 47 calls of work (vs Run 1's 11 — most of which were heartbeat-driven `HEARTBEAT_OK` no-ops because nothing was delivering Talk to it). Researcher costs more in this run (real work) but EM costs less (no solo synthesis fallback).

Estimated F-O-8 waste: 3 duplicate first-turn invocations × ~$1-2 each = $3-5 of the $16.37 (~25 %). Fixing F-O-8 should put the run at ~$12 net.

## What this run validates for Run 2'

1. **Talk-mediated coordination works under OpenClaw** with the bridge architecture. The Roster v1 channel model (letta-mcp-channel for the Letta side) has a viable OpenClaw analogue.
2. **Per-agent identity = regular Nextcloud user** is feasible. Human takeover by logging in as `em` or `researcher` would Just Work — no bot account constraints.
3. **N-gateway scales architecturally**. Adding 2 more gateways (Senior A, Senior B) for Run 2' is a compose-file change, not a coordination redesign.
4. **MCP scoping is solved structurally** — no per-gateway tool gating, just don't load what the agent shouldn't have.
5. **Cost path is viable**: ~$16/run for a 15-min 2-agent engagement. Run 2's 2 h × 4-agent budget projects to ~$80-120 with F-O-8 fixed (rough — depends heavily on cache hit rates at longer wall time and on the heartbeat-driven background spend with 4 agents).

## What still has to land before Run 2'

| | |
|---|---|
| F-O-8 fix (detached exec) | Required — Run 2' will hit MCP cold-start across 4 agents = 4× duplicate-delivery risk if unfixed |
| F-O-2 fix (workspace anchor in prompt + filesystem sandbox config) | Required — Run 2's 4-agent output multiplies the writes-outside-workspace surface |
| Run 2' compose (`docker-compose.4agent-multigateway.yml`) | Required — add openclaw-senior-a, openclaw-senior-b; bridge identities.json grows from 2 → 4 |
| 4-agent prompts + room topology | Required — confirm SA pair joins `#team` + creates `Senior-A-Researcher`, `Senior-B-Researcher` DMs (mirror Week 1's Letta topology) |
| Cost budget alert (G'-8) | Recommended — at $80-120 projected, the spike-scope $5 wall-clock cap is insufficient guardrail |

## Cross-references

- Previous: [t5-run-1prime-conclusions.md](t5-run-1prime-conclusions.md) (Run 1' single-process, F-O-1 blocker discovered)
- Ledger: [t5-openclaw-run-ledger.md](t5-openclaw-run-ledger.md) (Run 1'-mg row + F-O-7, F-O-8 added to findings table)
- Architecture pivot rationale: per-identity Talk plugin vs N-gateway tradeoff captured in PR thread (Run 1' findings PR #46 comments)
- Letta-side analogue: [`vezzadev/letta-mcp-channel`](https://github.com/vezzadev/letta-mcp-channel) (external repo — Roster v1 channel architecture this mirrors)
- Bridge source: [`spike-compose-openclaw/nextcloud-talk-bridge/bridge.py`](spike-compose-openclaw/nextcloud-talk-bridge/bridge.py)
- Compose: [`spike-compose-openclaw/docker-compose.2agent-multigateway.yml`](spike-compose-openclaw/docker-compose.2agent-multigateway.yml)
- Kickoff: [`spike-compose-openclaw/run-1prime-mg-kickoff.sh`](spike-compose-openclaw/run-1prime-mg-kickoff.sh)
- Snapshot artifacts: `spike-compose-openclaw/run-1prime-mg-snapshot/2026-05-24T01-03-57Z/` (gitignored; not committed)
