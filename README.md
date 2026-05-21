# Roster

**Docker-compose for human+AI teams.** One config defines roles, tools,
and who's AI vs human. `roster up` brings up the team with chat, email,
files, and memory — AI works through the same accounts a human would.
Swap any seat to human any time. `roster down` tears it all down.

> **Status: pre-v1, in active development.** The CLI shown below is the
> target design for v1, not what's in `main` yet. Progress in
> [`docs/gstack/design.md`](docs/gstack/design.md).

## Why

Standing up a multi-agent team today is weeks of plumbing. Chat channels.
Email identities. Agent memory. Tool configuration. Credentials. Every
piece works in isolation. Nobody has wired them together into something
that behaves like a team, which is why only deep technical people get
past setup, and why even they spend weeks before an agent produces useful
work.

Almost every multi-agent product I've seen is a coding tool. Roster
isn't. The v1 demo team is a research desk: an Engagement Manager, two
Senior Analysts, and a Researcher. Their job is to produce the kind of
brief a boutique consultancy bills five figures for. Everything they
output is a draft. Nothing ships without a human reading it first.

The bet behind this: project teams of mixed humans and AI agents become
a normal way to work in the next 18 months. They get spun up for a
project, torn down after, and the thing that keeps them coherent is a
human always being one command away from driving any seat.

## What you get

`roster up` provisions a 4-role research desk in under 10 minutes. Each
agent gets a real Nextcloud account, a real Migadu mailbox, and a real
shared workspace. They are not anonymous workers.

`roster takeover em` stops the Engagement Manager, rotates its
credentials, and hands you a login URL inside 30 seconds. While you're
driving, the AI is stopped at the runtime and locked out of its
accounts. When you hand back with `roster return em`, the agent
restarts with a short directive telling it to use its existing tools to
read up on what happened in its absence.

## How it compares

| | [Gas Town](https://github.com/sourcegraph/gas-town) | [gstack](https://github.com/garrytan/gstack) | Roster |
|---|---|---|---|
| Layer | Agent factory | Per-agent skill packs | Team provisioning |
| Domain | Coding only | Any (skills like /qa, /ship, /review) | Knowledge work (research, strategy, content) |
| Default team | 20–30 coding workers | Augments one agent | 4-role research desk |
| Communication | Internal git hooks | n/a (single agent) | Real email, chat, files |
| Identity | Disposable workers | Inherits from host | Persistent roles with memory |
| Human override | Mayor supervises | n/a | Become any role via GUI |

gstack isn't a competitor, it's a complement. gstack skills slot into a
Roster role's `skills:` field, and the agent runtime resolves them at
provisioning time. Roster gives a team its workspace. gstack gives an
agent its capabilities.

## Architecture

```
canned template (research-desk)
         │
         ▼
    Roster CLI  ── roster up / down / takeover / return / status
         │
    Docker Compose
         │
    ┌────┼────┬───────┬─────────────┐
    ▼    ▼    ▼       ▼             ▼
 Nextcloud  Migadu  Letta Server   Agent instances
 (workspace) (email) (runtime)     (one per role)
  · Talk     · SMTP   · Memory      · Engagement Manager
  · Files    · IMAP   · Lifecycle   · Senior Analyst (×2)
  · Mail UI                         · Researcher
```

Agents talk to Nextcloud through MCP (Talk and Files in v1). They use
Migadu for IMAP and SMTP, but in v1 that's strictly internal handoffs;
no client-facing mail yet. Agent-to-agent traffic flows through Nextcloud
Talk rooms (one `#team` plus per-pair DMs), so when a human takes over a
role they can read the whole conversation history natively, without any
custom UI.

Takeover stops the Letta agent first, then rotates credentials in
Nextcloud and Migadu. The runtime stop is the hard guarantee. The
credential rotation is defense in depth in case the agent already cached
something it shouldn't have.

v1 runs on a single host. Nextcloud binds to `0.0.0.0:8080` so
collaborators on your LAN can join the workspace. If you're not on a
trusted network, restrict it via firewall or pass `--nextcloud-bind
127.0.0.1`. Real DNS, TLS, and cloud deployment all land in v2.

## Quick start

> Not yet runnable. This is the target UX for v1.

```bash
# Pick a canned template and initialize the project
roster init --template research-desk --project market-entry-brief

# Bring the team up (Docker Compose + Nextcloud + Letta + agents)
roster up

# See who's running and what they're doing
roster status

# Take over the Engagement Manager role: login URL printed, agent stopped
roster takeover em

# Return the role to AI when you're done
roster return em

# Tear everything down
roster down
```

## Security posture

v1 tries to be honest about what it does and doesn't defend against.

The threat model is a confused or looping agent that a human needs to
seize control from. Takeover is best-effort, time-bounded containment.
It does nothing to claw back data an adversarial agent already exfiltrated
before being stopped, and we are upfront about that.

Prompt injection inside Talk messages and Files content is a known v1
weakness. The defense in v1 is light system-prompt hardening, and that's
it. Real defense (an MCP proxy sidecar that holds credentials away from
the agent runtime, outbound network policy) is on the v1.x research list.

Agents never hold Nextcloud admin credentials. A compromised agent can't
bypass takeover by creating itself a new account.

## Development

Roster is a Go CLI. The scaffold still carries the `go-project` and
`myapp` names from the template repo it was bootstrapped from; those get
renamed to `roster` in Week 2 of the v1 plan.

```bash
make tools          # Install dev tools (air, golangci-lint, goimports)
make dev            # Run with hot reload
make build          # Build binary
make test-all       # lint + vet + coverage (required before push)
```

See [AGENTS.md](AGENTS.md) for the full command list and code conventions.

### Development standards

v1 is being built under deliberately maximalist standards. Partly because
the product needs them. Partly as a rigor experiment to see what
maximalist standards on a research+platform+process combo costs a solo
operator in calendar time.

- TDD: no production code without a failing test first.
- All four test layers: unit, integration (testcontainers-go),
  end-to-end against real Docker Compose, plus 10 consecutive E2E runs
  on every commit to `main` (planned — not yet wired in CI).
- Subagent-driven implementation per feature: tester, implementer,
  reviewer, demo-presenter, demo-reviewer.
- Demo evidence on every PR (terminal recording plus screenshots).
- Human approval required on every PR. No CI-only auto-merge.

## Dependencies

- [Letta](https://letta.com/) — agent runtime (memory + lifecycle)
- [Nextcloud](https://nextcloud.com/) — workspace (Talk, Files, Mail UI)
- [Migadu](https://www.migadu.com/) — email (flat-rate hosting, Admin API)
- [Claude API](https://www.anthropic.com/) — agent LLM calls
- Docker + Docker Compose

## Distribution

CLI binary via [GoReleaser](https://goreleaser.com/) for
linux/darwin/windows on amd64 and arm64. Install with `go install` or
download from GitHub Releases. Container images on GHCR.

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Further reading

- [`docs/gstack/design.md`](docs/gstack/design.md) — full design doc:
  premises, architecture, failure modes, open questions.
- [AGENTS.md](AGENTS.md) — code conventions, build commands, project
  structure.

## AI attribution

<a href="https://aiattribution.github.io/statements/AIA-PAI-SeCeNc-Hin-R-?model=Claude%20Opus%204.7%2C%20gstack%201.40-v1.0">
  <strong>AIA PAI SeCeNc Hin R Claude Opus 4.7, gstack 1.40 v1.0</strong>&nbsp;
  <img src="docs/ai-attribution/icons/primarily-ai-icon.svg" height="20" alt="Primarily AI" title="Primarily AI" />
  <img src="docs/ai-attribution/icons/stylistic-edits-icon.svg" height="20" alt="Stylistic edits" title="Stylistic edits" />
  <img src="docs/ai-attribution/icons/content-edits-icon.svg" height="20" alt="Content edits" title="Content edits" />
  <img src="docs/ai-attribution/icons/new-content-icon.svg" height="20" alt="New content" title="New content" />
  <img src="docs/ai-attribution/icons/human-initiated-icon.svg" height="20" alt="Human-initiated" title="Human-initiated" />
  <img src="docs/ai-attribution/icons/certified-review-icon.svg" height="20" alt="Reviewed" title="Reviewed" />
</a>

This work was primarily AI-generated. AI was used to make stylistic
edits (structure, wording, clarity), content edits (scope, information,
ideas), and new content (text, images, analysis, ideas). AI was
human-initiated — prompted for its contributions, or AI assistance was
enabled. All AI-generated content was reviewed and approved by a human.
Models/tools used: Claude Opus 4.7 and [gstack](https://github.com/garrytan/gstack)
1.40.

Format: [AI Attribution Toolkit](https://aiattribution.github.io/) (IBM
Research, [CHI 2025](https://dl.acm.org/doi/full/10.1145/3706598.3713522)).
