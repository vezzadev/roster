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

Survey conducted 2026-05-19. Re-verify before committing — the leading repo (cbcoutinho) is actively maintained and may have changed coverage since.

### cbcoutinho/nextcloud-mcp-server  (Python, AGPL-3.0) — **leading candidate**

- Repo: https://github.com/cbcoutinho/nextcloud-mcp-server
- Last commit: 2026-05-19 (actively maintained)
- Stars / forks: 231 / 40
- Coverage: 110+ tools across 10 Nextcloud apps. **Talk (spreed): 6 tools** — list conversations, read/post messages, mark as read, list participants. **Files (WebDAV): 12 tools** — full CRUD + OCR/document extraction.
- Room-management fit: **partial — supports messaging in existing rooms but no room-create/delete operation.** Rooms must be created out-of-band (e.g., by the provisioner during `roster up`, or manually via Nextcloud admin).
- Deployment: Docker image, Helm chart, multi-user OAuth via Login Flow v2, app-password auth. Managed hosted variant (Astrolabe Cloud) also available.
- Notes: AGPL-3.0 is fine for Roster since it runs as a separate container — the license does not infect the orchestration code that talks to it over MCP. Confirm AGPL compatibility with downstream users of Roster (most use cases are internal teams, no redistribution).

### Frisch12/nextcloud-mcp-server  (Go, no license) — **blocker: unlicensed**

- Repo: https://github.com/Frisch12/nextcloud-mcp-server
- Last commit: 2026-04-04
- Stars / forks: 0 / 0
- Coverage: claims 82 tools, 3 MB Docker image, multi-instance. Lists Talk (conversations, messages, participants) and Files (WebDAV + favorites + search) explicitly.
- Notes: **Unlicensed = legally unusable until upstream adds a license.** Attractive Go footprint and stated coverage breadth, but the license problem rules it out for Roster unless we open an issue and wait for resolution.

### Tier 2 candidates (partial / file-focused / no Talk)

| Repo | Lang | Stars | Last push | License | Talk? | Notes |
|---|---|---|---|---|---|---|
| hithereiamaliff/mcp-nextcloud | TS | 30 | 2026-03-14 | AGPL-3.0 | ❌ | Notes/Calendar/Contacts/Tables + WebDAV; TS rewrite of cbcoutinho |
| Monadical-SAS/nextcloud-mcp-server | Py | 9 | 2025-03-08 | none | ❌ | Read-only experiment, stale |
| Rello/nextcloud-dynamic-mcp-server | Py | 5 | 2026-04-03 | none | ❌ | Generic OCS bridge |
| abdullahMASHUK/nextcloud-mcp-server | TS | 4 | 2025-09-03 | MIT | ❌ | Files-focused |
| No-Smoke/nextcloud-mcp-comprehensive | Py | 2 | 2026-04-02 | AGPL-3.0 | ❌ | Notes/Tables/WebDAV/Deck/Cookbook/Contacts |
| StefanRichterHuber/nextcloud-mcp | Java | 0 | 2026-05-12 | MIT | ❌ | Files only |
| healdigital/nextcloud-mcp-server | TS | 0 | 2026-05-16 | none | ❌ | WebDAV + OCS shares |

Long tail of ~15 more <2-star hobby forks exists (Artemnikov, worph, PhoeNox, phildue, michielb, Jaypeg-dev, Yeamika, oliveiraigorm, miyo-hime/yakumo, scottnailon, JupiterBroadcasting fork, …) — none add Talk coverage beyond cbcoutinho.

### Wrappers worth knowing (if MVP build is needed)

1. **nextcloud/spreed** (PHP, AGPL, 2.1k stars) — Talk's source. The authoritative OCS Talk API spec lives in `docs/`. Reference if implementing room-create from scratch.
2. **CrazyShipOne/nextcloud_talk_pybot** (Py, MIT, 14 stars, last push 2026-03) — small clean Python Talk client; good reference for chat send/receive/long-poll.
3. **gary-kim/go-nc-talk** (Go, Apache-2.0, 12 stars) — Go Talk client library, mature room/message coverage.
4. For Files: Python `webdavclient3`, `pyocclient`, or Nextcloud's own `nc-py-api` (official, ExApp-oriented but works standalone). No LangChain/LlamaIndex first-class Nextcloud loader exists beyond generic WebDAV.

## Coverage matrix summary

Against the API surface defined above:

| Candidate | Talk msg read/write | Talk room create | Talk DM | Files CRUD | Files share | Verdict |
|-----------|--------------------:|-----------------:|--------:|-----------:|------------:|---------|
| cbcoutinho/nextcloud-mcp-server | ✅ | ❌ (provision out-of-band) | ✅ (via existing rooms) | ✅ | ✅ | **ADOPT** |
| Frisch12/nextcloud-mcp-server | ✅ (claimed) | ✅ (claimed) | ✅ (claimed) | ✅ (claimed) | ? | blocked (no license) |
| All others | ❌ | ❌ | ❌ | ✅ partial | partial | n/a — no Talk |

## Decision

**Decision (2026-05-19, pre-spike): ADOPT cbcoutinho/nextcloud-mcp-server.**

Rationale:
1. AGPL-3.0 + actively maintained (today) + Talk + Files in one server is the unique combination in the survey.
2. The one gap (room create) is solvable out-of-band: the Roster provisioner creates `#team` and per-pair DM rooms during `roster up` using the Nextcloud Talk OCS API directly (no MCP needed for setup ops since the provisioner has admin creds). The agents only need send/read on existing rooms, which cbcoutinho covers.
3. **Skip the 3-day MVP build** that the design anticipated as a contingency. Save the 3 days for Week 2-6 work or as buffer for Week 1 overrun.

Carryforward risks:
- If during the spike cbcoutinho's Talk coverage proves insufficient for an unanticipated operation, fall back to: (a) PR upstream (cheaper than a parallel server), or (b) build a thin MCP MVP for just the missing op.
- AGPL: confirm Roster's downstream distribution model accommodates it. For internal-team usage (the v1 target), this is a non-issue.

## Setup notes (for Week 1 spike)

When wiring cbcoutinho into the spike's `docker-compose.yml`:

- Use the AGPL Docker image (not the Astrolabe Cloud managed variant — keeps the spike self-contained).
- Auth: app-password per agent (one app password per agent user in Nextcloud). OAuth Login Flow v2 is overkill for the spike.
- Create the `#team` room and the per-pair DM rooms manually via Nextcloud admin or `occ talk:room:create` before the agents start (the provisioner work belongs to Week 2; for Week 1 manual setup is fine and feeds [run-ledger.md](run-ledger.md) "Run N setup" notes).

See [Official Nextcloud MCP Server proposal (nextcloud/server #53211)](https://github.com/nextcloud/server/issues/53211) for the upstream conversation about an official server — track it for Week 2-6 if cbcoutinho stalls.
