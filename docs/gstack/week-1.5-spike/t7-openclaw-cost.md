# T7' — OpenClaw cost tracking

Parent: [README.md](README.md) §T7'

Topline cost signal against **SC#6 ($200/mo for 4-agent team)**. Per-call
instrumentation reuses Week 1's KQL backend — same cache columns, same
per-agent breakdown query — so 1.5 numbers can be diffed directly against
Run-1-anthropic-direct ($1.66 at 91.8% cache).

Status: ⏳ produced by T5' runs.

## Baseline to beat

| Run | Cost | Cache hit | Per-agent breakdown | Source |
|---|---|---|---|---|
| Week 1 Run 1 (OpenRouter) | $57.87 | 0% | EM $18.66 / Researcher $39.21 | `../week-1-spike/exports/run1-openrouter.csv` |
| Week 1 Run 1-anthropic-direct (partial) | $1.66 | 91.8% | EM $1.25 / Researcher $0.41 (60 calls before halt) | App Insights via `kql/03-per-agent-cost.kql` |

Week 1.5 target: 4-agent main run at **≤ $10** total clean-run spend
(extrapolation from Run-1-anthropic-direct's 2-agent $1.66 → 4-agent ~$4-$6
analyst work + heartbeat polling overhead per F-O5).

## New cost line vs Week 1: heartbeat polling

OpenClaw's heartbeat fires every N minutes (default 30, OAuth 60, F-O2 may
push to 5). Each firing is a model call even when the agent returns
`HEARTBEAT_OK`. This is a **new cost line that didn't exist in Letta** —
Letta's "tick" was a driver-side poll that never hit the model unless there
was actual work.

Tracking requirement: tag heartbeat-only calls with a distinguishing span
attribute (`openclaw.heartbeat=true`) so `kql/03-per-agent-cost.kql` can
separate them from work calls. The KQL query needs a `heartbeat_tokens`
column added — that's T9' scope.

Disentangled rollup target post-Run-2':

```
| Agent     | Work calls | Work tokens | Work $ | HB calls | HB tokens | HB $ | Total $ |
|-----------|------------|-------------|--------|----------|-----------|------|---------|
| em        |            |             |        |          |           |      |         |
| senior-a  |            |             |        |          |           |      |         |
| senior-b  |            |             |        |          |           |      |         |
| researcher|            |             |        |          |           |      |         |
| **Total** |            |             |        |          |           |      |         |
```

## Mid-spike checkpoint

After Run 1' smoke completes, project Run 2' cost using:

```
projected_run_2 = (run_1_work_cost / 2) * 4 + (heartbeat_call_rate × heartbeat_token_avg × 4 × run_2_duration_s)
```

If projected > $50, escalate F-O5 fallback before booting Run 2'.

## Exports

- `exports/openclaw-run-1-anthropic.csv` — raw App Insights export, populated post-Run 1'
- `exports/openclaw-run-2-anthropic.csv` — same, post-Run 2'

## Cross-references

- Week 1 cost methodology: [../week-1-spike/t7-spike-cost.md](../week-1-spike/t7-spike-cost.md)
- KQL queries: [../week-1-spike/spike-compose/kql/](../week-1-spike/spike-compose/kql/)
- The bug that made OpenRouter useless for cost: [letta-ai/letta#3351](https://github.com/letta-ai/letta/issues/3351) (sidestepped by Anthropic-native in both runtimes)
