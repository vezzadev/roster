# T5' — OpenClaw run ledger

Parent: [README.md](README.md) §T5'

Mirrors [../week-1-spike/t5-run-ledger.md](../week-1-spike/t5-run-ledger.md):
numbered runs, **prompt freeze per run**, hash-pinned config, hard caps,
artifact links. Row format identical to Week 1 so the AI panel can compare
runs across runtimes apples-to-apples.

Status: ⏳ not started — gated on
[t4-openclaw-mcp-fidelity.md](t4-openclaw-mcp-fidelity.md) pass +
[t9-otel-parity.md](t9-otel-parity.md) pass.

## Pre-flight readiness (G-list, mirrored from Week 1's G-1…G-8)

| Gate | Check | Status |
|---|---|---|
| G'-1 | OpenClaw pinned ≥ 2026.1.29 (CVE-2026-25253 patched) | ⏳ |
| G'-2 | OTel parity validated per T9' acceptance test | ⏳ |
| G'-3 | MCP fidelity check passed per T4' | ⏳ |
| G'-4 | Frozen prompts hashed + committed (same hashes as Week 1 modulo channel-tool name swaps) | ⏳ |
| G'-5 | Per-agent workspace seeded — AGENTS.md, SOUL.md, MEMORY.md, HEARTBEAT.md, TOOLS.md per agent | ⏳ |
| G'-6 | Anthropic auth wired (decide API-key vs OAuth — open question #5 in [README.md](README.md)) | ⏳ |
| G'-7 | Nextcloud Talk rooms created (one #team + per-pair DMs, same topology Week 1 used) | ⏳ |
| G'-8 | Cost budget alert set at the Anthropic console level (not just OpenClaw config — F-O5 mitigation) | ⏳ |

No run kicks off until all G'-gates are ✅.

## Run matrix

| Run | Goal | Agents | Models | Hard cap | Status |
|---|---|---|---|---|---|
| 1' — 2-agent smoke | Validate end-to-end happy path under OpenClaw before scaling up | EM + Researcher | Opus 4.7 + Sonnet 4.6 | 45 min | ⏳ |
| 2' — 4-agent main | SC#5 artifact run; produces the brief that goes to the AI panel | EM + Senior A + Senior B + Researcher | Opus 4.7 + Sonnet 4.6 × 3 | 2h | ⏳ |

Re-run policy: if Run 2' halts on a *fixable* runtime/infra bug (per the
run-failure recovery policy stored in operator memory — autonomously fix +
restart for straightforward fixes, halt + surface for upstream/non-trivial
ones), apply that policy. If it halts on an upstream OpenClaw bug, file a
finding row in this ledger, halt, and surface.

## Row template (filled in post-run)

```
### Run X' — <name>

| | |
|---|---|
| Started | <UTC timestamp> |
| Stopped | <UTC timestamp> |
| Wall    | <duration> |
| Config  | <env vars + hashes> |
| Agents  | <model + tools per agent> |
| Talk    | <room IDs, fresh vs reused> |
| Output  | <artifact paths> |
| Cost    | <total $ + cache hit rate + per-agent breakdown via kql/03-per-agent-cost.kql> |
| Outcome | success / partial / halt + one-line reason |

**Course of run.** <prose narrative of what happened, mirroring Week 1's style>

**Findings (F-O…).** Numbered, each linking the upstream bug or design issue.

**Driver/runtime behavior.** Heartbeat firing pattern, immediate-wake count if supported, orphan-call count.
```

## Findings log (F-O…)

Numbered in discovery order, mirroring Week 1's F-1…F-8 numbering for the
Letta side. F-O prefix to keep them visually distinct.

(none yet)

## Forced SPOF (T6')

During Run 2', `kill -9` one OpenClaw Gateway mid-flight. Observe and record
here:

- File-backed state survives restart? (expected yes)
- Heartbeat resumes cleanly? (timing in seconds from process up to first wake)
- Outstanding MCP tool calls — orphaned, retried, or cancelled? (this is the
  big question — Letta's were postgres-orphaned and uncancellable per Week 1)
- Talk-room re-sync — does the agent re-read messages received during downtime?

Land verdict here as a sub-section once executed.

## Cross-references

- Week 1 ledger conventions: [../week-1-spike/t5-run-ledger.md](../week-1-spike/t5-run-ledger.md)
- Frozen prompts source: [../week-1-spike/t5-system-prompts.md](../week-1-spike/t5-system-prompts.md)
- Per-run conclusion file template: [../week-1-spike/t5-run-1-conclusions.md](../week-1-spike/t5-run-1-conclusions.md)
