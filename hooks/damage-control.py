#!/usr/bin/env python3
"""
Damage Control -- PreToolUse Hook

Blocks dangerous commands and protects critical paths BEFORE execution.
Reads block/protect rules from a companion patterns.yaml file.

Exit codes:
  0 - Allow the tool execution
  2 - Block the tool execution (returns error message to Claude)

Based on IndyDevDan's damage control patterns.
"""

import sys
import json
import re
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Pattern loading (simple YAML parser -- no pyyaml dependency)
# ---------------------------------------------------------------------------

def load_patterns():
    """Load patterns from patterns.yaml without pyyaml dependency."""
    patterns_path = Path(__file__).parent / "patterns.yaml"

    if not patterns_path.exists():
        return None

    content = patterns_path.read_text()

    patterns = {
        "dangerous_commands": {"bash": {"block_patterns": []}},
        "paths": {"zero_access": [], "read_only": [], "no_delete": []},
        "allowlist": [],
    }

    current_section = None
    current_subsection = None

    for line in content.split("\n"):
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if stripped == "dangerous_commands:":
            current_section = "dangerous_commands"
            current_subsection = None
        elif stripped == "paths:":
            current_section = "paths"
            current_subsection = None
        elif stripped == "allowlist:":
            current_section = "allowlist"
            current_subsection = None
        elif stripped == "bash:" and current_section == "dangerous_commands":
            current_subsection = "bash"
        elif stripped == "block_patterns:":
            current_subsection = "block_patterns"
        elif stripped == "zero_access:":
            current_subsection = "zero_access"
        elif stripped == "read_only:":
            current_subsection = "read_only"
        elif stripped == "no_delete:":
            current_subsection = "no_delete"
        elif stripped.startswith("- '") or stripped.startswith('- "'):
            match = re.match(r"-\s*['\"](.+?)['\"]", stripped)
            if match:
                value = match.group(1)
                if current_section == "dangerous_commands" and current_subsection == "block_patterns":
                    patterns["dangerous_commands"]["bash"]["block_patterns"].append(value)
                elif current_section == "paths":
                    if current_subsection in patterns["paths"]:
                        patterns["paths"][current_subsection].append(value)
                elif current_section == "allowlist":
                    patterns["allowlist"].append(value)

    return patterns


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def is_allowlisted(path, patterns):
    """Check if path is in allowlist."""
    for allowed in patterns.get("allowlist", []):
        if allowed in path:
            return True
    return False


def check_bash_command(command, patterns):
    """Check if bash command matches any dangerous pattern."""
    block_patterns = (
        patterns.get("dangerous_commands", {}).get("bash", {}).get("block_patterns", [])
    )

    for pattern in block_patterns:
        try:
            if re.search(pattern, command, re.IGNORECASE):
                return (
                    f"BLOCKED: Dangerous command pattern detected: '{pattern}'\n"
                    f"Command: {command[:100]}..."
                )
        except re.error:
            continue

    return None


def check_path_protection(path, tool_name, patterns):
    """Check if path violates any protection rules."""
    if path.startswith("~"):
        path = os.path.expanduser(path)

    if is_allowlisted(path, patterns):
        return None

    path_rules = patterns.get("paths", {})

    # Zero access -- block all operations
    for protected in path_rules.get("zero_access", []):
        if protected in path:
            return (
                f"BLOCKED: Path '{path}' is protected (zero_access)\n"
                f"Pattern matched: '{protected}'"
            )

    # Read only -- block Write and Edit
    if tool_name in ["Write", "Edit"]:
        for protected in path_rules.get("read_only", []):
            if protected.startswith("^"):
                try:
                    if re.search(protected, path):
                        return (
                            f"BLOCKED: Path '{path}' is read-only (regex match)\n"
                            f"Pattern matched: '{protected}'"
                        )
                except re.error:
                    continue
            elif protected in path:
                return (
                    f"BLOCKED: Path '{path}' is read-only\n"
                    f"Pattern matched: '{protected}'"
                )

    return None


def check_delete_protection(command, patterns):
    """Check if rm/delete command targets protected no_delete paths."""
    if not re.search(r"\brm\b", command):
        return None

    no_delete = patterns.get("paths", {}).get("no_delete", [])

    for protected in no_delete:
        if protected in command:
            if is_allowlisted(protected, patterns):
                continue
            return (
                f"BLOCKED: Cannot delete protected path\n"
                f"Path: '{protected}' is in no_delete protection"
            )

    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Main hook entry point."""
    try:
        hook_input = sys.stdin.read()
        hook_data = json.loads(hook_input)

        tool_name = hook_data.get("tool_name", "")
        tool_input = hook_data.get("tool_input", {})

        patterns = load_patterns()
        if not patterns:
            sys.exit(0)

        block_reason = None

        if tool_name == "Bash":
            command = tool_input.get("command", "")
            block_reason = check_bash_command(command, patterns)
            if not block_reason:
                block_reason = check_delete_protection(command, patterns)

        elif tool_name in ["Write", "Edit"]:
            file_path = tool_input.get("file_path", "")
            block_reason = check_path_protection(file_path, tool_name, patterns)

        elif tool_name == "Read":
            file_path = tool_input.get("file_path", "")
            path_rules = patterns.get("paths", {})
            for protected in path_rules.get("zero_access", []):
                if protected in file_path and not is_allowlisted(file_path, patterns):
                    block_reason = (
                        f"BLOCKED: Path '{file_path}' is protected (zero_access)\n"
                        f"Pattern matched: '{protected}'"
                    )
                    break

        if block_reason:
            print(block_reason, file=sys.stderr)
            sys.exit(2)

        sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse hook input: {e}", file=sys.stderr)
        sys.exit(0)  # Fail open
    except Exception as e:
        print(f"ERROR: Damage control hook failed: {e}", file=sys.stderr)
        sys.exit(0)  # Fail open


if __name__ == "__main__":
    main()
