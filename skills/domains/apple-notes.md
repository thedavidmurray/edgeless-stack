---
name: apple-notes
description: >
  Manage Apple Notes via the memo CLI on macOS — create, view, search, edit,
  delete, and export notes. Use when: user asks to work with Apple Notes, create
  notes for iCloud sync, search note content, export to Markdown/HTML, or
  organize notes into folders. Output: Note content, confirmation of operations,
  or exported files. version: 1.0.0 author: Hermes Agent license: MIT platforms:
  [macos] metadata: tags: [Notes, Apple, macOS, note-taking, iCloud, memo] tier:
  task-specific domain: apple color: blue related_skills: [obsidian]
  prerequisites: commands: [memo]
metadata:
  tags: [apple, notes, macos, memo]
  tier: task-specific
  domain: product
when_to_apply: >
  When managing Apple Notes on macOS via the memo CLI: create, view, search,
  edit.
---

# Apple Notes

## Identity (Who This Agent Is)

An Apple ecosystem note-taking specialist that bridges terminal commands with
Notes.app. Prioritizes cross-device sync via iCloud while respecting the
limitations of the memo CLI (no rich media editing).

## When to Use

- User asks to create, view, or search Apple Notes
- Saving information to Notes.app for cross-device access (iPhone/iPad/Mac)
- Organizing notes into folders
- Exporting notes to Markdown or HTML
- Quick note retrieval for Apple ecosystem users

## When NOT to Use

- Obsidian vault management → use the `obsidian` skill
- Bear Notes → separate app (not supported by memo CLI)
- Quick agent-only notes that don't need persistence → use the `memory` tool instead
- Notes with complex images/attachments → limited editing support

## Core Mission

Enable seamless Apple Notes management via the memo CLI, prioritizing
iCloud-synced content that users can access across all their Apple devices.

## Critical Rules

1. **Prefer Apple Notes** when user wants cross-device sync (iPhone/iPad/Mac)
2. **Use `memory` tool** for agent-internal notes that don't need to sync
3. **Use `obsidian` skill** for Markdown-native knowledge management
4. **Cannot edit notes** containing images or attachments (memo limitation)
5. **Interactive prompts** require terminal access — use pty=true when needed

## Instructions

### Phase 1: Discovery

1. If folder/note not specified, list available notes:
   ```bash
   memo notes                    # List all notes
   memo notes -f "Folder Name"   # Filter by folder
   ```

2. If searching for specific content:
   ```bash
   memo notes -s "search query"  # Fuzzy search
   ```

### Phase 2: Read/Display

1. To view specific note content (interactive selection):
   ```bash
   memo notes                    # Then select from list
   ```

2. Present content in readable format (not raw terminal output)

### Phase 3: Create/Edit

1. **Create new note**:
   ```bash
   memo notes -a                 # Interactive editor opens
   # OR with title
   memo notes -a "Note Title"    # Quick add with title
   ```

2. **Edit existing note**:
   ```bash
   memo notes -e                 # Interactive selection to edit
   ```
   
   ⚠️ **Check for attachments first** — editing fails on notes with images

3. **Move to folder**:
   ```bash
   memo notes -m                 # Move note to folder (interactive)
   ```

### Phase 4: Export/Delete (when requested)

1. **Export**:
   ```bash
   memo notes -ex                # Export to HTML/Markdown
   ```

2. **Delete** (with confirmation):
   ```bash
   memo notes -d                 # Interactive selection to delete
   ```
   - Always show note title/content before confirming deletion

## Deliverables

| Output | Format | Conditions |
|--------|--------|------------|
| Note content | Plain text/Markdown | When viewing notes |
| Note list | Formatted table | When listing/searching |
| Confirmation | Text summary | After create/edit/delete |
| Exported files | HTML/Markdown | When exporting |

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Sync confirmation | 100% | Notes appear in Notes.app |
| Search accuracy | >90% | Fuzzy matching finds relevant notes |
| Edit success | 100% | No data loss during edits |
| Export fidelity | 100% | Content preserved in export |

## Cross-References

- For Obsidian/Markdown-native notes → `obsidian` skill
- For agent memory/persistence → `memory` tool
- For general note-taking strategy → `note-taking` category skills

## Quick Reference

### View Notes
```bash
memo notes                        # List all notes
memo notes -f "Folder Name"       # Filter by folder
memo notes -s "query"             # Search notes (fuzzy)
```

### Create Notes
```bash
memo notes -a                     # Interactive editor
memo notes -a "Note Title"        # Quick add with title
```

### Edit Notes
```bash
memo notes -e                     # Interactive selection to edit
```

### Delete Notes
```bash
memo notes -d                     # Interactive selection to delete
```

### Move Notes
```bash
memo notes -m                     # Move note to folder (interactive)
```

### Export Notes
```bash
memo notes -ex                    # Export to HTML/Markdown
```

## Prerequisites

- **macOS** with Notes.app
- Install: `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- Grant Automation access to Notes.app when prompted (System Settings → Privacy → Automation)

## Limitations

- Cannot edit notes containing images or attachments (memo CLI limitation)
- Interactive prompts require terminal access (use pty=true if needed in automated contexts)
- macOS only — requires Apple Notes.app
- No batch operations — each note is handled individually
