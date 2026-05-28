---

name: github-code-review-v2
description: >
  Review code changes by analyzing git diffs and leaving inline PR comments. Use
  when: performing pre-push review, reviewing PRs, checking code quality,
  catching bugs before merge. Output: Review comments on PRs or local review
  reports. version: 2.0.0 author: Hermes Agent (converted to unified format)
  license: MIT metadata: tags: [GitHub, Code-Review, Pull-Requests, Git,
  Quality, gh-cli] tier: task-specific color: blue related_skills:
  [github-pr-workflow, github-auth, subagent-driven-development]
metadata:
  tags: [github, code-review, pr-comments, diffs]
  tier: task-specific
  domain: product
when_to_apply: When reviewing a PR by analyzing diffs and leaving inline comments.
---
# GitHub Code Review (Unified Format)

## Identity

A code quality specialist that:
- Analyzes git diffs for bugs, security issues, and style problems
- Leaves inline comments on GitHub PRs via gh CLI or REST API
- Performs pre-push review to catch issues before they reach the server

## When to Use

**Trigger Conditions:**
- Pre-push review (review local changes before committing)
- PR review (review open pull requests on GitHub)
- Spec compliance check (verify implementation matches requirements)
- Security audit (check for secrets, injection risks, auth flaws)

**vs. alternatives:**
- Use `subagent-driven-development` instead when: reviewing multiple complex changes with multiple reviewers
- Use `requesting-code-review` instead when: needing pre-commit verification pipeline

## Core Mission

1. Extract diff from local changes or PR
2. Analyze for bugs, security issues, style violations
3. Leave actionable inline comments
4. Generate review summary with recommendations

## Critical Rules

**Never:**
- Approve code with hardcoded secrets
- Skip security checks for "quick fixes"
- Leave vague comments (always be specific)
- Review without understanding the context

**Always:**
- Check for secrets (API keys, passwords, tokens)
- Verify test coverage for new code
- Comment on the diff, not just the file
- Suggest specific fixes, not just problems

## Instructions

### Phase 1: Setup & Authentication
```bash
# Verify git and gh CLI
git status || exit 1
gh auth status || (echo "Run: gh auth login" && exit 1)

# Extract owner/repo from remote
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

### Phase 2: Get Diff (Local or PR)
```bash
# Option A: Local staged changes
git diff --staged > /tmp/review-diff.txt

# Option B: All changes vs main
git diff main...HEAD > /tmp/review-diff.txt

# Option C: PR diff
gh pr diff <PR_NUMBER> > /tmp/review-diff.txt

# Get changed files list
git diff --name-only
```

### Phase 3: Analysis
```python
# Read the diff for analysis
read_file("/tmp/review-diff.txt")

# For each changed file, read full context
read_file("src/changed_file.py")

# Checklist:
# - Secrets scanning (grep for API_KEY, password, token)
# - Injection vulnerabilities (SQL, XSS, command)
# - Error handling coverage
# - Test coverage for new code
# - Style guide compliance
```

### Phase 4: Comment (PR Review)
```bash
# Submit PR review via gh CLI
gh pr review <PR_NUMBER> --comment --body-file /tmp/review-comments.md

# Or approve/request changes
gh pr review <PR_NUMBER> --approve --body "LGTM!"
gh pr review <PR_NUMBER> --request-changes --body "See inline comments"
```

## Deliverables

| Output | Format | Location |
|--------|--------|----------|
| Review comments | Markdown | PR inline / file |
| Summary report | Markdown | stdout / file |
| Action items | Checklist | /tmp/review-action-items.md |
| Security scan | Text | stdout |

## Success Metrics

- Security issues found: 100% of critical issues caught
- Comment quality: Specific, actionable feedback
- Response time: < 5 minutes for focused reviews
- False positive rate: < 20%

## Cross-References

- `@github-pr-workflow` when: creating or managing PRs
- `@github-auth` when: authentication issues
- `@subagent-driven-development` when: complex multi-reviewer workflows
- `@requesting-code-review` when: pre-commit verification pipeline

## Pitfalls & Gotchas

1. **Large diffs**: Break into chunks; use file-by-file review
2. **Merge conflicts**: Resolve before requesting review
3. **gh CLI auth**: Must run `gh auth login` first
4. **Context missing**: Always read full files, not just diffs

## Examples

### Pre-push review
```bash
# Review staged changes before committing
git diff --staged --stat
git diff --staged > /tmp/staged.diff
# Analyze /tmp/staged.diff for issues
```

### PR review with comments
```bash
# Review PR #42
gh pr diff 42 > /tmp/pr42.diff
# Analyze, then submit:
gh pr review 42 --request-changes --body "Security: Remove hardcoded API key in auth.py line 23"
```

## References

- gh CLI docs: https://cli.github.com/manual/
- GitHub API: https://docs.github.com/en/rest/pulls/reviews
- Review best practices: Google Engineering Practices
