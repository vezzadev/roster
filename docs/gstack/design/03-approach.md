# Approaches Considered & Recommended Approach

Parent: [../design.md](../design.md)

## Approaches Considered

### Approach A: "Weekend Demo"

Docker Compose, one hardcoded template, scripted heartbeat agents (no real AI). Proves
provisioning + identity + takeover + teardown. Effort: S (1-2 weeks). Risk: Low. Doesn't
validate the core thesis that AI teams produce useful work.

### Approach B: "Working Team" (chosen, with Letta modification)

Docker Compose with real agents running on Letta (memory + channels for free). Nextcloud
for workspace, Migadu for email. One canned template (research-desk). The AI team actually
produces work. Effort: **10-12 weeks aspirational / 16-20 weeks realistic** under the
Development Standards rigor set below. Nominal scope is ~6 weeks but the TDD + subagent
+ demo-evidence + human-approval workflow per feature adds ~30-50% wall time, plus
~2-3 days of one-time stress/flake infra, plus from-scratch Nextcloud MCP work, plus
the fact that this combines a research project (does the agent team produce useful
work?) + a platform build + a process experiment, simultaneously, solo. Treat the
estimate as direction, not forecast. Week 6 is the natural re-baseline checkpoint --
expect to cut scope there if reality diverges. See Codex tension E in
[07-refinements.md](07-refinements.md).
Risk: Medium-High (MCP server for Nextcloud is new work, agent behavior design is open
research, dev workflow is unproven at this rigor for a solo operator).

### Approach C: "Spec First"

Define roster.yaml as an open specification. Build minimal reference implementation.
Effort: M (3-4 weeks). Risk: High (specs without adoption are dead documents, premature
abstraction before knowing the right abstractions).

## Recommended Approach

**Approach B: "Working Team" with Letta as agent runtime.**

Rationale: The thing to prove is not that you can provision infrastructure (table stakes)
or write a spec (premature). You need to prove that an AI team provisioned by roster
actually produces useful output on a real project.

Using Letta instead of raw Claude Agent SDK gives you:
- Agent memory persistence (core Letta feature)
- Multi-channel messaging via Letta Channels (Telegram, Slack, Discord built-in)
- Agent lifecycle management (Letta server)
- Same integration complexity as raw SDK, but more capabilities out of the box

See [04-architecture.md](04-architecture.md) for the system architecture, takeover flow,
agent execution model, failure modes, and integration interfaces.
See [05-implementation.md](05-implementation.md) for what to skip, development standards,
phases, cost model, distribution, and dependencies.
