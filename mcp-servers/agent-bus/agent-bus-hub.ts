#!/usr/bin/env bun
/**
 * Agent Bus Hub v0.2.0 - Durable message router for inter-session communication
 *
 * Architecture:
 *   - SQLite persistence (survives hub restarts)
 *   - Mailbox/presence split (offline sessions keep their mailbox)
 *   - Lease+ack delivery (messages aren't lost on poll)
 *   - Dead-letter queue for unknown recipients
 *   - Message expiry (24h direct, 1h broadcast)
 *   - Auto-reconnect support (clients re-register on 404)
 *
 * Usage:
 *   bun run agent-bus-hub.ts
 *
 * Environment:
 *   AGENT_BUS_PORT           - Port (default: 9800)                    # CUSTOMIZE: change port
 *   AGENT_BUS_DB             - SQLite path (default: ./agent-bus.db)   # CUSTOMIZE: change DB location
 *   AGENT_BUS_PRESENCE_TTL_MS - Presence timeout (default: 1800000 = 30 min)
 *   AGENT_BUS_LEASE_MS       - Message lease duration (default: 30000 = 30s)
 */

import { Database } from "bun:sqlite";
import { randomUUIDv7 } from "bun";

// CUSTOMIZE: Defaults for port, database path, and timing
const PORT = parseInt(process.env.AGENT_BUS_PORT || "9800", 10);
const DB_PATH =
  process.env.AGENT_BUS_DB ||
  new URL("agent-bus.db", import.meta.url).pathname;
const PRESENCE_TTL_MS = parseInt(
  process.env.AGENT_BUS_PRESENCE_TTL_MS || "1800000",
  10
); // 30 min
const LEASE_MS = parseInt(process.env.AGENT_BUS_LEASE_MS || "30000", 10); // 30s
const DIRECT_EXPIRY_MS = 24 * 60 * 60 * 1000; // 24h
const BROADCAST_EXPIRY_MS = 60 * 60 * 1000; // 1h

// ---------------------------------------------------------------------------
// Database setup
// ---------------------------------------------------------------------------

const db = new Database(DB_PATH, { create: true });
db.exec("PRAGMA journal_mode=WAL");
db.exec("PRAGMA busy_timeout=5000");

db.exec(`
  CREATE TABLE IF NOT EXISTS mailboxes (
    name TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
  );

  CREATE TABLE IF NOT EXISTS presence (
    name TEXT PRIMARY KEY REFERENCES mailboxes(name),
    connected_at TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    connection_id TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    mailbox TEXT NOT NULL,
    "from" TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'info',
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at TEXT NOT NULL,
    leased_at TEXT,
    leased_by TEXT,
    acked_at TEXT
  );

  CREATE INDEX IF NOT EXISTS idx_messages_mailbox_status ON messages(mailbox, status);
  CREATE INDEX IF NOT EXISTS idx_messages_expires ON messages(expires_at);
`);

const startTime = Date.now();

// ---------------------------------------------------------------------------
// Prepared statements
// ---------------------------------------------------------------------------

const stmts = {
  ensureMailbox: db.prepare(
    "INSERT OR IGNORE INTO mailboxes (name) VALUES (?)"
  ),
  upsertPresence: db.prepare(`
    INSERT INTO presence (name, connected_at, last_seen, connection_id)
    VALUES (?, datetime('now'), datetime('now'), ?)
    ON CONFLICT(name) DO UPDATE SET
      last_seen = datetime('now'),
      connection_id = excluded.connection_id
  `),
  touchPresence: db.prepare(
    "UPDATE presence SET last_seen = datetime('now') WHERE name = ?"
  ),
  prunePresence: db.prepare(
    "DELETE FROM presence WHERE datetime(last_seen, '+' || ? || ' seconds') < datetime('now')"
  ),
  getPresence: db.prepare("SELECT * FROM presence WHERE name = ?"),
  listPresence: db.prepare(`
    SELECT p.name, p.connected_at, p.last_seen, p.connection_id,
           (SELECT COUNT(*) FROM messages m WHERE m.mailbox = p.name AND m.status = 'pending') AS queue_depth
    FROM presence p
  `),
  listAllMailboxes: db.prepare(`
    SELECT mb.name, mb.created_at,
           p.last_seen, p.connection_id,
           (SELECT COUNT(*) FROM messages m WHERE m.mailbox = mb.name AND m.status = 'pending') AS pending_count
    FROM mailboxes mb
    LEFT JOIN presence p ON p.name = mb.name
  `),
  insertMessage: db.prepare(`
    INSERT INTO messages (id, mailbox, "from", message, type, status, expires_at)
    VALUES (?, ?, ?, ?, ?, ?, datetime('now', '+' || ? || ' seconds'))
  `),
  pollMessages: db.prepare(`
    SELECT id, "from", message, type, created_at
    FROM messages
    WHERE mailbox = ? AND status = 'pending' AND datetime(expires_at) > datetime('now')
    ORDER BY created_at ASC
    LIMIT 50
  `),
  leaseMessages: db.prepare(`
    UPDATE messages
    SET status = 'leased', leased_at = datetime('now'), leased_by = ?
    WHERE mailbox = ? AND status = 'pending' AND datetime(expires_at) > datetime('now')
  `),
  ackMessage: db.prepare(
    "UPDATE messages SET status = 'acked', acked_at = datetime('now') WHERE id = ? AND status = 'leased'"
  ),
  ackAllForMailbox: db.prepare(
    "UPDATE messages SET status = 'acked', acked_at = datetime('now') WHERE mailbox = ? AND status = 'leased'"
  ),
  unleaseExpired: db.prepare(`
    UPDATE messages SET status = 'pending', leased_at = NULL, leased_by = NULL
    WHERE status = 'leased' AND datetime(leased_at, '+' || ? || ' seconds') < datetime('now')
  `),
  expireMessages: db.prepare(`
    UPDATE messages SET status = 'expired'
    WHERE status IN ('pending', 'leased') AND datetime(expires_at) < datetime('now')
  `),
  cleanupOld: db.prepare(`
    DELETE FROM messages
    WHERE status IN ('acked', 'expired') AND datetime(created_at, '+7 days') < datetime('now')
  `),
  mailboxExists: db.prepare("SELECT 1 FROM mailboxes WHERE name = ?"),
  pendingCount: db.prepare(
    "SELECT COUNT(*) as cnt FROM messages WHERE mailbox = ? AND status = 'pending'"
  ),
  stats: db.prepare(`
    SELECT status, COUNT(*) as cnt FROM messages GROUP BY status
  `),
};

// ---------------------------------------------------------------------------
// Maintenance loop
// ---------------------------------------------------------------------------

setInterval(() => {
  const presenceTtlSec = Math.floor(PRESENCE_TTL_MS / 1000);
  const leaseSec = Math.floor(LEASE_MS / 1000);

  stmts.prunePresence.run(presenceTtlSec);
  stmts.unleaseExpired.run(leaseSec);
  stmts.expireMessages.run();
  stmts.cleanupOld.run();
}, 30000);

// ---------------------------------------------------------------------------
// HTTP server
// ---------------------------------------------------------------------------

function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

// CUSTOMIZE: Change hostname to "0.0.0.0" to accept remote connections
Bun.serve({
  port: PORT,
  hostname: "127.0.0.1",

  async fetch(req: Request): Promise<Response> {
    const url = new URL(req.url);
    const path = url.pathname;

    // --- Health ---
    if (path === "/health" && req.method === "GET") {
      const presenceList = stmts.listPresence.all();
      const msgStats = stmts.stats.all() as Array<{
        status: string;
        cnt: number;
      }>;
      return jsonResponse({
        status: "ok",
        version: "0.2.0",
        sessions: presenceList.length,
        uptime_seconds: Math.floor((Date.now() - startTime) / 1000),
        messages: Object.fromEntries(msgStats.map((r) => [r.status, r.cnt])),
      });
    }

    // --- Register session ---
    if (path === "/register" && req.method === "POST") {
      const body = (await req.json()) as { name: string };
      const { name } = body;
      if (!name) return jsonResponse({ error: "name required" }, 400);

      const connId = randomUUIDv7();
      stmts.ensureMailbox.run(name);
      stmts.upsertPresence.run(name, connId);

      // Check for pending messages (dead-letter recovery)
      const pending = stmts.pendingCount.get(name) as { cnt: number } | null;
      const pendingCount = pending?.cnt ?? 0;

      console.log(
        `[hub] Session registered: ${name} (conn: ${connId.slice(0, 8)})` +
          (pendingCount > 0
            ? ` -- ${pendingCount} pending messages waiting`
            : "")
      );
      return jsonResponse({
        status: "registered",
        name,
        connection_id: connId,
        pending_messages: pendingCount,
      });
    }

    // --- List sessions ---
    if (path === "/sessions" && req.method === "GET") {
      const list = stmts.listPresence.all();
      return jsonResponse({ sessions: list });
    }

    // --- List all mailboxes (including offline) ---
    if (path === "/mailboxes" && req.method === "GET") {
      const list = stmts.listAllMailboxes.all();
      return jsonResponse({ mailboxes: list });
    }

    // --- Send message to specific session ---
    if (path === "/send" && req.method === "POST") {
      const body = (await req.json()) as {
        from: string;
        to: string;
        message: string;
        type?: string;
        timestamp?: string;
      };
      const { from, to, message, type } = body;

      if (!to) return jsonResponse({ error: "to required" }, 400);
      if (!message) return jsonResponse({ error: "message required" }, 400);

      // Ensure mailbox exists (even for offline recipients)
      stmts.ensureMailbox.run(to);

      const msgId = randomUUIDv7();
      const expirySec = Math.floor(DIRECT_EXPIRY_MS / 1000);
      stmts.insertMessage.run(
        msgId,
        to,
        from || "unknown",
        message,
        type || "info",
        "pending",
        expirySec
      );

      const presence = stmts.getPresence.get(to);
      const online = !!presence;

      console.log(
        `[hub] ${from} -> ${to} (${online ? "online" : "offline/mailbox"}): ${message.slice(0, 80)}`
      );
      return jsonResponse({
        status: "queued",
        message_id: msgId,
        recipient_online: online,
      });
    }

    // --- Broadcast to all online sessions ---
    if (path === "/broadcast" && req.method === "POST") {
      const body = (await req.json()) as {
        from: string;
        message: string;
        type?: string;
        timestamp?: string;
      };
      const { from, message, type } = body;

      const sessions = stmts.listPresence.all() as Array<{ name: string }>;
      let delivered = 0;
      const expirySec = Math.floor(BROADCAST_EXPIRY_MS / 1000);

      for (const s of sessions) {
        if (s.name === from) continue;
        const msgId = randomUUIDv7();
        stmts.insertMessage.run(
          msgId,
          s.name,
          from || "unknown",
          message,
          type || "broadcast",
          "pending",
          expirySec
        );
        delivered++;
      }

      console.log(`[hub] ${from} broadcast to ${delivered} sessions`);
      return jsonResponse({ status: "broadcast", delivered_to: delivered });
    }

    // --- Poll for messages (lease-based) ---
    const pollMatch = path.match(/^\/poll\/(.+)$/);
    if (pollMatch && req.method === "GET") {
      const name = decodeURIComponent(pollMatch[1]);

      // Auto-register if mailbox exists but presence expired
      const mailbox = stmts.mailboxExists.get(name);
      if (!mailbox) {
        return jsonResponse(
          {
            error: "not registered",
            messages: [],
            hint: "call /register first",
          },
          404
        );
      }

      // Touch presence
      stmts.touchPresence.run(name);

      // Get pending messages
      const messages = stmts.pollMessages.all(name);

      // Lease them (mark as leased so they survive if not acked)
      if (messages.length > 0) {
        stmts.leaseMessages.run(name, name);
      }

      return jsonResponse({ messages });
    }

    // --- Ack messages (confirm delivery) ---
    if (path === "/ack" && req.method === "POST") {
      const body = (await req.json()) as {
        name: string;
        message_ids?: string[];
      };
      const { name, message_ids } = body;

      if (!name) return jsonResponse({ error: "name required" }, 400);

      let acked = 0;
      if (message_ids && message_ids.length > 0) {
        for (const id of message_ids) {
          const result = stmts.ackMessage.run(id);
          acked += result.changes;
        }
      } else {
        // Ack all leased messages for this mailbox
        const result = stmts.ackAllForMailbox.run(name);
        acked = result.changes;
      }

      return jsonResponse({ status: "acked", count: acked });
    }

    // --- Unregister (presence only, mailbox persists) ---
    if (path === "/unregister" && req.method === "POST") {
      const body = (await req.json()) as { name: string };
      db.prepare("DELETE FROM presence WHERE name = ?").run(body.name);
      console.log(
        `[hub] Session unregistered: ${body.name} (mailbox preserved)`
      );
      return jsonResponse({ status: "unregistered" });
    }

    return jsonResponse({ error: "not found" }, 404);
  },
});

console.log(`
===================================
  Agent Bus Hub v0.2.0
  Listening on 127.0.0.1:${PORT}
  Database: ${DB_PATH}
===================================

Endpoints:
  POST /register         - Register session + create mailbox
  POST /send             - Send to session (works even if offline)
  POST /broadcast        - Broadcast to online sessions
  GET  /poll/:name       - Poll + lease messages
  POST /ack              - Confirm message delivery
  GET  /sessions         - List online sessions
  GET  /mailboxes        - List all mailboxes (incl. offline)
  GET  /health           - Hub health + message stats
  POST /unregister       - Remove presence (mailbox persists)

Waiting for sessions to connect...
`);
