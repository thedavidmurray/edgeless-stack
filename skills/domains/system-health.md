---
name: system-health
description: >
  USE THIS SKILL whenever checking service status, monitoring infrastructure
  health, or the user mentions 'health check', 'is X running', 'system status',
  'service down', or 'alert'. Contains health check scripts, cron integration,
  Telegram alerting setup, expected state definitions, and mass agent recovery
  procedures.
metadata:
  tags: [monitoring, health-check, alerting, ops]
  tier: task-specific
  domain: tooling
when_to_apply: >
  When checking infrastructure health, validating uptime, or building monitoring
  around services.
---
# System Health Monitoring Skill

Portable health-check methodology for service fleets.

## Prerequisites

Tuned for one author's swarm topology (profile-based bot gateway + launchd + cron). The *methodology* is portable; the specific commands are not. Adapt example invocations to your own infra (systemd / cron / process manager) before running.

## Pre-Flight Checklist

Before running health checks in cron:

1. **Verify alert channel credentials** (e.g. Telegram bot token + chat id). If empty, locate or request setup before going live.
2. **Cross-reference risk level:** use a risk-escalation matrix to decide if findings warrant notification. P0/P1 → notify + consider dispatch. P2/P3 → log only unless clustered.
3. **Test the alert path** end-to-end before relying on it:
   ```bash
   curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
     -d "chat_id=${TELEGRAM_CHAT_ID}" \
     -d "text=Health check test" > /dev/null && echo "Telegram OK" || echo "Telegram FAIL"
   ```

## Health Check Script (template)

```bash
#!/bin/bash
# system-health.sh — adapt service names / ports / managers to your stack

TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID}"
ALERTS=""

# HTTP service example: only alert if port is listening but health endpoint fails
if ss -tln 2>/dev/null | grep -q :PORT || netstat -tln 2>/dev/null | grep -q :PORT; then
  if ! curl -sf http://localhost:PORT/api/health >/dev/null 2>&1; then
    ALERTS="${ALERTS}Service port PORT listening but health endpoint failing\n"
  fi
fi

# Systemd or fallback process check
SERVICE_ACTIVE=false
if command -v systemctl >/dev/null 2>&1; then
  systemctl is-active --quiet SERVICE 2>/dev/null && SERVICE_ACTIVE=true
else
  pgrep -f SERVICE >/dev/null 2>&1 && SERVICE_ACTIVE=true
fi
[ "$SERVICE_ACTIVE" = "false" ] && ALERTS="${ALERTS}SERVICE not active\n"

# Process-manager (pm2 example) — skip cleanly if not installed
if command -v pm2 >/dev/null 2>&1; then
  pm2 list | grep -q "APP.*online" || ALERTS="${ALERTS}APP not running in pm2\n"
fi

# Disk (>80%) and memory (>90%) thresholds
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
[ "$DISK_USAGE" -gt 80 ] && ALERTS="${ALERTS}Disk usage critical: ${DISK_USAGE}%\n"

MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
[ "$MEMORY_USAGE" -gt 90 ] && ALERTS="${ALERTS}Memory usage critical: ${MEMORY_USAGE}%\n"

# Send alert only if something is wrong
if [ -n "$ALERTS" ]; then
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=System Health Alert%0A%0A${ALERTS}%0ATimestamp: $(date -Iseconds)" \
    -d "parse_mode=Markdown" >/dev/null 2>&1
fi

echo "Health check completed: $(date -Iseconds)"
if [ -n "$ALERTS" ]; then
  echo "Issues detected:"; echo -e "$ALERTS"; exit 1
else
  echo "All systems healthy"; exit 0
fi
```

## Integration

Run via cron at low frequency (twice daily is plenty for most fleets):

```cron
0 8,20 * * * /path/to/system-health.sh >> /var/log/health.log 2>&1
```

## Troubleshooting

### Alternative port-checking methods
If `ss` or `netstat` are not available:
- `cat /proc/net/tcp 2>/dev/null | grep :HEX` (port as 4-digit hex)
- `lsof -i :PORT 2>/dev/null` if installed
- `curl -s -o /dev/null -w "%{http_code}" localhost:PORT/api/health` — returns 000 on connection refused
- `ps aux | grep -i NAME` (note: may show grep itself)

### Container environment considerations
In Docker / Kubernetes / VPS without systemd:
- `systemctl` may not exist — fall back to `pgrep -f`, `ps aux | grep -v grep`, `ps -p <PID>`
- Container root may be overlay; use `df -h /` for the actual root mount
- Localhost may be host network or a separate container — check network namespace

### Process manager not installed
If your expected process manager command isn't found, check `which`, package listings, and fall back to `ps aux | grep`.

## Remote-Host Offline Detection

Detect stale state from a peer host by checking the age of a sync marker file:

```bash
LAST_SYNC=$(stat -c %Y /path/to/.last-sync 2>/dev/null || echo 0)
NOW=$(date +%s)
AGE=$((NOW - LAST_SYNC))

if [ "$AGE" -gt 86400 ]; then   # 24h
  HOURS=$((AGE / 3600))
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=Remote host offline ${HOURS}h. Business impact: <state it>. $(date -Iseconds)"
fi
```

## Bot/Worker Restart Storm Diagnosis & Repair

When a supervised worker is reported "down" or "restarting repeatedly," the root cause is often the **supervisor script itself**, not the worker. Run this protocol before declaring the worker broken.

### Pre-Step: Eliminate Broken Auth Provider

A worker can be **connected but unable to respond** if its LLM/API provider auth has died (e.g. reused refresh token). Check the active provider and last auth error first — this is the most common false-positive "bot down".

### Step 1: Verify What Is Actually Running

```bash
for w in worker1 worker2 worker3; do
  echo "=== $w ==="
  pgrep -f "$w" | xargs -I {} ps -o pid,ppid,etime,command -p {} 2>/dev/null | tail -n +2
done
```

**Critical**: a worker may be alive but the supervisor's `pgrep` pattern only matches one command-line ordering. `pgrep -f "profile X gateway"` misses `gateway run --profile X`. Use the most permissive pattern that still uniquely identifies the worker.

### Step 2: Read the Supervisor State File

State files typically record `restart_times` arrays. N entries within M minutes triggers a storm threshold and locks out auto-recovery. Clear phantom history when restarts were supervisor bugs, not genuine crashes.

### Step 3: Inspect Worker Logs for "Already Running"

Patterns like `already running (PID NNN)` or `another instance is already running` mean the restart command lacks an equivalent of `--replace` / force-takeover. Fix it in the supervisor's restart function.

### Step 4: Check the Supervisor Script for Known Bugs

| Bug Pattern | Broken | Fixed |
|---|---|---|
| pgrep too specific | matches only one arg order | use the broadest unique substring |
| duplicate killer by PID | sorts PIDs, kills highest | remove; rely on init/launchd/systemd for dedup |
| `shell=True` + `start_new_session=True` restart | spawns shell that takes SIGHUP and kills child | use explicit arg list to `subprocess.Popen` |
| missing `--replace` / force flag | restart fails when prior PID lingers | always include the takeover flag |
| storm threshold too low | normal hiccups trip storm mode | raise to a value above expected flap rate |
| no startup grace | health check runs before worker writes first log | add 30-60s grace where `is_healthy()` returns True |
| no manual-restart exemption | admin restart counts toward storm threshold | clear storm state if running and last supervised restart > 5 min ago |
| no storm backoff | spams alerts every cycle once tripped | wait 10-15 min before next attempt |

**Why `shell=True` is dangerous**: combined with `start_new_session=True`, the wrapping shell receives SIGHUP when its parent dies and kills the child you meant to daemonize.

### Critical Fix: Startup Grace Period

```python
last_restart_ts = bot_state.get("last_restart_ts", 0)
if NOW_TS - last_restart_ts < STARTUP_GRACE_SECONDS:  # e.g. 45
    return True   # assume healthy during startup
```

### Critical Fix: Manual Restart Exemption

```python
if is_running(bot) and restart_times:
    if NOW_TS - max(restart_times) > 300:   # 5 min
        restart_times = []
        bot_state["restart_times"] = []
```

### Critical Fix: Storm Backoff

Once a storm is declared, stop trying every cycle. Wait 10-15 minutes before the next restart attempt and suppress duplicate alerts during that window.

### Step 5: Verify Service Unit / Plist Integrity

For each supervised worker confirm:
- Restart command includes the takeover flag (`--replace` or equivalent)
- KeepAlive / Restart policy is set, but with a throttle interval (e.g. 60s) to prevent rapid loops
- The unit/plist is actually loaded (`systemctl status` / `launchctl list`)

### Step 6: Confirm Fix

After patching:
1. `pgrep -f WORKER` returns exactly one PID
2. `ps -o etime` shows uptime > 2 minutes
3. Logs show successful connect to upstream / platform
4. No new "already running" errors

## Monitoring Philosophy: Data Over Alarms

For metrics the user cannot directly control (system load, upstream rate limits, provider availability), **prefer histograms and time-series data over plain-language warning spam**. Users need observability, not alarm fatigue.

### The Anti-Pattern: Warning Spam

```python
# BAD: sends an alert every cycle for something the user can't fix
if loadavg > 20:
    send_alert(f"WARNING: load {loadavg:.1f}")
```

After the 10th identical message the user tunes out — and real emergencies get lost.

### The Pattern: Log to History, Share Digests

```python
# GOOD: append to rolling history; no point alert
with open(HISTORY_FILE, "a") as hf:
    hf.write(json.dumps({"ts": NOW_ISO, "load_1m": round(loadavg, 1)}) + "\n")
```

Then post a histogram on a schedule (hourly / twice daily):

```
System Load Histogram (last 93 checks)
  min=20.1  avg=247.1  max=571.9  p95=524.7

  20.1 -   89.1 |#######################   |  17 (18.3%)
  89.1 -  158.0 |#################         |  14 (15.1%)
```

### When to Alert vs. When to Log

| Condition | Action | Rationale |
|---|---|---|
| Threshold exceeded, user cannot act | **Log only** | Alerting is waste; data is the value |
| Threshold exceeded, user **can** act (disk full, service down) | **Alert once, then quiet until resolved** | Actionable, but don't spam |
| Symptom of a root cause you just fixed | **Log to verify** | Confirm fix worked, don't celebrate with noise |
| Abnormal for > 1 hour | **Digest, not point alert** | Sustained issues need a trend view |

### User Frustration Signals

If the user says "can we stop these warnings?", "this is just spam", "I don't have full control over X", "better as a monitor than this" — you're in alarm-fatigue territory. Switch from point alerts to rolling history + scheduled digest. Ask cadence and channel.

## Overnight / Daily Report Format

Three-section format for highest signal-to-noise.

### Section 1: What Was Worked On (table)

```
| System | Status | Detail |
|---|---|---|
| Daily digest | Ran 06:03 | 57 open issues, 46 stale tasks cancelled |
| Hourly sync | Ok | 208 runs completed |
| 2-min monitor | Ok | 239 runs, silent watch active |
```

### Section 2: Issues to Address

Numbered list. For each: **what it is** (one line), **impact** (who/what is affected), **recommended action** (specific). Prioritize: user-facing impact > data integrity > cost/efficiency > cosmetic.

### Section 3: Opportunities

Short bullets — what's working well and how to extend it.

### Delivery Rules

- Lead with the table (Section 1)
- Total length under ~4000 chars unless asked for detail
- Use `---` section breaks for scannability
- Never open with filler ("I'm working on your request", "Here's what I found")
- If a section is empty, write "None identified"

## Supervisor Load Throttling — Catch-22

Supervisors that gate ALL restarts behind a system-load check create a catch-22: if runaway processes drive load above the threshold, the supervisor **cannot clean them up** because the load gate fires before the reaper. Load stays high; alerts fire every cycle.

### Diagnosing the Source of High Load

```bash
# Top CPU consumers
ps -eo pid,pcpu,comm | sort -k2 -nr | head -20

# Count instances of a suspect worker
pgrep -f WORKER_NAME | wc -l

# Is the supervisor itself spawning shells?
ps aux | grep supervisor | grep -v grep
```

### Remediation Options

| Approach | When to Use |
|---|---|
| Histogram + scheduled digest | **Default** — data over alarms |
| Raise threshold temporarily | Load is moderate from legitimate burst |
| Kill runaways manually, then restart what's needed | Very high load from zombie accumulation |
| Run zombie reaper **before** the load gate | Recurring issue; structural fix |

### Expected Load Bands (8-12 core machine)

- Idle: 1-5 · Normal work: 5-15 · Heavy compile/batch: 15-40
- Sustained > 50: investigate (zombies or hung processes)
- Sustained > 100: emergency cleanup

Load equal to ~25× core count almost certainly means zombie/runaway accumulation.

## Quiet-Worker False-Positive Kill

Supervisors that infer death from stale log-file mtime will SIGTERM healthy idle processes.

### How It Manifests

```python
log_age = time.time() - log_path.stat().st_mtime
if log_age > 3600:        # 1h of silence
    return False          # supervisor will kill
```

A worker with no incoming traffic and no scheduled work produces zero log output, so after the threshold elapses the supervisor declares it dead.

### Recommended Fixes

| Approach | Trade-off |
|---|---|
| Extend threshold (4-6h) | Simple, delays detection of real crashes |
| Idle heartbeat log line (1/min) | Structural fix; adds log noise |
| Process-liveness check (PID exists, not zombie); de-emphasize mtime | Best accuracy |
| WARN-only on log age; only kill if `is_running()` is also false | Safest — never false-positive kills |

### Diagnostic Commands

```bash
# Gaps in log timestamps
grep -E "^[0-9]{4}-[0-9]{2}-[0-9]{2}" /path/to/worker.log | tail -20

# Actual process uptime
ps -o etime -p $(pgrep -f WORKER)

# Log mtime
stat -c "%y" /path/to/worker.log
```

## Supervisor Threshold Elevation — Emergency Override

When runaway processes spike load above the normal threshold, temporarily raise the threshold so the reaper can run.

1. **Elevate**: raise the threshold (e.g. 20 → 250)
2. **Cleanup**: one supervisor cycle runs the reaper; load drops
3. **Auto-restore**: schedule a one-shot job to reset the threshold at a known time
4. **Verify**: confirm load stays below original threshold for > 10 min

**Pitfall:** the auto-restore job may fail silently if the supervisor script path moved. Always verify the threshold value after restore is supposed to have happened.

**Mass agent recovery:** when a single root cause puts many agents into `error` simultaneously, reset them all at once at the data store layer rather than waiting for individual retries.

## Worker Zombie Accumulation — Pattern

A common cascade behind very high load:

1. A scheduled script launches a short-lived worker per agent on a fixed interval
2. Each worker calls a backend API that ultimately blocks on a slow database query
3. The worker never exits because it's waiting on the DB
4. The next interval launches another worker without checking if the prior finished
5. After hours: many stale workers + many blocked DB processes

**Cleanup:**

```bash
pgrep -f WORKER_NAME | xargs -I {} ps -o pid,etime,command -p {}
for pid in $(pgrep -f WORKER_NAME); do kill -15 $pid; done
sleep 3
for pid in $(pgrep -f WORKER_NAME); do kill -9 $pid; done
```

**Prevention:** the supervisor's zombie reaper should run **before** the load gate, or a separate cron should unconditionally kill workers older than N minutes regardless of load.

## Process Count Threshold Pitfall

Supervisors that alert above a hardcoded process-count limit produce false positives when the fleet grows. Set the threshold based on the actual expected count for your current fleet, with headroom — not a value frozen at first deployment.

## Pipeline Content Filter Bias

Content enrichment pipelines that silently filter by topic/domain can cause entire categories of input to be skipped for weeks without detection. Audit every silent filter: log what was filtered, why, and how often, so dropped categories are visible.

## Expected State (template)

| Service | Expected |
|---|---|
| HTTP API | Listening on PORT, /api/health returns 200 |
| Gateway / supervisor | Active under systemd/launchd |
| Background workers | Running under chosen process manager |
| Disk | < 80% |
| Memory | < 90% |
| Known-stopped services | Documented as STOPPED with reason |
