# Architecture

Parent: [../design.md](../design.md)

## System Diagram

```
roster.yaml (canned template)
         |
         v
    Roster CLI
    roster up / down / takeover / return / status
         |
    Docker Compose
         |
    +----+----+----+----+
    |    |    |    |    |
    v    v    v    v    v

Nextcloud     Migadu      Letta Server      Agent Containers
(workspace)   (email)     (runtime)         (one per role)
- Talk        - SMTP/IMAP - Memory          - Engagement Manager
- Files       - Spam      - Channels        - Senior Analyst
- Wiki        - $19/mo    - Lifecycle       - Senior Analyst
- Calendar                                  - Researcher
- Tasks
- Mail UI

Agent <-> Nextcloud: MCP tools (v1: Talk + Files only; Wiki, Calendar, Deck deferred)
Agent <-> Email: IMAP/SMTP via Migadu (credential = Migadu app password, rotated on takeover)
Agent <-> Agent: Nextcloud Talk (visible to humans during takeover)
Human takeover: credential rotation on Nextcloud + Migadu (hard revocation)
v1 networking: localhost only (http://localhost:8080), real DNS deferred to v2
```

## Takeover Flow

Ordering (revised by /plan-ceo-review 2026-05-18): the Letta agent is stopped FIRST
so that even if downstream credential rotation partially fails, the agent cannot act.
This satisfies the *runtime-containment* portion of Premise 3 -- the agent cannot
issue NEW actions -- but does NOT undo prior exfiltration. See Premise 3 reframe in
[07-refinements.md](07-refinements.md) (Codex tension A).

```bash
$ roster takeover em

# 1. STOP agent's Letta agent instance (runtime kill switch — immediate)
# 2. Disable agent's Nextcloud app password
# 3. Revoke agent's Migadu app password
# 4. Generate temporary human credentials
# 5. Print single access URL

# Atomicity: if any of steps 2-3 fails, roster retries with exponential backoff
# (3 attempts). If still failing, prints "PARTIAL: credentials in service X are
# still active but the Letta agent is STOPPED — re-run `roster takeover em` to
# retry credential rotation, or proceed knowing the agent cannot use them."
# The runtime stop in step 1 is the hard guarantee; cred rotation is the
# defense-in-depth follow-up.

You are now the Engagement Manager. All services at one URL:
  http://localhost:8080          # (custom domain in v2)
  Login: em
  Temporary password: ********  (expires in 8h)

Run `roster return em` when done.
```

**Nextcloud-as-IDP path (Week 1 research item):** If Nextcloud's [oidc Identity Provider
app](https://apps.nextcloud.com/apps/oidc) can act as an OIDC IDP that other services
(future Letta, future Slack, future Archestra) federate against, takeover collapses to
"revoke the OIDC session" — atomic by design. Migadu's IMAP/SMTP doesn't speak OIDC
(would need OAUTH2 SASL support, requires verification), so Migadu app passwords likely
remain a separate auth domain in v1. Long-term path: replace Migadu with Nextcloud Mail
(federated through Nextcloud's IDP) to collapse auth domains; not in v1 scope.

## Key Implementation Work

1. **Roster CLI commands:** init, up, down, takeover, return, status
2. **Docker Compose generator:** from template to running services
3. **Nextcloud provisioner:** create users, app passwords, Talk rooms, shared folders
4. **Migadu provisioner:** create mailboxes via Admin API
5. **Letta agent definitions:** per-role system prompts, tools, memory config (~2 weeks)
6. **MCP server for Nextcloud (v1: Talk + Files only):** investigate existing community
   MCP servers first. If none exist, build minimal wrappers for Talk (send/read messages)
   and Files (read/write/list). Defer Collectives, Calendar, and Deck to v1.1.
7. **Credential rotation:** takeover/return flows with hard revocation
8. **Module rename:** `github.com/pedropaulovc/go-project` -> appropriate roster path,
   `cmd/myapp` -> `cmd/roster`

## Agent Execution Model

Agents are event-driven via Letta's message processing loop:
- **Trigger:** Nextcloud Talk messages (via polling or webhook), scheduled intervals, or
  explicit task assignment from another agent
- **Processing:** Agent receives context, reasons about next action, calls MCP tools
- **Output:** Messages to Talk, file writes, email sends -- all through real infrastructure
- **Idle behavior:** Agents check for new messages/tasks on a configurable interval
  (default: 30s). No continuous token burn when idle.

## Agent Catch-up After `roster return`

Catch-up design (revised by /plan-ceo-review 2026-05-18): no Roster-side
summarization pipeline. The Roster CLI injects a single short directive into the
agent's Letta core memory, and the agent uses its existing MCP tools to read what it
needs.

When a human returns a role to AI via `roster return <role>`:
1. Roster CLI restarts the Letta agent instance (it was stopped during takeover).
2. Roster CLI injects a single core-memory directive of the form:
   `"You were substituted by a human for X hours from t0 to t1. Before resuming any
   normal work, use your MCP tools (chat history, files activity, email list) to
   catch up on what happened during your absence."`
3. Agent processes that directive on its next message-handling cycle and pulls
   whatever context it deems relevant via its existing tools.

**Why this shape:**

- No Haiku-summarization dependency; no recursive summarization for long takeovers.
- Adapts to context budget naturally — the agent retrieves what fits.
- Uses tools the agent already has for normal operation; no new code paths.
- If Letta's WS to the server is down at return time, the directive injection is
  retried with exponential backoff; if persistent, `roster return` aborts with a
  clear error (Premise 3 stance: better to fail loudly than silently resume blind).

## Failure Modes

- **Partial provisioning (`roster up`):** If Nextcloud provisions but Migadu API fails,
  roster logs the partial state and offers `roster up --retry` to resume from the failed
  step. No automatic rollback -- partial state is useful for debugging.
- **Agent crash:** Docker Compose restart policy (`unless-stopped`) handles container
  crashes. Letta memory persists across restarts. Agent catches up on missed messages.
- **Migadu unavailable during takeover:** Revised by /plan-ceo-review 2026-05-18.
  Takeover ALWAYS stops the Letta agent first (runtime kill switch). If Migadu
  credential revocation then fails (e.g., Migadu unreachable), roster retries with
  exponential backoff 3x. On persistent failure: prints "PARTIAL: Migadu credentials
  still active but Letta agent is STOPPED — re-run `roster takeover` to retry." Premise
  3 holds because the agent cannot use any credentials while stopped.
- **Nextcloud unavailable:** `roster status` reports health of each service. Agents pause
  and buffer actions until Nextcloud recovers (Letta handles message buffering — verify
  this claim empirically in Week 1 validation).
- **`roster return` partial catch-up:** Per the revised catch-up design, the Roster CLI
  no longer pre-summarizes. If any MCP tool the agent uses for catch-up fails, the
  agent surfaces that error to its #team room (per the API-error handling decision
  below) and proceeds with whatever context it could fetch.

### Agent-side error catalog (added by /plan-ceo-review 2026-05-18)

Every agent-side codepath that calls an external service has a defined error response:

| Codepath | Failure | Response |
|---|---|---|
| OpenRouter API call | 429 rate limit | Letta retries with exponential backoff; on final failure, agent posts to #team: "Rate-limited, pausing 5 minutes," logs to per-agent error log in roster state dir |
| OpenRouter API call | 5xx / timeout | Same backoff + Talk surface as above |
| Model response (via OpenRouter) | Malformed JSON in tool call | Agent posts: "Received malformed tool call response, retrying once" + logs |
| Model response (via OpenRouter) | Refusal ("I cannot...") | Agent posts: "Model refused to act on this task — needs human input"; pauses on this work item |
| OpenRouter | Upstream Anthropic outage (502/503 surfaced by OR) | Treat as 5xx/timeout above; if persistent past 10 min, optionally route to a fallback OpenRouter model — operator decision recorded in run-ledger |
| MCP tool call | Timeout | Retry once with backoff; if persistent, post to #team and skip this tool call |
| MCP tool call (Files write) | Server 500 | Re-read file to detect partial write; post to #team if state ambiguous |
| Letta server WebSocket | Disconnect | Local headless container auto-reconnects (Letta-side concern); Roster CLI surfaces "agent X temporarily unreachable" via `roster status` |
| Catch-up directive injection | Letta server unreachable | Retry with backoff; if persistent, `roster return` aborts with clear error |

All error log entries are structured (slog JSON) and tagged with agent ID + role +
timestamp. `roster status` aggregates error counts per agent.

## Networking (v1)

v1 runs entirely on a single host. Service bind scopes (revised by /plan-ceo-review
2026-05-18):

| Service | Bind | Reachable from | Why |
|---|---|---|---|
| Nextcloud (port 8080) | `0.0.0.0` | The LAN | Multiple humans collaborate with the AI team via Nextcloud Talk/Files; the workspace must be LAN-reachable |
| Letta headless container | no host port forward | Docker network only | CLI talks to local Letta container which phones home to Letta server via WebSocket; nothing on the host LAN needs direct Letta access |
| MCP server | no host port forward | Docker network only | Internal to agents |
| Migadu | n/a (outbound only) | n/a | Roster CLI and agents make outbound IMAP/SMTP + Admin API calls; nothing inbound |

README must warn: "Roster v1 binds Nextcloud to 0.0.0.0. If you are not on a trusted
LAN, restrict access via firewall, VPN, or by setting `--nextcloud-bind 127.0.0.1` to
restrict to single-host use."

No DNS configuration, no TLS, no Traefik. Real DNS + TLS + custom domains (e.g.,
`project1.roster.ltd`) deferred to v2 when deploying to cloud (AKS/K8s path).

## Canned Template Format

Templates are Go structs embedded in the binary. Users select a template by name, not by
editing YAML.

```go
type Template struct {
    Name        string
    Description string
    Roles       []Role
}

type Role struct {
    ID          string   // "em", "analyst-1", "analyst-2", "researcher"
    DisplayName string   // "Engagement Manager"
    AgentModel  string   // "sonnet", "opus"
    Skills      []string // used in system prompt generation
    Resources   Resources
}
```

`roster init` picks a template and writes a `roster.json` state file. The user never
touches YAML in v1.

## Letta Integration Interface

Roster interacts with Letta via its REST API (default: `http://localhost:8283`):
- `POST /v1/agents` -- create agent with system prompt, tools, memory config
- `POST /v1/agents/{id}/messages` -- send message to agent (trigger processing)
- `GET /v1/agents/{id}/messages` -- read agent message history
- `DELETE /v1/agents/{id}` -- delete agent on `roster down`
- Memory management via `/v1/agents/{id}/memory` endpoints

No Go SDK exists for Letta. Roster wraps these REST endpoints directly using `net/http`.
Each role runs as a Letta agent instance within a single Letta server container (not
separate agent containers). The "Agent Containers" in the architecture diagram are Letta
agent instances managed by the shared Letta server.

## `roster.json` State File

Written by `roster init` to the current directory. All other commands discover it by
walking up the directory tree.

```json
{
  "template": "research-desk",
  "project": "market-entry-brief",
  "created_at": "2026-05-19T18:00:00Z",
  "services": {
    "nextcloud": { "url": "http://localhost:8080", "admin_password": "..." },
    "letta": { "url": "http://localhost:8283" },
    "migadu": { "domain": "market-entry-brief.roster.ltd" }
  },
  "roles": {
    "em": {
      "letta_agent_id": "agent-xxx",
      "nextcloud_user": "em",
      "email": "em@market-entry-brief.roster.ltd",
      "status": "ai",
      "takeover_at": null
    }
  }
}
```
