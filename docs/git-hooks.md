# Git Hooks

This project uses git hooks in `.husky/` to run automated checks before pushing code.

## What runs

| Hook | What it does |
|------|-------------|
| `pre-commit` | Blocks direct commits to `main` and reserved worktree branches (A–G) |
| `pre-push` | Blocks pushes of worktree branches, checks rebase conflicts against `origin/main` |

## How it works

The local git config `core.hooksPath=.husky` points git to the hook scripts. This is set by the provisioning script or manually.

### Git config precedence

| Scope | Setting | Effect |
|-------|---------|--------|
| Local (repo) | `core.hooksPath=.husky` | **Active** — set by provision script |
| Global | `core.hooksPath=<user-defined>` | Overridden by local setting |
| System | (not set by default) | — |

To inspect the active hooks path:

```bash
git config --local core.hooksPath   # should print .husky
```

## Setup

After cloning, run:

```bash
git config core.hooksPath .husky
```

Or use the provisioning script which does this automatically:

```bash
scripts/provision-repo.sh
```

## Skipping hooks

Hooks should **not** be skipped. If a check fails, fix the issue before pushing. See [AGENTS.md](../AGENTS.md) for the project's policy on git hooks.

In exceptional cases with explicit authorization:

```bash
git push --no-verify
```
