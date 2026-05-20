# Constraints, Premises, Cross-Model Perspective

Parent: [../design.md](../design.md)

## Constraints

- Solo founder on sabbatical
- Go CLI (cobra-based), existing CI/CD and GoReleaser in place
- Must run on a single machine for v1 (Docker Compose, not K8s)
- Letta as agent runtime (memory + channels), not raw Claude Agent SDK
- Budget-conscious: ~$100-200/mo for a 4-agent team including API costs
- Go module path and binary name need renaming from `go-project`/`myapp` to `roster`

## Premises

1. **Reproducible provisioning with selective state.** Both "blank slate" (throw away
   everything) and "known team" (clone a setup, carry forward memories) personas benefit
   from the same provisioning engine. Disposability is a consequence, not the feature.

2. **Real infrastructure as shared workspace with credential-based security boundaries.**
   Platform-agnostic via two requirements: MCP servers for AI roles + credential rotation
   for human takeover. Roster doesn't compete with agent-to-agent protocols (MCP, A2A) --
   it provisions the workspace those agents operate in.

3. **Human takeover = best-effort, time-bounded containment for a misbehaving or
   confused agent.** Stopping the Letta runtime + rotating credentials prevents *future*
   agent action; it does NOT defend against pre-takeover exfiltration, since the agent
   had live credentials and the prompt-injection threat surface is open in v1. Primary
   threat model: a confused/looping/off-the-rails agent that a human wants to seize
   control from. Adversarial-agent hardening (MCP proxy sidecar to isolate secrets from
   the agent runtime, outbound network policy, cred scoping) is a v1.x research item --
   see [07-refinements.md](07-refinements.md) "Premise 3 reframe (Codex tension A)."

4. **Independent survival path.** Open-source, multi-platform alternative to Microsoft
   Agent 365's governance layer. The YAML file is the source of truth for agent-human
   accountability. Acquihire is a bonus exit, not the only path.

5. **Ship for experimenters first (revised 2026-05-19).** The experimenter persona is
   now the analyst, consultant, or strategy operator with AI leverage interest -- already
   bought into blended human/AI workflows, needs better tooling not convincing. First-timers
   and the original "technical founder" persona follow later.

6. **Templates first, YAML composition later.** Ship v1 with canned templates. Measure
   demand for custom composition via issue requests. Avoid premature abstraction.

7. **Nextcloud + Migadu + Letta on Docker Compose for v1.** Single URL workspace,
   $19/mo flat email, managed agent runtime with memory and channel integrations.
   K8s/Terraform is the v2 evolution, not the starting point.

## Cross-Model Perspective

Codex (OpenAI) provided an independent cold read:

- **Steelman:** "This is an operating system for disposable AI-native companies, not just
  an agent orchestrator. The value is that one config can instantiate a real working
  environment with identities, permissions, shared tools, and a hard human override."

- **Key insight:** The narrowest wedge IS the real product. "Not 'multi-agent
  infrastructure,' not 'open protocol.' The win condition is an opinionated, end-to-end
  startup-team appliance for experimenters."

- **Challenged premise:** Early users won't want a composition language (YAML). They'll
  want a default company-in-a-box. Evidence: users consistently pick canned templates,
  barely edit config. *Founder accepted this challenge and revised to templates-first.*

- **48-hour prototype:** Docker Compose, one template, scripted agents, local SQLite.
  Zero to live workspace with named roles and working kill-switch in under 10 minutes.
  Skip Migadu, Letta, OIDC, K8s, multi-platform.
