# OpenClaw verified facts (2026-05-23)

Source-of-truth research that backstops [README.md](README.md) and the
spike-compose skeleton. **Every claim here is anchored to an OpenClaw doc page
or GitHub issue** so future readers can re-verify when OpenClaw moves.

Author note: a chunk of the first draft of this scaffold was based on a Milvus
blog explainer and the Vellum competitor writeup. Those were useful framing
but not authoritative on config syntax. This file replaces those guesses with
docs-anchored answers to the README's "open questions to resolve before
kickoff."

## Open question 1 — MCP transport support

**Confirmed: stdio, SSE, and streamable-http are all supported.** Streamable-http
shipped in **v2026.3.31** ([openclaw#55087 closing comment](https://github.com/openclaw/openclaw/issues/55087#issuecomment-4318895732),
[mcp-transport.ts:78](https://github.com/openclaw/openclaw/blob/34896839ba22/src/agents/mcp-transport.ts#L78)).
Before 2026.3.31, URL-based MCP configs were silently skipped with
`only stdio MCP servers are supported right now`. That's why the Milvus
article's "stdio-only" framing existed — it was true until ~7 weeks ago.

Canonical config shape ([docs.openclaw.ai/cli/mcp](https://docs.openclaw.ai/cli/mcp)):

```json5
{
  mcp: {
    servers: {
      // stdio
      "context7":      { command: "uvx", args: ["context7-mcp"] },
      // SSE (default when URL given, no transport)
      "remote-tools":  { url: "https://mcp.example.com", headers: { "Authorization": "Bearer ..." } },
      // streamable-http (explicit)
      "streaming":     { url: "https://mcp.example.com/stream", transport: "streamable-http", connectionTimeoutMs: 10000 },
    }
  }
}
```

**Implication for T4'**: stdio is the mature path (older, broader test coverage).
Streamable-http works but is newer; if Week 1's Letta streamable-http SSE-parse
bug is symptomatic of upstream MCP SDK framing issues, OpenClaw could hit a
related bug. **T4' should test stdio first, streamable-http second.** This
matches what F-O1 fallback bullet #1 in [t2-openclaw-fallback.md](t2-openclaw-fallback.md)
already recommends.

## Open question 2 — Heartbeat ↔ message-wake latency

**Heartbeat config** ([docs.openclaw.ai/gateway/configuration](https://docs.openclaw.ai/gateway/configuration)
"Set up heartbeat"):

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",      // duration string; "0m" disables
        target: "last",    // "last" | "none" | "<channel-id>"
      }
    }
  }
}
```

CLI equivalent:

```sh
openclaw config set agents.defaults.heartbeat.every "5m"
```

**Inbound-message wake is structural, not heartbeat-dependent.** OpenClaw's
Gateway processes messages as they arrive on a channel — that drives an
immediate agent turn. The heartbeat is the *fallback* that wakes the agent
when no message is in flight (e.g. to check its own HEARTBEAT.md checklist).
Source: the Gateway architecture description on the channels docs treats
inbound channel events as primary triggers.

**Implication for F-O2**: inbound-message latency is bounded by channel-poll
rate (channel-specific), not by `heartbeat.every`. The "30 min lag on a
Researcher response" worry in the original F-O2 framing is wrong for
message-driven flows. The heartbeat economic concern (F-O5) is still real
because every fired heartbeat is a model call — but heartbeat ≠ wake latency.

## Open question 3 — Memory hand-off (fresh-start vs migrate)

No upstream constraint blocks either choice. The README's recommendation
(fresh-start to keep the comparison clean) stands. Per-agent workspaces are
opaque directories OpenClaw consumes — what's inside is largely convention.

**Verified canonical config files** ([docs.openclaw.ai/gateway/configuration](https://docs.openclaw.ai/gateway/configuration)):

- `~/.openclaw/openclaw.json` — JSON5, schema-strict, hot-reloadable, the
  load-bearing config file
- `~/.openclaw/.env` — env-var fallback (won't override existing env vars)
- `agents.defaults.workspace` + `agents.list[].workspace` — per-agent dirs

The Milvus article's claim that the agent runtime "assembles context from
AGENTS.md, SOUL.md, TOOLS.md, MEMORY.md, daily log" appears to describe a
*workspace convention*, not a hard-coded set of files. The actual loader is
not visible in the public docs we've pulled. **The scaffold should treat
those .md files as templates we author, not as files OpenClaw mandates.**

## Open question 4 — Skill catalog

No-op for Week 1.5: the spike doesn't need community skills. Built-in tools
(per [docs.openclaw.ai/tools](https://docs.openclaw.ai/tools)) plus the two
MCP servers (Nextcloud + Firecrawl) cover the workload. Cisco's 26% vuln
finding from the Milvus piece is a *deployment* concern, not relevant to a
spike that authors no skills of its own.

## Open question 5 — Anthropic auth (API key vs OAuth)

**Two routes per [docs.openclaw.ai/providers/anthropic](https://docs.openclaw.ai/providers/anthropic):**

1. **API key** — `ANTHROPIC_API_KEY` env var, or set via `openclaw onboard
   --anthropic-api-key`, or config `env.ANTHROPIC_API_KEY`. Standard
   usage-based billing.
2. **Claude CLI reuse** — `openclaw onboard` → choose "Claude CLI". Reuses
   existing `claude` CLI credentials. Newer accounts hit the "Anthropic OAuth
   policy change" some Reddit threads describe — for production, the docs
   themselves recommend API key.

**Recommendation: API key.** Aligns with the F-O5 budget-cap mitigation
(spending limits at Anthropic console level) and avoids the Claude-CLI auth
expiry surface.

### Bonus finding — prompt caching is structural under OpenClaw

OpenClaw **auto-enables Anthropic prompt caching for API-key auth** with
`cacheRetention: "short"` (5 min) as the default. `"long"` (1 hour) is
configurable per model. Per-agent overrides via `agents.list[].params`. This
is the exact C-6 behavior Letta required patching to get on the OpenRouter
path, and what Letta gets natively only on its Anthropic-direct route.

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-7": {
          params: { cacheRetention: "long" }   // 1h cache
        }
      }
    }
  }
}
```

**Implication for T7'**: the 91.8% cache hit rate Run-1-anthropic-direct
achieved should reproduce structurally under OpenClaw without any patching.
The cost projection in T7' can assume "Letta-Anthropic-direct equivalent" as
the baseline.

## Topology revision — single Gateway hosts all 4 agents

The biggest correction to the scaffold. The original draft assumed
**4 OpenClaw Gateway containers** (one per agent identity, mirroring the
per-agent Letta container pattern that Week 1 ended up adopting).

**Correct topology per
[docs.openclaw.ai/gateway/configuration](https://docs.openclaw.ai/gateway/configuration)
"Configure multi-agent routing":** one Gateway, multiple agents via
`agents.list`:

```json5
{
  agents: {
    defaults: {
      workspace: "/workspace",
      model: { primary: "anthropic/claude-opus-4-7" },
      heartbeat: { every: "30m" }
    },
    list: [
      { id: "em",          default: true, workspace: "/workspace/em" },
      { id: "senior-a",                   workspace: "/workspace/senior-a" },
      { id: "senior-b",                   workspace: "/workspace/senior-b" },
      { id: "researcher",                 workspace: "/workspace/researcher" }
    ]
  },
  bindings: [
    // route Nextcloud Talk rooms to specific agents
  ]
}
```

**Why this matters for the spike**:

- Half the compose surface area: 1 Gateway service instead of 4
- One OTel emitter instead of 4 (still tag per-agent via `service.namespace` +
  agent-id attributes — T9' parity check needs to confirm OpenClaw emits the
  agent id as a span attribute)
- Heartbeat polling cost scales **per agent**, not per process — still 4×
  but no per-process overhead
- A Gateway crash takes down all 4 agents at once (worse blast radius than
  Letta's per-container model). T6' (forced SPOF) test result is now more
  consequential — recovery has to bring back the whole team.

## Install + version pinning

**Verified install path** ([docs.openclaw.ai/install/installer](https://docs.openclaw.ai/install/installer)):

- Default method: **npm global install**, fronted by the `install.sh` shell wrapper
- Node 24 default (Node 22.19+ also supported)
- Pin: `OPENCLAW_VERSION=<spec>` env var, or `--version <spec>` flag, accepting
  npm dist-tags or semver
- Beta channel: `--beta` (uses the `beta` dist-tag)

For a reproducible container: `npm install -g openclaw@<exact-version>` is
clean. The install.sh wrapper is for laptops, not Dockerfile builds.

**CVE-2026-25253 pin** — the Milvus blog's claim of `≥ 2026.1.29` is not
re-verifiable from the docs we've pulled. The actual CVE record and OpenClaw
CHANGELOG should be checked before T3' finalize. For now the scaffold pins to
**`2026.4.x` or later** (>= 2026.3.31 for streamable-http MCP, and well past
the late-January CVE patch window).

## Config secrets / env var substitution

Useful for the spike's Anthropic key + Firecrawl key handling:

```json5
{
  env: { ANTHROPIC_API_KEY: "${ANTHROPIC_API_KEY}" },     // literal substitution
  gateway: { auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" } }
}
```

Or the SecretRef pattern for higher-assurance setups:

```json5
{
  models: {
    providers: {
      openai: { apiKey: { source: "env", provider: "default", id: "OPENAI_API_KEY" } }
    }
  }
}
```

The spike uses plain env-var substitution; SecretRef is overkill for a
5-day timebox.

## What didn't get answered

- **CVE-2026-25253 patched-version pin**: needs CHANGELOG verification
- **MCP tool-call span instrumentation**: T9' has to find out empirically
  whether OpenClaw emits MCP spans, or whether we need a wrapper
- **`HEARTBEAT.md` as a literal file vs. just a documentation convention**:
  the docs talk about heartbeat *behavior* but not a specific markdown file
  the runtime parses. Possibly community convention; T3' to verify.

## Cross-references

- README open questions: [README.md](README.md) §"Open questions"
- Files this revises: [README.md](README.md), [t4-openclaw-mcp-fidelity.md](t4-openclaw-mcp-fidelity.md),
  [t9-otel-parity.md](t9-otel-parity.md), [t2-openclaw-fallback.md](t2-openclaw-fallback.md),
  [spike-compose-openclaw/](spike-compose-openclaw/)
