# Vault Template

This is a starter vault for the Edgeless Stack knowledge layer. Open it with [Obsidian](https://obsidian.md) or any markdown editor.

## Structure

```
00-Inbox/        Raw captures from agents (low trust, needs review)
  rss/           RSS feed items
  youtube/       YouTube summaries and transcripts
  web/           Archived web pages

01-Knowledge/    Reviewed, promoted content (high trust)
  Architecture/  System design decisions
  Operations/    Runbooks, procedures, troubleshooting
  Research/      Investigated topics, findings

02-Archive/      Stale or completed items (still searchable)
```

## How It Works

1. **Agents write to `00-Inbox/`** -- every capture, summary, or finding lands here
2. **You review weekly** -- skim the inbox, promote good notes to `01-Knowledge/`
3. **Archive stale items** -- anything in inbox older than 30 days goes to `02-Archive/`

## Customizing

<!-- CUSTOMIZE: Add folders for your domain. Common additions: -->

- `03-Projects/` -- Active project notes and context
- `04-People/` -- CRM-style notes about collaborators, clients
- `05-Templates/` -- Reusable note templates (Templater plugin)
- `06-Daily/` -- Daily notes (Periodic Notes plugin)

See [Obsidian Setup](../../docs/obsidian-setup.md) for plugin recommendations.

## Note Format

All notes should include YAML frontmatter:

```markdown
---
title: Note Title
tags: [tag1, tag2]
date: 2026-01-15T10:30:00
source: agent|human|rss|youtube|web
trust: high|medium|low
---

# Note Title

Content here...
```
