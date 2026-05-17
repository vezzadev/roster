#!/usr/bin/env bash
set -euo pipefail

# Intelligent dev server launcher with worktree-aware port mapping
# and zombie process management.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# ── Worktree-aware port mapping ────────────────────────────────────────────────

determine_port() {
  local branch
  branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

  case "$branch" in
    A) echo 8010 ;;
    B) echo 8020 ;;
    C) echo 8030 ;;
    D) echo 8040 ;;
    E) echo 8050 ;;
    F) echo 8060 ;;
    G) echo 8070 ;;
    *) echo "${PORT:-8080}" ;;
  esac
}

PORT=$(determine_port)
export PORT

# ── Zombie process cleanup ─────────────────────────────────────────────────────

LOCKFILE="/tmp/go-project-dev-${PORT}.pid"

cleanup_zombie() {
  if [ -f "$LOCKFILE" ]; then
    local old_pid
    old_pid=$(cat "$LOCKFILE")

    if kill -0 "$old_pid" 2>/dev/null; then
      echo "Killing zombie dev server (PID $old_pid) on port $PORT..."
      kill "$old_pid" 2>/dev/null || true
      sleep 1
      kill -9 "$old_pid" 2>/dev/null || true
    fi

    rm -f "$LOCKFILE"
  fi
}

cleanup_zombie

# ── Validate port availability ─────────────────────────────────────────────────

if lsof -i ":$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "ERROR: Port $PORT is already in use by another process."
  lsof -i ":$PORT" -sTCP:LISTEN
  exit 1
fi

# ── Start server ───────────────────────────────────────────────────────────────

mkdir -p logs
LOGFILE="logs/run-dev-$(date +%Y%m%d-%H%M%S).log"

echo "Starting dev server on :$PORT with hot reload (logging to $LOGFILE)"
echo "$$" > "$LOCKFILE"

trap 'rm -f "$LOCKFILE"' EXIT

if command -v air &>/dev/null; then
  air 2>&1 | tee "$LOGFILE"
else
  echo "WARN: air not installed, falling back to go run (no hot reload). Run 'make tools' to install."
  go run ./cmd/myapp 2>&1 | tee "$LOGFILE"
fi
