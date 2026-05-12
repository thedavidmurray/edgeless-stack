---
name: commit-hygiene
description: Enforces quantitative commit size thresholds and best practices to reduce defect rates. Validates commit messages, detects oversized commits, and suggests splitting strategies.
metadata:
  tags:
  - git
  - commits
  - quality
  - code-review
  - defect-prevention
  tier: general
  domain: product
version: 1.0.0
category: engineering-discipline
created: 2026-01-16
author: djm
trigger_patterns:
- commit*
- git commit*
- ready to commit*
- check commit*
dependencies:
- Git repository
- CLAUDE.md for project conventions
references:
- references/splitting-strategies.md
- references/conventional-commits.md
integration:
- precommit-validation skill
- code-review skill
- Git pre-commit hooks
source: claude-bootstrap analysis (github.com/alinaqi/claude-bootstrap)
research: Defect correlation with commit/PR size
when_to_apply: Before every git commit to validate message quality and detect oversized commits that should be split
---
# Commit Hygiene - Quantitative Thresholds

## Overview

Enforce evidence-based commit size thresholds to reduce defect rates. Research shows:
- <200 lines: ~15% defect rate
- 200-400 lines: ~23% defect rate
- >400 lines: 40%+ defect rate

Review quality deteriorates significantly after 200-400 lines.

**Core principle:** Small, focused commits are easier to review and less likely to introduce bugs.

## When to Use

**PROACTIVE TRIGGERS** - Use automatically when:
- User says "commit", "ready to commit", or "push"
- Before running `/precommit`
- After completing a feature implementation
- Before creating a pull request

**Integration points:**
- Runs before `/precommit` validation
- Can be invoked standalone with `/commit-check`
- Integrates with git pre-commit hooks

## Quantitative Thresholds

| Metric | 🟢 Green | 🟡 Yellow | 🔴 Red |
|--------|---------|----------|--------|
| Files changed | ≤5 | 5-10 | >10 |
| Lines added | ≤150 | 150-300 | >300 |
| Lines deleted | ≤100 | 100-200 | >200 |
| Total changes | ≤250 | 250-400 | >400 |
| Commit categories | 1 | 2 | 3+ |

### Zone Meanings

**🟢 Green Zone (Optimal)**
- Ideal commit size
- Easy to review thoroughly
- Low defect probability (~15%)
- Fast code review cycle

**🟡 Yellow Zone (Acceptable)**
- Larger than ideal but manageable
- Consider splitting if possible
- Moderate defect probability (~23%)
- May slow review process

**🔴 Red Zone (High Risk)**
- Too large for effective review
- SHOULD be split into smaller commits
- High defect probability (40%+)
- Review quality deteriorates significantly

## Severity Levels

| Severity | Symbol | Action | Threshold |
|----------|--------|--------|-----------|
| Critical | 🔴 | BLOCK commit | Red zone + sensitive files |
| High | 🟠 | WARN strongly, suggest split | Red zone |
| Medium | 🟡 | WARN, allow with confirmation | Yellow zone |
| Low | 🟢 | Note size, allow | Green zone |
| Info | ℹ️ | Suggestion only | Any |

## Validation Checks

### 1. Size Analysis
```bash
# Get staged changes statistics
git diff --cached --stat
git diff --cached --shortstat

# Count files changed
git diff --cached --name-only | wc -l

# Count line changes
git diff --cached --numstat
```

### 2. Commit Message Validation

**Conventional Commits format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Required:**
- Type: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Subject: Imperative mood, <50 chars, no period
- Body: Wrap at 72 chars (if present)

**Red flags:**
- Subject contains "and" (likely doing multiple things)
- Vague subjects: "updates", "changes", "fixes"
- Missing type prefix
- Subject >50 characters

### 3. Sensitive File Detection

**BLOCK if staging:**
- `.env`, `.env.*`
- `*credentials*`, `*secrets*`, `*password*`
- `*.pem`, `*.key`, `*.p12`
- `config/production.*` (unless explicitly allowed)
- `*.db` (unless migration or test data)

**WARN if staging:**
- `TODO.md`, `FIXME.md` (temporary files)
- `debug.*`, `test-output.*`
- Large binary files (>1MB)

### 4. Category Detection

Detect if commit mixes multiple categories:
- **Features**: New functionality
- **Fixes**: Bug fixes
- **Refactoring**: Code restructure
- **Tests**: Test additions/changes
- **Docs**: Documentation
- **Style**: Formatting, whitespace
- **Chore**: Dependencies, config

**Red flag:** 3+ categories in one commit

## Implementation

### Basic Usage

```
/commit-check [options]
```

**Options:**
- `--strict` - Block on Yellow zone
- `--allow-large` - Skip size checks (use sparingly)
- `--suggest-split` - Show splitting suggestions for Red zone
- `--message <msg>` - Validate commit message format

### Workflow

1. **Analyze Staged Changes**
   ```bash
   git status
   git diff --cached --stat
   git diff --cached --shortstat
   git diff --cached --name-only
   ```

2. **Calculate Metrics**
   - Files changed
   - Lines added/deleted/modified
   - Categories affected
   - Sensitive files present

3. **Apply Thresholds**
   - Determine zone (Green/Yellow/Red)
   - Assign severity level
   - Check for blockers (secrets, etc.)

4. **Generate Report**
   ```
   Commit Hygiene Analysis

   Size Assessment: 🟡 YELLOW
   - Files changed: 7 (Yellow threshold)
   - Lines added: 245
   - Lines deleted: 78
   - Total changes: 323 (Yellow zone)

   Commit Message: ⚠️ NEEDS IMPROVEMENT
   - Missing conventional commit type
   - Subject contains "and" - likely multiple changes

   Categories Detected: 2 (Acceptable)
   - Features (4 files)
   - Tests (3 files)

   Sensitive Files: ✅ NONE

   Recommendation: 🟡 ACCEPTABLE WITH CAUTION
   - Consider splitting features and tests into separate commits
   - Update commit message to follow conventional commits format

   Suggested split:
   1. feat(api): add user authentication endpoint (4 files)
   2. test(api): add authentication tests (3 files)
   ```

5. **Provide Splitting Suggestions** (if Red zone)
   - See `references/splitting-strategies.md`

6. **Block or Warn**
   - Critical: Refuse to proceed
   - High: Warn strongly, require confirmation
   - Medium: Warn, suggest improvement
   - Low: Note and allow

## Splitting Strategies

When commits are too large, suggest splitting by:

### By Layer
```
1. feat(db): add user authentication schema
2. feat(api): add authentication endpoints
3. feat(frontend): add login UI
4. test(auth): add authentication tests
```

### By Feature Slice
```
1. feat(user): add user creation (CRUD - Create)
2. feat(user): add user retrieval (CRUD - Read)
3. feat(user): add user updates (CRUD - Update)
4. feat(user): add user deletion (CRUD - Delete)
```

### Refactor First
```
1. refactor(auth): extract validation logic
2. feat(auth): add OAuth support
```

### By Risk Level
```
1. refactor(db): safe schema migrations
2. feat(api): new endpoints (higher risk)
```

## Red Flags - AUTO-WARN

Trigger warnings when detecting:

- ❌ Subject contains "and", "also", "plus"
- ❌ Over 10 files changed
- ❌ Over 400 lines modified
- ❌ 3+ categories mixed (features + fixes + refactors)
- ❌ Sensitive files in staging area
- ❌ Vague commit message ("updates", "changes", "fixes stuff")
- ❌ Missing conventional commit type
- ❌ Subject >50 characters
- ❌ No body for complex changes (>200 lines)

## Auto-BLOCK Conditions

Never proceed when:

- 🚫 Secrets/credentials detected in diff
- 🚫 `.env` files staged (unless `.env.example`)
- 🚫 Private keys (`.pem`, `.key`, `*.p12`)
- 🚫 Database dumps in staging (unless explicitly migrations)
- 🚫 >1000 lines changed without explicit `--allow-large` flag

## Commit Message Templates

### Feature
```
feat(component): add brief description

- Detail 1
- Detail 2
- Detail 3

Closes #123
```

### Bug Fix
```
fix(component): brief description of bug fixed

Previous behavior: [what was broken]
New behavior: [what's fixed]
Root cause: [why it happened]

Fixes #456
```

### Refactoring
```
refactor(component): brief description

- Extracted helper functions
- Improved naming
- No behavior changes

No functional changes
```

### Breaking Change
```
feat(api)!: change authentication endpoint

BREAKING CHANGE: /auth/login moved to /api/v2/auth/login

Migration guide:
- Update client calls from /auth/login to /api/v2/auth/login
- Add API version header: X-API-Version: 2

Closes #789
```

## Integration with Existing Skills

### `/precommit` Integration
```
1. Run /commit-check first (size and message validation)
2. If Green/Yellow, proceed to /precommit (security, quality)
3. If Red, suggest splitting before running /precommit
```

### `/review` Integration
```
After code review, before commit:
1. /review identifies issues
2. Fix issues
3. /commit-check validates commit size
4. /precommit validates security/quality
5. git commit
```

### Git Hooks Integration

Can be called from `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Run commit hygiene check
python /path/to/commit-hygiene-checker.py

if [ $? -ne 0 ]; then
  echo "Commit hygiene check failed"
  exit 1
fi
```

## Output Format

### Green Zone Example
```
✅ Commit Hygiene: GREEN

Size Assessment: 🟢 OPTIMAL
- Files changed: 3
- Lines added: 87
- Lines deleted: 12
- Total changes: 99

Commit Message: ✅ VALID
- Type: feat
- Scope: auth
- Subject: add password reset endpoint

Categories: 1 (Ideal)
- Features only

Sensitive Files: ✅ NONE

READY TO COMMIT
```

### Yellow Zone Example
```
⚠️ Commit Hygiene: YELLOW

Size Assessment: 🟡 ACCEPTABLE
- Files changed: 8 (approaching limit)
- Lines added: 267
- Lines deleted: 145
- Total changes: 412 (Yellow zone)

Commit Message: ⚠️ NEEDS IMPROVEMENT
- Missing type prefix
- Subject: "update authentication and add tests"
- Contains "and" - likely doing multiple things

Categories: 2 (Acceptable)
- Features (5 files)
- Tests (3 files)

Sensitive Files: ✅ NONE

RECOMMENDATION: Consider splitting
- Suggested split: features vs. tests

Proceed? (yes/no/split)
```

### Red Zone Example
```
🛑 Commit Hygiene: RED

Size Assessment: 🔴 TOO LARGE
- Files changed: 15 (3x ideal limit)
- Lines added: 523
- Lines deleted: 287
- Total changes: 810 (Red zone - high defect risk)

Commit Message: ❌ INVALID
- No conventional commit type
- Subject >50 chars: "made a bunch of updates to the authentication system and fixed some bugs and refactored the database layer"
- Multiple "and" conjunctions

Categories: 4 (Too many)
- Features (6 files)
- Fixes (4 files)
- Refactoring (3 files)
- Tests (2 files)

Sensitive Files: 🚫 BLOCKER
- .env (contains secrets)
- config/database.yml (production credentials)

BLOCKING COMMIT

Issues:
1. 🚫 CRITICAL: Secrets detected (.env, credentials)
2. 🔴 HIGH: Commit too large (810 lines, 40%+ defect probability)
3. 🟠 MEDIUM: Mixing 4 categories (features, fixes, refactoring, tests)
4. ❌ Invalid commit message format

Required Actions:
1. Remove .env and config/database.yml from staging
2. Split into smaller commits (suggested: 6-8 commits)
3. Fix commit message format

Suggested Commit Split:
1. refactor(db): extract database connection logic (3 files, ~100 lines)
2. feat(auth): add OAuth provider support (4 files, ~200 lines)
3. fix(auth): correct session timeout handling (2 files, ~50 lines)
4. fix(db): resolve connection pool leak (2 files, ~80 lines)
5. test(auth): add OAuth tests (2 files, ~150 lines)
6. docs(auth): update authentication guide (2 files, ~30 lines)

Run with --suggest-split for detailed breakdown
```

## Configuration

Can be customized per-project in `.git/hooks/commit-hygiene.config`:

```yaml
thresholds:
  files:
    green: 5
    yellow: 10
    red: 15
  lines_added:
    green: 150
    yellow: 300
    red: 500
  total_changes:
    green: 250
    yellow: 400
    red: 600

blocking:
  secrets: true
  red_zone: false  # warn but don't block

message:
  require_conventional: true
  require_body_over: 200  # lines changed

sensitive_patterns:
  - "*.env"
  - "*credentials*"
  - "*.pem"
  - "*.key"
```

## Metrics Tracking

Track over time to measure improvement:
- Average commit size
- Percentage in each zone
- Defect rates by zone
- Time to review by zone

Store in `.git/hooks/commit-metrics.json`:
```json
{
  "commits": [
    {
      "hash": "abc123",
      "date": "2026-01-16",
      "files": 3,
      "lines_added": 87,
      "lines_deleted": 12,
      "zone": "green",
      "defects_found": 0
    }
  ],
  "summary": {
    "green": 73,
    "yellow": 22,
    "red": 5,
    "average_size": 145
  }
}
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "These changes are related" | Related ≠ atomic. Split by layer or feature slice. |
| "Splitting will create more work" | Smaller commits = faster reviews = less rework. |
| "I'll lose context if I split" | Good commit messages preserve context. |
| "Review will happen anyway" | Review quality degrades at 200-400 lines. |
| "This is a quick fix" | Quick fixes >400 lines aren't quick. |
| "Too late, already coded it" | Commit in logical chunks, not coding order. |
| "Git history will be messy" | Clean history = many small commits. |
| "Just this once" | Data shows 40%+ defect rate. Every time counts. |

## When NOT to Use

Skip commit-hygiene when:
- Initial repository setup (bulk imports)
- Merge commits (not user-created content)
- Auto-generated code (migrations, etc.) with `--allow-large`
- Explicitly approved large changes with sign-off

Otherwise, enforce thresholds.

## Best Practices

1. **Commit Early, Commit Often**
   - Don't wait until feature is "done"
   - Commit logical units as you go
   - Use branches for work-in-progress

2. **One Concern Per Commit**
   - Features separate from fixes
   - Refactoring separate from features
   - Tests can be with feature OR separate (choose one convention)

3. **Write Commit Message First**
   - If message is hard to write, commit does too much
   - Should be able to summarize in <50 chars
   - If you need "and", you need two commits

4. **Review Your Own Diff**
   - Before committing, review `git diff --cached`
   - Look for unrelated changes
   - Split if multiple concerns found

5. **Use Interactive Staging**
   ```bash
   git add -p  # stage hunks interactively
   git commit  # commit staged hunks
   ```

## Verification Checklist

Before marking commit as valid:

- [ ] Size in Green or Yellow zone
- [ ] Commit message follows conventional commits
- [ ] Single category or intentional 2-category mix
- [ ] No sensitive files detected
- [ ] No "and" in commit subject (unless absolutely necessary)
- [ ] Subject <50 characters
- [ ] Body wraps at 72 characters (if present)
- [ ] Body explains WHY for changes >100 lines
- [ ] Related tests included OR tests in separate commit
- [ ] No TODO/FIXME without issue reference
- [ ] No debug code (console.log, print statements)

Can't check all boxes? Re-evaluate commit scope.

## Related Skills

- `/precommit` - Pre-commit validation (security, quality)
- `/review` - Code review before committing
- `/learn` - Save commit patterns discovered
- `/test` - Run tests before commit

## References

- `references/splitting-strategies.md` - Detailed commit splitting patterns
- `references/conventional-commits.md` - Commit message format guide
- Source: https://github.com/alinaqi/claude-bootstrap
- Research: Defect correlation with commit/PR size

## Final Rule

```
Commits >400 lines = 40%+ defect probability
Green zone commits = 15% defect probability
Smaller commits = better reviews = fewer bugs
```

Keep commits small. Your reviewers (and future self) will thank you.

---

**Remember:** This is evidence-based defect prevention. The thresholds aren't arbitrary - they're derived from real defect rate data. When the tool says "Red zone", it means statistically high risk.
