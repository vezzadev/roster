# Run Ledger

Timestamped events per spike run + prompt hashes + agent versions + outcomes. Source of truth for what was actually executed.

Parent: [../design.md](../design.md) · Spec: [../design/05-implementation.md](../design/05-implementation.md) Week 1 · [../design/07-refinements.md](../design/07-refinements.md) T4-D

## Why this file matters

Codex T4-D: without a frozen prompt + recorded version per run, the experiment is irreproducible. Any prompt change after a run begins requires a new numbered run. This file is the matrix.

## Run matrix

| Run # | Type | Agents | Time cap | Prompt hashes (EM / A / B / R) | Letta ver | Nextcloud ver | Model(s) | Started | Ended | Outcome |
|-------|------|--------|----------|--------------------------------|-----------|---------------|----------|---------|-------|---------|
| 1     | 2-agent smoke (ablation, post-swap) | EM + Researcher | 1h hard cap | | | | | | | |
| 2     | 4-agent main spike | EM + A + B + Researcher | none (target same day) | | | | | | | |

## Run 1 — 2-agent smoke (1h cap)

**Purpose:** ablation diagnosability — if Run 2 fails, 2-agent control localizes failure to collaboration overhead vs prompt design vs tool friction. **Run 1's brief is diagnostic, not rubric-gradable** — the rubric is calibrated for the 4-agent main run.

**Pairing (post-swap):** EM + Researcher. The original plan paired EM + Senior Analyst A but was swapped pre-kickoff to EM + Researcher so the spike's web-fetch surface + contamination guard get exercised live before Run 2. The analyst-synthesis loop is deferred to Run 2 where analysts have peers to collaborate with. See [t5-system-prompts.md](t5-system-prompts.md) Change log 2026-05-21 "Pre-Run 1 (post-swap)" for the rationale and the minimal prompt edits that made both EM and Researcher prompts role-generic enough to support the 2-agent variant.

- Prompts frozen at hash: EM=`e966a65548025d0dfe65ac52a24e4a855ec103de3a2223a966757f304f0ad40f` R=`2fff77b9103e233e7a7eea4728e90d668a42fd3e9e3d402c6ac7a86d29435d24`
- Contamination grep: 0 hits across 25 banned tokens for both prompts (verified pre-boot by `spike-compose/wire-run-1.py` with word-boundary regex)
- Letta architecture: **one Letta container per agent** — `letta-em` (127.0.0.1:8283) and `letta-researcher` (127.0.0.1:8284), each with the role's MCP sidecars registered only on its own Letta. See "Letta tool-namespace finding" below for why.
- Letta agent IDs (per-agent Letta architecture): EM=`agent-0a9bce41-6b16-4db8-88fe-150ffd255ad6` on `letta-em`, Researcher=`agent-b4a10f8f-ce23-4ebd-a3c1-39d4af6ec7e8` on `letta-researcher`. The earlier singleton-Letta IDs (`agent-414ea769…` EM, `agent-92367e4d…` Researcher) are retired — see finding below.
- Agent tool counts: EM = 15 cbcoutinho (Talk + WebDAV) + 3 Letta base = 18. Researcher = 15 cbcoutinho (Talk + WebDAV, scoped to researcher user) + 2 researcher-web wrapper (web_search + web_scrape) + 3 Letta base = 20.
- Env manifest snapshot: see [t5-env-manifest.md](t5-env-manifest.md) "Run 1 — 2026-05-21"
- Started: 2026-05-22 00:31:23 UTC (founder posted `Begin the engagement.` to EM agent on letta-em; EM responded with 18-message turn, posted kickoff brief to `#team` as actor `em` at 00:32:22 UTC)
- Ended: _TBD — 1h cap → 01:31 UTC_
- Outcome: _success / partial / failure_
- Notes:
  - EM oriented itself before sending the brief: `talk_list_participants` (vzyiva4u) → `nc_webdav_list_directory` (/agents) → `talk_list_conversations` → file-backed working notes at `/agents/_em-notes.md` → kickoff post to `#team`. Identity isolation confirmed at the tool-return layer (`actorId: em` echoed back).
  - **Memory blocks absent**: EM's first attempt at `memory_insert(label="human")` errored with `Block field human does not exist (available sections = ())`. The agents were created via `POST /v1/agents/` with `tool_ids` + `include_base_tools=true` but without explicit memory blocks; Letta apparently no longer ships default `human` / `persona` blocks. EM fell back to file-based notes in `/agents/_em-notes.md`, so the run is not blocked. Follow-up for Run 2 wiring is captured in "Follow-ups before Run 2" below.
  - **Analyst-A ghost in `#team`**: the spike-compose snapshot lists `em + analyst-a + researcher` as `#team` members from the pre-swap setup. The new EM agent saw analyst-a in `talk_list_participants` output and stated it would treat Analyst A as a teammate (DM expected via `EM-A` room token `eg72sheb`). Decision: _see Event log row "Analyst-A presence" below_.

### Follow-ups before Run 2

- **Add default memory blocks to agent creation in `wire-run-1.py`.** Letta 0.16.8 no longer ships default `human` + `persona` blocks; `memory_insert(label="human", …)` errors with `Block field human does not exist (available sections = ())`. Run 2 agents (Analyst A + Analyst B in particular) will likely lean on memory blocks more than Run 1's EM did — file-backed notes are an OK fallback for one synthesis agent but get awkward across four. Action: extend the `POST /v1/agents/` payload in `wire-run-1.py` with an explicit `memory_blocks` list defining at least `human` and `persona`, OR call `POST /v1/agents/<id>/core-memory/blocks` after agent create. Verify by re-running the agent-driven probe and asserting `memory_insert` succeeds.
- **Reconcile #team room membership before Run 2 reuses the same Nextcloud.** Run 1 removed `analyst-a` from `#team` (token `vzyiva4u`). For Run 2 add analyst-a back **and** add the new `analyst-b` user; verify all four agent actors are listed by `talk_list_participants(vzyiva4u)`. Same for the per-pair DM rooms (`EM-A`, `EM-B`, `A-B`, `A-Researcher`, `B-Researcher`).
- **`spike-compose/driver.py` runtime files.** `driver.log` and `driver-state.local` accumulate per-run; truncate or rotate before Run 2 so the state file doesn't start tick 1 already-advanced past prior messages.

### Event log (Run 1)

| Timestamp | Actor | Event |
|-----------|-------|-------|
| 2026-05-21 22:XX UTC | operator | Pre-boot gates (pre-swap): prompt hashes match (EM + Analyst A), banned-token grep 0 hits, both Letta agents created with 15 MCP tools each. Superseded by post-swap row below. |
| 2026-05-22 00:XX UTC | operator | Run 1 swapped from EM+Analyst A to EM+Researcher (see header). Old agents deleted; new agents created with re-frozen prompts. Pre-boot gates re-passed: EM hash + Researcher hash both verify, banned-token grep 0 hits across 25 tokens, identity-isolated tool-exec probe (talk_send_message + nc_webdav_write_file) passes for both agents via the **per-server execute endpoint** `POST /v1/mcp-servers/<sid>/tools/<tid>/run`. |
| 2026-05-22 00:1X UTC | operator | Founder posted `Begin the engagement.` to EM agent on the singleton Letta. EM's call to `talk_send_message` landed on the Researcher's MCP container — the brief was published to `#team` as actor `researcher`. **Letta tool-namespace finding** (below) identified. Re-kickoff postponed; per-agent Letta architecture work begun. |
| 2026-05-22 00:2X UTC | operator | Per-agent Letta architecture live: `letta-em` + `letta-researcher` each holding their own MCP registrations. Singleton `letta` container + `letta_data` volume destroyed. New agents created (EM=`agent-0a9bce41…`, Researcher=`agent-b4a10f8f…`). Hash + banned-token gates re-passed. **Agent-driven probe passes**: EM's `talk_send_message` posts as actor `em`, Researcher's as `researcher`; both `/agents/<role>-ping.txt` files written. |
| 2026-05-22 00:31:23 UTC | operator | Founder posted `Begin the engagement.` to EM agent (`agent-0a9bce41…` on letta-em). 62.5s response. EM orientation pass + kickoff brief published to `#team` at 00:32:22 UTC as actor `em` (HTTP 200, message id 253). |
| 2026-05-22 00:32:22 UTC | em (agent) | Kickoff brief posted to `#team`. Working notes initialized at `/agents/_em-notes.md`. |
| 2026-05-22 00:33:00 UTC | operator | Removed `analyst-a` from `#team` participants (`occ talk:room:remove vzyiva4u analyst-a`) to keep the Run 1 ablation clean — EM had inferred A would be on the team from the participant list. |
| 2026-05-22 00:34:25 UTC | operator | Posted clarification to EM agent: "the only teammate you have is the Researcher. Both Senior Analysts are unavailable for this run — cover their depth threads yourself." 117s response: EM updated `/agents/_em-notes.md`, posted team-composition correction to `#team` (msg id 255), sent detailed first sourcing batch to Researcher in `EM-Researcher` (msg id 256), drafted skeleton at `/agents/_em-outline.md`, polled `EM-Researcher` for a reply (none), and paused. |
| 2026-05-22 00:39:37 UTC | operator | **Started `spike-compose/driver.py` relay** — polls `#team` + `EM-Researcher` every 30s via admin OCS and wakes the right per-agent Letta with a digest of new messages. State at `driver-state.local`; events at `driver.log`. **v1 will replace this with the [`vezzadev/letta-mcp-channel`](https://github.com/vezzadev/letta-mcp-channel) generic MCP channel plugin** for Letta Code — push-based: agents receive Nextcloud notifications/resources/updates as inbound MCP messages and reply via native MCP tools. The spike driver is a synchronous-polling stand-in until that wires up. |
| _TBD_ | operator | Run 1 outcome captured at 1h cap (01:31:23 UTC) or earlier on `/agents/brief.md` declared final by EM. |

## Letta tool-namespace finding (pre-Run-1, 2026-05-22)

**Symptom.** Founder posted `Begin the engagement.` to the EM agent. EM reasoned correctly, produced an Indonesia-market kickoff brief, and called `talk_send_message(token="vzyiva4u", message="<brief>")`. The brief landed in `#team` but as actor `researcher`, not `em`. The Founder-facing chat in `EM-Researcher` showed nothing.

**What we expected.** Each agent's MCP sidecar (`nextcloud-mcp-em`, `nextcloud-mcp-researcher`) authenticates to Nextcloud as a different user via its own app token. So a `talk_send_message` call routed to the EM sidecar appears as `em`; routed to the Researcher sidecar appears as `researcher`. Identity isolation lives in the sidecar/MCP boundary.

**What we found.** Letta dedupes MCP tool names **globally within a Letta instance**, not per MCP server. Both sidecars expose a tool named `talk_send_message`. When Letta registered the second sidecar, it kept one `tool_id` for that name and bound it to whichever MCP server was registered **last** — `nextcloud-researcher` in our case. Both agents in the singleton Letta saw the same `tool_id` in their `tool_ids` list. So when the EM agent's reasoning produced the JSON tool call `{"name": "talk_send_message", …}`, Letta resolved it via the global `tool_id` and dispatched to `nextcloud-researcher`, which authenticated to Nextcloud as `researcher`.

**Why the earlier probe missed it.** The original `probe-tools.py` invoked tools via the per-server execute endpoint `POST /v1/mcp-servers/<server_id>/tools/<tid>/run`. That URL carries the server ID explicitly, so Letta routes by URL — not by global `tool_id` lookup. The probe always hit the right sidecar by URL construction, and passed. It told us nothing about the agent-driven path the real run takes.

**Fix.** Per-agent Letta containers, one per agent, with each role's MCP sidecars registered **only on that role's Letta**. Tool-name collisions then sit in separate Letta databases and cannot collapse. Compose changes:

- `letta` → `letta-em` (8283) + `letta-researcher` (8284). Each gets its own `letta_<role>_data` volume + the `url_validation.py` SSRF-guard patch bind-mount.
- `nextcloud-mcp-em` registered only on `letta-em`; `nextcloud-mcp-researcher` + `researcher-web` registered only on `letta-researcher`.
- `spike-compose/wire-run-1.py` extended with a per-role `letta_url`; the script POSTs MCPs and creates the agent against the role's own Letta.
- `spike-compose/probe-tools.py` rewritten to use the agent-driven path (POST `/v1/agents/<id>/messages` with a prompt asking for the tool call) instead of the per-server execute endpoint, so future regressions don't slip past.
- Letta stubs for `letta-analyst-a` (8285) + `letta-analyst-b` (8286) commented into `docker-compose.yml`, ready for Run 2.

**Verification (2026-05-22).** Post-fix agent-driven probe:

| Agent | Letta | `talk_send_message` actor | `/agents/<role>-ping.txt` |
|-------|-------|---------------------------|---------------------------|
| em (`agent-0a9bce41…`) | letta-em (8283) | `em` ✓ | `/agents/em-ping.txt` ✓ |
| researcher (`agent-b4a10f8f…`) | letta-researcher (8284) | `researcher` ✓ | `/agents/researcher-ping.txt` ✓ |

**Carryover implications.**
- The polluted `#team` history (one researcher-attributed kickoff brief + two pairs of probe messages) is left in place as evidence of the bug — to be considered for cleanup before re-kickoff if it would confuse the EM agent's view of #team. The new EM agent is created fresh with no memory; it will only encounter the polluted history if/when it queries `talk_get_messages`.
- The `t5-env-manifest.md` row for `Letta server` originally listed a single container; updated to reflect two per-agent Letta containers (same image/digest, different volumes + ports).
- Pattern to take forward into v1: enforcing per-agent Letta is the structural fix. Inside a single Letta, MCP tool names from different servers collide via global `tool_id`. There is no per-MCP namespacing in Letta's current model. If we later need many agents on one Letta for resource reasons, this needs to be reopened upstream (Letta tool-id allocation per MCP-server scope).

## Run 2 — 4-agent main spike

**Purpose:** the gating artifact for SC#5.

- Prompts frozen at hash: _EM=____ A=____ B=____ R=____
- Env manifest snapshot: see [t5-env-manifest.md](t5-env-manifest.md) as of start time
- Started:
- Ended:
- Outcome: _artifact produced / partial / no artifact_
- Forced SPOF event triggered at: _timestamp (see [t5-event-timeline.md](t5-event-timeline.md) and the SPOF section below)_
- Notes:

### Event log (Run 2)

| Timestamp | Actor | Event |
|-----------|-------|-------|
| _empty_ | | |

### Forced SPOF (kill -9 Letta server)

Per D7 + T6: one forced `kill -9` of the Letta server container mid-flight to observe reconnect / catch-up behavior.

- Triggered at: _timestamp_
- Pre-kill agent state:
- Post-kill behavior observed (reconnect time, catch-up summary correctness, lost actions):
- Verdict: _clean recovery / partial / data loss_

## Additional runs (if any)

If Run 2 fails and a new prompt freeze is needed, append Run 3 here. Do not edit Run 2's frozen hash — start a new row.
