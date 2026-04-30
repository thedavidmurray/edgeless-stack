#!/usr/bin/env bash
# cron-wrapper.sh -- Lockfile wrapper for cron jobs
#
# Prevents concurrent runs of the same job using PID-based lockfiles.
# Use this to wrap any cron job that should not run in parallel.
#
# Usage:
#   cron-wrapper.sh <job-name> <command...>
#
# Example crontab entry:
#   0 8 * * * /path/to/cron-wrapper.sh health-check /path/to/health-check.sh
#
# CUSTOMIZE: Set LOCK_DIR and LOG_DIR to your preferred locations.

set -euo pipefail

# --- Configuration ---
LOCK_DIR="/tmp"                          # CUSTOMIZE: Lockfile directory
LOG_DIR="${PROJECT_ROOT:-$(pwd)}/logs"    # CUSTOMIZE: Log directory
MAX_RUNTIME=300                          # CUSTOMIZE: Max runtime in seconds (default: 5 min)

# --- Arguments ---
if [ $# -lt 2 ]; then
    echo "Usage: cron-wrapper.sh <job-name> <command...>"
    exit 1
fi

JOB_NAME="$1"
shift
COMMAND="$@"

LOCKFILE="${LOCK_DIR}/${JOB_NAME}.lock"
TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
LOG_FILE="${LOG_DIR}/${JOB_NAME}-${TIMESTAMP}.log"

# --- Ensure directories ---
mkdir -p "$LOG_DIR"

# --- Lockfile check ---
if [ -f "$LOCKFILE" ]; then
    LOCK_PID=$(cat "$LOCKFILE" 2>/dev/null || echo "")
    if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] ${JOB_NAME}: Already running (PID ${LOCK_PID}), skipping" >> "${LOG_DIR}/${JOB_NAME}.log"
        exit 0
    fi
    # Stale lockfile -- remove it
    rm -f "$LOCKFILE"
fi

# --- Acquire lock ---
echo $$ > "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

# --- Run job ---
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Starting ${JOB_NAME}" >> "$LOG_FILE"

if timeout "$MAX_RUNTIME" $COMMAND >> "$LOG_FILE" 2>&1; then
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] ${JOB_NAME}: Completed successfully" >> "$LOG_FILE"
else
    EXIT_CODE=$?
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] ${JOB_NAME}: FAILED with exit code ${EXIT_CODE}" >> "$LOG_FILE"
    # CUSTOMIZE: Add alerting here (Telegram, Slack, email, etc.)
    # Example: send_alert "${JOB_NAME} failed with exit code ${EXIT_CODE}"
    exit $EXIT_CODE
fi

# --- Cleanup old logs ---
# CUSTOMIZE: Adjust retention period (default: 14 days)
find "$LOG_DIR" -name "${JOB_NAME}-*.log" -mtime +14 -delete 2>/dev/null || true
