# Go Project

## Commands

```bash
make dev            # Dev server with hot reload (air)
make build          # Build binary with version tag
make fmt            # Format code (gofmt + goimports)
make lint           # golangci-lint (strictest config)
make vet            # go vet
make test           # Unit tests with race detector
make test-coverage  # Tests with coverage report
make test-all       # REQUIRED before push (lint + vet + coverage)
make tools          # Install dev tools (air, golangci-lint, goimports)
make docker         # Build container image
make clean          # Remove build artifacts
```

## Code Conventions

### Go

- Go 1.26+ required
- Use cobra for CLI commands
- Errors must be handled explicitly — never use `_` for error returns
- Use structured logging (`log/slog`)
- Prefer table-driven tests
- No global mutable state

### Project Structure

```
cmd/myapp/          # CLI entrypoint
internal/cmd/       # Cobra command definitions
internal/           # Private application logic
api/v1alpha1/       # CRD types (when doing K8s)
```

### File Naming

- `snake_case.go` for all Go files
- `snake_case_test.go` for test files
- Package names: short, lowercase, no underscores

### Error Handling

- Wrap errors with context: `fmt.Errorf("operation: %w", err)`
- Let errors propagate to appropriate boundaries
- Validate at system boundaries (CLI input, API responses)

### Testing

For Roster v1, the authoritative testing standards live in
`docs/gstack/design.md` → "Development Standards" (TDD Iron Law, unit + integration +
E2E + stress, subagent-driven implementation per feature). The bullets below are the
inherited Go-template baseline; the design-doc Development Standards SUPERSEDE them
where they conflict:

- `go test -race ./...` must pass with zero failures
- Coverage threshold: 70% (enforced by `.github/workflows/ci-cd-pr.yml`)
- New features require unit tests (Roster v1 requires unit + integration + E2E + stress)
- No flaky tests — fix immediately (Roster v1 plans 10 consecutive E2E runs async on every commit to main; auto-files an issue on regression, does not gate PR merges — not yet wired in CI)
- Prefer table-driven tests with subtests

### Git Workflow

- Merge only (`gh pr merge --merge --auto`)
- Squash/rebase merge disabled
- PRs must be up-to-date with main before merging
- Rebase to update: `git pull --rebase origin main`
- Never bypass hooks (`--no-verify`)
- **Roster v1 addition:** human reviewer approval required on every PR before
  auto-merge fires. Demo evidence (terminal recording + screenshots) must be present
  under `demo/<date>-<feature>/` and linked in the PR description.

## Multi-Instance Port Management

For any HTTP components, worktree-based port mapping:
- Worktree A=8010, B=8020, C=8030, D=8040, E=8050, F=8060, G=8070
- Non-worktree: 8080 (default)

Set via `PORT` environment variable.

## LLM observability

Raw LLM call inputs, outputs, and costs are logged to an Azure Log Analytics
workspace (table `OpenRouter_CL`):

```
/subscriptions/07aba226-fd59-489a-b07b-4158fef12a5d/resourceGroups/rg-openrouter-swec-01/providers/Microsoft.OperationalInsights/workspaces/la-openrouter-swec-01
```

Query via `az cli` (workspace customer ID `0e1dc4da-9ef1-4e44-9fd5-d9d5a97ecb91`):

```bash
az monitor log-analytics query \
  --workspace 0e1dc4da-9ef1-4e44-9fd5-d9d5a97ecb91 \
  --analytics-query "OpenRouter_CL | where TimeGenerated > ago(1d) | summarize sum(Cost)"
```

Use it for cost attribution, debugging prompt/response payloads, and latency
analysis. Per-call records include the full request and response bodies.

## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool. When in doubt, invoke the skill.

Any product/entrepreneurship discussion (ideas, strategy, scope, brainstorming, design
system, full review pipelines) is handled via gstack skills with `./docs/gstack` as
the working directory — `cd` there before invoking the skill so plans, design docs,
and review artifacts land in that folder.

Key routing rules:
- Product ideas/brainstorming → invoke /office-hours
- Strategy/scope → invoke /plan-ceo-review
- Architecture → invoke /plan-eng-review
- Design system/plan review → invoke /design-consultation or /plan-design-review
- Full review pipeline → invoke /autoplan
- Bugs/errors → invoke /investigate
- QA/testing site behavior → invoke /qa or /qa-only
- Code review/diff check → invoke /review
- Visual polish → invoke /design-review
- Ship/deploy/PR → invoke /ship or /land-and-deploy
- Save progress → invoke /context-save
- Resume context → invoke /context-restore

## AI collaboration preferences

- **Codex second opinions:** Proactively offer to run Codex / get an independent AI cold read on strategy decisions, premise checks, design reviews, and gnarly debugging. Don't skip it to save 5 minutes — the user finds the cross-model perspective high-leverage.
- **Web research:** Always OK with WebSearch / Firecrawl / Browserbase to refine ideas, validate assumptions, or close information gaps. No need to ask permission for general research; ask only before sending anything sensitive or identifying.
