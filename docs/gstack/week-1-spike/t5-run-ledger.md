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
- Letta agent IDs: EM=`agent-414ea769-19a5-4553-bc49-ab8fb828c5f1`, Researcher=`agent-92367e4d-faeb-4100-94f1-ead0d2e9690a`
- Agent tool counts: EM = 15 cbcoutinho (Talk + WebDAV) + 3 Letta base = 18. Researcher = 15 cbcoutinho (Talk + WebDAV, scoped to researcher user) + 2 researcher-web wrapper (web_search + web_scrape) + 3 Letta base = 20.
- Env manifest snapshot: see [t5-env-manifest.md](t5-env-manifest.md) "Run 1 — 2026-05-21"
- Started: _TBD — kicked off when first user message posts to EM agent_
- Ended: _TBD_
- Outcome: _success / partial / failure_
- Notes:

### Event log (Run 1)

| Timestamp | Actor | Event |
|-----------|-------|-------|
| 2026-05-21 22:XX UTC | operator | Pre-boot gates (pre-swap): prompt hashes match (EM + Analyst A), banned-token grep 0 hits, both Letta agents created with 15 MCP tools each. Superseded by post-swap row below. |
| 2026-05-22 00:XX UTC | operator | Run 1 swapped from EM+Analyst A to EM+Researcher (see header). Old agents deleted; new agents created with re-frozen prompts. Pre-boot gates re-passed: EM hash + Researcher hash both verify, banned-token grep 0 hits across 25 tokens, identity-isolated tool-exec probe (talk_send_message + nc_webdav_write_file) passes for both agents. |
| _TBD_ | operator | Kickoff message posted to EM agent |

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
