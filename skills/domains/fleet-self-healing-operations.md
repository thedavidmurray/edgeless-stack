---
name: fleet-self-healing-operations
description: >
  Build self-monitoring, self-healing infrastructure for AI agent fleets. Detect
  ghost agents (registered but inactive), deploy activation crons, monitor
  health across multiple layers (cron execution, API availability, storage
  growth, work verification), and implement escalation protocols. Includes
  parallel backlog processing workers and automated recovery workflows. author:
  Edgeless/Hermes metadata: hermes: tags: [fleet-health, self-healing,
  monitoring, ghost-agents, cron-monitoring, escalation, parallel-workers,
  backpressure, agent-activation] complexity: advanced prerequisites:
  [paperclip-api, cron-jobs, sqlite, hermes-agent] related_skills:
  [paperclip-api, agent-optimization-infrastructure, cron-skill-review]
metadata:
  tags: [fleet, self-healing, monitoring, automation]
  tier: task-specific
  domain: tooling
when_to_apply: >
  When building self-monitoring, self-healing infrastructure for an agent fleet.
---

# Fleet Self-Healing Operations

Self-monitoring, self-healing infrastructure for AI agent fleets. Detects failures,
auto-recovers where possible, escalates to humans only when necessary.

## The Ghost Agent Problem

You have 20 agents registered in Paperclip. How many are actually working?

**Ghost agents** are registered but have:
- No activation schedules (no crons waking them)
- No work profiles (no SOUL.md, no assigned role)
- No monitoring (nobody notices they're dead)
- No recovery mechanism (when they fail, they stay dead)

They appear in dashboards. They consume mental overhead. They produce nothing.

## Five-Layer Self-Healing Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 5: Resource Consumption Health (Storage, Memory, Disk)                │
│    └─→ vault-size-monitor.py — Daily 2am tracking, auto-archive at 80%   │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 4: API Dependency Health (External Services)                          │
│    └─→ paperclip-api-health.py — 30min probes, circuit breaker pattern     │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 3: Backlog Processing Health (Work Accumulation)                      │
│    └─→ Parallel worker fleet — Auto-scale when thresholds exceeded       │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 2: Cron Execution Health (Scheduled Job Monitoring)                 │
│    └─→ cron-self-healing-monitor.py — Detect, restart, escalate          │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 1: Agent Activation Health (Ghost Agent Detection)                  │
│    └─→ agent-profile-gap-analyzer.py — Profile + cron deployment           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Layer 1: Agent Activation Health

### Detecting Ghost Agents

```bash
# Query all agents from Paperclip API
curl -s "http://127.0.0.1:3100/api/companies/${COMPANY_ID}/agents" | \
  python3 -c "
import sys, json
agents = json.load(sys.stdin)
for a in agents:
    name = a.get('name', 'unknown')
    # Check for Hermes profile
    import os
    profile_path = os.path.expanduser(f'~/.hermes/profiles/{name}')
    has_profile = os.path.exists(profile_path)
    print(f'{name:20} Profile: {\"✓\" if has_profile else \"✗\"}')
"
```

### Deploying Activation Crons

Every agent needs a heartbeat. Cron frequency depends on agent role:

| Agent Role | Activation Schedule | Cron Pattern |
|-----------|-------------------|--------------|
| Trading/Pamela | Every 5 minutes | `*/5 * * * *` |
| Code execution | Every 10 minutes | `*/10 * * * *` |
| Verification/QA | Every 15 minutes | `*/15 * * * *` |
| Ops monitoring | Every 5 minutes | `*/5 * * * *` |
| Security audit | Every 6 hours | `0 */6 * * *` |
| Creative overflow | Every 20 minutes | `*/20 * * * *` |
| Research/Scout | Every 6 hours | `0 */6 * * *` |
| Strategic/Beau | Every 8 hours | `0 */8 * * *` |
| Builder/Engineer | Every 10 minutes | `*/10 * * * *` |
| Curator/Research | Every 12 hours | `0 */12 * * *` |

**Cron job pattern:**
```bash
# ~/.hermes/cron/agent-activation-{agent_name}
*/5 * * * * cd ~/claude-projects && hermes run --agent {AGENT_ID} --prompt "Check Paperclip for assigned work. Complete one task. Report status." >> ~/.hermes/logs/{agent_name}-activation.log 2>&1
```

**Deployment script:**
```python
# deploy_agent_activation.py
ACTIVATION_SCHEDULES = {
    "trader": "*/5 * * * *",
    "kilo": "*/10 * * * *",
    "verifier": "*/15 * * * *",
    "anomaly": "*/5 * * * *",
    "cypher": "0 */6 * * *",
    "studio2": "*/20 * * * *",
    "scout": "0 */6 * * *",
    "beau": "0 */8 * * *",
    "builder": "*/10 * * * *",
    "curator": "0 */12 * * *",
}

def deploy_cron(agent_name, agent_id, schedule):
    cron_line = f"{schedule} cd ~/claude-projects && hermes run --agent {agent_id} --prompt 'Check Paperclip for assigned work...' >> ~/.hermes/logs/{agent_name}-activation.log 2>&1"
    # Add to crontab via hermes cron add
    subprocess.run(["hermes", "cron", "add", f"agent-activation-{agent_name}"], 
                 input=cron_line, text=True)
```

**Results from production deployment:**
- 10 ghost agents detected
- 6 new profiles created (Trader 2, Scout, Studio 2, Beau, Builder, Curator)
- 9 activation crons deployed
- 95% agent coverage achieved (19/20 active)

## Layer 2: Cron Execution Health

### The Self-Healing Monitor

```python
# cron-self-healing-monitor.py
#!/usr/bin/env python3
"""
Detect stale cron jobs and auto-restart or escalate
"""
import subprocess
import json
from datetime import datetime, timezone, timedelta

CRON_LIST_CMD = ["hermes", "cron", "list"]
STALE_THRESHOLD_MINUTES = 60  # Alert if no run in 60 min
RESTART_MAX_ATTEMPTS = 2

def check_cron_health():
    """Parse hermes cron list for error states"""
    result = subprocess.run(CRON_LIST_CMD, capture_output=True, text=True, timeout=30)
    output = result.stdout
    
    stale_jobs = []
    lines = output.split('\n')
    current_job = None
    
    for line in lines:
        if '[active]' in line or '[paused]' in line or '[error]' in line:
            current_job = {'lines': [], 'status': 'active' if '[active]' in line else 'error'}
        
        if current_job and 'last run:' in line.lower():
            # Parse last run time and detect errors
            if 'error:' in line.lower() or 'timeout' in line.lower():
                current_job['has_error'] = True
                current_job['error_detail'] = line
                stale_jobs.append(current_job)
    
    return stale_jobs

def attempt_restart(job_id):
    """Try to restart the cron job"""
    subprocess.run(["hermes", "cron", "restart", job_id])

def escalate_to_alerts(job_id, error_detail):
    """Post to Discord #alerts when auto-restart fails"""
    webhook_url = "https://discord.com/api/webhooks/ALERTS_ID/TOKEN"
    message = {
        "username": "Self-Healing Monitor",
        "embeds": [{
            "title": f"🚨 Cron Job Failed: {job_id}",
            "description": f"Auto-restart failed. Manual intervention required.\\n{error_detail}",
            "color": 15548997  # Red
        }]
    }
    subprocess.run(["curl", "-s", "-X", "POST", webhook_url,
                  "-H", "Content-Type: application/json",
                  "-d", json.dumps(message)])

if __name__ == "__main__":
    stale = check_cron_health()
    for job in stale:
        job_id = job.get('id')
        attempts = get_restart_attempts(job_id)
        
        if attempts < RESTART_MAX_ATTEMPTS:
            attempt_restart(job_id)
            log_restart(job_id)
        else:
            escalate_to_alerts(job_id, job.get('error_detail'))
```

### Current Production Metrics

| Metric | Value |
|--------|-------|
| Cron jobs monitored | 49 |
| Self-healing checks/day | ~288 (every 5 min) |
| Auto-restarts attempted/day | ~12 |
| Human escalations/day | ~2 |
| Mean time to detection | < 5 minutes |
| Mean time to recovery | < 10 minutes |

### Error Patterns Detected

| Error Type | Auto-restart? | Escalation |
|-----------|---------------|------------|
| Timeout (600s limit) | Yes | After 2 failed restarts |
| Exit code 1 (script error) | No | Immediate escalation |
| SSL/Certificate failure | Yes | After 1 restart |
| Rate limit (Discord 429) | Wait 5 min | Then retry |
| Resource exhaustion | No | Immediate escalation |

## Layer 3: Backlog Processing Health

### Parallel Worker Fleet

When backlog grows faster than processing, deploy parallel workers:

```python
# parallel_backlog_processor.py
AGENT_WORKER_POOL = {
    "rss": ["trader2", "scout", "scribe", "curator", "builder"],
    "youtube": ["scribe", "curator", "builder"],
    "enrichment": ["scribe", "curator"],
}

def distribute_work(source, work_items):
    """Round-robin assign to worker pool"""
    workers = AGENT_WORKER_POOL.get(source, ["scribe"])
    assignments = {}
    
    for i, item in enumerate(work_items):
        worker = workers[i % len(workers)]
        if worker not in assignments:
            assignments[worker] = []
        assignments[worker].append(item)
    
    return assignments
```

### Backlog Thresholds & Auto-scaling

| Backlog Size | Action | Workers Added |
|-------------|--------|---------------|
| < 100 items | Normal | Base pool |
| 100-500 items | Alert | None (monitor) |
| 500-1000 items | Scale | +2 workers |
| > 1000 items | Emergency | +4 workers, reduce quality gates |

**Production Results:**
- RSS backlog: 1,474 → 974 items (-34% in 24h)
- YouTube backlog: 111 → 69 items (-38%)
- 550 stale items auto-archived

### Work Verification (Anti-Cheating)

Agents can claim to work without producing. Verify actual output:

```python
# agent-work-verification.py
def verify_agent_output(agent_name, hours=4):
    """Check if agent produced actual deliverables"""
    # Check vault for recent edits
    vault_path = f"~/claude-projects/claude-vault"
    recent_files = subprocess.run(
        ["find", vault_path, "-name", "*.md", "-mtime", f"-{hours//24 + 1}"],
        capture_output=True, text=True
    ).stdout.strip().split('\n')
    
    # Check Paperclip for completed issues
    completed = query_paperclip(
        f"companies/{COMPANY_ID}/issues?assignee={agent_name}&status=done&updated=gt{hours}h"
    )
    
    # Check logs for errors
    log_errors = check_agent_logs(agent_name, hours)
    
    return {
        "vault_activity": len(recent_files),
        "completed_issues": len(completed),
        "log_errors": log_errors,
        "productive": len(recent_files) > 0 or len(completed) > 0
    }
```

## Layer 4: API Dependency Health

### Circuit Breaker Pattern

When external APIs fail, queue work for retry rather than continuously failing:

```python
# paperclip-api-health.py
CIRCUIT_BREAKER_THRESHOLD = 3  # Failures before opening
CIRCUIT_BREAKER_TIMEOUT = 300  # Seconds before trying again
COMPANY_ID = "c5ea22fb-99d2-46a1-87c6-e7fc1ab0d712"

def check_api_health():
    """Probe Paperclip API latency and availability.
    
    ⚠️ Paperclip v2026.428.0 removed /api/health. Use company-scoped endpoint.
    """
    try:
        start = time.time()
        # Valid probe endpoint (health was removed in v2026.428.0)
        response = requests.get(
            f"http://127.0.0.1:3100/api/companies/{COMPANY_ID}/agents",
            timeout=5
        )
        latency = (time.time() - start) * 1000
        
        return {
            "healthy": response.status_code == 200,
            "latency_ms": latency,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {"healthy": False, "error": str(e)}

def record_failure(api_name):
    """Track failures for circuit breaker"""
    state = load_circuit_state()
    state[api_name]["failures"] += 1
    state[api_name]["last_failure"] = time.time()
    
    if state[api_name]["failures"] >= CIRCUIT_BREAKER_THRESHOLD:
        state[api_name]["open"] = True
        alert_escalation(f"Circuit breaker OPEN for {api_name}")
    
    save_circuit_state(state)
```

### Daily 9am Blocker Digest

API dependencies that require human intervention get daily summaries:

```
📋 External Blocker Digest — 2026-04-30 09:00

🔴 Blocked >24h:
  • NotebookLM auth (EDGA-128, EDGA-145, EDGA-310, EDGA-306)
    → Action: Run `notebooklm login` in browser
  
  • SSH to VPS unavailable (EDGA-165)
    → Action: Check Hetzner status, rotate keys

🟡 Blocked 12-24h:
  • Gumroad account access (EDGA-165)
    → Action: Password reset or 2FA recovery

Total: 5 issues waiting on external resolution
```

## Layer 5: Resource Consumption Health

### Vault Size Monitoring

```python
# vault-size-monitor.py
VAULT_PATH = "~/claude-projects/claude-vault"
WARNING_THRESHOLD_GB = 8
CRITICAL_THRESHOLD_GB = 10

def check_vault_size():
    """Track storage growth and trigger archival"""
    result = subprocess.run(
        ["du", "-sh", os.path.expanduser(VAULT_PATH)],
        capture_output=True, text=True
    )
    size_str = result.stdout.split()[0]
    size_gb = parse_size(size_str)
    
    # Calculate growth rate
    history = load_size_history()
    if len(history) >= 7:
        daily_growth = (size_gb - history[-7]) / 7
    else:
        daily_growth = 0
    
    if size_gb > CRITICAL_THRESHOLD_GB:
        auto_archive_old_content(days=90)
        alert_critical(f"Vault critical: {size_gb:.1f}GB")
    elif size_gb > WARNING_THRESHOLD_GB:
        alert_warning(f"Vault warning: {size_gb:.1f}GB, {daily_growth:.1f}GB/day growth")
    
    record_size(size_gb)
```

### Auto-Archival Policy

| Age | Action |
|-----|--------|
| > 90 days | Move to `vault/99-Archive/` |
| > 180 days | Compress to `.tar.gz` |
| > 365 days | Move to cold storage (S3 Glacier) |

## Monitoring Script Suite

| Script | Frequency | Purpose | Location |
|--------|-----------|---------|----------|
| `agent-profile-gap-analyzer.py` | Daily 2am | Detect ghost agents | `~/.hermes/scripts/` |
| `cron-self-healing-monitor.py` | Every 5 min | Detect/restart stale crons | `~/.hermes/scripts/` |
| `agent-work-verification.py` | Every 4 hours | Verify actual agent output | `~/.hermes/scripts/` |
| `paperclip-api-health.py` | Every 30 min | Monitor API latency | `~/.hermes/scripts/` |
| `vault-size-monitor.py` | Daily 2am | Track storage growth | `~/.hermes/scripts/` |
| `external-blocker-escalation.py` | Daily 9am | Report stuck external deps | `~/.hermes/scripts/` |

## Evolution: Span-Based Anomaly Detection (OTel Layer)

The 5-layer stack above uses **process polling** and **cron log parsing** for detection. This is effective but coarse: it sees whether a process exists, not whether the agent is actually doing productive work. OTel spans provide finer-grained visibility.

**Span-based detection targets:**

| Detection | Process-Based Method | Span-Based Method | Precision Gain |
|-----------|----------------------|-------------------|----------------|
| **Phantom stall** | `process(list)` empty for >15 min | Parent span open with 0 child spans for >15 min | Catches Kilo May 17 loop (200+ min) at 15 min |
| **Ghost agent** | Missing cron output | Missing heartbeat spans for 2x expected interval | Confirms the *agent* not just the *cron* is dead |
| **Auth cascade** | Gateway 401 logs | `model=null` or `provider=unknown` on >3 consecutive spans | Cross-provider failure visible in one trace |
| **Loop churn** | CPU/load metrics | >10 spans/min with zero file/terminal spans | Distinguishes productive busy from empty churn |

**Implementation (SHIPPED 2026-05-18):**
- `scripts/lib/anomaly_detector.py` (~8.3 KB) queries Jaeger every 5 min for last 10 min of spans
- Detects: phantom stalls (agent span open >30 min, 0 child spans), ghost agents (no heartbeat spans for 2x cron interval), auth cascades (`model=null` or `provider=unknown` on >3 consecutive calls), loop churn (>5 spans per 5 min with zero file/terminal spans)
- Alerts post to `#alerts` via `discli` with trace_id, last tool, recommended kill action
- False positive target: <5% over 7 days
- Dashboard: `scripts/health/trace-dashboard.py` (~9.2 KB) produces Tufte-style terminal tables + Discord embeds for `#audit-log`

**Relation to existing stack:** Span-based detection is **Layer 6** of the self-healing stack. It does not replace Layers 1-5; it augments them with causal data. When a process-based alert fires, the span trace shows *why* (e.g., "last tool was `browser_click` that timed out, no recovery span followed").

**Status:** All blockers cleared. EDGA-4106 through EDGA-4113 shipped in session 2026-05-18. See `references/otel-jaeger-swarm-epic-spec.md` for original specification and `references/otel-jaeger-swarm-shipped-2026-05-18.md` for complete shipped session report with file inventory, calibration thresholds, and architecture decisions.

## Escalation Protocol

### Recovery Cascade Deadlock (Paperclip)

**Pattern:** A systemic failure creates multiple blocked tasks. The system auto-generates recovery tasks to unblock them. But the recovery tasks also get blocked (or are created with `blocked` status). Agents claim the blocked tasks and produce deliverables, but the deliverables can't be merged because the parent task is blocked. This creates a **deadlock**: source issues blocked, recovery blocked, and agents working on unclaimable issues.

**Example (EDGA-5998, 2026-05-28):**
- 73 tasks blocked simultaneously (REV-xxx revenue tasks, CLIENT tasks, recovery tasks)
- All with `blocked` status and no `blockedReason`
- Previous recovery cascade issues (EDGA-4199, EDGA-4594, EDGA-3976) were cancelled but never resolved
- Agents (Scribe, Edgeless CC) were working on blocked tasks despite the blocked status

**Detection:**
```bash
# Count blocked tasks
paperclipai issue list -C <company_id> --status blocked --json | python3 -c "import sys,json; print(len(json.load(sys.stdin)))"

# Check for cascade-related patterns
# Look for: REV-xxx, CLIENT, "Recover", "Test Client" in titles
```

**Fix:**
1. **Identify the cascade scope** — filter blocked tasks to only those created in the current cascade
2. **Change status from `blocked` to `todo`** for all cascade tasks simultaneously
3. **Do NOT change status one-by-one** — this triggers individual notifications and creates noise
4. **Update the meta-issue** (e.g., EDGA-5998) to `done` with a summary comment
5. **Verify remaining blocked tasks** are genuinely non-cascade (older issues, not related to the current event)

```python
# Bulk unblock script
import subprocess, json

cascade_ids = ["EDGA-5995", "EDGA-5990", "EDGA-5991", ...]  # all 73 IDs

for iid in cascade_ids:
    subprocess.run([
        "paperclipai", "issue", "update", iid,
        "--status", "todo",
        "--comment", "Unblocked from cascade — auto-recovery"
    ], capture_output=True)
```

**Prevention:**
- After any mass-block event, create a SINGLE meta-issue to track the cascade
- Do NOT create individual recovery tasks for each blocked task — this multiplies the problem
- The recovery system should check if a task is already blocked before creating a recovery task
- Recovery tasks should be created with `todo` status, not `blocked`
- After unblocking, monitor for 24-48 hours to ensure agents don't re-enter blocked state

### Credential Distribution Principle

**Not every agent needs every credential.** The user corrected a blanket "add GITHUB_TOKEN to all profiles" approach with two sharp questions:

1. "Do they need gh auth if they can assign to Claude Code?" — If an agent's code path routes through Claude Code (which uses desktop app auth), it may not need direct git credentials.
2. "Don't other bots have gh auth working? I don't think EVERYONE needs gh auth" — Some agents only read/query (Hive, Scribe) and never push. Others (Beau) already have working tokens.

**Apply this principle:**
- **Only provision auth to agents that ACTUALLY use the capability**
- Check the agent's AGENTS.md for git/push/PR operations before adding credentials
- If the agent runs with `cwd=~/claude-projects`, python-dotenv may already load project `.env` (GITHUB_PAT, etc.) — verify that first
- Add credentials to the SMALLEST set of profiles that genuinely need them
- Document which agent has which credential in a fleet credential matrix

**Anti-pattern:** "Everyone gets everything just in case." This creates credential sprawl, makes rotation harder, and increases blast radius if one profile is compromised.

| Condition | Priority | Channel | Action |
|-----------|----------|---------|--------|
| Auto-restart failed 2x | High | #alerts | Manual intervention required |
| 3+ agents unhealthy | Critical | #alerts + SMS | Systemic issue |
| API down >30 min | High | #alerts | Circuit breaker engaged |
| Vault >90% capacity | Medium | #audit-log | Auto-archive triggered |
| Blocker >24h old | Medium | Daily digest | Human unblock required |
| Work verification failed | High | #alerts | Agent investigation |

### Escalation Message Format

For human-facing critical alerts, rich embeds are still useful:

```json
{
  "username": "Fleet Monitor",
  "embeds": [{
    "title": "🚨 {severity}: {condition}",
    "description": "{details}",
    "fields": [
      {"name": "Affected", "value": "{agent_list}", "inline": true},
      {"name": "Duration", "value": "{time_since_failure}", "inline": true},
      {"name": "Auto-action", "value": "{attempted_recovery}", "inline": false}
    ],
    "color": 15548997,
    "timestamp": "{iso_timestamp}"
  }]
}
```

For routine bot-to-bot coordination, do **not** use verbose bracket envelopes or rich prose. Use the compact protocol in `references/compact-discord-coordination.md`:

```text
FROM>TO OP REF [flags] | body
H>K ! EDGA-147 p1 | build ContentView; verify compile
K>H + EDGA-147 | claimed
K>H = EDGA-147 | tests pass
H>* . EDGA-147 | closed
```

Rules: one ACK max, `.` closes the exchange, never reply to `.`, no thanks/goodbye/standing-by messages, no bot-to-bot @mentions, keep bodies under 240 chars unless delivering a result.

## Production Results

After 30 days of operation:

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Ghost agents | 10/20 | 1/20 | -90% |
| Cron errors undetected | ~5/day | 0 | -100% |
| Mean time to detect failure | Hours | <5 min | -95% |
| Mean time to recovery | Manual | <10 min | Automated |
| RSS backlog growth | +50/day | -20/day | Reversed |
| Human fire-drills/week | 3-4 | <1 | -75% |
| Fleet uptime | ~85% | ~98% | +13% |

## Implementation Guide

### Phase 1: Detect Ghost Agents

```bash
# 1. Query Paperclip fleet
curl -s "http://127.0.0.1:3100/api/companies/${COMPANY_ID}/agents" | \
  python3 -c "import sys,json;[print(a['name']) for a in json.load(sys.stdin)]" > /tmp/fleet.txt

# 2. Check local profiles
ls ~/.hermes/profiles/ > /tmp/local.txt

# 3. Find gaps
diff /tmp/fleet.txt /tmp/local.txt
```

### Phase 2: Deploy Activation Crons

```bash
# Deploy for each ghost agent
for agent in trader2 scout studio2 beau builder curator; do
    echo "Deploying activation cron for $agent..."
    python3 ~/.hermes/scripts/deploy_agent_activation.py $agent
done
```

### Phase 3: Enable Self-Healing Monitors

```bash
# Add to crontab via hermes cron
hermes cron add cron-self-healing-monitor "*/5 * * * * python3 ~/.hermes/scripts/cron-self-healing-monitor.py"
hermes cron add agent-work-verification "0 */4 * * * python3 ~/.hermes/scripts/agent-work-verification.py"
hermes cron add paperclip-api-health "*/30 * * * * python3 ~/.hermes/scripts/paperclip-api-health.py"
hermes cron add vault-size-monitor "0 2 * * * python3 ~/.hermes/scripts/vault-size-monitor.py"
hermes cron add external-blocker-escalation "0 9 * * * python3 ~/.hermes/scripts/external-blocker-escalation.py"
hermes cron add agent-profile-gap-analyzer "0 2 * * * python3 ~/.hermes/scripts/agent-profile-gap-analyzer.py"
```

### Phase 4: Verify Escalation Paths

```bash
# Test Discord webhooks
curl -s -X POST "https://discord.com/api/webhooks/ALERTS_ID/TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"🧪 Test alert from self-healing system"}'
```

## Troubleshooting

### Symptom: ALL API providers fail simultaneously (fleet auth cascade)

**Signal:** Every agent returns `model=null`, all gateways show 401/403 from the same provider, and fallback models also fail.

**This is a P0 fleet-blocking incident.** Automated circuit breakers cannot help when every provider is dead. The coordinator must manually triage and recover.

**Recovery:** See `swarm-coordination/references/fleet-auth-cascade-recovery.md` for the production-tested protocol:
1. Systematic provider testing with live curl inference calls (not just `/models` lists)
2. Identify the sole surviving provider
3. Backup + batch-migrate all 20+ profile configs using Python/sed
4. Fix main `~/.hermes/config.yaml` (often missed in profile-only fixes)
5. Fix `fallback_model` blocks that point to dead providers
6. Full YAML audit to confirm zero dead providers remain
7. Sequential gateway restart (30-60s spacing to avoid Discord rate limits)

**Prevention:** After recovery, add a second provider as `fallback_model` with a DIFFERENT provider than primary, and ensure credential pools have active keys for at least 2 providers at all times.

### Symptom: API health probe reports down but Paperclip is responsive

**Check:** Health probe using outdated endpoint (`/api/health` or `/api/agents`)
**Fix:** Update probe to company-scoped endpoint: `GET /api/companies/{companyId}/agents`. See `paperclip-api` skill for valid endpoints.

### Symptom: ImportError on recently-added constant/module

**Check:** Gateway or cron processes were started BEFORE the code update that introduced the new symbol.
**Root cause:** Python caches imported modules in process memory. When `hermes_constants.py` (or any shared module) is updated on disk, running processes still hold the old version. New code that imports the recently-added constant fails with `ImportError: cannot import name 'X' from 'module'`.

**Detection:**
```bash
# Compare file mtime vs process start time
stat -f "%Sm" ~/.hermes/hermes-agent/hermes_constants.py
ps -o pid,lstart,command -p <gateway_pid> | head -2
# If process started BEFORE the file was modified, the module is stale.
```

**Fix:**
1. Identify stale processes: any gateway/cron started before the code update timestamp
2. Kill them: `kill -TERM $pid` (or `kill -KILL` if unresponsive)
3. Let auto-restart or launchd respawn them — fresh processes load the new module
4. For critical agents, manually restart: `hermes gateway restart --profile <name>`

**Prevention:** After any Hermes code update (git pull, skill install, pip upgrade), always restart ALL gateway processes. The `hermes-agent` venv is an editable install — changes on disk are immediate but processes must reload.

**Real case (2026-05-25):** `PARTIAL_STREAM_STUB_ID` added to `hermes_constants.py` at 13:10. Gateways started at 13:06 failed with `ImportError`. New gateway started at 14:12 loaded the constant correctly. Killing stale PIDs and letting respawn fixed it.

---

### Symptom: API health probe intermittently fails after restart

**Check:** Paperclip may have shifted to next free port after embedded PostgreSQL crash
**Fix:** Probe 3100 first, fallback to 3101 if unreachable. The restart cycle: old process dies → new process starts on 3101 → eventually reclaims 3100. Check `server.log` for `Requested port is busy; using next free port`.

### Symptom: Monitor runs but never detects issues

**Check:** `hermes cron list` output format changed
**Fix:** Update parsing regex in monitor script

### Symptom: Auto-restart loops infinitely

**Check:** Restart counter not persisting
**Fix:** Ensure restart attempts logged to SQLite/state file

### Symptom: Escalation messages not reaching Discord

**Check 1:** Webhook URL environment variable not set
**Fix:** Add to `~/.hermes/.env` and source in cron

**Check 2:** Script uses `os.environ.get("DISCORD_BOT_TOKEN")` with silent guard
**Fix:** This is a known silent-failure pattern — see `references/cron-discord-delivery-patterns.md` for
       three approaches (direct curl ❌, Hermes send_message ✅, webhook ⚠️)

### Symptom: Ghost agent detection missing agents

**Check:** Agent name normalization (case, spaces vs dashes)
**Fix:** Normalize names when comparing Paperclip vs local profiles

## References

- Session transcript: `references/session-2026-04-30-fleet-activation.md`
- Production deployment metrics: `references/self-healing-results-30day.md`
- Monitoring script templates: `templates/cron-self-healing-monitor.py`
- Agent activation deployment: `templates/deploy-agent-activation.py`
- Cron Discord delivery patterns: `references/cron-discord-delivery-patterns.md`
- Compact Discord coordination protocol: `references/compact-discord-coordination.md`
- **Ghost agent cascade cleanup**: `references/ghost-agent-cascade-cleanup.md` — bulk-close recovery issues, reassign real work, disable broken agents
- **OTel + Jaeger swarm epic**: `references/otel-jaeger-swarm-shipped-2026-05-18.md` — full shipped session report with file inventory, calibration thresholds, architecture decisions, and trace propagation protocol
- **Full-stack restart procedures**: `references/full-stack-restart-procedures.md` — step-by-step recovery for Paperclip (embedded postgres), ChromaDB (HTTP server), and Hermes gateways when core dependencies die in a chain
- **Stale Python module cache incident**: `references/stale-python-module-cache-incident-2026-05-25.md` — detailed reproduction of the `PARTIAL_STREAM_STUB_ID` ImportError, detection method, timeline, and prevention
- **Bulk skeleton agent fix**: `references/bulk-skeleton-agent-fix.md` — automated script to fix ghost agents missing tools, skills, auth, AGENTS.md, SOUL.md
- **Recovery spam cleanup**: `references/recovery-spam-cleanup.md` — bulk cancel Paperclip recovery tasks whose parents are resolved/deleted

## Changelog

- **v1.0.0** (2026-04-30): Initial skill — ghost agent detection, five-layer 
  self-healing stack, escalation protocols, parallel backlog processing,
  production results from 19-agent fleet deployment (49 crons, 16 monitoring
  scripts, 34% backlog reduction in 24h).
