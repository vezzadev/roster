"""Standalone F-8 repro: minimal Letta 0.16.8 + native Anthropic, single
agent, slam a single very large user message and observe what happens at
the next-turn summarizer call.

Hypothesis (F-8 in t5-run-2-rerun-conclusions.md): Letta's summarizer calls
AnthropicClient.stream_async expecting AsyncStream[BetaRawMessageStreamEvent]
but receives an async_generator object; `async with stream:` in
anthropic_parallel_tool_call_streaming_interface.py:249 raises
TypeError: 'async_generator' object does not support the asynchronous
context manager protocol.

Usage:
    LETTA_TOKEN=... python3 repro-f8.py http://127.0.0.1:8290

The script:
  1. Creates a fresh agent with anthropic/claude-sonnet-4-6.
  2. Sends N huge user messages (configurable, default 4 turns × ~150K
     tokens of filler each).
  3. Prints per-turn usage and the response shape; on HTTP error or
     completion, leaves the agent alive so docker logs can be tailed for
     the crash trace.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

LETTA_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8290"
LETTA_TOKEN = os.environ.get("LETTA_TOKEN") or open(
    os.path.join(os.path.dirname(__file__), "letta.local")
).read().strip()

TURNS = int(os.environ.get("TURNS", "4"))
FILLER_REPEATS = int(os.environ.get("FILLER_REPEATS", "12000"))  # ~150K tokens at 12.5 chars/token


def http(method, path, body=None, timeout=600):
    req = urllib.request.Request(
        f"{LETTA_URL}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {LETTA_TOKEN}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def main():
    print(f"== F-8 repro against {LETTA_URL}", flush=True)
    print(f"== TURNS={TURNS} FILLER_REPEATS={FILLER_REPEATS} (~{FILLER_REPEATS * 12 / 1000:.0f}K chars / turn)", flush=True)

    ctx_window = int(os.environ.get("CTX_WINDOW", "32000"))
    agent = http("POST", "/v1/agents/", {
        "name": "f8-repro",
        "model": "anthropic/claude-sonnet-4-6",
        "embedding": "letta/letta-free",
        "include_base_tools": True,
        "context_window_limit": ctx_window,
    })
    print(f"== context_window_limit={ctx_window}", flush=True)
    aid = agent["id"]
    print(f"== agent: {aid}", flush=True)

    filler = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * FILLER_REPEATS

    for i in range(1, TURNS + 1):
        prompt = f"Turn {i}. Read this dump and reply with one word.\n\n{filler}"
        t0 = time.time()
        try:
            resp = http("POST", f"/v1/agents/{aid}/messages", {
                "messages": [{"role": "user", "content": prompt, "name": "repro"}]
            })
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:1000]
            print(f"== turn {i} HTTP {e.code} after {time.time()-t0:.1f}s: {body}", flush=True)
            break
        u = resp.get("usage", {})
        msgs = resp.get("messages", [])
        statuses = [m.get("status") for m in msgs if m.get("message_type") == "tool_return_message"]
        types = [m.get("message_type") for m in msgs]
        print(
            f"== turn {i}  t={time.time()-t0:.1f}s  "
            f"prompt={u.get('prompt_tokens')} cached_in={u.get('cached_input_tokens')} "
            f"cache_write={u.get('cache_write_tokens')} completion={u.get('completion_tokens')} "
            f"steps={u.get('step_count')} | msg_types={types[:6]}... | statuses={statuses[:4]}",
            flush=True,
        )

    print(f"== done. agent {aid} left alive for log inspection.", flush=True)


if __name__ == "__main__":
    main()
