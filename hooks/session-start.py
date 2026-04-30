#!/usr/bin/env python3
"""
Session Start Hook (Stop event -- fires at the start of a new session)

Auto-initializes session context: assigns a session ID, checks memory system
availability, and optionally checks backlog staleness.

Outputs a JSON response with session metadata and optional user-facing messages.

CUSTOMIZE: Set MEMORY_INIT_PATH and BACKLOG_DIR to match your project layout,
or set the environment variables CLAUDE_MEMORY_INIT and CLAUDE_BACKLOG_DIR.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add lib to path
LIB_PATH = Path(__file__).parent / "lib"
sys.path.insert(0, str(LIB_PATH))

# ---------------------------------------------------------------------------
# Configuration
# CUSTOMIZE: Point these at your memory initializer and backlog directory.
# ---------------------------------------------------------------------------
PROJECT_DIR = Path(os.environ.get(
    "CLAUDE_PROJECT_DIR",
    Path(__file__).parent.parent  # assumes hooks/ is one level below project root
))

MEMORY_INIT_PATH = Path(os.environ.get(
    "CLAUDE_MEMORY_INIT",
    str(PROJECT_DIR / ".claude" / "memory" / "session_initializer.py")
))

SESSION_LOG_PATH = Path(__file__).parent / "sessions.log"


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def log_session_start(session_id: str, metadata: dict = None):
    """Append a session-start event to the local log."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "session_start",
        "session_id": session_id,
        "metadata": metadata or {},
    }
    try:
        with open(SESSION_LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def check_memory_system() -> dict:
    """Check if the memory system initializer exists and list connectors."""
    status = {"available": False, "initialized": False, "systems": []}

    if MEMORY_INIT_PATH.exists():
        status["available"] = True
        connectors_dir = MEMORY_INIT_PATH.parent / "connectors"
        if connectors_dir.exists():
            for connector in connectors_dir.glob("*_connector.py"):
                system_name = connector.stem.replace("_connector", "")
                status["systems"].append(system_name)

    return status


def check_backlog_staleness() -> dict:
    """
    Check if a backlog directory has changed since the last recorded sync.

    CUSTOMIZE: Override via CLAUDE_BACKLOG_DIR env var or replace this function
    with your own staleness check.
    """
    backlog_dir = Path(os.environ.get(
        "CLAUDE_BACKLOG_DIR",
        str(PROJECT_DIR / "backlog" / "tasks")
    ))

    if not backlog_dir.exists():
        return {"is_stale": False, "reason": "No backlog directory found", "task_count": 0}

    try:
        task_count = len(list(backlog_dir.glob("task-*.md")))
        return {"is_stale": False, "reason": "OK", "task_count": task_count}
    except Exception as e:
        return {"is_stale": False, "reason": f"Check failed: {e}", "task_count": 0}


def generate_init_suggestion(memory_status: dict) -> str:
    """Generate a user-facing message about available memory systems."""
    if not memory_status["available"]:
        return ""
    systems = memory_status.get("systems", [])
    if not systems:
        return ""
    lines = [
        "",
        "**Memory System Available:**",
        f"- Connected systems: {', '.join(systems)}",
        "- Run `/memory` to initialize all memory sources",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    session_id = hook_input.get("session_id", datetime.now().strftime("%Y%m%d_%H%M%S"))

    os.environ["CLAUDE_SESSION_ID"] = session_id
    os.environ["CLAUDE_SESSION_START"] = datetime.now().isoformat()

    memory_status = check_memory_system()
    backlog_status = check_backlog_staleness()

    log_session_start(session_id, {
        "memory_available": memory_status["available"],
        "memory_systems": memory_status["systems"],
        "backlog_stale": backlog_status.get("is_stale", False),
    })

    response = {
        "decision": "continue",
        "metadata": {
            "session_id": session_id,
            "session_start": os.environ["CLAUDE_SESSION_START"],
            "memory_available": memory_status["available"],
        },
    }

    output_parts = []

    suggestion = generate_init_suggestion(memory_status)
    if suggestion:
        output_parts.append(suggestion)

    if backlog_status.get("is_stale"):
        output_parts.append(
            f"\n**Backlog needs sync:** {backlog_status.get('reason', 'Unknown')}\n"
            "- Run `/backlog-sync` to update\n"
        )

    if output_parts:
        response["outputToUser"] = "\n".join(output_parts)

    print(json.dumps(response))


if __name__ == "__main__":
    main()
