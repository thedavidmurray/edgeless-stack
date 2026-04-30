#!/usr/bin/env bash
# email-triage.sh -- Email inbox triage template
#
# Spawns a short-lived agent to categorize and triage email inbox.
# Schedule: 2-3x daily
#
# CUSTOMIZE: Set your email tool, agent command, and output directories.

set -euo pipefail

# --- Configuration ---
# CUSTOMIZE: Set your paths and tools
PROJECT_ROOT="${PROJECT_ROOT:-$(pwd)}"
LOG_DIR="$PROJECT_ROOT/logs/email-triage"
LOCKFILE="/tmp/email-triage.lock"

# CUSTOMIZE: Your email CLI tool
# Examples: himalaya, gws gmail, mutt, etc.
EMAIL_CMD="echo 'CUSTOMIZE: Set your email command'"

# CUSTOMIZE: Your agent command for autonomous triage
# Example: claude -p "..." --output-format text
AGENT_CMD=""

# CUSTOMIZE: Output directories
TRIAGE_OUTPUT_DIR="$PROJECT_ROOT/output/email-triage"

mkdir -p "$LOG_DIR" "$TRIAGE_OUTPUT_DIR"

# --- Lockfile (prevent concurrent runs) ---
if [ -f "$LOCKFILE" ]; then
    LOCK_PID=$(cat "$LOCKFILE" 2>/dev/null || echo "")
    if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
        exit 0
    fi
    rm -f "$LOCKFILE"
fi
echo $$ > "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
RESULT_FILE="$LOG_DIR/triage-${TIMESTAMP}.log"

# --- Get inbox snapshot ---
# CUSTOMIZE: Replace with your email tool command
INBOX_SNAPSHOT=$($EMAIL_CMD 2>/dev/null | head -40)

if [ -z "$INBOX_SNAPSHOT" ]; then
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] No inbox items, skipping" >> "$LOG_DIR/triage.log"
    exit 0
fi

# --- Build triage prompt ---
# CUSTOMIZE: Adjust categories and output format for your workflow
PROMPT="You are an email triage agent.

Here is the current inbox (unread):

\`\`\`
${INBOX_SNAPSHOT}
\`\`\`

Your tasks:
1. **Categorize** each email: actionable / worth-reading / noise / spam
2. **Flag** anything urgent or requiring a response
3. **Identify** newsletters with technical content worth saving
4. **Write a summary** to ${TRIAGE_OUTPUT_DIR}/triage-${TIMESTAMP}.md

Format your summary as:
## Email Triage - $(date '+%Y-%m-%d %H:%M')
### Actionable (respond/act)
### Worth Reading
### Noise (skip)

Be concise."

# --- Run triage agent ---
# CUSTOMIZE: Replace with your agent invocation
if [ -n "$AGENT_CMD" ]; then
    timeout 300 $AGENT_CMD "$PROMPT" > "$RESULT_FILE" 2>&1 || true
else
    echo "CUSTOMIZE: Set AGENT_CMD to your agent invocation" > "$RESULT_FILE"
    echo "Prompt would be:" >> "$RESULT_FILE"
    echo "$PROMPT" >> "$RESULT_FILE"
fi

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Triage complete" >> "$LOG_DIR/triage.log"

# Cleanup old logs
find "$LOG_DIR" -name "triage-*.log" -mtime +14 -delete 2>/dev/null || true
