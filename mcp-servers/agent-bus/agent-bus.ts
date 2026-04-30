#!/usr/bin/env bun
/**
 * Agent Bus MCP Server v0.2.0 - Inter-session communication for Claude Code
 *
 * This is the MCP server that each Claude Code session runs. It connects
 * to the Agent Bus Hub (HTTP server) and exposes tools for sending/receiving
 * messages between sessions.
 *
 * Tools provided:
 *   - agent_bus_set_name: Set your session name
 *   - agent_bus_send: Send a message to a specific session
 *   - agent_bus_broadcast: Send a message to all connected sessions
 *   - agent_bus_list: List connected sessions
 *   - agent_bus_status: Check hub connectivity
 *
 * Environment:
 *   AGENT_BUS_NAME     - Session name (default: session-<pid>)         # CUSTOMIZE
 *   AGENT_BUS_HUB      - Hub URL (default: http://127.0.0.1:9800)     # CUSTOMIZE
 *   AGENT_BUS_POLL_MS  - Poll interval in ms (default: 2000)          # CUSTOMIZE
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Session name resolution order:
// 1. AGENT_BUS_NAME env var
// 2. ~/.claude-session-name file
// 3. Fallback: session-<pid>
function resolveSessionName(): string {
  if (process.env.AGENT_BUS_NAME && process.env.AGENT_BUS_NAME !== "default") {
    return process.env.AGENT_BUS_NAME;
  }
  try {
    // CUSTOMIZE: Change this path if you store session names elsewhere
    const nameFile = `${process.env.HOME}/.claude-session-name`;
    const name = require("fs").readFileSync(nameFile, "utf-8").trim();
    if (name) return name;
  } catch {}
  return `session-${process.pid}`;
}

let SESSION_NAME = resolveSessionName();

// CUSTOMIZE: Hub URL and poll interval
const HUB_URL = process.env.AGENT_BUS_HUB || "http://127.0.0.1:9800";
const POLL_INTERVAL_MS = parseInt(
  process.env.AGENT_BUS_POLL_MS || "2000",
  10
);

// --- MCP Server ---

const mcp = new Server(
  { name: "agent-bus", version: "0.2.0" },
  {
    capabilities: {
      experimental: { "claude/channel": {} },
      tools: {},
    },
    instructions: `You are connected to the Agent Bus channel as "${SESSION_NAME}".

Messages from other Claude Code sessions arrive as <channel source="agent-bus" from="..." type="...">.

You have these tools:
- agent_bus_set_name: Set your session name (call this first if your name shows as "default")
- agent_bus_send: Send a message to another session by name (works even if they're offline -- message is held for 24h)
- agent_bus_broadcast: Send a message to ALL connected sessions
- agent_bus_list: List all currently connected sessions
- agent_bus_status: Check hub connectivity

When you receive a message, respond appropriately. If the message has reply_to="${SESSION_NAME}", it is addressed to you.
If it has type="request", the sender expects a response -- use agent_bus_send to reply.
If it has type="broadcast", it is informational.

Keep responses concise when replying through the bus. Include your session name so the recipient knows who answered.`,
  }
);

// --- Tool Handlers ---

mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "agent_bus_send",
      description:
        "Send a message to a specific Claude Code session via the Agent Bus. Messages are held for 24h even if the recipient is offline.",
      inputSchema: {
        type: "object",
        properties: {
          target: {
            type: "string",
            description:
              'Name of the target session (e.g. "session-1", "dispatch")',
          },
          message: {
            type: "string",
            description: "The message content to send",
          },
          type: {
            type: "string",
            enum: ["info", "request", "response", "alert"],
            description: "Message type (default: info)",
          },
        },
        required: ["target", "message"],
      },
    },
    {
      name: "agent_bus_broadcast",
      description: "Broadcast a message to ALL connected Claude Code sessions",
      inputSchema: {
        type: "object",
        properties: {
          message: {
            type: "string",
            description: "The message content to broadcast",
          },
          type: {
            type: "string",
            enum: ["info", "alert", "status"],
            description: "Message type (default: info)",
          },
        },
        required: ["message"],
      },
    },
    {
      name: "agent_bus_list",
      description: "List all currently connected sessions on the Agent Bus",
      inputSchema: {
        type: "object",
        properties: {},
      },
    },
    {
      name: "agent_bus_status",
      description:
        "Check Agent Bus hub connectivity and session registration",
      inputSchema: {
        type: "object",
        properties: {},
      },
    },
    {
      name: "agent_bus_set_name",
      description:
        "Set this session's name on the Agent Bus (re-registers with hub)",
      inputSchema: {
        type: "object",
        properties: {
          name: {
            type: "string",
            description:
              'Session name (e.g. "session-1", "dispatch", "codex-1")',
          },
        },
        required: ["name"],
      },
    },
  ],
}));

mcp.setRequestHandler(CallToolRequestSchema, async (req) => {
  const args = req.params.arguments as Record<string, string>;

  switch (req.params.name) {
    case "agent_bus_send": {
      const { target, message, type = "info" } = args;
      try {
        const res = await fetch(`${HUB_URL}/send`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            from: SESSION_NAME,
            to: target,
            message,
            type,
            timestamp: new Date().toISOString(),
          }),
        });
        const data = (await res.json()) as {
          status?: string;
          error?: string;
          message_id?: string;
          recipient_online?: boolean;
        };
        if (!res.ok) {
          return {
            content: [
              {
                type: "text" as const,
                text: `Failed to send: ${data.error || res.statusText}`,
              },
            ],
          };
        }
        const onlineStatus = data.recipient_online
          ? "online"
          : "offline (held in mailbox)";
        return {
          content: [
            {
              type: "text" as const,
              text: `Sent to ${target}: ${data.status} (recipient: ${onlineStatus}, id: ${data.message_id?.slice(0, 8)})`,
            },
          ],
        };
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return {
          content: [
            { type: "text" as const, text: `Hub unreachable: ${msg}` },
          ],
        };
      }
    }

    case "agent_bus_broadcast": {
      const { message, type = "info" } = args;
      try {
        const res = await fetch(`${HUB_URL}/broadcast`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            from: SESSION_NAME,
            message,
            type,
            timestamp: new Date().toISOString(),
          }),
        });
        const data = (await res.json()) as { delivered_to?: number };
        return {
          content: [
            {
              type: "text" as const,
              text: `Broadcast sent to ${data.delivered_to || 0} sessions`,
            },
          ],
        };
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return {
          content: [
            { type: "text" as const, text: `Hub unreachable: ${msg}` },
          ],
        };
      }
    }

    case "agent_bus_list": {
      try {
        const res = await fetch(`${HUB_URL}/sessions`);
        const data = (await res.json()) as {
          sessions: Array<{
            name: string;
            connected_at: string;
            last_seen: string;
            queue_depth?: number;
          }>;
        };
        const list = data.sessions
          .map(
            (s) =>
              `  ${s.name} (connected: ${s.connected_at}, last seen: ${s.last_seen}${s.queue_depth ? `, pending: ${s.queue_depth}` : ""})`
          )
          .join("\n");
        return {
          content: [
            {
              type: "text" as const,
              text: `Connected sessions:\n${list || "  (none)"}`,
            },
          ],
        };
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return {
          content: [
            { type: "text" as const, text: `Hub unreachable: ${msg}` },
          ],
        };
      }
    }

    case "agent_bus_status": {
      try {
        const res = await fetch(`${HUB_URL}/health`);
        const data = (await res.json()) as {
          status: string;
          version?: string;
          sessions: number;
          uptime_seconds: number;
          messages?: Record<string, number>;
        };
        const msgInfo = data.messages
          ? ` | Messages: ${JSON.stringify(data.messages)}`
          : "";
        return {
          content: [
            {
              type: "text" as const,
              text: `Hub: ${data.status} (v${data.version || "0.1"}) | Sessions: ${data.sessions} | Uptime: ${data.uptime_seconds}s${msgInfo} | This session: ${SESSION_NAME}`,
            },
          ],
        };
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return {
          content: [
            { type: "text" as const, text: `Hub unreachable: ${msg}` },
          ],
        };
      }
    }

    case "agent_bus_set_name": {
      const oldName = SESSION_NAME;
      SESSION_NAME = args.name;
      // Unregister old name, register new
      try {
        await fetch(`${HUB_URL}/unregister`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: oldName }),
        });
      } catch {}
      const ok = await registerWithHub();
      return {
        content: [
          {
            type: "text" as const,
            text: ok
              ? `Renamed from "${oldName}" to "${SESSION_NAME}" and re-registered with hub`
              : `Renamed to "${SESSION_NAME}" but hub registration failed`,
          },
        ],
      };
    }

    default:
      throw new Error(`Unknown tool: ${req.params.name}`);
  }
});

// --- Connect to Claude Code over stdio ---
await mcp.connect(new StdioServerTransport());

// --- Register with hub and poll for messages ---

async function registerWithHub(): Promise<boolean> {
  try {
    const res = await fetch(`${HUB_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: SESSION_NAME }),
    });
    if (res.ok) {
      const data = (await res.json()) as { pending_messages?: number };
      if (data.pending_messages && data.pending_messages > 0) {
        console.error(
          `[agent-bus] ${data.pending_messages} pending messages waiting`
        );
      }
    }
    return res.ok;
  } catch {
    return false;
  }
}

async function ackMessages(messageIds: string[]): Promise<void> {
  try {
    await fetch(`${HUB_URL}/ack`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: SESSION_NAME, message_ids: messageIds }),
    });
  } catch {
    // Best effort -- messages will be re-delivered if ack fails
  }
}

async function pollMessages(): Promise<void> {
  try {
    const res = await fetch(`${HUB_URL}/poll/${SESSION_NAME}`);

    // Auto-reconnect on 404 (presence expired or hub restarted)
    if (res.status === 404) {
      console.error(`[agent-bus] Session expired, re-registering...`);
      await registerWithHub();
      return;
    }

    if (!res.ok) return;

    const data = (await res.json()) as {
      messages: Array<{
        id: string;
        from: string;
        message: string;
        type: string;
        created_at: string;
      }>;
    };

    const ackedIds: string[] = [];

    for (const msg of data.messages) {
      try {
        await mcp.notification({
          method: "notifications/claude/channel",
          params: {
            content: msg.message,
            meta: {
              from: msg.from,
              type: msg.type,
              timestamp: msg.created_at,
              reply_to: SESSION_NAME,
            },
          },
        });
        // Notification succeeded -- ack this message
        if (msg.id) ackedIds.push(msg.id);
      } catch (e) {
        console.error(
          `[agent-bus] Failed to deliver message ${msg.id}: ${e}`
        );
        // Don't ack -- message will be re-delivered on next poll
      }
    }

    // Ack successfully delivered messages
    if (ackedIds.length > 0) {
      await ackMessages(ackedIds);
    }
  } catch {
    // Hub unavailable, will retry next poll
  }
}

// Register and start polling
const registered = await registerWithHub();
if (registered) {
  console.error(
    `[agent-bus] Registered as "${SESSION_NAME}" with hub at ${HUB_URL}`
  );
} else {
  console.error(
    `[agent-bus] WARNING: Could not register with hub at ${HUB_URL}. Start the hub first.`
  );
}

// Poll loop
setInterval(pollMessages, POLL_INTERVAL_MS);
