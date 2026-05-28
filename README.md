# Edgeless Stack

A complete AI agent infrastructure. Memory that persists, hooks that protect, skills that compound, and agents that run while you sleep.

This is the system behind [Edgeless Lab](https://edgelesslab.com) -- extracted, documented, and ready to deploy.

## What You Get

| Layer | What | Why |
|-------|------|-----|
| **Memory** | SQLite episodic ledger + ChromaDB vectors + markdown vault | Agents remember across sessions. Not just context -- structured, searchable, trust-leveled memory. |
| **Hooks** | 6 production safety hooks | Agents don't run `rm -rf`, don't skip verification, don't lie about completion. |
| **Skills** | 12 core skills + domain extensions | Reusable capabilities: planning, cleanup, research, memory management, code review. |
| **Cron** | 5 scheduling patterns + wrapper | Agents work while you don't. Health checks, knowledge triage, email processing. |
| **Agent Bus** | MCP-based inter-agent messaging | Multiple agents coordinate without stepping on each other. |
| **Templates** | CLAUDE.md, SOUL.md, MEMORY.md | Drop into any project and start building. |

## Quick Start (15 minutes)

```bash
# Clone
git clone https://github.com/edgeless-ai/edgeless-stack.git
cd edgeless-stack

# Configure
cp .env.example .env
# Edit .env with your API keys

# Install hooks into your Claude Code project
./install.sh /path/to/your/project

# Or run the full stack with Docker
docker compose up -d
```

### What `install.sh` does

1. Copies hooks to your project's `.claude/hooks/`
2. Registers them in `.claude/settings.json`
3. Sets up the memory directory structure
4. Creates a starter `CLAUDE.md` from the template
5. Initializes the SQLite episodic ledger
6. Prints a verification checklist

No magic. Every file it touches is visible and editable.

## Architecture

```
Your Project
├── .claude/
│   ├── hooks/              <- Safety & automation (from this repo)
│   │   ├── damage-control.py
│   │   ├── completion-verifier.py
│   │   └── session-lifecycle.py
│   ├── skills/             <- Agent capabilities (from this repo)
│   │   ├── _manifest.md
│   │   └── core/
│   └── memory/             <- Persistent context (from this repo)
│       ├── MEMORY.md
│       └── session_initializer.py
├── data/
│   └── shared_memory/      <- SQLite episodic ledger
│       └── events.sqlite3
├── CLAUDE.md               <- Project configuration (template provided)
└── chroma-data/            <- Vector embeddings (optional)
```

## Memory System

Three layers, each with different trust levels:

| Layer | Storage | Trust | Use |
|-------|---------|-------|-----|
| **Episodic Ledger** | SQLite (append-only) | High | Ground truth. What actually happened. |
| **Semantic Index** | ChromaDB vectors | Medium | Search results. May surface stale entries. |
| **Curated Vault** | Markdown files | High | Human-reviewed knowledge. Quality-controlled. |

The memory system initializes at session start, loads context from all layers, and provides a unified search interface. If any layer is unavailable, the system degrades gracefully.

```python
# Write an episode (append-only, high trust)
from memory.shared_memory import SharedMemoryService

service = SharedMemoryService.from_sqlite_path("data/shared_memory/events.sqlite3")
service.write_episode(
    agent="Builder",
    memory_type="decision",
    content="Selected FastAPI over Flask for the knowledge API",
    tags=["architecture", "api"],
    confidence=0.9,
)

# Search across all layers
results = service.search_memory(query="API architecture decisions", limit=5)
```

## Hooks

Hooks are Python scripts that run before or after Claude Code tool calls. They are the safety net.

### Included Hooks

| Hook | Trigger | What It Does |
|------|---------|-------------|
| `damage-control.py` | PreToolUse | Blocks destructive commands (`rm -rf`, `git push --force`, `DROP TABLE`). Configurable patterns. |
| `completion-verifier.py` | PostToolUse | Requires evidence before accepting task completion. No "I think I did it." |
| `session-lifecycle.py` | Start/Stop | Loads memory at start, saves session summary at end. |
| `vault-archiver.py` | PostToolUse | Archives fetched web content to the knowledge vault. |
| `cost-tracker.py` | PostToolUse | Tracks token usage and costs per session. |
| `taxonomy-guard.py` | PreToolUse | Prevents writes to wrong directories. Enforces folder structure. |

### Writing Your Own

```python
#!/usr/bin/env python3
"""Example: block writes to production config files."""

import json, sys

def main():
    event = json.loads(sys.stdin.read())
    tool = event.get("tool_name", "")
    input_data = event.get("tool_input", {})

    if tool == "Write" and "/production/" in input_data.get("file_path", ""):
        print(json.dumps({
            "decision": "block",
            "reason": "Cannot write to production config files directly"
        }))
    else:
        print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
```

See `hooks/examples/` for more patterns.

## Skills

Skills are markdown-defined capabilities that Claude Code loads on demand. They encode domain knowledge, workflow patterns, and behavioral rules. **106 skills currently shipped** (5 core + 101 domain). See `skills/_manifest.md` for the full index.

Run `python3 scripts/validate.py` before committing to catch frontmatter drift, manifest desync, or personal-path leaks. CI runs the same check on PRs touching `skills/`.

```markdown
---
name: research-deep
description: Multi-source research with citation tracking
domain: knowledge
---

When the user asks for deep research on a topic:

1. Search the local vault first (check existing knowledge)
2. Search ChromaDB for related entries
3. Use web search for current information
4. Cross-reference sources, note conflicts
5. Write findings to vault with source citations
6. Update the knowledge index
```

### Core Skills (always loaded)

- `memory-system` -- Initialize and query the 3-layer memory
- `session-planning` -- Break work into verifiable steps
- `cleanup` -- Post-task housekeeping
- `verify-completion` -- Evidence-based task verification
- `retrospective` -- Session learning and feedback capture

### Domain Skills (loaded on demand)

- `code-review` -- Systematic review with checklist
- `research-deep` -- Multi-source investigation
- `content-research-writer` -- Research-to-publication pipeline
- `test-driven-development` -- TDD workflow patterns

## Cron Jobs

For agents that run 24/7 on a VPS. Each pattern follows the golden rule: **silence means success**.

```bash
# Run a cron job with the lockfile wrapper (prevents overlap)
./cron/cron-wrapper.sh "health-check" ./cron/health-check.sh

# Example crontab
0 */6 * * * /path/to/cron/cron-wrapper.sh "health" /path/to/cron/health-check.sh
0 */4 * * * /path/to/cron/cron-wrapper.sh "email" /path/to/cron/email-triage.sh
0 16  * * * /path/to/cron/cron-wrapper.sh "digest" /path/to/cron/knowledge-digest.sh
```

## Agent Bus (MCP Server)

Multi-agent coordination via an MCP server. Sessions discover each other and pass messages.

```bash
# Start the hub
cd mcp-servers/agent-bus && bun run src/index.ts

# In Claude Code, agents can:
# - agent_bus_list: See who's online
# - agent_bus_send: Message another session
# - agent_bus_broadcast: Notify all sessions
```

## Docker Deployment

For running the full stack (ChromaDB + Agent Bus + cron scheduler):

```bash
docker compose up -d

# Services:
# - chromadb:    localhost:8000  (vector database)
# - agent-bus:   localhost:9800  (inter-agent messaging)
# - cron:        (scheduled job runner)
```

## Project Structure

```
edgeless-stack/
├── README.md
├── LICENSE
├── .env.example
├── docker-compose.yml
├── install.sh
│
├── memory/
│   ├── shared_memory/          # SQLite episodic ledger
│   │   ├── __init__.py
│   │   ├── service.py          # Unified memory interface
│   │   ├── models.py           # Data schemas
│   │   ├── sqlite_store.py     # Append-only storage
│   │   └── promotion_worker.py # ChromaDB promotion
│   └── vault_template/         # Starter vault structure
│       ├── 00-Inbox/
│       ├── 01-Knowledge/
│       └── 02-Archive/
│
├── hooks/
│   ├── damage-control.py
│   ├── completion-verifier.py
│   ├── session-lifecycle.py
│   ├── vault-archiver.py
│   ├── cost-tracker.py
│   ├── taxonomy-guard.py
│   ├── lib/                    # Shared hook utilities
│   └── examples/               # Additional hook patterns
│
├── skills/
│   ├── _manifest.md
│   ├── core/                   # Always-loaded skills
│   └── domains/                # On-demand skills
│
├── cron/
│   ├── cron-wrapper.sh
│   ├── health-check.sh
│   ├── knowledge-digest.sh
│   ├── email-triage.sh
│   └── cost-report.sh
│
├── mcp-servers/
│   └── agent-bus/              # Inter-agent messaging
│
├── templates/
│   ├── CLAUDE.md               # Project configuration
│   ├── SOUL.md                 # Agent personality
│   └── MEMORY.md               # Memory structure
│
└── docs/
    ├── architecture.md         # System design
    ├── memory-contract.md      # Memory layer specification
    ├── hooks-guide.md          # Writing custom hooks
    └── deployment.md           # VPS + Docker setup
```

## Built From Production

This stack runs 24/7 at [Edgeless Lab](https://edgelesslab.com):

- 16 active hooks guard every tool call
- 151 skills across 12 domains
- 3-layer memory with 30K+ knowledge entries
- 8 cron jobs processing email, RSS, YouTube, and system health
- 5 agents coordinating via the agent bus

The code in this repo is extracted from that system. Not a tutorial. Not a demo. Production infrastructure, simplified for reuse.

## Related

- [Claude Memory Kit](https://github.com/edgeless-ai/claude-memory-kit) -- Starter memory template (subset of this stack)
- [Claude Code Hooks](https://github.com/edgeless-ai/claude-code-hooks) -- Hook examples (subset of this stack)
- [Edgeless Lab Blog](https://edgelesslab.com/blog) -- Field notes from running this system
- [Products](https://edgelesslab.com/products) -- Deep-dive guides for specific components

## License

MIT
