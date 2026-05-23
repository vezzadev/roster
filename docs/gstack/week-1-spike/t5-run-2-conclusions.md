# Run 2 Conclusions — local-sandbox web tools (Modal retirement)

Reads what the Run 2 transcript means for the Modal-vs-local-sandbox tooling decision and surfaces a new behavioral finding about multi-agent coordination. Sourced from [t5-run-1-conclusions.md](t5-run-1-conclusions.md) (baseline), [spike-compose/run-2-local-sandbox-tools/artifacts/](spike-compose/run-2-local-sandbox-tools/artifacts/) (brief + bundles + URL log), [spike-compose/run-2-local-sandbox-tools.kickoff.log](spike-compose/run-2-local-sandbox-tools.kickoff.log), and `spike-compose/driver.log` (relayed off-disk before container shutdown).

Parent: [../design.md](../design.md) · Prior: [t5-run-1-conclusions.md](t5-run-1-conclusions.md) C-6 (cache fix), [t5-run-ledger.md](t5-run-ledger.md) (Modal infra ledger)

## Topline

**Run 2's tooling goal was met. Its engagement output was thin.**

The Modal sandbox path was abandoned during T5 (cloudpickle `PyCapsule` error when deploying from a FastAPI request context — see [Modal teardown](#modal-teardown)). Run 2 validated that **Letta's LOCAL sandbox with `use_venv=True` + `pip_requirements=["firecrawl-py"]`** is a working substitute: tools register as `custom`, the venv builds once at `/root/.letta/tool_execution_dir/venv` (~30-60s one-time), and per-call dispatch is fast. Researcher executed 32 real `web_scrape` / `firecrawl_search` calls in the first 14 minutes, with status codes (200 / 403 / 404 / DNS failed / paywall) preserved per URL — same fidelity as the retired `researcher-web-mcp` wrapper, minus the Node sidecar and Modal dependency.

The engagement itself deadlocked at 14 minutes into a 60-minute cap. EM and Researcher produced a partial brief (~7.3KB, 1 of 5 sections fully written, 9 sourced footnotes), two Thread-A bundles (a 6KB first cut and a 16.7KB live version), and a Thread-B competitive scan (8.7KB, 7 named players assessed) — then both agents went idle for 46 minutes with no further wakes because the Researcher silently wrote files to `/agents/research/` without posting per-bundle Talk notifications, the EM had no recurring poll mechanism, and the driver had no Talk messages to relay.

**Bottom line: the infrastructure path forward is clear (LOCAL sandbox replaces Modal for v1). The 2-agent collaboration loop has a coordination gap that 4-agent Run 2 plans should address before the gating SC#5 artifact.**

> **Follow-up (2026-05-23): F-1 / F-2 superseded by structural driver fix.** PR #39 added a periodic-tick wake fallback to `driver.py` (`TICK_PERIOD_S=600`) so the EM and any other agent get woken every 10 min of idle even when no Talk activity arrives — backstop for the silent-write deadlock without relying on producer-side prompt rules. Two 2-agent re-runs (rows `2-2agent-tickfix-1` and `2-2agent-tickfix-2` in [t5-run-ledger.md](t5-run-ledger.md)) loaded the fix cleanly and ran for 15 + 35 min respectively with no deadlock; the second produced ~123 KB of consultancy content (5 research items + EM-absorbed analyst doc) for $19.66 at 87% cache hit. The tick path itself was *not* exercised in either run — agents stayed within 10 min of their last Talk activity the whole time. Full analysis: [t5-run-2-rerun-conclusions.md](t5-run-2-rerun-conclusions.md).

## What this run validated

### V-1. LOCAL sandbox is the v1 Python-tools path. Modal is dropped.

Sandbox config persisted at the Letta-Researcher container:

```json
{ "type": "local",
  "config": {
    "sandbox_dir": "/root/.letta/tool_execution_dir",
    "use_venv": true,
    "venv_name": "venv",
    "pip_requirements": [{"name": "firecrawl-py"}]
  } }
```

First call triggered a venv build with full transitive resolution (`firecrawl-py` + httpx, aiohttp, pydantic, etc.). Subsequent calls executed in milliseconds against the cached venv. Researcher's URL audit log ([artifacts/researcher-urls-log.md](spike-compose/run-2-local-sandbox-tools/artifacts/researcher-urls-log.md)) shows 32 distinct Firecrawl calls in 06:00 of wall-clock — same per-call latency profile as the Modal path's expected behavior, achieved without Modal infrastructure.

### V-2. Reserved-name override is a real footgun (and fixable)

Letta's `constants.BUILTIN_TOOLS = ["run_code", "run_code_with_tools", "web_search", "fetch_webpage"]` silently reclassifies any CUSTOM tool registered under those names to `tool_type=letta_builtin` and drops the source. Initial Run 2 wiring (registering as `web_search`) produced a tool the agent could call by name but whose body was the empty builtin stub. Renaming to `firecrawl_search` produced a working CUSTOM tool. The `wire-local-tools.py` script now uses `firecrawl_search` + `web_scrape` (the latter is not on the reserved list).

### V-3. Anthropic-direct cache path still working

EM kickoff turn (run-d2044028, Opus 4.7, 18 steps, ~104s): prompt = 2,072,148, **cached_in = 2,005,683 (96.8% hit)**, cache_write = 66,410, completion = 6,923. Matches the C-6 fix from Run 1-anthropic-direct — the native Anthropic-client path injects `cache_control` markers; cache hit rate per turn is 95-97% once the system prompt + memory blocks are warm.

## What this run revealed

### F-1. Per-bundle Talk notifications are not optional; the multi-agent loop deadlocks without them

**Timeline (`spike-compose/driver.log`):**

| time     | event                                                                |
|----------|----------------------------------------------------------------------|
| 04:31:11 | driver started, 1h cap                                               |
| 04:31:13 | kickoff posted to EM (`/v1/agents/<em>/messages` direct call)        |
| 04:32:16 | wake researcher — #team msg 327 (EM's kickoff brief)                 |
| 04:37:57 | wake em — #team msg 328 (Researcher's receipt confirmation)          |
| 04:38:10 | wake researcher — DM msg 329 (EM "checking in — no file yet")        |
| 04:43:51 | wake em — DM msg 330 (Researcher "draft now live at A-...")          |
| 04:45:45 | wake researcher — #team msg 331 (EM "Thread A — received, high quality") |
| 04:45:52 | researcher run started, **failed** after ~6s                         |
| **04:45:52 — 05:31:36 (46m)** | **no further wakes, no Talk activity, both agents idle** |
| 05:31:36 | driver hard cap reached                                              |

In that idle window, file timestamps show the Researcher **had already written** `A-indonesia-3pl-sme-landscape.md` (04:40:48) and `B-competitors.md` (04:41:45) — without posting Talk notifications about them. EM never knew. The driver only relays Talk messages, so without per-bundle pings, the wake signal dried up.

The Researcher's final wake (msg 331) produced a Letta run marked `status=failed` 6 seconds in. Cause not in scope here, but it didn't matter — even if that run had succeeded, the protocol gap was already manifest: two bundles written, zero notifications.

**Recommendation for Run 2 (4-agent, gating):** the Researcher (and any other producer agent) must post to its assigned Talk room **on every file write**, even a one-line "wrote `<path>`, key claim: <X>". The system prompt should make this non-optional. Optionally, the EM should `talk_send_message` itself a no-op wake every N minutes if no other activity has occurred — periodic self-poll — but the cleaner fix is upstream at the producer.

### F-2. EM busy-poll pattern wastes step budget when waiting

EM's kickoff turn used 50 steps (its full budget) — ~25 of them in a tight alternating loop of `talk_get_messages(token=#team)` + `nc_webdav_list_directory(/agents/research)`, each returning empty / same-state, while waiting for the Researcher to produce anything. The kickoff turn nominally produced 6,923 completion tokens; a large fraction was spent on reasoning about whether to poll again.

This costs money on every Run (Opus 4.7 prompt at $5/M with 97% cache hit is still real spend on the cache-write portion) and is the dominant contributor to EM's first-turn cost in Run 2. Two fixes worth trying in Run 2 v2:

- **(a) Earlier yield.** System-prompt rule: "After kickoff (`talk_send_message` to #team), yield. Do not poll for responses. The driver will wake you when a participant replies."
- **(b) Pacing guidance.** If polling is needed (e.g. EM mid-synthesis waiting on a specific bundle), enforce a `time.sleep(N)` between checks via a tool, not by burning reasoning steps.

(a) is the cleaner change and matches the driver-mediated wake pattern in [v1_letta_channel.md](../../../README.md#v1-channel) (Roster v1 uses [`vezzadev/letta-mcp-channel`](https://github.com/vezzadev/letta-mcp-channel) which has the same wake semantics). The current EM persona doesn't have an explicit yield rule; adding one is a 2-line system-prompt edit.

### F-3. Letta `/v1/runs/{id}` and related endpoints have a path-param parse bug

`GET /v1/runs/run-cbcf5aa8-...-c9b7ee3e8c33` returns 404 with `"Run not found with id='['run-...']'"` — the server is wrapping the path component in a list. `/usage` works, but `/metrics`, `/steps`, and the raw run-by-id endpoint do not. Worked around by listing runs and reading them from `/v1/runs/` (which returns a list with all fields). Not blocking; flagging for future bug-file decision (per [upstream_research_isolation](../../../README.md#contributing) memory, no upstream filing without explicit ask).

## Cost

Run-2 active window: 04:23:52 (first EM run) → 04:45:51 (last Researcher run), ~22 minutes of actual compute across 11 runs (5 EM Opus + 6 Researcher Sonnet, including 2 failed and 1 cancelled).

Token aggregates (from `/v1/runs/{id}/usage`):

| Agent             | Prompt tokens | Completion tokens |
|-------------------|--------------:|------------------:|
| EM (Opus 4.7)     |     3,005,643 |            19,110 |
| Researcher (S4.6) |     3,900,215 |            36,819 |
| **Total**         | **6,905,858** |        **55,929** |

Cost estimate against published Anthropic-direct prices (Opus 4.7: $5/$25/$0.50/$6.25 in/out/cache-read/cache-write per M; Sonnet 4.6: $3/$15/$0.30/$3.75 per M). Cache hit rate verified at 96.8% for the kickoff turn; assumed similar across the other 10 runs (system prompt + memory blocks dominate the prompt; conversation deltas are small).

| Scenario        | EM     | Researcher | Total     |
|-----------------|-------:|-----------:|----------:|
| 0% cache (worst)|  $15.62|     $12.34 |    $27.96 |
| 90% cache       |   $3.34|      $2.78 |     $6.13 |
| 97% cache       |   $2.39|      $2.04 |   **$4.43** |

Baseline: Run 1-anthropic-direct cost $1.66 actual for 50 minutes of work that produced a full brief and 6 bundles. Run 2 spent ~3× more for ~30% of the output. Most of that overhead is in the EM kickoff turn (run-d2044028, 2.07M prompt, single turn = ~$1.20 at 97% cache hit on its own) — see F-2 above. The deadlock didn't add cost (agents were idle, not burning tokens), but it didn't add value either.

Anthropic admin-API endpoints (`/v1/organizations/cost_report`, `/v1/organizations/usage_report/messages`) require an Admin API key; the spike's `anthropic.local` is a regular API key, so the actual billed cost isn't directly verifiable from this side. Estimate above is the best read.

## Modal teardown

Recorded here for v1 doc cross-reference. Sequence in T5 was:

1. Configure `SandboxConfig(type=MODAL)` via REST — required structurally matching the Pydantic union (the `type` field is `@property`, not a stored field; Pydantic resolves by field set, so `npm_requirements: []` was the discriminator that disambiguated from `E2BSandboxConfig`).
2. Register tool with `X-Experimental-Modal-Sandbox: true` header (Letta reads from `dependencies.py:get_headers` alias).
3. Patch in-container `MODAL_DEFAULT_PYTHON_VERSION` from `3.12` to `3.11` to match Letta server image.
4. **First Modal-sandbox tool call from within FastAPI request context → `cannot pickle 'PyCapsule' object` (cloudpickle 3.0).** Server `sys.modules` is polluted with OpenTelemetry + Pydantic 2.11 PyCapsule objects that cloudpickle traverses during function serialization. Isolated `python3 -c` repro outside the FastAPI process succeeded; the same code from a request handler always failed.
5. Tried closure-narrowing patches (extracting `tool.source_code` outside the `@modal_app.function` decorator). Did not help; the pollution is in the parent process at import time.

Per direction in this thread, **stop at root cause; do not file upstream issue or draft patch without explicit ask**. Local sandbox (this run) is the v1 path. Modal-sandbox isolation becomes a v1+ concern if and when it's needed.

## Run 2 v2 — what to change before the gating 4-agent attempt

Three concrete pre-conditions before re-running:

1. **Add producer-side ping rule to Researcher and any Senior Analyst personas:** *"After writing any file under `/agents/`, immediately `talk_send_message` to the relevant Talk room with a one-line summary (path + key claim). No silent writes."*
2. **Add yield rule to EM persona:** *"After posting to a room or sending an assignment, yield. Do not poll for responses; the driver will wake you on replies. Polling is only allowed if you've been explicitly asked to track a long-running job."*
3. **Add a 4-agent registry** (EM + Researcher + Analyst-A + Analyst-B) and verify all four per-agent Letta containers wire CUSTOM tools the same way — this run only exercised 2/4 of the per-agent containers, and `wire-local-tools.py` currently hardcodes the Researcher's URL only.

None of these change the tooling decision (LOCAL sandbox stays); they fix the coordination protocol that surfaced when 2/4 agents weren't enough to keep the loop self-sustaining.
