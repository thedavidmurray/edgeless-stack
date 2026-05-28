---


name: chroma
description: >
  Open-source embedding database for AI applications. Store embeddings and
  metadata, perform vector and full-text search, filter by metadata. Simple
  4-function API. Scales from notebooks to production clusters. Use for semantic
  search, RAG applications, or document retrieval. Best for local development
  and open-source projects.
metadata:
  tags: [chromadb, vector-db, embeddings, rag]
  tier: task-specific
  domain: tooling
when_to_apply: >
  When storing or querying embeddings in ChromaDB for semantic search or RAG.
---
# Chroma - Open-Source Embedding Database

The AI-native database for building LLM applications with memory.

## When to use Chroma

**Use Chroma when:**
- Building RAG (retrieval-augmented generation) applications
- Need local/self-hosted vector database
- Want open-source solution (Apache 2.0)
- Prototyping in notebooks
- Semantic search over documents
- Storing embeddings with metadata

**Metrics**:
- **24,300+ GitHub stars**
- **1,900+ forks**
- **v1.3.3** (stable, weekly releases)
- **Apache 2.0 license**

**Use alternatives instead**:
- **Pinecone**: Managed cloud, auto-scaling
- **FAISS**: Pure similarity search, no metadata
- **Weaviate**: Production ML-native database
- **Qdrant**: High performance, Rust-based

## Quick start

### Installation

```bash
# Python
pip install chromadb

# JavaScript/TypeScript
npm install chromadb @chroma-core/default-embed
```

### Basic usage (Python)

```python
import chromadb

# Create client
client = chromadb.Client()

# Create collection
collection = client.create_collection(name="my_collection")

# Add documents
collection.add(
    documents=["This is document 1", "This is document 2"],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    ids=["id1", "id2"]
)

# Query
results = collection.query(
    query_texts=["document about topic"],
    n_results=2
)

print(results)
```

## Core operations

### 1. Create collection

```python
# Simple collection
collection = client.create_collection("my_docs")

# With custom embedding function
from chromadb.utils import embedding_functions

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-key",
    model_name="text-embedding-3-small"
)

collection = client.create_collection(
    name="my_docs",
    embedding_function=openai_ef
)

# Get existing collection
collection = client.get_collection("my_docs")

# Delete collection
client.delete_collection("my_docs")
```

### 2. Add documents

```python
# Add with auto-generated IDs
collection.add(
    documents=["Doc 1", "Doc 2", "Doc 3"],
    metadatas=[
        {"source": "web", "category": "tutorial"},
        {"source": "pdf", "page": 5},
        {"source": "api", "timestamp": "2025-01-01"}
    ],
    ids=["id1", "id2", "id3"]
)

# Add with custom embeddings
collection.add(
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    documents=["Doc 1", "Doc 2"],
    ids=["id1", "id2"]
)
```

### 3. Query (similarity search)

```python
# Basic query
results = collection.query(
    query_texts=["machine learning tutorial"],
    n_results=5
)

# Query with filters
results = collection.query(
    query_texts=["Python programming"],
    n_results=3,
    where={"source": "web"}
)

# Query with metadata filters
results = collection.query(
    query_texts=["advanced topics"],
    where={
        "$and": [
            {"category": "tutorial"},
            {"difficulty": {"$gte": 3}}
        ]
    }
)

# Access results
print(results["documents"])      # List of matching documents
print(results["metadatas"])      # Metadata for each doc
print(results["distances"])      # Similarity scores
print(results["ids"])            # Document IDs
```

### 4. Get documents

```python
# Get by IDs
docs = collection.get(
    ids=["id1", "id2"]
)

# Get with filters
docs = collection.get(
    where={"category": "tutorial"},
    limit=10
)

# Get all documents
docs = collection.get()
```

### 5. Update documents

```python
# Update document content
collection.update(
    ids=["id1"],
    documents=["Updated content"],
    metadatas=[{"source": "updated"}]
)
```

### 6. Delete documents

```python
# Delete by IDs
collection.delete(ids=["id1", "id2"])

# Delete with filter
collection.delete(
    where={"source": "outdated"}
)
```

## Persistent storage

```python
# Persist to disk
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.create_collection("my_docs")
collection.add(documents=["Doc 1"], ids=["id1"])

# Data persisted automatically
# Reload later with same path
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("my_docs")
```

## Embedding functions

### Default (Sentence Transformers)

```python
# Uses sentence-transformers by default
collection = client.create_collection("my_docs")
# Default model: all-MiniLM-L6-v2
```

### OpenAI

```python
from chromadb.utils import embedding_functions

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-key",
    model_name="text-embedding-3-small"
)

collection = client.create_collection(
    name="openai_docs",
    embedding_function=openai_ef
)
```

### HuggingFace

```python
huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
    api_key="your-key",
    model_name="sentence-transformers/all-mpnet-base-v2"
)

collection = client.create_collection(
    name="hf_docs",
    embedding_function=huggingface_ef
)
```

### Custom embedding function

```python
from chromadb import Documents, EmbeddingFunction, Embeddings

class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        # Your embedding logic
        return embeddings

my_ef = MyEmbeddingFunction()
collection = client.create_collection(
    name="custom_docs",
    embedding_function=my_ef
)
```

## Metadata filtering

```python
# Exact match
results = collection.query(
    query_texts=["query"],
    where={"category": "tutorial"}
)

# Comparison operators
results = collection.query(
    query_texts=["query"],
    where={"page": {"$gt": 10}}  # $gt, $gte, $lt, $lte, $ne
)

# Logical operators
results = collection.query(
    query_texts=["query"],
    where={
        "$and": [
            {"category": "tutorial"},
            {"difficulty": {"$lte": 3}}
        ]
    }  # Also: $or
)

# Contains
results = collection.query(
    query_texts=["query"],
    where={"tags": {"$in": ["python", "ml"]}}
)
```

## LangChain integration

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Split documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(documents)

# Create Chroma vector store
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    persist_directory="./chroma_db"
)

# Query
results = vectorstore.similarity_search("machine learning", k=3)

# As retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
```

## LlamaIndex integration

```python
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
import chromadb

# Initialize Chroma
db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_or_create_collection("my_collection")

# Create vector store
vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Create index
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context
)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("What is machine learning?")
```

## Server mode (REQUIRED for Mac clients)

**Mac clients must use HttpClient** to connect through the launchd-managed server:

```python
import chromadb
from chromadb.config import Settings

# ✅ CORRECT: Connect through launchd-managed server
client = chromadb.HttpClient(
    host="localhost",
    port=8100,
    settings=Settings(anonymized_telemetry=False)
)
```

**Why**: The launchd agent (`com.example.chroma`) manages the server lifecycle on `localhost:8100` with data at `~/projects/chroma-data`. Using `HttpClient` ensures:
- All access goes through the managed server process
- No orphaned `chroma run` processes can spin up independently
- File locking is handled by the single server process

**Anti-pattern** (DO NOT USE on Mac):
```python
# ❌ WRONG: Bypasses the launchd-managed server
client = chromadb.PersistentClient(path="~/projects/chroma-data")
```

While `PersistentClient` with the correct path accesses the same database, it bypasses the server and risks spawning orphaned processes if `chroma run` is launched independently.

**Existing scripts may still use `PersistentClient`.** If you discover scripts writing to a hardcoded `chroma-data` path while the live server runs on port 8100, those scripts are creating a separate invisible database. See `references/persistentclient-migration.md` for the audit, patch, and verification workflow used to migrate production scripts (`knowledge_spine_upsert.py`, `knowledge_spine_query.py`, `sync_memory_to_chroma.py`, `run_yt_triage.py`).

### V1 API deprecation note

Direct HTTP checks against the legacy v1 endpoints will fail:
```bash
# ❌ DEPRECATED — returns error
curl -s http://localhost:8100/api/v1/heartbeat
# → {"error":"Unimplemented","message":"The v1 API is deprecated. Please use /v2 apis"}
```

The Python `HttpClient` uses the v2 protocol internally and is unaffected. Verify server health via Python instead of curl:
```python
import chromadb
client = chromadb.HttpClient(host='localhost', port=8100)
print([c.name for c in client.list_collections()])  # ['hermes_learnings', ...]
```

### Server startup (launchd)

The launchd agent auto-starts the server:
- **Plist**: `~/Library/LaunchAgents/com.example.chroma.plist`
- **PID**: Check with `launchctl list | grep chroma`
- **Logs**: `~/claude-projects/logs/chroma-server.{log,err}`

### Emergency manual restart (launchd down)

When the launchd-managed server is not running and you need to bring ChromaDB back online immediately:

```bash
# Find the chroma binary from the chromadb pip package
which chroma
# Typical path on macOS: /Library/Frameworks/Python.framework/Versions/3.11/bin/chroma

# Start the HTTP server
chroma run --path ~/projects/chroma-data --port 8100 --host 127.0.0.1
```

**Critical traps to avoid:**

| Trap | Why it fails | Correct command |
|------|--------------|-----------------|
| `uvx chroma run ...` | Installs `chroma==0.2.0`, a DIFFERENT CLI tool unrelated to ChromaDB | Use the `chroma` binary from `pip install chromadb` |
| `python3 -m chromadb.cli.server run ...` | Module `chromadb.cli.server` does not exist in chromadb 1.5.8 | Use the `chroma` CLI binary directly |
| `curl http://localhost:8100/api/v1/heartbeat` | v1 API returns 410 Gone | Use `GET /api/v2/heartbeat` |

**Verification after manual start:**
```bash
# v2 heartbeat (v1 is deprecated)
curl -s -m 3 http://127.0.0.1:8100/api/v2/heartbeat
# Expected: {"nanosecond heartbeat":...}

# List collections
curl -s -m 5 http://127.0.0.1:8100/api/v2/tenant/default/database/default/collections
# Expected: JSON array of collection objects
```

**Hermes background process note:** When starting servers from an agent session, use `terminal(background=true)` and poll with `process(action='poll')`. Do NOT use shell `&` or `nohup` — the Hermes terminal tool blocks these patterns. After starting, run health checks in follow-up `terminal()` calls.

## Hermes MCP Integration

Expose your local ChromaDB HTTP server to Hermes Agent profiles via the Model Context Protocol (MCP) so every agent can query, add, and manage documents without writing Python.

**Prerequisites:** ChromaDB running in HTTP server mode (see "Server mode" section above), `uv` installed.

**Install the MCP server (persistent binary):**
```bash
uv tool install chroma-mcp
```

**Do NOT use `uvx chroma-mcp`.** `uvx` downloads ~106 packages on every cold start; the Hermes MCP handshake times out before the server finishes initializing. A persistent binary (`uv tool install`) starts instantly.

**Add to `~/.hermes/config.yaml`:**
```yaml
mcp_servers:
  chroma:
    command: chroma-mcp
    args:
      - --client-type
      - http
      - --host
      - localhost
      - --port
      - "8100"
      - --ssl
      - "false"
```

**Critical: `--ssl false`**  
The local ChromaDB HTTP server does not use TLS. Without this flag, `chroma-mcp` attempts TLS negotiation and the connection crashes silently.

**Verification:**
```bash
hermes mcp test chroma
# Expected: Connected (XXXXms), 13 tools discovered
```

**Tools exposed:** `chroma_query_documents`, `chroma_add_documents`, `chroma_get_documents`, `chroma_list_collections`, `chroma_peek_collection`, `chroma_delete_documents`, and collection management tools.

**Profile propagation:** MCP servers in main `~/.hermes/config.yaml` are inherited by **all profiles**. Restart gateways after config changes: `hermes gateway restart --profile <name>`.

For the full reproduction recipe including exact config, anti-patterns, and verification steps, see `references/hermes-mcp-setup.md`.

For migrating thousands of documents to canonical metadata, deduplication checks, and cron script replacement patterns, see `references/metadata-migration-at-scale.md`.

## Best practices

1. **Use persistent client** - Don't lose data on restart
2. **Add metadata** - Enables filtering and tracking
3. **Batch operations** - Add multiple docs at once
4. **Choose right embedding model** - Balance speed/quality
5. **Use filters** - Narrow search space
6. **Unique IDs** - Avoid collisions
7. **Regular backups** - Copy chroma_db directory
8. **Monitor collection size** - Scale up if needed
9. **Test embedding functions** - Ensure quality
10. **Standardize metadata keys across collections** — Use `source_path`, `source`, `source_type`, `item_id`, `route`, `score`, `created_at` consistently. Mixed keys (`source_file`, `file_name`, `path`, `vault_path`, `memory_path`, `ticket_path` for the same concept) cause cross-collection filter failures. See `references/persistentclient-migration.md` for the canonical schema and backfill strategy.
11. **Use server mode for production** - Better for multi-user

## Performance

| Operation | Latency | Notes |
|-----------|---------|-------|
| Add 100 docs | ~1-3s | With embedding |
| Query (top 10) | ~50-200ms | Depends on collection size |
| Metadata filter | ~10-50ms | Fast with proper indexing |

## Resources

- **GitHub**: https://github.com/chroma-core/chroma ⭐ 24,300+
- **Docs**: https://docs.trychroma.com
- **Discord**: https://discord.gg/MMeYNTmh3x
- **Version**: 1.3.3+
- **License**: Apache 2.0


