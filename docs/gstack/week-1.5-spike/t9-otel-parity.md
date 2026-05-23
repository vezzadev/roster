# T9' — OTel observability parity

Parent: [README.md](README.md) §T9' (spike-blocker)

**Purpose:** verify that the Node.js OpenTelemetry stack instrumenting
OpenClaw produces spans with the same `gen_ai.*` semantic conventions Week 1's
Python wrap (Letta + `opentelemetry-instrument`) emitted, so the existing
KQL queries under `../week-1-spike/spike-compose/kql/` keep working unchanged.

Hard gate. If Week 1's queries don't return populated cache-token columns for
OpenClaw spans, **no T5' run kicks off**, because we can't grade cost or
cache fidelity against Run-1-anthropic-direct's $1.66 / 91.8% baseline.

Status: ⏳ not started.

## Parity matrix

| Signal | Week 1 source | Week 1.5 source (Node) | KQL query that consumes it | Pass condition |
|---|---|---|---|---|
| LLM call exists | `opentelemetry-instrument` auto-wrap of `anthropic` Python SDK | `@opentelemetry/auto-instrumentations-node` with `@opentelemetry/instrumentation-undici` or anthropic-specific instrumentation | `kql/01-llm-calls.kql` | Spans appear with span name = `chat <model>` or `anthropic.messages.create` |
| Input tokens | `gen_ai.usage.input_tokens` attr | same attr name required | `kql/03-per-agent-cost.kql` | Non-null column |
| Output tokens | `gen_ai.usage.output_tokens` | same | `kql/03-per-agent-cost.kql` | Non-null |
| Cache read tokens | `gen_ai.usage.cache_read_input_tokens` | same — **the load-bearing column** | `kql/03-per-agent-cost.kql` | Non-null and matches Anthropic SDK's `cache_read_input_tokens` field |
| Cache create tokens | `gen_ai.usage.cache_creation_input_tokens` | same | `kql/03-per-agent-cost.kql` | Non-null |
| Per-agent attribution | `service.name` set by container | **Single Gateway, multiple agents** — `service.name=openclaw-gateway` for all. Per-agent attribution must come from an OpenClaw-emitted attribute like `openclaw.agent_id` (TBD whether this is auto-emitted; see [openclaw-facts.md](openclaw-facts.md) §"Topology revision") | `kql/03-per-agent-cost.kql` group-by must change from `service.name` to `openclaw.agent_id` | One row per agent id |
| MCP tool call span | implicit via Letta's HTTP client | TBD — OpenClaw's MCP client may not be auto-instrumented; manual wrap likely | `kql/04-tool-latency.kql` (to author) | Spans with `mcp.tool.name` attr + duration |
| Heartbeat call distinguisher | n/a — Letta didn't have this | `openclaw.heartbeat=true` span attr on heartbeat-fired runs | new query in `kql/05-heartbeat.kql` | Distinct from work calls |

## Acceptance test (the gate)

The pass/fail call is **mechanical, not subjective**:

1. Bring up one OpenClaw Gateway with OTel auto-instrumentations + Anthropic SDK
2. Drive a 5-minute single-agent session: 1 prompt-cached system message + 5 turns of `chat` + 1 MCP tool call to a stub MCP server
3. Wait 90s for Azure App Insights to ingest
4. Run **unchanged** `../week-1-spike/spike-compose/kql/03-per-agent-cost.kql` with the OpenClaw `service.name` filter
5. **Pass:** query returns one row, all 4 token columns populated, cache-read column shows ≥1 cached token (the second message should hit cache)
6. **Fail:** any column null or query returns zero rows

Document the pass/fail call at the top of this file with the exact KQL output.

## What if the gate fails

If T9' fails on the off-the-shelf Node OTel instrumentations, this task
becomes the spike's actual deliverable — author whatever instrumentation
shim closes the gap. Likely shim shapes:

- **Wrap the Anthropic Node SDK manually** with an `OTel` decorator that emits `gen_ai.*` attrs from the response's `usage` field. ~1d.
- **Patch the existing KQL queries** to accept either naming convention (Python-emitted vs Node-emitted attrs). Easier on the consumer side, harder to maintain. ~3h.
- **Run a OpenTelemetry Collector processor** that rewrites Node-emitted attrs into the Python naming convention. Cleanest. ~4h.

Decide between these only if the gate fails — pre-deciding wastes effort.

## Outputs

- Top-of-file verdict line (✅ parity / 🚧 shim required / ❌ structural gap)
- `parity-test-output/kql-03-result.csv` — the exact KQL output that made the call
- If shim required: `parity-shim/` with the chosen shim's source

## Cross-references

- KQL queries the gate calls: [../week-1-spike/spike-compose/kql/](../week-1-spike/spike-compose/kql/)
- Letta-side OTel wrap that set the baseline: [../week-1-spike/spike-compose/Dockerfile.letta](../week-1-spike/spike-compose/Dockerfile.letta)
- OTel collector config (reused as-is): [../week-1-spike/spike-compose/otel-collector/](../week-1-spike/spike-compose/otel-collector/)
- The F-8 OTel anthropic-wrap bug that halted Week 1's Run-2-4agent — the Node path **must not** reproduce this: [../week-1-spike/t5-run-2-conclusions.md](../week-1-spike/t5-run-2-conclusions.md) F-8
