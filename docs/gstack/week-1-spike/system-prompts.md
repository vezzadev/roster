# System Prompts

Final working prompts per role for the Week 1 validation spike.

Parent: [../design.md](../design.md) · Spec: [../design/05-implementation.md](../design/05-implementation.md) Week 1

## Prompt freeze discipline

Per the run matrix in [run-ledger.md](run-ledger.md), prompts are frozen per numbered run. Any change after a run begins requires a new numbered run. Record the prompt hash (`sha256` of the prompt text) for each role in the run-ledger entry.

## Prompt sanitization rules (contamination guard)

Enforces Layer 1 + Layer 2 + Goodhart resistance per [grading-rubric.md](grading-rubric.md) "Contamination guard". **Every role's system prompt MUST follow these rules — verify before each numbered run and record verification in [run-ledger.md](run-ledger.md).**

System prompts must NOT contain:

- The names "McKinsey", "BCG", "Boston Consulting Group", "Bain", "Strategy&", "Roland Berger", "Monitor Deloitte", "Oliver Wyman", "L.E.K.", "Kearney" — by firm name. Reference to "top-tier strategy consultancies" or "Big-3 strategy firms" is also banned (still leaks the target).
- Any URL or title of a specific public consulting brief, including the 5 anchor briefs in [grading-rubric.md](grading-rubric.md) (BCG Vietnam, McKinsey Beating-the-Odds, BCG SA E-Tailers, Bain Emerging Markets, BCG Changing-Your-Orbit).
- The 8 rubric dimensions or their descriptions ("market sizing", "competitive landscape", "entry mode analysis", "risks + mitigations" etc. as a checklist). Agents may produce these sections because that is how good market-entry briefs are structured, but not because the prompt told them to score points on them.
- Phrases like "produce an analyst-grade brief", "produce a Big-3-quality deliverable", "meet the standards of a top strategy firm" — these prime the agents to template-match.
- References to the grading scale (1-5), the gate decision criteria, or the AI-panel review step.

System prompts MAY contain:

- The task description: "produce a market-entry brief on whether [hypothetical mid-market vertical-SaaS firm targeting Indonesian logistics SMBs] should enter Indonesia in 2026, and if so, how."
- Role description (EM coordinates; Senior Analysts do depth work; Researcher gathers public data).
- Communication conventions (which Talk room, which Files folder, when to hand off).
- Tool usage constraints (Researcher's blocklist — see [mcp-investigation.md](mcp-investigation.md) "Network and ACL policy"; verbatim hand-copied into the Researcher prompt as a tool-policy clause).
- Output format spec (markdown, sections at the agent's discretion, citations required for non-obvious claims).

Verification before each run:

- Pipe each role's prompt through a grep for the banned-token list above. Zero hits required.
- Record the prompt hash AND the grep verification result in [run-ledger.md](run-ledger.md) "Prompts frozen at hash" line.

## Engagement Manager (EM)

Model: claude-opus-4-7 (per design Cost Model — synthesis role)
Frozen for run: _none yet_
Hash: _none yet_

```
<system prompt here>
```

## Senior Analyst A

Model: claude-sonnet-4-6 (per design Cost Model)
Frozen for run: _none yet_
Hash: _none yet_

```
<system prompt here>
```

## Senior Analyst B

Model: claude-sonnet-4-6 (per design Cost Model)
Frozen for run: _none yet_
Hash: _none yet_

```
<system prompt here>
```

## Researcher

Model: claude-sonnet-4-6 (per design Cost Model)
Frozen for run: _none yet_
Hash: _none yet_

```
<system prompt here>
```

## Change log

| Date | Run | Role | Change |
|------|-----|------|--------|
| _empty_ | | | |
