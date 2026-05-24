# Run 1' — open questions to characterize during the run

## OQ-1: Does `tools.byProvider.<id>: { allow: [] }` actually hide that MCP from an agent?

**Observed (2026-05-23 23:48 UTC):** Health-check turn for EM (configured with
`nextcloud-em.allow=["*"]`, `nextcloud-researcher.allow=[]`,
`researcher-web.allow=[]`) returned a reply asserting it could see both
`nextcloud-em__*` and `nextcloud-researcher__*` tools (the researcher's MCP
was supposed to be hidden).

**Caveat:** model self-introspection may be unreliable. Confirm during Run 1'
by:
- Inspecting an actual `toolDefinitions` array on a turn.
- Watching whether EM ever invokes `nextcloud-researcher__*` or vice versa.

**If broken:** per-agent identity isolation in OpenClaw v2026.5.20 cannot be
enforced via `byProvider` alone — would need either (a) separate gateway
processes per agent, or (b) gating at the MCP-server layer (different auth
per agent identity). This is a structural finding for the spike.

## OQ-2: EM writes artifacts to `/agents/` at container root, not its workspace mount

**Observed (2026-05-23 23:53 UTC):** EM created `/agents/_draft_brief_v1.md`
and `/agents/_working_notes.md` at the container root, even though its
workspace mount is `/workspace/em` and `AGENTS.md` lives there. The host
volume `./agents/em` never received these writes — they exist only inside
the ephemeral container fs.

**Likely cause:** AGENTS.md / BOOTSTRAP.md don't explicitly anchor the agent
to `/workspace/em` for all artifact paths. The model invented `/agents` as
a parallel to `agents/` (the host directory) and OpenClaw's filesystem tool
created the dir without complaint.

**Two distinct issues here:**
1. **Persona/prompt:** anchor BOOTSTRAP.md on the workspace path.
2. **Tool boundary:** OpenClaw's fs tool doesn't sandbox writes to the
   workspace dir — it'll write anywhere the container user can. That's a
   hardening gap (or at minimum a config the spike should set).

**Mitigation in-flight:** background loop snapshots `/agents/*` every 60s
during the run; kickoff teardown also explicitly `docker cp`s `/agents`.
Future runs need the prompt fix + a filesystem sandbox config.

## OQ-3: EmbeddedAttemptSessionTakeoverError after auto-compaction

**Observed (2026-05-23 23:55 UTC):**
```
[agent/embedded] embedded run auto-compaction start: reason=overflow
[agent/embedded] embedded run auto-compaction complete: compactionCount=1 willRetry=true
[agent/embedded] compaction retry aggregate timeout (60000ms): proceeding with pre-compaction state
[diagnostic] lane task error: lane=main error="EmbeddedAttemptSessionTakeoverError: session file changed while embedded prompt lock was released: /root/.openclaw/agents/em/sessions/<sid>.jsonl"
```

OpenClaw released the prompt lock during compaction; another lane (probably
heartbeat-driven) wrote to the same session jsonl in the gap. Result: the
compacted state was discarded, run continued on the pre-compaction state.

**Implication:** every auto-compaction in OpenClaw v2026.5.20 risks losing
work if any other lane writes the session during the compaction window. For
multi-lane agents (heartbeat + main + reminders), this is structural.

**Action:** characterize during Run 1' — does it recur? does EM lose
meaningful state? File upstream after run if reproducible.
