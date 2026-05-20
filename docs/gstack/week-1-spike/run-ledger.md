# Run Ledger

Timestamped events per spike run + prompt hashes + agent versions + outcomes. Source of truth for what was actually executed.

Parent: [../design.md](../design.md) · Spec: [../design/05-implementation.md](../design/05-implementation.md) Week 1 · [../design/07-refinements.md](../design/07-refinements.md) T4-D

## Why this file matters

Codex T4-D: without a frozen prompt + recorded version per run, the experiment is irreproducible. Any prompt change after a run begins requires a new numbered run. This file is the matrix.

## Run matrix

| Run # | Type | Agents | Time cap | Prompt hashes (EM / A / B / R) | Letta ver | Nextcloud ver | Model(s) | Started | Ended | Outcome |
|-------|------|--------|----------|--------------------------------|-----------|---------------|----------|---------|-------|---------|
| 1     | 2-agent smoke (ablation) | EM + Senior Analyst A | 1h hard cap | | | | | | | |
| 2     | 4-agent main spike | EM + A + B + Researcher | none (target same day) | | | | | | | |

## Run 1 — 2-agent smoke (1h cap)

**Purpose:** ablation diagnosability — if Run 2 fails, 2-agent control localizes failure to collaboration overhead vs prompt design vs tool friction.

- Prompts frozen at hash: _EM=____ A=____
- Env manifest snapshot: see [env-manifest.md](env-manifest.md) as of start time
- Started: _TBD_
- Ended: _TBD_
- Outcome: _success / partial / failure_
- Notes:

### Event log (Run 1)

| Timestamp | Actor | Event |
|-----------|-------|-------|
| _empty_ | | |

## Run 2 — 4-agent main spike

**Purpose:** the gating artifact for SC#5.

- Prompts frozen at hash: _EM=____ A=____ B=____ R=____
- Env manifest snapshot: see [env-manifest.md](env-manifest.md) as of start time
- Started:
- Ended:
- Outcome: _artifact produced / partial / no artifact_
- Forced SPOF event triggered at: _timestamp (see [event-timeline.md](event-timeline.md) and the SPOF section below)_
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
