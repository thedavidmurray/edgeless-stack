---
name: changelog-generator
description: >
  Generates user-facing changelogs from git history by parsing conventional commits,
  categorizing changes, and transforming technical messages into clear release notes.
  Invoke this skill when preparing a release, tagging a version, creating weekly update
  summaries, or maintaining a public CHANGELOG.md. Trigger phrases: "generate changelog",
  "create release notes", "what changed since", "summarize commits", "update changelog".
metadata:
  tags:
    - changelog
    - release-notes
    - git
    - versioning
    - conventional-commits
  version: "1.0.0"
when_to_apply: >
  When preparing release notes for a new version, summarizing changes for stakeholders,
  generating weekly/monthly update digests, or maintaining a public changelog file.
---

# Changelog Generator

Transform technical git commits into polished, user-friendly changelogs.

## Overview

This skill:
1. Reads git history for a given range (tag-to-tag, date-based, or commit SHA range)
2. Parses conventional commit prefixes to categorize each change
3. Rewrites technical commit messages into user-facing language
4. Filters out internal-only commits (tests, chores, CI) unless explicitly included
5. Renders output in Markdown, HTML, or JSON

---

## Invocation Syntax

```
/changelog                              # Since last git tag (or last 20 commits)
/changelog --since "2 weeks ago"        # Time-based range
/changelog v1.2.0..v1.3.0              # Between two tags or SHAs
/changelog --format html               # Output as HTML
/changelog --format json               # Output as JSON
/changelog --include-internal          # Include refactor/test/chore commits
/changelog --style brief               # One-liner per entry (default)
/changelog --style detailed            # Multi-sentence descriptions
/changelog --output CHANGELOG.md       # Write directly to file
```

---

## Step-by-Step Workflow

### Step 1 — Determine the commit range

Run these commands to establish the range:

```bash
# Preferred: since last annotated or lightweight tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null)

if [ -n "$LAST_TAG" ]; then
  echo "Generating changelog since tag: $LAST_TAG"
  RANGE="${LAST_TAG}..HEAD"
else
  echo "No tags found — using last 30 commits"
  RANGE=""
fi
```

For a date-based range:
```bash
# Replace <since> with any git-date string, e.g. "7 days ago", "2025-01-01"
SINCE="<since>"
RANGE="--since=\"${SINCE}\""
```

For an explicit version range:
```bash
# Replace <from> and <to> with tag names or commit SHAs
RANGE="<from>..<to>"
```

### Step 2 — Collect commits

```bash
# Collect commits with full message, author, and date
# --no-merges excludes plain merge commits
# Handle squash merges separately (see Step 3)
git log ${RANGE} \
  --no-merges \
  --pretty=format:"%H%x09%s%x09%an%x09%ad" \
  --date=short
```

To also capture merge commit subjects (useful for squash-merge workflows):
```bash
git log ${RANGE} \
  --merges \
  --pretty=format:"%H%x09%s%x09%an%x09%ad" \
  --date=short
```

### Step 3 — Parse and categorize each commit

Use the following prefix map to assign every commit to a category.

#### Conventional Commit Prefix Map

| Prefix(es) | Output Category | User-Facing? |
|---|---|---|
| `feat`, `feature` | New Features | Yes |
| `fix`, `bugfix`, `hotfix` | Bug Fixes | Yes |
| `perf` | Performance | Yes |
| `docs` | Documentation | Yes (if user-docs) |
| `security` | Security | Yes |
| `deprecate`, `deprecated` | Deprecations | Yes |
| `BREAKING CHANGE`, `!` suffix | Breaking Changes | Yes (always shown) |
| `refactor` | Internal | No (filtered by default) |
| `test`, `tests` | Internal | No (filtered by default) |
| `chore`, `build`, `ci`, `cd` | Internal | No (filtered by default) |
| `style`, `format` | Internal | No (filtered by default) |
| `revert` | Reverts | Yes (show with caution) |
| *(no prefix / unknown)* | Other Changes | Yes |

#### Scope extraction

If the commit includes a scope — e.g. `feat(auth): ...` — extract and use it as a label:
- `feat(api): add rate limiting` → category **New Features**, label **API**
- `fix(dashboard): correct chart colours` → category **Bug Fixes**, label **Dashboard**

#### Breaking change detection

A commit is a breaking change if any of the following are true:
- Subject starts with `BREAKING CHANGE:` or `BREAKING:`
- Subject type ends with `!` (e.g. `feat!:`, `fix(api)!:`)
- Commit body contains a `BREAKING CHANGE:` footer

Breaking changes MUST always appear in output regardless of `--include-internal`.

### Step 4 — Transform to user-facing language

For every user-facing commit, rewrite the message following these rules:

1. **Remove the conventional prefix** — strip `feat:`, `fix(scope):`, etc.
2. **Capitalise the first word**
3. **Reframe around user benefit**, not implementation detail
4. **Expand abbreviations** — `auth` → authentication, `UI` → interface, `DB` → database
5. **Keep it concise** — aim for one clear sentence in `--style brief` (default)
6. **Add a second sentence** in `--style detailed` explaining the benefit or context

**Rewrite examples:**

| Raw commit | Rewritten entry |
|---|---|
| `feat(auth): implement OAuth2 PKCE flow for mobile` | **OAuth Login** — Added secure sign-in support for mobile apps |
| `fix: prevent crash when file list is empty` | Fixed a crash that occurred when the file list was empty |
| `perf(sync): batch writes to reduce round-trips` | Sync is now significantly faster due to batched writes |
| `feat!: remove legacy /v1/users endpoint` | **[Breaking]** Removed the legacy `/v1/users` API endpoint — migrate to `/v2/users` |
| `fix(dashboard): chart colours wrong in dark mode` | Fixed chart colours in dark mode |

### Step 5 — Group and order entries

Order categories in output as follows (omit empty categories):

1. Breaking Changes
2. New Features
3. Bug Fixes
4. Performance
5. Security
6. Documentation
7. Deprecations
8. Reverts
9. Other Changes

Within each category, list entries in reverse-chronological order (newest first).

### Step 6 — Render output

#### Markdown (default)

```markdown
# Changelog — v<VERSION> / <DATE>

## Breaking Changes

- **[Breaking]** Description of breaking change

## New Features

- **Feature Label**: Description of what users can now do
- Description of another new capability

## Bug Fixes

- Fixed issue where X caused Y
- Resolved problem with Z under certain conditions

## Performance

- Operation X is now N× faster

## Security

- Patched vulnerability in authentication flow

## Deprecations

- `/v1/old-endpoint` is deprecated and will be removed in v3.0
```

#### HTML

Wrap the same structure in semantic HTML:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Changelog — v<VERSION></title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; color: #1a1a1a; }
    h1 { border-bottom: 2px solid #e5e5e5; padding-bottom: 0.5rem; }
    h2 { margin-top: 2rem; color: #2d2d2d; }
    ul { padding-left: 1.5rem; }
    li { margin-bottom: 0.4rem; line-height: 1.6; }
    .breaking { color: #c0392b; font-weight: bold; }
    .label { font-weight: 600; }
  </style>
</head>
<body>
  <h1>Changelog &mdash; v<VERSION></h1>
  <h2>Breaking Changes</h2>
  <ul>
    <li><span class="breaking">[Breaking]</span> Description</li>
  </ul>
  <h2>New Features</h2>
  <ul>
    <li><span class="label">Feature Label:</span> Description</li>
  </ul>
  <!-- ... remaining categories ... -->
</body>
</html>
```

#### JSON

```json
{
  "version": "<VERSION>",
  "date": "<YYYY-MM-DD>",
  "range": "<from>..<to>",
  "categories": {
    "breaking_changes": [
      {
        "hash": "abc1234",
        "raw": "feat!: remove legacy endpoint",
        "rewritten": "Removed the legacy /v1/users endpoint",
        "scope": null,
        "author": "Jane Smith",
        "date": "2025-06-01"
      }
    ],
    "new_features": [],
    "bug_fixes": [],
    "performance": [],
    "security": [],
    "documentation": [],
    "deprecations": [],
    "reverts": [],
    "other": []
  }
}
```

---

## Handling Special Cases

### Squash merges

Many teams squash-merge feature branches. The merge commit subject often contains the PR title. Treat the merge commit subject as the changelog entry, applying the same categorisation rules. If the subject lacks a conventional prefix, place it in **Other Changes**.

### Monorepo / multiple packages

If the repo uses scopes that map to packages (e.g. `feat(api):`, `fix(web):`), group entries by scope within each category, or add a `--scope <name>` filter to include only one package.

### Non-conventional commits

If commits do not follow conventional commit format, attempt a best-effort categorisation:
- Subject starts with "Add" / "Implement" / "Introduce" → **New Features**
- Subject starts with "Fix" / "Resolve" / "Correct" → **Bug Fixes**
- Subject starts with "Improve" / "Optimise" / "Speed" → **Performance**
- Subject starts with "Update docs" / "Document" → **Documentation**
- All others → **Other Changes**

---

## Configuration File (Optional)

Projects can place a `.changelog.yml` at the repository root to override defaults:

```yaml
# .changelog.yml
version_prefix: "v"          # Prefix stripped when displaying version names
output_file: "CHANGELOG.md"  # Default output path when --output is used
default_format: "markdown"   # markdown | html | json
default_style: "brief"       # brief | detailed
include_internal: false       # Show refactor/test/chore commits
include_scopes_as_labels: true

# Custom category overrides
categories:
  - id: new_features
    emoji: "✨"
    heading: "New Features"
  - id: bug_fixes
    emoji: "🐛"
    heading: "Bug Fixes"
  - id: performance
    emoji: "⚡"
    heading: "Performance"
  - id: security
    emoji: "🔒"
    heading: "Security"
  - id: breaking_changes
    emoji: "💥"
    heading: "Breaking Changes"
  - id: deprecations
    emoji: "⚠️"
    heading: "Deprecations"
  - id: documentation
    emoji: "📖"
    heading: "Documentation"

# Terms to expand in commit messages
expansions:
  auth: authentication
  UI: interface
  DB: database
  API: API
  perf: performance
  cfg: configuration
```

---

## CI/CD Integration

### GitHub Actions — auto-generate release notes on tag push

```yaml
name: Release Changelog
on:
  push:
    tags:
      - 'v*'

jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0          # Full history needed for tag comparison
      - name: Generate changelog
        run: |
          # Collect commits since the previous tag
          PREV_TAG=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || git rev-list --max-parents=0 HEAD)
          CURRENT_TAG=${GITHUB_REF#refs/tags/}
          git log "${PREV_TAG}..HEAD" --no-merges \
            --pretty=format:"- %s (%an)" > release-notes.txt
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          body_path: release-notes.txt
```

### Pre-release checklist

```bash
# Before tagging a release:
# 1. Generate and review the changelog
/changelog --style detailed

# 2. Write to CHANGELOG.md
/changelog --output CHANGELOG.md

# 3. Commit and tag
git add CHANGELOG.md
git commit -m "docs: update changelog for v2.5.0"
git tag -a v2.5.0 -m "Release v2.5.0"
```

---

## Output Quality Guidelines

- **One entry per logical change** — if multiple commits describe the same change (e.g. fix + follow-up), merge them into one entry
- **User perspective first** — "You can now..." not "We added..."
- **Avoid jargon** — write for users, not contributors
- **No internal ticket numbers** in user-facing sections (acceptable in JSON `hash` field)
- **Breaking changes always include migration guidance** when available
- **Review before publishing** — generated output is a first draft; always read through before shipping

---

## Related Skills

- `dev-docs` — Generate API reference and other technical documentation
- `commit-hygiene` — Lint and standardise commit messages before they reach the changelog
- `code-review` — Review changes that will appear in the next changelog
