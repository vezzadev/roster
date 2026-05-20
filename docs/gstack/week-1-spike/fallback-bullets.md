# Fallback Bullets — Pre-Committed Exits

Pre-spike exercise output: 3-4 alternative experiments per likely failure mode, so a tired post-failure founder doesn't have to invent them at the worst possible moment.

Parent: [../design.md](../design.md) · Spec: [../design/07-refinements.md](../design/07-refinements.md) D5 + T2

## Why this file matters

Codex T2 (CRITICAL): without pre-committed exits, an ambiguous Week 1 result gets narrated into "promising enough" and 1 week becomes 4 on a dead premise. These bullets are not a decision tree — they are pre-written alternatives that are cheaper to consult than to invent.

## How to use

If Run 2 produces a result that triggers any of the three failure-mode signals below: **stop the spike, open this file, pick one of the bullets, and only then resume.** The discipline is "consult the bullets before resuming," not "rigidly follow the bullets."

If none of the three failure modes matches the situation, that itself is a signal — the failure may be outside the pre-imagined space, which is exactly when motivated reasoning is most dangerous.

---

## Failure mode 1: Letta unfit

**Signal:** The runtime is the bottleneck. Agents technically respond but Letta's memory persistence, message passing, or multi-agent coordination is the source of the failure (e.g., agents lose context across handoffs, messages get lost, the headless container WebSocket-disconnects repeatedly, or agent definitions don't survive restarts). The brief is unproduced because the substrate is unreliable, not because the agents are bad.

Alternatives, lightest first:

- **Drop to raw Anthropic API + thin orchestration script.** Skip Letta entirely; coordinate the four agents via a single Python script that maintains conversation state in-process. Loses persistence between runs but removes the Letta variable. Cost: 1 day. Test: can a 4-agent run complete with no runtime crashes?
- **Try Letta with single-process embedded mode (no headless container split).** Eliminate the WebSocket layer that's the suspected SPOF. Cost: half a day. Test: same as above.
- **Swap to a different agent runtime (Claude Agent SDK direct, or AutoGen).** Bigger pivot, but if Letta is structurally unfit the whole Premise 3 needs revisiting. Cost: 2-3 days for re-spike. Test: does the failure reproduce on a different substrate? If no, Letta is the issue; if yes, it's elsewhere.
- **Stop and re-baseline.** If three runtimes fail similarly, the issue is in the design (the agent design, the tools surface, or the prompts), not the runtime. Open `what-didnt-work.md`, write up the cross-runtime evidence, and call the gate.

## Failure mode 2: Agents don't coordinate

**Signal:** Runtime is fine. Each agent works individually. But the 4-agent team doesn't produce a coherent brief — agents duplicate work, overwrite each other's files, ignore messages, or the EM fails to delegate. The 2-agent smoke run (Run 1) produced something coherent; Run 2 falls apart at the coordination layer.

Alternatives, lightest first:

- **Reduce to 3 agents (drop one Senior Analyst).** Tests whether the failure is N-agent overhead vs structural. If 3 works and 4 doesn't, the design needs a coordination primitive (round-robin, explicit lock per file, shared scratchpad) before scaling back to 4. Cost: half a day to re-run with prompts adjusted.
- **Make the EM prescriptive instead of facilitative.** Replace "delegate work to your team" with a step-by-step playbook the EM follows: "step 1, ask Senior A for market sizing; step 2, ask Senior B for competitor map; step 3, ask Researcher for sources; step 4, synthesize." Loses adaptivity but tests whether the issue is the EM's planning step. Cost: 2h to rewrite prompts.
- **Add a shared scratchpad file convention with explicit locking.** Each agent writes to its own section; EM consolidates. Constrains the failure mode where agents overwrite each other. Cost: 2h to add the convention + prompt updates.
- **Stop and call it.** If reducing N, making the EM rigid, and adding locking all fail to produce a coherent brief, the multi-agent collaboration model itself may not produce value at this complexity. That's a major design signal — the brief might be better done by one strong agent with subagent spawning, which collapses the whole product narrative.

## Failure mode 3: Output unusable

**Signal:** Runtime is fine. Coordination is fine. A brief gets produced. But it's bad — vague, hallucinated, structurally incoherent, or missing dimensions the grading rubric considers non-negotiable. The self-grade scores ≤ 2 on multiple dimensions, or the multi-AI panel review converges on "no analyst would trust this."

Alternatives, lightest first:

- **Sharpen the prompts.** Add the McKinsey/BCG comparator brief structure directly into the EM's system prompt as a target template. Cost: 1h to rewrite prompts; new numbered run. Test: does the same agent team produce a meaningfully better brief with explicit structural scaffolding?
- **Upgrade model tier.** Move Senior Analyst A and B to Opus (currently Sonnet per design Cost Model). Burns SC#6 budget — if this works, the design's cost story needs revisiting. Cost: 1 new run, ~2-3x token cost. Test: artifact quality vs cost-budget tradeoff.
- **Reduce scope of the brief.** Pick a narrower target market or a single dimension (e.g., just competitive landscape, not full market-entry). If a narrower brief is analyst-grade and a full one is not, the product positioning shifts from "market-entry briefs" to "specific dimension deep-dives." Cost: 1 new run with adjusted prompts. Test: passes rubric on the narrower scope.
- **Stop and call it.** If three prompt iterations + an Opus upgrade + a scope reduction all produce sub-rubric briefs, the agents-produce-analyst-grade-work premise is broken at this date. That is the gate doing its job — proceed to v1 pivot or stop per the CEO plan.

---

## Honesty guard

After applying any bullet: write up what happened in [what-didnt-work.md](what-didnt-work.md) **before** declaring success or failure. The bullets are alternatives to invent-on-the-spot; they are not exemptions from the journal discipline.

## Carried risk

Per [../design/07-refinements.md](../design/07-refinements.md) "Carried risks": the bullets may be ignored at the failure moment if the founder is mid-failure-mode. The discipline of consulting this file at the failure trigger depends on the founder. The mitigation has no further mitigation.
