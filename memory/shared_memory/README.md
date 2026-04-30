# Shared Memory: 3-Layer Trust Model

Cross-runtime memory system that lets multiple AI agents (Claude Code, Codex, Hermes, custom agents) share persistent context through a unified contract.

## Architecture

Memory flows through three layers with increasing trust and durability:

### Layer 1: Episodic (SQLite) -- Fast, Append-Only

Every agent writes raw episodes here. This is the hot path: low-latency, local SQLite, no external dependencies. Episodes are timestamped, tagged, and scoped by agent/project/session. Full-text search (FTS5) is used when available, with automatic LIKE fallback.

**Trust level**: Low. Any agent can write anything. Episodes are raw observations, not validated knowledge.

### Layer 2: Semantic (ChromaDB) -- Promoted, Deduplicated

Episodic memories that prove useful get *promoted* into a vector store via the promotion queue. Promotions are:
- **Queued** by agents or humans who judge an episode worth persisting
- **Deduplicated** by content hash (same content never indexed twice)
- **Processed** by the `PromotionWorker` in batch passes

**Trust level**: Medium. Content has been explicitly nominated for long-term storage. Semantic search makes it retrievable by meaning, not just keywords.

### Layer 3: Curated (Pluggable) -- Human-Verified

The `curated_search` slot accepts any backend -- an Obsidian vault, a knowledge base, a wiki. This layer holds knowledge that humans have reviewed and organized.

**Trust level**: High. Content has been validated by a human or a trusted editorial process.

## Quick Start

```python
from shared_memory import SharedMemoryService, WriteEpisodeRequest, SourceRuntime

# Minimal setup: episodic memory only (no vector store needed)
svc = SharedMemoryService.from_sqlite_path("./my_memory.sqlite3")

# Write an episode
receipt = svc.write_episode(WriteEpisodeRequest(
    agent="my-agent",
    source_runtime=SourceRuntime.OTHER,
    session_id="session-001",
    project="my-project",
    content="User prefers concise answers over verbose explanations.",
    tags=["preference", "communication-style"],
    confidence=0.8,
))

# Search across all layers
from shared_memory import SearchMemoryRequest
results = svc.search_memory(SearchMemoryRequest(query="communication preferences"))
```

## Adding Semantic Search (Optional)

```python
from shared_memory import SharedMemoryService
from shared_memory.adapters import build_chromadb_search_adapter

svc = SharedMemoryService.from_sqlite_path(
    "./my_memory.sqlite3",
    semantic_search=build_chromadb_search_adapter(
        chroma_path="./my_chroma_data",
        collection_name="unified_knowledge",
    ),
)
```

## Configuration

All paths are configurable via environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `SHARED_MEMORY_DB_PATH` | `./data/shared_memory/events.sqlite3` | SQLite database location |
| `CHROMA_DB_PATH` | `./data/chroma` | ChromaDB persistence directory |

## HTTP API

An optional FastAPI server exposes the full contract over HTTP:

```bash
pip install fastapi uvicorn
uvicorn shared_memory.api:app --host 127.0.0.1 --port 8042
```

Endpoints: `POST /episodes`, `POST /search`, `POST /context`, `POST /promotions`, `POST /promotions/process`, `GET /health`.
