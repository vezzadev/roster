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

- `go test -race ./...` must pass with zero failures
- Coverage threshold: 70%
- New features require unit tests
- No flaky tests — fix immediately
- Prefer table-driven tests with subtests

### Git Workflow

- Merge only (`gh pr merge --merge --auto`)
- Squash/rebase merge disabled
- PRs must be up-to-date with main before merging
- Rebase to update: `git pull --rebase origin main`
- Never bypass hooks (`--no-verify`)

## Multi-Instance Port Management

For any HTTP components, worktree-based port mapping:
- Worktree A=8010, B=8020, C=8030, D=8040, E=8050, F=8060, G=8070
- Non-worktree: 8080 (default)

Set via `PORT` environment variable.
