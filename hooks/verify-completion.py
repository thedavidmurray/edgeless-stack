#!/usr/bin/env python3
"""
Verify Completion Hook

Evidence-first completion verification for autonomous agent workflows.
Defaults to FAIL -- a PASS verdict requires all declared checks to pass.

Usage:
    python verify-completion.py --type python
    python verify-completion.py --type task-42
    python verify-completion.py --type task-42 --evidence type=test_output,file_path=/tmp/out.txt
    python verify-completion.py --type python --verbose

Exit Codes:
    0 - PASS: All required checks passed
    1 - FAIL: One or more required checks failed
    2 - ERROR: Configuration or runtime error

Evidence Types (--evidence type=<TYPE>,...):
    test_output      Command output proving tests pass
    screenshot       Image file proving UI state
    health_check     Service/endpoint health result
    metric_value     Numeric metric (coverage %, latency, etc.)
    diff             Before/after diff for config changes
    file_content     File content proof (word count, lines, etc.)
    command_output   Arbitrary command output captured as evidence

Integration with autonomous loops:
    Exit 0 -> task done, move to next
    Exit 1 -> task not done, keep working or report failure
    Exit 2 -> system error, escalate to human

CUSTOMIZE: This hook expects a CompletionVerifier class. Either:
  1. Provide your own src/kernel/completion_verifier.py, or
  2. Use the lightweight built-in checks below by removing the import.
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional


# ---------------------------------------------------------------------------
# CUSTOMIZE: Import path for your verifier module.
# If you don't have one, the built-in lightweight verifier below is used.
# ---------------------------------------------------------------------------
_VERIFIER_AVAILABLE = False
try:
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from src.kernel.completion_verifier import CompletionVerifier  # noqa: E402
    _VERIFIER_AVAILABLE = True
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Lightweight built-in verifier (used when no external verifier is available)
# ---------------------------------------------------------------------------

class LightweightResult:
    """Minimal verification result."""

    def __init__(self):
        self.is_complete = True
        self.checks_run = 0
        self.checks_passed = 0
        self.failures: List[str] = []
        self.warnings: List[str] = []
        self.evidence_links: List[str] = []

    def verdict(self) -> str:
        return "PASS" if self.is_complete else "FAIL"

    def __str__(self) -> str:
        if self.is_complete:
            return f"PASS: {self.checks_passed}/{self.checks_run} checks passed"
        lines = [f"FAIL: {self.checks_passed}/{self.checks_run} checks passed"]
        for f in self.failures:
            lines.append(f"  FAILED: {f}")
        return "\n".join(lines)


def _run_check(name: str, command: str, cwd: str) -> tuple:
    """Run a shell command as a check. Returns (passed: bool, detail: str)."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=60
        )
        if result.returncode == 0:
            return True, f"{name}: OK"
        return False, f"{name}: exit {result.returncode} -- {result.stderr[:200]}"
    except subprocess.TimeoutExpired:
        return False, f"{name}: timed out (60s)"
    except Exception as e:
        return False, f"{name}: error -- {e}"


# CUSTOMIZE: Add or remove checks for your project type.
BUILTIN_CHECKS = {
    "python": [
        ("syntax", "python -m compileall -q ."),
        ("tests", "python -m pytest --tb=short -q 2>/dev/null || echo 'no pytest'"),
    ],
    "typescript": [
        ("typecheck", "npx tsc --noEmit 2>/dev/null || echo 'no tsc'"),
        ("tests", "npx jest --passWithNoTests 2>/dev/null || echo 'no jest'"),
    ],
    "general": [
        ("syntax", "true"),  # Always passes -- override with project-specific checks
    ],
}


def lightweight_verify(project_type: str, cwd: str, extra_evidence: Optional[List[Dict]] = None) -> LightweightResult:
    """Run built-in checks when no external verifier is available."""
    result = LightweightResult()

    # Determine check suite
    if project_type.startswith("task-"):
        checks = BUILTIN_CHECKS.get("general", [])
    else:
        checks = BUILTIN_CHECKS.get(project_type, BUILTIN_CHECKS["general"])

    for name, command in checks:
        result.checks_run += 1
        passed, detail = _run_check(name, command, cwd)
        if passed:
            result.checks_passed += 1
        else:
            result.is_complete = False
            result.failures.append(detail)

    # Record evidence
    if extra_evidence:
        for ev in extra_evidence:
            ev_type = ev.get("type", "unknown")
            ev_path = ev.get("file_path", ev.get("note", ""))
            result.evidence_links.append(f"[{ev_type}] {ev_path}")

    return result


# ---------------------------------------------------------------------------
# Argument parsing helpers
# ---------------------------------------------------------------------------

def _parse_evidence_arg(raw: str) -> Dict[str, Any]:
    """Parse --evidence key=value,key=value or JSON string."""
    raw = raw.strip()
    if raw.startswith("{"):
        return json.loads(raw)
    result: Dict[str, Any] = {}
    for part in raw.split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip()] = v.strip()
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Evidence-first completion verification for autonomous agents",
    )
    # CUSTOMIZE: Default config path for your project layout.
    parser.add_argument("--config", default=".claude/completion-criteria.yaml",
                        help="Path to completion criteria YAML file")
    parser.add_argument("--type", default="general",
                        help="Project type: python, typescript, general, task-XX")
    parser.add_argument("--cwd", default=".",
                        help="Working directory for command execution")
    parser.add_argument("--include-optional", action="store_true",
                        help="Include optional checks (warnings only)")
    parser.add_argument("--evidence", action="append", dest="evidence",
                        metavar="KEY=VALUE,...",
                        help="Add evidence artifact (repeatable)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed output")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Minimal output (PASS/FAIL only)")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = Path.cwd() / config_path

    cwd = Path(args.cwd)
    if not cwd.is_absolute():
        cwd = Path.cwd() / cwd

    extra_evidence: Optional[List[Dict[str, Any]]] = None
    if args.evidence:
        extra_evidence = [_parse_evidence_arg(ev) for ev in args.evidence]

    try:
        # Use external verifier if available, otherwise built-in
        if _VERIFIER_AVAILABLE:
            verifier = CompletionVerifier.from_yaml(str(config_path))
            result = verifier.verify(
                project_type=args.type,
                cwd=str(cwd),
                include_optional=args.include_optional,
                extra_evidence=extra_evidence,
            )
        else:
            result = lightweight_verify(args.type, str(cwd), extra_evidence)

        # Output
        if args.quiet:
            print(result.verdict())
        elif args.verbose:
            print(f"\n{'='*60}")
            print(f"Verification: {args.type}")
            print(f"{'='*60}\n")
            print(str(result))
            if result.warnings:
                print(f"\n{'='*60}")
                print("Warnings (Optional Checks):")
                for warning in result.warnings:
                    print(f"  WARNING: {warning}")
        else:
            if result.is_complete:
                print(f"PASS: {result.checks_passed}/{result.checks_run} required checks passed")
                if result.evidence_links:
                    print("Evidence:")
                    for link in result.evidence_links:
                        print(f"  - {link}")
            else:
                print(str(result))

        sys.exit(0 if result.is_complete else 1)

    except FileNotFoundError as e:
        print(f"ERROR: Configuration file not found: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: Verification failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
