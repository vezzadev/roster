#!/usr/bin/env bash
#
# wire-openclaw.sh — seed per-agent workspace directories.
#
# Replaces Week 1's wire-run-N.py. Note that openclaw.json (the actual
# load-bearing config) is checked in at agents/openclaw.json — this script
# only creates the per-agent workspace dirs and populates them with the
# conventional Markdown files the Letta system-prompt content is being
# translated into.
#
# Run before `docker compose up`. Idempotent.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="${SCRIPT_DIR}/agents"
TEMPLATE_DIR="${AGENTS_DIR}/_template"

ALL_AGENTS=(em senior-a senior-b researcher)
AGENTS=("${@:-${ALL_AGENTS[@]}}")

if [[ ! -f "${AGENTS_DIR}/openclaw.json" ]]; then
  echo "✗ Missing ${AGENTS_DIR}/openclaw.json — that's the load-bearing config and is checked in." >&2
  exit 1
fi

for agent in "${AGENTS[@]}"; do
  workspace="${AGENTS_DIR}/${agent}"
  mkdir -p "${workspace}"
  echo "→ Seeding ${agent} at ${workspace}"

  # Convention (per the Milvus article — not a hard OpenClaw contract; see
  # openclaw-facts.md §"Open question 3"). T3' may rename or restructure.
  for file in AGENTS.md SOUL.md MEMORY.md HEARTBEAT.md TOOLS.md; do
    if [[ ! -f "${workspace}/${file}" ]]; then
      if [[ -f "${TEMPLATE_DIR}/${file}" ]]; then
        cp "${TEMPLATE_DIR}/${file}" "${workspace}/${file}"
      else
        echo "# ${agent} — ${file}" > "${workspace}/${file}"
        echo "" >> "${workspace}/${file}"
        echo "TBD: fill from ../../../week-1-spike/t5-system-prompts.md §${agent^^}" >> "${workspace}/${file}"
      fi
    fi
  done
done

echo "✓ Wired ${#AGENTS[@]} agent(s). Bring up with: docker compose up -d"
