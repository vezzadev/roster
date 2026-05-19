# Research Desk Source Transcript

Verbatim transcript of the Pedro × Claude side-chat on 2026-05-19 that
sourced [`research-desk-domain-knowledge.md`](research-desk-domain-knowledge.md).
Vendored here so the reference doc has a durable, in-repo source instead
of relying on an external Claude share URL.

**Original share URL (may expire):** `https://claude.ai/share/4406d240-2cc9-4465-a135-bdbc3572c5e7`

---

## Q1 — how do research desks work in consulting companies

*Pedro, 11:53 AM*

> how do research desks work in consulting companies

**Claude:**

Research desks (also called knowledge services, knowledge & insights,
research & analytics) are dedicated internal teams that support case
teams with secondary research, data gathering, and analysis. They exist
because partners and consultants are expensive billable resources whose
time is better spent on synthesis and client interaction than on pulling
company filings or building competitor longlists.

Most large firms run a hub-and-spoke model. MBB (McKinsey, BCG, Bain)
and the Big Four all operate large centralized research centers,
typically in lower-cost locations — McKinsey has Knowledge Centers in
places like Gurgaon, Waltham, and Wrocław; BCG has its Knowledge &
Insight team and Knowledge Specialists organization; Bain has Knowledge
& Information; Deloitte has its Insight team. These can run into the
thousands of people globally. On top of the central pool, firms often
have researchers embedded in practice areas (industries like healthcare,
FS, energy; functions like ops, M&A, marketing) for deeper domain
specialization.

The day-to-day operating model is request-based. A consultant submits a
request via an internal ticketing system describing the question,
deliverable, deadline, and any context. Requests are triaged by a
manager and assigned based on topic and turnaround. Most desks publish
service levels — something like a 2-hour quick-turn for a single data
point, 24 hours for a standard company profile, and 3–5 days for an
in-depth market scan or benchmark. "Follow the sun" workflows across
time zones are common: a New York consultant briefs the desk at end of
day, an analyst in India or the Philippines works overnight, and the
deliverable lands in their inbox by morning.

The actual work spans secondary research (pulling from Capital IQ,
Bloomberg, Refinitiv, Factiva, Euromonitor, IBISWorld, PitchBook, plus
industry-specific sources like IQVIA for pharma or CoStar for real
estate), company and market profiles, competitive landscapes, market
sizing, benchmarking, chart-building, literature reviews, and primary
research support like survey design and expert-call setup through
networks like GLG, AlphaSights, and Third Bridge. Senior researchers —
often called knowledge experts, practice experts, or specialists —
operate closer to consultants: they join calls, shape hypotheses, and
own proprietary knowledge assets (benchmarks, deal databases,
methodology repositories) that the firm reuses across engagements.

Economically, research time is usually overhead or partially absorbed
rather than directly billed, which is why utilization, request volume,
and reusability of outputs matter a lot to how these groups are
measured. The career track is its own ladder — analyst, senior analyst,
manager, expert — though crossover into consulting happens.

The biggest current shift is GenAI. Firms have rolled out internal LLM
tools (McKinsey's Lilli, BCG's tooling on top of frontier models, Bain's
partnership with OpenAI) that handle the long tail of "find me three
comparable transactions" or "summarize this 10-K." That's pushed
research desks toward higher-value work: synthesis, judgment calls,
validating AI output, and curating the proprietary data the LLMs are
grounded on.

---

## Q2 — find ai agent skills / plugins that assist this work

*Pedro, 11:58 AM*

> find ai agent skills / plugins that assist this work

**Claude:**

Here's the landscape of AI skills, plugins, and agents that map directly
to research-desk work, grouped by where they slot in.

### Claude Skills (drop-in for Claude Code / Claude Desktop)

These are the literal "skills" — markdown-defined capabilities you can
install:

- **market-research** (affaan-m/everything-claude-code) — competitive
  analysis, investor due diligence, and industry intelligence with cited
  sources and decision-oriented summaries; covers market sizing,
  competitor comparisons, fund research, and tech scans. Install via
  `npx skills add https://github.com/affaan-m/everything-claude-code --skill market-research`.
  It explicitly enforces source attribution and contrarian-view
  inclusion to avoid "research theater."
- **Market Analysis (McKinsey frameworks)** on mcpmarket.com — runs
  market research and competitive analysis using McKinsey-style
  frameworks inside Claude Code.
- **Market Research skill** (mcpmarket) — structured methodology for
  TAM/SAM/SOM sizing, competitive landscape mapping, demographic
  profiling, and risk assessment in Markdown reports.
- **Market Researcher Agent** — deploys four specialist subagents (Trend
  Analyst, Consumer Researcher, Industry Analyst, Opportunity Finder)
  for a 360° view of an industry.
- **awesome-claude-code-subagents** (VoltAgent) and
  **awesome-claude-code-toolkit** (rohitg00) — open-source repos with
  market-researcher subagents that explicitly do top-down + bottom-up
  TAM reconciliation, competitor mapping from G2/Capterra/pricing/job
  postings, and segment identification from survey, support-ticket, and
  review data. The rohitg00 toolkit alone bundles 135 agents, 35 skills,
  42 commands, and 176+ plugins.

### Anthropic-native research workflows

- **Claude Cowork** — Anthropic's desktop workspace for long-running
  research. The "Size a market" use case handles the full research and
  formatting loop, builds a visible plan in the sidebar covering
  segments/geographies/frameworks, cross-checks bottom-up against
  analyst reports, and returns a deck, model, and sourced documentation.
- **Claude's Deep Research** in claude.ai (toggle in settings) —
  multi-step research with a research plan and citations, equivalent to
  ChatGPT/Gemini's deep research modes.

### The platform every consulting research desk actually uses

**AlphaSense** is the dominant tool here — used by 95% of the top
consultancies and 88% of S&P 100 companies. Their AI stack maps almost
1:1 onto research-desk tasks:

- **Workflow Agents** — one-click end-to-end workflows that generate
  deep research reports, pitch decks, memos, tables, and slides,
  integrating broker research, expert call transcripts, filings, news,
  and your internal documents. Pre-built ones include Channel Checks,
  Earnings Analysis, and Company Primers.
- **Custom Agents** — user-built, schedulable workflows in natural
  language for competitive intelligence, earnings analyses, and
  investment screening.
- **Deep Research** — performs dozens of searches across 500M+ premium
  documents (public + private markets + your firm's proprietary data),
  parses thousands of results, and produces comprehensive analysis
  sourced from content that's not on the open web (sell-side research,
  expert call libraries via Tegus).
- **AI-Led Expert Calls** — AI conducts and transcribes primary research
  interviews with built-in compliance safeguards, drawing on the Tegus
  expert library.
- **Generative Grid** — side-by-side document analysis (great for
  comparing 20 10-Ks at once).

Architecturally they're running a multi-model stack — Anthropic via AWS
Bedrock for reasoning/agentic work, Gemini for long-context, and Llama
via Cerebras for high-volume inference.

### Adjacent agentic research platforms

- **Perplexity** (Deep Research / Spaces) — outputs citations you can
  verify, marketed as a dedicated research analyst for teams who need
  trusted sources.
- **ChatGPT Deep Research** and **Gemini Deep Research** —
  general-purpose deep research, useful when content sits on the open
  web.
- **Elicit** and **Consensus** — for academic/scientific literature
  reviews (clinical, regulatory, scientific consulting).
- **GWI Agent Spark** — grounds answers in 1.4M+ annual surveys across
  50+ markets, useful when you need exact percentages by segment rather
  than generic figures.
- **Julius AI** — AI data analyst for survey exports, CRM snapshots,
  performance data, and product metrics, with Python/R/SQL fallback and
  Slack/email delivery.
- **Relevance AI** — has a marketplace of pre-built consulting-style
  agents: industry analysis, competitor profiling, TAM/SAM/SOM with
  Python calculations, SWOT, trend tracking, persona development — each
  chains search + code + analysis steps.
- **MindStudio**, **Ema**, **Cognosys** — let you compose your own
  research agents from building blocks.

### MCP servers worth connecting to a research-desk agent

The pattern most large firms use is a Claude (or in-house) agent with
MCP connections to:

- **Firecrawl / Browserbase** — web scraping and browser automation
  (what you're already running).
- **PitchBook, Capital IQ, FactSet** — increasingly exposing MCP/agent
  APIs; otherwise screen-scrape via Browserbase with a logged-in
  session.
- **Internal KM systems** (SharePoint, Confluence, Notion) — for
  surfacing past deliverables and benchmarks.
- **Expert networks** — GLG, AlphaSights, and Third Bridge all have API
  access for enterprise customers; some now expose programmatic
  transcript search.

### What the big consulting firms actually run internally

For reference, since these aren't external products:

- **McKinsey Lilli** — internal GenAI assistant grounded in 100K+
  McKinsey documents and 70+ years of intellectual capital. Reported
  high adoption across the firm.
- **BCG's GPT tools** + partnership with OpenAI/Anthropic for
  proprietary assistants.
- **Bain × OpenAI / Bain × Anthropic** partnerships powering internal
  research agents.
- **Cornerstone Research** (econ consulting) — deploys an agentic
  research platform across case work for quantitative analysis, document
  review, and opposing-expert rebuttal, with all outputs replicated by a
  professional before litigation use.
- **Harvey** (legal-adjacent) — now used by over 50% of Am Law 100
  firms; power users save nearly 37 hours/month; relevant model for what
  a consulting equivalent looks like.

### Practical stack for replicating a research desk yourself

If you're trying to assemble a desk-in-a-box rather than buy AlphaSense,
the working combination today is roughly: Claude Code/Cowork with the
market-research and market-analysis Skills + Firecrawl + Browserbase MCP
for retrieval + a Perplexity or AlphaSense API for premium sources + an
Excel/PowerPoint MCP for deliverables. The awesome-claude-code-toolkit
repo is the closest thing to a turnkey package.

---

## Q3 — how does AlphaSense fit in

*Pedro, 12:07 PM*

> [quoting the secondary-research paragraph from Q1] how does alphasense
> fit into this ? is it another data source or an aggregator of premium
> sources or a whole research desk as a service

**Claude:**

It's all three, layered — and the center of gravity has shifted over
time. Here's how I'd decompose it against your three buckets:

**As a data source.** AlphaSense owns content you can't get anywhere
else. The big one is the Tegus expert call transcript library —
AlphaSense bought Tegus in 2024 for ~$930M specifically to own that
asset. Tegus has hundreds of thousands of recorded calls with operators,
customers, and former executives across industries; for a consulting
researcher, that's competitive with (and sometimes a substitute for)
commissioning a fresh GLG/AlphaSights call. On top of that, their newer
AI-Led Expert Calls let the platform itself conduct and transcribe
primary research interviews with built-in compliance safeguards — so
AlphaSense is now generating new primary content, not just hosting it.

**As an aggregator of premium sources.** This is the original DNA. They
license and unify sell-side research (Goldman, Morgan Stanley, JPM,
etc.), earnings call transcripts, SEC and global filings, trade press,
news, and increasingly industry-specific journals — 500M+ premium
documents across public and private markets, alongside your firm's own
proprietary data. The pitch versus Factiva or a Bloomberg terminal is
that those are quantitative-heavy or news-heavy; AlphaSense is
qualitative-heavy and search-native across long-form documents. Most
consulting research desks use AlphaSense alongside Capital IQ /
Bloomberg / PitchBook, not instead of them — AlphaSense for "what are
people saying about this company/market" and the terminals for
financials, ownership, and structured screening.

**As a research desk as a service.** This is the direction of travel
and where the agentic features come in. Workflow Agents now generate
deep research reports, pitch decks, memos, tables, and slides with one
click, integrating external premium content with your internal
documents. Deep Research performs dozens of searches, parses thousands
of results, and produces analyst-level synthesis. Combine those with
Custom Agents and AI-Led Expert Calls and you can plausibly run a
single-prompt-to-pitch-ready-deck workflow that used to take a research
analyst 2–3 days.

**What it does NOT replace in a consulting research desk.** Worth being
precise here, because the "research desk as a service" framing
oversells it:

- Bespoke synthesis aligned to a specific case team's hypothesis and
  storyline — AlphaSense gives you raw and semi-cooked outputs, not a
  finished MECE answer.
- Curation of the firm's proprietary knowledge assets (benchmarks, deal
  databases, methodology repos) — that's internal and lives in the
  firm's KM systems.
- Primary research that AlphaSense's expert library doesn't cover —
  niche functional or geographic experts still come from
  GLG/AlphaSights/Third Bridge live calls.
- Source diversification beyond their licensed set — industry-specific
  verticals (IQVIA for pharma claims, CoStar for real estate, IBISWorld
  for SMB sectors) still sit outside.
- Anything client-confidential where the data can't leave the firm's
  environment.

So the cleanest one-liner: **AlphaSense is the
aggregator-plus-proprietary-content layer, with an increasingly capable
agent layer on top that absorbs the templated/repeatable parts of desk
work** (company primers, industry primers, M&A target lists,
earnings-prep packs, channel checks). The desk function above that —
case-specific synthesis, knowledge asset curation, custom primary
research, integration into deliverables — still sits with human
researchers, just with their hours reallocated toward the
higher-judgment slices.

---

## Q4 — how do people learn to become researchers, analysts

*Pedro, 12:11 PM*

> how do people learn to become researchers, analysts

**Claude:**

There's no single track — research and analyst roles in consulting are
entered through several pipelines and the learning happens mostly on
the job. Here's how it actually works.

**Entry pathways.** The most common route is campus recruiting straight
into a research analyst role, typically at one of the offshore knowledge
centers (Gurgaon, Manila, Wrocław, San José). Undergraduate degrees in
business, economics, finance, engineering, or liberal arts all work —
firms recruit broadly because the actual skills are taught in-house.
For specialized practices the credentials get more specific: pharma/life
sciences research desks lean heavily on PhDs and MDs, healthcare
analytics teams want biostats or epi backgrounds, and
quantitative-heavy financial services roles favor finance, stats, or CS
degrees. Lateral entry is also common — people coming from sell-side
equity research, investment banking analyst programs, in-house
competitive intelligence teams, or specialist research firms (Frost &
Sullivan, Euromonitor, Gartner) often slot in at the senior analyst or
manager level. A smaller pipeline is library/information science (MLIS)
backgrounds, especially for the more KM-oriented senior roles that own
knowledge curation rather than fresh research.

**What you actually need to learn.** The hard skills break down into:

- *Database fluency* — Capital IQ, Bloomberg, Refinitiv/Eikon, Factiva,
  PitchBook, Euromonitor, IBISWorld. Knowing which to use for what is
  half the job. Most firms require their analysts to certify on
  Bloomberg (BMC) and S&P Capital IQ in the first few months.
- *Excel* — pivot tables, lookups, financial functions, building clean
  models with proper formatting conventions. The MBB-style spreadsheet
  hygiene (color-coded inputs vs formulas, structured layouts) is its
  own dialect.
- *PowerPoint* — chart-building, MECE slide structuring, "ghost deck"
  thinking. Sounds trivial; isn't.
- *Financial statement analysis and market sizing* — top-down vs
  bottom-up methodology, triangulation, sanity-checking.
- *SQL and increasingly Python/R* — especially for analyst roles
  attached to data-heavy practices.
- *Prompting and AI tool literacy* — now table-stakes; firms expect new
  hires to know how to drive AlphaSense, Perplexity, Claude/ChatGPT, and
  the firm's internal copilots, and more importantly to validate their
  outputs.

The soft skills are harder but more important long-term: translating a
vague consultant request into a researchable scope, distinguishing
signal from noise in a 200-page document, source triangulation, writing
briefs that don't require follow-up, and managing 5+ requests
simultaneously under tight SLAs.

**How firms actually train people.** The structure is roughly: 2–6
weeks of formal onboarding (database training, methodology, firm
frameworks, soft skills, deliverable templates), then an apprenticeship
model where you're paired with a senior researcher for 3–6 months who
reviews your work line-by-line before it goes to a consultant. Most
firms run regular internal trainings on industry verticals, new tools,
frameworks (Porter's five forces, growth-share, value chain analysis —
yes, still). McKinsey's Knowledge Center onboarding, BCG's KIBS
programs, and Bain's Knowledge & Information training are all
variations on this model. Then there's industry/sector specialization —
usually after 12–18 months you align to a practice (healthcare, FS,
energy, TMT, ops, M&A) and build depth.

**External certifications and self-study that move the needle.** The
CFA is popular among finance-leaning analysts and the most credible
external credential for fundamental research skills. SCIP (Strategic
and Competitive Intelligence Professionals) runs competitive
intelligence certifications. Bloomberg Market Concepts is the
entry-level Bloomberg cert most firms reimburse. For methodology depth:
Damodaran's valuation materials (free on his NYU site) are the most
cited resource; "Competition Demystified" (Greenwald) for strategy
frameworks; reading Goldman/Morgan Stanley initiation reports is
genuinely the best way to learn what good output looks like; 10-Ks of
large complex companies for primary-source literacy. McKinsey Insights,
BCG Henderson Institute, and Bain Insights are useful for absorbing how
the firms structure thinking.

**What's actually changing right now.** The bottom rung is being
automated. Pulling a company profile, drafting a competitor landscape,
summarizing an earnings call, building a basic market sizing — AI tools
do these in minutes. So the skill that's appreciating is *judgment over
AI output* — knowing when a Deep Research result is missing a key
source, when a TAM number is structurally wrong, when an AI-generated
competitor map has the wrong segmentation. Firms are increasingly
hiring with this in mind: less "can you pull data" and more "can you
decide what's wrong with the data the AI pulled." The career ladder is
also compressing — analyst-to-knowledge-expert paths are getting faster
for people who can wrap AI tools well, and slower for those who can't.

The cleanest summary: most learning happens on the job through
apprenticeship and rep volume, the formal training is mostly database
and methodology basics, and the current frontier is layering AI tool
fluency on top of traditional research craft.
