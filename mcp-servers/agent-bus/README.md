# Agent Bus

Inter-session communication for Claude Code agents. Lets multiple Claude Code sessions discover each other, send direct messages, and broadcast to all connected sessions.

## Architecture

```
                    Hub (HTTP + SQLite, port 9800)
                   /          |          \
          session-1      session-2      dispatch
        (MCP server)   (MCP server)   (MCP server)
```

Two components:

- **Hub** (`agent-bus-hub.ts`) -- HTTP server with SQLite persistence. Manages session registration, message routing, and mailbox storage. Runs as a long-lived process (launchd, systemd, or just a terminal).
- **MCP Server** (`agent-bus.ts`) -- Runs inside each Claude Code session via MCP. Exposes tools and polls the hub for incoming messages every 2 seconds.

## Features

- **Durable delivery**: Messages to offline sessions are held for 24 hours.
- **Lease-based polling**: Messages are leased on poll and only removed after acknowledgment, preventing loss.
- **Broadcast**: Send to all connected sessions at once.
- **Session discovery**: List who is currently online.
- **Auto-reconnect**: Sessions re-register automatically if presence expires.
- **SQLite persistence**: Hub survives restarts without losing queued messages.

## Quick Start

```bash
# 1. Install dependencies
bun install

# 2. Start the hub
bun run agent-bus-hub.ts

# 3. Add to your .mcp.json (Claude Code config)
# See "MCP Configuration" below

# 4. Start Claude Code -- the agent-bus tools are now available
```

## MCP Configuration

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "agent-bus": {
      "command": "bun",
      "args": ["run", "/path/to/agent-bus.ts"],
      "env": {
        "AGENT_BUS_NAME": "my-session",
        "AGENT_BUS_HUB": "http://127.0.0.1:9800"
      }
    }
  }
}
```

## Tools

Once loaded, each Claude Code session gets these tools:

| Tool | Description |
|------|-------------|
| `agent_bus_set_name` | Set this session's name on the bus |
| `agent_bus_send` | Send a message to a specific session (works offline) |
| `agent_bus_broadcast` | Send a message to all connected sessions |
| `agent_bus_list` | List currently connected sessions |
| `agent_bus_status` | Check hub connectivity and stats |

## Environment Variables

### Hub (`agent-bus-hub.ts`)

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_BUS_PORT` | `9800` | HTTP port |
| `AGENT_BUS_DB` | `./agent-bus.db` | SQLite database path |
| `AGENT_BUS_PRESENCE_TTL_MS` | `1800000` (30 min) | How long before idle sessions are pruned |
| `AGENT_BUS_LEASE_MS` | `30000` (30s) | How long a message lease lasts before re-delivery |

### MCP Server (`agent-bus.ts`)

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_BUS_NAME` | `session-<pid>` | This session's name |
| `AGENT_BUS_HUB` | `http://127.0.0.1:9800` | Hub URL |
| `AGENT_BUS_POLL_MS` | `2000` | Poll interval in milliseconds |

## Hub API

The hub exposes a simple REST API (useful for debugging or external integrations):

```bash
# Health check
curl http://127.0.0.1:9800/health

# List online sessions
curl http://127.0.0.1:9800/sessions

# List all mailboxes (including offline)
curl http://127.0.0.1:9800/mailboxes

# Send a message directly
curl -X POST http://127.0.0.1:9800/send \
  -H 'Content-Type: application/json' \
  -d '{"from":"cli","to":"dispatch","message":"hello","type":"info"}'
```

## Testing

```bash
# Start the hub first, then:
bun run test-bus.ts
```

## Running as a Service

### macOS (launchd)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.agent-bus.hub</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/bun</string>
        <string>run</string>
        <string>/path/to/agent-bus-hub.ts</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/agent-bus-hub.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/agent-bus-hub.log</string>
</dict>
</plist>
```

### Linux (systemd)

```ini
[Unit]
Description=Agent Bus Hub
After=network.target

[Service]
ExecStart=/path/to/bun run /path/to/agent-bus-hub.ts
Restart=always
Environment=AGENT_BUS_PORT=9800

[Install]
WantedBy=default.target
```
