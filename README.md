# Go Project

Template project for Go CLI applications and Kubernetes operators.

## Requirements

- Go >= 1.26
- Docker (for container builds)

## Quick Start

```bash
make tools        # Install dev tools (air, golangci-lint, goimports)
make dev          # Run with hot reload
make build        # Build binary to bin/myapp
make test-all     # Run lint + vet + tests with coverage
```

## Scripts

| Command              | Description                              |
| -------------------- | ---------------------------------------- |
| `make dev`           | Run with hot reload (air)                |
| `make build`         | Build binary with version tag            |
| `make run`           | Build and run                            |
| `make fmt`           | Format code (gofmt + goimports)          |
| `make lint`          | Run golangci-lint                        |
| `make vet`           | Run go vet                               |
| `make test`          | Run unit tests with race detector        |
| `make test-coverage` | Run tests with coverage report           |
| `make test-all`      | Full suite: lint + vet + coverage        |
| `make docker`        | Build container image                    |
| `make tools`         | Install dev tools                        |
| `make clean`         | Remove build artifacts                   |

## Project Structure

```
.
├── cmd/myapp/              # CLI entrypoint
├── internal/
│   └── cmd/                # Cobra command definitions
├── scripts/
│   ├── dev.sh              # Dev launcher (port mapping, zombie cleanup)
│   └── provision-repo.sh   # GitHub repo provisioning
├── .github/workflows/      # CI/CD pipelines
├── .husky/                 # Git hooks
├── .air.toml               # Hot reload config
├── .goreleaser.yml         # Release config (binaries + docker)
├── Dockerfile              # Multi-stage container build
└── Makefile                # Build & dev commands
```

## Releasing

Tagged releases are built by [GoReleaser](https://goreleaser.com/):
- Cross-compiled binaries (linux/darwin/windows, amd64/arm64)
- Container image pushed to GHCR
- Checksums and changelog

```bash
git tag v0.1.0
git push origin v0.1.0
```
