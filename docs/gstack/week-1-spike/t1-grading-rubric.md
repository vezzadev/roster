# Grading Rubric

Public-brief-anchored rubric used for self-grading the spike's [t8-sample-brief.md](t8-sample-brief.md) and as input to the multi-AI opinion panel.

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
2. **For each "3+" score, name a specific quote from [t8-sample-brief.md](t8-sample-brief.md) that justifies it** — no score without evidence.
3. **The multi-AI opinion panel grades against this same rubric independently** — divergence > 1 point on any dimension is a flag.

## Contamination guard

A high score is meaningless if the brief is paraphrased from a public consulting brief the agents fetched or recalled from training. Three layers of contamination risk; the first two are addressable, the third is detectable post-hoc only.

| Layer | Risk | Addressable? |
|---|---|---|
| 1 — Direct comparator access | Agents fetch BCG Vietnam (or one of the other 5 anchor briefs) and paraphrase | ✅ pre-spike controls |
| 2 — Adjacent-brief plagiarism | Agents fetch a different Big-3 SEA / Indonesia brief and copy its structure / insights | ⚠️ partially — domain blocklist catches verbatim, not derivative recall |
| 3 — Latent training-data leakage | Model has seen Big-3 briefs in training and reproduces them from memory without web access | ❌ not eliminable; detectable post-hoc only |

### Controls (colocated with enforcement)

| Control | Layer | Where enforced |
|---|---|---|
| Rubric / comparator URLs not in any agent-readable file | 1 | Nextcloud Files ACL: `/agents/` vs `/founder/` — see [t4-mcp-investigation.md](t4-mcp-investigation.md) "Network and ACL policy" |
| System prompts never mention the comparator brief, "McKinsey / BCG / Bain", or the 8 rubric dimensions | 1, 2, Goodhart | [t5-system-prompts.md](t5-system-prompts.md) "Prompt sanitization rules" |
| Consulting-firm domain blocklist for the Researcher | 1, 2 | [t4-mcp-investigation.md](t4-mcp-investigation.md) "Network and ACL policy" |
| URL fetch log for every Researcher fetch | 1, 2 detection | [t5-researcher-urls.md](t5-researcher-urls.md) |
| Verbatim 7-gram match check post-spike | 1 detection | This file — "Post-spike checks" below |
| AI-panel "derivative check" — name a suspected source brief | 2, 3 | This file — "Panel-only checks" below |
| Reverse-grade against a non-Big-3 anchor | 2, 3 | This file — "Panel-only checks" below |

### Post-spike checks

Run these against [t8-sample-brief.md](t8-sample-brief.md) before any positive gate decision. Failure on any of them downgrades the gate by one tier (strong → weakly positive, weakly positive → negative).

**Verbatim match check (7-gram, against 5 anchor briefs):**

1. Extract plain-text of [t8-sample-brief.md](t8-sample-brief.md) and the 5 anchor PDFs (the BCG/McKinsey/Bain URLs above).
2. Generate all 7-word sequences from each.
3. Intersect sample-brief's 7-grams against each anchor's 7-grams.
4. Flag any non-trivial hit (excludes common phrases — e.g., "in the next five to ten years" is uninteresting; "the four success factors for entrants are" is a hit).
5. Threshold: **zero non-trivial hits** = pass. **≥ 1 non-trivial hit** = fail Layer 1; investigate.

Cheap implementation: a 20-line Python script with `nltk` or a shell pipeline (`tr`, `awk`, `sort`, `comm`). No external service needed.

**Researcher URL audit:**

Open [t5-researcher-urls.md](t5-researcher-urls.md). For each logged fetch, verify:

- Domain is not on the consulting-firm blocklist.
- Domain is not an archive/mirror of a blocklisted domain (`web.archive.org/.../bcg.com/...`, SlideShare hosting BCG decks, etc.).
- Fetched content snippet does not name a Big-3 firm as the source of cited statistics or structure.

If any fetch evaded the blocklist, the sample-brief is contaminated; reset and re-run with the blocklist hardened.

### Panel-only checks

Add these to the multi-AI opinion panel's review prompt (in addition to scoring the 8 dimensions):

> **Derivative check:** Does this brief read as derivative of any specific public consulting brief you can name? If yes, name the suspected source (firm + title + year if you can). If you suspect derivation but cannot name a source, say so. Be explicit about confidence.

> **Reverse-grade:** Score this brief against an *independent* rubric — the IDEO / d.school case-write-up format (problem framing → user research → solution alternatives → prototype → validation). If the brief scores well against both the Big-3 market-entry rubric AND a structurally different framework, that's evidence of genuine analysis, not template-matching. If it scores well against only the Big-3 rubric, that's a Goodhart signal.

The panel's derivative-check verdict and reverse-grade score are recorded in the AI-panel review file (created during T8; see [../design/07-refinements.md](../design/07-refinements.md) T1).

### What this does NOT eliminate

Layer 3 is real and unfixable from inside the spike. A motivated brief that reorganizes prose without verbatim copy can still be derivative of internalized training data. The honest gate is not "did the agents reason from first principles" (unprovable) but "does this look like work an analyst would trust." The contamination guard raises the floor; the AI-panel review + (later) practicing-analyst review raise the ceiling. The Codex T1 mitigation chain stands.

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
