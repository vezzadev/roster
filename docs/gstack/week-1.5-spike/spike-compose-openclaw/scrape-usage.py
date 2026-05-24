#!/usr/bin/env python3
"""Post-run cost rollup from OpenClaw session transcripts.

Run 1' cost-rollup mechanism. OpenClaw session transcripts at
`~/.openclaw/agents/<agent>/sessions/*.jsonl` record each assistant message
with full Anthropic `usage` (`input`, `output`, `cacheRead`, `cacheWrite`,
`totalTokens`). This script reads those, sums per (agent, model), applies
Anthropic posted rates, and emits the same shape as Week 1's
`kql/03-per-agent-cost.kql`.

Authoritative for this spike's cost numbers. The KQL path is left
disconnected until OpenClaw emits the matching `model.usage` diagnostic
event for primary turns (see boot-smoke-findings.md for the gap).

Usage:
    docker exec openclaw-run-1prime python3 - < scrape-usage.py
or:
    docker cp openclaw-run-1prime:/root/.openclaw/agents ./agents-snapshot/
    python3 scrape-usage.py ./agents-snapshot
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import defaultdict

# Anthropic posted rates, USD per token. Matches Week 1's
# kql/03-per-agent-cost.kql price tables.
RATES = {
    "claude-opus-4-7":    {"input": 15.0e-6, "output": 75.0e-6, "cache_read": 1.50e-6,  "cache_write": 18.75e-6},
    "claude-sonnet-4-6":  {"input":  3.0e-6, "output": 15.0e-6, "cache_read": 0.30e-6,  "cache_write":  3.75e-6},
    "claude-haiku-4-5":   {"input":  0.8e-6, "output":  4.0e-6, "cache_read": 0.08e-6,  "cache_write":  1.00e-6},
}


def find_sessions(root: pathlib.Path) -> list[tuple[str, pathlib.Path]]:
    """Walk `<root>/agents/<agent>/sessions/*.jsonl` and yield (agent_id, path)."""
    out = []
    for agent_dir in (root / "agents").iterdir() if (root / "agents").exists() else []:
        sessions_dir = agent_dir / "sessions"
        if not sessions_dir.is_dir():
            continue
        for jsonl in sessions_dir.glob("*.jsonl"):
            if jsonl.name.endswith(".trajectory.jsonl"):
                continue
            out.append((agent_dir.name, jsonl))
    return out


def sum_usage(sessions: list[tuple[str, pathlib.Path]]):
    """Return per-(agent, model) totals + per-call counts."""
    totals = defaultdict(lambda: {"calls": 0, "input": 0, "output": 0, "cache_read": 0, "cache_write": 0})
    for agent, path in sessions:
        for line in path.read_text().splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = rec.get("message") or {}
            usage = msg.get("usage")
            if not usage or msg.get("role") != "assistant":
                continue
            model = msg.get("model", "unknown")
            key = (agent, model)
            totals[key]["calls"] += 1
            totals[key]["input"]       += int(usage.get("input", 0) or 0)
            totals[key]["output"]      += int(usage.get("output", 0) or 0)
            totals[key]["cache_read"]  += int(usage.get("cacheRead", 0) or 0)
            totals[key]["cache_write"] += int(usage.get("cacheWrite", 0) or 0)
    return totals


def cost_for(model: str, t: dict) -> float:
    rates = RATES.get(model)
    if not rates:
        return float("nan")
    return (
        t["input"]       * rates["input"]
        + t["output"]      * rates["output"]
        + t["cache_read"]  * rates["cache_read"]
        + t["cache_write"] * rates["cache_write"]
    )


def cache_hit_pct(t: dict) -> float:
    prompt = t["input"] + t["cache_read"] + t["cache_write"]
    return (100.0 * t["cache_read"] / prompt) if prompt else 0.0


def main(root: str) -> int:
    sessions = find_sessions(pathlib.Path(root))
    if not sessions:
        print(f"no session jsonl found under {root}/agents/*/sessions/", file=sys.stderr)
        return 1
    totals = sum_usage(sessions)

    print(f"{'agent':<14}{'model':<22}{'calls':>7}{'input':>10}{'output':>10}{'cache_rd':>10}{'cache_wr':>10}{'hit%':>7}{'$':>10}")
    total_cost = 0.0
    for (agent, model), t in sorted(totals.items()):
        c = cost_for(model, t)
        total_cost += c if c == c else 0.0  # NaN check
        print(f"{agent:<14}{model:<22}{t['calls']:>7}{t['input']:>10}{t['output']:>10}{t['cache_read']:>10}{t['cache_write']:>10}{cache_hit_pct(t):>6.1f}%{c:>10.4f}")
    print(f"{'TOTAL':<14}{'':<22}{'':>7}{'':>10}{'':>10}{'':>10}{'':>10}{'':>7}{total_cost:>10.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "/root/.openclaw"))
