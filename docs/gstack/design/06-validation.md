# Validation: Success Criteria, Open Questions, Assignment

Parent: [../design.md](../design.md)

## Success Criteria

1. `roster up` provisions a working 4-role AI team in under 10 minutes
2. `roster takeover <role>` gives a human full access to all role services at
   `http://localhost:8080` within 30 seconds, and the AI agent is provably blocked
3. `roster return <role>` resumes the AI agent with a catch-up summary (Talk messages,
   file changes, emails since takeover timestamp injected into Letta memory)
4. `roster down` tears down all resources cleanly (Docker containers + volumes)
5. The AI team produces at least one meaningful artifact (market-entry brief,
   strategy memo, or research synthesis) without human intervention on a sample
   project -- validate this BEFORE any provisioning code lands by manually running
   agents against a sample brief (Week 1). This is the gating decision for
   proceeding with weeks 2-6. Spike artifact lands in
   [../week-1-spike/t8-sample-brief.md](../week-1-spike/t8-sample-brief.md). **External-validation
   bar (revised by /plan-eng-review 2026-05-19):** founder self-grades the spike
   artifact against the anchored public McKinsey/BCG market-entry brief (rubric
   in [../week-1-spike/t1-grading-rubric.md](../week-1-spike/t1-grading-rubric.md));
   before any time/money is spent on a practicing analyst, a **multi-AI opinion
   panel** (Codex + Claude + others) reviews the artifact against the same spec.
   Only if the AI panel signal is positive does the project pay for a practicing
   analyst review (week 2 first 3 days). The 8h-saved bar, when an analyst
   review happens, is normalized to **text-deliverable-equivalent hours**
   (artifact-vs-artifact, not artifact-vs-full-consulting-engagement). Carried
   risk acknowledged: Codex rated the self-grade pathway CRITICAL for motivated
   reasoning; the AI panel substitution is the mitigation \-- see
   [07-refinements.md](07-refinements.md).
6. Total infrastructure cost stays under $200/mo for a 4-agent team. Spike-period
   tracking in [../week-1-spike/t7-spike-cost.md](../week-1-spike/t7-spike-cost.md).

Additional acceptance criteria from /plan-ceo-review (2026-05-18):

- **SC7:** `schema/roster.v1.json` v1.0.0 committed AND reachable at stable external URL
  with correct content-type.
- **SC8:** `roster activity <role> --follow` attaches within 2 seconds; renders Letta
  message history with sub-second latency from REST response (measured: timestamp delta
  between Letta response receipt and stdout flush).

## Open Questions

1. **Nextcloud MCP server scope:** Build from scratch or wrap existing Nextcloud REST
   client libraries? How much of the Nextcloud API surface do agents actually need?
2. **Agent behavior design:** How prescriptive should role system prompts be? Too rigid
   and agents can't adapt; too loose and they don't collaborate meaningfully.
3. **Letta Channels vs Nextcloud Talk:** Use Letta channels (Slack/Discord) for external
   communication and Nextcloud Talk for internal team chat? Or consolidate on one?
4. **Agent-to-agent communication:** Direct Letta multi-agent tools, or mediated through
   Nextcloud Talk (visible to humans during takeover)?
5. **Template format:** How much of the template is exposed to the user vs. hidden as
   implementation detail?
6. **Cost model accuracy:** Real-world Claude API costs for 4 agents with moderate
   autonomy need measurement. Target: total infrastructure + API under $200/mo.
7. **Nextcloud OIDC viability:** Can Nextcloud's `oidc` Identity Provider app federate
   credentials for agent access in a way that makes single-revocation atomic? If yes,
   v1.x may simplify takeover. Investigation: Week 1.5 spike (deferred from Week 1 per
   /plan-eng-review 2026-05-19).
8. **Migadu OAUTH2 SASL support:** Does Migadu support OAUTH2 SASL for IMAP/SMTP, or
   are app passwords the only auth surface? Affects whether "single auth domain" is
   reachable in v1.x. Investigation: Week 1.5 (deferred from Week 1 per
   /plan-eng-review 2026-05-19).
9. **Letta SPOF behavior under failure:** When the headless container loses WebSocket
   to the server, what happens to in-flight agent actions? When the server comes back,
   does the agent catch up automatically? Week 1 validation = reactive logging of
   any natural disconnects + **one forced `kill -9` of the Letta server mid-spike**
   to observe reconnect/catch-up. Full 3-scenario test (clean WS close, kill -9,
   60s sustained outage) deferred to v1.x \-- carried risk acknowledged. Forced-kill
   verdict captured in
   [../week-1-spike/t5-run-ledger.md](../week-1-spike/t5-run-ledger.md) "Forced SPOF" section.
10. **MCP proxy sidecar viability:** Can an MCP proxy sidecar between the agent
    runtime and tool servers (Nextcloud MCP, email) hold credentials such that
    the agent never sees them directly? If so, exfiltration becomes architectural-
    not-policy. Investigation: v1.x research; document outcome before any "hard
    kill" language returns to Premise 3.

## The Assignment

**Watch someone try to set up a multi-agent project team without roster.** Not
hypothetically -- actually sit with one person (a friend, a colleague, someone from a
Discord community) and watch them try to provision AI teammates with real communication
channels. Don't help. Don't explain. Write down every place they get stuck, every
integration they struggle with, every moment they give up or ask for help. That
observation is worth more than six months of building in isolation. It will tell you
whether the 10-minute-to-working-team promise is solving real pain or imagined pain.

## What I noticed about how you think

- You refined Premise 1 when challenged, but you didn't weaken it -- you made it
  stronger. "Reproducible provisioning with selective state" is a sharper framing than
  "disposable teams." You said the blank-slate person benefits from throw away, the
  known-team person benefits from cloning. Same engine, different state carryover. That's
  the kind of reframe that turns a niche feature into a general capability.

- When I challenged real infrastructure vs. protocol-level communication, you didn't
  defend "real infrastructure" abstractly. You went concrete: "the only two requirements
  are MCP servers for AI roles and credential rotation for takeover." You defined the
  minimal interface, not the maximal architecture.

- You caught that MCP isn't needed for human roles -- "it will prevent returning to AI"
  but humans use the tools natively. That kind of degradation-path thinking (the system
  works with partial AI support and expands as MCP coverage grows) is how you avoid
  blocking yourself on ecosystem dependencies.

- You pivoted from M365 to Nextcloud + Migadu, and then from raw Claude Agent SDK to
  Letta, both times for the same reason: reduce integration surface while keeping
  capabilities. You optimize for fewer moving parts, not more features.
