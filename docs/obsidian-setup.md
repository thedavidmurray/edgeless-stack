# Obsidian Vault Setup

The knowledge vault layer of the Edgeless Stack uses [Obsidian](https://obsidian.md) as the human-readable interface to your agent's memory. This guide covers installation, recommended plugins, and how to customize the vault for your workflow.

## Quick Start

1. **Install Obsidian**: [obsidian.md/download](https://obsidian.md/download) (free for personal use)
2. **Open vault**: File > Open Vault > Select the `vault_template/` directory from this repo
3. **Install community plugins**: Settings > Community Plugins > Browse (see list below)
4. **Connect to your agent**: Set `OBSIDIAN_VAULT_PATH` in your `.env` file

## Vault Structure

The template vault follows a numbered-folder taxonomy:

```
vault_template/
├── 00-Inbox/          <- Raw captures land here (agent writes, you review)
│   ├── rss/           <- RSS feed items
│   ├── youtube/       <- YouTube summaries
│   └── web/           <- Archived web pages
├── 01-Knowledge/      <- Promoted, reviewed content (high trust)
│   ├── Architecture/
│   ├── Operations/
│   └── Research/
└── 02-Archive/        <- Completed/stale items (low priority, still searchable)
```

<!-- CUSTOMIZE: Add or rename folders to match your domain. The numbered prefix
     keeps folders in a logical order. Common additions:
     - 03-Projects/    (active project notes)
     - 04-People/      (CRM-style people notes)
     - 05-Templates/   (reusable note templates)
-->

## Recommended Plugins

These are the plugins that make the vault work as an AI knowledge system. Install via Settings > Community Plugins > Browse.

### Essential (install these first)

| Plugin | Why | Config Notes |
|--------|-----|-------------|
| **Dataview** | Query your vault like a database. List all notes by tag, date, status. | Enable JavaScript queries for advanced use |
| **Templater** | Template engine for consistent note structure. Better than core Templates plugin. | Set template folder to `_templates/` |
| **Quick Add** | Macro system for common captures (new inbox item, new knowledge note) | Set up macros for your most common note types |
| **Local REST API** | Lets your agent read/write vault notes programmatically | Default port 27124. Required for agent vault access |

### Recommended (install when you need them)

| Plugin | Why | Config Notes |
|--------|-----|-------------|
| **Periodic Notes** | Daily/weekly/monthly notes for session logs and reviews | Link to your daily template |
| **Calendar** | Visual calendar for daily notes. Click a date to create/open its note. | Pairs with Periodic Notes |
| **Tag Wrangler** | Rename, merge, and manage tags across your vault | Essential once vault exceeds ~500 notes |
| **Obsidian Git** | Auto-commit vault changes to git. Backup + version history. | Set auto-commit interval to 5-10 minutes |
| **Advanced Tables** | Better table editing in markdown | Quality of life improvement |
| **Kanban** | Turn any note into a Kanban board. Good for tracking task status. | Use for backlog visualization |

### For Power Users

| Plugin | Why | Config Notes |
|--------|-----|-------------|
| **Excalidraw** | Embedded diagrams and visual thinking inside notes | Heavy plugin -- only install if you use diagrams regularly |
| **Database Folder** (DB Folder) | Notion-style database views for structured data | Alternative to Dataview for visual users |
| **Smart Connections** | AI-powered similar note suggestions. Surfaces related knowledge. | Uses local embeddings, no API key needed |
| **Linter** | Auto-format notes on save (YAML frontmatter, headings, spacing) | Configure rules in settings |

## Connecting Your Agent to the Vault

### Option 1: Direct File Access (simplest)

Your agent writes markdown files directly to the vault directory. This is how the Edgeless Stack works by default.

```bash
# In .env
OBSIDIAN_VAULT_PATH=/path/to/your/vault

# Agent writes a note
echo "---
title: API Architecture Decision
tags: [architecture, api]
date: $(date -u +%Y-%m-%dT%H:%M:%S)
---
Selected FastAPI over Flask for the knowledge API..." > "$OBSIDIAN_VAULT_PATH/00-Inbox/api-decision.md"
```

### Option 2: Local REST API (recommended for production)

Install the **Local REST API** plugin, then your agent can read/write via HTTP:

```bash
# Read a note
curl -s http://localhost:27124/vault/00-Inbox/api-decision.md \
  -H "Authorization: Bearer your-api-key"

# Create/update a note
curl -s -X PUT http://localhost:27124/vault/00-Inbox/new-note.md \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: text/markdown" \
  -d "# New Note\nContent here..."
```

<!-- CUSTOMIZE: Set your API key in the Local REST API plugin settings.
     Add it to your .env as OBSIDIAN_REST_API_KEY -->

### Option 3: Obsidian CLI (advanced)

For headless/automated access, use the [obsidian-cli](https://github.com/Yakitrak/obsidian-cli):

```bash
# Install
go install github.com/Yakitrak/obsidian-cli@latest

# Usage
obsidian-cli note create "00-Inbox/my-note" --content "# Title\nBody"
obsidian-cli note search "API architecture"
```

## Note Format Conventions

All notes in the vault should follow this frontmatter pattern:

```markdown
---
title: Descriptive Title
tags: [tag1, tag2]
date: 2026-01-15T10:30:00
source: agent|human|rss|youtube|web
trust: high|medium|low
---

# Descriptive Title

Content here...
```

<!-- CUSTOMIZE: Add fields relevant to your domain:
     - project: which project this relates to
     - status: draft|review|published
     - priority: p0|p1|p2
     - author: who created this note
-->

### Trust Levels

| Trust | Meaning | Who writes | Review needed? |
|-------|---------|-----------|---------------|
| **high** | Verified, human-reviewed | Human or promoted from medium | No |
| **medium** | Agent-generated, plausible | Agent (automated captures) | Yes -- review before acting on |
| **low** | Raw capture, may be noisy | Automated ingestion | Yes -- may be garbage |

Notes in `00-Inbox/` default to `trust: low`. When you review and move them to `01-Knowledge/`, update to `trust: high`.

## Vault Maintenance

### Weekly Review (15 minutes)

1. **Inbox zero**: Review `00-Inbox/`, promote good notes to `01-Knowledge/`, archive stale ones to `02-Archive/`
2. **Tag cleanup**: Use Tag Wrangler to merge similar tags
3. **Orphan check**: Dataview query to find notes with no backlinks:
   ```dataview
   LIST FROM ""
   WHERE length(file.inlinks) = 0 AND !contains(file.folder, "02-Archive")
   SORT file.mtime DESC
   LIMIT 20
   ```

### Monthly Maintenance

1. **Archive old inbox items**: Anything in `00-Inbox/` older than 30 days
2. **Review knowledge quality**: Spot-check `01-Knowledge/` notes for accuracy
3. **Plugin updates**: Settings > Community Plugins > Check for updates

## Scaling Tips

- **Under 1,000 notes**: Default setup works fine
- **1,000-5,000 notes**: Enable Obsidian Git for backups, use Tag Wrangler
- **5,000+ notes**: Add Database Folder or Dataview for structured queries, consider Smart Connections for AI-assisted navigation
- **10,000+ notes**: Split into multiple vaults by domain, or use a strict folder taxonomy

---

*Part of the [Edgeless Stack](https://github.com/thedavidmurray/edgeless-stack)*
