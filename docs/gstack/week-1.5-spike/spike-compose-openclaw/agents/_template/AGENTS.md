# AGENTS.md (template)

OpenClaw reads this file at the start of every turn. It defines the agent's
role, the team, and the coordination contract.

**Mapping from Letta system prompts** (see `../../../../week-1-spike/t5-system-prompts.md`):

- Letta's `system` block → AGENTS.md "Role" + "Mandate" sections
- Letta's `persona` memory block → SOUL.md
- Letta's `human` memory block → SOUL.md "Working with the founder" section
- Letta's `archival_memory_*` calls → MEMORY.md (file-backed; OpenClaw scribe skill writes here on each turn)

TBD on T3' kickoff: copy frozen prompt content from t5-system-prompts.md
into each agent's customized AGENTS.md (per-identity variants).

## Role

<one line — e.g. "Engineering Manager coordinating a 4-person market-entry research team">

## Mandate

<frozen from Week 1 t5-system-prompts.md per agent>

## Team

- **EM** — Engineering Manager (Opus 4.7) — coordinates, synthesizes, makes
  the final call on the brief
- **Senior A** — Senior Analyst (Sonnet 4.6) — competitive landscape +
  market sizing track
- **Senior B** — Senior Analyst (Sonnet 4.6) — demand signals + entry
  archetype track
- **Researcher** — Researcher (Sonnet 4.6) — primary-source web research,
  feeds A and B via Talk

## Coordination contract

- All inter-agent messages go through Nextcloud Talk via the `nextcloud-mcp`
  server (one #team room + per-pair DMs)
- File deliverables land in shared Nextcloud Files folders per the contamination
  guard split (see `../../../../week-1-spike/t4-mcp-investigation.md`
  "Network and ACL policy")
- The Researcher is the **only** agent with web access; A/B and the EM may
  not call web tools directly
