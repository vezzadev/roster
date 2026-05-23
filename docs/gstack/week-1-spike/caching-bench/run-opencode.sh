#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
export OPENROUTER_API_KEY="$(cat "$HERE/../spike-compose/openrouter.local")"
DOC="$HERE/workload.md"
MODEL="openrouter/anthropic/claude-sonnet-4.6"

# opencode stores sessions per project (cwd). Use a clean cwd so we know which
# session is ours.
WORKDIR="$HERE/results/opencode-workdir"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo "=== opencode bench start: $(date -u +%FT%TZ) ==="
echo "--- turn 1 ---"
~/.opencode/bin/opencode run --model "$MODEL" --file "$DOC" -- \
  "Read the attached brief. In one sentence, what is the main strategic conclusion?" \
  2>&1 | tail -5

echo "--- turn 2 ---"
~/.opencode/bin/opencode run --model "$MODEL" --continue \
  "Now in one sentence, what is the most surprising finding?" \
  2>&1 | tail -5

echo "=== opencode bench end: $(date -u +%FT%TZ) ==="
