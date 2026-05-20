# Event Timeline

Agent-to-agent message timeline for debugging. Captures who said what to whom, when, and the surrounding context — enough that a failed run can be reconstructed without replaying it.

Parent: [../design.md](../design.md) · Spec: [../design/07-refinements.md](../design/07-refinements.md) T4-C

## Why this file matters

[t5-run-ledger.md](t5-run-ledger.md) records what was executed. This file records what happened **between** the agents — the message-passing trace that explains why the artifact looks the way it does (or why it didn't get produced). When the brief is weak in section X, the timeline shows whether that's because no agent worked on X, two agents fought over it, or the EM never delegated it.

## Format

One H2 per run. Entries are flat-table rows with monotonically increasing timestamps relative to run start.

Fields:
- `t+`: elapsed seconds from run start
- `from`: agent role (EM / A / B / R / system)
- `to`: agent role or `#team` / `DM-A-B` etc.
- `channel`: Nextcloud Talk room or DM
- `event`: short tag — `message`, `tool_call`, `file_write`, `task_assigned`, `block`, `idle`, `restart`, …
- `summary`: one-line summary; full text goes in the linked transcript file if needed

## Run 1 — 2-agent smoke

| t+ | from | to | channel | event | summary |
|----|------|----|---------|-------|---------|
| _empty_ | | | | | |

## Run 2 — 4-agent main spike

| t+ | from | to | channel | event | summary |
|----|------|----|---------|-------|---------|
| _empty_ | | | | | |

### Forced SPOF window (Run 2)

Mark the kill -9 + reconnect window inline in the table above using `system` as `from` and `restart` as event. Cross-reference [t5-run-ledger.md](t5-run-ledger.md) "Forced SPOF" section for the verdict.

## Capture method

Decide before Run 1 starts:

- [ ] Letta has a built-in message bus dump → use it
- [ ] Nextcloud Talk message export (per-room) → reconcile with agent action logs
- [ ] Manual logging from a side script that subscribes to the room(s)

Record the method here so the next run uses the same one.
