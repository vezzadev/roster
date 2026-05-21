# Grading Rubric

Public-brief-anchored rubric used for self-grading the spike's [t8-sample-brief.md](t8-sample-brief.md) and as input to the multi-AI opinion panel.

Parent: [../design.md](../design.md) · Spec: [../design/06-validation.md](../design/06-validation.md) SC#5 · [../design/07-refinements.md](../design/07-refinements.md) D2

## Dimensions

Scoring scale: **1 (clearly worse than comparator) — 3 (rough parity with BCG Vietnam) — 5 (clearly better)**. Sub-3 on any single dimension is a fail signal for that dimension regardless of average.

Calibration choice: **"3 = parity" means what BCG Vietnam actually does, not an idealized market-entry brief.** Where BCG Vietnam itself falls short (no paired mitigations, no decision framework, no archetype-bifurcation, inconsistent forecast methodology, sector deep-dives without TAM-style sizing for the buyer's segment), those gaps are coded into the **"5"** tier — i.e., to score above the comparator the spike brief must do something the comparator skipped. See [Anchor](#anchor) for the structural mapping.

The spike target is country **+ sector** (US vertical-SaaS firm entering Indonesia logistics SMB), while BCG Vietnam is country-only. Dimensions 4, 5, and 7 push beyond what the comparator covers (target-segment TAM/SAM/SOM, named competitor positioning, entry-mode evaluation); dimensions 2, 3, 6, 8 map directly to BCG Vietnam sections; dimension 1 partly extends (BCG has an exec summary but no concrete enter / no-go recommendation).

| # | Dimension | Maps to BCG Vietnam | "3" (parity with BCG) | "5" (clearly better than BCG) | Sub-3 (fail) |
|---|-----------|---------------------|------------------------|--------------------------------|---------------|
| 1 | Executive summary + recommendation | "Executive Summary" (with its 4 success factors) | Exec summary present + concrete recommendation (enter / enter conditionally / do not enter) + 3-5 named success factors or focus areas | Recommendation conditioned on reader profile **+** phased 90-day plan **+** success factors traceable to specific evidence in the body (BCG Vietnam's 4 factors live only in the exec summary and are not picked up downstream — beating that is the bar) | No exec summary, OR recommendation is wishy-washy / "it depends" without stated conditions |
| 2 | Country snapshot + macro context | "Vietnam: At a Glance" + "Macroeconomic overview" | KPI dashboard (6-9 tiles: GDP, GDP/cap, FDI, inflation, population, EoDB or equivalent), data <18mo + macro indicators (GDP trajectory, FDI flows, trade flows, demographic/MAC shift) + at least one forecast with cited source | + peer-country benchmark (ASEAN-6 or named peers) + **named forecast methodology on every forecast** (e.g., "Oxford Economics 2024", "internal wealth-and-population model") — BCG Vietnam attributes methodology only on some charts | No quantified snapshot, OR macro figures without source/method, OR single-year only |
| 3 | Business environment | "Business environment" | Regulatory rank + trade agreements + workforce cost/availability + tax/incentives | + concrete incentive table (e.g., CIT % × exemption years by activity tier, BCG-Vietnam-style) **and** SaaS-relevant items called out (data residency / personal data law, FX repatriation, withholding tax on cross-border SaaS revenue, e-commerce / electronic transactions law) | Vague "favorable business climate" without specifics |
| 4 | Target market sizing + sub-segmentation | (extends BCG sector slides; BCG does big stat callouts, not TAM/SAM/SOM) | TAM/SAM/SOM for the target segment (Indonesian logistics SMB SaaS) with stated method + sub-segments named (e.g., 3PL vs freight forwarder; $1M vs $10M ARR tiers) | + sensitivity range on SOM + ICP profile and use-case per sub-segment + adoption-pattern hypothesis | Single number with no method, OR macro/sector-only sizing without a SOM for the actual buyer, OR no internal segmentation |
| 5 | Competitive landscape | (extends "Notable Startups" logos + Appendix Ecosystem maps; BCG does logo walls, not positioning) | Named competitors (local Indonesian + regional SEA + global) with positioning notes per player | + strategic groups / 2x2 (e.g., price × verticalization, or local-presence × product-depth) **or** moat analysis per named competitor (distribution, regulatory, customer lock-in) | Vague "competitors include…" or no named players |
| 6 | Risks + mitigations | "Risks & Challenges" (4 classes: political & economic / legal & regulatory / operational / environmental) | Risks categorized into 4-5 classes with **concrete named examples** per risk (BCG-Vietnam style — e.g., not just "concentration risk" but "Samsung = 26% of GDP") | + **mitigations paired with each risk** (BCG Vietnam does NOT do this — pairing is explicitly above the comparator) + risks ranked by likelihood × impact | Risks listed without examples, OR uncategorized risk soup |
| 7 | Entry mode evaluation | (BCG Vietnam only lists corporate structures in appendix; JV called out as popular via Honda example, but no go/no-go gate or phasing) | 2-3 entry modes evaluated with trade-offs (e.g., direct sales / reseller partnership / JV with local SI / acquisition / wait-and-watch) | + **recommended mode with reasoning + first-step actions** + bifurcation by reader profile or scenario (BCG Vietnam is uniform across reader archetypes — bifurcating beats it) | Single mode assumed, or modes listed without trade-offs |
| 8 | Citation discipline | Inline source lines per slide + References section (Reports / Other sources / Press releases) | Inline source per non-trivial claim + References section at end | + primary sources where possible (World Bank, IMF, Bank Indonesia, gov't statistics, named industry reports) **and** zero consulting-firm secondary citations — the contamination guard ([below](#contamination-guard)) requires the latter; sourcing claims from a BCG/McKinsey/Bain brief is a contamination signal even if technically a citation | Unsourced assertions, OR exclusively secondary citations, OR citations to consulting-firm content (auto-fails sub-3 via the contamination guard) |

Structural notes:

- **Section ordering is not its own dimension.** The 8 dimensions ARE the structure — a missing section gets sub-3 on the corresponding dimension, which is a more honest signal than a meta "structure" score.
- **BCG Vietnam's "4 success factors" device** (Exec Summary only) is folded into Dimension 1. Reusing that device verbatim is a contamination risk (see post-spike 7-gram check); using an equivalent device with different factor names is fine.
- **Appendices are not scored.** BCG Vietnam puts ecosystem maps, FTA list, and entry-condition tables in appendices; the spike brief may or may not include them. If present and useful, they raise specific dimensions (5, 3) toward "5"; if absent, the main body still has to carry the score.

## Anchor

The rubric is anchored to **publicly available Big-3 market-entry briefs**, not a founder-invented spec. Codex T1: a founder-invented rubric is a fake gate.

Honest framing: Big-3 firms rarely publish full client market-entry decks (those are confidential). The closest public analogues are firm-published thought-leadership pieces that follow market-entry structure. The set below has been verified accessible (PDFs hosted on the firms' own domains as of 2026-05).

**Primary comparator: BCG, "Vietnam: A Global Engine of Growth" (2023)**
- URL: https://web-assets.bcg.com/2c/b0/af4990ba41bf8be7e6301789a7be/vietnam-a-global-engine-of-growth.pdf
- Format: 62-page slide deck (joint with Golden Gate Ventures / GGVbrain), not a prose report. "Sections" are slide-banner prefixes.
- Why this one: Recent (2023), SEA geography-entry framing, full deck publicly hosted on BCG's own CDN. Closest to the canonical market-entry brief shape in the verified set.
- **Actual section order, verbatim** (used as rubric structure):
  1. Executive Summary — names "4 success factors for entrants" (this device appears only here; the back half is not organized around it).
  2. **Vietnam: At a Glance** — 9-tile KPI dashboard (GDP growth, GDP/cap, FDI inflows, interest rate, inflation, population, EoDB rank, literacy).
  3. **Macroeconomic overview** — GDP trajectory vs ASEAN-6, FDI hotspot, near-term growth forecast, 10-yr trade-flow change, manufacturing shift / China geopolitics, MAC (middle-and-affluent class) growth. Forecast methodology cited on the trade-flow map (BCG Trade Finance Model 2022) and MAC slide (BCG wealth & population model) — not consistently on all forecasts.
  4. **Business environment** — World Bank EoDB ranks across 10 topics, FTA map (15 active + 4 in negotiation), labour costs, expat-city ranking, APAC corporate-tax table, incentives matrix (High tech / Large scale / Social importance with CIT % × exemption years).
  5. **Investment opportunities** — 3-pillar framework (Digital / Green / Hi-tech) + sector deep-dives (HealthTech, FinTech, EdTech, Asset-light Logistics, Renewables). Each sector slide: big stat callouts + drivers bullets + "Notable Startups" logo wall. Funding-history charts on FinTech and EdTech.
  6. **Risks & Challenges** — 4 classes: Political & economic, Legal & regulatory, Operational, Environmental. Each risk has named concrete examples (Samsung 26%-of-GDP dependence; EVN monopoly; 36 clean-electricity investor petition; Lloyd's-cited climate exposure). **Risks are NOT paired with mitigations.**
  7. **Exits** — IPO market overview, ~5-yr unicorn-to-IPO comparison, Vietnam M&A. Prose on body slide; data in appendix.
  8. Appendices — Business Environment detail, Ecosystem maps, Exits, Vietnam FTAs, Vietnam Market Entry Condition list (prohibition list + conditioned list with foreign-ownership ratios).
  9. References — Reports / Other sources / Press releases.
- **Gaps in BCG Vietnam that the rubric codes as "5" tier** (i.e., to beat the comparator the spike brief must do these):
  - Mitigations paired with risks.
  - Explicit decision framework / go-no-go / phased entry plan.
  - Bifurcation by reader archetype (first-mover vs follower; global vs regional; etc.).
  - Forecast methodology cited consistently on every forecast.
  - Success-factor framework that recurs in the body (BCG's 4 factors live only in the exec summary).

**Secondary comparator: McKinsey Quarterly, "Beating the Odds in Market Entry" (Horn, Lovallo, Viguerie, 2005)**
- URL: https://www.mckinsey.com/~/media/McKinsey/Business%20Functions/Strategy%20and%20Corporate%20Finance/Our%20Insights/Beating%20the%20odds%20in%20market%20entry/Beating%20the%20odds%20in%20market%20entry.pdf
- Why this one: Meta-rubric source. Names the 6 predictors (scale, relatedness, complementary assets, order of entry, life-cycle stage, tech innovation) and 5 inside-view dimensions (value prop, market size, competition, share/revenue, costs) that practicing analysts actually use. Use this when scoring rubric dimensions 2-7 for "is this how a Big-3 analyst would frame it?"

**Additional references (for AI-panel and structure cross-checks):**

- BCG, "Foreign E-Tailers Are Here! Is South African E-Commerce Ready?" (Nov 2024) — https://web-assets.bcg.com/b5/b4/333e56944145a10f0d57408b8067/foreign-e-tailers-are-here-is-south-african-e-commerce-ready-3.pdf — inverse angle (defense vs entry).
- Bain, "Are You Ahead of the Curve in Emerging Markets?" (~2012) — https://media.bain.com/Images/INDUSTRY_BRIEF_Ahead_of_curve_in_emerging_markets.pdf — bifurcated tracks (enter-vs-defend) pattern.
- BCG, "Changing Your Orbit" India (Jun 2014) — https://web-assets.bcg.com/img-src/Changing-Your-Orbit-Jun-2014-India_tcm9-28793.pdf — explicit 3-step entry framework.

**Structural pattern across the set, with honest variance noted:** all five cover context/sizing → market participants → some form of decision framework or success-factor list → recommendation. Bifurcation by reader archetype (enter-vs-defend, aggressive-vs-cautious) is present in the Bain emerging-markets brief and the BCG South Africa e-tail brief, but **not in the BCG Vietnam primary comparator**. The 8 rubric dimensions above map onto the BCG Vietnam structure specifically (the primary comparator), with bifurcation coded as a "5" tier upgrade on Dimension 7 rather than a parity requirement, because requiring it would set the bar above the primary comparator.

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

Per Honesty guard #2: every score ≥ 3 must name a specific quote from [t8-sample-brief.md](t8-sample-brief.md). No score without evidence.

| # | Dimension | Score | Evidence quote (required for score ≥ 3) |
|---|-----------|-------|------------------------------------------|
| 1 | Exec summary + recommendation | _–_ | |
| 2 | Country snapshot + macro context | _–_ | |
| 3 | Business environment | _–_ | |
| 4 | Target market sizing + sub-segmentation | _–_ | |
| 5 | Competitive landscape | _–_ | |
| 6 | Risks + mitigations | _–_ | |
| 7 | Entry mode evaluation | _–_ | |
| 8 | Citation discipline | _–_ | |
| | **Average / verdict** | _–_ | |

## Gate decision

| Outcome | Trigger | Next step |
|---------|---------|-----------|
| Strong positive | Self-grade ≥ 4 avg AND AI panel ≥ 4 avg with no sub-3 dimensions | Recruit paid analyst (Week 2, first 3 days) |
| Weakly positive | Self-grade 3-4 OR AI panel split | Discuss with one ICP contact first; analyst recruit only if signal holds |
| Negative | Self-grade < 3 OR AI panel < 3 OR any sub-3 dimension that matters for the comparator | Apply [fallback bullets](#) — pivot or stop, do NOT proceed to Week 2 |
