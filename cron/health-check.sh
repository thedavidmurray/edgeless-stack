#!/usr/bin/env bash
# health-check.sh -- Basic system health check template
#
# Checks key services and resources, sends alerts on failures.
# Schedule: Every 6 hours or daily at 9am.
#
# CUSTOMIZE: Add your own service checks, thresholds, and alert channels.

set -euo pipefail

# --- Configuration ---
# CUSTOMIZE: Set your project root and alert mechanism
PROJECT_DIR="${PROJECT_ROOT:-$(pwd)}"
LOG_DIR="$PROJECT_DIR/logs/health"
LOG_FILE="$LOG_DIR/health-$(date +%Y%m%d_%H%M%S).log"

# CUSTOMIZE: Your notification command (Telegram, Slack, email, etc.)
# Example: ALERT_CMD="python3 send_telegram.py"
ALERT_CMD="echo"

mkdir -p "$LOG_DIR"
exec > "$LOG_FILE" 2>&1

echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ'): Starting health check"

FAILURES=0
REPORT=""

# --- Check 1: Disk Space ---
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_USAGE" -gt 90 ]; then
    REPORT="${REPORT}\n- CRITICAL: Disk usage at ${DISK_USAGE}%"
    FAILURES=$((FAILURES + 1))
elif [ "$DISK_USAGE" -gt 80 ]; then
    REPORT="${REPORT}\n- WARN: Disk usage at ${DISK_USAGE}%"
fi

# --- Check 2: Memory ---
# CUSTOMIZE: Adjust for your OS (this is macOS-flavored)
if command -v vm_stat &>/dev/null; then
    FREE_PAGES=$(vm_stat | awk '/Pages free/ {print $3}' | tr -d '.')
    FREE_MB=$((FREE_PAGES * 4096 / 1048576))
    if [ "$FREE_MB" -lt 512 ]; then
        REPORT="${REPORT}\n- WARN: Free memory ${FREE_MB}MB"
    fi
elif command -v free &>/dev/null; then
    # Linux
    FREE_MB=$(free -m | awk '/Mem:/ {print $7}')
    if [ "$FREE_MB" -lt 512 ]; then
        REPORT="${REPORT}\n- WARN: Available memory ${FREE_MB}MB"
    fi
fi

# --- Check 3: Service Health ---
# CUSTOMIZE: Add your service endpoints
SERVICES=(
    # "http://localhost:8080/health|My API"
    # "http://localhost:5678/healthz|n8n"
    # "http://localhost:3000/api/health|Frontend"
)

for SERVICE in "${SERVICES[@]}"; do
    URL="${SERVICE%%|*}"
    NAME="${SERVICE##*|}"
    if ! curl -sf --max-time 10 "$URL" > /dev/null 2>&1; then
        REPORT="${REPORT}\n- FAIL: ${NAME} (${URL}) not responding"
        FAILURES=$((FAILURES + 1))
    fi
done

# --- Check 4: Cron Job Health ---
# CUSTOMIZE: Check that recent cron logs exist and don't contain errors
CRON_JOBS=(
    # "logs/email-triage|email-triage|1"    # name|dir pattern|max age in days
    # "logs/kb-synthesizer|kb-synth|1"
)

for JOB in "${CRON_JOBS[@]}"; do
    IFS='|' read -r JOB_DIR JOB_PATTERN JOB_MAX_AGE <<< "$JOB"
    if [ -d "$PROJECT_DIR/$JOB_DIR" ]; then
        RECENT=$(find "$PROJECT_DIR/$JOB_DIR" -name "${JOB_PATTERN}*" -mtime -"$JOB_MAX_AGE" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$RECENT" -eq 0 ]; then
            REPORT="${REPORT}\n- WARN: No recent ${JOB_PATTERN} logs (expected within ${JOB_MAX_AGE}d)"
        fi
    fi
done

# --- Check 5: Git Status ---
# CUSTOMIZE: Enable if you want to track uncommitted changes
# if [ -d "$PROJECT_DIR/.git" ]; then
#     UNCOMMITTED=$(cd "$PROJECT_DIR" && git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
#     if [ "$UNCOMMITTED" -gt 20 ]; then
#         REPORT="${REPORT}\n- INFO: ${UNCOMMITTED} uncommitted changes"
#     fi
# fi

# --- Summary ---
echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ'): Health check complete"

if [ $FAILURES -gt 0 ]; then
    MSG="Health Check: ${FAILURES} failure(s)${REPORT}"
    echo -e "$MSG"
    $ALERT_CMD "$MSG" 2>/dev/null || echo "WARN: Alert send failed"
    exit 1
elif [ -n "$REPORT" ]; then
    MSG="Health Check: OK (with warnings)${REPORT}"
    echo -e "$MSG"
    # CUSTOMIZE: Optionally alert on warnings too
    # $ALERT_CMD "$MSG" 2>/dev/null || true
fi

echo "Health check: ALL CLEAR"

# Cleanup old logs
find "$LOG_DIR" -name "health-*.log" -mtime +14 -delete 2>/dev/null || true
