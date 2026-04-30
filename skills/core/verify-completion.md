---
name: verify-completion
description: >
  Evidence-first task completion verification. Run BEFORE declaring any task
  complete. Defaults to FAIL -- a PASS verdict requires proof. Returns PASS
  or FAIL with evidence links.
metadata:
  tags: [verification, completion, evidence, testing, quality, proof]
  tier: general
  domain: kernel
when_to_apply: >
  Before declaring any task complete; evidence-first check that defaults to FAIL
---

# Verify Completion Skill

Evidence-first task completion verification for autonomous agents. Verdict
defaults to FAIL. A PASS is only issued when ALL required checks pass AND
any declared evidence artifacts are present.

## Agent Self-Check Protocol

**Every agent MUST verify completion before declaring done:**

```
Before telling the user a task is done:
1. Run: /verify [task-type]
2. Verdict defaults to FAIL -- do not assume PASS
3. If FAIL, continue working on failed checks
4. Only declare COMPLETE if verification returns PASS (exit code 0)
```

## When to Use

**Mandatory triggers** -- always verify before:
- Declaring a task complete
- Telling the user "I'm done" or "Task completed"
- Moving to the next task in a sequence
- Ending a loop iteration

**Skip verification only for:**
- Informational queries (no code changes)
- Research/exploration tasks
- User explicitly says "skip verification"

## Usage

```bash
# CUSTOMIZE: Point to your verification script
python .claude/hooks/verify-completion.py --type task-150 --verbose

# Verify against project type criteria
/verify python
/verify typescript

# With explicit evidence
/verify task-150 --evidence type=test_output,file_path=/tmp/out.txt
```

## How It Works

1. **Verdict defaults to FAIL** -- never assumed, must be proven.

2. **Task-Specific Criteria** (`task-XXX`):
   - Looks for task file in backlog
   - Parses `completion_criteria` from YAML frontmatter
   - Runs all required checks

3. **Project-Type Criteria** (`python`, `typescript`, etc.):
   - Reads from completion criteria config
   - Runs standard checks (tests, linting, type checking)

4. **Evidence Collection**:
   - Each passing check may produce an evidence link
   - Caller can inject additional evidence via `--evidence`
   - All evidence links appear in the PASS verdict output

## Verification Output

```
PASS: All 5/5 required checks passed
Evidence:
  - [test_output] /tmp/pytest-out.txt
  - [file_content] src/my_feature.py
```

or

```
FAIL: 2 check(s) failed:
  - All tests pass: Command failed with exit code 1
  - No linting errors: Command failed with exit code 1
```

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | PASS | Safe to declare task done |
| 1 | FAIL | Continue working, fix failures |
| 2 | ERROR | Configuration/runtime error, investigate |

## Evidence Types

| Type | Value | Use For |
|------|-------|---------|
| Test output | `test_output` | Command output proving tests pass |
| Screenshot | `screenshot` | Image file proving UI state |
| Health check | `health_check` | Service/endpoint health result |
| Metric value | `metric_value` | Numeric metric (coverage %, latency) |
| Diff | `diff` | Before/after diff for config changes |
| File content | `file_content` | File exists + content proof |
| Command output | `command_output` | Arbitrary command output |

## Task Completion Checklist Format

Add this to task file YAML frontmatter:

```yaml
---
completion_criteria:
  required:
    - command: "pytest tests/test_my_feature.py -v"
      description: "Feature tests pass"
      timeout: 120

    - file_exists: "src/my_feature.py"
      description: "Implementation exists"

    - command: "ruff check src/my_feature.py"
      description: "No linting errors"

  optional:
    - command: "mypy src/my_feature.py"
      description: "Type checking passes"
---
```

## Check Types

| Type | Syntax | Purpose |
|------|--------|---------|
| `command` | `command: "pytest"` | Run command, check exit code 0 |
| `file_exists` | `file_exists: "path"` | Verify file exists |
| `file_absent` | `file_absent: "path"` | Verify file does NOT exist |
| `output_match` | `output_match: "regex"` | Command output matches pattern |
| `output_absent` | `output_absent: "regex"` | Command output does NOT match |

## Anti-Patterns

**Don't:**
- Declare complete without running verification
- Ignore FAIL status and declare done anyway
- Skip verification because "it's a small change"
- Trust that tests passed without actually running them
- Assume PASS -- the system defaults to FAIL

**Do:**
- Always verify before completing
- Supply at least one evidence artifact per task
- Fix all failed checks before declaring done
- Re-run verification after fixes

## Related Skills

- `test-driven-development` -- Write tests that feed verification
- `code-review` -- Review code quality (complementary)
- `session-planning` -- Plans reference verification at phase end
