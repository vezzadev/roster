# Spike Cost

Cost-tracking summary for the Week 1 spike. Topline signal that SC#6 ($200/mo for 4-agent moderate use) is reachable.

Parent: [../design.md](../design.md) · Spec: [../design/05-implementation.md](../design/05-implementation.md) Cost Model · [../design/06-validation.md](../design/06-validation.md) SC#6 · [../design/07-refinements.md](../design/07-refinements.md) D8 + T7

## Why this file matters

Codex D8 was rated HIGH: a deferred cost story leaves SC#6 unanchored until weeks 5-6, by which point sunk-cost momentum has accrued. Mitigation: **hourly OpenRouter usage exports** + **mid-week and end-week trendline checks** against the $200/mo budget. This is not full per-call instrumentation (that's deferred to weeks 5-6) — it is topline signal only.

OpenRouter is the inference routing layer in v1 (Anthropic models routed through OpenRouter, key in `spike-compose/openrouter.local`). OpenRouter adds a per-model markup over Anthropic-direct list prices, so the SC#6 ($200/mo) math in [../design/05-implementation.md](../design/05-implementation.md) "Cost Model" — which was computed at Anthropic-direct rates — needs to be re-baselined once the first OpenRouter trendline lands.

## Capture method

- Source: OpenRouter dashboard → Activity / usage export → hourly or daily granularity
- Frequency: snapshot at end of each working day during spike + extra snapshot before/after Run 2
- Storage: append CSV/JSON exports under `exports/` next to this file (gitignored if large; commit summary only)

## Daily snapshots

| Date | Cumulative spend ($) | Δ vs prev day | Notes |
|------|----------------------|----------------|-------|
| _empty_ | | | |

## Per-run cost

| Run | Wall time | Input tokens | Output tokens | Cost ($) | Cost / output-token | Notes |
|-----|-----------|--------------|----------------|----------|---------------------|-------|
| Run 1 (2-agent smoke) | | | | | | 1h cap |
| Run 2 (4-agent main)  | | | | | | |

## Trendline checks

### Mid-week (target: day 3 or earlier)

- Spend so far: $_–_
- Projected full-week spend (linear): $_–_
- Projected full-month spend (linear from full-week): $_–_
- Verdict vs SC#6 ($200/mo): _on track / drifting / blown_
- Action if drifting: _which lever to pull — fewer agents / shorter context / cheaper model on which role_

### End-of-week

- Spend total: $_–_
- Projected monthly: $_–_
- Verdict vs SC#6: _on track / drifting / blown_
- Findings to carry into the design's Cost Model section (revise if reality differs):

## Carried risk

Per [../design/07-refinements.md](../design/07-refinements.md) "Carried risks": hourly trendlines catch gross overruns but miss per-agent cost attribution. Per-call instrumentation is still needed by week 5 to know which role is the cost driver.
