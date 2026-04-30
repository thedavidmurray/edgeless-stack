---
name: cleanup
description: >
  Removes dead code, unused dependencies, and performs codebase maintenance.
  Use when projects need pruning, dependencies are bloated, or dead code
  accumulates.
metadata:
  tags: [cleanup, dead-code, dependencies, maintenance, refactoring]
  tier: general
  domain: product
when_to_apply: >
  When a codebase has accumulated dead code, unused imports, or bloated
  dependencies that need pruning
---

# Cleanup Skill

## Overview

Remove dead code, unused dependencies, and perform codebase maintenance.
Keeps projects lean and healthy.

## Trigger

- **Command**: `/cleanup`
- **Keywords**: cleanup, clean, prune, remove unused, dead code, maintenance

## Cleanup Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    CLEANUP WORKFLOW                          │
├─────────────────────────────────────────────────────────────┤
│  1. Detect Project    ->  package.json, requirements.txt    │
│  2. Scan Dependencies ->  Find unused packages              │
│  3. Find Dead Code    ->  Unused exports, orphan files      │
│  4. Clear Caches      ->  node_modules/.cache, __pycache__  │
│  5. Generate Report   ->  Markdown summary                  │
│  6. Confirm & Execute ->  Remove with user approval         │
└─────────────────────────────────────────────────────────────┘
```

## Implementation

### Step 1: Project Detection

```bash
if [ -f "package.json" ]; then
    PROJECT_TYPE="node"
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    PROJECT_TYPE="python"
elif [ -f "Cargo.toml" ]; then
    PROJECT_TYPE="rust"
else
    PROJECT_TYPE="unknown"
fi
```

### Step 2: Dependency Analysis

**Node.js:**
```bash
npx depcheck --json > /tmp/depcheck-report.json
cat /tmp/depcheck-report.json | jq '.dependencies, .devDependencies'
```

**Python:**
```bash
pipreqs . --savepath /tmp/used-requirements.txt --force
diff requirements.txt /tmp/used-requirements.txt
```

### Step 3: Dead Code Detection

**JavaScript/TypeScript:**
```bash
npx ts-prune 2>/dev/null || echo "ts-prune not available"
npx unimported 2>/dev/null || echo "unimported not available"
```

**Python:**
```bash
autoflake --check --remove-all-unused-imports -r . 2>&1
```

### Step 4: Cache Cleanup

```bash
# Node.js caches
CACHE_DIRS=("node_modules/.cache" ".next/cache" ".nuxt" "dist" "build" ".turbo")

# Python caches
PYTHON_CACHE=("__pycache__" ".pytest_cache" ".mypy_cache" "*.pyc" ".coverage" "htmlcov")

du -sh ${CACHE_DIRS[@]} 2>/dev/null
```

### Step 5: Report Generation

```markdown
# Cleanup Report
Generated: $(date)
Project: $(basename $(pwd))

## Unused Dependencies
| Package | Type | Action |
|---------|------|--------|

## Dead Code
| File | Reason | Lines |
|------|--------|-------|

## Cache Cleanup
| Directory | Size | Status |
|-----------|------|--------|

## Estimated Savings
- Dependencies: ~N packages
- Dead code: ~N lines
- Cache: ~N MB disk space
```

## Safety Checks

Before ANY deletion:

1. **Git repository check** -- Warn if no git repo (changes cannot be reverted)
2. **Uncommitted changes check** -- Show changes and confirm
3. **Create backup list** -- Write files-to-delete list before acting

## Scopes

| Scope | What It Does |
|-------|--------------|
| `all` | Full cleanup (deps + code + cache) |
| `deps` | Only unused dependencies |
| `code` | Only dead code detection |
| `cache` | Only clear caches |
| `git` | Prune merged branches, gc |

## Options

| Option | Effect |
|--------|--------|
| `--dry-run` | Show what would happen, no changes |
| `--aggressive` | Include git cleanup, questionable items |
| `--report` | Generate report only, no deletions |
| `--force` | Skip confirmations (use with care) |

## Examples

```bash
/cleanup                    # Interactive full cleanup
/cleanup deps --dry-run     # Preview dependency cleanup
/cleanup cache              # Just clear caches
/cleanup all --report       # Full report, no deletions
/cleanup git --aggressive   # Prune branches, git gc
```

## Related Skills

- `code-review` -- Identify code quality issues
- `verify-completion` -- Verify cleanup was thorough
