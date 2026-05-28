---
name: telegram-ops-alerting
description: >
  USE THIS SKILL whenever sending operational alerts, health check failures, or
  escalation notifications via Telegram. ALWAYS use to format alert messages,
  verify delivery, and handle alert rate limiting. Centralizes alerting patterns
  from system-health, mac-offline-protocol, and risk monitoring.
metadata:
  tags: [telegram, alerts, rate-limiting, ops]
  tier: task-specific
  domain: tooling
when_to_apply: >
  When sending operational alerts to Telegram with rate limiting and consistent
  formatting.
---

# Telegram Operations Alerting

## Environment Prerequisites

Required environment variables:
- `TELEGRAM_BOT_TOKEN` - Bot API token (get from @BotFather)
- `TELEGRAM_CHAT_ID` - Target chat/channel ID

Verification:
```bash
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "Telegram alerting not configured"
    exit 1
fi
```

## Alert Deduplication & Batching

- **Never repeat the same item in consecutive alerts.** If a service is still down, escalate severity rather than sending identical messages. Repeating alerts trains the user to ignore them.
- **Batch related items.** One message with 5 items is better than 5 separate messages. Use a count header and one-liners.
- **Inbox alerts are NOT health alerts.** Use `email-processing-v2` for inbox-specific deduplication patterns (message-ID tracking, 7-day state pruning, gws parsing). The alerting skill governs format and severity; the email skill governs content and deduplication.
- **Silent by default.** When a monitor finds nothing new, send nothing. Do not send "all clear" or "no new items" unless explicitly requested.

## Alert Severity Levels

| Level | Prefix | Usage | Rate Limit |
|-------|--------|-------|------------|
| INFO | [INFO] | Status updates, routine events | None |
| WARNING | [WARN] | Degradation, approaching thresholds | 1 per hour |
| ALERT | [ALERT] | Service down, P0/P1 issues | Immediate |
| CRITICAL | [CRIT] | Multi-system failure, data loss | Immediate + email backup |

## Standard Alert Format

```markdown
[SEVERITY]: [Service] [Condition]

Impact: [Brief description]
Detected: [ISO timestamp]
Duration: [If applicable]

Details:
- Item 1
- Item 2

Action Required: [What to do / who to escalate]
```

## From Other Skills

- system-health: Uses for disk/memory/Pamela alerts
- mac-offline-protocol: Uses for COO offline escalation
- risk-escalation-matrix: Determines severity thresholds
