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
- Notes: AGPL-3.0 is a non-issue — Roster is itself AGPL-3.0 (see `LICENSE` at repo root), so license-compatibility concerns evaporate.

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

## Setup notes (for Week 1 spike)

When wiring cbcoutinho into the spike's `docker-compose.yml`:

- Use the AGPL Docker image (not the Astrolabe Cloud managed variant — keeps the spike self-contained).
- Auth: app-password per agent (one app password per agent user in Nextcloud). OAuth Login Flow v2 is overkill for the spike.
- Create the `#team` room and the per-pair DM rooms manually via Nextcloud admin or `occ talk:room:create` before the agents start (the provisioner work belongs to Week 2; for Week 1 manual setup is fine and feeds [t5-run-ledger.md](t5-run-ledger.md) "Run N setup" notes).

See [Official Nextcloud MCP Server proposal (nextcloud/server #53211)](https://github.com/nextcloud/server/issues/53211) for the upstream conversation about an official server — track it for Week 2-6 if cbcoutinho stalls.

## Network and ACL policy (contamination guard)

Enforces Layer 1 + Layer 2 of [t1-grading-rubric.md](t1-grading-rubric.md) "Contamination guard". Both policies MUST be in place before Run 1 begins; verify in [t5-run-ledger.md](t5-run-ledger.md) "Run N setup".

### Nextcloud Files folder ACLs

Two top-level folders with disjoint access:

| Folder | Read | Write | Contents |
|--------|------|-------|----------|
| `/agents/` | EM, Senior A, Senior B, Researcher | EM, Senior A, Senior B, Researcher | Working files, draft brief, internal notes, the produced [t8-sample-brief.md](t8-sample-brief.md) artifact (synced out at end of run) |
| `/founder/` | founder only | founder only | [t1-grading-rubric.md](t1-grading-rubric.md), comparator brief PDFs (if downloaded for offline reference), AI-panel review file, anything mentioning the rubric, dimensions, or scoring |

The four agent app-passwords MUST have **zero** permissions on `/founder/`. Verify via Nextcloud admin UI before Run 1: log in as each agent user, confirm `/founder/` is invisible. Record the verification in [t5-run-ledger.md](t5-run-ledger.md).

The Roster provisioner (Week 2 work) will encode this ACL structure as part of `roster up`; for Week 1 manual setup is fine.

### Researcher domain blocklist

The Researcher role is the only agent with web access (per design — EM, Senior Analysts do not fetch URLs directly). Block the following at the Researcher's tool layer or via an outbound HTTP proxy:

**Hard block (consulting firm primary domains):**

- `bcg.com`, `web-assets.bcg.com`, `bcghendersoninstitute.com`
- `mckinsey.com`, `mckinseyandcompany.com`
- `bain.com`, `media.bain.com`
- `strategyand.pwc.com`, `pwc.com/consulting` (Strategy&)
- `monitordeloitte.com`, `deloitte.com/insights/strategy`
- `rolandberger.com`
- `oliverwyman.com`
- `lek.com`
- `kearney.com`, `middleeast.kearney.com`

**Hard block (mirrors and archives of the above):**

- Any `web.archive.org/web/*/bcg.com/...` or similar archived consulting-firm URL
- SlideShare paths matching `slideshare.net/.../bcg-*`, `slideshare.net/.../mckinsey-*`, etc.
- `scribd.com` paths matching consulting-firm titles
- `documentcloud.org` paths matching consulting-firm titles

**Allow-list exception (gray zone):**

- `economysea.withgoogle.com` and `https://www.bain.com/insights/e-conomy-sea-*` — the Google-Temasek-Bain e-Conomy SEA report is the canonical SEA market-sizing source and is a published industry report (different genre than a market-entry brief). Allowing it loses the spike if it turns out the Researcher heavily templates from it; the post-spike verbatim check catches that.
- Trade press, news outlets, World Bank, IMF, government statistics offices, industry trade associations — all permitted.

**Enforcement:**

Pick the tightest option that the Researcher's tool surface supports:

1. **MCP-level allow-list / block-list** in the Researcher's tool definition — if the MCP server for web fetching supports per-tool URL filtering.
2. **Outbound HTTP proxy** (e.g., Squid) on the Docker network, configured with the blocklist; Researcher's HTTP_PROXY env var points at it.
3. **Last resort: trust + audit.** The Researcher self-reports every URL to [t5-researcher-urls.md](t5-researcher-urls.md); blocklist violations are caught at audit time, not at fetch time. Weakest control — contamination has already occurred by the time you read it.

For Week 1 spike, **prefer #2 (outbound proxy)**. Squid with a `dstdomain` ACL list takes ~30 minutes to configure.

### Verification checklist (before Run 1)

- [ ] `/founder/` invisible to all four agent accounts (tested by logging in as each).
- [ ] Researcher's outbound proxy is up and the blocklist is loaded.
- [ ] `curl -x http://squid:3128 https://www.bcg.com/` from the Researcher container returns 403 / blocked.
- [ ] `curl -x http://squid:3128 https://www.worldbank.org/` from the Researcher container returns 200 (allow-list still works).
- [ ] [t5-researcher-urls.md](t5-researcher-urls.md) is initialized and Researcher is wired to append to it on every fetch.
