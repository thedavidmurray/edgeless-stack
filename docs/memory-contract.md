# Memory Contract

The Edgeless Stack uses a 3-layer memory system. Each layer has different characteristics, and understanding them is critical to building agents that don't confabulate.

## The Three Layers

### Layer 1: Episodic Ledger (SQLite)

**Trust: HIGH** | **Storage: Append-only** | **Query: SQL**

The ground truth. Every significant agent action is logged as an episode. Episodes are append-only -- agents can never modify or delete them.

```python
from memory.shared_memory import SharedMemoryService

service = SharedMemoryService.from_sqlite_path("data/shared_memory/events.sqlite3")

# Write (append-only)
service.write_episode(
    agent="Builder",
    memory_type="decision",
    content="Selected FastAPI over Flask for the knowledge API",
    tags=["architecture", "api"],
    confidence=0.9,
)

# Read (full SQL access)
episodes = service.search_episodes(
    query="API architecture",
    agent="Builder",
    limit=10,
)
```

**What to log:**
- Decisions and their rationale
- Task completions and outcomes
- Errors and recovery actions
- Configuration changes

**What NOT to log:**
- Routine tool calls (use cost tracker hook instead)
- Raw content (store in vault, reference by path)
- Anything you wouldn't want to defend in a post-mortem

### Layer 2: Semantic Index (ChromaDB)

**Trust: MEDIUM** | **Storage: Vector embeddings** | **Query: Similarity search**

The search layer. Content from the ledger and vault gets embedded for semantic retrieval. Useful for finding related content, but may surface stale or irrelevant results.

```python
# Promotion worker pushes high-confidence episodes to ChromaDB
from memory.shared_memory import PromotionWorker

worker = PromotionWorker(
    sqlite_path="data/shared_memory/events.sqlite3",
    chroma_host="localhost",
    chroma_port=8000,
)

# Promote episodes with confidence > 0.7
worker.promote_recent(min_confidence=0.7)

# Search semantically
results = service.search_memory(
    query="how to handle API rate limits",
    limit=5,
)
```

**Why medium trust:**
- Embeddings can surface tangentially related content
- Old entries may no longer be accurate
- Vector similarity != semantic correctness

<!-- CUSTOMIZE: You can skip ChromaDB entirely and use only SQLite + Vault.
     The system degrades gracefully -- semantic search just won't be available. -->

### Layer 3: Curated Vault (Obsidian/Markdown)

**Trust: HIGH (after review)** | **Storage: Markdown files** | **Query: Full-text search**

The human layer. Agents write to an inbox. Humans review, edit, and promote notes to the knowledge directory. Once promoted, vault content is high-trust.

```
vault/
├── 00-Inbox/          <- Agent writes here (trust: low)
├── 01-Knowledge/      <- Human promotes here (trust: high)
└── 02-Archive/        <- Stale/completed items (trust: low)
```

**Trust flow:**
1. Agent writes raw capture to `00-Inbox/` (trust: low)
2. Human reviews, edits, adds context
3. Human moves to `01-Knowledge/` (trust: high)
4. Periodically, stale knowledge moves to `02-Archive/`

## Memory Contract Rules

These rules prevent the most common agent memory failures:

### Rule 1: Never Trust Your Own Outputs

An agent that reads its own previous outputs and treats them as ground truth will confabulate. Always:
- Check the ledger for what actually happened (not what you planned)
- Verify file existence before referencing cached paths
- Re-read current state instead of relying on remembered state

### Rule 2: Append, Don't Update

The episodic ledger is append-only. If a decision changes, write a new episode that supersedes the old one. Don't update the original.

```python
# Right: new episode superseding old decision
service.write_episode(
    agent="Builder",
    memory_type="decision",
    content="Switched from FastAPI to Flask (FastAPI's async caused issues with SQLite)",
    tags=["architecture", "api", "supersedes"],
    confidence=0.85,
)

# Wrong: updating the original episode (this is not possible by design)
```

### Rule 3: Trust Levels Are Not Optional

Every piece of data has a trust level. Low-trust data informs decisions; high-trust data grounds them.

| Source | Trust | Can Ground Decisions? |
|--------|-------|-----------------------|
| SQLite episodic ledger | High | Yes |
| Human-reviewed vault notes | High | Yes |
| ChromaDB search results | Medium | Only with verification |
| Agent inbox captures | Low | No -- review first |
| Agent self-reports | Low | Never without evidence |

### Rule 4: Degrade Gracefully

If ChromaDB is down, the system still works -- you just lose semantic search. If the vault is empty, the agent still has the ledger. Design for partial availability.

```python
# The service handles this automatically
service = SharedMemoryService.from_sqlite_path("data/shared_memory/events.sqlite3")
# If ChromaDB is unreachable, search_memory falls back to SQLite full-text search
```

## Maintenance

### Periodic Promotion

Run the promotion worker periodically to push high-confidence episodes to ChromaDB:

```bash
python3 -c "
from memory.shared_memory import PromotionWorker
worker = PromotionWorker('data/shared_memory/events.sqlite3')
worker.promote_recent(min_confidence=0.7, max_age_days=30)
"
```

### Vault Review

Weekly: review `00-Inbox/`, promote or archive. See [Obsidian Setup](obsidian-setup.md) for the full review workflow.

### Ledger Backup

The SQLite database is a single file. Back it up regularly:

```bash
cp data/shared_memory/events.sqlite3 backups/events-$(date +%Y%m%d).sqlite3
```

---

*Part of the [Edgeless Stack](https://github.com/thedavidmurray/edgeless-stack)*
