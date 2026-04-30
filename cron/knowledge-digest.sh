#!/usr/bin/env bash
# knowledge-digest.sh -- Knowledge consolidation and synthesis template
#
# Processes inbox items (RSS, bookmarks, notes) into structured knowledge
# base articles. Uses an LLM to cluster topics and synthesize summaries.
#
# Schedule: Daily (e.g., 10am)
#
# CUSTOMIZE: Set paths, LLM client, and notification preferences.

set -euo pipefail

# --- Configuration ---
# CUSTOMIZE: Set your project root and Python path
PROJECT_DIR="${PROJECT_ROOT:-$(pwd)}"
LOG_DIR="$PROJECT_DIR/logs/kb-synthesizer"
LOG_FILE="$LOG_DIR/kb-synth-$(date +%Y%m%d_%H%M%S).log"
PYTHON="${PYTHON:-python3}"

# CUSTOMIZE: Your notification command
NOTIFY_CMD="echo"

# CUSTOMIZE: Directories for inbox and knowledge base
INBOX_DIR="$PROJECT_DIR/inbox"           # Where new items land
KNOWLEDGE_DIR="$PROJECT_DIR/knowledge"   # Where KB articles live
ARCHIVE_DIR="$PROJECT_DIR/archive"       # Where processed items go

mkdir -p "$LOG_DIR" "$INBOX_DIR" "$KNOWLEDGE_DIR" "$ARCHIVE_DIR"

exec > "$LOG_FILE" 2>&1
echo "$(date): Starting knowledge digest"

# --- Run the synthesizer ---
RESULT=$($PYTHON -c "
import sys, json, os
from pathlib import Path
from datetime import datetime, timedelta

# CUSTOMIZE: Set your paths
INBOX = Path('$INBOX_DIR')
KB = Path('$KNOWLEDGE_DIR')
ARCHIVE = Path('$ARCHIVE_DIR')

stats = {'processed': 0, 'new_articles': 0, 'updated': 0, 'errors': 0}

try:
    # Step 1: Find recent inbox files (last 7 days)
    cutoff = datetime.now() - timedelta(days=7)
    files = []
    for f in INBOX.rglob('*.md'):
        if f.stat().st_mtime > cutoff.timestamp():
            files.append(f)

    if not files:
        print(json.dumps({'status': 'empty', 'msg': 'No recent inbox files', **stats}))
        sys.exit(0)

    # Step 2: Read file titles and snippets
    file_data = []
    for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
        try:
            content = f.read_text(errors='replace')
            title = f.stem.replace('-', ' ').replace('_', ' ')
            # Extract title from frontmatter if present
            if content.startswith('---'):
                for line in content.split('\\n')[1:20]:
                    if line.startswith('---'):
                        break
                    if line.startswith('title:'):
                        title = line.split(':', 1)[1].strip().strip('\"')
            snippet = content[:500]
            file_data.append({'path': str(f), 'title': title, 'snippet': snippet})
        except Exception as e:
            stats['errors'] += 1

    if not file_data:
        print(json.dumps({'status': 'empty', 'msg': 'No readable files', **stats}))
        sys.exit(0)

    # Step 3: Cluster by topic (simple keyword-based)
    # CUSTOMIZE: Replace with LLM clustering for better results
    # Example with LLM:
    #   from your_llm_client import complete
    #   clusters = complete('Group these titles into topics: ...')
    clusters = [{'topic': 'Mixed Topics', 'indices': list(range(len(file_data)))}]

    # Step 4: Create or update KB articles
    for cluster in clusters:
        topic = cluster['topic']
        indices = cluster['indices']
        if not indices:
            continue

        group = [file_data[i] for i in indices if i < len(file_data)]
        slug = topic.lower().replace(' ', '-')[:50]
        kb_path = KB / f'{slug}.md'

        if kb_path.exists():
            # Append new sources
            with open(kb_path, 'a') as f:
                f.write(f'\\n\\n## Update {datetime.now().strftime(\"%Y-%m-%d\")}\\n')
                for item in group:
                    f.write(f'- {item[\"title\"]}\\n')
            stats['updated'] += 1
        else:
            # Create new article
            with open(kb_path, 'w') as f:
                f.write(f'---\\ntitle: {topic}\\ndate: {datetime.now().strftime(\"%Y-%m-%d\")}\\ntags: []\\n---\\n\\n')
                f.write(f'# {topic}\\n\\n')
                for item in group:
                    f.write(f'## {item[\"title\"]}\\n{item[\"snippet\"][:200]}\\n\\n')
            stats['new_articles'] += 1

        # Archive processed files
        for item in group:
            try:
                src = Path(item['path'])
                dst = ARCHIVE / src.name
                src.rename(dst)
                stats['processed'] += 1
            except Exception:
                stats['errors'] += 1

    print(json.dumps({'status': 'ok', **stats}))

except Exception as e:
    print(json.dumps({'status': 'error', 'msg': str(e), **stats}))
" 2>&1)

echo "Result: $RESULT"

# --- Parse and notify ---
STATUS=$($PYTHON -c "
import sys, json
try:
    d = json.loads('''$RESULT''')
    if d.get('status') == 'empty':
        print(d.get('msg', 'Nothing to process'))
    elif d.get('status') == 'ok':
        parts = []
        if d.get('new_articles', 0): parts.append(f\"{d['new_articles']} new KB articles\")
        if d.get('updated', 0): parts.append(f\"{d['updated']} updated\")
        if d.get('processed', 0): parts.append(f\"{d['processed']} items archived\")
        if d.get('errors', 0): parts.append(f\"{d['errors']} errors\")
        print('KB Digest: ' + ', '.join(parts) if parts else 'KB Digest: nothing to process')
    else:
        print(f\"KB Digest ERROR: {d.get('msg', 'unknown')}\")
except:
    print('KB Digest: parse error')
" 2>/dev/null || echo "KB Digest: complete")

if [ -n "$STATUS" ] && [ "$STATUS" != "Nothing to process" ]; then
    $NOTIFY_CMD "$STATUS" 2>/dev/null || echo "WARN: Notification failed"
fi

echo "$(date): Knowledge digest complete"
find "$LOG_DIR" -name "kb-synth-*.log" -mtime +14 -delete 2>/dev/null || true
