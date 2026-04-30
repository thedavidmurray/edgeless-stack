---
name: code-review
description: >
  Comprehensive code review for catching issues before they become problems.
  Use PROACTIVELY after writing significant code.
metadata:
  tags: [code-review, quality, bugs, security, proactive]
  tier: general
  domain: product
when_to_apply: >
  Proactively after writing a significant function, class, or module
  before telling the user it is done
---

# Code Review Skill

Comprehensive code review for catching bugs, security issues, and quality
problems before they reach production.

## When to Activate

**Proactive triggers** -- use automatically when:
- After writing a new function, class, or module
- After implementing a feature (before telling user "done")
- After refactoring existing code
- When making security-sensitive changes
- Before suggesting code is production-ready

**Do NOT use for:**
- Single-line fixes
- Comment/documentation changes only
- Trivial formatting changes

## Usage

```
/review [file_or_directory] [options]
```

**Options:**
- `--type <full|security|performance|quick>` -- Review focus (default: full)
- `--severity <critical|high|medium|low|all>` -- Minimum severity to report

## Review Dimensions

| Dimension | What's Checked |
|-----------|----------------|
| **Security** | Injection, auth bypass, secrets, input validation |
| **Performance** | N+1 queries, unnecessary loops, memory leaks |
| **Quality** | Code smells, duplication, complexity |
| **Correctness** | Logic errors, edge cases, error handling |
| **Style** | Consistency, naming, documentation |

## Review Types

### `quick` (1-2 min)
- Surface-level scan
- Obvious bugs and security issues
- Basic style violations

### `full` (3-5 min)
- Complete analysis across all dimensions
- Pattern detection
- Performance considerations

### `security` (2-3 min)
- OWASP Top 10 focused
- Input validation
- Authentication/authorization
- Secrets detection

### `performance` (2-3 min)
- Algorithm complexity
- Database query patterns
- Memory usage
- Caching opportunities

## Implementation

<!-- CUSTOMIZE: Choose your review approach.
     Options:
     - Manual checklist (simplest)
     - External LLM review via MCP (zen-mcp codereview, etc.)
     - Static analysis tools (ESLint, ruff, clippy)
     - Combination of the above
-->

Steps:
1. **Identify Scope** -- Determine files to review
2. **Run Static Analysis** -- Linting, type checking
3. **Deep Analysis** -- Pattern detection and security analysis
4. **Synthesis** -- Final recommendations and action items

## Output Format

```
Code Review: src/hooks/skill-activation.py

Summary:
- Lines reviewed: 206
- Issues found: 3
- Overall: NEEDS ATTENTION

Critical (0): None found
High (1): [details]
Medium (2): [details]
Low (0): None found

Positive Patterns: [what's done well]
Action Items: [prioritized fixes]
```

## Related Skills

- `test-driven-development` -- Write tests for issues found
- `cleanup` -- Remove dead code identified in review
- `verify-completion` -- Verify fixes after review
