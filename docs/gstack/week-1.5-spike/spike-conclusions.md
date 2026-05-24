# Week 1 / 1.5 spike — conclusions and gate decision

Parent: [README.md](README.md) · Wraps up: [../week-1-spike/README.md](../week-1-spike/README.md) + this folder.

Decision date: 2026-05-23.

This file ends the runtime-swap spike (Week 1 Letta → Week 1.5 OpenClaw). Run 2' (4-agent SC#5 artifact run) is **deferred** — the evidence already in hand is sufficient to make the architecture call, and the missing input (cost optimization) is a Week 2 prerequisite, not a spike deliverable.

---

## 1. Verdict in one paragraph

**Nextcloud Talk is a viable medium for agent intercommunication** — proven independently on both runtimes (Letta Run 1 and OpenClaw Run 1'-mg both produced cited market-entry briefs through Talk-mediated EM↔Researcher coordination, no human intervention beyond a kickoff post). **OpenClaw beats Letta on every spike-scope criterion that isn't cost**: cleaner runtime, larger ecosystem, no auto-compaction race, sandboxable per-gateway containers, file-state vs Letta's Postgres-orphan tool calls. **But OpenClaw's cost trajectory is prohibitive at current shape** — ~$65/hr for a 2-agent run with 90%+ cache hit. Scaling to the 4-agent SC#5 shape would put a single brief in the $130-260 range and a continuous desk in the $1k+/day range, neither of which fits the desk-as-service economics in [`../design/06-validation.md`](../design/06-validation.md) SC#6. **Cost optimization is the gating Week 2 prerequisite; running Run 2' before it lands would burn money producing an artifact whose runtime is already known not to be Letta.**

---

## 2. Evidence anchoring each leg of the verdict

### Leg 1 — Nextcloud Talk viable for agent comms

| Source | What it proves |
|---|---|
| [../week-1-spike/run1-artifacts/brief.md](../week-1-spike/run1-artifacts/brief.md) | Letta + Talk produced a 222-line brief through 50 min of autonomous EM↔Researcher coordination via [`vezzadev/letta-mcp-channel`](https://github.com/vezzadev/letta-mcp-channel) (push-based MCP plugin). |
| [spike-compose-openclaw/run-1prime-mg-snapshot/2026-05-24T01-03-57Z/em-writes/brief.md](spike-compose-openclaw/run-1prime-mg-snapshot/2026-05-24T01-03-57Z/em-writes/brief.md) | OpenClaw + Talk produced a 163-line brief through 15 min of autonomous coordination via the [`nextcloud-talk-bridge`](spike-compose-openclaw/nextcloud-talk-bridge/) sidecar (per-identity OCS long-poll + `docker exec`). |
| [t1-checks-report.md](t1-checks-report.md) | Both briefs cleared the contamination guard (URL audit + 7-gram check, 0 hits). Quality differential is depth-of-analysis under cap, not architecture. |

Talk's room model (1 group room per team + 1 DM per pair) maps cleanly to the engagement-manager / researcher topology. Both push-based (letta-mcp-channel) and pull-based (talk-bridge OCS long-poll) shapes work; the bridge sidecar is the path forward because it doesn't require an upstream Letta plugin to ride on the channel API.

### Leg 2 — OpenClaw > Letta on everything but cost

Comparison limited to spike-scope criteria; not a general runtime endorsement.

| Criterion | Letta | OpenClaw | Margin |
|---|---|---|---|
| Codebase maturity | Auto-compaction lock-release race ([F-7](../week-1-spike/t5-run-1-conclusions.md) → discards compaction work); `memory_insert(label="human")` schema drift; Postgres-orphaned uncancellable tool calls under SPOF. | Single-process per agent, file-backed session jsonl, deterministic cold-boot in ~5 s. F-O-2 (fs-tool unsandboxed) is a config gap, not a code race. | OpenClaw |
| Ecosystem | Letta-internal MCP channel; bespoke driver needed for Nextcloud delivery ([`vezzadev/letta-mcp-channel`](https://github.com/vezzadev/letta-mcp-channel)). | Standard MCP client (streamable-http + stdio via uvx); bridge sidecar is ~250 LOC, no upstream patch. | OpenClaw |
| Per-agent isolation | Single Letta server, all agents share Postgres + tool table → MCP scoping (`tools.byProvider.allow:[]`) needed and unreliable. | N-gateway topology: each agent is its own container with its own MCP servers → isolation is structural, no scoping needed (F-O-4 resolved structurally in [run ledger](t5-openclaw-run-ledger.md)). | OpenClaw |
| Coordination loop validity | Validated under load in Run 1 (50 min, push-based via letta-mcp-channel). | Validated under load in Run 1'-mg (16 min, pull-based via talk-bridge sidecar). | Parity |
| Recovery & checkpointing | Postgres-backed session state; tool-call orphans under crash. | File-backed `/state/bridge-state.json` + per-session jsonl; verified resume-from-disk in Run 1'-mg. | OpenClaw |
| Brief quality (under different caps) | Run 1 (50 min, 2-agent) → 4.06 avg, strong-positive. | Run 1'-mg (15 min, 2-agent) → 3.25 avg, sub-3 on D2 + D6. | Letta — but cap-bound, not architecture |
| Open critical issues blocking Week 2 | F-7 (compaction race) is upstream and unresolved; F-1 (Talk-channel transport bugs) ditto. | F-O-2 (fs-tool sandbox) + F-O-8 (bridge timeout false alarm, 25 % token waste) — both spike-fixable. | OpenClaw |

Letta's open issues are upstream-code races requiring patches across a less-active codebase; OpenClaw's are configuration tightenings the spike's own code owns. That's the asymmetry that flips the runtime call.

### Leg 3 — Cost is the gating constraint

| Run | Agents | Wall | Cost | Per-hour-2-agent rate | Cache hit |
|---|---|---|---|---|---|
| Letta Run 1 | 2 | ~50 min | **$57.87** (unoptimized, 0 % cache hit per Anthropic billing) | ~$70/hr | 0 % (no cache wins under Letta's prompt-rotation pattern) |
| OpenClaw Run 1' (single proc) | 2 | 15 min 45 s | **$19.54** | **~$74/hr** | EM 92.5 %, Researcher 73.1 % |
| OpenClaw Run 1'-mg (multi-gateway) | 2 | 16 min 06 s | **$16.37** | **~$61/hr** | EM 91.9 %, Researcher 88.8 % |

**Projection for the Run 2' SC#5 shape (4 agents × 2 h):** at the Run 1'-mg per-agent-hour rate ($61 / 2 = ~$30 / agent-hour at 90 %+ cache), a 4-agent / 2 h brief lands in the **$240 ballpark**, before counting Senior A + Senior B's longer-than-EM context and any F-O-8 waste. That's one brief at a cost an analyst would reject.

**Continuous-desk projection** ([`../design/06-validation.md`](../design/06-validation.md) SC#6's "research desk" framing): an 8 h day of 4-agent activity at this rate is ~$1k/day per desk, ~$20k/mo. AlphaSense-style enterprise pricing is $15-40k/year/seat — the desk-as-service unit economics break by an order of magnitude.

**The cost lever the spike already identified is "request-count reduction" — cut Researcher's 162 LLM calls per brief by batching tool-results in a single turn**, not "more caching" (Letta Run 1 conclusions §C-6 showed caching alone gets 24 %, not 67 %). That's a Week 2 prerequisite, not a spike artifact.

---

## 3. Gate decision

Per the rubric's gate matrix in [`../week-1-spike/t1-grading-rubric.md`](../week-1-spike/t1-grading-rubric.md#gate-decision):

- **Quality gate (SC#5)**: ✅ cleared. Letta Run 1 hit strong-positive (self 4.06 / panel 4.625, 4.75; URL audit clean; 7-gram clean — see [`t1-checks-report.md`](t1-checks-report.md)). The architecture call doesn't require a separate OpenClaw artifact above the same bar because (a) Run 1'-mg's negative-gate result is cap-bound, not architecture-bound, and (b) the runtime question and the quality question are separable — Run 1 settled the quality question on Letta-the-runtime, Run 1'-mg settled the coordination-medium question on OpenClaw, and there is no remaining quality-vs-architecture confound that Run 2' would resolve.
- **Cost gate (SC#6)**: ❌ fails on current shape. Cost optimization is the named Week 2 prerequisite.
- **Runtime call**: OpenClaw. Letta is retired from the active runtime list — see §5 for the disposition of Letta-specific work products.

---

## 4. What's deferred (NOT going to happen in this spike)

| Item | Status | Why deferred | Where it picks up |
|---|---|---|---|
| Run 2' — 4-agent / 2 h SC#5 artifact run | **deferred** | Cost-prohibitive at current per-agent-hour; runtime call already settled by Run 1 + Run 1'-mg. Running it now would burn ~$240 producing an artifact whose runtime verdict is already known. | After Week 2 cost-optimization milestone (request-count reduction + cache-write amortization); rerun under SC#5 protocol with all four checks per [`t1-checks-report.md`](t1-checks-report.md). |
| T6' — Forced SPOF test (`kill -9` mid-flight) | **deferred** | Was scheduled under Run 2'; folds into the post-cost-opt re-run. The OpenClaw recovery model (file-backed state + bridge state.json) is already verified at the cold-boot level; the SPOF test adds mid-flight realism. | Same as Run 2'. |
| Paid-analyst hire (Week 2 first 3 days) | **conditional-deferred** | Per gate matrix, Letta Run 1's strong-positive unlocks the paid-analyst step. But hiring the analyst before cost optimization means paying for a desk that can't economically sustain its own output cadence — a bad signal to send. | After cost optimization, OR in parallel if cost-opt gets a credible ETA. |
| OAuth path for OpenClaw → Anthropic auth | deferred (G'-6) | API-key path is sufficient for spike scope. | Future runtime-config spike. |
| Detached-exec / per-session-lock fix for F-O-8 | **gating for Run 2'** | 25 % token waste from bridge timeout + duplicate-delivery. Must land before any longer-cap run. | Week 2 prereq alongside cost optimization. |

---

## 5. Disposition of work products

| Path | Disposition |
|---|---|
| [`../week-1-spike/`](../week-1-spike/) — Letta spike | **Frozen-in-place.** Findings F-1 through F-8 remain valid as documentation of why Letta is not the runtime; not deleted. |
| [`spike-compose-openclaw/`](spike-compose-openclaw/) — OpenClaw scaffold | **Carries forward** into Week 2. F-O-2, F-O-3, F-O-8 are open and tracked in [`t5-openclaw-run-ledger.md`](t5-openclaw-run-ledger.md). |
| [`spike-compose-openclaw/nextcloud-talk-bridge/`](spike-compose-openclaw/nextcloud-talk-bridge/) | **Carries forward.** ~250 LOC sidecar; Week 2 may consider upstreaming as an OpenClaw plugin once F-O-8 is fixed. |
| [`t8-openclaw-brief.md`](t8-openclaw-brief.md) "T8' — gate-decision brief" | Status updated to **superseded by this file** (Run 2' deferred; gate decision made on cumulative evidence). |
| [`t1-checks-report.md`](t1-checks-report.md) | **Carries forward.** Will be re-run against the post-cost-opt brief under the same protocol. |

---

## 6. Week 2 prerequisites (out-of-scope for this spike, named for handoff)

1. **Cost optimization — request-count reduction.** Researcher's 162 LLM calls / 50 min on Run 1 is the biggest lever per [Run 1 §C-6](../week-1-spike/t5-run-1-conclusions.md). Target: batch tool-results so one LLM call covers ≥3 tool invocations under stable context. Bench: $30/hour per agent at 4-agent shape gets the desk to ~$240/day, ~$5k/mo — within the desk-as-service envelope.
2. **F-O-8 fix.** Detached `docker exec` OR per-session bridge lock so the 180 s timeout false alarm doesn't trigger duplicate delivery. ~30 LOC.
3. **F-O-2 fix.** Tighten the per-gateway workspace mount and fs-tool config so writes can't escape `/workspace/<agent>/`. Config-only.
4. **Blocklist tightening.** Add `deloitte.com/*/services/tax/perspectives/*` (closes the only residual Letta-Run-1 URL-audit gap — see [`t1-checks-report.md §2`](t1-checks-report.md#2-researcher-url-audit)).
5. **Re-run Run 2' under SC#5 protocol** with all four checks per [`t1-checks-report.md`](t1-checks-report.md).

---

## 7. What this spike did NOT establish

- **Layer-3 contamination (latent training-data leakage)** — undetectable in-spike per rubric §"What this does NOT eliminate". Only practicing-analyst review can address.
- **Architecture under SPOF** — T6' deferred; mid-flight `kill -9` not yet exercised on OpenClaw.
- **4-agent coordination under cap** — Run 2' deferred. Run 1'-mg validated 2-agent EM↔Researcher; the EM ↔ Senior-A ↔ Senior-B ↔ Researcher fan-out is unproven on OpenClaw.
- **Cost optimization itself** — explicitly out of scope; named as Week 2 prereq above.

---

## Cross-references

- Week 1 spike root: [../week-1-spike/README.md](../week-1-spike/README.md)
- Week 1.5 spike root: [README.md](README.md)
- Validation criteria (SC#5, SC#6): [../design/06-validation.md](../design/06-validation.md)
- Run ledger (numbered runs + findings): [t5-openclaw-run-ledger.md](t5-openclaw-run-ledger.md)
- Quality checks (rubric + URL + panel + 7-gram): [t1-checks-report.md](t1-checks-report.md)
