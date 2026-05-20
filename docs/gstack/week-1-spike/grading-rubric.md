# Grading Rubric

Public-brief-anchored rubric used for self-grading the spike's [sample-brief.md](sample-brief.md) and as input to the multi-AI opinion panel.

Parent: [../design.md](../design.md) · Spec: [../design/06-validation.md](../design/06-validation.md) SC#5 · [../design/07-refinements.md](../design/07-refinements.md) D2

## Anchor

The rubric is anchored to a **publicly available McKinsey / BCG / Bain market-entry brief**, not a founder-invented spec. Codex T1: a founder-invented rubric is a fake gate.

- Public comparator brief: _TBD — link before spike starts_
- Why this comparator: _TBD — match industry / depth / format_
- Sections of the comparator brief used as the rubric structure: _TBD_

## Dimensions

Scoring scale: **1 (clearly worse than comparator) — 3 (rough parity) — 5 (clearly better)**. Sub-3 on any single dimension is a fail signal for that dimension regardless of average.

| # | Dimension | What "3" looks like | What "5" looks like | Sub-3 means |
|---|-----------|---------------------|---------------------|-------------|
| 1 | Section structure | Same headline sections as comparator | Same + meaningful sub-structure | Brief is incoherent or misordered |
| 2 | Market sizing & methodology | TAM/SAM/SOM shown with stated method | + sensitivity analysis | Sizing assertion without method |
| 3 | Competitive landscape | Named competitors with positioning | + 2x2 / strategic groups | Vague "competitors include…" |
| 4 | Customer segmentation | Segments named + sized | + use cases per segment | Single undifferentiated market |
| 5 | Entry mode analysis | 2-3 modes evaluated with trade-offs | + recommendation with reasoning | Single mode, no alternatives considered |
| 6 | Risks + mitigations | Named risks with mitigations | + ranking by likelihood × impact | Risks listed without mitigations |
| 7 | Recommendation clarity | Clear go / no-go / conditional | + first 90-day plan | Wishy-washy "depends" without conditions |
| 8 | Citation discipline | Sources cited for non-trivial claims | + primary sources where possible | Unsourced assertions |

## Honesty guard

Codex T1 (CRITICAL): self-grade is motivated-reasoning-prone. Mitigations:

1. **Fill in scores BEFORE reading the brief end-to-end again** — first impression matters.
2. **For each "3+" score, name a specific quote from [sample-brief.md](sample-brief.md) that justifies it** — no score without evidence.
3. **The multi-AI opinion panel grades against this same rubric independently** — divergence > 1 point on any dimension is a flag.

## Self-grade

| # | Dimension | Score | Evidence quote |
|---|-----------|-------|----------------|
| 1 | Section structure | _–_ | |
| 2 | Market sizing | _–_ | |
| 3 | Competitive landscape | _–_ | |
| 4 | Customer segmentation | _–_ | |
| 5 | Entry mode | _–_ | |
| 6 | Risks + mitigations | _–_ | |
| 7 | Recommendation clarity | _–_ | |
| 8 | Citation discipline | _–_ | |
| | **Average / verdict** | _–_ | |

## Gate decision

| Outcome | Trigger | Next step |
|---------|---------|-----------|
| Strong positive | Self-grade ≥ 4 avg AND AI panel ≥ 4 avg with no sub-3 dimensions | Recruit paid analyst (Week 2, first 3 days) |
| Weakly positive | Self-grade 3-4 OR AI panel split | Discuss with one ICP contact first; analyst recruit only if signal holds |
| Negative | Self-grade < 3 OR AI panel < 3 OR any sub-3 dimension that matters for the comparator | Apply [fallback bullets](#) — pivot or stop, do NOT proceed to Week 2 |
