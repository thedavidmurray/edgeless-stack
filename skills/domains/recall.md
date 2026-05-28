---
name: recall
description: >
  Search past Claude Code session transcripts for prior work on a topic.
  Headless equivalent of the Desktop-only
  `mcp__ccd_session_mgmt__search_session_transcripts` MCP tool. Greps the local
  JSONL transcript store at ~/.claude/projects/<encoded>/*.jsonl, returns JSON
  with session_id, mtime, match_count, and a context snippet per hit. Use before
  starting fresh work to check if David already solved this in an earlier
  session — prevents redoing investigations and surfaces forgotten context.
metadata:
  tags: [search, history, claude-code, transcripts]
  tier: task-specific
  domain: knowledge
when_to_apply: >
  When searching past Claude Code session transcripts for prior work on a topic.
---

# Recall — Past Session Transcript Search

Search the local Claude Code session transcript store for prior conversations
matching a query. Useful when David asks about something that "we discussed
before" or when investigating an error/topic that may have been resolved in
an earlier session.

## When to use

- Before starting a fresh investigation: "have we hit this error before?"
- When David references prior context: "remember when we set up X?"
- To find session IDs for `claude --resume <id>`
- To audit what's been tried on a topic across many sessions

## Script

`~/.hermes/scripts/recall.py` (Python 3.11)

## Invocation

```bash
python3.11 ~/.hermes/scripts/recall.py "<query>" [--limit 5] [--project <path>]
```

- `<query>` — substring (min 2 chars, case-insensitive). Searches user/assistant
  text content only, not tool calls or metadata.
- `--limit N` — max sessions to return, sorted most-recent-first (default: 5).
- `--project <path>` — defaults to `-Users-djm-claude-projects`. Pass an absolute
  path to auto-encode for other projects.

## Output

JSON array on stdout. Each entry:

```json
{
  "session_id": "ec4a3fdf-11c6-434b-b87d-da86026263c4",
  "mtime_iso": "2026-05-11T22:14:07+00:00",
  "match_count": 5,
  "first_snippet": "…matching text with context…"
}
```

## Examples

```bash
# Find sessions discussing Pamela
python3.11 ~/.hermes/scripts/recall.py "Pamela" --limit 3

# Search a different project's sessions
python3.11 ~/.hermes/scripts/recall.py "deploy error" --project /Users/djm/other-repo
```

## Privacy note

Transcript content may include secrets (Discord tokens, API keys) if they
appeared in prior conversations. Do NOT pipe `recall.py` output to logs,
Discord, or shared channels without redaction. Treat output as sensitive by
default.

## Why this exists

Hermes runs headless via `claude -p` and cannot use the Desktop MCP tool
`mcp__ccd_session_mgmt__search_session_transcripts`. The JSONL transcript
store is shared filesystem state, so any process can grep it. This skill
gives Hermes the same recall capability David has via the `/recall` slash
command.

## Related

- David-side: `/recall <query>` slash command at `~/.claude/commands/recall.md`
- Desktop MCP: `mcp__ccd_session_mgmt__search_session_transcripts`
- Cross-surface: both read the same JSONL store at
  `~/.claude/projects/-Users-djm-claude-projects/*.jsonl`
