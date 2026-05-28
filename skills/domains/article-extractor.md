---

name: article-extractor
title: Article Extractor
description: >
  Extracts clean article content from any URL (blog posts, news articles,
  documentation, GitHub READMEs). Removes ads, navigation, sidebars, and
  clutter. Uses a multi-backend fallback chain for maximum compatibility.
  Activate when the user provides a URL and wants the text content, asks to
  "download this article", "extract the content from [URL]", or "save this
  blog post as text".
metadata:
  tags:
    - article
    - extraction
    - scraping
    - web
    - content
    - readability
    - trafilatura
    - firecrawl
  tier: general
  domain: web
allowed-tools: Bash, Write, Read
version: 1.0.0
created: 2025-01-01
when_to_apply: >
  When the user provides a URL and wants the article text extracted as clean markdown.
---
# Article Extractor

Extracts main content from web articles and blog posts, removing navigation,
ads, newsletter signups, and other clutter. Produces clean, readable markdown
suitable for saving to any destination of the user's choice.

## When to Apply

Activate when the user:

- Provides an article or blog URL and wants the text content
- Asks to "download this article" or "grab this post"
- Wants to "extract the content from [URL]"
- Asks to "save this blog post as markdown"
- Needs clean article text without distractions
- Is building a local reading list or knowledge base from web content

## Backend Fallback Chain

Try backends in this order. Move to the next one when the previous produces
no content or fails.

### 1. reader-cli (Mozilla Readability — preferred)

```bash
# Check availability
command -v reader

# Install if missing
npm install -g reader-cli

# Extract (outputs clean markdown)
reader "$URL"
```

Best for: static articles, blog posts, news sites, documentation pages.
Pros: Based on Firefox Reader View, excellent clutter removal, no API key
required, free.

### 2. trafilatura (Python — fallback)

```bash
# Check availability
command -v trafilatura

# Install if missing (in a venv or user install)
pip install trafilatura

# Extract as plain text
trafilatura --URL "$URL" --output-format txt --no-comments

# Extract with metadata as JSON
trafilatura --URL "$URL" --json
```

Best for: academic articles, complex layouts, non-English content.
Pros: Very accurate, handles multiple languages, configurable, free.

### 3. Firecrawl (API — JS-heavy sites)

```python
import os
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])
result = app.scrape_url(url, params={"formats": ["markdown"]})
content = result.get("markdown", "")
```

Install: `pip install firecrawl-py`
Requires: `FIRECRAWL_API_KEY` environment variable.
Best for: Medium, Substack, LinkedIn, Notion, single-page apps that require
JavaScript rendering or bypass anti-bot measures.
Credits: 500 free/month on the free plan — use judiciously.

### 4. Basic fetch (stdlib — last resort)

```python
import urllib.request
import html.parser

class _TextExtractor(html.parser.HTMLParser):
    SKIP_TAGS = {"script", "style", "nav", "header", "footer", "aside"}

    def __init__(self):
        super().__init__()
        self._skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip and data.strip():
            self.parts.append(data.strip())

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=15) as resp:
    raw_html = resp.read().decode("utf-8", errors="replace")

extractor = _TextExtractor()
extractor.feed(raw_html)
content = "

".join(extractor.parts)
```

Pros: Zero dependencies (Python stdlib only).
Cons: Less accurate — will include some noise. Use only as a last resort.

## Core Extraction Workflow

```bash
#!/usr/bin/env bash
# Usage: extract_article.sh <URL> [output_dir]

URL="$1"
OUTPUT_DIR="${2:-.}"   # default: current directory
CONTENT=""
TITLE=""
AUTHOR=""
DATE=""
TOOL_USED=""

# ── 1. reader-cli ────────────────────────────────────────────────────────────
if command -v reader &>/dev/null; then
    CONTENT=$(reader "$URL" 2>/dev/null)
    if [ -n "$CONTENT" ]; then
        TOOL_USED="reader"
        TITLE=$(echo "$CONTENT" | head -n 1 | sed 's/^# //')
    fi
fi

# ── 2. trafilatura ───────────────────────────────────────────────────────────
if [ -z "$CONTENT" ] && command -v trafilatura &>/dev/null; then
    JSON=$(trafilatura --URL "$URL" --json 2>/dev/null)
    if [ -n "$JSON" ]; then
        TOOL_USED="trafilatura"
        CONTENT=$(echo "$JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('text', ''))
")
        TITLE=$(echo "$JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('title', ''))
")
        AUTHOR=$(echo "$JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('author', ''))
")
        DATE=$(echo "$JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('date', ''))
")
    fi
fi

# ── 3. Firecrawl (requires FIRECRAWL_API_KEY) ────────────────────────────────
if [ -z "$CONTENT" ] && [ -n "$FIRECRAWL_API_KEY" ]; then
    CONTENT=$(python3 - <<'PYEOF'
import os, sys
try:
    from firecrawl import FirecrawlApp
    app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])
    result = app.scrape_url(sys.argv[1], params={"formats": ["markdown"]})
    print(result.get("markdown", ""))
except Exception as e:
    print("", end="")
PYEOF
"$URL")
    if [ -n "$CONTENT" ]; then
        TOOL_USED="firecrawl"
    fi
fi

# ── 4. stdlib fallback ───────────────────────────────────────────────────────
if [ -z "$CONTENT" ]; then
    CONTENT=$(python3 - "$URL" <<'PYEOF'
import sys, urllib.request, html.parser

class _T(html.parser.HTMLParser):
    SKIP = {"script","style","nav","header","footer","aside"}
    def __init__(self): super().__init__(); self._s=0; self.p=[]
    def handle_starttag(self, t, _):
        if t in self.SKIP: self._s += 1
    def handle_endtag(self, t):
        if t in self.SKIP and self._s: self._s -= 1
    def handle_data(self, d):
        if not self._s and d.strip(): self.p.append(d.strip())

try:
    req = urllib.request.Request(sys.argv[1], headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        html_bytes = r.read().decode("utf-8", errors="replace")
    x = _T(); x.feed(html_bytes)
    print("

".join(x.p))
except Exception as e:
    print("")
PYEOF
)
    if [ -n "$CONTENT" ]; then
        TOOL_USED="basic-fetch"
    fi
fi

# ── 5. Failure ───────────────────────────────────────────────────────────────
if [ -z "$CONTENT" ]; then
    echo "ERROR: All backends failed for $URL" >&2
    exit 1
fi

# ── Build filename ────────────────────────────────────────────────────────────
[ -z "$TITLE" ] && TITLE=$(echo "$URL" | sed 's|https\?://||' | tr '/' '-' | cut -c1-80)
FILENAME=$(echo "$TITLE" | tr '/' '-' | tr ':' '-' | tr '?' '' | \
           tr '"' '' | tr '<>' '' | tr '|' '-' | \
           sed 's/  */ /g' | sed 's/^ //;s/ $//' | cut -c1-100)
OUTFILE="$OUTPUT_DIR/${FILENAME}.md"

# ── Build frontmatter ─────────────────────────────────────────────────────────
WORD_COUNT=$(echo "$CONTENT" | wc -w | tr -d ' ')
TODAY=$(date +%Y-%m-%d)

cat > "$OUTFILE" <<FRONTMATTER
---
title: "${TITLE}"
author: "${AUTHOR}"
date: "${DATE}"
source_url: ${URL}
extracted_date: ${TODAY}
word_count: ${WORD_COUNT}
extraction_backend: ${TOOL_USED}
---

FRONTMATTER

echo "$CONTENT" >> "$OUTFILE"

echo "Saved: $OUTFILE (${WORD_COUNT} words, backend: ${TOOL_USED})"
```

## Metadata Generated

Every extracted file includes a YAML frontmatter block:

| Field | Source |
|---|---|
| `title` | Extracted from article or URL path |
| `author` | Extracted when available (trafilatura, Firecrawl) |
| `date` | Publication date when available |
| `source_url` | The original URL |
| `extracted_date` | Today's date (ISO 8601) |
| `word_count` | Approximate word count of the body |
| `extraction_backend` | Which backend produced the result |

## What Gets Removed

- Navigation menus and breadcrumbs
- Advertisements and promotional banners
- Newsletter signup forms
- Related-articles sidebars
- Comment sections
- Social media share buttons
- Cookie consent overlays
- Analytics scripts and trackers

## What Gets Kept

- Article title and author byline
- All body paragraphs
- Section headings (preserved as markdown `#`)
- Inline code and code blocks
- Blockquotes and pull quotes
- Meaningful lists

## Output Path

The skill does NOT write to any hardcoded location. Ask the user where they
want the file saved, or default to the current working directory.

Recommended pattern:

```
Extracted: "Article Title Here"
  Words : 2,341
  Backend: reader
  Saved  : ./Article-Title-Here.md

Preview (first 15 lines):
---
[show first 15 lines]
---
Show full content? (y/n)
```

## Handling Paywalled Content

When content is behind a paywall or login:

1. Attempt extraction — some paywalled sites include body text in the HTML
   (metered paywall), which reader-cli or trafilatura can grab.
2. If content is still empty or under 200 words, inform the user clearly:
   "This article appears to be behind a paywall. The extracted content is
   limited. You may need to log in or use a subscription to access the full
   text."
3. Do NOT fabricate or summarize content that was not actually retrieved.
4. Save whatever partial content was found with a `paywall: true` frontmatter
   flag so the user knows it is incomplete.

## Handling GitHub READMEs

GitHub READMEs render as HTML but are also available as raw markdown:

```bash
# Convert github.com URL to raw.githubusercontent.com
RAW_URL=$(echo "$URL" | \
    sed 's|github.com|raw.githubusercontent.com|' | \
    sed 's|/blob/|/|')
curl -s "$RAW_URL" > article.md
```

Use this shortcut before trying the full extraction chain.

## Error Handling Reference

| Condition | Detection | Action |
|---|---|---|
| Tool not installed | `command -v` returns non-zero | Skip to next backend |
| Empty extraction | Output is blank or under 50 chars | Try next backend |
| Network error | curl/urllib raises exception | Try next backend; report if all fail |
| Paywall / login wall | Content under 200 words | Save partial, flag `paywall: true` |
| Invalid URL | curl/urllib fails immediately | Report invalid URL to user |
| Special chars in title | Filename creation fails | Apply sanitization pattern |

## Performance Reference

| Backend | Speed | Accuracy | Requires |
|---|---|---|---|
| reader-cli | Fast | High | Node.js (`npm i -g reader-cli`) |
| trafilatura | Medium | Very High | Python 3 (`pip install trafilatura`) |
| Firecrawl | Medium | High (JS sites) | API key + `pip install firecrawl-py` |
| Basic fetch | Fast | Medium | Python 3 stdlib only |

## Best Practices

- Always verify extraction produced content before saving.
- Show the user a preview (first 10-15 lines) before writing the file.
- Store the source URL in frontmatter — provenance matters.
- For batch extraction, add a short delay between requests to be respectful.
- Never fabricate content that was not retrieved.
- If the user does not specify an output path, ask or default to CWD.
