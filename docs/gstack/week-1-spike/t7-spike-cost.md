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
| 2026-05-22 | $57.87 | +$57.87 | Run 1 (EM + Researcher, ~50 min active). Hit the original $50 OpenRouter cap mid-run; founder raised to $100 and the run resumed. Raw OpenRouter export at [exports/run1-openrouter.csv](exports/run1-openrouter.csv). |

## Per-run cost

| Run | Wall time | Prompt tokens (input) | Completion tokens (output) | Reasoning tokens | Requests | Cost ($) | Notes |
|-----|-----------|----------------------:|---------------------------:|-----------------:|---------:|---------:|-------|
| Run 1 (2-agent smoke, EM + Researcher) | ~50 min active (00:31:23 → 01:21:10 UTC, incl. ~3-min OpenRouter-cap stall) | 16,055,531 | 149,802 | 691 | 223 | **$57.87** | Per-model split: Opus 4.7 (EM) $18.66 / 61 req / 3.4M prompt; Sonnet 4.6 (Researcher) $39.21 / 162 req / 12.6M prompt. **Sonnet/Researcher is the cost driver, not Opus/EM** (2.1× higher) — driven by request count × prompt-token re-read on every tool call. **Zero prompt caching on either model** — verified via OpenRouter per-request JSON (`native_tokens_cached: 0` across all sampled rows). Both Opus and Sonnet billed match list price to the cent at zero cache (Opus 4.7 at $5/M input / $25/M output; Sonnet 4.6 at $3/M / $15/M). Letta's `cache_control` injection lives only in its native Anthropic-client path, not the OpenAI-compatible OpenRouter path used here — see [t5-run-1-conclusions.md](t5-run-1-conclusions.md) C-3 for the root cause + Run 2 fix options. Full Cost section + 4-agent extrapolation in the same doc. |
| Run 1-bis (2-agent cost A/B via Letta Cloud) | | | | | | | pending — same workload as Run 1 but inference via Letta Cloud's managed model handles (`auto-chat` / `auto-fast` / `auto-memory` — exact selection TBD with founder) instead of `anthropic/*` through OpenRouter. Capture: per-request cost from Letta Cloud's billing surface + cache-hit counters if exposed. Compares against Run 1's $57.87 OpenRouter floor on identical prompts and traffic shape |
| Run 2 (4-agent main)  | | | | | | | pending |

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
