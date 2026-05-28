---

name: proof-of-completion
description: >
  Structured proof-of-completion block for agent-delivered work. Include before
  marking any issue done.
metadata:
  tags: [completion, evidence, verification]
  tier: task-specific
  domain: product
when_to_apply: >
  When delivering work — include a structured proof-of-completion block before
  marking done.
---
# Proof of Completion

## Overview

Before marking any issue **done**, agents MUST include a `## Proof of Completion` block in the issue description. This is a hard gate: the `paperclip-completion-sync.py` cron will reject any issue marked done that lacks this block, resetting it to `in_progress`.

**Why:** Simon Last proved that the agent must prove the work is done, not just mark it done. This structural fix prevents phantom completions and gives Ombudsman (QA) concrete artifacts to review.

## When to Use

**Mandatory before:**
- Marking any Paperclip issue `done`
- Declaring a task complete in any bot-to-bot handoff
- Closing a PR or merging a feature branch

**Applies to:**
- Code changes (files, commits, tests)
- Infrastructure work (configs deployed, services restarted)
- Documentation (pages written, links verified)
- Research (findings documented, sources cited)

## Proof Block Format

Copy this template into the issue description under `## Proof of Completion`:

```markdown
## Proof of Completion

- **What was done**: [1-2 sentence summary of the deliverable]
- **How to verify**: [exact command to run, file path to inspect, or test to execute]
- **Proof artifacts**: [links to files, commits, output logs, or screenshots]
- **Diff summary**: [what changed — files touched, lines added/removed]
- **Side effects**: [risks, breaking changes, follow-ups needed, or "None"]
```

## Examples

### Example A: Code Fix

```markdown
## Proof of Completion

- **What was done**: Fixed off-by-one error in `scraper.py` pagination loop.
- **How to verify**: Run `python -m pytest tests/test_scraper.py::test_pagination -v`
- **Proof artifacts**: Commit `a1b2c3d`, PR #42, test output showing 3/3 pass
- **Diff summary**: `scraper.py` L89-94 — changed `range(limit)` to `range(limit+1)`
- **Side effects**: None
```

### Example B: Infrastructure Deploy

```markdown
## Proof of Completion

- **What was done**: Deployed cron health-check script to Hetzner VPS and enabled systemd timer.
- **How to verify**: `ssh root@89.167.52.198 systemctl status cron-health-check.timer`
- **Proof artifacts**: `/etc/systemd/system/cron-health-check.timer` (created), `/opt/scripts/cron-health-check.py` (deployed)
- **Diff summary**: Added 2 files, 78 lines total; no existing files modified
- **Side effects**: Timer fires every 5 minutes — monitor logs for 48h
```

### Example C: Documentation

```markdown
## Proof of Completion

- **What was done**: Wrote AGENTS.md section on Tiered Skill Loading with load commands.
- **How to verify**: Open `claude-projects/AGENTS.md`, search for "Tiered Skill Loading"
- **Proof artifacts**: Lines 45-100 of AGENTS.md (direct link to file)
- **Diff summary**: Added 55 lines to AGENTS.md; no deletions
- **Side effects**: None — additive docs only
```

## Quality Checks

Before submitting proof block, verify:

1. **Verifiable**: Another human (or agent) can follow "How to verify" and confirm
2. **Specific**: File paths, commit SHAs, line numbers — not vague references
3. **Complete**: All five fields filled; "None" is acceptable for side effects
4. **Honest**: If work is partial, say so — do not mark done

## Common Mistakes

| Mistake | Why It Fails QA |
|---------|-----------------|
| "Tests pass" without command | Ombudsman can't reproduce |
| "Fixed bug" without file names | No way to inspect the change |
| Empty side effects | Hides risks; always assess |
| Links to private/internal URLs | External reviewers can't access |
| "See PR" as only artifact | PR might be unmerged or changed |

## Enforcement

- `paperclip-completion-sync.py` runs every 30 minutes
- Issues marked `done` without proof block → reset to `in_progress` with warning
- Repeat offenders logged in `.paperclip-qa-log.jsonl` for router feedback
- Ombudsman QA review is still required even with proof block present
