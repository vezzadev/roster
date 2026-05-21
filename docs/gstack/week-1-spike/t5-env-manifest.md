# Env Manifest

Versions of every component touched during the Week 1 spike. Captured at the start of each run and re-captured if anything changes.

Parent: [../design.md](../design.md) · Spec: [../design/07-refinements.md](../design/07-refinements.md) T4-C

## Why this file matters

When a spike result needs to be reproduced months later (or a regression appears), "Letta latest" or "Nextcloud current" is unactionable. Pin versions per run; re-pin if anything moves.

## Snapshot template

Repeat this block per run (Run 1, Run 2, …). Stamp the timestamp at the start of the run.

### Run _N_ — _timestamp_

#### Host

- OS: _e.g., Linux 6.6.x WSL2 / macOS 14.x_
- Docker: `docker --version`
- Docker Compose: `docker compose version`
- Architecture: _amd64 / arm64_

#### Containers

| Service | Image | Tag / digest | Notes |
|---------|-------|--------------|-------|
| Nextcloud | | | |
| Nextcloud DB (postgres / mariadb) | | | |
| Letta server | | | |
| Letta headless / worker | | | |
| MCP server (if separate container) | | | |

#### Letta config

- Letta version: `letta --version` or container tag
- Persistence backend: _sqlite / postgres / …_
- Agent runtime: _OpenRouter (Anthropic models) / proxy_ — direct Anthropic API is no longer the canonical path; v1 routes through OpenRouter

#### Nextcloud config

- Version: _from `occ status`_
- Apps enabled: _Talk, Files, …_
- Storage backend:

#### Models

Per design Cost Model: EM on Opus for synthesis (~3x Sonnet cost); other three roles on Sonnet. v1 routes inference through **OpenRouter** (the OpenRouter API key lives in `spike-compose/openrouter.local`, sourced into the Letta container by `spike-compose/bring-up.sh`). Letta exposes OpenRouter-routed models under handles prefixed `openrouter/`; the table below shows the Letta handles wired into the agent definitions. The bare OpenRouter ID (without the `openrouter/` prefix) applies only if you bypass Letta — e.g., the t2 raw-OpenRouter fallback.

Verified at smoke-test 2026-05-21: both handles below resolve in Letta's model registry against the live OpenRouter key (Letta synced 258 LLM models, two opus 4.7 variants — `:fast` is the alternative routing flag — and one sonnet 4.6).

| Role | Provider | Letta handle (use this in agent definitions) | OpenRouter ID (fallback if bypassing Letta) | Notes |
|------|----------|-----------------------------------------------|---------------------------------------------|-------|
| EM | OpenRouter | `openrouter/anthropic/claude-opus-4.7` | `anthropic/claude-opus-4.7` | Synthesis role; per design Cost Model |
| Senior Analyst A | OpenRouter | `openrouter/anthropic/claude-sonnet-4.6` | `anthropic/claude-sonnet-4.6` | |
| Senior Analyst B | OpenRouter | `openrouter/anthropic/claude-sonnet-4.6` | `anthropic/claude-sonnet-4.6` | |
| Researcher | OpenRouter | `openrouter/anthropic/claude-sonnet-4.6` | `anthropic/claude-sonnet-4.6` | |

OpenRouter pricing carries a markup over direct Anthropic — revisit SC#6 ($200/mo) math in [t7-spike-cost.md](t7-spike-cost.md) once the trendline lands.

#### MCP server(s)

- Source: _community repo + commit SHA / built-in MVP + commit SHA_
- Endpoints exposed: _list_

## Change log

| Run | Component | Change | Reason |
|-----|-----------|--------|--------|
| _empty_ | | | |
