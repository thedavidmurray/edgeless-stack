#!/usr/bin/env bash
# Start the Agent Bus Hub
#
# Usage:
#   ./start-agent-bus.sh              # Start hub only (foreground)
#   ./start-agent-bus.sh --background # Start hub in background
#
# Prerequisites:
#   - bun installed (https://bun.sh)
#   - Dependencies installed: bun install

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# CUSTOMIZE: Change default port
HUB_PORT="${AGENT_BUS_PORT:-9800}"

echo "=== Agent Bus Hub ==="
echo "Starting hub on port ${HUB_PORT}..."

# Check if hub is already running
if curl -s "http://127.0.0.1:${HUB_PORT}/health" > /dev/null 2>&1; then
  echo "Hub already running on port ${HUB_PORT}"
  curl -s "http://127.0.0.1:${HUB_PORT}/health" | python3 -m json.tool 2>/dev/null || true
  exit 0
fi

if [[ "${1:-}" == "--background" ]]; then
  bun run "${SCRIPT_DIR}/agent-bus-hub.ts" &
  HUB_PID=$!
  echo "Hub started in background (PID: ${HUB_PID})"
  sleep 1

  if curl -s "http://127.0.0.1:${HUB_PORT}/health" > /dev/null 2>&1; then
    echo "Hub healthy."
  else
    echo "ERROR: Hub failed to start"
    exit 1
  fi
else
  # Foreground (blocks)
  exec bun run "${SCRIPT_DIR}/agent-bus-hub.ts"
fi
