# HEARTBEAT.md (template)

The list OpenClaw's heartbeat scheduler walks every interval. If nothing on
the list is actionable, the agent returns `HEARTBEAT_OK` and the Gateway
silently drops the response.

**No Letta equivalent.** Letta was request-driven; this file is the
structural substitute for the `driver.py` polling loop Week 1 needed.

## Inbox checks

- [ ] New unread messages in #team
- [ ] New unread DMs in pair rooms
- [ ] Mentioned (`@<my-name>`) anywhere

## Workstream checks

- [ ] Files in `/agents/research/` modified since my last read
- [ ] Files in `/agents/synthesis/` modified since my last read
- [ ] Any escalations pending my decision

## Self-checks

- [ ] Is my last commitment overdue? (e.g. "I'll have this draft by X")
- [ ] Did I leave a tool call mid-flight last turn?

---

*Per-agent variants of this list land during T3' — the EM's HEARTBEAT.md
is heavier (coordination) than the Researcher's (mostly fetch queue).*
