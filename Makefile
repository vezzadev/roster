VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo dev)
LDFLAGS := -ldflags "-X main.version=$(VERSION)"

.PHONY: dev build run fmt lint vet test test-coverage test-all tools docker clean check-links

dev:
	./scripts/dev.sh

build:
	go build $(LDFLAGS) -o bin/myapp ./cmd/myapp

run: build
	./bin/myapp

fmt:
	gofmt -w .
	goimports -w .

lint:
	golangci-lint run ./...

vet:
	go vet ./...

test:
	go test -race ./...

test-coverage:
	go test -race -coverprofile=coverage.out -covermode=atomic ./...
	@echo "--- Coverage report ---"
	@go tool cover -func=coverage.out
	@go tool cover -html=coverage.out -o coverage.html

test-all: lint vet test-coverage check-links

check-links:
	@command -v lychee >/dev/null 2>&1 || { \
		echo "lychee not installed. Install: cargo install lychee  (or)  brew install lychee"; \
		exit 1; \
	}
	lychee --config lychee.toml --no-progress "**/*.md"

docker:
	docker build --build-arg VERSION=$(VERSION) -t myapp:$(VERSION) .

tools:
	go install github.com/air-verse/air@latest
	go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@latest
	go install golang.org/x/tools/cmd/goimports@latest

clean:
	rm -rf bin/ coverage.out coverage.html tmp/ dist/
