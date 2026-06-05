# Architecture

The Edgeless Stack is a 5-layer system for building AI agents that persist, protect, and compound their knowledge over time.

```
┌─────────────────────────────────────────────────┐
│  Layer 5: AGENT                                 │
│  Cron jobs, Agent Bus, orchestration             │
├─────────────────────────────────────────────────┤
│  Layer 4: ORCHESTRATION                         │
│  Skills, session planning, task management       │
├─────────────────────────────────────────────────┤
│  Layer 3: KNOWLEDGE                             │
│  Obsidian vault, RSS/YouTube ingestion, search   │
├─────────────────────────────────────────────────┤
│  Layer 2: TOOLS                                 │
│  Hooks (safety), completion verification         │
├─────────────────────────────────────────────────┤
│  Layer 1: INFRASTRUCTURE                        │
│  SQLite ledger, ChromaDB vectors, config         │
└─────────────────────────────────────────────────┘
```

## Layer 1: Infrastructure

The foundation. Append-only storage that agents can't accidentally destroy.

- **SQLite Episodic Ledger**: Every agent action logged. Append-only (agents can write, never delete). Ground truth for "what actually happened."
- **ChromaDB Vector Store**: Semantic search over all memory. Medium trust -- may surface stale entries. Optional but recommended.
- **Configuration**: `.env` file + `CLAUDE.md` project config. Single source of truth for all settings.

## Layer 2: Tools (Hooks)

The safety net. Hooks intercept every tool call and enforce guardrails.

- **PreToolUse hooks** fire before a tool executes. Can block destructive operations (`rm -rf`, `git push --force`, `DROP TABLE`).
- **PostToolUse hooks** fire after. Can verify outcomes, archive results, track costs.
- **Session lifecycle hooks** load context at start, save summaries at end.

Hooks are Python scripts that read JSON from stdin and write JSON to stdout. They run in-process with zero latency. See `hooks/` for the full set.

## Layer 3: Knowledge

The vault. Where agents store and retrieve structured knowledge.

- **Obsidian Vault**: Human-readable markdown files organized by topic. Agents write to an inbox; humans review and promote.
- **Ingestion Pipelines**: RSS feeds, YouTube transcripts, web archives flow into the vault automatically.
- **Trust Hierarchy**: Inbox (low trust) -> Knowledge (medium, reviewed) -> Archive (low priority). Agents never blindly trust their own outputs.

## Layer 4: Orchestration (Skills)

The capabilities layer. Skills encode domain knowledge and workflow patterns.

- **Core skills** (always loaded): Memory management, session planning, task verification, cleanup.
- **Domain skills** (on demand): Code review, research, content writing, TDD. Loaded only when relevant to save context.
- **Manifest**: `skills/_manifest.md` indexes all skills with descriptions and trigger conditions.

Skills are markdown files. They don't execute code -- they provide instructions that shape how the agent approaches work.

## Layer 5: Agent

The autonomous layer. Agents that run without human presence.

- **Cron Jobs**: Scheduled tasks with lockfile protection. Health checks, email triage, knowledge consolidation.
- **Agent Bus**: MCP server for inter-agent messaging. Agents discover each other and coordinate work.
- **Golden Rule**: Silence means success. Agents only alert humans when something needs attention.

## Data Flow

```
External Sources (RSS, email, YouTube, web)
       │
       ▼
  ┌─────────┐    ┌──────────────┐
  │  Cron   │───>│  Vault Inbox │──── Human review ───> Knowledge
  │  Jobs   │    │  (low trust) │                       (high trust)
  └────┬────┘    └──────────────┘
       │
       ▼
  ┌─────────┐    ┌──────────────┐
  │  Hooks  │───>│ SQLite Ledger│──── Ground truth
  │ (guard) │    │ (append-only)│
  └─────────┘    └──────────────┘
       │
       ▼
  ┌─────────┐    ┌──────────────┐
  │  Agent  │<──>│  ChromaDB    │──── Semantic search
  │ Session │    │  (vectors)   │
  └─────────┘    └──────────────┘
```

## Design Principles

1. **Append-only over CRUD**: Agents can create and read. They never update or delete ground truth. This prevents confabulation -- the ledger is an honest record.

2. **Trust levels, not access levels**: Every piece of data has a trust level. Low-trust data is useful context but never grounds a decision. High-trust data comes from humans or verified agent outputs.

3. **Hooks over hope**: Safety isn't a prompt instruction ("please don't delete things"). It's a runtime check that blocks the action before it happens. Hooks are the enforcement mechanism.

4. **Skills over prompts**: Reusable behavior patterns beat one-off instructions. Skills compound over time as you refine them. Prompts are fire-and-forget.

5. **Silence means success**: Healthy systems don't need to announce every action. If a cron job runs and nothing is wrong, it produces no output. Alerts only fire when something needs human attention.

---

*Part of the [Edgeless Stack](https://github.com/thedavidmurray/edgeless-stack)*
