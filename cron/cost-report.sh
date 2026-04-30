#!/usr/bin/env bash
# cost-report.sh -- API and infrastructure cost tracking template
#
# Aggregates API usage costs across providers and sends a summary.
# Schedule: Weekly (e.g., Monday 9am) or daily.
#
# CUSTOMIZE: Add your API providers, billing endpoints, and thresholds.

set -euo pipefail

# --- Configuration ---
PROJECT_DIR="${PROJECT_ROOT:-$(pwd)}"
LOG_DIR="$PROJECT_DIR/logs/cost-reports"
LOG_FILE="$LOG_DIR/cost-$(date +%Y%m%d).log"
PYTHON="${PYTHON:-python3}"

# CUSTOMIZE: Your notification command
NOTIFY_CMD="echo"

# CUSTOMIZE: Monthly budget threshold (in USD)
BUDGET_WARN=50
BUDGET_CRITICAL=100

mkdir -p "$LOG_DIR"

exec > "$LOG_FILE" 2>&1
echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ'): Starting cost report"

# --- Collect costs ---
REPORT=$($PYTHON -c "
import json, os
from datetime import datetime, timedelta
from pathlib import Path

# CUSTOMIZE: Load your API keys
# from dotenv import load_dotenv
# load_dotenv('$PROJECT_DIR/.env')

costs = {}
total = 0.0
errors = []

# --- Provider 1: OpenRouter ---
# CUSTOMIZE: Uncomment and set your API key
# try:
#     import requests
#     resp = requests.get(
#         'https://openrouter.ai/api/v1/auth/key',
#         headers={'Authorization': f'Bearer {os.environ[\"OPENROUTER_API_KEY\"]}'},
#         timeout=10
#     )
#     if resp.ok:
#         data = resp.json().get('data', {})
#         usage = data.get('usage', 0) / 100  # cents to dollars
#         limit = data.get('limit', 0) / 100
#         costs['OpenRouter'] = {'usage': round(usage, 2), 'limit': round(limit, 2)}
#         total += usage
# except Exception as e:
#     errors.append(f'OpenRouter: {e}')

# --- Provider 2: Anthropic ---
# CUSTOMIZE: Check your Anthropic billing
# try:
#     # Anthropic doesn't have a usage API, track via logged requests
#     log_path = Path('$PROJECT_DIR/logs/llm-usage.jsonl')
#     if log_path.exists():
#         month_start = datetime.now().replace(day=1)
#         month_tokens = 0
#         for line in log_path.read_text().splitlines():
#             entry = json.loads(line)
#             if entry.get('provider') == 'anthropic':
#                 ts = datetime.fromisoformat(entry['timestamp'])
#                 if ts >= month_start:
#                     month_tokens += entry.get('total_tokens', 0)
#         # Rough cost estimate (adjust per model)
#         est_cost = month_tokens * 0.000015  # ~\$15/M tokens avg
#         costs['Anthropic'] = {'usage': round(est_cost, 2), 'tokens': month_tokens}
#         total += est_cost
# except Exception as e:
#     errors.append(f'Anthropic: {e}')

# --- Provider 3: Infrastructure ---
# CUSTOMIZE: Add VPS, database, storage costs
# costs['VPS (Hetzner)'] = {'usage': 7.50, 'note': 'Monthly fixed'}
# costs['Storage'] = {'usage': 0.00, 'note': 'Under free tier'}
# total += 7.50

# --- Placeholder if no providers configured ---
if not costs:
    costs['(no providers configured)'] = {'usage': 0, 'note': 'CUSTOMIZE: Add your API providers above'}

report = {
    'date': datetime.now().strftime('%Y-%m-%d'),
    'period': 'month-to-date',
    'total_usd': round(total, 2),
    'providers': costs,
    'budget_warn': $BUDGET_WARN,
    'budget_critical': $BUDGET_CRITICAL,
    'over_budget': total > $BUDGET_CRITICAL,
    'near_budget': total > $BUDGET_WARN,
    'errors': errors
}

print(json.dumps(report, indent=2))
" 2>&1)

echo "$REPORT"

# --- Format and notify ---
TOTAL=$(echo "$REPORT" | $PYTHON -c "import sys,json; print(json.load(sys.stdin).get('total_usd', 0))" 2>/dev/null || echo "0")
OVER=$(echo "$REPORT" | $PYTHON -c "import sys,json; print(json.load(sys.stdin).get('over_budget', False))" 2>/dev/null || echo "False")
NEAR=$(echo "$REPORT" | $PYTHON -c "import sys,json; print(json.load(sys.stdin).get('near_budget', False))" 2>/dev/null || echo "False")

if [ "$OVER" = "True" ]; then
    MSG="CRITICAL: Monthly costs \$${TOTAL} exceed budget \$${BUDGET_CRITICAL}"
    $NOTIFY_CMD "$MSG" 2>/dev/null || echo "WARN: Notification failed"
elif [ "$NEAR" = "True" ]; then
    MSG="WARNING: Monthly costs \$${TOTAL} approaching budget \$${BUDGET_WARN}"
    $NOTIFY_CMD "$MSG" 2>/dev/null || echo "WARN: Notification failed"
fi

# --- Save report ---
REPORT_FILE="$PROJECT_DIR/output/cost-report-$(date +%Y%m%d).json"
mkdir -p "$(dirname "$REPORT_FILE")"
echo "$REPORT" > "$REPORT_FILE"

echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ'): Cost report complete (total: \$${TOTAL})"

# Cleanup old logs
find "$LOG_DIR" -name "cost-*.log" -mtime +30 -delete 2>/dev/null || true
