# Spike runtime (compose)

Docker Compose plumbing for the Week 1 validation spike. Copy this directory to a runtime location outside the repo (e.g., `~/spike-runtime/`) before `docker compose up` — Nextcloud's `/agents/` and `/founder/` volumes live inside Docker-managed storage, but anything bind-mounted into containers should not be the repo working tree.

Parent: [../README.md](../README.md) · Spec: [../../design/05-implementation.md](../../design/05-implementation.md) Week 1

## Files

- `docker-compose.yml` — Postgres, Redis, Nextcloud (web + Talk), Letta server, cbcoutinho/nextcloud-mcp-server. Squid commented out — uncomment before Run 2.
- `bring-up.sh` — wrapper that loads `openrouter.local` + `letta.local` into env and execs `docker compose`. Use this instead of `docker compose` directly.
- `.env.example` — non-sensitive Nextcloud credentials template. Copy to `.env`, fill, `chmod 600`. **Never commit `.env`.**
- `openrouter.local` (gitignored) — raw OpenRouter API key, one line. The two sensitive credentials are pulled out of `.env` so they sit in dedicated single-purpose files.
- `letta.local` (gitignored) — raw Letta server token, one line.
- `.gitignore` — keeps `.env` and `squid/` operational files out of git. `*.local` is matched by the repo-root `.gitignore` (defense in depth).
- `squid/` (Run 2 prep, not yet written) — `squid.conf` + `blocklist.txt` with the consulting-firm domains from [../t4-mcp-investigation.md](../t4-mcp-investigation.md) "Network and ACL policy".

## Bring-up sequence

See the top of `docker-compose.yml` — the 10-step sequence is captured there inline. All `docker compose ...` invocations in that sequence go through `./bring-up.sh ...` instead, so OpenRouter + Letta secrets get loaded from the `.local` files.

Example:

```
./bring-up.sh up -d nc-db nc-redis nextcloud
./bring-up.sh exec --user www-data nextcloud php occ app:install spreed
./bring-up.sh up -d letta nextcloud-mcp
./bring-up.sh logs -f letta
./bring-up.sh down
```

## Run 1 readiness gates

- [ ] `.env` populated; `chmod 600 .env` applied.
- [ ] `docker compose up -d nc-db nc-redis nextcloud` → all healthy.
- [ ] Talk installed: `docker compose exec --user www-data nextcloud php occ app:install spreed`.
- [ ] Users `em`, `analyst-a` created; one app-password each.
- [ ] `/agents/` and `/founder/` folders created; ACLs verified by logging in as each agent user (`/founder/` must be invisible).
- [ ] Talk rooms `#team` and `EM-A` created with the right participants.
- [ ] `docker compose up -d letta nextcloud-mcp` → healthy.
- [ ] Letta agents wired with frozen EM + Analyst A prompts; SHA-256 hashes re-verified against [../t5-system-prompts.md](../t5-system-prompts.md) "Hash protocol".
- [ ] Banned-token grep returns 0 hits.
- [ ] Container image digests captured in [../t5-env-manifest.md](../t5-env-manifest.md) Run 1 row.
- [ ] [../t5-run-ledger.md](../t5-run-ledger.md) Run 1 row opened with timestamp + frozen-hash + contamination-grep result + the documented "Run 1 brief is diagnostic, not rubric-gradable" note.

## Run 2 extras (after Run 1 closes)

- [ ] `squid/squid.conf` and `squid/blocklist.txt` written from [../t4-mcp-investigation.md](../t4-mcp-investigation.md) "Network and ACL policy".
- [ ] Squid service uncommented in `docker-compose.yml`.
- [ ] `docker compose up -d squid` → healthy.
- [ ] Four `curl -x http://squid:3128 ...` verification checks from t4 pass: two blocked, two allowed.
- [ ] Users `analyst-b`, `researcher` created; one app-password each.
- [ ] DM rooms `EM-B`, `EM-Researcher`, `A-B`, `A-Researcher`, `B-Researcher` created.
- [ ] `/agents/researcher-urls-log.md` initialized as an empty file in Nextcloud Files (Researcher appends to it; founder copies the contents to [../t5-researcher-urls.md](../t5-researcher-urls.md) post-run for the repo audit trail).
- [ ] Letta agents wired with frozen Analyst B + Researcher prompts; hashes + contamination grep re-verified.
- [ ] Researcher's URL-fetch surface has `HTTP_PROXY=http://squid:3128`.

## What this does NOT include (deliberately)

- **Roster CLI** — Week 2 work. Spike is hand-config.
- **Provisioner** — Week 2. The manual steps above are what `roster up` will eventually automate.
- **Backup/restore** — beyond spike scope; volumes are ephemeral if you `docker compose down -v`.
- **Production hardening** — `127.0.0.1` binds are the only nod toward "do not expose to the internet". Do not run this stack on a public host.
