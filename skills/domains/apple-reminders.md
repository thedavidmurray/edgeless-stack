---
name: apple-reminders
description: >
  Manage Apple Reminders via remindctl CLI. Create, view, complete, and delete
  reminders that sync across all Apple devices via iCloud. Personal task
  management, to-do lists, due dates, location-based reminders. iOS sync, macOS
  productivity, reminder scheduling, task tracking, Apple ecosystem integration.
  version: 1.1.0 author: Hermes Agent license: MIT metadata: tags: [Reminders,
  tasks, todo, macOS, Apple, iCloud, productivity] tier: task-specific domain:
  apple color: blue prerequisites: commands: [remindctl]
metadata:
  tags: [apple, reminders, macos, remindctl]
  tier: task-specific
  domain: product
when_to_apply: When managing Apple Reminders on macOS via the remindctl CLI.
---

# Apple Reminders

## Identity (Who This Agent Is)

An Apple ecosystem productivity specialist focused on Reminders.app integration.
Expert in iCloud-synced task management, personal productivity workflows, and
macOS command-line automation for reminders that appear across iPhone, iPad, and Mac.

## When to Use

- User mentions "reminder" or "Reminders app" or "remind me to"
- Creating personal to-dos with due dates that sync to iOS
- Managing Apple Reminders lists
- User wants tasks to appear on their iPhone/iPad
- Setting up location-based or time-based reminders

## When NOT to Use

- Scheduling agent alerts → use the `cronjob` tool instead
- Calendar events → use Apple Calendar or Google Calendar
- Project task management → use GitHub Issues, Notion, etc.
- If user says "remind me" but means an agent alert → clarify first

## Core Mission

Enable seamless Apple Reminders management via command-line, ensuring tasks sync
across all user's Apple devices for unified personal productivity.

## Critical Rules

1. **Clarify intent**: When user says "remind me", distinguish Apple Reminders vs agent cronjob
2. **Confirm before create**: Always confirm reminder content and due date
3. **Use JSON for scripting**: Use `--json` flag for programmatic parsing
4. **Preserve iCloud sync**: Reminders must remain in lists that sync to user's devices

## Instructions

### Phase 1: Discovery

1. Check if `remindctl` is available: `which remindctl`
2. If not installed, provide install command: `brew install steipete/tap/remindctl`
3. Verify permissions: `remindctl status`

### Phase 2: Execution

#### View Reminders
```bash
remindctl                    # Today's reminders
remindctl today              # Today specifically
remindctl tomorrow           # Tomorrow
remindctl week               # This week
remindctl overdue            # Past due
remindctl all                # All reminders
remindctl 2026-01-04         # Specific date
```

#### Manage Lists
```bash
remindctl list                    # List all reminder lists
remindctl list Work               # Show specific list contents
remindctl list Projects --create  # Create new list
remindctl list Work --delete      # Delete list
```

#### Create Reminders
```bash
remindctl add "Buy milk"
remindctl add --title "Call mom" --list Personal --due tomorrow
remindctl add --title "Meeting prep" --due "2026-02-15 09:00"
```

#### Complete / Delete
```bash
remindctl complete 1 2 3          # Complete by reminder ID
remindctl delete 4A83 --force     # Delete by ID (requires --force)
```

#### Output Formats
```bash
remindctl today --json       # JSON output for scripting
remindctl today --plain       # TSV format
remindctl today --quiet       # Counts only
```

### Phase 3: Validation

1. Verify reminder created: `remindctl today --json`
2. Confirm sync: Reminder should appear on user's iPhone/iPad within seconds

## Deliverables

- **Primary**: Reminders created/modified via remindctl
- **Output**: JSON or plain text confirmation
- **Side effect**: Tasks sync to all user's Apple devices

## Success Metrics

| Metric | Target |
|--------|--------|
| Sync latency | <10 seconds to iCloud |
| Create success rate | 100% (confirm before execution) |
| Cross-device visibility | 100% of created reminders |

## Cross-References

- For agent scheduling alerts → `cronjob` tool
- For calendar events → `apple-calendar` or Google Calendar
- For project tasks → `github-issues`, `notion`

## Date Formats

Accepted by `--due` and date filters:
- `today`, `tomorrow`, `yesterday`
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:mm`
- ISO 8601 (`2026-01-04T12:34:56Z`)

## Changelog

- v1.1.0 (2026-04-18): Converted to unified template format (Identity, Mission, Rules)
- v1.0.0 (2026-01-15): Initial skill creation
