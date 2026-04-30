#!/usr/bin/env bun
/**
 * Test script for Agent Bus Hub
 *
 * Registers sessions, sends messages, and verifies delivery.
 * Requires the hub to be running: bun run agent-bus-hub.ts
 *
 * Usage: bun run test-bus.ts
 */

// CUSTOMIZE: Change if your hub runs on a different port
const HUB_URL = process.env.AGENT_BUS_HUB || "http://127.0.0.1:9800";

async function json(url: string, method = "GET", body?: unknown) {
  const opts: RequestInit = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  return { status: res.status, data: await res.json() };
}

async function test() {
  console.log("=== Agent Bus Hub Tests ===\n");

  // 1. Health check
  console.log("1. Health check...");
  const health = await json(`${HUB_URL}/health`);
  console.assert(health.status === 200, "Health should return 200");
  console.assert(
    (health.data as { status: string }).status === "ok",
    "Status should be ok"
  );
  console.log("   PASS\n");

  // 2. Register sessions
  console.log("2. Register sessions...");
  await json(`${HUB_URL}/register`, "POST", { name: "test-session-1" });
  await json(`${HUB_URL}/register`, "POST", { name: "test-session-2" });
  await json(`${HUB_URL}/register`, "POST", { name: "test-dispatch" });
  const sessions = await json(`${HUB_URL}/sessions`);
  const sessionList = (sessions.data as { sessions: Array<{ name: string }> })
    .sessions;
  const testSessions = sessionList.filter((s) => s.name.startsWith("test-"));
  console.assert(testSessions.length === 3, "Should have 3 test sessions");
  console.log(
    `   Registered: ${testSessions.map((s) => s.name).join(", ")}`
  );
  console.log("   PASS\n");

  // 3. Direct message
  console.log("3. Direct message (test-session-1 -> test-session-2)...");
  const send = await json(`${HUB_URL}/send`, "POST", {
    from: "test-session-1",
    to: "test-session-2",
    message: "Hey, can you review the auth module?",
    type: "request",
    timestamp: new Date().toISOString(),
  });
  console.assert(send.status === 200, "Send should return 200");
  console.log("   PASS\n");

  // 4. Poll messages
  console.log("4. Poll messages (test-session-2)...");
  const poll = await json(`${HUB_URL}/poll/test-session-2`);
  const messages = (
    poll.data as {
      messages: Array<{ from: string; message: string; type: string }>;
    }
  ).messages;
  console.assert(messages.length >= 1, "Should have at least 1 message");
  console.assert(
    messages[0].from === "test-session-1",
    "From should be test-session-1"
  );
  console.log(`   Got: "${messages[0].message.slice(0, 60)}"`);
  console.log("   PASS\n");

  // 5. Broadcast
  console.log("5. Broadcast (test-dispatch -> all)...");
  const broadcast = await json(`${HUB_URL}/broadcast`, "POST", {
    from: "test-dispatch",
    message: "All sessions: new task available",
    type: "alert",
    timestamp: new Date().toISOString(),
  });
  const delivered = (broadcast.data as { delivered_to: number }).delivered_to;
  console.assert(delivered >= 2, "Should deliver to at least 2 (not self)");
  console.log(`   Delivered to ${delivered} sessions`);
  console.log("   PASS\n");

  // 6. Cleanup: unregister test sessions
  console.log("6. Cleanup...");
  await json(`${HUB_URL}/unregister`, "POST", { name: "test-session-1" });
  await json(`${HUB_URL}/unregister`, "POST", { name: "test-session-2" });
  await json(`${HUB_URL}/unregister`, "POST", { name: "test-dispatch" });
  console.log("   PASS\n");

  console.log("=== All tests passed ===");
}

try {
  await test();
} catch (e) {
  console.error("Test failed:", e);
  process.exit(1);
}
