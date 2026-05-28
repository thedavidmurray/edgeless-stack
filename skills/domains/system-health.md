---


name: system-health
description: >
  USE THIS SKILL whenever checking service status, monitoring infrastructure
  health, or the user mentions 'health check', 'is X running', 'system status',
  'service down', or 'alert'. ALWAYS use for monitoring Mastra, Hermes gateway,
  Pamela trading bot, disk space, and memory usage. Contains health check
  scripts, cron integration, Telegram alerting setup, expected state definitions
  for all Paperclip services, and mass agent recovery procedures.
metadata:
  tags: [monitoring, health-check, alerting, ops]
  tier: task-specific
  domain: tooling
when_to_apply: >
  When checking infrastructure health, validating uptime, or building monitoring
  around services.
---
# System Health Monitoring Skill

Health checks for critical Paperclip organization services.

## Services Monitored

| Service | Endpoint | Check Method |
|---------|----------|--------------|
| Mastra | localhost:4111 | curl /api/health |
| Hermes Gateway | systemd | systemctl is-active |
| Pamela | pm2 | pm2 list, status |
| Disk | VPS | df -h |
| Memory | VPS | free -h |

## Pre-Flight Checklist

Before running health checks in cron:

1. **Verify Telegram credentials** (see `credential-discovery` skill):
   ```bash
   echo "Bot: ${TELEGRAM_BOT_TOKEN:0:10}... Chat: ${TELEGRAM_CHAT_ID}"
   ```
   If empty, follow credential-discovery protocol to locate or request setup.

2. **Cross-reference risk level:**
   - Use `risk-escalation-matrix` skill to determine if findings warrant immediate notification
   - P0/P1 issues → Telegram + consider dispatch
   - P2/P3 issues → Log only unless clustered

3. **Test alert path:**
   ```bash
   curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
     -d "chat_id=${TELEGRAM_CHAT_ID}" \
     -d "text=Health check test" > /dev/null && echo "Telegram OK" || echo "Telegram FAIL"
   ```

---

## Health Check Script

```bash
#!/bin/bash
# /root/.hermes/scripts/system-health.sh

TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID}"
ALERTS=""

# Mastra check - intentionally stopped per CEO approval, only alert if listening but unhealthy
if ss -tln 2>/dev/null | grep -q :4111 || netstat -tln 2>/dev/null | grep -q :4111; then
  # Port is listening, check health endpoint
  if ! curl -sf http://localhost:4111/api/health >/dev/null 2>&1; then
    ALERTS="${ALERTS}Mastra port 4111 listening but health endpoint failing\n"
  fi
fi

# Hermes gateway check
HERMES_ACTIVE=false
if command -v systemctl >/dev/null 2>&1; then
  # Systemd environment
  if systemctl is-active --quiet hermes-gateway 2>/dev/null; then
    HERMES_ACTIVE=true
  fi
else
  # Container or non-systemd environment
  if pgrep -f hermes-gateway >/dev/null 2>&1; then
    HERMES_ACTIVE=true
  fi
fi
if [ "$HERMES_ACTIVE" = "false" ]; then
  ALERTS="${ALERTS}Hermes gateway not active\n"
fi

# Pamela check (only if pm2 is installed)
if command -v pm2 >/dev/null 2>&1; then
  if ! pm2 list | grep -q "pamela.*online"; then
    ALERTS="${ALERTS}Pamela not running in pm2\n"
  fi
else
  ALERTS="${ALERTS}pm2 not installed - Pamela check skipped\n"
fi

# Disk check (alert if >80%)
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_USAGE" -gt 80 ]; then
  ALERTS="${ALERTS}Disk usage critical: ${DISK_USAGE}%\n"
fi

# Memory check (alert if >90%)
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
if [ "$MEMORY_USAGE" -gt 90 ]; then
  ALERTS="${ALERTS}Memory usage critical: ${MEMORY_USAGE}%\n"
fi

# Send Telegram alert if any issues
if [ -n "$ALERTS" ]; then
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=⚠️ *System Health Alert* ⚠️%0A%0A${ALERTS}%0ATimestamp: $(date -Iseconds)" \
    -d "parse_mode=Markdown" >/dev/null 2>&1
fi

# Output for logging
echo "Health check completed: $(date -Iseconds)"
if [ -n "$ALERTS" ]; then
  echo "Issues detected:"
  echo -e "$ALERTS"
  exit 1
else
  echo "All systems healthy"
  exit 0
fi
```

## Integration

Run via cron 2x/day:

```cron
# Hermes system health check (2x/day, 08:00 and 20:00 UTC)
0 8,20 * * * /root/.hermes/scripts/system-health.sh >> /var/log/hermes-health.log 2>&1
```

## Troubleshooting

### Alternative port checking methods
If `ss` or `netstat` are not available:
- Use `cat /proc/net/tcp 2>/dev/null | grep :101B` (4111 decimal = 0x101B hex)
- Use `lsof -i :4111 2>/dev/null` if installed
- Use `curl -s -o /dev/null -w "%{http_code}" localhost:4111/api/health` - returns 000 if connection refused
- Use `ps aux | grep -i mastra` to see if Mastra process is running (note: may show grep itself)

### Container environment considerations
In containerized environments (Docker, Kubernetes, VPS without systemd):
- `systemctl` may not be available. Use alternative process checks:
  - `pgrep -f hermes-gateway` – returns PID if process exists
  - `ps aux | grep -E "hermes-gateway" | grep -v grep` – full process info
  - `ps -p <PID>` to verify process details if pgrep returns a PID
- Disk usage: container root filesystem may be overlay; use `df -h /` for root mount
- Service discovery: containers may have different network namespaces; localhost services may be in host network or separate containers

### Different Mastra endpoints
Mastra may have multiple endpoints:
- `/api/health` - standard health check
- `/api/agents` - list agents (also indicates service is up)
- `/` - root endpoint may return 200

### pm2 not installed
If `pm2` command not found:
- Check `which pm2`, `npm list -g | grep pm2`
- Pamela may be running via other process manager (systemd, direct node)
- Consider `ps aux | grep -E \"pamela|node\"` to find processes

## Mac Offline Detection

Additional check for rsync staleness:

```bash
#!/bin/bash
# Mac offline detection

LAST_SYNC=$(stat -c %Y /opt/david-sync/vault/.last-sync 2>/dev/null || echo 0)
NOW=$(date +%s)
AGE=$((NOW - LAST_SYNC))

# 24 hours = 86400 seconds
if [ "$AGE" -gt 86400 ]; then
  HOURS=$((AGE / 3600))
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=🚨 *Mac Offline Alert* 🚨%0A%0AMac has not synced in ${HOURS} hours.%0ABusiness impact: COO unavailable for dispatch processing.%0A%0ATimestamp: $(date -Iseconds)" \
    -d "parse_mode=Markdown" >/dev/null 2>&1
fi
```

## Hermes Bot Restart Storm Diagnosis & Repair

When a Hermes bot is reported as "down" or "restarting repeatedly," the root cause is often the supervisor script itself, not the bot. Use this protocol before declaring the bot broken.

### Pre-Step: Check Auth Provider State (Fast Elimination)

Before investigating supervisor state or gateway logs, quickly verify the bot isn't suffering from a **broken LLM provider** that prevents responses while keeping the gateway alive:

```bash
# Check active provider -- if 'openai-codex', check for auth death
grep '"active_provider"' ~/.hermes/profiles/<PROFILE>/auth.json

# If openai-codex, check for permanent failure
grep -A3 'last_auth_error' ~/.hermes/profiles/<PROFILE>/auth.json
```

If `active_provider` is `openai-codex` and `last_auth_error.code` is `refresh_token_reused`, the bot is **connected to Discord but cannot respond**. Switch to `custom` and restart:

```bash
sed -i '' 's/"active_provider": "openai-codex"/"active_provider": "custom"/' \
  ~/.hermes/profiles/<PROFILE>/auth.json
launchctl kickstart -k ai.hermes.gateway-<PROFILE>
```

See `credential-discovery` skill and `references/openai-codex-auth-death-pattern.md` for full details. This check takes 5 seconds and eliminates the most common false-positive "bot down" report.

### Step 1: Verify What Is Actually Running

```bash
# Check both pattern styles: launchd (--profile X gateway run) and wrapper (gateway run --profile X)
for bot in atlas beau hive kilo scribe edgeless-cc ombudsman trader; do
    echo "=== $bot ==="
    pgrep -f "profile $bot" | xargs -I {} ps -o pid,ppid,etime,command -p {} 2>/dev/null | tail -n +2
done
```

**Critical**: A bot may be alive but the supervisor's `pgrep` pattern only matches one command-line ordering. `pgrep -f "profile atlas gateway"` misses `hermes gateway run --profile atlas`.

### Step 2: Read the Supervisor State File

```bash
cat ~/projects/logs/hermes-supervisor-state.json | python3 -m json.tool
```

Look for `restart_times` arrays. Three entries within 60 minutes triggers the storm threshold and locks out auto-recovery. Clear phantom history when the restarts were supervisor bugs, not genuine crashes:

```python
import json
from pathlib import Path
state = json.loads(Path("~/projects/logs/hermes-supervisor-state.json").read_text())
for bot in ["atlas", "beau"]:
    state.get(bot, {}).pop("restart_times", None)
Path("~/projects/logs/hermes-supervisor-state.json").write_text(json.dumps(state, indent=2))
```

### Step 3: Inspect Gateway Logs for "Already Running"

```bash
tail -n 50 ~/.hermes/profiles/PROFILE/logs/gateway.stdout
tail -n 50 ~/.hermes/profiles/PROFILE/logs/gateway.log
```

If you see `Gateway already running (PID NNN)` or `Another gateway instance is already running`, the restart command lacks `--replace`. Check the supervisor's `restart_bot()` function.

### Step 4: Check the Supervisor Script for Known Bugs

Open `~/projects/scripts/cron/hermes-bot-supervisor.sh` and verify these four patterns are correct:

| Bug Pattern | Broken | Fixed |
|-------------|--------|-------|
| **pgrep too specific** | `pgrep -f "profile {p} gateway"` | `pgrep -f "profile {p}"` |
| **duplicate killer by PID** | Sorts PIDs, kills highest | Removed entirely — use launchd/systemd for dedup |
| **shell=True restart** | `subprocess.Popen(cmd, shell=True, ...)` | Direct arg list: `subprocess.Popen([HERMES_VENV, "-m", "hermes_cli.main", "--profile", p, "gateway", "run", "--replace"], ...)` |
| **missing --replace** | No `--replace` in restart command | Always include `--replace` |
| **storm threshold too low** | `STORM_THRESHOLD = 3` | `STORM_THRESHOLD = 5` (Discord hiccups are normal) |
| **no startup grace** | `is_healthy()` checks log mtime immediately after restart | Add `STARTUP_GRACE_SECONDS = 45` — wait 45s before health checks |
| **no manual-restart exemption** | Manual restarts count toward storm threshold | Clear storm state if bot is running but last supervised restart was >5 min ago |
| **no storm backoff** | Alerts every 5 min after storm detected | Add `STORM_BACKOFF_SECONDS = 900` — wait 15 min before next attempt |

**Why `shell=True` is dangerous here**: Combined with `start_new_session=True`, it spawns a shell that gets SIGHUP when its parent dies, killing the gateway even though it was meant to daemonize.

### Critical Fix: Startup Grace Period

After ANY restart (manual or auto), the gateway needs 5-10 seconds to fully start, connect to Discord, and write its first log entry. Without a grace period, the supervisor sees a not-yet-fully-started process as dead and restarts it again, creating false storm alerts.

```python
# In is_healthy():
last_restart_ts = bot_state.get("last_restart_ts", 0)
if NOW_TS - last_restart_ts < STARTUP_GRACE_SECONDS:  # 45 seconds
    return True  # Assume healthy during startup
```

### Critical Fix: Manual Restart Exemption

When an admin manually restarts a bot, the supervisor must NOT count that toward the automatic restart threshold. Otherwise a single manual restart + 2 Discord hiccups = storm mode.

```python
# Before checking is_storm():
if is_running(bot) and restart_times:
    last_supervised_restart = max(restart_times)
    if NOW_TS - last_supervised_restart > 300:  # 5 minutes
        log("INFO", f"{bot}: manual restart detected — clearing storm state")
        restart_times = []
        bot_state["restart_times"] = []
```

### Critical Fix: Storm Backoff

Once storm is detected, alerting every 5 minutes creates spam. Wait 15 minutes before the next restart attempt.

```bash
STORM_BACKOFF_SECONDS=900  # 15 minutes
```

### Step 5: Verify Launchd Plist Integrity

```bash
cat ~/Library/LaunchAgents/ai.hermes.gateway-PROFILE.plist
```

Required fields for stable operation:
- `ProgramArguments` must include `--replace`
- `ProgramArguments` should include `--accept-hooks` if the bot uses hooks
- `KeepAlive` with `SuccessfulExit` = `false`
- `ThrottleInterval` = `60` (prevents rapid restart loops)

If the plist is unloaded or misconfigured:
```bash
launchctl load -w ~/Library/LaunchAgents/ai.hermes.gateway-PROFILE.plist
launchctl list | grep PROFILE
```

### Step 6: Confirm Fix

After patching, verify:
1. `pgrep -f "profile PROFILE"` returns exactly one PID
2. `ps -o etime` shows the process has been up for > 2 minutes
3. `tail ~/.hermes/profiles/PROFILE/logs/gateway.log` shows `discord connected` or the relevant platform
4. No new `already running` errors in `gateway.stdout`

**Reference**: Full session debug transcript with log evidence and exact patches is in `references/hermes-restart-storm-debug.md`.

**Reference**: Supervisor threshold elevation incident (2026-05-13) with load-228 zombie accumulation, emergency override pattern, and auto-restore verification in `references/supervisor-threshold-elevation-incident.md`.

**Reference**: Mass launchd plist rewrite incident (2026-05-18) where 20+ plists were rewritten simultaneously, triggering a cascade of gateway restarts that killed a 65-minute in-flight task. Root cause, timeline, and prevention options in `references/mass-launchd-plist-rewrite-incident.md`.

---

## Monitoring Philosophy: Data Over Alarms

When monitoring metrics the user cannot directly control (system load, API rate limits, provider availability), **prefer histograms and time-series data over plain-language warning spam**. Users need observability, not alarm fatigue.

### The Anti-Pattern: Warning Spam

```python
# BAD: Sends Telegram every 5 minutes for something user can't fix
if loadavg > 20:
    send_alert(f"WARNING: Supervisor skipping restarts — system load {loadavg:.1f}")
```

This creates **alert fatigue**. After the 10th identical message, the user tunes out. Worse, the alert channel becomes noise, so real emergencies get lost.

### The Pattern: Log to History, Share Histograms

```python
# GOOD: Append to rolling history, share digest on a schedule
HISTORY_FILE = Path("~/projects/logs/system-load-history.jsonl")
with open(HISTORY_FILE, "a") as hf:
    hf.write(json.dumps({"ts": NOW_ISO, "load_1m": round(loadavg, 1)}) + "\n")

# No alert. The data is there for analysis.
```

Then share a **histogram** via cron:

```bash
# Hourly digest to Discord #bot-backroom
0 * * * * system-load-histogram.py --last 24h --share
```

**Example output:**
```
**System Load Histogram** (last 93 checks)
  min=20.1  avg=247.1  max=571.9  p95=524.7
  >20:   93  >50:   83  >100:   74

  20.1 -   89.1  |███████████████████████       |   17 (18.3%)
  89.1 -  158.0  |█████████████████           |   14 (15.1%)
  ...
```

**Why this works:**
- User sees **distribution and trends**, not isolated spikes
- P95 tells them "how bad does it get" without emotional language
- The histogram reveals if load is bimodal (idle vs. burst) or consistently high
- One digest replaces 12 individual warnings

### When to Alert vs. When to Log

| Condition | Action | Rationale |
|-----------|--------|-----------|
| Metric exceeds threshold but user cannot act on it | **Log only** | Alerting is waste; data is value |
| Metric exceeds threshold and user **can** act (disk full, service down) | **Alert once, then quiet until resolved** | Actionable, but don't spam |
| Metric is a symptom of a root cause you just fixed | **Log for verification** | Confirm fix worked, don't celebrate with noise |
| Metric has been abnormal for >1 hour | **Digest, not point alert** | Sustained issue needs trend view, not repeated "still bad" |

### User Frustration Signals to Watch For

If the user says any of these, you're in alarm-fatigue territory:
- "Can we stop these warnings?"
- "This is just spam"
- "I don't have full control over X"
- "Better as a monitor than this"

**Response:** Immediately switch from point alerts to rolling history + scheduled digest. Ask what cadence they want (hourly? twice daily? daily?) and what channel (#bot-backroom vs. silent log only).

### Reference

- Histogram script: `~/.hermes/scripts/system-load-histogram.py`
- Template (copyable): `templates/system-load-histogram.py` in this skill
- History file: `~/projects/logs/system-load-history.jsonl`
- Cron job: `system-load-histogram` (runs hourly at `:00`)

---

## Overnight Report Format

When the user asks for an overnight report, summary, or status update across the organization, use this three-section format. It is the standard the user expects and produces the highest signal-to-noise ratio.

### Section 1: What Was Worked On

Scan these sources in order:
1. **Hermes cron jobs** (`~/.hermes/profiles/*/cron/jobs.json`) — check `last_status`, `last_run_at`, `completed` counts
2. **Crontab state files** (`logs/state/*.json`) — `status`, `items_processed`, `wall_seconds`
3. **Paperclip daily digest** (`logs/paperclip-daily-digest.log`) — open issues, stale cancellations
4. **Agent-specific logs** (`logs/cron_failures.log`, skill-specific logs)

Present as a table:
```
| System | Status | Detail |
|---|---|---|
| Paperclip daily digest | Ran 06:03 | 57 open issues, 46 stale recovery tasks cancelled |
| ChromaDB sync | Hourly, ok | 208 runs completed |
| Drop monitor | Every 2 min, ok | 239 runs, silent watch active |
```

### Section 2: Issues to Address

Enumerate as a numbered list. For each issue:
- **What it is** (one line)
- **Impact** (who/what is affected)
- **Recommended action** (specific, not vague)

Prioritize by: user-facing impact > data integrity > cost/efficiency > cosmetic.

Examples:
1. **Cron email spam** — `cron_failure_alerter.py` has phantom monitored jobs with no crontab entries. Remove `weekly_report`, `monthly_report`, `weekly_health_summary` from `MONITORED_JOBS`.
2. **Kilo paperclip-worker-pull** — Failing with 403 "API key budget limit exceeded". Check provider billing or rotate API key.
3. **Hive discord-digest-sweep** — Anthropic billing error for 2+ days. Either add credits or route digest to a cheaper model (Kimi via Fireworks).

### Section 3: Opportunities

Short bullets of what's working well and how to extend it:
- **Drop monitor proven** — 239 clean runs. Extend to concert tickets with VPS + Playwright path.
- **Ticket resale system live** — Needs user input Sunday, then runs autonomously.
- **Paperclip stale-task cleanup effective** — 46 cancelled today. Swarm health improving.

### Delivery Rules

- Lead with the table (Section 1) — users scan tables faster than prose
- Keep total length under 4000 characters unless asked for detail
- Use `---` section breaks for scannability
- Never open with "I'm working on your request" or "Here's what I found" filler
- If a section is empty, write "None identified" rather than omitting it

---

## Supervisor Load Throttling — Alert Fatigue vs. Cleanup Catch-22

The supervisor (`hermes-bot-supervisor.sh`) gates ALL restarts behind a system-load check:

```python
def is_system_overloaded(threshold: float = 20.0) -> bool:
    return os.getloadavg()[0] > threshold
```

When load exceeds 20, the script:
1. Logs `[THROTTLE] System load X > 20 — skipping all restarts this cycle`
2. Sends a **Telegram alert**: `WARNING: Supervisor skipping restarts — system load X`
3. **Exits immediately** — so zombie reaping and process-count checks never run

### The Catch-22

If runaway processes (zombie hermes chat workers, duplicate gateways, or CPU-heavy jobs) are driving load above 20, the supervisor **cannot clean them up** because the load gate fires before the reaper. Load stays high, alerts fire every 5 minutes forever.

### Diagnosing the Source of High Load

```bash
# Top CPU consumers
ps -eo pid,pcpu,comm | sort -k2 -nr | head -20

# Check for zombie hermes workers (common on Mac)
pgrep -f "hermes_cli.main" | wc -l
ps aux | grep -c "hermes"

# Check if load is from the supervisor itself spawning shells
ps aux | grep "bot-supervisor" | grep -v grep
```

### Remediation Options

| Approach | Command / Edit | When to Use |
|----------|---------------|-------------|
| **Histogram + scheduled digest** | Replace `send_alert()` with history logging + `system-load-histogram.py` cron | **Default** — data over alarms |
| **Raise threshold temporarily** | Edit `is_system_overloaded(threshold=60.0)` in supervisor | Load is 20-40 from legitimate burst, not runaway zombies |
| **Kill runaways manually** | `pkill -f "hermes_cli.main"` then restart needed bots via launchd | Load is 200+ from zombie accumulation |
| **Skip load gate for reaper only** | Patch supervisor to run `reap_zombie_workers()` before the load check | Recurring issue; structural fix |

### Expected Load on Mac

A healthy Mac with 8-12 cores should show:
- Idle: 1-5
- Normal work: 5-15
- Heavy compile/batch: 15-40
- **Sustained > 50**: investigate immediately (zombies or hung processes)
- **Sustained > 100**: emergency cleanup needed

A load of 209 means ~200 runnable processes are competing for CPU — almost certainly zombie hermes workers or a runaway loop, not legitimate load.

**Note:** When load exceeds threshold, the supervisor logs the value to a rolling history file (`~/projects/logs/system-load-history.jsonl`) and exits quietly. A separate cron job (`system-load-histogram`) posts an ASCII histogram to Discord #bot-backroom every hour. No Telegram spam.

## Quiet Bot False-Positive Kill — Log-MTime Health Check Pitfall

When a Hermes bot is quiet (low Discord traffic, infrequent cron jobs), the supervisor may declare it **UNHEALTHY** and kill it based on nothing more than stale `gateway.log` modification time. This is a false positive — the bot is idle, not dead.

### How It Manifests

The supervisor's `is_healthy()` function checks:

```python
gateway_log = Path(HERMES_DIR) / "profiles" / profile / "logs" / "gateway.log"
log_age = time.time() - gateway_log.stat().st_mtime
if log_age > 3600:  # No log activity in 1 hour
    return False
```

A bot with no incoming messages and no cron jobs to run produces **zero log output**. After 1 hour of silence, the supervisor SIGTERM's it.

**Real example — Kilo (2026-05-14):**
- Kilo has one cron job: `yt-enrichment-continuous-worker` every **3 hours**
- Between 08:42 and 09:45: 62 minutes of complete silence
- Supervisor: `[UNHEALTHY] kilo: process alive but not responding — killing before restart`
- Same cycle hit 5 bots simultaneously: edgeless-cc, scribe, ombudsman, atlas, kilo

**Reference**: Full diagnostic evidence in `references/quiet-bot-log-mtime-kill.md`.  
**Session evidence**: Exact transcript, log gaps, and cron schedule in `references/quiet-bot-kilo-session-evidence.md`.

### Why This Is Distinct from Restart Storms

- The bot is **genuinely running** — process is alive, Discord is connected
- The kill is **not** a supervisor bug (the 3600s threshold is by design)
- The kill is **wrong** for quiet bots because log mtime is a proxy for liveness, not actual liveness

### Recommended Fixes

| Approach | Change | Trade-off |
|----------|--------|-----------|
| **Extend threshold** | `3600 → 14400` (4h) or `21600` (6h) | Simple, but delays detection of real crashes |
| **Heartbeat log line** | Gateway cron ticker emits `INFO` every minute when idle | Structural fix, adds noise to logs |
| **Process liveness check** | Check PID exists + not zombie, de-emphasize log mtime | Best accuracy, slightly more complex |
| **WARN-only for log age** | Log stale mtime as warning, only kill if `is_running()` is also false | Safest for quiet bots, never false-positive kills |

### Diagnostic Commands

```bash
# Check gap in gateway.log timestamps (look for multi-hour gaps)
grep -E "^[0-9]{4}-[0-9]{2}-[0-9]{2}" ~/.hermes/profiles/PROFILE/logs/gateway.log | tail -20

# Check actual process uptime (should be hours/days, not minutes)
ps -o etime -p $(pgrep -f "profile PROFILE")

# Check when gateway.log was last modified
stat -f "%Sm" ~/.hermes/profiles/PROFILE/logs/gateway.log
```

---

### Supervisor Threshold Elevation — Emergency Override Pattern

When runaway processes spike system load above the normal threshold (20.0), the supervisor enters a catch-22: it cannot clean up zombies because the load gate fires before the reaper. The emergency workaround is to **temporarily raise the threshold** so the reaper can run.

**Pattern:**
1. **Elevate**: Edit `is_system_overloaded(threshold=250.0)` in `hermes-bot-supervisor.sh`
2. **Cleanup**: Let one supervisor cycle run — reaper kills zombies, load drops
3. **Auto-restore**: Schedule a cron job (`restore-supervisor-threshold`) to reset threshold back to 20.0 at next opportunity
4. **Verify**: Confirm load drops below 20 and stays there for >10 minutes before declaring fixed

**Example from 2026-05-13:**
- Load spiked to 228 from heartbeat worker zombie accumulation
- Threshold elevated from 20.0 to 250.0 at ~17:00
- Auto-restore cron scheduled for 2026-05-14 12:00 (noon)
- **Pitfall**: The auto-restore cron may fail silently if the supervisor script path changes or if cron environment lacks Python. Verify it actually ran by checking the threshold value in the script.

**Post-incident verification:**
```bash
# Check current threshold
grep "is_system_overloaded" ~/projects/scripts/cron/hermes-bot-supervisor.sh

# Check if auto-restore cron exists and ran
crontab -l | grep restore-supervisor
# If threshold is still elevated, manually patch it back:
sed -i '' 's/threshold: float = 250\.0/threshold: float = 20.0/' \
  ~/projects/scripts/cron/hermes-bot-supervisor.sh
```

**Mass agent recovery after systemic failure:** When a single root cause (provider bug, auth cascade, rate limit storm) puts many Paperclip agents into `error` simultaneously, reset them all at once via PostgreSQL rather than waiting for individual retries. See `references/mass-agent-recovery-postgresql.md` for the exact procedure.

---

### Case Study: Heartbeat Worker Zombie Accumulation (2026-05-13)

**Observed pattern:** Load average 228 on an 8-core Mac. Root cause was not a single runaway process but a **cascade of stale `hermes chat` heartbeat workers**.

**The chain:**
1. Heartbeat scripts launch `hermes chat -q ...` for each agent (Beau, Scribe, Edgeless CC)
2. Each worker queries Paperclip API via curl to localhost:3100
3. Paperclip forwards to postgres — queries block on large datasets
4. The heartbeat worker never exits because it's waiting for postgres
5. Next cron cycle (5 min) launches another worker without checking if the prior one finished
6. After several hours: **7 stale `hermes chat` workers** + **10 postgres SELECT/BIND processes** at 15-35% CPU each

**Process signature:**
```
postgres: paperclip paperclip 127.0.0.1(XXXXX) SELECT    -- 10+ of these
hermes chat -q You are "Beau", an AI agent employee...   -- 7 of these, 1-5 hours old
```

**Cleanup:**
```bash
# Identify all stale workers
pgrep -f "hermes chat" | xargs -I {} ps -o pid,etime,command -p {}

# Kill all (SIGTERM then SIGKILL)
for pid in $(pgrep -f "hermes chat"); do kill -15 $pid; done
sleep 3
for pid in $(pgrep -f "hermes chat"); do kill -9 $pid; done
```

**Prevention:** The supervisor's zombie reaper (`reap_zombie_workers()`) is gated behind the load check. When load > 20, the reaper never runs, so the very mechanism meant to clean up zombies is disabled by the zombies themselves. Consider running the reaper **before** the load gate, or adding a separate cron that kills `hermes chat` workers older than 30 minutes regardless of load.

**Post-cleanup load trajectory:** 228 → 190 → 164 → 147 (over ~30 seconds as postgres finishes backlog and workers terminate)

## Process Count Threshold Pitfall

The supervisor counts `hermes_cli.main` processes and alerts if > 20. This threshold is too low for multi-bot setups. See `references/hermes-process-count-threshold.md` for:
- Normal process counts for the current fleet (~27+)
- Why the 20 threshold produces false-positive alerts
- Corrected threshold (~80) and diagnostic commands
- Historical context: 2026-05-13 zombie accumulation incident

## Pipeline Content Filter Bias

Content enrichment pipelines that silently filter by topic domain can cause entire categories of knowledge to be skipped for weeks without detection. See `references/notebooklm-content-filter-bias.md` for the pattern, diagnosis commands, and prevention rules. This was discovered when the NotebookLM auto-ingest script hardcoded a generative-art-only filter, causing AI/LLM industry news to be silently discarded for ~19 days.

## Expected State

| Service | Expected |
|---------|----------|
| Mastra | STOPPED (approved by CEO) |
| Hermes Gateway | Active (systemd) |
| Pamela | Running (pm2) |
| Phantom | NOT RUNNING (OOM risk) |
| Disk | <80% |
| Memory | <90% |
