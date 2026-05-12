---
name: precommit-validation
description: Comprehensive pre-commit validation using zen-mcp's precommit and security audit tools. Run PROACTIVELY before any git commit to catch issues early.
metadata:
  tags:
  - pre-commit
  - validation
  - security
  - quality
  - git
  tier: task-specific
  domain: product
when_to_apply: Before any git commit or push to catch security issues and code quality problems early
---
# Pre-Commit Validation Skill

Pre-commit validation using zen-mcp's precommit and security audit tools.

## When to Activate

**PROACTIVE TRIGGERS** - Use automatically when:
- User says "commit", "push", "deploy", or "ship it"
- After completing a feature implementation
- After fixing bugs (verify fix doesn't introduce new issues)
- Before creating a pull request

## Usage

```
/precommit [options]
```

**Options:**
- `--security` - Focus on security vulnerabilities
- `--quick` - Fast check (staged files only)
- `--thorough` - Deep analysis with expert validation

## Implementation

### Pre-Commit Workflow

1. **Gather Git State** - Check what's changing:
```bash
git status
git diff --cached --stat
git diff --stat
```

2. **Run Pre-Commit Analysis** - Use zen-mcp precommit:
```
mcp__zen__precommit(
    step="Analyzing staged and unstaged changes",
    step_number=1,
    total_steps=3,
    next_step_required=true,
    findings="Initial analysis...",
    model="o3",
    include_staged=true,
    include_unstaged=true,
    thinking_mode="high"
)
```

3. **Security Scan** (if --security or significant changes):
```
mcp__zen__secaudit(
    step="Security review of changed files",
    step_number=1,
    total_steps=2,
    findings="Security analysis...",
    model="o3",
    audit_focus="comprehensive"
)
```

4. **Quality Check**:
```
mcp__zen__codereview(
    step="Code quality review of changes",
    step_number=1,
    total_steps=2,
    findings="Quality assessment...",
    model="gemini-2.5-flash",
    review_type="quick"
)
```

## Checklist Verified

- [ ] No secrets/credentials in diff
- [ ] No debug code (console.log, print statements)
- [ ] Error handling present
- [ ] Input validation for user data
- [ ] Tests exist for new functionality
- [ ] No TODO/FIXME left unaddressed

## Output Format

```
Pre-Commit Analysis

Changes Detected:
- Modified: 3 files
- Added: 1 file
- Staged: 2 files

Security Check: PASS
- No secrets detected
- No obvious vulnerabilities
- Input validation present

Quality Check: WARNINGS
- Missing docstring in new_function()
- Consider error handling in line 45

Test Status:
- Related tests: Found
- Recommendation: Run tests before commit

READY TO COMMIT
   or
ISSUES FOUND - Address before committing
```

## Related Skills

- `/review` - Deep code review (post-implementation)
- `/learn` - Save important patterns discovered
- `/test` - Run tests before commit
- `mcp__zen__secaudit` - Full security audit

## Command Reference

Corresponds to `/precommit` command.
