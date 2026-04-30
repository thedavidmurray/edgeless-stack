# Writing Custom Hooks

Hooks are Python scripts that intercept Claude Code tool calls. They're the safety net that prevents agents from doing things they shouldn't.

## How Hooks Work

1. Claude Code is about to execute a tool (e.g., `Write`, `Bash`, `Edit`)
2. Your hook receives the tool name and input as JSON on stdin
3. Your hook prints a JSON response to stdout
4. Claude Code acts on the response (`allow`, `block`, or `modify`)

```
Claude Code                 Your Hook
    │                          │
    ├── stdin: {tool, input} ──>│
    │                          │── logic ──
    │<── stdout: {decision} ───│
    │                          │
    ▼ (proceeds or blocks)
```

## Hook Types

| Type | When | Use For |
|------|------|---------|
| **PreToolUse** | Before tool executes | Block dangerous commands, enforce directory rules |
| **PostToolUse** | After tool executes | Verify outputs, archive content, track costs |
| **Start** | Session begins | Load memory, set up context |
| **Stop** | Session ends | Save session summary, clean up |

## Minimal Hook Template

```python
#!/usr/bin/env python3
"""Hook description here."""

import json
import sys

def main():
    event = json.loads(sys.stdin.read())
    tool = event.get("tool_name", "")
    input_data = event.get("tool_input", {})

    # Your logic here
    if should_block(tool, input_data):
        print(json.dumps({
            "decision": "block",
            "reason": "Why this was blocked"
        }))
    else:
        print(json.dumps({"decision": "allow"}))

def should_block(tool, input_data):
    # CUSTOMIZE: Add your rules here
    return False

if __name__ == "__main__":
    main()
```

## Registering Hooks

Add hooks to `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "*",
        "command": "python3 .claude/hooks/my-hook.py"
      }
    ]
  }
}
```

The `matcher` field filters which tools trigger the hook:
- `"*"` -- all tools
- `"Bash"` -- only Bash commands
- `"Write"` -- only file writes

## Common Patterns

### Block Destructive Commands (PreToolUse)

```python
BLOCKED_PATTERNS = [
    "rm -rf /",
    "git push --force",
    "DROP TABLE",
    "DROP DATABASE",
    "chmod 777",
    # CUSTOMIZE: Add patterns relevant to your project
]

if tool == "Bash":
    command = input_data.get("command", "")
    for pattern in BLOCKED_PATTERNS:
        if pattern in command:
            print(json.dumps({
                "decision": "block",
                "reason": f"Blocked destructive command: {pattern}"
            }))
            return
```

### Enforce Directory Structure (PreToolUse)

```python
ALLOWED_WRITE_DIRS = [
    "src/",
    "tests/",
    "docs/",
    # CUSTOMIZE: Add your project directories
]

if tool == "Write":
    path = input_data.get("file_path", "")
    if not any(path.startswith(d) for d in ALLOWED_WRITE_DIRS):
        print(json.dumps({
            "decision": "block",
            "reason": f"Writes only allowed in: {', '.join(ALLOWED_WRITE_DIRS)}"
        }))
```

### Archive Web Fetches (PostToolUse)

```python
import os
from datetime import datetime

if tool == "WebFetch":
    url = input_data.get("url", "")
    content = event.get("tool_output", "")

    vault_path = os.environ.get("VAULT_PATH", "./vault")
    archive_dir = os.path.join(vault_path, "00-Inbox", "web")
    os.makedirs(archive_dir, exist_ok=True)

    slug = url.split("/")[-1][:50] or "page"
    filename = f"{datetime.now().strftime('%Y%m%d')}-{slug}.md"

    with open(os.path.join(archive_dir, filename), "w") as f:
        f.write(f"---\nsource: {url}\ndate: {datetime.now().isoformat()}\ntrust: low\n---\n\n{content[:5000]}")
```

### Track Token Costs (PostToolUse)

```python
import os

COST_LOG = os.environ.get("COST_LOG", "./logs/costs.jsonl")

# Log every tool call with timestamp
entry = {
    "timestamp": datetime.now().isoformat(),
    "tool": tool,
    "session": os.environ.get("CLAUDE_SESSION_ID", "unknown"),
}
with open(COST_LOG, "a") as f:
    f.write(json.dumps(entry) + "\n")
```

## Testing Hooks

Test hooks by piping JSON to stdin:

```bash
echo '{"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}}' | python3 .claude/hooks/damage-control.py
# Should output: {"decision": "block", "reason": "..."}

echo '{"tool_name": "Bash", "tool_input": {"command": "git status"}}' | python3 .claude/hooks/damage-control.py
# Should output: {"decision": "allow"}
```

## Tips

- **Keep hooks fast**: They run on every tool call. Avoid network requests or heavy computation.
- **Fail open**: If your hook crashes, Claude Code continues (it won't block forever). Log the error for debugging.
- **Layer hooks**: Use multiple small hooks instead of one giant one. Easier to debug and customize.
- **Use environment variables**: Don't hardcode paths. Use `.env` so the same hooks work across projects.

---

*Part of the [Edgeless Stack](https://github.com/edgeless-ai/edgeless-stack)*
