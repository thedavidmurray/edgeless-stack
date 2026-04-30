---
name: memory-system
description: >
  Initialize and manage a layered memory architecture for session continuity.
  Use at session start to restore context, when searching past sessions,
  or checking memory health.
metadata:
  tags: [memory, context, session, continuity, initialization, recall, history]
  tier: general
  domain: kernel
when_to_apply: >
  When initializing a new session, recalling past context, searching across
  previous sessions, or checking memory health
---

# Memory System Skill

## When to Use

- Session start -- always initialize to restore prior context
- User asks "what did we do before" or "catch me up"
- Agent needs to search past sessions or decisions
- Checking memory system health
- Explicit `/memory` command

## Memory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY COORDINATOR                        │
│                  (Unified Search & Orchestration)            │
├───────────────────┬───────────────┬─────────────────────────┤
│ Vector Store      │  Fast Cache   │      Knowledge Base     │
│ (Primary)         │ (Neural/KV)   │   (Structured Docs)     │
│                   │               │                         │
│ Semantic search   │ Fast lookups  │   Long-term docs        │
│ Embeddings        │ Pattern match │   Markdown files        │
└───────────────────┴───────────────┴─────────────────────────┘
```

<!-- CUSTOMIZE: Replace with your memory backend(s).
     Common options:
     - ChromaDB (local vector store)
     - Pinecone / Weaviate (cloud vector store)
     - SQLite (simple key-value)
     - Plain markdown files (simplest)
     - Claude Code memory files (~/.claude/projects/...)
-->

### Core Components

- **session_initializer** -- Main memory restoration system
- **memory_coordinator** -- Unified search and orchestration
- **connectors/** -- Individual memory system connectors
- **configs/** -- Configuration files

## Initialization Sequence

### Step 1: Load Configuration

```python
# CUSTOMIZE: Set your config path
config_path = ".claude/memory/configs/memory_sources.yaml"
```

### Step 2: Initialize Connectors

```python
from session_initializer import SessionInitializer
initializer = SessionInitializer()
status = initializer.initialize()
```

### Step 3: Health Check

```python
from memory_coordinator import MemoryCoordinator
coordinator = MemoryCoordinator()
health = coordinator.get_system_health()
```

### Step 4: Load Context

```python
results = coordinator.search("session context", limit=20)
```

## Memory Sources

### Vector Store (Primary)

<!-- CUSTOMIZE: Your vector store setup -->
- **Collection**: `unified_knowledge`
- **Features**: Semantic search, embeddings, metadata filtering

### Structured Knowledge Base

<!-- CUSTOMIZE: Your knowledge base location -->
- **Path**: `knowledge/` or Obsidian vault
- **Features**: Structured documentation, insights, procedures

### Agent Memory Files

<!-- CUSTOMIZE: Your agent memory location -->
- **Path**: `.claude/projects/.../memory/`
- **Features**: Persistent markdown files with YAML frontmatter

## Quick Commands

```bash
# CUSTOMIZE: Adapt these to your project structure

# Run memory initialization
python .claude/memory/session_initializer.py

# Test connectivity
python .claude/memory/session_initializer.py --test-only

# Search memory
python -c "from memory_coordinator import MemoryCoordinator; mc = MemoryCoordinator(); print(mc.search('query'))"
```

## Performance Targets

| System | Target | Notes |
|--------|--------|-------|
| Initialization | < 2s | Should not block session start |
| Context Loading | < 3s | Async where possible |
| Memory Search | < 1s | Use vector similarity |

## Error Handling

### Graceful Degradation

- Memory system continues if individual connectors fail
- Fallback mechanisms for each memory source
- Comprehensive error logging and recovery

### Recovery Procedures

```bash
# Reinitialize failing connector
python -c "from session_initializer import SessionInitializer; SessionInitializer()._initialize_connectors()"

# Clear cache and restart
rm -rf .claude/memory/__pycache__/
python .claude/memory/session_initializer.py
```

## Integration Points

- **Hooks**: Pre-session (memory init), post-session (context archiving)
- **MCP Servers**: Vector store queries via MCP tools
- **Cron Jobs**: Automated maintenance and consolidation

## Related Skills

- `system-status` -- Health monitoring
- `research-deep` -- Knowledge retrieval
- `retrospective-learning` -- Persisting session learnings
