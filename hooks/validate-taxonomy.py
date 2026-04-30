#!/usr/bin/env python3
"""
Validate Taxonomy -- PreToolUse Hook

Enforces directory taxonomy rules on file writes. Prevents writes to
deprecated or renamed directories and detects duplicate numbered folders.

Use cases:
  - Block writes to folders that have been renamed or archived
  - Enforce a canonical numbered-folder structure (00-Inbox, 01-Journal, etc.)
  - Run standalone with --check to audit the vault for violations

CUSTOMIZE: Edit VAULT_DIR, DEPRECATED_FOLDERS, and VALID_NUMBERED to match
your project's directory structure. Set VAULT_DIR env var to override.
"""

import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Configuration
# CUSTOMIZE: Point at your vault / content directory.
# ---------------------------------------------------------------------------
VAULT_DIR = os.environ.get(
    "VAULT_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vault"),
)

# CUSTOMIZE: Deprecated folder prefixes that should never receive new writes.
# Format: relative paths from VAULT_DIR root, with trailing slash.
DEPRECATED_FOLDERS = [
    # Example entries -- replace with your own:
    # "old-inbox/",       # Renamed to 00-Inbox/
    # "10-Reports/",      # Moved to 13-Reports/
]

# CUSTOMIZE: Valid numbered top-level folders.
# Keys are the two-digit prefix; values are the expected folder name.
VALID_NUMBERED = {
    "00": "00-Inbox",
    "01": "01-Journal",
    "02": "02-Agents",
    "03": "03-Knowledge",
    "04": "04-Sessions",
    "05": "05-Solutions",
    "06": "06-Config",
    "07": "07-Business",
    "08": "08-Reference",
    "09": "09-Secrets",
    "10": "10-Meta",
    "11": "11-Databases",
    "13": "13-Reports",
    "99": "99-Archive",
}

# CUSTOMIZE: Non-numbered top-level folders that are valid.
VALID_UNNUMBERED = ["_system", "Excalidraw"]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_for_duplicates():
    """Verify no duplicate numbered folders exist at the vault root."""
    if not os.path.isdir(VAULT_DIR):
        return []

    errors = []
    numbers_seen = {}
    for entry in os.listdir(VAULT_DIR):
        full = os.path.join(VAULT_DIR, entry)
        if not os.path.isdir(full):
            continue
        match = re.match(r"^(\d{2})-", entry)
        if match:
            num = match.group(1)
            if num in numbers_seen:
                errors.append(
                    f"DUPLICATE: {entry} and {numbers_seen[num]} both use number {num}"
                )
            numbers_seen[num] = entry

    return errors


def check_deprecated_path(file_path):
    """Check if a file path targets a deprecated folder."""
    errors = []
    rel = file_path.replace(VAULT_DIR + "/", "").replace(VAULT_DIR, "")
    for dep in DEPRECATED_FOLDERS:
        if rel.startswith(dep):
            errors.append(f"DEPRECATED: {dep} -- use the canonical location instead")
    return errors


def validate_write(file_path):
    """Validate a file write operation against taxonomy rules."""
    errors = []

    if VAULT_DIR not in file_path:
        return errors

    errors.extend(check_deprecated_path(file_path))
    errors.extend(check_for_duplicates())

    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Run as standalone check or as a PreToolUse hook."""

    # Standalone audit mode
    if "--check" in sys.argv:
        errors = check_for_duplicates()

        for dep in DEPRECATED_FOLDERS:
            dep_path = os.path.join(VAULT_DIR, dep)
            if os.path.exists(dep_path):
                count = sum(1 for _ in os.walk(dep_path) for _ in _[2])
                if count > 0:
                    errors.append(f"STALE: {dep} still exists with {count} files")

        if errors:
            print("Taxonomy validation FAILED:")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)
        else:
            print("Taxonomy validation PASSED")
            print(f"  {len(VALID_NUMBERED)} numbered folders, 0 collisions")
            print(f"  {len(VALID_UNNUMBERED)} unnumbered folders (system/plugin)")
            print(f"  {len(DEPRECATED_FOLDERS)} deprecated paths blocked")
            sys.exit(0)

    # Hook mode: read from stdin
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name not in ("Write", "Edit", "mcp__filesystem__write_file"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    if not file_path:
        sys.exit(0)

    errors = validate_write(file_path)
    if errors:
        result = {"decision": "block", "reason": f"Taxonomy violation: {'; '.join(errors)}"}
        print(json.dumps(result))
        sys.exit(0)


if __name__ == "__main__":
    main()
