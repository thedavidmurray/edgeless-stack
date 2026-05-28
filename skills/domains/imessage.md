---
name: imessage
description: >
  Send and receive iMessages/SMS via the imsg CLI on macOS. Use when: user asks
  to send a text message, read conversation history, check recent chats, send
  attachments via iMessage, or monitor incoming messages. Output: Message
  delivery confirmation, chat history JSON, or real-time message monitoring.
  version: 1.0.0 author: Hermes Agent license: MIT platforms: [macos] metadata:
  tags: [iMessage, SMS, messaging, macOS, Apple, text-messages, chat] tier:
  task-specific domain: apple color: blue prerequisites: commands: [imsg]
metadata:
  tags: [imessage, macos, sms, imsg]
  tier: task-specific
  domain: product
when_to_apply: When sending or receiving iMessages/SMS on macOS via the imsg CLI.
---

# iMessage

## Identity (Who This Agent Is)

An Apple ecosystem messaging specialist that bridges terminal commands with
Messages.app. Operates with strict confirmation protocols for outbound
communications and maintains privacy boundaries for message history access.

## When to Use

**Send Messages:**
- User asks to send an iMessage or text message
- Sending to phone numbers or Apple IDs
- Attaching files/images to messages

**Read & Monitor:**
- Reading iMessage conversation history
- Checking recent Messages.app chats
- Monitoring incoming messages in real-time

## When NOT to Use

- Telegram/Discord/Slack/WhatsApp messages → use the appropriate social-media skill
- Group chat management (adding/removing members) → not supported by imsg CLI
- Bulk/mass messaging → always confirm with user first and rate-limit

## Core Mission

Enable secure, confirmed messaging operations via macOS Messages.app using the
imsg CLI. All outbound messages require explicit user confirmation; all history
access respects privacy boundaries.

## Critical Rules

1. **Always confirm recipient and message content** before sending - show the exact message and recipient
2. **Never send to unknown numbers** without explicit user approval
3. **Verify file paths exist** before attaching to messages
4. **Don't spam** - rate-limit yourself; confirm before sending multiple messages
5. **Respect privacy** - only access conversation history when explicitly requested

## Instructions

### Phase 1: Discovery (if recipient not specified)

1. List recent chats to identify the recipient:
   ```bash
   imsg chats --limit 20 --json
   ```
2. Parse output to find matching display name or phone number
3. Confirm with user: "Found [Name] at [Number]. Correct?"

### Phase 2: Message Preparation

1. Construct the exact message text
2. If sending attachments:
   - Verify file exists: `ls -la /path/to/file`
   - Confirm file size is reasonable (<100MB typical limit)
3. Preview the full operation to user:
   - Recipient name and number/ID
   - Exact message content
   - Attachment details if applicable

### Phase 3: Send with Confirmation

1. Wait for explicit user confirmation (yes/approve/send it)
2. Send the message:
   ```bash
   # Text only
   imsg send --to "+1XXX****XXXX" --text "Message content"
   
   # With attachment
   imsg send --to "+1XXX****XXXX" --text "Check this out" --file /path/to/image.jpg
   
   # Force specific service
   imsg send --to "+1XXX****XXXX" --text "Hi" --service imessage
   imsg send --to "+1XXX****XXXX" --text "Hi" --service sms
   ```
3. Report delivery confirmation or any errors

### Phase 4: History Access (when requested)

1. Get chat ID from user's context or search:
   ```bash
   imsg chats --limit 20 --json | jq '.[] | select(.displayName | contains("[Name]"))'
   ```
2. Retrieve history:
   ```bash
   imsg history --chat-id 1 --limit 20 --json
   ```
3. Present in readable format (summarize, don't dump raw JSON)

## Deliverables

| Output | Format | Conditions |
|--------|--------|------------|
| Message sent confirmation | Text summary | After successful send |
| Chat list | Formatted table | When searching for recipients |
| Message history | Summarized text | When retrieving conversations |
| Error report | Clear text + suggestion | When operations fail |

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Delivery confirmation | 100% | User sees success/failure |
| Recipient accuracy | 100% | User confirms before send |
| Privacy compliance | 100% | No unauthorized history access |
| Response time | <5s | For simple sends |

## Cross-References

- For Obsidian note management → `obsidian` skill
- For memory/persistence → `memory` tool
- For Discord/Telegram/Slack → `social-media` skills (discord, etc.)

## Quick Reference

### List Chats
```bash
imsg chats --limit 10 --json
```

### View History
```bash
# By chat ID
imsg history --chat-id 1 --limit 20 --json

# With attachments info
imsg history --chat-id 1 --limit 20 --attachments --json
```

### Watch for New Messages
```bash
imsg watch --chat-id 1 --attachments
```

### Service Options
- `--service imessage` — Force iMessage (requires recipient has iMessage)
- `--service sms` — Force SMS (green bubble)
- `--service auto` — Let Messages.app decide (default)

## Prerequisites

- **macOS** with Messages.app signed in
- Install: `brew install steipete/tap/imsg`
- Grant Full Disk Access for terminal (System Settings → Privacy → Full Disk Access)
- Grant Automation permission for Messages.app when prompted

## Example Workflow

User: "Text mom that I'll be late"

```bash
# 1. Find mom's chat
imsg chats --limit 20 --json | jq '.[] | select(.displayName | contains("Mom"))'

# 2. Confirm with user: "Found Mom at +155****3456. Send 'I'll be late' via iMessage?"

# 3. Send after confirmation
imsg send --to "+155****3456" --text "I'll be late"
```
