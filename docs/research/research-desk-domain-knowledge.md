# Research Desk Domain Knowledge — Reference for Roster v1

**Purpose.** Domain reference for Roster v1's `research-desk` template work.
Informs (a) which agent skills/MCPs to plug into each role, (b) the long-term
memory progression an agent should accumulate to "level up" from junior
analyst to knowledge expert, and (c) validation/benchmarking targets.

**Source.** Pedro × Claude side-chat, 2026-05-19, four Q&As. Original transcript:
https://claude.ai/share/4406d240-2cc9-4465-a135-bdbc3572c5e7

Reorganized below by use case for Roster, not preserved verbatim. Quote
attribution is to Claude's responses in that chat.

---

## 1. How a research desk operates (informs role behavior + handoffs)

**Org shape:** hub-and-spoke. MBB and Big Four run centralized research
centers in lower-cost locations (McKinsey Knowledge Centers in Gurgaon /
Waltham / Wrocław, BCG Knowledge & Insight, Bain Knowledge & Information,
Deloitte Insight). Thousands of people globally per firm. On top, researchers
embedded in practice areas (industries: healthcare, FS, energy; functions:
ops, M&A, marketing) for domain depth.

**Operating model: request-based.** A consultant submits a request via an
internal ticketing system describing question, deliverable, deadline, context.
Requests triaged by a manager and assigned based on topic + turnaround.

**Service levels (typical):**
- 2-hour quick-turn for a single data point
- 24 hours for a standard company profile
- 3–5 days for an in-depth market scan or benchmark
- "Follow-the-sun" common: NY consultant briefs at EOD → analyst in India
  works overnight → deliverable in inbox by morning.

**Roster v1 implication:** the `#team` Talk room is the ticketing channel.
The Engagement Manager triages and assigns. SLA-shaped behavior should be
in the EM's system prompt (quick-turn vs. standard vs. deep). Per-pair DM
rooms map to the manager-assigning-to-analyst pattern.

**Work taxonomy (what gets requested):**
- Secondary research from premium databases
- Company profiles + market profiles
- Competitive landscapes
- Market sizing (top-down + bottom-up, triangulated)
- Benchmarking
- Chart-building
- Literature reviews
- Primary research support (survey design, expert-call setup)

**Senior researcher role (Roster maps this to the EM):** join calls, shape
hypotheses, own proprietary knowledge assets (benchmarks, deal databases,
methodology repositories) that get reused across engagements.

**Economics:** research time is overhead or partially absorbed, rarely
billed directly. Utilization, request volume, and reusability of outputs
are the measured metrics. *Roster note: agent cost/interaction ≈ "billable"
analog; design templates so outputs are reusable across briefs.*

---

## 2. AI skill / plugin landscape (informs per-role skill selection)

Grouped by where each slots into a desk workflow.

### Claude Skills (closest to Roster's role-skill model)

| Skill | Where it fits | Source |
|---|---|---|
| `market-research` | Competitive analysis, investor DD, industry intelligence with cited sources, market sizing, fund research | `affaan-m/everything-claude-code` — install: `npx skills add https://github.com/affaan-m/everything-claude-code --skill market-research` |
| Market Analysis (McKinsey frameworks) | TAM/SAM/SOM sizing, competitive landscape, MECE structuring | mcpmarket.com |
| Market Researcher Agent | Deploys 4 specialists (Trend Analyst, Consumer Researcher, Industry Analyst, Opportunity Finder) | mcpmarket.com |
| `awesome-claude-code-subagents` | Subagents for top-down + bottom-up TAM reconciliation, competitor mapping from G2/Capterra/job postings | VoltAgent |
| `awesome-claude-code-toolkit` | 135 agents, 35 skills, 42 commands, 176+ plugins — closest to "desk in a box" | rohitg00 |

**Roster role mapping (initial guess, to validate Week 1):**
- **Engagement Manager:** `market-research` + McKinsey frameworks skill (synthesis, MECE, storyline)
- **Senior Analyst:** `market-research` + sector-specific subagents (TAM, competitor mapping)
- **Researcher:** focused on retrieval — primarily MCPs (see below), light on Claude Skills

### Anthropic-native research workflows

- **Claude Cowork** — desktop workspace for long-running research. Built-in "Size a market" use case builds a plan in sidebar, cross-checks bottom-up against analyst reports, returns deck + model + sourced docs.
- **Claude Deep Research** (claude.ai setting) — multi-step research with plan + citations.

### Premium platform every consulting desk actually uses

**AlphaSense** — 95% of top consultancies, 88% of S&P 100. AI stack maps
1:1 onto research-desk tasks:

| AlphaSense product | Maps to |
|---|---|
| Workflow Agents (Channel Checks, Earnings Analysis, Company Primers) | EM pre-built brief templates |
| Custom Agents | User-defined scheduled briefs |
| Deep Research | Cross-source synthesis (Researcher role) |
| AI-Led Expert Calls | Primary research (out of v1 scope) |
| Generative Grid | Side-by-side document analysis (Analyst role) |

Stack underneath: Anthropic on AWS Bedrock for reasoning, Gemini for
long-context, Llama via Cerebras for high-volume inference. *Roster v1 is
Claude-only; multi-model is a v2 question.*

### Adjacent agentic platforms (worth knowing, not v1 deps)

| Platform | Niche |
|---|---|
| Perplexity (Deep Research / Spaces) | Open-web research with verifiable citations |
| ChatGPT / Gemini Deep Research | General-purpose, open-web |
| Elicit, Consensus | Academic / scientific lit review |
| GWI Agent Spark | Survey-grounded answers (1.4M+ annual surveys) |
| Julius AI | Data analyst — survey exports, CRM, Python/R/SQL fallback |
| Relevance AI | Marketplace of consulting-style agents (industry analysis, SWOT, TAM, personas) |
| MindStudio, Ema, Cognosys | Compose your own from blocks |

### MCP servers worth connecting

Pattern most large firms use: Claude (or in-house) agent + MCP to:

- **Firecrawl / Browserbase** — web scraping, browser automation *(already in your stack)*
- **PitchBook, Capital IQ, FactSet** — increasingly exposing MCP/agent APIs; otherwise screen-scrape via Browserbase with logged-in session
- **SharePoint / Confluence / Notion** — surfacing past deliverables + benchmarks (internal KM)
- **GLG, AlphaSights, Third Bridge** — enterprise API access for expert networks; some now expose programmatic transcript search

**Roster v1 implication:** Talk + Files MCP is enough for v1 demo. Firecrawl
MCP is the first external-data MCP to add post-validation (covers most
secondary research needs at low cost). AlphaSense/Bloomberg/Capital IQ
require enterprise licenses — defer to v1.x or "bring your own."

### Big-firm internal tools (reference, not buyable)

| Tool | What it is |
|---|---|
| McKinsey Lilli | Internal GenAI grounded in 100K+ McKinsey docs + 70 yrs of intellectual capital. High firm adoption. |
| BCG GPT tools | Partnership with OpenAI/Anthropic for proprietary assistants |
| Bain × OpenAI / Anthropic | Internal research agents |
| Cornerstone Research (econ consulting) | Agentic research platform for quant analysis, doc review, opposing-expert rebuttal. All outputs replicated by a professional before litigation use. |
| Harvey (legal) | >50% of Am Law 100 firms; power users save ~37 hours/month. Closest analog to "consulting desk in a box." |

### "Desk in a box" working combination today

> Claude Code/Cowork + market-research and market-analysis Skills +
> Firecrawl + Browserbase MCP for retrieval + Perplexity or AlphaSense API
> for premium sources + Excel/PowerPoint MCP for deliverables.
> awesome-claude-code-toolkit is the closest turnkey package.

**This is essentially what Roster's research-desk template is rebuilding** —
but provisioned as a team with persistent identities, takeover, and the
Letta runtime instead of a single Claude Code instance.

---

## 3. AlphaSense decomposed (informs "desk-as-a-service" mental model)

AlphaSense is three layers, useful as a model for what Roster's product
absorbs vs. leaves to humans:

**Layer 1 — Data source.** Owns content unavailable elsewhere. Tegus
acquisition (2024, ~$930M) → hundreds of thousands of expert call
transcripts. AI-Led Expert Calls generate new primary content with built-in
compliance. *Roster has no equivalent in v1; the agent uses publicly
scraped + user-provided content.*

**Layer 2 — Aggregator of premium sources.** Sell-side research (Goldman,
MS, JPM), earnings transcripts, SEC filings, trade press, news — 500M+
premium docs across public + private markets + firm-proprietary data.
Qualitative-heavy, search-native across long-form documents. Used
alongside Capital IQ / Bloomberg / PitchBook, not instead of them.
*Roster has no aggregation layer in v1; relies on MCP-driven retrieval.*

**Layer 3 — Research desk as a service (direction of travel).** Workflow
Agents generate deep research reports, pitch decks, memos, tables, slides
with one click. Deep Research performs dozens of searches across thousands
of results. Single-prompt-to-pitch-ready-deck workflow that used to take
2–3 days. **This is the layer Roster competes in.**

**What AlphaSense does NOT replace** (and Roster shouldn't try to in v1):
- Bespoke synthesis aligned to a case team's hypothesis and storyline
- Curation of the firm's proprietary knowledge assets (benchmarks, deal DBs, methodology repos)
- Primary research that the expert library doesn't cover (niche functional/geographic experts via live GLG/AlphaSights/Third Bridge calls)
- Source diversification beyond the licensed set (IQVIA for pharma, CoStar for real estate, IBISWorld for SMB sectors)
- Client-confidential where data can't leave the firm's environment

> "AlphaSense is the aggregator-plus-proprietary-content layer with an
> increasingly capable agent layer on top that absorbs the templated/
> repeatable parts of desk work (company primers, industry primers, M&A
> target lists, earnings-prep packs, channel checks). The desk function
> above that — case-specific synthesis, knowledge asset curation, custom
> primary research, integration into deliverables — still sits with human
> researchers, just with their hours reallocated toward the higher-judgment
> slices."

**Roster v1 positioning implication:** Roster's research desk competes
specifically with the Layer 3 "templated/repeatable parts of desk work."
The pitch should NOT claim to replace case-specific synthesis or
proprietary knowledge curation. The buyer is a human analyst/consultant
whose hours get reallocated upward — exactly the Cursor pattern named in
the design delta's "buyer paradox."

---

## 4. Researcher learning paths (informs agent long-term memory + benchmarks)

This section is the highest-value reference for **agent memory validation
and benchmarking**. The progression below is what a human junior researcher
accumulates; mirror it as the long-term-memory growth target for a Roster
analyst agent over time.

### Entry pathways (human)
- Campus recruiting → offshore knowledge centers (Gurgaon, Manila, Wrocław, San José)
- Undergrad in business, econ, finance, engineering, liberal arts — broad recruiting because skills are taught in-house
- Specialized practices:
  - Pharma/life sciences → PhD/MD heavy
  - Healthcare analytics → biostats / epi
  - Quant FS → finance, stats, CS
- Lateral entry: sell-side equity research, IB analyst programs, in-house competitive intelligence, specialist firms (Frost & Sullivan, Euromonitor, Gartner) — slot in at senior analyst or manager
- Smaller pipeline: MLIS (library/info science) for KM-oriented senior roles owning knowledge curation

### Hard skills (the explicit curriculum)

| Skill | Roster relevance |
|---|---|
| Database fluency (Capital IQ, Bloomberg, Refinitiv/Eikon, Factiva, PitchBook, Euromonitor, IBISWorld; sector: IQVIA, CoStar) | **Knowing which DB to use for what is half the job.** Map to MCP selection: agent should learn "for company financials → Capital IQ MCP; for industry sizing → IBISWorld; etc." |
| Bloomberg BMC + S&P Capital IQ certs in first few months | **Agent equivalent:** completing a per-MCP "fluency benchmark" — N successful queries with correct schema usage |
| Excel — pivot tables, lookups, financial functions, MBB color-coding (inputs vs formulas) | Out of v1 scope; Excel MCP is a v1.x add |
| PowerPoint — chart-building, MECE slides, "ghost deck" thinking | Out of v1 scope; PowerPoint MCP is a v1.x add |
| Financial statement analysis + market sizing (top-down vs bottom-up, triangulation, sanity-checking) | **Critical for analyst-agent skill design.** Add as a baseline `market-sizing` skill |
| SQL + Python/R for data-heavy practices | Defer; Letta has Python tool execution available |
| Prompting + AI tool literacy (AlphaSense, Perplexity, Claude/ChatGPT, firm copilots) — **and validating outputs** | Recursive: Roster agents using Roster-style validation |

### Soft skills (harder but more important long-term)

- Translating a vague consultant request into a researchable scope
- Distinguishing signal from noise in a 200-page document
- Source triangulation
- Writing briefs that don't require follow-up
- Managing 5+ requests simultaneously under tight SLAs

**Roster memory implication:** these are the patterns to validate in an
agent's long-term memory. After N briefs, an EM agent should accumulate
heuristics like "when X type of brief comes in, scope it as Y questions"
and "source A is biased toward Z view, triangulate with B." This is the
"levels up" signal.

### Firm training structure (what an agent should simulate)

1. **2–6 weeks formal onboarding** — database training, methodology, firm
   frameworks, soft skills, deliverable templates
   *Agent analog:* a `roster up` initialization phase loads template-specific
   priors into Letta core memory.
2. **3–6 months apprenticeship** — paired with senior researcher who reviews
   work line-by-line before it goes to consultant
   *Agent analog:* EM-reviews-analyst-draft loop in `#team` Talk room.
   Validation: % of analyst drafts EM revises before approving (declining
   over time = learning).
3. **Industry/sector specialization at 12–18 months** — align to a practice
   (healthcare, FS, energy, TMT, ops, M&A) and build depth
   *Agent analog:* per-template specialization. A research-desk instance
   bound to "HR-tech" briefs builds different memory than one bound to
   "fintech."

### Frameworks and methodology references (worth grounding agents on)

- Porter's five forces — still used
- Growth-share matrix — still used
- Value chain analysis — still used
- Damodaran's valuation materials (free on NYU site) — most cited
  resource for valuation methodology
- Greenwald, "Competition Demystified" — strategy frameworks
- Goldman / Morgan Stanley initiation reports — best way to learn what
  good output looks like
- 10-Ks of large complex companies — primary-source literacy
- McKinsey Insights, BCG Henderson Institute, Bain Insights — how firms
  structure thinking

### External certifications (signal for what to benchmark agents against)

| Cert | What it measures |
|---|---|
| CFA | Fundamental research skills (finance) |
| SCIP | Competitive intelligence professional |
| Bloomberg Market Concepts | Entry-level Bloomberg |

### What's changing right now (the AI-era shift)

> "The bottom rung is being automated. Pulling a company profile, drafting
> a competitor landscape, summarizing an earnings call, building a basic
> market sizing — AI tools do these in minutes. So the skill that's
> appreciating is _judgment over AI output_ — knowing when a Deep Research
> result is missing a key source, when a TAM number is structurally wrong,
> when an AI-generated competitor map has the wrong segmentation. Firms
> are increasingly hiring with this in mind: less 'can you pull data' and
> more 'can you decide what's wrong with the data the AI pulled.'"

**This is the validation/benchmarking frontier for Roster.** A research-desk
agent's value isn't in pulling — it's in catching AI errors. v1.x success
criteria should test: given a brief with a deliberately wrong premise or a
missing key source, does the EM/analyst flag it before the brief ships?

---

## Quick lookup index (for Roster v1 work)

| Need | Section |
|---|---|
| What does an Engagement Manager do? | §1 (Senior researcher role) |
| Which Claude Skill should I plug into the EM? | §2 (Claude Skills table) |
| Which MCPs does the analyst need? | §2 (MCP servers) |
| What's the v1 demo NOT trying to do? | §3 ("What AlphaSense does NOT replace") |
| What should an agent's long-term memory accumulate? | §4 (Hard skills, Soft skills) |
| How do I validate the agent is "learning"? | §4 (Firm training structure — EM-review-revision rate) |
| What's the v1.x benchmarking target? | §4 ("What's changing right now") |
