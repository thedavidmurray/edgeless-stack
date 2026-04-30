---
name: session-planning
description: >
  Structured session planning for complex multi-phase tasks. Creates plans
  that prevent goal drift over long sessions (50+ tool calls). Use for tasks
  with 3+ distinct phases, backlog items requiring coordinated execution,
  or research-heavy work.
metadata:
  tags: [planning, session, phases, goal-drift, attention, structured, multi-phase]
  tier: general
  domain: kernel
when_to_apply: >
  When a task has 3 or more distinct phases, involves complex multi-step work,
  or risks goal drift over a long session
---

# Session Planning Skill

## Overview

Create and manage structured session plans for complex multi-phase tasks. Based
on the "Attention Manipulation" pattern -- keeps goals visible even after 50+
tool calls to prevent goal drift.

## When to Use

- Task has 3 or more distinct phases
- Working on a backlog item needing structured execution
- Task requires research and documentation phases
- Project where goals might drift after 50+ tool calls
- User says "plan this out" or "let's structure this"

## Workflow

### Step 1: Create Plan

<!-- CUSTOMIZE: Set your session plan output directory -->
- Create plan file in your sessions directory (e.g., `sessions/YYYY-MM/`)
- Fill in frontmatter (task reference, total_phases, tags)
- Define goal (one sentence end state)
- Break into phases with checkboxes

### Step 2: During Session -- Attention Refresh

- A pre-decision hook reads the active plan before major tool calls
- Keeps goals visible even after 50+ tool calls
- Prevents goal drift

<!-- CUSTOMIZE: Wire up a hook that reads the active plan file
     before Write/Edit/Bash operations -->

### Step 3: Research Tracking -- 2-Action Rule

- After every 2 WebFetch/WebSearch/Read operations on external content
- Save findings to a research log (e.g., `knowledge/research-sessions/YYYY-MM-DD-topic.md`)
- Link back to session plan in frontmatter

### Step 4: Error Handling -- 3-Strike Protocol

- **Attempt 1**: Diagnose & Fix -- Read error, identify root cause, apply fix
- **Attempt 2**: Alternative Approach -- Try different method (never repeat same action)
- **Attempt 3**: Broader Rethink -- Question assumptions, search solutions
- **After 3 failures**: Escalate to user with explanation of all attempts

### Step 5: Session End -- Verify Completion

- Check for incomplete phases before ending
- Mark plan status as 'completed' when done
- Link to research sessions and task updates

## Frontmatter Schema

```yaml
---
created: 2026-01-16T10:30:00
session_id: abc123...
type: session_plan
status: in_progress         # or 'completed'
current_phase: 2
total_phases: 5
task_ref: "task-97"         # CUSTOMIZE: Your task reference format
research_sessions: []
tags: [kernel, automation]
---
```

## Template

```markdown
# Session Plan: [Task Title]

## Goal
[One sentence describing the end state]

## Phases

### Phase 1: [Name]
- [ ] Step 1
- [ ] Step 2

### Phase 2: [Name]
- [ ] Step 1
- [ ] Step 2

### Phase 3: [Name]
- [ ] Step 1
- [ ] Step 2

## Notes
[Running notes during execution]
```

## Integration Points

<!-- CUSTOMIZE: Adapt these to your project structure -->
- **Hooks**: Pre-decision (attention refresh), session-end (completion check)
- **Knowledge Base**: Session plans directory, research sessions directory
- **Backlog**: Bidirectional links between tasks and session plans
- **Memory**: Index session plans for retrieval in future sessions

## Anti-Patterns

- Don't create isolated task_plan.md files scattered in project root
- Don't store findings outside your research directory
- Don't duplicate progress tracking across multiple systems
- Don't break existing session file formats

## Related Skills

- `retrospective-learning` -- End-of-session learning extraction
- `verify-completion` -- Task completion verification
- `memory-system` -- Context persistence across sessions
