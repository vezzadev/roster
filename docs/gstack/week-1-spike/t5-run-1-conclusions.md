# Run 1 Conclusions — 2-agent ablation (EM + Researcher)

Reads what the Run 1 transcript means for the spike's success criteria, the v1 design, and the Run 2 plan. Sourced from [t5-run-ledger.md](t5-run-ledger.md) (event log + Letta tool-namespace finding), [run1-artifacts/](run1-artifacts/) (brief + bundles + URL audit), and [t5-env-manifest.md](t5-env-manifest.md) (architecture snapshot).

Parent: [../design.md](../design.md) · Spec: [../design/06-validation.md](../design/06-validation.md) SC#5 / SC#6 · [../design/05-implementation.md](../design/05-implementation.md) Cost Model

## Topline

Run 1 was a diagnostic 2-agent ablation, not the gating SC#5 artifact (which is reserved for the 4-agent Run 2 in [t8-sample-brief.md](t8-sample-brief.md) per [../design/06-validation.md](../design/06-validation.md)). It nevertheless produced a structured Indonesia market-entry brief — `run1-artifacts/brief.md`, 208 lines, 34,465 bytes, all 6 Researcher bundles integrated, [^A*]–[^F*] footnote map intact — in ~50 minutes of wall-clock with no human intervention beyond a kickoff message, a clarifying team-composition correction, and a pacing nudge near the 1h cap.

**Bottom line: every piece of the architecture the spike was meant to test held under live load. The work surfaces three corrections to the v1 design (one structural, two operational) and one cost-trendline call.**

## What this run validated (with evidence)

### V-1. Identity isolation under the agent-driven path

The original singleton-Letta setup posted EM's first kickoff brief to `#team` as actor `researcher` — a tool-namespace collision (see [t5-run-ledger.md](t5-run-ledger.md) "Letta tool-namespace finding"). After splitting into per-agent Letta containers, the agent-driven probe and the entire Run 1 transcript both passed: every `talk_send_message` the agents produced posted under the intended actor (`actorId` echoed back in the Nextcloud OCS tool returns; cross-checked at the room-history layer).

> *Evidence:* event-log rows for 00:32:22 UTC (kickoff posted as `em`), 00:34:55 UTC (team-comp update as `em`), 00:39 UTC onward (every Researcher bundle posted as `researcher` in the DM), 01:21:10 UTC (`brief final` as `em`). Zero misattribution after the per-agent cutover.

### V-2. Contamination guard works server-side, never had to fire under load

Researcher made 112 web fetches via the `researcher-web-mcp` wrapper. Every `web_search` call carried the 11-host consulting-firm `excludeDomains` list (see `researcher-web-mcp/audit/fetch.jsonl`); every `web_scrape` URL passed the wrapper's pre-egress block check. **Zero blocks fired during the run.** The only `host:bcg.com` block in the audit log is the pre-kickoff verification probe at 00:21:29 UTC.

Two interpretations:

1. The blocklist is correctly scoped — Researcher's source instinct kept it on Indonesian primary sources (BPS, Bank Indonesia, OJK, ALFI, Deloitte Indonesia, Komdigi, World Bank IEP, ITA Country Commercial Guide) and never reached for a McKinsey/BCG search reflex.
2. The 2-agent ablation may understate contamination risk because Researcher had no analyst peers prompting it toward synthesis-style queries. Run 2 retest needed before declaring the guard "low utilization."

### V-3. Originality guard observed working in flight (twice)

The system-prompt anti-recall clause was visible in the transcript, not theoretical:

- **First correction (~01:00 UTC):** EM's initial reading of the competitive landscape included a "Jan 2024 three-way Shipper/Waresix/Trukita merger" — a fact apparently lifted from training. Researcher's Bundle B corrected this against primary sources (the actual deal was a Waresix–Trukita acquisition in Dec 2020, per the e27 citation). EM accepted the correction in its working notes and the brief footnote `[^B-Waresix]` carries the corrected event.
- **Second correction (~01:20 UTC, during finalize):** EM's first-draft brief stated "IDR ~16,100, 8-10% depreciation 2022-2025." Bundle E's supplement (msg 275) and Bundle A (msg 276) put the actual figure at IDR 17,648 (May 2026), ~22-24% cumulative depreciation. EM updated §5/§7 and added a "kill if IDR breaks 18,500" line in §3 reflecting the wider drift than its memory suggested.

Both corrections come from primary sources Researcher actually fetched, not from prompt-injected scolding. That is the loop the design was hoping to see. The footnote map in Appendix A makes each correction traceable.

### V-4. Per-agent Letta architecture (now load-tested)

The structural fix from the namespace finding survived a full run: two `letta-*` containers with non-overlapping MCP registrations, no tool-id collisions across the boundary. Bind-mounted `url_validation.py` SSRF-guard patch still functions; both Letta containers boot clean against the persistent SQLite volume; agent state persists across the OpenRouter outage + driver restart (state file advanced; both agents resumed mid-conversation without re-orientation).

### V-5. The polling driver pattern is sufficient for spike-scale collaboration

`spike-compose/driver.py` (the synchronous stand-in for [`vezzadev/letta-mcp-channel`](https://github.com/vezzadev/letta-mcp-channel)) ran ~12 ticks across the active hour. Average wake-to-response latency on Researcher (web-fetch turns) was around 60–120s; on EM (synthesis turns) 30–60s. Two TimeoutError client-side timeouts at 300s — neither lost work (Letta finished server-side, state advanced, next tick relayed the resulting messages). State-file-on-disk + last-id-per-(room, agent) was enough to survive a manual restart with zero re-orientation cost.

## What this run revealed (corrections to the v1 design)

### C-1. **Per-agent Letta is a structural v1 decision, not a spike workaround.**

The namespace collision is not a Letta misconfiguration — it is a property of Letta's current tool-id allocation model (one global tool-id per `name`, last-write-wins across MCP servers within a single Letta instance). For Roster v1 with 4 agents on the same host, this means one of:

- **(a) One Letta container per agent identity** (what Run 1 used). Operationally heavier — each container is ~150–300 MB resident + its own SQLite. Boot time multiplies. With 4 agents per team this is fine; with N agents on a shared host this scales unpleasantly.
- **(b) Single Letta with name-mangled MCP tools** (e.g., a per-agent prefix on `talk_send_message` → `em_talk_send_message`). Requires patching the MCP sidecars to expose distinct tool names per agent, or a Letta-side rename layer. Adds wiring complexity, blurs the MCP server identity surface.
- **(c) Upstream fix in Letta — per-MCP-server tool-id namespacing.** Right architectural answer but blocked on an external project's release cadence.

**Recommendation:** v1 ships (a). It works today, it is the bounded blast radius for a small team, and the trade-off is RAM/disk, not correctness. Document the limit in v1 docs; revisit (c) if/when the upstream lands.

### C-2. **Letta default memory blocks no longer ship; agent creation must populate them.**

Empirical: `memory_insert(label="human")` errored with `Block field human does not exist (available sections = ())` on the EM agent. The agent fell back to file-backed notes in `/agents/_em-notes.md`. This worked for one synthesis agent over 50 min but will be friction-y across four agents over longer runs. Already captured as a Run 2 follow-up in [t5-run-ledger.md](t5-run-ledger.md) "Follow-ups before Run 2" → fix in `wire-run-1.py` to seed `human` + `persona` blocks (or whatever Letta 0.16.8's current canonical schema is) on agent create.

**Update (Run 1-redo, 2026-05-22 15:45 UTC).** `wire-run-1.py` now seeds per-role `human` + `persona` memory blocks on agent create. Verified post-wire via `GET /v1/agents/<id>/core-memory/blocks`: both agents had both blocks attached. **But neither agent called `memory_insert` or `memory_replace` during the 15-min re-run** — character counts on both blocks matched the seed values exactly after the run ended. Two interpretations: (a) the re-run was dominated by the Talk-history reconstruction shortcut (see C-5) so the agents never had a steady-state period where memory writes would be useful, or (b) the system prompts don't sufficiently push the agents toward memory_insert as a tool of first resort for non-deliverable state. Re-validate with a genuinely-fresh Run 2 (no Talk-room history bleed) before drawing a firm conclusion.

### C-3. **Prompt caching is not happening anywhere — Letta's OpenAI-compatible path doesn't inject `cache_control` markers, and both models paid full uncached list price.**

**Direct evidence (OpenRouter per-request data, queried via the logs page with workspace_id filter):**

For every sampled generation in Run 1 — both Opus 4.7 and Sonnet 4.6, regardless of which backend OpenRouter routed to (Anthropic-direct vs Google Vertex appeared for Sonnet) — the raw generation JSON shows:

```
"native_tokens_cached": 0,
"usage_cache": null,
```

**Cost reconciliation against OpenRouter's posted prices** (queried live from `https://openrouter.ai/api/frontend/models`):

| Model handle (OpenRouter) | Input ($/M) | Output ($/M) | Cache read ($/M) | Cache write ($/M) |
|---|---:|---:|---:|---:|
| `anthropic/claude-opus-4.7`   |  5.00 |  25.00 | 0.50 | 6.25 |
| `anthropic/claude-sonnet-4.6` |  3.00 |  15.00 | 0.30 | 3.75 |

Plugging Run 1's tokens into these prices at zero cache (no discount):

| Model | Prompt × $/M | Completion × $/M | Expected | Actual | Δ |
|-------|--------------|------------------|---------:|-------:|--:|
| Opus 4.7 (EM)           | 3,412,552 × $5  = $17.06 | 64,024 × $25  = $1.60 | **$18.66** | **$18.66** | $0.00 |
| Sonnet 4.6 (Researcher) | 12,642,979 × $3 = $37.93 | 85,778 × $15  = $1.29 | **$39.22** | **$39.21** | $0.01 |

Match to the cent. **Both models are paying full uncached list price.** The earlier draft of this section interpreted Opus's spend as a "~67% discount vs list" — that was a pricing-assumption error (Opus 4.7 is $5/$25, not the $15/$75 of earlier Opus generations). With correct prices the picture is uniform: 0% cache hit across the board.

**Letta-side root cause (verified by inspecting `letta/letta:latest` image, digest `aa66c3eeee13`):**

- `cache_control` injection logic exists at `/app/letta/llm_api/anthropic_client.py:660-725` and helpers `_add_cache_control_to_system_message`, `_add_cache_control_to_messages` (lines 1334–1383). These mark tools, system prompts, and the trailing 2 message blocks with `{"type": "ephemeral"}`.
- That logic lives **only** in the native Anthropic-client path. Grep across the whole image for `cache_control` returns hits exclusively in `anthropic_client.py`.
- Letta's OpenRouter provider (`schemas/providers/openrouter.py`, `schemas/model.py:492` `OpenRouterModelSettings(... # OpenAI-compatible)`) routes requests through `llm_api/openai_client.py`, which has **no** `cache_control` references and never adds the markers.
- Net result: every Run 1 outbound request was an OpenAI-compatible chat completion with no cache hint, so Anthropic and Vertex both treated each turn as a fresh prompt.

**Expected savings if `cache_control` were correctly emitted on the OpenAI-compatible path:**

Working-context for a Researcher turn is ~78K prompt tokens (12.6M / 162 requests). Anthropic's cache is keyed on the request's prefix, so the bulk of that 78K is the stable system prompt + memory blocks + accumulating message history — the part that shouldn't change turn-over-turn within the 5-minute cache TTL. At an assumed 70% cache-hit rate on input tokens (standard for tool-call-heavy agent loops with no memory churn between turns):

- Sonnet: 70% of 12.6M × $0.30/M cache_read + 30% × $3/M input + 30% × $3.75/M cache_write + $1.29 output ≈ **$2.65 + $11.38 + $14.22 + $1.29 = $29.54** (vs $39.21 actual; saves ~$10)
- Opus:   70% of 3.4M × $0.50/M + 30% × $5/M + 30% × $6.25/M + $1.60 ≈ **$1.19 + $5.12 + $6.40 + $1.60 = $14.31** (vs $18.66 actual; saves ~$4)

Combined savings on Run 1's profile: ~$14 of $57.87 (~24%). Note: this is more modest than the "67%" the earlier draft claimed, because the cache-write penalty on the first turn at each new prefix eats much of the cache-read win. The real lever for SC#6 is **request-count reduction** (cutting Researcher's 162 → fewer LLM calls by batching tool-results in a single turn), not caching alone. Caching is still worth doing — it's a free 20-25% — but it is not the difference between SC#6 funding 2 runs/mo vs 5.

**Run 1's $57.87 is the unoptimized floor, not a savings opportunity gone wrong.**

**Investigation plan (closed for Run 1, carried into Run 2):**

1. ✅ Verified zero cache hits via OpenRouter raw JSON (`native_tokens_cached: 0`).
2. ✅ Verified Letta's cache_control logic lives only in `anthropic_client.py`, not in `openai_client.py` / OpenRouter path.
3. **Open for Run 2:** Choose one of:
   - **(a) Patch `openai_client.py`** to inject Anthropic-style `cache_control` markers when the model handle matches `anthropic/*`. Extends the existing `letta-patches/` bind-mount channel. Smallest surface change; cleanest A/B test.
   - **(b) Switch Letta to its native Anthropic provider** (env: `ANTHROPIC_API_KEY`, no OpenRouter middleman). Loses OpenRouter's failover + the per-workspace cost visibility, but immediately picks up the existing `cache_control` code path. Probably wrong for v1 because we lose Broadcast → observability.
   - **(c) File upstream Letta issue** and wait. Slowest path.
4. **For Run 2 observability:** Configure OpenRouter Broadcast → OpenTelemetry Collector → Azure App Insights (user-stated next step). Trace data includes `cached_tokens` natively, so the verification loop on whatever fix we ship becomes a KQL query, not a per-row click-through.

### C-4. **Synthesis pacing needs an external trigger, not just a hard wall-clock cap.**

Without the founder's pacing nudge at 01:08 UTC ("stop intake after Bundle A, start drafting"), the EM was happy to keep batching Researcher bundles. Some of that is good (the brief got more sources), some is unbounded (the 1h cap would have been hit with no brief drafted). For v1 the right shape is probably:

- Soft signal at 60% of budget ("you have 40% remaining; consider closing intake").
- Hard signal at 85% ("draft now; integrate any in-flight bundles after the first pass; no new requests").
- Wall-clock cap forces a graceful brief-as-of-now save, not a kill.

Pure "1h cap" was sufficient for Run 1 because the founder was operating the runtime live. For unattended v1 use, the EM prompt itself needs internal budget awareness, or Roster CLI needs to wake EM with these signals.

### C-5. **Talk chat history is the deeper recovery surface — `/agents/` + Letta pgdata wipe is not a "clean re-run."**

Found during the Run 1-redo on 2026-05-22 15:45 UTC after the pgdata-mount fix had landed (see [t5-run-ledger.md](t5-run-ledger.md) "Run 1 state loss" post-mortem). Goal of the re-run: a 15-min smoke against the post-fix compose to confirm state now persists across `docker compose down`, with memory blocks enabled. To get a "fresh" start, the re-run wiped:

- `letta_em_pgdata` + `letta_researcher_pgdata` volumes (Letta-side agents + messages + memory blocks gone).
- `/agents/*` in `nc_data` (brief.md, outline, all bundles, audit log, EM notes deleted).
- Driver state file truncated.

**What was *not* wiped: the Nextcloud Talk room message history.** The `EM-Researcher` DM (token `z4n3425w`) still carried 22 messages from Run 1 — the original Researcher bundles posted as chat. The `#team` room (token `vzyiva4u`) carried Run 1's kickoff + team-comp + brief-final.

**What the agents did.** Within ~10 minutes the EM:

1. Called `talk_get_messages` on both rooms; read the preserved Run 1 history.
2. Reconstructed engagement state from that history without re-fetching any source.
3. Produced a new `/agents/brief.md` (32.8 KB) and a new `/agents/_research-consolidated.md` (22 KB) that **explicitly** opened with the disclaimer:

   > *"Reconstructed from chat history because prior session's files did not persist to disk."*

4. Zero `web_search` or `web_scrape` calls during the re-run (verified against `researcher-web-mcp/audit/fetch.jsonl` — no rows appended after the run start).

The agents correctly identified that the deliverables had been wiped, correctly chose to reconstruct rather than restart, and used a tool affordance (`talk_get_messages`) the system prompt does not explicitly suggest for recovery. This is good *agent* behavior — but for the purposes of validating the spike it means the re-run was **not a fresh run**; it was a recovery run.

**Implications.**

- **For Run 2 readiness gates (G-1…G-8 below):** add a new gate — **G-3.5: Talk room history must be truncated or rooms recreated before Run 2 boots**, otherwise Run 2's "fresh" 4-agent run inherits Run 1's research bundles via `talk_get_messages`. The pgdata + `/agents/` wipe alone is insufficient.
- **For v1 design:** Talk chat history-as-substrate is a load-bearing property of the architecture, not just a delivery transport. Agents can and will use it to recover state across runtime resets. This is by design (Roster's whole premise is that Talk is the durable system of record), but it means any "reset to known-clean" workflow has to address the Talk side too — not just the agent runtime.
- **For the [`vezzadev/letta-mcp-channel`](https://github.com/vezzadev/letta-mcp-channel) push-MCP-channel plugin:** the spike polling driver delivers digests of new messages; the v1 channel will surface chat history as MCP resources/notifications. Whatever shape it takes, the property "agents read Talk history on wake" is the design intent — the takeaway is that *the test harness*, not the runtime, has to assume responsibility for clean-state hygiene.
- **For C-2 (memory blocks unused).** The Run 1-redo's failure to write to `human` / `persona` blocks is not evidence that the seeded blocks don't work — it's evidence that the re-run never reached a steady state where memory writes were useful. The agents were in recovery mode for the entire 15 min: read history → reconstruct → write deliverables → idle (the deadline was already past per the reconstructed timeline). Re-validate memory-block usage on Run 2 only.

**Action.** Add Talk-room reset to the Run 2 prep checklist (G-3.5 in the table below). For Run 1-bis on Letta Cloud, the same applies — either truncate the rooms or use fresh room tokens.

### C-6. Run 2 (as-wired, OpenRouter routing) is blocked on upstream Letta fix; Letta Cloud is not the unblock.

C-3 above identified the root cause: Letta's `cache_control` injection lives only in `anthropic_client.py`, not in the OpenAI-compatible OpenRouter path the spike uses. Filed upstream on 2026-05-22 21:05 UTC as [letta-ai/letta#3351](https://github.com/letta-ai/letta/issues/3351) ("OpenRouter / OpenAI-compatible path skips cache_control injection") with bench numbers + the code-path investigation. The spike does not draft patches; it tracks the issue's resolution.

**Block decision.** Running the 4-agent Run 2 on the broken path costs roughly $100/run for ~$75 of work that should land cached — about 24% over budget on the Run-1 extrapolation in C-3, with both Opus (1 of 4 agents) and Sonnet (3 of 4) paying full list price across ~16M+ prompt tokens per main run. Pressing ahead burns SC#6 headroom for zero diagnostic gain — the cost root cause is already understood, and the brief-quality variable is independent of cache state.

**Unblock options re-evaluated:**

- **(b) BYOK Anthropic-direct (recommended).** Wire Letta against `ANTHROPIC_API_KEY` directly instead of `OPENROUTER_API_KEY`; switch model handles from `openrouter/anthropic/claude-{opus-4.7,sonnet-4.6}` to the native `anthropic/claude-*` handles (exact slugs verified against Letta's model registry post-switch). Letta's `anthropic_client.py` emits `cache_control` correctly today — verified by upstream code-grep (C-3) and externally benched: the `pi` harness on the same OpenRouter key + same workload reports `CachedInputTokens` 23,536 at turn 2 for $0.009, vs Letta-via-OpenRouter at $0.061 for the same turn (numbers from the #3351 issue body). Trade-off: lose OpenRouter's failover and the per-workspace cost dashboard the spike has been using. The dashboard loss matters operationally — re-instrument with OpenTelemetry → Anthropic-native usage counters before Run 2 kickoff.
- **(a) Patch `openai_client.py` to inject `cache_control` markers** — still viable as a bind-mount alongside the existing `letta-patches/url_validation.py`. Riskier: we'd carry a forked code path for the spike duration, and any image bump invalidates it. Hold as fallback if (b) hits a snag.
- **(c) Wait for the upstream fix.** Issue is freshly filed with no triage label yet. Not a viable timeline.
- **(d) Swap the local container for Letta Cloud — does NOT unblock.** Letta Cloud runs the same `letta-ai/letta` server code (OSS repo, just hosted); the `cache_control` logic still lives only in `anthropic_client.py`. Routing `openrouter/anthropic/*` through Cloud bypasses caching identically to local. Cloud would help **only if combined with the same BYOK + native-handle switch as (b)** — but that switch works on the local container at zero added cost or networking friction.

**Cloud-specific frictions surfaced by the evaluation** (in case Cloud is desired for other reasons later — managed postgres, SLA, multi-host scale):

- **MCP networking is the hard blocker.** Letta Cloud reaches MCPs over `streamable_http` / `SSE` on the public internet. Our 3 sidecars (`nextcloud-mcp-em`, `nextcloud-mcp-researcher`, `researcher-web-mcp`) listen on the local `spike` Docker bridge only. Exposing each would require Cloudflare Tunnel / ngrok / Tailscale Funnel per sidecar + auth-token wiring; per-call latency moves from local-bridge µs to public-internet ms; tunnel reliability becomes a new failure surface during the agent loop. Docs do not list a private-network bridge.
- **MCP tool-name dedup likely still applies.** Same MCP registry code as self-hosted. The v1 API migration guide introduces an optional `project_id` for resource scoping that *may* namespace per project, but the docs don't claim it isolates tool-name collisions. The per-agent-Letta architecture (C-1) likely needs to persist as multiple Cloud agents or multiple projects, not a singleton.
- **Cost overhead.** API Plan is **$20/mo + $0.10/active-agent-month + $0.00015/sec server-tool CPU + LLM pass-through** ([pricing](https://docs.letta.com/guides/build-with-letta/pricing)). Pure overhead given the cache bug is not actually fixed by the swap.
- **Auth + schema swap.** `LETTA_SERVER_PASSWORD` → `LETTA_API_KEY`; base URL `http://127.0.0.1:8283` → `https://api.letta.com`; `letta-client` SDK version must match Cloud's API version per the v1 migration guide. Surfacing here so it's not surprising on the day we *do* migrate for a different reason.

**Conclusion.** Cloud is a non-trivial migration that does not address the cost bug motivating it. Pick (b). Cloud stays parked as a future option once #3351 is upstream-fixed and we have a reason to move off local — managed postgres, multi-host scale, SLA — not as a Run 2 unblock.

**Implication for Run 1-bis.** The original premise (A/B against Letta Cloud's `letta/auto-*` managed handles for cache-hit signal) is invalidated — Cloud bypasses the same code path. Replace with **Run 1-anthropic-direct**: identical 2-agent EM+Researcher workload, identical prompts, but Letta wired to native Anthropic via `ANTHROPIC_API_KEY` + native `anthropic/claude-*` handles. Purpose: confirm cache hits land via Letta's native path on the spike's actual workload shape before a 4-agent rewire. Lands as a new row in [t5-run-ledger.md](t5-run-ledger.md) + [t7-spike-cost.md](t7-spike-cost.md).

## Cost — first OpenRouter trendline (and what it means for SC#6)

**Direct datum (OpenRouter hourly export, 2026-05-22 00:00 and 01:00 UTC buckets — all Run 1 activity falls inside these two hours):**

| Model | Role | Requests | Prompt tokens | Completion tokens | Spend ($) |
|-------|------|---------:|--------------:|------------------:|----------:|
| `anthropic/claude-opus-4.7`   | EM         |  61 |  3,412,552 | 64,024 | **$18.66** |
| `anthropic/claude-sonnet-4.6` | Researcher | 162 | 12,642,979 | 85,778 | **$39.21** |
| **Total** | | **223** | **16,055,531** | **149,802** | **$57.87** |

Wall-clock active research: ~50 min. **Sonnet/Researcher cost 2.1× more than Opus/EM** — the inverse of what a per-token-price reading suggests. Two drivers:

1. **Request volume.** Researcher made 162 LLM calls vs EM's 61 — the agent-driven path through Letta produces one LLM call per tool call (reasoning + tool decision), and Researcher's web-fetch loop dominates that pipe.
2. **Context re-read on every tool call.** 12.6M prompt tokens / 162 requests = ~78K prompt tokens per Researcher call on average. The conversation history + accumulating bundle drafts + every prior tool return get re-read every turn. Sonnet's lower per-token price (vs Opus) is wiped out by ~4× the token volume.

Completion tokens were tiny in both cases (Opus 64K / Sonnet 86K total — about $1/$1 worth at completion rates). **The cost line is prompt-token volume × request count, not completion.**

**Extrapolation to a 4-agent Run 2 (do not take this as a forecast, take it as a topline signal):**

- EM Opus: keeps the Run 1 profile if Analyst depth threads handle their own synthesis → **~$19**.
- Researcher Sonnet: with Analyst peers now generating source requests, request count + bundle size likely both *go up*. Conservative: same as Run 1 → **~$39**. Realistic upper bound: 1.5× → **~$60**.
- Analyst A + B (Sonnet): less web-fetch-heavy than Researcher but heavier reading + drafting load. Mid-band estimate: **~$15–25 each**, possibly higher if their own working-files re-read pattern matches Researcher's.
- **4-agent Run 2 cost band: $85–125 for a comparable ~50–90 min wall-clock.**

SC#6 = $200/mo for a 4-agent team at moderate use. At ~$100/run, the monthly budget funds **~2 main runs per month** — within the SC#6 envelope if "moderate" means a small handful of full briefs per month, not continuous polling.

**Caveats that materially move the number:**

- **Researcher is the cost driver, not EM.** If v1 trims Researcher request volume (e.g., batching multiple search/scrape calls into a single Letta turn instead of one-call-per-tool, or cutting the working-context re-read by tightening Letta's memory-block strategy), the biggest savings live there.
- **Continuous polling vs. intermittent.** Run 1's driver only woke an agent on a real new message — that's the "moderate use" model. A continuous `every 30s` poll that wakes every agent regardless of new messages would multiply request count and burn the budget in hours, not days.
- **OpenRouter markup vs. Anthropic-direct.** The SC#6 baseline in [../design/05-implementation.md](../design/05-implementation.md) "Cost Model" was computed at Anthropic-direct list. OpenRouter adds per-model markup; Run 1's $57.87 is the OpenRouter-priced reality. SC#6 re-baseline is still pending; Run 1 confirms the re-baseline should hold at $200/mo for moderate use but tightly.
- **Reasoning tokens are negligible.** 0.05% of total tokens across both models in Run 1; not a lever worth optimizing.

**Action:** populated [t7-spike-cost.md](t7-spike-cost.md) Run 1 row with the per-model split. Trendline assessment requires the Run 2 data point; do not generalize beyond "Sonnet/Researcher is the cost driver" yet.

## Brief quality — preliminary read (not a formal SC#5 self-grade)

Formal rubric self-grade is deferred to Run 2's brief in [t8-sample-brief.md](t8-sample-brief.md) per the validation plan. Informal observations on Run 1's `run1-artifacts/brief.md`:

- **Concrete recommendation.** Conditional entry H2 2026, $250K Year-1 cap, month-9 hard gate with specific numbers (10 logos / $15K MRR / 85% GRR). Not a "it depends."
- **Named-entity density.** Specific competitors named with dated events (Kargo + TheLorry Jul 2024; Shipper Feb 2024 layoffs; McEasy East Ventures Jul 2022; MileApp pricing IDR 2.5M/mo; Locus + Ingka Oct 2025; etc.).
- **Primary sources cited and traceable.** Footnote map in Appendix A links every non-trivial claim to a URL Researcher actually fetched (cross-checked against `run1-artifacts/researcher-urls-log.md`).
- **Self-aware caveats.** Appendix B explicitly flags GetLatka ARR figures as self-reported, Mastercard MSE Barometer sampling limitation, Michael Page parsing partial truncation, no DJP primary ruling on SaaS-as-royalty, no foreign vertical-logistics SaaS Indonesia-SMB customer roster found. This is the "what we don't know" surface a grader would otherwise have to find themselves.
- **Templating risk minimal.** §3 "what could kill this" + §8 "what would change our mind" are written as concrete inverse-conditions, not as a generic risks list. No 8-dimension-rubric scaffolding.

What a grader could legitimately push on:

- Cost-of-entry section (§5) leans on the Michael Page Salary Guide which was partially truncated in PDF parsing — Researcher's own audit flags this in Bundle E. The salary ranges in §5 should be considered directional.
- Three-source rule for the most load-bearing claims (PT PMA capital reduction; PSE enforcement; SaaS-as-royalty classification) — currently 2 sources each. Run 2 should triangulate further.
- The "channel-partner credibility risk" in §3 is the right framing, but the brief does not name candidate partners. That's an analyst's next-pass deliverable, not a one-shot brief deliverable, but worth calling out.

**Working judgment, not a formal grade:** a multi-AI opinion panel would likely return positive signal on this brief against the rubric in [t1-grading-rubric.md](t1-grading-rubric.md) — but the 4-agent Run 2 is the artifact that matters for SC#5.

## Gaps + risks for Run 2

| # | Gap | Why it matters | Action |
|---|-----|---------------|--------|
| G-1 | No Analyst A / B agent in Run 1 | The analyst↔analyst↔researcher collaboration loop is the SC#5-critical interaction that 2-agent ablation cannot test | Run 2 wires A + B; observe whether DM rooms `A-B`, `A-Researcher`, `B-Researcher` actually carry work or sit unused |
| G-2 | Memory blocks absent (C-2 above) | File-backed notes worked for 1 synthesis agent; 4 agents will hit name collisions / merge conflicts on `/agents/_*-notes.md` | Fix in `wire-run-1.py` before Run 2 boots; verify with agent-driven probe |
| G-3 | `#team` analyst membership mid-run change | Run 1 removed analyst-a from `#team`; the room is currently `em + researcher + admin` (see room snapshot at run end) | Re-add analyst-a, add analyst-b, verify all 4 agents see all 4 as participants before kickoff |
| G-3.5 | Talk room history bleeds across runs (C-5 above) | Run 1-redo showed agents reconstruct deliverables from preserved Talk history via `talk_get_messages`. Run 2 with the same room tokens inherits Run 1's research bundles + brief as substrate, contaminating the "fresh 4-agent run" surface | Truncate `#team`, `EM-Researcher`, `EM-A`, `EM-B`, `A-B`, `A-Researcher`, `B-Researcher` to zero messages **OR** delete and recreate the rooms with new tokens before Run 2 kickoff. Verify via `talk_get_messages(token)` returning `[]` for each room before driver start |
| G-4 | Driver state file carries Run 1's last-seen IDs | Run 2 tick 1 would start advanced past pre-Run-1 history; if Run 2 reuses room tokens, EM will not be re-woken with msg 279 (Run 1's `brief final`) — that's actually the right behavior, but the driver state should be reset to zero so any kickoff messages get delivered cleanly | Truncate `driver-state.local`; rotate or archive `driver.log` |
| G-5 | Inference path + cost cap | Run 2 as-currently-wired (OpenRouter routing) is blocked on [letta-ai/letta#3351](https://github.com/letta-ai/letta/issues/3351) per **C-6 above** — broken `cache_control` injection on the OpenAI-compatible path makes Run 2 ~24% over budget. Letta Cloud does not unblock (same code path). | Adopt option (b) from C-6: switch Letta to native Anthropic via `ANTHROPIC_API_KEY` + `anthropic/claude-*` handles before Run 2 kickoff. Run **Run 1-anthropic-direct** as the verification A/B first. If staying on OpenRouter as fallback, raise the cap to $300 — but native-Anthropic path is the recommended unblock. |
| G-6 | Brief stored separately from t8-sample-brief.md | Run 1's brief is under `run1-artifacts/`; SC#5's referenced location is `t8-sample-brief.md` | Decision: keep Run 1 under run1-artifacts (it's not the SC#5 artifact); Run 2's brief lands in t8-sample-brief.md as planned |
| G-7 | Forced SPOF test (kill -9 Letta) not exercised | Per [t5-run-ledger.md](t5-run-ledger.md) "Forced SPOF" section + D7 + T6, Run 2 should observe reconnect / catch-up after a Letta kill | Schedule the kill at ~50% of Run 2's wall-clock; capture pre/post agent state |
| G-8 | Polling driver still synthronous; no [letta-mcp-channel](https://github.com/vezzadev/letta-mcp-channel) integration | Out of scope for the spike; flagged here so it's traceable | Track on the v1 roadmap, not on Run 2 |

## What stays frozen for Run 2

- EM prompt at hash `e966a65548025d0dfe65ac52a24e4a855ec103de3a2223a966757f304f0ad40f`.
- Researcher prompt at hash `2fff77b9103e233e7a7eea4728e90d668a42fd3e9e3d402c6ac7a86d29435d24`.
- Analyst A prompt at hash `4f715306639f…` (unchanged since first freeze).
- Analyst B prompt at hash `318161ba9304…` (unchanged since first freeze).
- Per-agent Letta architecture in `spike-compose/docker-compose.yml`.
- Researcher-web wrapper image + blocklist (`spike-compose-researcher-web-mcp:latest sha256:cbebd3ca0…`).
- Contamination banned-token list + word-boundary regex in `wire-run-1.py`.

## What changes for Run 2

- **Switch inference from OpenRouter to native Anthropic (C-6 option b).** Wire `ANTHROPIC_API_KEY` into `bring-up.sh`; swap model handles in `wire-run-1.py` from `openrouter/anthropic/claude-{opus-4.7,sonnet-4.6}` to the equivalent native `anthropic/claude-*` slugs; verify `cache_control` markers land on the wire by inspecting one outbound payload via the spike's debug logging (or the `pi`-harness-style turn-2 cache-hit check); land a verification A/B as **Run 1-anthropic-direct** before booting Run 2.
- Wire 4 agents (add Analyst A + Analyst B Letta containers + MCP sidecars, uncomment the stubs in `docker-compose.yml`).
- Reset driver state file; rotate driver.log.
- Add explicit memory blocks (`human` + `persona`) on agent create.
- Re-add analyst-a to `#team`; add analyst-b; create the 5 remaining pair-DM rooms.
- Run 2's brief lands at `t8-sample-brief.md`; run-ledger row + cost row populated as it runs.
- Schedule the forced SPOF (`kill -9 letta-em` mid-flight) at ~50% wall-clock.
