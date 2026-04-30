# Deployment Guide

Three deployment modes, from simplest to most capable.

## Mode 1: Local Only (5 minutes)

Run everything on your dev machine. Best for getting started.

```bash
# Install into your project
./install.sh /path/to/your/project

# Start Claude Code
cd /path/to/your/project
claude
```

You get: hooks, skills, SQLite memory, CLAUDE.md template. No Docker, no VPS, no ChromaDB.

<!-- CUSTOMIZE: This is enough for most individual developers. Scale up
     only when you need semantic search, cron jobs, or multi-agent coordination. -->

## Mode 2: Local + Docker (15 minutes)

Add ChromaDB for semantic search and the Agent Bus for multi-agent coordination.

```bash
# Start infrastructure
cp .env.example .env
# Edit .env with your API keys
docker compose up -d

# Verify
curl http://localhost:8000/api/v1/heartbeat  # ChromaDB
curl http://localhost:9800/health             # Agent Bus

# Install into your project
./install.sh /path/to/your/project
```

You get: everything in Mode 1, plus semantic search and inter-agent messaging.

## Mode 3: VPS (Always-On Agent)

For agents that run 24/7. Requires a Linux VPS.

### VPS Setup

```bash
# Provision (Hetzner CX22 recommended -- ~$5/month)
# Ubuntu 24.04, SSH key auth, non-root user

# On the VPS:
sudo apt update && sudo apt install -y python3.11 python3-pip docker.io docker-compose-v2 git

# Clone the stack
git clone https://github.com/edgeless-ai/edgeless-stack.git
cd edgeless-stack

# Configure
cp .env.example .env
nano .env  # Add API keys, Telegram token, email config

# Start infrastructure
docker compose up -d

# Install cron jobs
crontab -e
# Add:
# 0 */6 * * * /path/to/edgeless-stack/cron/cron-wrapper.sh "health" /path/to/edgeless-stack/cron/health-check.sh
# 0 */4 * * * /path/to/edgeless-stack/cron/cron-wrapper.sh "email" /path/to/edgeless-stack/cron/email-triage.sh
# 0 16  * * * /path/to/edgeless-stack/cron/cron-wrapper.sh "digest" /path/to/edgeless-stack/cron/knowledge-digest.sh
```

### Security Hardening

```bash
# SSH: disable password auth
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Firewall: allow only SSH + your services
sudo ufw allow OpenSSH
sudo ufw allow 8000/tcp  # ChromaDB (only if you need remote access)
sudo ufw enable

# Unattended upgrades
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

### systemd Service (for Claude Code agent)

```ini
# /etc/systemd/user/claude-agent.service
[Unit]
Description=Claude Code Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/claude -p "You are a production agent. Load memory, check inbox, process tasks." --dangerously-skip-permissions
WorkingDirectory=/home/agent/project
Restart=on-failure
RestartSec=30
Environment=HOME=/home/agent

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/home/agent

[Install]
WantedBy=default.target
```

```bash
# Enable and start
systemctl --user enable --now claude-agent

# Check status
systemctl --user status claude-agent
journalctl --user -u claude-agent -f
```

<!-- CUSTOMIZE: Adjust WorkingDirectory, ReadWritePaths, and the ExecStart
     prompt to match your project and agent personality. -->

## Monitoring

### Health Check Cron

The included `cron/health-check.sh` monitors:
- Disk usage (alerts above 85%)
- Memory usage
- Docker container status
- API endpoint availability
- Cron job recency

Configure alerting in `.env`:
```bash
# Telegram alerts (recommended)
TELEGRAM_BOT_TOKEN=your-token
TELEGRAM_CHAT_ID=your-chat-id

# Or email alerts
# ALERT_EMAIL=you@example.com
```

### Log Locations

| Component | Log |
|-----------|-----|
| Cron jobs | `./logs/cron-*.log` (via cron-wrapper.sh) |
| ChromaDB | `docker compose logs chromadb` |
| Agent Bus | `docker compose logs agent-bus` |
| Claude Agent | `journalctl --user -u claude-agent` |
| SQLite ledger | `./data/shared_memory/events.sqlite3` |

## Backup Strategy

```bash
# Daily: SQLite + vault
cp data/shared_memory/events.sqlite3 backups/events-$(date +%Y%m%d).sqlite3
tar czf backups/vault-$(date +%Y%m%d).tar.gz vault/

# Weekly: Full stack
tar czf backups/edgeless-stack-$(date +%Y%m%d).tar.gz \
    --exclude='chroma-data' \
    --exclude='node_modules' \
    --exclude='.git' \
    .
```

<!-- CUSTOMIZE: Add backup rotation (keep last 7 daily, last 4 weekly).
     Use `find backups/ -name "events-*" -mtime +7 -delete` for rotation. -->

---

*Part of the [Edgeless Stack](https://github.com/edgeless-ai/edgeless-stack)*
