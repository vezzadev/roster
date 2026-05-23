# Week 1.5 boot-smoke findings

**Date:** 2026-05-23
**Branch:** `spike/week-1.5-boot-smoke`
**Scope:** Cheapest possible validation of the Week 1.5 spike's load-bearing assumptions before committing to a 2- or 4-agent run.

## Verdict

| Gate | Result |
|---|---|
| Gateway builds + boots | ✅ pass |
| Anthropic API call works through Gateway | ✅ pass |
| OTel spans reach a collector | ✅ pass (via OpenClaw's first-party `diagnostics-otel` plugin) |
| **T9' parity — `gen_ai.usage.*` cache-token columns populated** | 🚧 **partial — primary-turn `model.usage` event not emitted** |

**Recommendation:** halt before T5' Run 1', surface the partial-parity finding, decide whether to (a) patch the gap in OpenClaw core, (b) author a shim that reads `usage` from session transcripts, or (c) widen scope and treat shim authoring as the Week 1.5 deliverable. Same shape as the T9'-gate-fail branch in [t9-otel-parity.md](t9-otel-parity.md) §"What if the gate fails".

## What passed

### Build + boot
- `Dockerfile.openclaw` produces a working image from `openclaw@2026.5.20` on `node:24-bookworm-slim`.
- Gateway starts in `<3s` to `[gateway] ready`, listens on `:18789`, loads `diagnostics-otel` and Anthropic provider, heartbeat correctly disabled per config.

### Chat through Gateway
- `openclaw agent --agent smoke --message "..." --json` returns expected reply for short prompts. `executionTrace.winnerProvider=anthropic`, `winnerModel=claude-haiku-4-5`, `runner=embedded`.

### OTel via OpenClaw's first-party plugin
The generic `@opentelemetry/auto-instrumentations-node` bundle was a dead end — it only ships `instrumentation-{http,undici,dns,net}` and emits no `gen_ai.*` semantic-convention spans for Anthropic. Replaced with `clawhub:@openclaw/diagnostics-otel`, baked into the image. After enable:

**Spans observed:** `openclaw.context.assembled`, `openclaw.diagnostic.phase`, `openclaw.harness.run`, `openclaw.model.call`, `openclaw.run`. The `openclaw.model.call` span carries:
- `gen_ai.system: anthropic`
- `gen_ai.request.model: claude-haiku-4-5`
- `gen_ai.operation.name: chat`
- `openclaw.api: anthropic-messages`
- `openclaw.model_call.request_bytes`, `response_bytes`, `time_to_first_byte_ms`

**Metrics observed (18 per export):** `gen_ai.client.operation.duration`, `openclaw.run.duration_ms`, `openclaw.harness.duration_ms`, `openclaw.queue.*`, `openclaw.session.state`, `openclaw.model_call.*`, `openclaw.memory.*`, `openclaw.telemetry.exporter.events`.

## What failed — the load-bearing gap

The two metrics Week 1's `kql/03-per-agent-cost.kql` consumes are **not emitted** in my run:
- `gen_ai.client.token.usage` (histogram, `gen_ai.token.type=input|output`)
- `openclaw.tokens.*` (counter, `input|output|cache_read|cache_write|total`)

And the `openclaw.model.call` span does **not** carry `gen_ai.usage.input_tokens` / `cache_read_input_tokens` / `cache_creation_input_tokens` attributes that the docs describe.

### Why

The data exists. The session transcript at `/root/.openclaw/agents/smoke/sessions/<id>.jsonl` records the assistant message with full usage:

```json
"usage": { "input": 3, "output": 5, "cacheRead": 0, "cacheWrite": 16471, "totalTokens": 16479, ... }
```

But the diagnostic event that the `diagnostics-otel` plugin subscribes to (`type: "model.usage"`) is emitted from only one site in `openclaw@2026.5.20` core:

```
dist/agent-runner.runtime-Dcz2JPFe.js
  ↑ inside the followupRun / replyPayloads commitment block,
    gated on  isDiagnosticsEnabled(cfg) && hasNonzeroUsage(usage)
```

The plugin's emission code is correct — `recordModelUsage` would write `gen_ai.client.token.usage` and `openclaw.tokens.*` histograms with all four token types if the event fired. It just doesn't fire for primary turns in this build.

### Evidence

- Plugin source `/root/.openclaw/extensions/diagnostics-otel/dist/index.js` includes a handler for `case "model.usage"` that writes both the GenAI semconv histogram and OpenClaw counters with input/output/cache_read/cache_write/prompt/total.
- `grep -rE '"model\.usage"' /usr/local/lib/node_modules/openclaw/dist/` finds exactly one emit site, in the followup path.
- Three smoke chats (`PING`/`PONG`/`TRACE`/`METRIC`/`METRIC2`/"one two three..."), all with non-zero usage in the transcript, produced zero `gen_ai.client.token.usage` and zero `openclaw.tokens.*` data points on the wire.

This is **not** the `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` toggle — that only swaps `gen_ai.system` ↔ `gen_ai.provider.name`. It's an event-emission gap.

## Options

Same shape as T9'-fail branch ([t9-otel-parity.md](t9-otel-parity.md)):

1. **Upstream patch** — add the `model.usage` emit at the primary-turn finalize site in `agent-runner.runtime`. Probably the cleanest fix; ~1d to author + verify, plus the OpenClaw PR-review tail. Likely scope is small (mirror the followup-path block) but I haven't read enough core to be sure.
2. **Transcript-replay shim** — write a sidecar that tails session transcripts (which already carry `usage`), normalizes to OTLP `gen_ai.client.token.usage`, and ships to the collector. Decouples us from upstream; ~4h. Cost: another moving part to keep alive across runs.
3. **Collector-side derivation** — derive token counters from `openclaw.model_call.request_bytes` / `response_bytes` as a *proxy* and reword the spike's cost rubric to "approximate". Worst option — defeats SC#6 ($200/mo) cost accuracy.

## What's deferred

- T4' MCP fidelity (Indonesian unicode-chunk-split) — not touched.
- Workspace `*.md` runtime-contract verification — not touched.
- CVE pin via CHANGELOG search — not touched.
- Frozen system-prompt port from Week 1 — not touched.
- T5' Run 1' (2-agent) and Run 2' (4-agent) — blocked on T9' parity decision.

## Stack state

- Image: `spike-compose-openclaw-openclaw-gateway:latest` (Dockerfile pinned to `openclaw@2026.5.20` + plugin install at build).
- Compose: `docker-compose.boot-smoke.yml` + `agents/openclaw.boot-smoke.json` + `otel-collector-boot-smoke.yaml` + `.env.smoke` (gitignored).
- Bring up: `docker compose --env-file .env.smoke -f docker-compose.boot-smoke.yml up -d`.
- Drive chat: `docker exec openclaw-boot-smoke openclaw agent --agent smoke --message "..." --json`.
- Inspect metrics: `docker logs otel-collector-boot-smoke 2>&1 | grep "Name: gen_ai"`.

## Cross-references

- [t9-otel-parity.md](t9-otel-parity.md) — the gate, including the pre-declared shim options.
- [openclaw-facts.md](openclaw-facts.md) §"Topology revision" — single-Gateway / multi-agent assumption verified end-to-end at boot.
- `/usr/local/lib/node_modules/openclaw/docs/gateway/opentelemetry.md` — OpenClaw's own OTel reference (inside the npm package).
