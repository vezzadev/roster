# MCP Investigation: Nextcloud Talk + Files

Investigation of community Nextcloud MCP servers and the build-vs-adopt decision for Week 1.

Parent: [../design.md](../design.md) · Spec: [../design/05-implementation.md](../design/05-implementation.md) Week 1 · [../design/07-refinements.md](../design/07-refinements.md) D4 + T4-B

## Why this file matters

Codex T4-B: "exists" is not enough. The investigation must answer **API coverage** and **room-management fit**, not just "is there a server in some registry". If no community server covers the operations the agents need, a ~3-day MVP build of a minimal Talk+Files MCP is the contingency. That contingency is what makes Week 1 likely overrun to 1.5-2 weeks.

## Required API surface

The agents need the following Nextcloud operations through MCP. Fill in as the spike defines them; do not invent capabilities the agents don't actually use.

### Talk

| Op | Used by | Notes |
|----|---------|-------|
| Create room (#team) | EM at spike start | Single team room |
| Create DM rooms (per-pair) | EM | Per-pair DMs for parallel work |
| Send message to room | All roles | |
| Read message history | All roles | |
| List rooms | All roles | |
| Add/remove participant | EM | For takeover/return flows (v2 — may not be needed in W1) |

### Files

| Op | Used by | Notes |
|----|---------|-------|
| Read file | All roles | |
| Write file | All roles | |
| List directory | All roles | |
| Create directory | EM | |
| Delete file | (probably not in W1) | |
| Share file with user | (probably not in W1) | |

## Candidates investigated

_(populate as you investigate; one H3 per candidate)_

### _candidate-name-here_

- Repo: _link_
- Last commit: _date_
- License:
- Stars / forks:
- Coverage matrix (against the table above): _✅ / ❌ per row_
- Room-management fit (one #team + per-pair DMs):
- Notes:

## Coverage matrix summary

| Candidate | Talk coverage | Files coverage | Room fit | Verdict |
|-----------|---------------|----------------|----------|---------|
| _empty_   |               |                |          |         |

## Decision

_Adopt / build MVP / hybrid_ — write the verdict here once the matrix is filled in. Include the date and the trigger that closed the decision.

If **build MVP**, the scope is the minimal subset of the Talk + Files tables above that the spike actually needs — not the full Nextcloud API.
