---
name: file-organizer
description: Intelligently organize messy folders, find duplicates, and suggest better structures.

metadata:
  tags:
  - file-organizer
  - cleanup
  - organization
  - duplicates
  - folder-structure
  tier: task-specific
  domain: tooling
when_to_apply: When a directory is messy, files are scattered, duplicates have accumulated, or folder structure needs improvement
---
# File Organizer

Personal organization assistant for maintaining clean, logical file structures.

## When to Use

- Downloads folder is chaotic
- Files scattered across directories
- Duplicate files taking up space
- Folder structure doesn't make sense
- Starting a new project needing structure
- Cleaning up before archiving
- Vault organization needs work

## What This Skill Does

1. **Analyzes Current Structure**: Reviews folders and files to understand what exists
2. **Finds Duplicates**: Identifies duplicate files across directories
3. **Suggests Organization**: Proposes logical folder structures based on content
4. **Automates Cleanup**: Moves, renames, and organizes files with approval
5. **Maintains Context**: Makes smart decisions based on file types, dates, content
6. **Reduces Clutter**: Identifies old files that can be archived

## Usage

```
/organize ~/Downloads              # Organize specific folder
/organize --duplicates ~/Documents # Find duplicates
/organize --structure ~/Projects   # Suggest structure improvements
/organize --dry-run ~/folder       # Preview without changes
```

## Workflow

### Step 1: Understand the Scope

Ask clarifying questions:
- Which directory needs organization?
- What's the main problem? (can't find things, duplicates, no structure?)
- Any files or folders to avoid?
- How aggressively to organize? (conservative vs comprehensive)

### Step 2: Analyze Current State

```bash
# Get overview of current structure
ls -la [target_directory]

# Check file types and sizes
find [target_directory] -type f -exec file {} \; | head -20

# Identify largest files
du -sh [target_directory]/* | sort -rh | head -20

# Count file types
find [target_directory] -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn
```

Summarize findings:
- Total files and folders
- File type breakdown
- Size distribution
- Date ranges
- Obvious organization issues

### Step 3: Identify Organization Patterns

**By Type**:
- Documents (PDF, DOCX, TXT, MD)
- Images (JPG, PNG, SVG)
- Videos (MP4, MOV)
- Archives (ZIP, TAR)
- Code/Projects (directories with code)
- Data (CSV, JSON, XLSX)

**By Purpose**:
- Work vs Personal
- Active vs Archive
- Project-specific
- Reference materials
- Temporary/scratch

**By Date**:
- Current year/month
- Previous years
- Very old (archive candidates)

### Step 4: Find Duplicates (if requested)

```bash
# Find exact duplicates by hash
find [directory] -type f -exec md5 {} \; | sort | uniq -d

# Find files with same name
find [directory] -type f -printf '%f
' | sort | uniq -d

# Find similar-sized files (potential duplicates)
find [directory] -type f -printf '%s %p
' | sort -n
```

For each set of duplicates:
- Show all file paths
- Display sizes and modification dates
- Recommend which to keep (usually newest or best location)
- **Always ask for confirmation before deleting**

### Step 5: Propose Organization Plan

Present a clear plan before making changes:

```markdown
# Organization Plan for [Directory]

## Current State
- X files across Y folders
- [Size] total
- File types: [breakdown]
- Issues: [list problems]

## Proposed Structure

```
[Directory]/
├── Active/
│   ├── Projects/
│   └── Documents/
├── Archive/
│   ├── 2024/
│   └── 2025/
└── ToSort/
```

## Changes to Make

1. **Create new folders**: [list]
2. **Move files**:
   - X PDFs → Documents/
   - Y images → Assets/
   - Z old files → Archive/
3. **Delete**: [duplicates or trash files]

## Files Needing Decision

- [List any files requiring user input]

Ready to proceed? (yes/no/modify)
```

### Step 6: Execute Organization

After approval:

```bash
# Create folder structure
mkdir -p "path/to/new/folders"

# Move files with logging
mv "old/path/file.pdf" "new/path/file.pdf"
```

**Important Rules**:
- Always confirm before deleting
- Log all moves for potential undo
- Preserve modification dates
- Handle filename conflicts
- Stop and ask if unexpected situations

### Step 7: Provide Summary

```markdown
# Organization Complete

## What Changed

- Created [X] new folders
- Organized [Y] files
- Freed [Z] MB by removing duplicates
- Archived [W] old files

## New Structure

[Show the new folder tree]

## Maintenance Tips

1. **Weekly**: Sort new downloads
2. **Monthly**: Review and archive completed projects
3. **Quarterly**: Check for duplicates

Want to organize another folder?
```

## Special: Vault Organization

For Obsidian vault organization (`claude-vault/`):

### Vault Structure Standards

```
claude-vault/
├── 00-Inbox/           # Quick capture
├── 01-Sessions/        # Session logs (YYYY-MM/)
├── 02-Projects/        # Active project docs
├── 03-Knowledge/       # Persistent knowledge
├── 05-Solutions/       # Reusable solutions
├── 06-Config/          # Configuration docs
├── 08-Reference/       # External references
├── 09-Secrets/         # Sensitive (gitignored)
├── 10-Meta/            # Vault meta docs
├── 13-Reports/         # Generated reports
└── 99-Archive/         # Old/completed items
```

### Vault Organization Rules

1. Files without clear home → `00-Inbox/`
2. Session-specific → `01-Sessions/YYYY-MM/`
3. Knowledge meant to persist → `03-Knowledge/`
4. Completed projects → `99-Archive/`

## Safety Checks

Before ANY deletion:

1. **Git check**: Warn if no version control
2. **Uncommitted changes**: Show and confirm
3. **Create backup list**: Log files to be moved/deleted
4. **Dry run option**: Preview all changes first

## Examples

### Example 1: Downloads Cleanup

**User**: "My Downloads folder has 500+ files"

**Process**:
1. Analyze: Find patterns (work docs, installers, images)
2. Propose: Work/, Personal/, Installers/, Archive/
3. Confirm: User approves plan
4. Execute: Move files to appropriate folders
5. Result: 500 files → 4 organized folders

### Example 2: Duplicate Removal

**User**: "Find duplicates in Documents"

**Output**:
```markdown
# Found 23 Sets of Duplicates (156 MB total)

## Set 1: "report.pdf"
- `/Documents/report.pdf` (2.3 MB, 2024-03-15)
- `/Documents/old/report.pdf` (2.3 MB, 2024-03-15)
- `/Desktop/report.pdf` (2.3 MB, 2024-03-10)

**Recommendation**: Keep `/Documents/report.pdf`
Delete the other 2 copies?
```

### Example 3: Project Structure

**User**: "Review my ~/Projects directory"

**Output**:
```markdown
# Analysis of ~/Projects

## Issues Found
- Mix of active and archived projects (3+ years old)
- No consistent naming convention
- Duplicate project folders (project-v1, project-v2, project-old)

## Proposed Structure

```
Projects/
├── Active/
│   ├── client-work/
│   └── side-projects/
├── Archive/
│   ├── 2023/
│   └── 2024/
└── Templates/
```

Want me to implement this?
```

## Best Practices

### Folder Naming
- Use clear, descriptive names
- Use hyphens (not spaces): `project-name`
- Be specific: `client-proposals` not `docs`
- Use prefixes for ordering: `01-active`, `02-archive`

### File Naming
- Include dates: `2026-01-13-meeting-notes.md`
- Be descriptive: `q4-financial-report.xlsx`
- Remove download artifacts: `doc (1).pdf` → `doc.pdf`

### When to Archive
- Projects not touched in 6+ months
- Completed work for reference
- Files hesitant to delete (archive first)

## Related Skills

- `cleanup` - Remove dead code and dependencies
- `capture-state` - Capture current state before organizing
