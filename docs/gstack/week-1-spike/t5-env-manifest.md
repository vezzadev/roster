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
- Agent runtime: _direct Anthropic API / proxy_

#### Nextcloud config

- Version: _from `occ status`_
- Apps enabled: _Talk, Files, …_
- Storage backend:

#### Models

Per design Cost Model: EM on Opus for synthesis (~3x Sonnet cost); other three roles on Sonnet. Pin exact model ID per run.

| Role | Provider | Model ID | Notes |
|------|----------|----------|-------|
| EM | Anthropic | claude-opus-4-7 | Synthesis role; per design Cost Model |
| Senior Analyst A | Anthropic | claude-sonnet-4-6 | |
| Senior Analyst B | Anthropic | claude-sonnet-4-6 | |
| Researcher | Anthropic | claude-sonnet-4-6 | |

#### MCP server(s)

- Source: _community repo + commit SHA / built-in MVP + commit SHA_
- Endpoints exposed: _list_

## Change log

| Run | Component | Change | Reason |
|-----|-----------|--------|--------|
| _empty_ | | | |
