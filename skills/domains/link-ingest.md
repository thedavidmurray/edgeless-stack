---

name: link-ingest
description: >
  Ingest, save, or archive any web URL into the knowledge base. Fetches content
  using intelligent scraping (Firecrawl for JS-heavy sites, basic HTTP for simple),
  creates a well-structured Obsidian note with proper frontmatter and tags, and
  stores to ChromaDB for semantic search. Supports articles, YouTube videos, GitHub
  repos, arXiv papers, podcasts, books, and music. Triggers on: "ingest this",
  "save this link", "archive this article", "/ingest URL", user pastes a URL and
  asks to process or save it, "add this to the knowledge base", "store this URL".
allowed-tools: WebFetch, WebSearch, Write, Read, Bash, mcp__chroma__chroma_add_documents, mcp__chroma__chroma_get_collection_info
user-invocable: true
command: /ingest
arguments: url
created: 2026-01-18
updated: 2026-04-17
version: 3.2
metadata:
  tags: [ingest, url, web, obsidian, chromadb, knowledge-base, scraping]
  tier: general
  domain: ingestion
when_to_apply: When the user pastes a URL and asks to save, archive, or ingest it into the knowledge base
---
# Link Ingest Skill (v3.0)

Ingest ANY web content into the knowledge base with **intelligent scraping strategy**, auto-detected content type, enrichment, and proper Obsidian metadata.

## What's New in v3.0

- **Firecrawl integration** for JS-heavy sites (Medium, Substack, Twitter/X)
- **Tavily search** fallback for paywalled/blocked content
- **Smart URL classification** auto-selects best scraping method
- **67% fewer tokens** using markdown output vs raw HTML

## When to Use

Activate when the user:
- Says "ingest this: [URL]"
- Says "save this link" or "archive this article"
- Pastes a URL and asks to process/save it
- Uses `/ingest <url>`
- Shares a YouTube, Spotify, GitHub, arXiv, or any other URL

## Content Type Detection

Automatically detect content type from URL:

| URL Pattern | Content Type | Schema |
|-------------|--------------|--------|
| `youtube.com/watch`, `youtu.be/` | video | video schema |
| `open.spotify.com/track` | music | music schema |
| `open.spotify.com/episode` | podcast | podcast schema |
| `arxiv.org` | paper | paper schema |
| `github.com/{owner}/{repo}` | repo | repo schema |
| `goodreads.com/book` | book | book schema |
| `podcasts.apple.com` | podcast | podcast schema |
| `*.bandcamp.com`, `soundcloud.com` | music | music schema |
| Everything else | article | article schema |


## Search Query Rules

See project search-triggering conventions for query rules.

1. Never include years in search queries -- use the `since` field instead.
2. Never include relative-time words (latest, recent, current, today, this week) -- use the `since` field.
3. Decompose broad queries into multiple specific facets with proper nouns.

## Scraping Strategy (v3.0)

### URL Classification

The scraping module auto-classifies URLs to choose the best method:

| Site Type | Method | Why |
|-----------|--------|-----|
| **JS-Heavy** (Medium, Substack, Twitter/X, LinkedIn, Notion) | Firecrawl | Renders JavaScript, bypasses anti-bot |
| **Simple Static** (GitHub raw, arXiv, plain blogs) | Basic HTTP | Fast, no API credits needed |
| **Search/Discovery** | Tavily | Better for finding related content |
| **Blocked/Failed** | WebFetch fallback | Last resort |

### Scraping Tools Location

```
src/tools/scraping/
├── __init__.py          # Unified exports
├── firecrawl_client.py  # Firecrawl + basic fetch wrapper
└── tavily_client.py     # Search + extraction
```

### Usage in Python

```python
# Load environment with API keys
from dotenv import load_dotenv
load_dotenv('.env')  # Load your project's .env

# Import scraping tools
import sys
sys.path.insert(0, '.')  # Add project root
from src.tools.scraping import scrape_url, tavily_search, FirecrawlClient

# Auto-selects best method (Firecrawl for JS sites, basic for simple)
result = scrape_url("https://medium.com/article")
print(result.content)   # Clean markdown
print(result.title)     # Extracted title
print(result.source)    # "firecrawl" or "basic"

# Force Firecrawl for tricky sites
result = scrape_url("https://spa-site.com", force_firecrawl=True)

# Use Tavily for search + content (great for research)
search_results = tavily_search("Claude AI agents tutorial", include_raw_content=True)
for r in search_results.results:
    print(f"{r.title}: {r.url}")
    print(r.raw_content[:500])  # Full page content
```

## Workflow

### Step 1: Detect Content Type

```python
def detect_content_type(url):
    if 'youtube.com/watch' in url or 'youtu.be/' in url:
        return 'video'
    elif 'open.spotify.com/track' in url:
        return 'music'
    elif 'open.spotify.com/episode' in url:
        return 'podcast'
    elif 'arxiv.org' in url:
        return 'paper'
    elif 'github.com' in url and url.count('/') >= 4:
        return 'repo'
    elif 'goodreads.com/book' in url:
        return 'book'
    elif 'podcasts.apple.com' in url:
        return 'podcast'
    elif 'bandcamp.com' in url or 'soundcloud.com' in url:
        return 'music'
    else:
        return 'article'
```

### Step 2: Fetch Content (v3.0 Strategy)

**Primary: Use scrape_url() - Auto-selects best method:**
```python
from src.tools.scraping import scrape_url
result = scrape_url(url)
if result.success:
    content = result.content  # Clean markdown
    title = result.title
```

**JS-Heavy Sites (auto-detected by scrape_url):**
- Medium, Substack, Twitter/X, LinkedIn, Notion, Vercel apps
- Uses Firecrawl API for JavaScript rendering
- Returns clean markdown (67% fewer tokens)

**Simple Sites (auto-detected):**
- GitHub raw files, arXiv abstracts, static blogs
- Uses basic HTTP fetch (no API credits)
- Converts HTML to text

**Fallback Chain:**
1. Try `scrape_url()` (auto-selects Firecrawl or basic)
2. If fails → Try Tavily search for page content
3. If fails → Fall back to WebFetch tool

**For YouTube (via search if blocked):**
```python
from src.tools.scraping import tavily_search
results = tavily_search(f"{video_title} {channel}", include_raw_content=True)
```

**For Research/Discovery:**
```python
from src.tools.scraping import tavily_search
results = tavily_search("Claude AI tutorial", max_results=5, include_answer=True)
print(results.answer)  # AI-generated summary
```

### Step 3: AI Enrichment

Analyze the content to extract:
1. **Topics** - 3-5 main topics/keywords
2. **Entities** - Tools, people, companies mentioned
3. **Subtype** - Tutorial, news, reference, etc.
4. **Relevance Score** - Quality estimate (0.0-1.0)
5. **Summary** - 2-sentence summary for Dataview

### Step 4: Create Obsidian Note

Generate a note with STANDARDIZED frontmatter (customize frontmatter per your vault setup):

```yaml
---
# Core (required for all types)
note_type: knowledge_base
content_type: article  # or video, music, podcast, book, paper, repo
title: "Content Title"
source_url: "https://..."
ingested_at: 2026-01-18
created: 2026-01-18
updated: 2026-01-18
status: active

# Hierarchical tags (auto-generated)
tags:
  - content/article           # content/{type}
  - content/article/tutorial  # content/{type}/{subtype}
  - source/web               # source/{tool}
  - domain/example-com       # domain/{domain}
  - topic/ai-ml              # topic/{topic} (from AI extraction)
  - topic/langchain

# Quality
relevance_score: 0.85

# Type-specific fields (vary by content type)
author: "Author Name"
published: 2026-01-15
word_count: 2500
reading_time_minutes: 12
content_subtype: tutorial

# AI-extracted entities
topics: [RAG, LangChain, AI, embeddings]
mentioned_tools: [LangChain, ChromaDB, OpenAI]
mentioned_people: [Harrison Chase]
mentioned_companies: [LangChain Inc]

# Summary for Dataview tables
summary: "Step-by-step guide to building RAG applications using LangChain"

# Processing metadata
processed_by: link-ingest
chromadb_id: "link-abc123"
---
```

### Step 3: Structure the Note Body

```markdown
# {Title}

## Summary
{2-3 sentence summary}

## Key Points
- Point 1
- Point 2
- Point 3

## Content
{Main article content, cleaned}

## Actionable Items
- [ ] Any action items extracted from the content

## Metadata
- **Source**: {url}
- **Domain**: {domain}
- **Ingested**: {date}
- **Word Count**: {count}

---
*Ingested via link-ingest skill*
```

### Step 3b: Perplexity Research Enrichment (MANDATORY for backlog-worthy content)

**When the ingested content contains actionable concepts, techniques, or patterns that could generate backlog tasks**, enrich with Perplexity academic research BEFORE creating any tasks.

**Trigger conditions** (any of):
- Content contains technical concepts applicable to existing projects (trading, agents, ML)
- Content proposes a methodology, framework, or pattern
- User explicitly requests backlog task creation
- Content type is: tutorial, paper, technical article, educational video

**Enrichment workflow:**
1. Extract 2-3 key concepts from the ingested content
2. For each concept, run a Perplexity search with academic/technical focus:
   ```
   mcp__perplexity-mcp__perplexity_search_web(
     query="<concept> <application domain> best practices research"
   )
   ```
3. Synthesize findings: what does current research say? What are the caveats? How does this apply to our specific projects?
4. Include enrichment in the Obsidian note under a `## Research Enrichment` section
5. When creating backlog tasks, incorporate Perplexity findings into the task's technical approach and acceptance criteria

**Example:**
- Ingested article about "variance drag in compound returns"
- Perplexity query: "variance drag prediction markets binary options position sizing"
- Finding: "Binary outcomes don't compound within a single position, but drag applies across sequential trades. Half-Kelly is more robust."
- Backlog task enriched with: specific position sizing formula, reference to Kelly criterion, real-world application to Pamela bot

**Skip enrichment when:**
- Content is purely entertainment/creative (music, art)
- Content is a simple reference/documentation page
- Content has no actionable technical depth

### Step 4: Save to Vault

Save to: `<your-vault>/Knowledge/WebIntake/`

Filename pattern: `YYYY-MM-DD-{sanitized-title}.md`

### Step 5: Store to ChromaDB

Use MCP tool to add to `link_intake` collection:

```python
mcp__chroma__chroma_add_documents(
    collection_name="link_intake",
    documents=[summary + "

" + content[:8000]],
    ids=[f"link-{url_hash}"],
    metadatas=[{
        "title": title,
        "url": url,
        "domain": domain,
        "ingested_at": date,
        "type": "article",
        "source": "link_ingest_skill"
    }]
)
```

### Step 6: Confirm to User

```
Ingested: {title}
- Saved to: <vault>/Knowledge/WebIntake/{filename}
- Added to ChromaDB: link_intake collection
- Tags: source/web, content-type/article, domain/{domain}
```

## Standardized Tag Hierarchy

Always use these tag patterns for consistency:

| Category | Pattern | Examples |
|----------|---------|----------|
| Source | `source/{tool}` | `source/web`, `source/youtube`, `source/arxiv` |
| Content Type | `content-type/{type}` | `content-type/article`, `content-type/tutorial`, `content-type/reference` |
| Domain | `domain/{domain}` | `domain/github-com`, `domain/hackernews` |
| Status | `status/{status}` | `status/to-review`, `status/actionable` |
| Topic | `topic/{topic}` | `topic/python`, `topic/ai-ml` |

## Error Handling

**v3.0 Fallback Chain:**
1. `scrape_url()` fails → Try Tavily search for cached/indexed content
2. Tavily fails → Fall back to WebFetch tool
3. WebFetch fails → Inform user, suggest URL check
4. ChromaDB fails → Still save to vault, warn about search limitation
5. Content paywalled → Try Tavily (often has cached snippets), save what's available

**Checking scrape result:**
```python
result = scrape_url(url)
if not result.success:
    print(f"Primary scrape failed: {result.error}")
    # Try Tavily fallback
    search = tavily_search(f"site:{domain} {title_guess}")
    if search.results:
        content = search.results[0].content
```

## API Credit Usage

| Method | Credits | When Used |
|--------|---------|-----------|
| Basic fetch | Free | Simple static sites |
| Firecrawl | 500 total free | JS-heavy sites (Medium, etc.) |
| Tavily | 1000/month free | Search fallback, research |
| WebFetch | Built-in | Last resort fallback |

**Conservation tips:**
- Let `scrape_url()` auto-detect - only uses Firecrawl when needed
- Use Tavily for search/discovery (generous free tier)
- Reserve Firecrawl for sites that truly need JS rendering

## Examples

**User**: "ingest this: https://medium.com/@author/great-article"

**Response**:
1. Detect: JS-heavy site (Medium) → Use Firecrawl
2. `scrape_url(url)` returns clean markdown
3. Extract metadata, generate tags
4. Create Obsidian note with proper frontmatter
5. Save to vault
6. Add to ChromaDB
7. Confirm: "Ingested 'Great Article Title' - saved to vault and ChromaDB (via Firecrawl)"

**User**: "/ingest https://blog.example.com/tutorial"

1. Detect: Simple blog → Use basic fetch (no API credits)
2. Same workflow, fast and free

**User**: "/ingest https://paywalled-site.com/article"

1. `scrape_url()` fails (paywall)
2. Try Tavily search for cached content
3. If found: Use snippet/cached version
4. If not: Inform user, save URL with minimal metadata
