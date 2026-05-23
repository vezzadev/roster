# spike-compose-openclaw — skeleton

Parent: [../README.md](../README.md) §T3'

Mirrors Week 1's `spike-compose/` but with the runtime swapped from Letta to
OpenClaw. **Skeleton only** — several files contain explicit `TBD` markers
where OpenClaw config details (env var names, auth, MCP transport syntax)
need verification against the live OpenClaw 2026.1.29+ release before any
service comes up.

Status: ⏳ skeleton landed; live config pending T3' completion.

## Layout

```
spike-compose-openclaw/
├── README.md                          (this file)
├── docker-compose.yml                 (1 Gateway + Nextcloud + MCP sidecars + OTel collector)
├── Dockerfile.openclaw                (Node 24 + OpenClaw npm install + OTel auto-instrumentations)
├── wire-openclaw.sh                   (per-agent workspace seed — replaces Letta's wire-run-N.py)
└── agents/
    ├── openclaw.json                  (load-bearing config — defines all 4 agents via agents.list[])
    ├── _template/                     (convention Markdown files, copied into each agent dir)
    ├── em/                            (EM workspace — files seeded from _template)
    ├── senior-a/
    ├── senior-b/
    └── researcher/
```

Per [openclaw-facts.md](../openclaw-facts.md) §"Topology revision", the
correct OpenClaw pattern is **one Gateway hosting all four agents via
`agents.list[]` in `openclaw.json`**, not four Gateway containers. Half the
compose surface area; matches OpenClaw's design intent for multi-agent
routing.

## What's reused from Week 1 unchanged

- `../week-1-spike/spike-compose/otel-collector/` — OTel collector config (collector is runtime-agnostic, just routes spans to App Insights)
- `../week-1-spike/spike-compose/kql/` — KQL queries (T9' gate validates they work against OpenClaw spans)
- `../week-1-spike/spike-compose/researcher-web-mcp/` — Firecrawl MCP server (T4' validates it works under OpenClaw)
- Nextcloud + `cbcoutinho/nextcloud-mcp-server` setup (T4' validates same)

## What's new vs Week 1

- 4 OpenClaw Gateway services in place of 4 Letta containers
- No `driver.py` — OpenClaw heartbeats replace polling
- Per-agent Markdown workspaces in place of Letta's postgres-backed core memory
- Node-side OTel auto-instrumentations in place of Python `opentelemetry-instrument`

## Bring-up sequence (post-T3' + T9' + T4')

```sh
# 1. Pin OpenClaw version. Streamable-http MCP needs ≥ 2026.3.31;
#    CVE-2026-25253 patched version TBD (see openclaw-facts.md §"Install").
echo OPENCLAW_VERSION=2026.4.0 > .env

# 2. Seed per-agent workspace directories (idempotent).
./wire-openclaw.sh   # defaults to em senior-a senior-b researcher

# 3. Bring up stack.
docker compose up -d

# 4. Verify the Gateway is healthy (single control plane on :18789, docker-network-bound).
docker compose exec openclaw-gateway curl -fs http://localhost:18789/healthz
```

The control plane bind is **docker-network-only** by default — no host
exposure — per the CVE-2026-25253 mitigation noted in
[../README.md](../README.md).
