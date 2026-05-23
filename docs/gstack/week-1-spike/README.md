# Week 1 Spike — Index

Parent: [../design.md](../design.md) · Spec: [../design/05-implementation.md](../design/05-implementation.md) Week 1 · [../design/07-refinements.md](../design/07-refinements.md) D1-D8 + T4-A/B/C/D

This folder is where the Week 1 validation spike lives. Files are prefixed with the task ID (T1-T8) that owns their content, sourced from the canonical task list emitted by `/plan-eng-review` on 2026-05-19: `~/.gstack/projects/vezzadev-roster/tasks-eng-review-20260519-181046.jsonl` (lives outside the repo, not a clickable link).

## Gating decision

The spike validates **Success Criterion #5** (see [../design/06-validation.md](../design/06-validation.md)): can a 4-agent team (EM + 2 Senior Analysts + Researcher) produce an analyst-grade market-entry brief without human intervention? If yes, proceed to Week 2 (provisioner code). If no, apply [t2-fallback-bullets.md](t2-fallback-bullets.md) — pivot or stop.

## Task → file map

| Task | Priority | Effort (human / CC) | Owning file(s) | Status |
|------|----------|---------------------|----------------|--------|
| T1 | P1 | 3h / 20min | [t1-grading-rubric.md](t1-grading-rubric.md) | ✅ done — 8 dimensions remapped to actual BCG Vietnam section order; "5 = better" tier codes the gaps BCG itself doesn't fill (paired mitigations, decision framework, archetype bifurcation, consistent forecast methodology) |
| — | — | — | [spike-compose/](spike-compose/) | ✅ stood up — `docker-compose.yml` brought up + bind-mounted Letta SSRF patch (`letta-patches/url_validation.py`); `wire-run-1.py` provisions per-agent Letta containers + MCP wiring; `driver.py` synchronous Talk→Letta relay (~12 ticks across Run 1 with 0 lost messages); `show-trace.py` ad-hoc reasoning-trace dump. Squid not used — replaced by Firecrawl-side blocklist in `researcher-web-mcp/` per PR #29 |
| T2 | P1 | 30min / 5min | [t2-fallback-bullets.md](t2-fallback-bullets.md) | ✅ done — 3 failure modes × 4 alternatives + terminal exits |
| T3 | P1 | 2h / 10min | (this folder) | ✅ done — 11 files scaffolded |
| T4 | P1 | 3d / 1d | [t4-mcp-investigation.md](t4-mcp-investigation.md) | ✅ done — adopt cbcoutinho/nextcloud-mcp-server; MVP build skipped |
| T5 | P1 | 2d / 4h | [t5-run-ledger.md](t5-run-ledger.md), [t5-system-prompts.md](t5-system-prompts.md), [t5-env-manifest.md](t5-env-manifest.md), [t5-event-timeline.md](t5-event-timeline.md), [t5-what-didnt-work.md](t5-what-didnt-work.md), [t5-researcher-urls.md](t5-researcher-urls.md), [t5-run-1-conclusions.md](t5-run-1-conclusions.md), [run1-artifacts/](run1-artifacts/) | 🟡 **Run 1 done** + **Run 1-anthropic-direct partial** (2026-05-23). The C-6 unblock validated end-to-end on the live spike workload — 60 calls, **91.8% cache hit**, **$1.66** vs Run 1's $57.87 at 0% cache — but no brief was produced: Researcher hung permanently on an SSE-parse bug in Letta's `mcp.client.streamable_http` when a Firecrawl response chunk-split an escaped unicode sequence (a `​` in an Indonesian e-commerce page). **Run 2 (SC#5-gating) is now blocked on the MCP framing bug**; the OpenRouter cache bug [letta-ai/letta#3351](https://github.com/letta-ai/letta/issues/3351) is sidestepped by the native-Anthropic route confirmed here. See [t5-run-ledger.md](t5-run-ledger.md) Run 1-anthropic-direct row for full failure trace + cost rollup |
| T6 | P2 | 15min / 2min | [t5-run-ledger.md](t5-run-ledger.md) "Forced SPOF" section | ⏳ not started — awaits Run 2 mid-flight |
| T7 | P2 | 1h / 15min | [t7-spike-cost.md](t7-spike-cost.md), [exports/run1-openrouter.csv](exports/run1-openrouter.csv) | 🟡 Run 1 ($57.87 at 0% cache) + **Run 1-anthropic-direct ($1.66 at 91.8% cache, partial)** rows in. The 30–50× per-token reduction on the cached path is confirmed empirically on the live spike workload via Azure App Insights / OTel auto-instrumentation (`spike-compose/kql/03-per-agent-cost.kql`). Run 1-anthropic-direct halted before brief.md due to the MCP streamable-http SSE-parse bug — Run 2 cost projection therefore still pending. |
| T8 | P1 | 2h / 30min | [t8-sample-brief.md](t8-sample-brief.md) + AI-panel review file (to be created at T8 time) | ⏳ not started — Run 1's `run1-artifacts/brief.md` is **not** the SC#5 artifact (only 2 of 4 agents); informal preliminary read in [t5-run-1-conclusions.md](t5-run-1-conclusions.md) "Brief quality" section. Formal SC#5 self-grade + multi-AI panel still awaits Run 2 |

Legend: ✅ done · 🟡 partial · ⏳ not started

## Task summary

### T1 — Grading rubric

Author the public-brief-anchored rubric that the founder + multi-AI opinion panel use to score the produced brief. Anchored to publicly available Big-3 market-entry briefs (Codex T1: a founder-invented rubric is a fake gate). File: [t1-grading-rubric.md](t1-grading-rubric.md). Primary comparator is BCG "Vietnam: A Global Engine of Growth" (2023); secondary meta-rubric is McKinsey "Beating the Odds in Market Entry" (2005). Includes the contamination guard cross-references (Layer 1/2/3 controls).

### T2 — Fallback bullets

30-min pre-spike exercise: 3-4 bullet alternative experiments per likely failure mode (Letta unfit / agents do not coordinate / output unusable), lightest-first, each with a terminal "stop and call it" exit. Pre-committed exits to break the motivated-reasoning trap if Week 1 fails (Codex T2 mitigation). File: [t2-fallback-bullets.md](t2-fallback-bullets.md).

### T3 — Folder scaffold

Create this folder with all 9 canonical files specified by D6 + T4-C, so subsequent tasks have homes to land output. Added two extra files during execution: `t2-fallback-bullets.md` (T2's output) and `t5-researcher-urls.md` (contamination guard audit log). Total: 11 files plus this index. T3 produces no content of its own.

### T4 — MCP investigation

Survey existing Nextcloud MCP servers; answer **API coverage** (Talk + Files operations the agents need) and **room-management fit** (one #team room + per-pair DMs), not just "does a server exist." If no community server fits, build a minimal Talk+Files MCP MVP (~3 days). File: [t4-mcp-investigation.md](t4-mcp-investigation.md). **Outcome:** `cbcoutinho/nextcloud-mcp-server` (AGPL-3.0, actively maintained) covers send/read messages + full Files CRUD; room create handled by the provisioner via OCS Talk API. MVP build skipped — saves the 3 days the design anticipated as a contingency.

### T5 — Spike runs

Numbered runs with **prompt freeze per run** + run matrix committed to [t5-run-ledger.md](t5-run-ledger.md) (Codex T4-D mitigation).

- **Run 1: 2-agent smoke (1h hard cap)** — EM + Researcher (pairing swapped from EM + Analyst A pre-kickoff per PR #30 — Researcher is the higher-friction partner to pair the EM with first). Ablation control so a 4-agent failure can be localized to collaboration overhead vs prompt design vs tool friction (Codex T4-A). **Done** 2026-05-22 00:31:23 → 01:21:10 UTC. Outcome: success, structured brief in [run1-artifacts/brief.md](run1-artifacts/brief.md), conclusions in [t5-run-1-conclusions.md](t5-run-1-conclusions.md). Per-agent Letta architecture (one Letta container per agent identity) adopted pre-Run-1 after a tool-namespace collision was discovered under the singleton setup; promoted to a v1 structural decision in [t5-run-1-conclusions.md](t5-run-1-conclusions.md) C-1 after the run validated it under load.
- **Run 1-anthropic-direct: cache mechanism validated, brief not produced (2026-05-23)** — identical 2-agent EM+Researcher workload but Letta wired to native Anthropic via `ANTHROPIC_API_KEY` (handles `anthropic/claude-*`). C-6 confirmed live on the spike workload: 60 Anthropic calls, **91.8% overall cache hit rate** (727,307 cache_read / 792,219 prompt tokens), **$1.66** for the clean run vs Run 1's $57.87 at 0% cache — the expected 30–50× per-token reduction on the cached path. Per-span data lands in Azure App Insights via OTel auto-instrumentation (`spike-compose/Dockerfile.letta` + `spike-compose/docker-compose.otel.yml` + `spike-compose/kql/`). The run did NOT produce a brief: Researcher hung permanently on an SSE-parse bug in Letta's bundled `mcp.client.streamable_http` when a Firecrawl-returned MCP response chunk-split an escaped unicode sequence (a `​` in an Indonesian e-commerce page). Letta's run-cancel surface (`DELETE /v1/runs/<id>`, `POST /v1/agents/<id>/messages/cancel`) cannot recover the orphan; container restart preserves it (postgres-persisted). Bug noted but not yet filed. See [t5-run-ledger.md](t5-run-ledger.md) Run 1-anthropic-direct row for the full failure trace.
- **Run 2: 4-agent main spike** — full team (EM + 2 Senior Analysts + Researcher). Produces the artifact in [t8-sample-brief.md](t8-sample-brief.md). **Now blocked on the MCP streamable-http SSE-parse bug** surfaced by Run 1-anthropic-direct — any Letta agent doing Firecrawl-backed web research at scale will eventually hit a page with an escaped unicode sequence at a chunk boundary and lock up. The original OpenRouter cache bug [letta-ai/letta#3351](https://github.com/letta-ai/letta/issues/3351) is sidestepped: Run 2 will use the native-Anthropic route confirmed in Run 1-anthropic-direct (Letta-Cloud-equivalent for the cache_control codepath). Two unblockers needed before booting Run 2: (a) MCP parser fixed upstream, or (b) `researcher-web-mcp` swapped to stdio or a chunked-aware client. G-1…G-8 readiness list in the same doc still gates kickoff alongside.

T5 also populates: [t5-system-prompts.md](t5-system-prompts.md) (frozen prompts + hashes), [t5-env-manifest.md](t5-env-manifest.md) (container + model versions per run), [t5-event-timeline.md](t5-event-timeline.md) (agent-to-agent message trace), [t5-what-didnt-work.md](t5-what-didnt-work.md) (running dead-end journal), [t5-researcher-urls.md](t5-researcher-urls.md) (Researcher URL fetch log for the contamination guard).

### T6 — Forced SPOF test

During Run 2, `kill -9` the Letta server container mid-flight to observe reconnect/catch-up behavior. One forced kill; full 3-scenario empirical test (clean WS close, kill -9, 60s outage) deferred to v1.x — carried risk acknowledged (Codex Q9 / D7). Verdict lands in [t5-run-ledger.md](t5-run-ledger.md) "Forced SPOF" section.

### T7 — Cost tracking

Hourly OpenRouter usage export + mid-week and end-week trendline check against **SC#6 ($200/mo for 4-agent team)**. Topline signal only; per-call instrumentation deferred to weeks 5-6 (Codex D8 mitigation). File: [t7-spike-cost.md](t7-spike-cost.md); raw exports under [exports/](exports/).

**Run 1 finding (2026-05-22):** OpenRouter spend matches list price to the cent at zero prompt caching (Opus EM $18.66 + Sonnet Researcher $39.21 = $57.87). Per-request `native_tokens_cached: 0` across all sampled rows. Root cause traced to Letta's `cache_control` injection being scoped to `anthropic_client.py` only, not the OpenAI-compatible OpenRouter path the spike uses (see [t5-run-1-conclusions.md](t5-run-1-conclusions.md) C-3). **Filed upstream as [letta-ai/letta#3351](https://github.com/letta-ai/letta/issues/3351)** with bench numbers + code-path investigation.

**Run 1-anthropic-direct finding (2026-05-23):** native-Anthropic switch validates the C-6 unblock end-to-end on the live spike workload — 60 Anthropic calls before halt, **91.8% overall cache hit rate** (727,307 cache_read / 792,219 prompt tokens), **$1.66** total clean-run spend vs Run 1's $57.87 uncached-OpenRouter equivalent. Per-service: letta-em (Opus 4.7) 17 calls = $1.25; letta-researcher (Sonnet 4.6) 43 calls = $0.41. Source: Azure App Insights via OTel auto-instrumentation (`spike-compose/Dockerfile.letta` derived image + `spike-compose/docker-compose.otel.yml` collector overlay + `spike-compose/kql/03-per-agent-cost.kql`). Run halted before brief.md by the MCP streamable-http SSE-parse bug — see T5 above. Run 2's cost projection on the 4-agent workload therefore remains pending on a successful brief-producing run.

### T8 — Gate decision

After Run 2 artifact lands: founder self-grades the brief against [t1-grading-rubric.md](t1-grading-rubric.md). Multi-AI opinion panel (Codex + Claude + others) reviews independently against the same rubric. **Only if the panel signal is positive** is a paid practicing analyst recruited (Week 2 first 3 days). The AI-panel review file is created at T8 time and lives in this folder. Spike artifact in [t8-sample-brief.md](t8-sample-brief.md).

## Contamination guard

A high grading score is meaningless if the brief is paraphrased from a public consulting brief. See [t1-grading-rubric.md](t1-grading-rubric.md) "Contamination guard" for the three-layer threat model and controls, [t5-system-prompts.md](t5-system-prompts.md) "Prompt sanitization rules" for prompt-level enforcement, [t4-mcp-investigation.md](t4-mcp-investigation.md) "Network and ACL policy" for the Nextcloud folder split + Researcher domain blocklist, and [t5-researcher-urls.md](t5-researcher-urls.md) for the per-fetch audit log.

## Calendar

Time-box: 1 week (calendar reality: 1.5-2 weeks was the original budget when a 3-day MCP MVP build was the anticipated contingency; T4's adoption of cbcoutinho removed that contingency, so the spike is back to ~1 week unless mid-run gaps surface).

## Cross-references

- Design TOC: [../design.md](../design.md)
- Week 1 spec: [../design/05-implementation.md](../design/05-implementation.md)
- Success criteria + open questions: [../design/06-validation.md](../design/06-validation.md)
- Decisions D1-D8 + Codex tensions T1-T4-D: [../design/07-refinements.md](../design/07-refinements.md)
