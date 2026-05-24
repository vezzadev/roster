# T5' — OpenClaw run ledger

Parent: [README.md](README.md) §T5'

Mirrors [../week-1-spike/t5-run-ledger.md](../week-1-spike/t5-run-ledger.md):
numbered runs, **prompt freeze per run**, hash-pinned config, hard caps,
artifact links. Row format identical to Week 1 so the AI panel can compare
runs across runtimes apples-to-apples.

Status: 🛠 Run 1' scaffolded; T9' partial-pass per [boot-smoke-findings.md](boot-smoke-findings.md) (transcript-replay cost-scrape used as fallback); T4' deferred to mid-run observation.

## Pre-flight readiness (G-list, mirrored from Week 1's G-1…G-8)

| Gate | Check | Status |
|---|---|---|
| G'-1 | OpenClaw pinned ≥ 2026.1.29 (CVE-2026-25253 patched) | ⚠️ pinned to latest (`2026.5.20`); CVE backport not separately verified — accepted spike-scope risk |
| G'-2 | OTel parity validated per T9' acceptance test | 🚧 partial — span semconv + duration metric pass; token-usage histogram silent → fall back to [`scrape-usage.py`](spike-compose-openclaw/scrape-usage.py) reading session transcripts |
| G'-3 | MCP fidelity check passed per T4' | ⏳ folded into Run 1' as live observation — researcher-web-mcp (streamable-http) + cbcoutinho/nextcloud-mcp-server (stdio via uvx) both exercised |
| G'-4 | Frozen prompts hashed + committed (same hashes as Week 1 modulo channel-tool name swaps) | ✅ EM = `e966a655…`, Researcher = `2fff77b9…` — verbatim port to `agents/em/AGENTS.md` + `agents/researcher/AGENTS.md`, sha256 match Week 1 |
| G'-5 | Per-agent workspace seeded — AGENTS.md, SOUL.md, MEMORY.md, HEARTBEAT.md, TOOLS.md per agent | ✅ AGENTS/SOUL/USER/IDENTITY/BOOTSTRAP seeded per agent (TOOLS.md/HEARTBEAT.md deferred — embedded in AGENTS to preserve hash) |
| G'-6 | Anthropic auth wired (decide API-key vs OAuth — open question #5 in [README.md](README.md)) | ✅ API-key path chosen (smoke-validated boot-smoke run) — OAuth deferred to a later spike |
| G'-7 | Nextcloud Talk rooms created (one #team + per-pair DMs, same topology Week 1 used) | ✅ reusing Week 1 rooms (`#team qcfcaosp`, `EM-Researcher fdj2y9qi`) — Nextcloud + accounts still up in `spike-compose_spike` network |
| G'-8 | Cost budget alert set at the Anthropic console level (not just OpenClaw config — F-O5 mitigation) | ⚠️ accepted-risk for 15-min Run 1' — budget exposure < $5 worst case (hard wall-clock cap) |

Run 1' kicks off with G'-2/3 deferred; Run 2' requires G'-2 fully closed.

## Run matrix

| Run | Goal | Agents | Models | Hard cap | Status |
|---|---|---|---|---|---|
| 1' — 2-agent smoke (single process) | Validate end-to-end happy path under OpenClaw before scaling up | EM + Researcher | Opus 4.7 + Sonnet 4.6 | **15 min** | ⚠️ partial — brief produced ($19.54), coordination loop NOT validated (F-O-1 Talk→OpenClaw delivery gap). See [conclusions](t5-run-1prime-conclusions.md). |
| 1'-mg — 2-agent re-run, N-gateway architecture | Validate the bridge-based fix for F-O-1 before scaling to 4 agents | EM + Researcher | Opus 4.7 + Sonnet 4.6 | **15 min** | ✅ success — 163-line brief with 20 cited sources at **$16.37** (17 % cheaper than Run 1'); F-O-1 verified fixed; F-O-7 + F-O-8 opened. See [conclusions](t5-run-1prime-mg-conclusions.md). |
| 2' — 4-agent main | SC#5 artifact run; produces the brief that goes to the AI panel | EM + Senior A + Senior B + Researcher | Opus 4.7 + Sonnet 4.6 × 3 | 2h | **deferred** (see [spike-conclusions.md](spike-conclusions.md)) — cost-prohibitive on current per-agent-hour rate (~$240 projected); runtime verdict already settled by Run 1 + Run 1'-mg. Re-runs after Week 2 cost optimization + F-O-8 fix. |

Run 1' kickoff command: `./spike-compose-openclaw/run-1prime-kickoff.sh`. Hard-cap enforced via `HARD_CAP_SECONDS=900` then graceful `compose down`. Snapshot lands under `spike-compose-openclaw/run-1prime-snapshot/<ISO-timestamp>/`.

Re-run policy: if Run 2' halts on a *fixable* runtime/infra bug (per the
run-failure recovery policy stored in operator memory — autonomously fix +
restart for straightforward fixes, halt + surface for upstream/non-trivial
ones), apply that policy. If it halts on an upstream OpenClaw bug, file a
finding row in this ledger, halt, and surface.

## Row template (filled in post-run)

```
### Run X' — <name>

| | |
|---|---|
| Started | <UTC timestamp> |
| Stopped | <UTC timestamp> |
| Wall    | <duration> |
| Config  | <env vars + hashes> |
| Agents  | <model + tools per agent> |
| Talk    | <room IDs, fresh vs reused> |
| Output  | <artifact paths> |
| Cost    | <total $ + cache hit rate + per-agent breakdown via kql/03-per-agent-cost.kql> |
| Outcome | success / partial / halt + one-line reason |

**Course of run.** <prose narrative of what happened, mirroring Week 1's style>

**Findings (F-O…).** Numbered, each linking the upstream bug or design issue.

**Driver/runtime behavior.** Heartbeat firing pattern, immediate-wake count if supported, orphan-call count.
```

## Findings log (F-O…)

Numbered in discovery order, mirroring Week 1's F-1…F-8 numbering for the
Letta side. F-O prefix to keep them visually distinct.

| # | Title | Severity | Discovered | Status |
|---|---|---|---|---|
| F-O-1 | Talk → OpenClaw delivery gap — no inbound channel without a per-identity Talk plugin | **blocker** for autonomous coordination | Run 1' | **resolved** in Run 1'-mg — `nextcloud-talk-bridge` sidecar closes the loop (per-identity OCS long-poll + `docker exec` into the right gateway) |
| F-O-2 | Filesystem writes escape the workspace mount; OpenClaw fs-tool unsandboxed | high | Run 1' | open — multi-gateway unchanged the surface; needs prompt fix + runtime config fix |
| F-O-3 | Auto-compaction lock-release race → `EmbeddedAttemptSessionTakeoverError`, compaction work discarded | upstream | Run 1' | open — not observed in Run 1'-mg (shorter turns, no overflow); re-test under Run 2's 2 h cap |
| F-O-4 | Per-agent MCP scoping (`tools.byProvider.allow: []`) may be ineffective | medium | boot-smoke + Run 1' | **resolved structurally** under N-gateway — each gateway loads only its own MCP servers; no `allow:[]` needed |
| F-O-5 | Cost rollup path bug in `run-1prime-kickoff.sh` (`openclaw-agents/..` vs `agents/`) | low | Run 1' | fixed; verified in Run 1'-mg |
| F-O-6 | Kickoff message lacks engagement spec; EM has to derive scope from AGENTS.md → cross-run inconsistency | medium | Run 1' | fixed; verified in Run 1'-mg (brief baked into kickoff script) |
| F-O-7 | Nextcloud auto-provisions a `Talk updates ✅` room with ~20 release-notes messages per new user; naive bridge with `lastKnownMessageId=0` replays them | low | Run 1'-mg | fixed in `bridge.py` (anchor at `lastMessage.id` on first sight of a room) |
| F-O-8 | Bridge 180 s synchronous timeout is a false alarm during MCP-cold-start turns; `docker exec` kill doesn't signal the in-container process → orphan + duplicate-delivery on retry → ~25 % token waste | medium | Run 1'-mg | open — Run 2' must land detached-exec fix or per-session bridge locking |

Details: [t5-run-1prime-conclusions.md](t5-run-1prime-conclusions.md) (Run 1' single-process), [t5-run-1prime-mg-conclusions.md](t5-run-1prime-mg-conclusions.md) (Run 1'-mg multi-gateway), [t5-run-1prime-open-questions.md](t5-run-1prime-open-questions.md).

## Forced SPOF (T6')

During Run 2', `kill -9` one OpenClaw Gateway mid-flight. Observe and record
here:

- File-backed state survives restart? (expected yes)
- Heartbeat resumes cleanly? (timing in seconds from process up to first wake)
- Outstanding MCP tool calls — orphaned, retried, or cancelled? (this is the
  big question — Letta's were postgres-orphaned and uncancellable per Week 1)
- Talk-room re-sync — does the agent re-read messages received during downtime?

Land verdict here as a sub-section once executed.

## Cross-references

- Week 1 ledger conventions: [../week-1-spike/t5-run-ledger.md](../week-1-spike/t5-run-ledger.md)
- Frozen prompts source: [../week-1-spike/t5-system-prompts.md](../week-1-spike/t5-system-prompts.md)
- Per-run conclusion file template: [../week-1-spike/t5-run-1-conclusions.md](../week-1-spike/t5-run-1-conclusions.md)
