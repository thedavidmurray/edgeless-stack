---
name: retrospective-learning
description: >
  Extracts and persists learnings from coding sessions to enable continual
  improvement. Use at end of sessions, after completing features, or when
  switching major tasks.
metadata:
  tags: [retrospective, learning, session-end, persistence, improvement]
  tier: general
  domain: kernel
when_to_apply: >
  At the end of a significant coding session or after completing a complex
  feature to extract and persist learnings
---

# Retrospective Learning Skill

Extract and persist learnings from coding sessions to enable continual improvement.

## When to Activate

- End of significant coding sessions
- After completing a feature or fixing a complex bug
- User says "what did we learn" or "retrospective"
- When switching between major tasks

## Core Capability

Analyze session activity to extract learnings and persist them to:
1. Vector store (searchable knowledge)
2. Agent memory files (cross-session context)
3. Skill updates (modify existing skills)
4. Backlog tasks (actionable improvements)

## Learning Categories

### Skills Updates
New capabilities or edge cases for existing skills

### New Skills
Patterns worthy of their own skill file

### Best Practices
Document but don't automate -- coding conventions, tips

### Failures to Remember
Approaches that don't work -- prevent repeating mistakes

### Backlog Items
Future work identified during session

## Persistence Targets

| Learning Type | Target |
|---------------|--------|
| Techniques | Vector store + agent memory |
| Skill changes | Edit skill.md files |
| Best practices | Agent memory |
| Failures | Vector store (searchable) |
| Backlog | backlog/tasks/*.md |

<!-- CUSTOMIZE: Map these targets to your actual storage locations.
     Common setups:
     - ChromaDB collection for vector store
     - ~/.claude/projects/.../memory/ for agent memory
     - Obsidian vault for knowledge base
     - backlog/tasks/ for actionable items
-->

## Key Patterns

### Documenting Failures
```
What was tried -> Why it failed -> What works instead
```

### Vector Store Document Format
```json
{
  "type": "session_learning",
  "session_date": "2026-01-06",
  "category": "skill_update",
  "content": "...",
  "context": "..."
}
```

### Memory File Naming
- `pattern-X-discovered`
- `failure-Y-documented`
- `best-practice-Z`

## Output

Structured summary with:
- Learnings persisted (counts)
- Key insights (prioritized)
- Failures documented
- Backlog items created
- Skills updated

## Session Log Template

<!-- CUSTOMIZE: Set your sessions directory path -->

```python
from datetime import datetime
import os

date = datetime.now()
# CUSTOMIZE: Your sessions directory
sessions_dir = f"sessions/{date.strftime('%Y-%m')}"
os.makedirs(sessions_dir, exist_ok=True)

vault_path = f"{sessions_dir}/retrospective-{date.strftime('%Y-%m-%d')}.md"

vault_content = f"""---
type: retrospective
date: {date.strftime('%Y-%m-%d')}
session_focus: {{session_focus}}
learnings_count: {{learnings_count}}
failures_count: {{failures_count}}
tags:
  - retrospective
  - session-log
---

# Session Retrospective - {date.strftime('%Y-%m-%d')}
## {{session_focus}}

### Key Accomplishments
{{accomplishments_list}}

### Learnings Extracted
{{learnings_list}}

### Failures Documented
{{failures_list}}

### Backlog Items Created
{{backlog_list}}

### Technical Debt Identified
{{tech_debt_list}}
"""

with open(vault_path, 'w') as f:
    f.write(vault_content)
```

## Notification (Optional)

<!-- CUSTOMIZE: Set up your preferred notification channel.
     Options: email, Telegram, Slack, Discord, etc. -->

After persisting learnings, optionally send a summary notification:
- Subject format: "Retro: [Session Focus]"
- Include: learnings count, key insights, backlog items created

## Command

```
/retrospective
/retrospective --focus <topic>
```

## Integration

- Trigger after project completion
- Trigger at iteration milestones
- Trigger when switching projects
- Works with session-planning skill for phase-end reviews

## Related Skills

- `session-planning` -- Plans that trigger retrospectives at phase boundaries
- `memory-system` -- Where learnings get stored
- `verify-completion` -- Completion checks before retrospective
