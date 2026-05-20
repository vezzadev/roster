# Problem & Market

Parent: [../design.md](../design.md)

## Elevator Pitch

Docker-compose for human+AI teams. One YAML file defines roles, skills, and tools.
`roster up` provisions a full project team -- chat, email, files, memory. Take over
any role, any time, via GUI. `roster down` tears it all down. Open protocol, open
source.

The v1 canned team is a **research desk** (Engagement Manager + 2 Senior Analysts
+ Researcher) producing the kind of market-entry brief a boutique consultancy
charges five figures for. Almost every multi-agent product today is a coding tool;
Roster is not.

## Problem Statement

Building AI-staffed project teams today requires weeks of integration work: provisioning
comms channels, creating email identities, wiring up agent memory, configuring tools, and
managing credentials. Each piece works in isolation but nobody has defined how they compose
into a coherent team. Only deeply technical people can run multi-agent project teams, and
even they burn weeks on plumbing instead of building.

## Demand Evidence

- Founder built "the-office" hackathon project (github.com/pedropaulovc/the-office) using
  Claude Agent SDK. Hit the integration complexity wall firsthand.
- No open standard exists for defining AI team composition, role bindings, or lifecycle
  management.
- Microsoft Agent 365 (GA May 2026, E7 license) validates governance as a real enterprise
  need, but only observes/governs -- does not provision teams or workspaces.
- Gas Town (Steve Yegge, 13k GitHub stars) validated multi-agent orchestration but
  targets coding-only with ~$100/hr token burn. Roster targets any project role at
  ~$100-200/mo total.
- Closest competitors (Ruh AI, Dust.tt) target existing companies augmenting human teams,
  not people spinning up new AI-native project teams from scratch.
- [Archestra](https://archestra.ai/) (Aug 2025, $3.3M pre-seed, MIT-licensed):
  open-source enterprise MCP gateway and guardrails platform from repeat
  Grafana/Elastic founders. Plugs into existing
  enterprise stacks (Slack, Teams, Jira, Confluence, SharePoint) to make agent
  write-access safe against the "lethal trifecta." Different wedge from Roster:
  Archestra wraps an existing organization; Roster provisions a new project workspace
  from blank state. Overlap is vocabulary (agents, MCP, Docker, credentials, Slack) and
  credential-rotation patterns, not target user or job-to-be-done. Possible v1.5
  integration target (optional MCP gateway inside the Docker Compose) rather than
  pure competitor. Full comparison: pedro-main-research-archestra-20260518-171126.md
  in ~/.gstack/projects/vezzadev-roster/.
- Anthropic acquihired Zulip leadership (May 2026) signaling intent to build
  agents-in-comms infrastructure. Gap exists at the "team orchestration" layer above.

**Demand risk (acknowledged):** Long-term AI agent collaboration is niche today. This is
a bet that AI teams provisioned per project (spun up, torn down) become normal within
18 months, and being 12 months ahead on the integration layer is the play. Acceptable
downside for a sabbatical project: deep multi-agent expertise, portfolio piece,
open-source community signal.

## Status Quo

- Advanced users: git + Claude Code, bespoke scripts, manually configured agent instances
- Most people: not doing this at all because multi-agent collaboration is too niche
- Closest competitors target different use cases (enterprise augmentation, coding-only)
- No tool exists for "spin up an entire AI project team with real identities and comms"

### Positioning: contract, not infrastructure

Roster doesn't compete on infrastructure choice -- it competes on the abstraction. The
provisioning contract is two requirements: MCP servers for AI roles + credential rotation
for human takeover. Any backend that satisfies this contract works. v1 uses Nextcloud
because it's a concrete proof of concept, but a lighter provider (shared directory + Slack
channel + Mailgun) would work with the same roster.yaml.

### Gas Town (positioning context)

Gas Town (Steve Yegge, 13k GitHub stars, v1.0 Apr 2026) is the closest conceptual
neighbor. It validated the multi-agent orchestration space but occupies a different niche:

| | Gas Town | Roster |
|---|---|---|
| Domain | Coding agents only | Any project team role |
| Agent count | 20-30 parallel (factory) | 3-5 focused (team) |
| Cost profile | ~$100/hr token burn | ~$100-200/mo total |
| Communication | Internal git hooks, beads | Real email, chat, files (external-facing) |
| Identity model | Disposable workers (polecats) | Persistent role identities with memory |
| Human involvement | Mayor supervises | Human can become any role (takeover via GUI) |
| Output | Code (PRs, commits) | Business outcomes (research, strategy, outreach) |
| Provisioning | Config directories | Full infrastructure (Nextcloud, email, storage) |
| Reputation | Polarized (visionary vs tokenmaxxing theater) | — |

**Roster's positioning: "the sane alternative."** Same insight (AI teams are the unit of
work), practical execution. Not a token-burning code factory... a real project team with
identities, inboxes, and human-friendly takeover. $200/mo, not $3k/week.

Gas Town is opinionated about the infrastructure (git hooks, beads, config directories).
Roster is opinionated about the contract and agnostic about the infrastructure.

**Key differentiators for hardcore AI users (first target market):**
1. Agents have real identities (email, chat accounts) not anonymous workers
2. Human takeover is first-class, not an afterthought
3. Non-coding roles (analyst, researcher, strategist, content roles) are first-class citizens; v1 default is research-desk
4. Predictable teams, not long-running factories

### gstack (composability with agent skill systems)

Agent skills (e.g., gstack's /qa, /ship, /review) integrate naturally via the role spec
once YAML provisioning ships:

```yaml
roles:
  - id: engineer
    type: ai
    agent: {provider: claude, model: opus}
    skills: [gstack-qa, gstack-ship, gstack-review]
```

**Roster's positioning:** no special integration needed. Skills are just another field in
the role definition, resolved by the agent runtime (Letta) at provisioning time. Roster
provisions the team and workspace; skill systems provide the agent's internal capabilities.

## Target User & Narrowest Wedge

**Primary (revised 2026-05-19):** boutique consultancy partner, indie analyst, or
in-house strategy/research operator who wants to scale themselves. Already runs
research-desk work manually with a small team; the value prop is the same workflow,
compressed.

**Secondary:** content/research/strategy people inside larger companies who need
a "quick brief" capability without going through the firm's official research
request process.

**Narrowest wedge (revised 2026-05-19):** one canned template (`research-desk`:
Engagement Manager, 2 Senior Analysts, Researcher), one canned demo brief
(market-entry brief for a hardcoded vertical, e.g. HR-tech or fintech), one
canned output format (single-document strategy memo with appendix). No slide
decks, no financial models, no external-facing comms in v1. Canned templates
first (measure demand for custom YAML composition via issue requests),
Nextcloud + Migadu on Docker Compose, one CLI command to provision, one command
to destroy.

**Cut from v1:** the original `app-dev-team` template (PM/Designer/Engineer/
Marketing). Revive only if external demand surfaces post-v1.

**Buyer paradox:** marketing copy can punch up at the consulting category
("replace your $50k engagement with a 4-agent research desk for $200/mo");
in-product UX must make the analyst feel leveraged, not replaced. Same dynamic
as Cursor: the buyer is the very person the public hook appears to threaten.
Letting the marketing energy bleed into product copy kills the actual buyer.
