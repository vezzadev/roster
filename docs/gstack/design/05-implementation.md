# Implementation: standards, phases, costs, distribution

Parent: [../design.md](../design.md)

## What to Skip in v1

- K8s / Terraform / Helm (Docker Compose only)
- Multiple templates (one: research-desk; editorial-studio and curriculum-studio queued for v1.x; app-dev-team cut, revive on demand)
- YAML composition language (canned templates only)
- OIDC / Keycloak (Nextcloud built-in auth)
- Multiple platform bindings (Nextcloud + Migadu only)
- CRD / operator pattern (CLI + Docker Compose)
- State cloning / known-team memory persistence (blank-slate only in v1)
- Real DNS / TLS / custom domains (localhost only)
- Nextcloud MCP tools beyond Talk + Files (Calendar, Deck, Collectives deferred)
- Letta Channels for external messaging (v1 uses Nextcloud Talk only for intra-team
  comms; Letta Channels reserved for v2 external notifications)

## Development Standards (set by /plan-ceo-review on 2026-05-18)

All Roster v1 development follows these standards, sourced from the user's chosen
methodology skills:

- **TDD Iron Law:** no production code without a failing test first. Watch test fail.
  Write minimal code to pass. Refactor green. Edge cases and errors are first-class.
  Ref: [test-driven-development](https://github.com/pedropaulovc/personal-marketplace/tree/main/plugins/superpowers/skills/test-driven-development).
- **Test layers (all required):** unit (real code, mocks only at REST client boundaries
  to Nextcloud/Migadu/Letta), integration (testcontainers-go for real services),
  end-to-end (full `roster up → takeover → return → down` against Docker Compose),
  stress (10 consecutive E2E runs, async on every commit to main; auto-files an
  issue if regression is detected; does NOT gate PR merges — see
  [07-refinements.md](07-refinements.md) "Test infrastructure" for the full policy).
- **Subagent-driven implementation per feature.** Five-teammate team (tester,
  implementer, code-reviewer, demo-presenter, demo-reviewer). Coordinator never
  implements. Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`. Ref:
  [subagent-driven-development](https://github.com/pedropaulovc/personal-marketplace/tree/main/plugins/superpowers/skills/subagent-driven-development).
- **Demo evidence per PR.** demo-presenter records terminal walkthrough (asciinema or
  similar) plus screenshots; saved under `demo/<date>-<feature>/`; included in PR
  description.
- **Human approval mandatory on every PR.** No PR auto-merges without a human reviewer
  approving in addition to CI gates.

These standards layer on top of AGENTS.md's 70% coverage baseline (enforced by
`.github/workflows/ci-cd-pr.yml`) — coverage remains the floor; TDD + the 4 test
layers + subagent-driven dev are the additional rigor for Roster v1.

**Timeline impact:** the original 6-week solo estimate is more realistically
**10-12 weeks aspirational / 16-20 weeks realistic** at this rigor level (revised per
Codex tension E -- maximalist standards on a research+platform+process combo, solo,
is not predictable). Treat 10-12w as direction, not forecast. Week 6 is the natural
re-baseline checkpoint. The user chose maximalist standards explicitly; the timeline
reality is the cost. See CEO plan (`~/.gstack/projects/vezzadev-roster/ceo-plans/2026-05-18-roster-v1.md`)
for the scope-vs-timeline analysis.

## Implementation Phases

Sequencing decision (revised by /plan-ceo-review on 2026-05-18): the highest-risk work
item -- agents producing useful collaborative work on a real project -- is moved to
Week 1, before any CLI or provisioning code lands. If Week 1 validation fails, pivot
or stop before sinking weeks into automation that has no value.

Per the Development Standards above, every CLI command, every provisioner function, and
every credential-rotation step in the weeks below is built via TDD + subagent team +
demo evidence. The "10-12 weeks" timeline reflects this; the "6 weeks" callouts below
are nominal scope phases, not calendar guarantees.

**Week 1: Validation spike (highest-risk first).** Hand-configure Nextcloud + Letta +
**4 Letta agents (full team: EM + 2 Senior Analysts + Researcher)** on a real sample
project -- no CLI, no automation, just `docker run` and manually written agent
definitions. Plus one **2-agent smoke-test run, capped at 1 hour**, for ablation
diagnosability (so a 4-agent failure can be localized to collaboration overhead vs
prompt design vs tool friction). Validate Success Criterion #5: do the agents
produce a meaningful artifact (a market-entry brief, draft strategy memo, or
research synthesis) without human intervention? **The artifact spec is anchored to
a public McKinsey/BCG market-entry brief** \-- agents target that section structure
and depth, not a founder-invented rubric. See
[../week-1-spike/t1-grading-rubric.md](../week-1-spike/t1-grading-rubric.md) for the
anchor briefs and rubric dimensions; the produced artifact lands in
[../week-1-spike/t8-sample-brief.md](../week-1-spike/t8-sample-brief.md). Time-box 1 week (calendar reality: the
MCP MVP work below is likely a 3-day from-scratch build, so plan for 1.5-2 weeks
realistic). **This is the gating decision.** In parallel: investigate existing
Nextcloud MCP servers; the investigation must answer **API coverage (Talk +
Files operations needed) and room-management fit (one #team room + per-pair DMs
require specific MCP capabilities)**, not just existence \-- if no community
server covers the needed ops, ~3 days to build a minimal Talk+Files MCP MVP that
unblocks the spike. Investigation results + decision live in
[../week-1-spike/t4-mcp-investigation.md](../week-1-spike/t4-mcp-investigation.md). Q7 (Nextcloud OIDC) and Q8 (Migadu OAUTH2 SASL) are deferred
to week 1.5 \-- they affect takeover UX, not spike validity. Q9 (Letta SPOF):
log natural disconnects during the spike + run **one forced `kill -9` of the
Letta server** mid-spike to observe reconnect/catch-up behavior (full 3-scenario
test deferred to v1.x); kill verdict lands in
[../week-1-spike/t5-run-ledger.md](../week-1-spike/t5-run-ledger.md) "Forced SPOF"
section. Cost tracking: **hourly OpenRouter usage exports with
mid-week and end-week trendline checks** \-- topline signal that SC#6 ($200/mo)
is on track; full per-call instrumentation deferred to weeks 5-6. OpenRouter
carries a per-model markup over direct Anthropic; SC#6 may need to be
revisited once the first trendline lands. Daily snapshots
+ trendlines live in [../week-1-spike/t7-spike-cost.md](../week-1-spike/t7-spike-cost.md). Outputs of
Week 1 feed Week 2's provisioner design (what users/passwords/rooms does the
agent setup actually need?). All spike outputs live in **[`docs/gstack/week-1-spike/`](../week-1-spike/)**
under named files (see [07-refinements.md](07-refinements.md) D6 + T4-C for the
full list with per-file purposes). Prompt freeze per numbered run + run matrix
in [../week-1-spike/t5-run-ledger.md](../week-1-spike/t5-run-ledger.md) \-- no
undocumented prompt thrash. Before the spike: 30-min exercise to write 3-4
bullet alternatives for likely failure modes (Letta unfit, agents don't
coordinate, output unusable) so "pivot or stop" has pre-committed exits. Bullets
captured in [../week-1-spike/t2-fallback-bullets.md](../week-1-spike/t2-fallback-bullets.md).

**Week 2:** Module rename (`go-project` -> `roster`), Docker Compose generator,
Nextcloud provisioner (create users, app passwords, Talk rooms). Encode the manual
Week 1 setup into automation.

**Week 3:** Migadu provisioner (Admin API), MCP server for Nextcloud Talk + Files (1-2
weeks if no community server exists), credential rotation (takeover/return flows).

**Week 4-5:** Roster CLI commands (init, up, down, takeover, return, status), Letta
integration (REST API wrapper), end-to-end integration testing.

**Week 6:** Polish, documentation, first release via GoReleaser.

**Calendar reality:** The Week-1-through-6 phases are nominal scope phases. With the
Development Standards (TDD + subagent-driven implementation + demo evidence + human
approval), each phase consumes ~1.7-2x calendar time vs solo CC implementation. Realistic
delivery: 10-12 weeks. This was accepted as a deliberate tradeoff (rigor over speed)
in the /plan-ceo-review of 2026-05-18.

## Cost Model (rough estimate)

```
Infrastructure:
  Migadu (email)                           $19/mo
  Compute (Nextcloud + Letta, VPS/local)   $0-20/mo (local dev is free)

Claude models via OpenRouter (4 agents, moderate autonomy):
  Agents poll every 30s but only call the model when there's work to do.
  Estimate: ~50-100 meaningful interactions/agent/day (not 30s polling).
  Average interaction: ~2K input tokens + ~500 output tokens.
  Sonnet (anthropic/claude-sonnet-4.6): ~$0.003/input 1K + ~$0.015/output 1K
    = ~$0.0135/interaction at Anthropic-direct list price.
  Per agent per day: ~$0.68-1.35
  Per agent per month: ~$20-40
  4 agents: ~$80-160/mo

  One Opus agent (Engagement Manager, for synthesis): ~3x Sonnet cost = ~$60-120/mo
  Revised with Opus: $100-200/mo for API alone

  OpenRouter markup: numbers above are Anthropic-direct list price. OpenRouter
  passes through at a per-model markup; pin actual OpenRouter rates per the
  catalog at run start (see t7-spike-cost.md). Re-baseline SC#6 ($200/mo) once
  the first OpenRouter trendline lands — likely a small upward push.

Total: $119-239/mo at Anthropic-direct rates (within $200/mo target for moderate
  usage, may exceed with heavy Opus usage). Add OpenRouter markup on top.
```

## Letta Channels Contingency

Letta Channels is in beta. v1 architecture does not depend on it -- intra-team
communication uses Nextcloud Talk via MCP tools. If Letta Channels stabilizes, v2 adds
external notification channels (Telegram, Slack). If Channels proves unstable, the
architecture is unaffected. Letta is used in v1 for memory persistence and agent lifecycle
management only.

## Distribution Plan

- CLI binary: GitHub Releases via GoReleaser (cross-compiled, already configured)
- Container images: GHCR (already configured in goreleaser.yml)
- Installation: `go install` or download binary from releases
- Docker Compose templates: bundled in the binary or fetched from a templates repo
- Migadu setup: manual DNS configuration (documented), mailbox creation automated

## Dependencies

- Letta (open source, actively maintained, channels in beta)
- Nextcloud (open source, mature, Helm chart available)
- Migadu ($19/mo, Admin API for programmatic mailbox management)
- OpenRouter (model inference; routes to Anthropic Claude models in v1, can route to alternative providers as a fallback)
- Docker + Docker Compose (local development)
