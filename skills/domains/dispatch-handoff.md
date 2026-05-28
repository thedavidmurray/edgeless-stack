---

name: dispatch-handoff
description: >
  USE THIS SKILL whenever creating dispatches from Hermes to COO, or when the
  user mentions 'dispatch', 'handoff', 'send to Mac', 'send to Claude', or 'pass
  to COO'. ALWAYS use for structured work handoffs between Chief of Staff (VPS)
  and COO (Mac). Contains the standardized template with from/to/type/priority
  frontmatter that ensures COO receives proper context, acceptance criteria, and
  related references.
metadata:
  tags: [handoff, coordination, workflow, hermes]
  tier: task-specific
  domain: product
when_to_apply: >
  When handing off work between agents and a human owner with standardized
  acceptance criteria.
---
# Dispatch Handoff Skill

Standardized format for dispatching work from Hermes (VPS) to COO (Mac Claude).

**Reference:** All handoffs follow the harmonized protocol at `/opt/david-sync/inboxes/PROTOCOL.md`

## Pre-Dispatch Setup

**Verify directory exists** (create if missing):
```bash
mkdir -p /opt/david-sync/inboxes/dispatch/inbox
```

Common error if skipped: `ENOENT` when writing dispatch file.

### Shortcut: Direct repo access

If the agent has direct filesystem access to the target repo (e.g. running on the Mac where `github-repos/edgelesslab.com/` lives), skip the formal dispatch inbox. Drop files straight into the repo, create a Paperclip goal for tracking, and report back. This avoids rsync latency and inbox polling. Only use when the agent can `cp` files into the working tree directly.

---

## Quick Reference

**Location:** `/opt/david-sync/inboxes/dispatch/inbox/`

**File naming:** `{from}-{type}-{short-title}-{YYYYMMDD}.md`

## Template Format

```markdown
---
from: hermes
to: dispatch
type: [directive|query|escalation|status]
priority: [normal|high|urgent]
created: ISO-8601
title: [short description]
ref: [optional: ID of message being responded to]
---

## Summary
[2-3 sentences max describing what this contains and why it matters]

## Content
[Details, findings, instructions, or asks]

## Acceptance Criteria
[If type=directive: what defines done]

## Related
[File paths, task IDs, links]
```

## Type Definitions

| Type | Use When |
|------|----------|
| directive | Decision made, needs COO implementation |
| query | Information needed from COO |
| escalation | Problem detected, needs COO attention/override |
| status | Routine update, no action required |
| response | Reply to a previous directive/query |

## Priority Guidelines

| Priority | Mechanism | Expected Response |
|----------|-----------|-------------------|
| normal | Inbox only | Next session/cron cycle |
| high | Inbox + Telegram alert | Same day |
| urgent | Telegram only | Immediate |

## Post-Dispatch Actions

After creating a dispatch:

1. **Update project-state.md:** Add to [IN-FLIGHT] or [QUEUED] at `/opt/david-sync/vault/03-Knowledge/Operations/project-state.md`
2. **If high/urgent:** Send Telegram alert referencing the dispatch file
3. **Log in backlog:** Link to relevant task IDs in `/opt/david-sync/backlog/tasks/`

## Example

```markdown
---
from: hermes
to: dispatch
type: directive
priority: high
created: 2026-04-04T14:22:00Z
title: Fix RSS cron failure - TheRundown API
---

## Summary
RSS ingest cron has been failing for 3 days due to expired TheRundown API key. 47 sports items backlogged. Need COO decision on key rotation vs feed deprecation.

## Content
- Cron logs show 401 errors starting 2026-04-01
- TheRundown API key in ~/.hermes/.env is 6 months old
- Backup feeds (ESPN, BBC) still operational
- 47 unprocessed sports items in backlog

**Decision needed:** Rotate TheRundown API key or remove feed from rotation?

**If rotating:** Update key in 1Password and .env, test with curl
**If deprecating:** Update newsletter-subscriptions.yaml, notify #sports-intel

## Acceptance Criteria
- [ ] Decision recorded in project-state.md
- [ ] Action taken (key rotated or feed removed)
- [ ] Cron tested and passing

## Related
- File: `/opt/david-sync/backlog/tasks/task-198.md`
- Cron: `hermes-agent-system-health` (2x/day)
- Protocol: /opt/david-sync/inboxes/PROTOCOL.md
```

## Post-Dispatch Protocol

After writing dispatch to inbox, ALWAYS update tracking:

1. **Read dispatch-tracker:** Use `skill_view("dispatch-tracker")` 
2. **Read current tracker.md:** `mcp_filesystem_read_text_file` on `/opt/david-sync/inboxes/dispatch/tracker.md`
3. **Update QUEUED section:** Add new dispatch to queue table
4. **Write back:** Update tracker.md via MCP

**Without this step:**
- COO cannot see dispatch in living status board
- Queue depth metrics become inaccurate
- Work may appear "lost" between inbox and tracker

---

## See Also

- Full protocol: `/opt/david-sync/inboxes/PROTOCOL.md`
- Project dashboard: `/opt/david-sync/vault/03-Knowledge/Operations/project-state.md`
- Directory structure: `/opt/david-sync/inboxes/`
- dispatch-tracker skill: For maintaining the living status board
