#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
export OPENROUTER_API_KEY="$(cat "$HERE/../spike-compose/openrouter.local")"
SESSION_DIR="$HERE/results/pi-session"
rm -rf "$SESSION_DIR"
mkdir -p "$SESSION_DIR"
DOC="$HERE/workload.md"

echo "=== pi bench start: $(date -u +%FT%TZ) ==="
echo "--- turn 1 ---"
pi --provider openrouter --model anthropic/claude-sonnet-4.6 \
   --session-dir "$SESSION_DIR" \
   --append-system-prompt "$DOC" \
   --print \
   "In one sentence, what is the main strategic conclusion of this brief?" \
   2>&1 | tail -5

echo "--- turn 2 ---"
pi --provider openrouter --model anthropic/claude-sonnet-4.6 \
   --continue \
   --session-dir "$SESSION_DIR" \
   --append-system-prompt "$DOC" \
   --print \
   "Now in one sentence, what is the most surprising finding?" \
   2>&1 | tail -5

echo "=== pi bench end: $(date -u +%FT%TZ) ==="
