# Caching bench — Letta vs opencode vs pi

Three-harness bench to validate whether Anthropic prompt caching is
exercised end-to-end when each harness routes the same workload through
OpenRouter to `anthropic/claude-sonnet-4.6`.

Motivation: Run 1 of the t5 spike showed every Letta-via-OpenRouter
request paying full uncached list price. We want to know whether other
harnesses on the same OpenRouter path actually cache. See
[../t5-run-1-conclusions.md](../t5-run-1-conclusions.md) §C-3.

## Setup

- `workload.md` — concatenation of Run 1's `brief.md` + `t5-run-1-conclusions.md`. ~63 KB / ~16 K tokens of stable content. Loaded as system prompt (Letta, pi) or attached file (opencode).
- 2-turn workload per harness, same questions:
  1. "In one sentence, what is the main strategic conclusion of this brief?"
  2. "Now in one sentence, what is the most surprising finding?"
- All three harnesses point at the same OpenRouter key (`spike-compose/openrouter.local`, `ApiKeyName=roster-1`). Time-windowed split in Log Analytics.
- Observability: Azure LA workspace `la-openrouter-swec-01` / table `OpenRouter_CL` (see `../../../AGENTS.md` LLM observability section).

## Runners

| Harness | Script | Notes |
|---------|--------|-------|
| Letta `0.13.x` (image digest `aa66c3eeee13`) | `run-letta.py` | Uses live spike Letta server on `127.0.0.1:8283`. Creates a fresh agent with workload as system prompt, sends 2 messages, deletes agent. |
| opencode `1.15.7` | `run-opencode.sh` | `opencode run --file workload.md` for turn 1, `--continue` for turn 2. Provider configured at `~/.config/opencode/opencode.json`. |
| pi-coding-agent `0.74.0` | `run-pi.sh` | `pi --provider openrouter --append-system-prompt workload.md` for both turns, `--continue` for turn 2. |

## Results (2026-05-22)

Query: `OpenRouter_CL` rows for `anthropic/claude-sonnet-4.6` between 20:50:00 and 20:55:30 UTC, counting exact occurrences of `"cache_control":{"type":"ephemeral"}` in the outbound `Input` payload.

| Harness | Turn | PromptTokens | CachedInputTokens | `cache_control` markers in payload | Cost (USD) |
|---------|-----:|-------------:|------------------:|----------------------------------:|-----------:|
| **pi**       | 1 |  23,539 |      0 | 2 |  $0.0893 |
| **pi**       | 2 |  23,623 | **23,536** | 2 |  **$0.0090** |
| **opencode** | 1 |  45,388 |      0 | 2 |  $0.1713 |
| **opencode** | 2 |  45,460 |      0 | 2 |  $0.1717 |
| **letta**    | 1 |  20,020 |      0 | **0** |  $0.0613 |
| **letta**    | 2 |  20,117 |      0 | **0** |  $0.0611 |

Interpretation:

- **pi** is the clean working comparison: cache_control markers present, turn 2 reads the ~23 K-token cache, cost drops ~10× ($0.0893 → $0.0090).
- **opencode** injects cache_control markers but turn 2 still misses the cache. The two turns' system-message lengths differ by 5 chars (56430 → 56435) — a dynamic field at the start of the cache-eligible prefix invalidates the entire cache. Matches the symptom in [sst/opencode#20110](https://github.com/anomalyco/opencode/issues/20110). opencode is *trying* to cache but has a separate known bug; this bench does not demonstrate cost savings for opencode.
- **letta** emits zero cache_control markers on the OpenRouter / OpenAI-compatible path. This matches the source-code finding that cache-control injection lives only in `letta/llm_api/anthropic_client.py`. Both turns pay full uncached price.

The pi vs Letta delta is the cleanest exhibit for the upstream bug report.

## Reproducing

```bash
cd docs/gstack/week-1-spike/caching-bench
./run-pi.sh        # pi: ~$0.10 burn
./run-opencode.sh  # opencode: ~$0.35 burn
python3 run-letta.py  # letta: ~$0.12 burn (requires spike-compose stack up)
```

Then:

```bash
az monitor log-analytics query \
  --workspace 0e1dc4da-9ef1-4e44-9fd5-d9d5a97ecb91 \
  --analytics-query "OpenRouter_CL
| where TimeGenerated > ago(1h)
| where Model == 'anthropic/claude-sonnet-4.6'
| extend CC=countof(tostring(Input), '\"cache_control\":{\"type\":\"ephemeral\"}')
| project TimeGenerated, PromptTokens, CachedInputTokens, Cost, CC
| order by TimeGenerated asc"
```
