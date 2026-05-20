# Grading Rubric

Public-brief-anchored rubric used for self-grading the spike's [sample-brief.md](sample-brief.md) and as input to the multi-AI opinion panel.

Parent: [../design.md](../design.md) · Spec: [../design/06-validation.md](../design/06-validation.md) SC#5 · [../design/07-refinements.md](../design/07-refinements.md) D2

## Dimensions

Scoring scale: **1 (clearly worse than comparator) — 3 (rough parity) — 5 (clearly better)**. Sub-3 on any single dimension is a fail signal for that dimension regardless of average. Dimensions are drafted to map onto the structural pattern observed in the comparator briefs (see [Anchor](#anchor) below).

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

## Anchor

The rubric is anchored to **publicly available Big-3 market-entry briefs**, not a founder-invented spec. Codex T1: a founder-invented rubric is a fake gate.

Honest framing: Big-3 firms rarely publish full client market-entry decks (those are confidential). The closest public analogues are firm-published thought-leadership pieces that follow market-entry structure. The set below has been verified accessible (PDFs hosted on the firms' own domains as of 2026-05).

**Primary comparator: BCG, "Vietnam: A Global Engine of Growth" (2023)**
- URL: https://web-assets.bcg.com/2c/b0/af4990ba41bf8be7e6301789a7be/vietnam-a-global-engine-of-growth.pdf
- Why this one: Full slide deck, geography-entry framing, recent (2023), covers macro indicators → sector deep-dives → success factors → entry recommendations. Closest to the canonical market-entry brief shape in the verified set.
- Sections used as rubric structure: Executive summary → market context (macro/social) → sector deep-dives → "4 success factors for entrants" → market-entry recommendations.

**Secondary comparator: McKinsey Quarterly, "Beating the Odds in Market Entry" (Horn, Lovallo, Viguerie, 2005)**
- URL: https://www.mckinsey.com/~/media/McKinsey/Business%20Functions/Strategy%20and%20Corporate%20Finance/Our%20Insights/Beating%20the%20odds%20in%20market%20entry/Beating%20the%20odds%20in%20market%20entry.pdf
- Why this one: Meta-rubric source. Names the 6 predictors (scale, relatedness, complementary assets, order of entry, life-cycle stage, tech innovation) and 5 inside-view dimensions (value prop, market size, competition, share/revenue, costs) that practicing analysts actually use. Use this when scoring rubric dimensions 2-7 for "is this how a Big-3 analyst would frame it?"

**Additional references (for AI-panel and structure cross-checks):**

- BCG, "Foreign E-Tailers Are Here! Is South African E-Commerce Ready?" (Nov 2024) — https://web-assets.bcg.com/b5/b4/333e56944145a10f0d57408b8067/foreign-e-tailers-are-here-is-south-african-e-commerce-ready-3.pdf — inverse angle (defense vs entry).
- Bain, "Are You Ahead of the Curve in Emerging Markets?" (~2012) — https://media.bain.com/Images/INDUSTRY_BRIEF_Ahead_of_curve_in_emerging_markets.pdf — bifurcated tracks (enter-vs-defend) pattern.
- BCG, "Changing Your Orbit" India (Jun 2014) — https://web-assets.bcg.com/img-src/Changing-Your-Orbit-Jun-2014-India_tcm9-28793.pdf — explicit 3-step entry framework.

**Structural pattern observed across all five:** context/sizing → competitive landscape → 3-6 success-factor framework → entry-mode or strategic-option decision → recommendation, often bifurcated (enter-vs-defend or aggressive-vs-cautious). The 8 rubric dimensions above were drafted to map onto this pattern.

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
