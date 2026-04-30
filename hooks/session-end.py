#!/usr/bin/env python3
"""
Session End Hook (Stop event)

Saves session context, generates a summary, and optionally archives to a
vault/notes directory for continuity across sessions.

Features:
  - Session statistics (tool count, duration, errors)
  - Optional vault archiving with YAML frontmatter
  - Retrospective gating: blocks session end if a retrospective is required
    but not yet completed (configurable)
  - Security hardening: session ID sanitization, path boundary checks

CUSTOMIZE: Set environment variables or edit the Configuration section below.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# CUSTOMIZE: Adjust these for your project layout.
# ---------------------------------------------------------------------------
PROJECT_DIR = Path(os.environ.get(
    "CLAUDE_PROJECT_DIR",
    Path(__file__).parent.parent,
))
HOOKS_DIR = Path(__file__).parent
SESSION_LOG_PATH = HOOKS_DIR / "sessions.log"

# CUSTOMIZE: Where session summaries are archived (set to "" to disable).
VAULT_SESSIONS_PATH = Path(os.environ.get(
    "CLAUDE_VAULT_SESSIONS",
    str(PROJECT_DIR / "vault" / "sessions"),
))

# Retrospective thresholds -- set any to 0 to disable that trigger.
RETRO_REQUIRED_TOOL_COUNT = int(os.environ.get("RETRO_TOOL_COUNT", "10"))
RETRO_REQUIRED_DURATION_SECONDS = int(os.environ.get("RETRO_DURATION_SECS", "600"))
RETRO_REQUIRED_ERRORS = int(os.environ.get("RETRO_ERROR_COUNT", "3"))

# CUSTOMIZE: Set to False to disable retrospective gating entirely.
RETRO_GATING_ENABLED = os.environ.get("RETRO_GATING_ENABLED", "false").lower() == "true"

RETRO_TRACKING_PATH = HOOKS_DIR / ".retrospective_status.json"

# Security constants
MAX_SESSION_ID_LENGTH = 64
MAX_INPUT_SIZE = 100_000
ALLOWED_SESSION_ID_CHARS = re.compile(r"^[a-zA-Z0-9_-]+$")


# ---------------------------------------------------------------------------
# Security helpers
# ---------------------------------------------------------------------------

def sanitize_session_id(session_id: str) -> str:
    """Sanitize session ID to prevent path traversal and injection."""
    if not isinstance(session_id, str):
        return "unknown"
    session_id = session_id[:MAX_SESSION_ID_LENGTH]
    session_id = session_id.replace("..", "").replace("/", "").replace("\\", "")
    if not ALLOWED_SESSION_ID_CHARS.match(session_id):
        session_id = "".join(c for c in session_id if c.isalnum() or c in "-_")
    return session_id if session_id else "unknown"


def validate_path_within_boundary(path: Path, boundary: Path) -> bool:
    """Verify a path resolves within expected boundary."""
    try:
        return str(path.resolve()).startswith(str(boundary.resolve()))
    except (OSError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Session statistics
# ---------------------------------------------------------------------------

def get_session_stats(session_id: str) -> dict:
    """Gather session statistics from environment and optional event DB."""
    stats = {
        "tool_count": 0,
        "top_tools": [],
        "duration_seconds": 0,
        "errors": 0,
    }

    # CUSTOMIZE: If you track tool usage in a SQLite DB, query it here.
    # The original implementation reads from an events.db file.
    # For the generic version we just compute duration from env.

    session_start = os.environ.get("CLAUDE_SESSION_START")
    if session_start:
        try:
            start = datetime.fromisoformat(session_start)
            stats["duration_seconds"] = int((datetime.now() - start).total_seconds())
        except Exception:
            pass

    return stats


def log_session_end(session_id: str, stats: dict):
    """Append a session-end event to the local log."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "session_end",
        "session_id": session_id,
        "stats": stats,
    }
    try:
        with open(SESSION_LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Retrospective logic
# ---------------------------------------------------------------------------

def should_suggest_retrospective(stats: dict) -> bool:
    """Determine if session warrants a retrospective."""
    return (
        stats.get("tool_count", 0) >= RETRO_REQUIRED_TOOL_COUNT
        or stats.get("duration_seconds", 0) >= RETRO_REQUIRED_DURATION_SECONDS
        or stats.get("errors", 0) >= RETRO_REQUIRED_ERRORS
    )


def get_retrospective_status(session_id: str) -> dict:
    try:
        if RETRO_TRACKING_PATH.exists():
            with open(RETRO_TRACKING_PATH) as f:
                data = json.load(f)
                if data.get("session_id") == session_id:
                    return data
    except Exception:
        pass
    return {"completed": False}


def mark_retrospective_required(session_id: str, stats: dict):
    try:
        data = {
            "session_id": session_id,
            "required": True,
            "completed": False,
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
        }
        with open(RETRO_TRACKING_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def is_retrospective_complete(session_id: str) -> bool:
    status = get_retrospective_status(session_id)
    return status.get("completed", False)


# ---------------------------------------------------------------------------
# Vault archiving
# ---------------------------------------------------------------------------

def archive_to_vault(session_id: str, stats: dict):
    """Archive session summary as a markdown note with YAML frontmatter."""
    if not VAULT_SESSIONS_PATH or str(VAULT_SESSIONS_PATH) == "":
        return

    vault_path = Path(VAULT_SESSIONS_PATH)
    safe_session_id = sanitize_session_id(session_id)
    now = datetime.now()
    month_dir = vault_path / now.strftime("%Y-%m")

    try:
        if not validate_path_within_boundary(vault_path, PROJECT_DIR):
            return

        month_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{now.strftime('%Y-%m-%d')}-session-{safe_session_id[:8]}.md"
        filepath = month_dir / filename

        if not validate_path_within_boundary(filepath, vault_path):
            return

        if not filepath.exists():
            duration_min = stats.get("duration_seconds", 0) // 60
            top_tools_list = stats.get("top_tools", [])[:3]
            top_tools = ", ".join(
                sanitize_session_id(t.get("name", "unknown"))[:50]
                for t in top_tools_list if isinstance(t, dict)
            )

            content = f"""---
created: {now.isoformat()}
session_id: {safe_session_id}
note_type: session_log
status: completed
---

# Session Summary - {now.strftime('%Y-%m-%d %H:%M')}

## Metrics
- Duration: {duration_min} minutes
- Tool calls: {stats.get('tool_count', 0)}
- Errors: {stats.get('errors', 0)}
- Top tools: {top_tools or 'N/A'}

## Notes
*(Auto-generated session log)*
"""
            temp_filepath = filepath.with_suffix(".tmp")
            with open(temp_filepath, "w") as f:
                f.write(content)
            temp_filepath.rename(filepath)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    try:
        raw_input = sys.stdin.read(MAX_INPUT_SIZE)
        hook_input = json.loads(raw_input)
        if not isinstance(hook_input, dict):
            hook_input = {}
    except (json.JSONDecodeError, ValueError):
        hook_input = {}

    raw_session_id = os.environ.get(
        "CLAUDE_SESSION_ID", hook_input.get("session_id", "unknown")
    )
    session_id = sanitize_session_id(raw_session_id)

    stats = get_session_stats(session_id)

    # Retrospective gating (disabled by default -- set RETRO_GATING_ENABLED=true)
    if RETRO_GATING_ENABLED:
        retro_required = should_suggest_retrospective(stats)
        retro_complete = is_retrospective_complete(session_id) if retro_required else True

        if retro_required and not retro_complete:
            mark_retrospective_required(session_id, stats)
            duration_min = stats.get("duration_seconds", 0) // 60
            tool_count = stats.get("tool_count", 0)

            print(
                f"\nSESSION EXIT BLOCKED - Retrospective required!\n"
                f"   Session had {tool_count} tool calls over {duration_min} minutes.\n"
                f"   Run /retrospective before ending session.\n",
                file=sys.stderr,
            )
            print(json.dumps({"continue": False, "decision": "block"}))
            return

    log_session_end(session_id, stats)
    archive_to_vault(session_id, stats)

    # Clean up tracking file
    if RETRO_TRACKING_PATH.exists():
        try:
            RETRO_TRACKING_PATH.unlink()
        except Exception:
            pass

    print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
