#!/usr/bin/env python3
"""Caching-bench Letta runner.

Creates a fresh agent on the local Letta server, sends two messages that
share a stable system prompt, then deletes the agent. The point is to
generate two OpenRouter requests with an identical cacheable prefix so we
can read CachedInputTokens from OpenRouter_CL.
"""
import json
import pathlib
import sys
import time
import urllib.request

HERE = pathlib.Path(__file__).parent.resolve()
LETTA_URL = "http://127.0.0.1:8283"
TOKEN = (HERE.parent / "spike-compose" / "letta.local").read_text().strip()
DOC = (HERE / "workload.md").read_text()


def http(method, path, body=None):
    req = urllib.request.Request(
        f"{LETTA_URL}{path}",
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
        data=json.dumps(body).encode() if body is not None else None,
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())


def main():
    system_prompt = (
        "You are a research assistant. The user has loaded the following "
        "document into your working context. Answer follow-up questions about "
        "it concisely and in a single sentence.\n\n"
        f"--- DOCUMENT START ---\n{DOC}\n--- DOCUMENT END ---"
    )

    print(f"=== letta bench start: {time.strftime('%FT%TZ', time.gmtime())} ===")
    print(f"system prompt size: {len(system_prompt)} chars (~{len(system_prompt)//4} tokens)")

    agent = http(
        "POST",
        "/v1/agents/",
        {
            "name": f"cachebench-{int(time.time())}",
            "system": system_prompt,
            "model": "openrouter/anthropic/claude-sonnet-4.6",
            "embedding": "letta/letta-free",
            "tools": [],
            "include_base_tools": False,
            "include_base_tool_rules": False,
        },
    )
    agent_id = agent["id"]
    print(f"agent created: {agent_id}")

    try:
        for i, prompt in enumerate(
            [
                "In one sentence, what is the main strategic conclusion of this brief?",
                "Now in one sentence, what is the most surprising finding?",
            ],
            start=1,
        ):
            print(f"--- turn {i} ---")
            t0 = time.time()
            resp = http(
                "POST",
                f"/v1/agents/{agent_id}/messages",
                {"messages": [{"role": "user", "content": prompt}]},
            )
            for m in resp.get("messages", []):
                if m.get("message_type") == "assistant_message":
                    print(m.get("content", "")[:400])
            print(f"latency: {time.time() - t0:.1f}s")
    finally:
        try:
            http("DELETE", f"/v1/agents/{agent_id}")
            print(f"agent deleted: {agent_id}")
        except Exception as e:
            print(f"cleanup warning: {e}", file=sys.stderr)

    print(f"=== letta bench end: {time.strftime('%FT%TZ', time.gmtime())} ===")


if __name__ == "__main__":
    main()
