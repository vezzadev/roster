# Researcher URL Fetch Log

Append-only log of every URL the Researcher role fetches during the Week 1 spike. Auditable trail for the contamination guard.

Parent: [../design.md](../design.md) · Spec: [grading-rubric.md](grading-rubric.md) "Contamination guard" · [mcp-investigation.md](mcp-investigation.md) "Network and ACL policy"

## Why this file matters

The Researcher is the only agent with web access. Without a fetch log, blocklist evasion (archive mirrors, SlideShare hosts of consulting briefs, gray-zone domains) is undetectable. The log makes contamination findable post-hoc and creates a deterrent during the run.

## Format

One row per fetch. The Researcher appends synchronously at fetch time — never batched at end of run, never reconstructed from memory.

| Run | t+ (s from run start) | URL | HTTP status | Bytes | Snippet (first 200 chars of fetched body) | Used for (which section of [sample-brief.md](sample-brief.md)) |
|-----|------|-----|-------------|-------|--------------------------------------------|-----------------|
| _empty_ | | | | | | |

## Append discipline

- **Synchronous.** Append before processing the fetched content, not after.
- **Including failures.** 4xx, 5xx, blocked-by-proxy (403 from Squid) — all logged. Blocked attempts are diagnostic signal.
- **No edits, no deletions.** Mistakes get appended, not corrected in place. If the Researcher fetches the wrong URL, the next row logs the correct one and a third row notes the redundancy.
- **Append in [event-timeline.md](event-timeline.md) too.** Each fetch is also an `event_type: tool_call` row in the timeline; this file is the detailed view, the timeline is the cross-agent view.

## Audit procedure (run during + after spike)

Mid-run (Run 2, hourly):

1. Scan the URL column for any consulting-firm domain or known mirror path. If found: **kill the spike**, do not let it complete. The artifact is contaminated.
2. Scan snippets for naming of "McKinsey / BCG / Bain / consulting" in the fetched content. If a non-blocklisted source quotes or mirrors consulting-brief content, that's a Layer 2 leak.

Post-run:

3. Cross-check every URL against the blocklist in [mcp-investigation.md](mcp-investigation.md). Zero violations required to pass Layer 1.
4. Spot-check 5-10 fetched URLs by visiting them yourself. Confirm the snippets match the live content (catches Researcher fabrication / hallucinated citations).
5. Cross-check URLs against the citations in [sample-brief.md](sample-brief.md). Every cited source in the brief should appear here. Citations in the brief that are NOT in this log are fabricated — major fail signal.

## Verification status

- Researcher wired to append: _TBD — verify in [run-ledger.md](run-ledger.md) "Run N setup"_
- Outbound proxy active: _TBD — see [mcp-investigation.md](mcp-investigation.md) verification checklist_
- Audit performed (mid-run): _none yet_
- Audit performed (post-run): _none yet_
