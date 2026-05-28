---

name: understand-anything
description: >
  Use when analyzing, visualizing, or explaining codebases with
  Understand-Anything. Interactive knowledge graphs, architecture tours, diff
  impact, and semantic Q&A for any project.
metadata:
  tags: [codebase, analysis, visualization]
  tier: task-specific
  domain: knowledge
when_to_apply: >
  When analyzing, visualizing, or explaining a codebase with
  Understand-Anything.
---
# Understand-Anything for Hermes

## Overview

Understand-Anything turns any codebase into an interactive knowledge graph you can explore, search, and ask questions about. It works with Claude Code, Codex, Cursor, Copilot, Gemini CLI, and **Hermes**.

> "Graphs that teach > graphs that impress."

## When to Use

- Onboarding to an unfamiliar codebase — get the big picture without reading every file
- Architecture review — see layers, dependencies, and domain flows
- Pre-commit impact analysis — understand ripple effects before you commit
- Codebase documentation — generate plain-English summaries of every component
- Knowledge-base visualization — turn markdown wikis into force-directed graphs

## Installation

### One-line install (macOS / Linux)
```bash
curl -fsSL https://raw.githubusercontent.com/Lum1104/Understand-Anything/main/install.sh | bash -s hermes
```

### Manual install
```bash
git clone https://github.com/Lum1104/Understand-Anything.git ~/.understand-anything/repo
ln -sfn ~/.understand-anything/repo/understand-anything-plugin/skills ~/.hermes/skills/understand-anything
```

### Update
```bash
~/.understand-anything/repo/install.sh --update
```

## Commands

| Command | What it does | When to use |
|---|---|---|
| `/understand` | Analyze codebase and generate `knowledge-graph.json` | First run on any project |
| `/understand-dashboard` | Open interactive web dashboard | Explore visually |
| `/understand-chat <query>` | Ask natural-language questions about the code | "How does auth work?" |
| `/understand-diff` | Analyze impact of current uncommitted changes | Before committing |
| `/understand-explain <path>` | Deep-dive a specific file or function | Focus on one component |
| `/understand-onboard` | Generate onboarding guide for new devs | Team onboarding |
| `/understand-domain` | Extract business domain knowledge | Map code to business |
| `/understand-knowledge <path>` | Analyze a Karpathy-pattern LLM wiki | Wiki visualization |

## Workflow

### First-time analysis
```bash
/understand
```
Generates `.understand-anything/knowledge-graph.json`. This is the source of truth for all other commands.

### Daily usage
```bash
/understand-chat "How does the payment flow work?"
/understand-diff
/understand-dashboard
```

### Incremental updates
After code changes, re-run `/understand` to update the graph. Only changed files are re-analyzed.

### Auto-update on every commit
```bash
/understand --auto-update
```
Installs a post-commit hook.

## Graph Structure (for power users)

The knowledge graph JSON contains:
- `project` — metadata (name, description, languages, frameworks)
- `nodes[]` — files, functions, classes, modules, concepts, configs, services, etc.
- `edges[]` — imports, contains, calls, depends_on, configures, documents, deploys, triggers
- `layers[]` — architectural layers (API, Service, Data, UI, Utility)
- `tour[]` — auto-generated architecture walkthrough ordered by dependency

Node ID format: `file:path`, `function:path:name`, `class:path:name`, `config:path`

## Hermes-Specific Notes

- All 8 sub-skills are auto-discovered after installation: `understand`, `understand-chat`, `understand-dashboard`, `understand-diff`, `understand-domain`, `understand-explain`, `understand-knowledge`, `understand-onboard`
- Skills live under `~/.hermes/skills/understand-anything/` as symlinks to the upstream repo
- The graph file is project-local (`.understand-anything/knowledge-graph.json`), not global
- For monorepos, scope analysis: `/understand src/frontend`

## Links

- Repo: https://github.com/Lum1104/Understand-Anything
- Homepage: https://understand-anything.com/
- Demo: https://understand-anything.com/demo/
