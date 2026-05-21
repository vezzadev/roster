# Week 1 Spike — Index

Parent: [../design.md](../design.md) · Spec: [../design/05-implementation.md](../design/05-implementation.md) Week 1 · [../design/07-refinements.md](../design/07-refinements.md) D1-D8 + T4-A/B/C/D

This folder is where the Week 1 validation spike lives. Files are prefixed with the task ID (T1-T8) that owns their content, sourced from the canonical task list emitted by `/plan-eng-review` on 2026-05-19: `~/.gstack/projects/vezzadev-roster/tasks-eng-review-20260519-181046.jsonl` (lives outside the repo, not a clickable link).

## Gating decision

The spike validates **Success Criterion #5** (see [../design/06-validation.md](../design/06-validation.md)): can a 4-agent team (EM + 2 Senior Analysts + Researcher) produce an analyst-grade market-entry brief without human intervention? If yes, proceed to Week 2 (provisioner code). If no, apply [t2-fallback-bullets.md](t2-fallback-bullets.md) — pivot or stop.

## Task → file map

| Task | Priority | Effort (human / CC) | Owning file(s) | Status |
|------|----------|---------------------|----------------|--------|
| T1 | P1 | 3h / 20min | [t1-grading-rubric.md](t1-grading-rubric.md) | ✅ done — 8 dimensions remapped to actual BCG Vietnam section order; "5 = better" tier codes the gaps BCG itself doesn't fill (paired mitigations, decision framework, archetype bifurcation, consistent forecast methodology) |
| — | — | — | [spike-compose/](spike-compose/) | 🟡 compose + .env.example + runbook drafted; copy to ~/spike-runtime/ and step through `docker-compose.yml` bring-up sequence to boot Run 1 |
| T2 | P1 | 30min / 5min | [t2-fallback-bullets.md](t2-fallback-bullets.md) | ✅ done — 3 failure modes × 4 alternatives + terminal exits |
| T3 | P1 | 2h / 10min | (this folder) | ✅ done — 11 files scaffolded |
| T4 | P1 | 3d / 1d | [t4-mcp-investigation.md](t4-mcp-investigation.md) | ✅ done — adopt cbcoutinho/nextcloud-mcp-server; MVP build skipped |
| T5 | P1 | 2d / 4h | [t5-run-ledger.md](t5-run-ledger.md), [t5-system-prompts.md](t5-system-prompts.md), [t5-env-manifest.md](t5-env-manifest.md), [t5-event-timeline.md](t5-event-timeline.md), [t5-what-didnt-work.md](t5-what-didnt-work.md), [t5-researcher-urls.md](t5-researcher-urls.md) | 🟡 prompts frozen 2026-05-21 (4 roles, 0 banned-token hits, hashes recorded); runs await Nextcloud + Letta + Squid setup |
| T6 | P2 | 15min / 2min | [t5-run-ledger.md](t5-run-ledger.md) "Forced SPOF" section | ⏳ not started — awaits Run 2 mid-flight |
| T7 | P2 | 1h / 15min | [t7-spike-cost.md](t7-spike-cost.md) | ⏳ not started — capture method documented; no snapshots yet |
| T8 | P1 | 2h / 30min | [t8-sample-brief.md](t8-sample-brief.md) + AI-panel review file (to be created at T8 time) | ⏳ not started — awaits Run 2 artifact |

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

Two numbered runs with **prompt freeze per run** + run matrix committed to [t5-run-ledger.md](t5-run-ledger.md) (Codex T4-D mitigation).

- **Run 1: 2-agent smoke (1h hard cap)** — EM + Senior Analyst A. Ablation control so a 4-agent failure can be localized to collaboration overhead vs prompt design vs tool friction (Codex T4-A).
- **Run 2: 4-agent main spike** — full team (EM + 2 Senior Analysts + Researcher). Produces the artifact in [t8-sample-brief.md](t8-sample-brief.md).

T5 also populates: [t5-system-prompts.md](t5-system-prompts.md) (frozen prompts + hashes), [t5-env-manifest.md](t5-env-manifest.md) (container + model versions per run), [t5-event-timeline.md](t5-event-timeline.md) (agent-to-agent message trace), [t5-what-didnt-work.md](t5-what-didnt-work.md) (running dead-end journal), [t5-researcher-urls.md](t5-researcher-urls.md) (Researcher URL fetch log for the contamination guard).

### T6 — Forced SPOF test

During Run 2, `kill -9` the Letta server container mid-flight to observe reconnect/catch-up behavior. One forced kill; full 3-scenario empirical test (clean WS close, kill -9, 60s outage) deferred to v1.x — carried risk acknowledged (Codex Q9 / D7). Verdict lands in [t5-run-ledger.md](t5-run-ledger.md) "Forced SPOF" section.

### T7 — Cost tracking

Hourly OpenRouter usage export + mid-week and end-week trendline check against **SC#6 ($200/mo for 4-agent team)**. Topline signal only; per-call instrumentation deferred to weeks 5-6 (Codex D8 mitigation). File: [t7-spike-cost.md](t7-spike-cost.md). v1 routes inference through OpenRouter; OpenRouter markup over Anthropic-direct list price may push SC#6 — re-baseline when the first trendline lands.

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
