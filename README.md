# Roster

**Docker-compose for AI teams.** One config defines roles, skills, and tools.
`roster up` provisions a full project team — chat, email, files, memory.
`roster down` tears it all down. Humans can take over any role at any time.

> **Status: pre-v1, in active development.** The CLI you see in this README is
> the target design, not yet what's in `main`. Track progress in
> [`docs/gstack/design.md`](docs/gstack/design.md).

## Why

Spinning up a multi-agent project team today means weeks of integration work:
provisioning chat channels, creating email identities, wiring up agent memory,
configuring tools, managing credentials. Each piece works in isolation, but
nobody has defined how they compose into a coherent team. Only deeply technical
people get past the plumbing — and even they burn weeks before any agent
produces useful work.

Roster's bet: disposable, blended human/AI project teams become normal within
18 months, and the integration layer is where the value lives.

## What you get

- **One command to provision.** `roster up` spins up a 4-role app-dev team
  (PM, Designer, Engineer, Marketing) in under 10 minutes.
- **Real identities, real infrastructure.** Each agent gets a Nextcloud
  account, email mailbox (Migadu), and shared workspace — not anonymous
  workers.
- **First-class human takeover.** `roster takeover pm` stops the agent,
  rotates credentials, and hands you a login URL within 30 seconds. The AI
  is provably blocked.
- **Resume with context.** `roster return pm` restarts the agent with a
  catch-up directive — the agent uses its existing tools to read what
  happened while you were driving.
- **Predictable cost.** ~$100–200/mo total for a 4-agent team, including
  API calls. No token-burning factories.

## How it compares

| | [Gas Town](https://github.com/sourcegraph/gas-town) | Roster |
|---|---|---|
| Domain | Coding agents only | Any project role |
| Agent count | 20–30 parallel | 3–5 focused |
| Cost | ~$100/hr token burn | ~$100–200/mo |
| Communication | Internal git hooks | Real email, chat, files |
| Identity | Disposable workers | Persistent roles with memory |
| Human override | Mayor supervises | Become any role via GUI |

Closest enterprise neighbor is [Archestra](https://archestra.ai/) — but
Archestra wraps an existing organization, while Roster provisions a new
workspace from blank state. Microsoft Agent 365 observes; it doesn't
provision. Dust.tt / Ruh AI augment existing companies; Roster spins up new
AI-native teams.

## Architecture

```
roster.yaml (canned template)
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
  · Talk     · SMTP   · Memory      · PM
  · Files    · IMAP   · Lifecycle   · Engineer
  · Mail UI  · $19/mo               · Designer
                                    · Marketing
```

- **Agents ↔ Nextcloud:** MCP tools (Talk + Files in v1).
- **Agents ↔ Email:** IMAP/SMTP via Migadu app passwords.
- **Agents ↔ Agents:** Nextcloud Talk rooms (one `#team` + per-pair DMs),
  visible to humans during takeover.
- **Takeover:** stop the Letta agent first, then rotate Nextcloud + Migadu
  credentials. Hard runtime kill switch; credential rotation is
  defense-in-depth.

v1 runs on a single host. Nextcloud binds to `0.0.0.0:8080` so collaborators
on your LAN can join — restrict via firewall or
`--nextcloud-bind 127.0.0.1` if you're not on a trusted network. Real DNS,
TLS, and cloud deployment land in v2.

## Quick start

> Not yet runnable. This is the target UX for v1.

```bash
# Pick a canned template and initialize the project
roster init --template app-dev-team --project my-experiment

# Bring the team up (Docker Compose + Nextcloud + Letta + agents)
roster up

# See who's running and what they're doing
roster status

# Take over the PM role — get a login URL, agent is stopped
roster takeover pm

# Return the role to AI when you're done
roster return pm

# Tear everything down
roster down
```

## Security posture

v1 is honest about what it does and doesn't defend against:

- **Threat model:** a confused or looping agent that a human needs to seize
  control from. Takeover is a *best-effort, time-bounded containment*, not
  a defense against an adversarial agent that already exfiltrated
  credentials.
- **Prompt injection in Talk/Files content** is a known v1 weakness. Light
  system-prompt hardening only. Real defense (MCP proxy sidecar, outbound
  network policy) is a v1.x research item.
- **Agent admin separation:** agents never hold Nextcloud admin
  credentials. A compromised agent cannot bypass takeover by creating new
  accounts.

## Development

Roster is a Go CLI. The current scaffold inherits from a Go template; the
`go-project` / `myapp` names are scheduled to be renamed to `roster` in
Week 2 of the v1 plan.

```bash
make tools          # Install dev tools (air, golangci-lint, goimports)
make dev            # Run with hot reload
make build          # Build binary
make test-all       # lint + vet + coverage (required before push)
```

See [AGENTS.md](AGENTS.md) for the full command list and code conventions.

### Development standards

v1 is built under deliberately maximalist standards (chosen as a rigor
experiment alongside the product work):

- **TDD Iron Law:** no production code without a failing test first.
- **Test layers:** unit, integration (testcontainers-go), end-to-end (full
  `up → takeover → return → down` against real Docker Compose), plus 10
  consecutive E2E stress runs on every commit to `main`.
- **Subagent-driven implementation** per feature (tester, implementer,
  code-reviewer, demo-presenter, demo-reviewer).
- **Demo evidence on every PR** (terminal recording + screenshots).
- **Human approval mandatory** on every PR before auto-merge.

These standards SUPERSEDE the "70% coverage" baseline inherited from the Go
template. Full rationale in
[`docs/gstack/design.md`](docs/gstack/design.md) → Development Standards.

## Roadmap

| Phase | Scope |
|---|---|
| **Week 1** | Validation spike — hand-configure Letta + 2 agents on a real project. Gating decision: do they produce useful output? |
| **Week 2** | Module rename, Docker Compose generator, Nextcloud provisioner. |
| **Week 3** | Migadu provisioner, MCP server for Nextcloud (Talk + Files), credential rotation. |
| **Week 4–5** | CLI commands (init, up, down, takeover, return, status), Letta REST integration, E2E tests. |
| **Week 6** | Polish, docs, first release. |

**Calendar reality:** 10–12 weeks aspirational, 16–20 weeks realistic for a
solo operator under the standards above. Week 6 is the re-baseline
checkpoint.

## Dependencies

- [Letta](https://letta.com/) — agent runtime (memory + lifecycle).
- [Nextcloud](https://nextcloud.com/) — workspace (Talk, Files, Mail UI).
- [Migadu](https://www.migadu.com/) — email ($19/mo flat, Admin API).
- [Claude API](https://www.anthropic.com/) — agent LLM calls.
- Docker + Docker Compose.

## Distribution

- CLI binary via [GoReleaser](https://goreleaser.com/) (linux/darwin/windows,
  amd64/arm64) — `go install` or download from GitHub Releases.
- Container images on GHCR.

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Further reading

- [`docs/gstack/design.md`](docs/gstack/design.md) — full design doc:
  premises, architecture, failure modes, cost model, open questions.
- [AGENTS.md](AGENTS.md) — code conventions, build commands, project
  structure.
