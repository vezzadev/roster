# T8' — OpenClaw gate-decision brief

Parent: [README.md](README.md) §T8'

The artifact this spike exists to produce. Lands as a Markdown brief at the
end of Run 2' covering Indonesia 3PL market entry — same workload, same
rubric, same blind AI-panel review protocol as Week 1's T8.

Status: ⏳ awaits Run 2' completion in [t5-openclaw-run-ledger.md](t5-openclaw-run-ledger.md).

## Acceptance protocol (unchanged from Week 1)

1. Run 2' produces this brief autonomously — no human edits, no patch-ups
2. Founder self-grades against [../week-1-spike/t1-grading-rubric.md](../week-1-spike/t1-grading-rubric.md) (same 8 dimensions, same tier codes)
3. Multi-AI opinion panel reviews independently against the same rubric (same panel as Week 1: Codex + Claude + at least one other) under the blind protocol — panel doesn't know which runtime produced the brief
4. **Only if panel signal is positive** does the paid analyst hire proceed for Week 2 confirmation

## Comparator artifacts

| Brief | Source | Score | Notes |
|---|---|---|---|
| Week 1 Run 1 `brief.md` | [../week-1-spike/run1-artifacts/brief.md](../week-1-spike/run1-artifacts/brief.md) | informal — see [../week-1-spike/t5-run-1-conclusions.md](../week-1-spike/t5-run-1-conclusions.md) | 2-agent ablation, not SC#5-comparable |
| BCG "Vietnam: A Global Engine of Growth" (2023) | rubric anchor | n/a | Primary rubric anchor, not a comparator |
| This file | this spike | TBD | 4-agent, SC#5 candidate |

## Contamination guard (unchanged)

Per [../week-1-spike/t1-grading-rubric.md](../week-1-spike/t1-grading-rubric.md)
"Contamination guard" — three-layer threat model:

- **Layer 1** (prompt): no consulting brief language in agent prompts. Frozen prompts reused from Week 1 with hash-equivalence check before kickoff.
- **Layer 2** (tools): `researcher-web-mcp` domain blocklist excludes BCG, McKinsey, Bain, Deloitte domains. Same blocklist as Week 1.
- **Layer 3** (artifact): post-run audit checks the brief for verbatim phrase matches against the BCG comparator.

The Researcher URL log lands at `researcher-urls-openclaw.md` in this folder
during Run 2' for the Layer 2 audit.

## Brief structure (template)

Section order mirrors the BCG Vietnam comparator's actual structure, per
Week 1's rubric remap:

1. Executive summary
2. Market context + sizing
3. Competitive landscape
4. Demand signals + segmentation
5. Entry archetypes (bifurcated)
6. Forecast (consistent methodology across scenarios)
7. Decision framework
8. Risks + paired mitigations

Each section graded 0-5 by the rubric, with tier 5 anchored to "fills the
gaps BCG itself doesn't fill" per the T1 design.

## Cross-references

- Week 1 sample brief: [../week-1-spike/t8-sample-brief.md](../week-1-spike/t8-sample-brief.md) (✅ written by Week 1 T8)
- Grading rubric: [../week-1-spike/t1-grading-rubric.md](../week-1-spike/t1-grading-rubric.md)
- Run ledger that produces this: [t5-openclaw-run-ledger.md](t5-openclaw-run-ledger.md)
