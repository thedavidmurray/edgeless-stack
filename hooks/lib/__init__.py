"""
Shared utilities for Claude Code hooks.

Provides common patterns used across PreToolUse, PostToolUse, and notification hooks.
"""

import json
import sys
from typing import Any, Dict, Optional, Tuple


def read_hook_input(max_size: int = 100_000) -> Dict[str, Any]:
    """
    Read and parse JSON hook input from stdin.

    Claude Code passes hook context as a JSON object on stdin.
    Returns an empty dict on parse failure (fail-open).

    Args:
        max_size: Maximum bytes to read from stdin (default 100KB).

    Returns:
        Parsed JSON dict, or empty dict on error.
    """
    try:
        raw = sys.stdin.read(max_size)
        data = json.loads(raw)
        if not isinstance(data, dict):
            return {}
        return data
    except (json.JSONDecodeError, ValueError, EOFError):
        return {}


def get_tool_info(hook_input: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Extract tool name and tool input from hook data.

    Handles both PreToolUse and PostToolUse schemas.

    Returns:
        Tuple of (tool_name, tool_input_dict).
    """
    tool_name = hook_input.get("tool_name", hook_input.get("tool", ""))
    tool_input = hook_input.get("tool_input", hook_input.get("input", {}))

    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except json.JSONDecodeError:
            tool_input = {}

    return tool_name, tool_input


def block(reason: str) -> None:
    """
    Block tool execution (PreToolUse hooks only).

    Prints reason to stderr and exits with code 2.
    """
    print(reason, file=sys.stderr)
    sys.exit(2)


def allow() -> None:
    """Allow tool execution (PreToolUse hooks only). Exits with code 0."""
    sys.exit(0)


def continue_response(extra: Optional[Dict[str, Any]] = None) -> None:
    """
    Emit a PostToolUse continue response and exit.

    Args:
        extra: Additional keys to merge into the response dict.
    """
    response = {"continue": True}
    if extra:
        response.update(extra)
    print(json.dumps(response))
    sys.exit(0)
