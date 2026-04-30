#!/usr/bin/env bash
set -euo pipefail

# Edgeless Stack Installer
# Copies hooks, skills, memory, and templates into your project.
# Usage: ./install.sh /path/to/your/project

STACK_DIR="$(cd "$(dirname "$0")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: ./install.sh /path/to/your/project${NC}"
    echo ""
    echo "This installs the Edgeless Stack into an existing project."
    echo "It will NOT overwrite existing files unless you pass --force."
    exit 1
fi

PROJECT_DIR="$1"
FORCE=false
[ "${2:-}" = "--force" ] && FORCE=true

if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}Error: $PROJECT_DIR does not exist${NC}"
    exit 1
fi

echo "Installing Edgeless Stack into: $PROJECT_DIR"
echo "================================================"

# --- 1. Create directory structure ---
echo -e "\n${GREEN}[1/6]${NC} Creating directory structure..."
mkdir -p "$PROJECT_DIR/.claude/hooks"
mkdir -p "$PROJECT_DIR/.claude/hooks/lib"
mkdir -p "$PROJECT_DIR/.claude/hooks/examples"
mkdir -p "$PROJECT_DIR/.claude/skills/core"
mkdir -p "$PROJECT_DIR/.claude/skills/domains"
mkdir -p "$PROJECT_DIR/.claude/memory"
mkdir -p "$PROJECT_DIR/data/shared_memory"

# --- 2. Copy hooks ---
echo -e "${GREEN}[2/6]${NC} Installing hooks..."
for hook in "$STACK_DIR"/hooks/*.py; do
    [ -f "$hook" ] || continue
    dest="$PROJECT_DIR/.claude/hooks/$(basename "$hook")"
    if [ -f "$dest" ] && [ "$FORCE" != true ]; then
        echo -e "  ${YELLOW}SKIP${NC} $(basename "$hook") (exists, use --force to overwrite)"
    else
        cp "$hook" "$dest"
        echo -e "  ${GREEN}OK${NC}   $(basename "$hook")"
    fi
done

# Copy hook lib
if [ -d "$STACK_DIR/hooks/lib" ]; then
    cp -r "$STACK_DIR/hooks/lib/"* "$PROJECT_DIR/.claude/hooks/lib/" 2>/dev/null || true
fi

# Copy hook examples
if [ -d "$STACK_DIR/hooks/examples" ]; then
    cp -r "$STACK_DIR/hooks/examples/"* "$PROJECT_DIR/.claude/hooks/examples/" 2>/dev/null || true
fi

# --- 3. Copy skills ---
echo -e "${GREEN}[3/6]${NC} Installing skills..."
if [ -d "$STACK_DIR/skills/core" ]; then
    cp -r "$STACK_DIR/skills/core/"* "$PROJECT_DIR/.claude/skills/core/" 2>/dev/null || true
    echo -e "  ${GREEN}OK${NC}   Core skills"
fi
if [ -d "$STACK_DIR/skills/domains" ]; then
    cp -r "$STACK_DIR/skills/domains/"* "$PROJECT_DIR/.claude/skills/domains/" 2>/dev/null || true
    echo -e "  ${GREEN}OK${NC}   Domain skills"
fi
if [ -f "$STACK_DIR/skills/_manifest.md" ]; then
    cp "$STACK_DIR/skills/_manifest.md" "$PROJECT_DIR/.claude/skills/"
fi

# --- 4. Set up memory ---
echo -e "${GREEN}[4/6]${NC} Setting up memory system..."

# Copy memory templates
if [ -f "$STACK_DIR/templates/MEMORY.md" ]; then
    dest="$PROJECT_DIR/.claude/memory/MEMORY.md"
    if [ -f "$dest" ] && [ "$FORCE" != true ]; then
        echo -e "  ${YELLOW}SKIP${NC} MEMORY.md (exists)"
    else
        cp "$STACK_DIR/templates/MEMORY.md" "$dest"
        echo -e "  ${GREEN}OK${NC}   MEMORY.md"
    fi
fi

# Copy shared memory Python package
if [ -d "$STACK_DIR/memory/shared_memory" ]; then
    cp -r "$STACK_DIR/memory/shared_memory" "$PROJECT_DIR/data/"
    echo -e "  ${GREEN}OK${NC}   Shared memory (SQLite episodic ledger)"
fi

# Initialize empty SQLite database
if [ ! -f "$PROJECT_DIR/data/shared_memory/events.sqlite3" ]; then
    python3 -c "
import sqlite3, os
db_path = os.path.join('$PROJECT_DIR', 'data', 'shared_memory', 'events.sqlite3')
conn = sqlite3.connect(db_path)
conn.execute('''CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now')),
    agent TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT DEFAULT '[]',
    confidence REAL DEFAULT 0.5,
    source TEXT DEFAULT 'agent'
)''')
conn.execute('CREATE INDEX IF NOT EXISTS idx_episodes_agent ON episodes(agent)')
conn.execute('CREATE INDEX IF NOT EXISTS idx_episodes_type ON episodes(memory_type)')
conn.execute('CREATE INDEX IF NOT EXISTS idx_episodes_timestamp ON episodes(timestamp)')
conn.commit()
conn.close()
print('  Initialized events.sqlite3')
" 2>/dev/null || echo -e "  ${YELLOW}WARN${NC} Could not initialize SQLite (python3 required)"
fi

# --- 5. Create CLAUDE.md ---
echo -e "${GREEN}[5/6]${NC} Setting up project configuration..."
if [ -f "$STACK_DIR/templates/CLAUDE.md" ]; then
    dest="$PROJECT_DIR/CLAUDE.md"
    if [ -f "$dest" ] && [ "$FORCE" != true ]; then
        echo -e "  ${YELLOW}SKIP${NC} CLAUDE.md (exists)"
    else
        cp "$STACK_DIR/templates/CLAUDE.md" "$dest"
        echo -e "  ${GREEN}OK${NC}   CLAUDE.md"
    fi
fi

# --- 6. Register hooks in settings.json ---
echo -e "${GREEN}[6/6]${NC} Registering hooks..."

SETTINGS_FILE="$PROJECT_DIR/.claude/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
    echo -e "  ${YELLOW}SKIP${NC} settings.json exists -- add hooks manually"
    echo -e "  See: ${STACK_DIR}/docs/hooks-guide.md"
else
    cat > "$SETTINGS_FILE" << 'SETTINGS'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "*",
        "command": "python3 .claude/hooks/damage-control.py"
      },
      {
        "matcher": "Write",
        "command": "python3 .claude/hooks/taxonomy-guard.py"
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "command": "python3 .claude/hooks/completion-verifier.py"
      }
    ],
    "Start": [
      {
        "command": "python3 .claude/hooks/session-lifecycle.py start"
      }
    ],
    "Stop": [
      {
        "command": "python3 .claude/hooks/session-lifecycle.py stop"
      }
    ]
  }
}
SETTINGS
    echo -e "  ${GREEN}OK${NC}   Hooks registered in settings.json"
fi

# --- Done ---
echo ""
echo "================================================"
echo -e "${GREEN}Edgeless Stack installed!${NC}"
echo ""
echo "Verification checklist:"
echo "  [x] Hooks copied to .claude/hooks/"
echo "  [x] Skills copied to .claude/skills/"
echo "  [x] Memory directory initialized"
echo "  [x] SQLite episodic ledger created"
echo "  [x] CLAUDE.md project config created"
echo "  [x] Hook settings registered"
echo ""
echo "Next steps:"
echo "  1. Edit CLAUDE.md with your project details"
echo "  2. Review hooks in .claude/hooks/ -- customize blocked patterns"
echo "  3. Start Claude Code in your project: cd $PROJECT_DIR && claude"
echo ""
echo "Optional:"
echo "  - Set up ChromaDB: docker compose -f $STACK_DIR/docker-compose.yml up chromadb -d"
echo "  - Set up Agent Bus: cd $STACK_DIR/mcp-servers/agent-bus && bun install && bun run src/index.ts"
echo "  - Set up Obsidian vault: see $STACK_DIR/docs/obsidian-setup.md"
