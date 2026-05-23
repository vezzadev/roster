import json, pathlib, time, urllib.request, sys

SPIKE = pathlib.Path(__file__).parent
LETTA_TOKEN = (SPIKE / "letta.local").read_text().strip()
AGENTS = json.loads((SPIKE / "run1-agents.local").read_text())
em = AGENTS["em"]
out_dir = SPIKE / "run-1-anthropic-direct"
out_dir.mkdir(exist_ok=True)

started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
print(f"kickoff at {started} to EM={em['agent_id']}", flush=True)
body = {"messages": [{"role": "user", "content": "Begin the engagement.", "name": "founder"}]}
req = urllib.request.Request(
    f"{em['letta_url']}/v1/agents/{em['agent_id']}/messages",
    data=json.dumps(body).encode(),
    headers={"Authorization": f"Bearer {LETTA_TOKEN}", "Content-Type": "application/json"},
    method="POST",
)
t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=1800) as resp:
        payload = resp.read()
        dt = time.time() - t0
        (out_dir / "kickoff-response.json").write_bytes(payload)
        print(f"kickoff http={resp.status} bytes={len(payload)} time={dt:.6f}s", flush=True)
        print(f"kickoff response received at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}", flush=True)
except Exception as e:
    print(f"kickoff failed after {time.time()-t0:.1f}s: {e!r}", flush=True)
    sys.exit(1)

data = json.loads(payload)
usage = data.get("usage", {})
print(f"  usage: prompt={usage.get('prompt_tokens')} cached_in={usage.get('cached_input_tokens')} cache_write={usage.get('cache_write_tokens')} completion={usage.get('completion_tokens')} reasoning={usage.get('reasoning_tokens')} steps={usage.get('step_count')}", flush=True)
msgs = data.get("messages", [])
print(f"  {len(msgs)} messages produced", flush=True)
for m in msgs:
    t = m.get("message_type") or m.get("role")
    if t == "tool_call_message":
        tc = m.get("tool_call", {})
        print(f"    [tool_call] {tc.get('name')}({(tc.get('arguments') or '')[:140]})", flush=True)
    elif t == "tool_return_message":
        st = m.get("status", "?")
        print(f"    [tool_return] status={st}", flush=True)
    elif t == "assistant_message":
        body = (m.get("content") or "")[:240].replace("\n"," ")
        print(f"    [assistant] {body}", flush=True)
    elif t == "reasoning_message":
        body = (m.get("reasoning") or "")[:240].replace("\n"," ")
        print(f"    [reasoning] {body}", flush=True)
