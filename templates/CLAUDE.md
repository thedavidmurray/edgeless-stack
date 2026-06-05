# Claude Code Project Configuration

<!-- This is a starter CLAUDE.md template. Place it at your project root.
     Claude Code reads this file at the start of every session to understand
     your project's conventions, tools, and constraints.

     CUSTOMIZE: Replace all placeholder values with your actual configuration.
     Remove sections you don't need. Add sections specific to your project.
-->

## Project Identity

- **Name**: <!-- CUSTOMIZE: Your project name -->
- **Language**: <!-- CUSTOMIZE: Python, TypeScript, Rust, etc. -->
- **Description**: <!-- CUSTOMIZE: One-line description -->

## Memory System

<!-- CUSTOMIZE: Choose your memory approach.
     Options:
     - ChromaDB (semantic search)
     - Plain markdown files (simplest)
     - Claude Code built-in memory (~/.claude/projects/.../memory/)
     - Custom vector store
-->

**Initialize at session start:**
```bash
# CUSTOMIZE: Your memory init command
# python .claude/memory/session_initializer.py
```

## Key Commands

<!-- CUSTOMIZE: List the commands your agent should know about -->

```bash
# Run tests
# CUSTOMIZE: Your test command
pytest tests/ -v

# Lint
# CUSTOMIZE: Your lint command
ruff check .

# Build
# CUSTOMIZE: Your build command
# npm run build

# Type check
# CUSTOMIZE: Your type check command
# mypy src/
```

## Pre-commit Hooks

<!-- CUSTOMIZE: Describe your pre-commit setup.
     DO NOT bypass with --no-verify unless you're certain.
-->

The pre-commit hook runs smoke tests on changed files:
- **Compile check**: Catches syntax errors
- **Import check**: Validates entry points
- **Lint check**: Enforces code style

```bash
# Run smoke tests manually
# CUSTOMIZE: Your smoke test command
python scripts/preflight/smoke_test.py
```

## Skills

<!-- CUSTOMIZE: List your available skills.
     Skills are markdown instruction files that teach Claude domain-specific
     patterns and workflows. See skills/ directory.
-->

| Skill | Command | Purpose |
|-------|---------|---------|
| Memory | `/memory` | Initialize memory, search context |
| Plan | `/plan` | Create structured session plan |
| Verify | `/verify` | Evidence-first completion check |
| Review | `/review` | Code review |
| Retrospective | `/retrospective` | End-of-session learning |

## Hooks

<!-- CUSTOMIZE: List your active hooks.
     Hooks are scripts that run automatically at specific lifecycle points.
-->

| Hook | Trigger | Purpose |
|------|---------|---------|
| Pre-commit | `git commit` | Smoke tests |
| Session-end | Session close | Retrospective prompt |

## Anti-Patterns

<!-- These are common mistakes to avoid. Keep this section short and direct. -->

**ALWAYS check existing infrastructure before proposing new patterns.**

| Don't | Do Instead |
|-------|------------|
| Create files in random locations | Use canonical directories |
| Skip verification | Run `/verify` before declaring done |
| Build duplicate systems | Check what already exists |
| Bypass pre-commit hooks | Fix the underlying issue |

## Canonical Locations

<!-- CUSTOMIZE: Define your project's directory structure.
     This prevents files from being scattered randomly.
-->

| Category | Location |
|----------|----------|
| **Source code** | `src/` |
| **Tests** | `tests/` |
| **Configuration** | `config/` |
| **Documentation** | `docs/` |
| **Scripts** | `scripts/` |
| **Backlog** | `backlog/tasks/` |
| **Knowledge** | `knowledge/` |

## Completion Verification

**NEVER declare a task complete without verification.**

```bash
# CUSTOMIZE: Your verification command
python .claude/hooks/verify-completion.py --type task-XXX --verbose
```

## API Keys

<!-- CUSTOMIZE: Point to your env file. NEVER commit secrets. -->

- Consolidated at: `.env` (gitignored)
- Load: `from dotenv import load_dotenv; load_dotenv('.env')`

## JavaScript Dependency Management
- Use **pnpm** instead of npm or yarn wherever practical
- Configure pnpm with `minimumReleaseAge: 1440` (24-hour quarantine on new package versions)

## Environment

<!-- CUSTOMIZE: Your runtime environment details -->

- Python: <!-- version and path -->
- Node: <!-- version if applicable -->
- Package manager: pnpm (preferred) or pip

---
*Template from Edgeless Stack. Customize for your project.*
