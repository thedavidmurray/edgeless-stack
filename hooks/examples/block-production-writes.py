#!/usr/bin/env python3
"""
Example Hook: Block Production Writes

A minimal PreToolUse hook that blocks writes to production directories.
Use this as a starting point for writing your own hooks.

Hook contract:
  - Reads JSON from stdin with keys: tool_name, tool_input
  - Exit 0 to ALLOW the tool call
  - Exit 2 to BLOCK the tool call (print reason to stderr)

To install, add to your .claude/settings.json:

    {
      "hooks": {
        "PreToolUse": [
          {
            "matcher": "Write|Edit",
            "hooks": ["python hooks/examples/block-production-writes.py"]
          }
        ]
      }
    }
"""

import sys
from pathlib import Path

# Add the hooks lib to path for shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from __init__ import read_hook_input, get_tool_info, block, allow  # noqa: E402

# CUSTOMIZE: Directories that should never receive writes.
BLOCKED_PATHS = [
    "/var/www/production/",
    "/opt/app/release/",
    # Add your own production paths here
]

# CUSTOMIZE: Patterns that bypass the block (e.g., config hot-reload files).
ALLOWED_PATTERNS = [
    ".env.local",
    "/tmp/",
]


def main():
    hook_input = read_hook_input()
    if not hook_input:
        allow()

    tool_name, tool_input = get_tool_info(hook_input)

    # Only check Write and Edit tools
    if tool_name not in ("Write", "Edit"):
        allow()

    file_path = tool_input.get("file_path", "")
    if not file_path:
        allow()

    # Check allowlist first
    for pattern in ALLOWED_PATTERNS:
        if pattern in file_path:
            allow()

    # Check blocked paths
    for blocked in BLOCKED_PATHS:
        if file_path.startswith(blocked):
            block(
                f"BLOCKED: Cannot write to production directory.\n"
                f"Path: {file_path}\n"
                f"Matched rule: {blocked}\n"
                f"Move to a staging directory first."
            )

    allow()


if __name__ == "__main__":
    main()
