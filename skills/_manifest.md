# Skill Manifest

Index of all included skills with applicability metadata.

**Total skills**: 9 | **Core**: 5 | **Domain**: 4

## Core Skills

Broadly useful in most sessions. Load these by default.

| Skill | Domain | When to Apply |
|-------|--------|---------------|
| `memory-system` | kernel | Session start, recalling past context, searching memory, checking health |
| `session-planning` | kernel | Task has 3+ phases, complex multi-step work, risk of goal drift |
| `verify-completion` | kernel | Before declaring any task complete; evidence-first, defaults to FAIL |
| `retrospective-learning` | kernel | End of session, after completing a feature, switching major tasks |
| `cleanup` | product | Codebase has dead code, unused imports, bloated dependencies |

**Location**: `skills/core/`

## Domain Skills

Load on demand for particular task types.

| Skill | Domain | When to Apply |
|-------|--------|---------------|
| `code-review` | product | After writing significant code, before declaring done |
| `research-deep` | knowledge | Complex topic requiring multi-step investigation and synthesis |
| `content-research-writer` | knowledge | Writing blog posts, articles, newsletters requiring research |
| `test-driven-development` | product | Implementing any feature or bugfix -- RED-GREEN-REFACTOR |

**Location**: `skills/domains/`

## Skill File Structure

Each skill is a single markdown file with YAML frontmatter:

```yaml
---
name: skill-name
description: >
  What this skill does and when to use it.
metadata:
  tags: [tag1, tag2]
  tier: general          # or task-specific
  domain: kernel         # kernel, product, knowledge, workflow
when_to_apply: >
  One-sentence trigger description
---
```

## Adding New Skills

1. Create `skills/<tier>/<skill-name>.md` with frontmatter
2. Add entry to this manifest
3. Include `<!-- CUSTOMIZE -->` comments for user-specific values
4. Keep the pattern: When to Use, Workflow, Implementation, Anti-Patterns, Related Skills

## Tiered Loading Pattern

To reduce context window usage, skills can be loaded on demand:

```bash
# Load all core skills (always relevant)
cat skills/core/*.md

# Load domain skills when needed
cat skills/domains/code-review.md
```

For large skill libraries (50+), implement a loader script that reads
the manifest and loads only relevant skills based on task domain.
