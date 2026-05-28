---
name: agent-fleet-capability-audit
description: >
  Survey available skills/tools across Hermes categories, audit subscription vs
  local capabilities, document agent-to-skill mappings, and assign specific
  tasks to appropriate agents with Discord notifications. Interactive fleet
  capability management and targeted delegation workflow.
metadata:
  tags: [agent-fleet, audit, capabilities, skills]
  tier: task-specific
  domain: tooling
when_to_apply: >
  When surveying available skills/tools across an agent fleet and auditing
  capability gaps.
---
# Agent Fleet Capability Audit & Delegation

> **Purpose**: Survey → Document → Assign → Notify
> **Interactive workflow** for deliberate fleet capability management, not automated gap detection.

## Prerequisites

This skill **requires the Hermes Agent runtime**. It scans `$HERMES_HOME/skills/` and agent profiles to survey available capabilities; it is not useful outside that environment. Set `HERMES_HOME` (defaults to `~/.hermes`) before running.

## When to Use

**Trigger Conditions:**
- "What skills/tools do we have available?"
- "Audit agent capabilities"
- "Map tools to agents"
- "Which agent should handle [task]?"
- "Survey available integrations"
- "Document what [subscription] gives us"
- "Assign [specific work] to [agent type]"

**NOT for:**
- Automated skill gap detection (use `cron-skill-review`)
- Self-improving optimization (use `agent-optimization-infrastructure`)
- Fleet health monitoring (use `paperclip-fleet-analyzer`)

**Use this when:** You need a deliberate, interactive audit of capabilities followed by immediate task assignment.

## Workflow Overview

```
1. SURVEY    → skills_list per category, skill_view on relevant ones
2. CATALOG   → subscription vs local, API keys vs managed, agent affinity
3. DOCUMENT  → workflow guides + skill-to-agent mapping in vault
4. ASSIGN    → Paperclip issue with assigneeAgentId + priority
5. NOTIFY    → backroom (structured tags) + general (human visibility)
```

## Step 1: Survey Skills Inventory

### List Skills by Category

```python
from hermes_tools import skills_list

categories = ["nous", "creative", "mlops", "devops",
              "software-development", "media", "productivity", "research"]

for cat in categories:
    skills = skills_list(category=cat)
    print(f"{cat}: {skills.count} skills")
```

### View Specific Skills

```python
skill_view(name="<skill-name>")
# → description, triggers, required_env, linked_files
```

Key fields: `triggers`, `required_environment_variables`, `required_commands`, `linked_files`.

## Step 2: Catalog Capabilities

### Subscription vs Local Matrix

Build a matrix per category distinguishing subscription-included tools (e.g. image gen, web extract, browser automation, TTS via your gateway) from local/open alternatives (Stable Diffusion, Playwright, whisper) and the setup each requires.

### Agent-to-Skill Affinity Mapping

For each agent in your fleet, list **primary** skills (matches role) and **secondary** skills (supporting). Derive from each agent's role/title:

```
<AgentName> (<Role>):
  Primary:   <skill-1>, <skill-2>
  Secondary: <skill-3>, <skill-4>
```

## Step 3: Document Workflows

### Tool Workflow Guide

For subscription tools or complex local tools, create a dedicated workflow doc at `<vault>/Workflows/{tool}-workflow.md`:

```yaml
---
title: {Tool} Workflow Guide
date: {YYYY-MM-DD}
type: workflow
subscription: {yes/no}
cost: {description}
---

# {Tool} Usage Guide

## When to Use
## When NOT to Use
## Tool Reference   (function | purpose | example)
## Agent Mapping    (agent | use case)
## Workflow Patterns
```

### Skill-to-Agent Mapping

At `<vault>/Workflows/hermes-skills-agent-mapping.md`: table of all skills by category, agent profiles with primary/secondary skills, workflow triggers (which skill fires on what input), dependency graph (skill A → skill B chains).

## Step 4: Assign Work

```python
def select_agent_for_task(task_description, keywords_to_agents, default):
    task_lower = task_description.lower()
    for keywords, agent in keywords_to_agents.items():
        if any(k in task_lower for k in keywords):
            return agent
    return default
```

Populate `keywords_to_agents` from your own fleet's role definitions.

### Create Paperclip Issue

```python
import subprocess, json

API_BASE = "http://127.0.0.1:3100/api"
COMPANY_ID = "{your-company-id}"
AGENT_IDS = {"<AgentName>": "<agent-uuid>"}

def assign_to_agent(task_title, task_description, agent_name, priority="medium"):
    payload = {
        "title": task_title,
        "description": task_description,
        "priority": priority,
        "status": "in_progress",
        "assigneeAgentId": AGENT_IDS[agent_name],
    }
    r = subprocess.run(
        ["curl", "-s", "-X", "POST",
         f"{API_BASE}/companies/{COMPANY_ID}/issues",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True,
    )
    return json.loads(r.stdout).get("identifier")
```

## Step 5: Notify

### Bot-Backroom (Agent Coordination)

Structured message with anti-loop protocol tags:

```
`[{timestamp}]` **[FROM:{coordinator}]** **[TO:{AGENT}]** [TYPE:ASSIGNED] [REF:{issue_id}]
ETA: {eta}

{task_summary}
```

### General (Human Visibility)

Short kickoff line: title, issue id, assigned agent, ETA.

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Tool Workflow Guide | `<vault>/Workflows/{tool}-workflow.md` | When/how to use specific tools |
| Skill-Agent Mapping | `<vault>/Workflows/hermes-skills-agent-mapping.md` | Reference for delegation decisions |
| Paperclip Issue | `<PREFIX>-XXX` | Tracked work assignment |
| Backroom message | bot-coordination channel | Agent coordination (structured tags) |
| General message | human-visibility channel | Active work announcements |

## Integration with Other Skills

| Skill | Relationship |
|-------|--------------|
| `cron-skill-review` | Complements automated gap detection with manual audits |
| `agent-optimization-infrastructure` | Consumes assignment telemetry for delegation optimization |
| `paperclip-fleet-analyzer` | Uses assignment data for fleet health reports |
| `paperclip-api` | Underlying API for issue creation/assignment |
| `discord-swarm-handoff-protocol` | Structured messaging format for notifications |

## Common Patterns

### Pattern A: New Tool Discovery
1. `skills_list` all categories → does the skill exist?
2. `skill_view` → check requirements, triggers
3. Document in workflow guide if complex
4. Map to appropriate agent(s)
5. Create test issue if needed

### Pattern B: Complex Multi-Step Assignment
1. Survey all required skills
2. Identify primary vs supporting agents
3. Create parent issue with sub-tasks
4. Assign sub-tasks to respective agents
5. Post coordination messages linking dependencies

### Pattern C: Subscription Audit
1. List skills in subscription category
2. Catalog subscription vs local capabilities
3. Create subscription workflow guide
4. Update agent mappings for new tools
5. Notify agents of new capabilities

## Pitfalls & Solutions

| Pitfall | Solution |
|---------|----------|
| Agent not responding | Check if agent has `reportsTo` set; escalate to boss |
| Skill requires setup | Document setup steps in workflow guide before assigning |
| Subscription tool expired | Check auth status first; fallback to local alternatives |
| Unclear which agent | Use keyword matching; default to a generic implementation agent |
| Issue creation fails | Verify `assigneeAgentId` present; check Paperclip API response |
| Rate limits | Use structured tags instead of @mentions; post once per channel |

## Skill Allocation & Redundancy Design

When designing optimal agent-skill mappings (not just auditing existing ones):

### Token Budget Per Agent Role

| Agent Role | Token Budget | Rationale |
|------------|--------------|-----------|
| Coordinator | 8-12k | Fast routing, minimal context |
| Code Executor | 15-20k | Code context, tests, files |
| Research Planner | 10-15k | Logs, infrastructure |
| Knowledge Curator | 12-18k | Long docs, KB articles |
| Architecture Lead | 20-30k | Deep reasoning, specifications |

### Intentional Redundancy

Critical skills should exist on **multiple agents** for bus factor (coordination, code review, debugging, API access). Pair a primary agent with a backup that uses a different model backend so split-brain recovery and reasoning diversity are preserved. Gateway tools (subscription-backed) can be enabled on all agents — they share quota, no per-agent cost.

### Model Fallback Chain

```yaml
model:
  default: <primary-model>
fallback_providers:
  - <secondary-provider>
  - <tertiary-provider>
```

### Subscription Gateway Optimization

Route expensive operations through your subscription gateway when active:

```yaml
web:        { backend: firecrawl, use_gateway: true }
image_gen:  { use_gateway: true }
browser:    { cloud_provider: browser-use, use_gateway: true }
tts:        { provider: <gateway>, use_gateway: true }
```

### Cross-Training Decision Matrix

| Same skill on multiple agents? | When YES | When NO |
|---|---|---|
| YES | Critical coordination; different backends give different reasoning patterns | Token overhead not worth marginal gain |
| NO | Exclusive specializations (OAuth-bound, unique role) | Most standard operations |

## Expensive Model Guardrails

When some agents run metered models (Opus, GPT-class) while others run flat-rate, implement strict entry filters to prevent budget burn.

### Cost Model Reference

Track approximate input/output $/1M tokens per agent's model and the multiplier vs your cheapest flat-rate baseline. Use this to decide routing thresholds.

### Mandatory Pre-Response Checklist (in expensive agent's SOUL.md)

```markdown
## When to Act — TOKEN GUARDRAILS (CRITICAL)

**EXPENSIVE MODEL WARNING:** You run on [MODEL] via [PROVIDER]
(metered, ~[N]× cost of baseline). Minimize invocations aggressively.

**MANDATORY pre-check before ANY response:**
1. Is this genuine [ARCH/REASONING]-level work requiring deep analysis?
2. Could a cheaper agent handle this directly?
3. Is the requester explicitly asking for [your specialty] authority?

**If ANY of: trivial implementation, simple fix, status query, routine config → EXIT.**

**Respond ONLY when:**
- Explicit [ARCH] tag or "architecture review" / "system design" request
- [TYPE:ARCH] handoff with genuine cross-system scope
- Complex multi-component reasoning beyond cheaper agents

**EXIT / Stay silent on:**
- Implementation tasks (route to [CHEAPER_AGENT])
- Research queries (route to [RESEARCH_AGENT])
- Documentation requests (route to [SCRIBE_AGENT])
- Trivial questions or status checks

**If unsure: EXIT. Let cheaper coordinator triage.**
```

### Routing Filter (Coordinator Agent)

```python
def route_with_cost_guard(request, complexity,
                          cheap_coordinator, implementation_agent,
                          research_agent, scribe_agent, arch_agent):
    if is_simple_query(request):          return cheap_coordinator
    if is_implementation_task(request):   return implementation_agent
    if is_research_query(request):        return research_agent
    if is_documentation_task(request):    return scribe_agent
    if ("architecture" in request.lower() or "design" in request.lower()
        or "[ARCH]" in request or complexity == "cross_system"):
        return arch_agent
    return cheap_coordinator
```

### Cost Monitoring

Track invocations, input/output tokens, and estimated cost per expensive agent in a daily report. Alert if expensive agent invocations exceed ~10% of total activity.

### Example Routing Decisions

| Request | Bad Routing | Good Routing | Why |
|---------|-------------|--------------|-----|
| "Fix this bug" | Expensive arch agent | Code executor | Implementation, not architecture |
| "Design system X" | Direct, untagged | Arch agent with [ARCH] tag | Genuine system design |
| "Review this PR" | Expensive arch agent | Code executor | Faster/cheaper |
| "What's status of X?" | Expensive arch agent | Cheap coordinator | Status query, no reasoning needed |

### Pitfall: Silent Budget Burn

**Problem**: Expensive agent responds to every @mention by default.
**Solution**: Explicit exit criteria in SOUL.md requiring pre-check.

## Pattern D: Release-Driven Skill Expansion

When a new Hermes release drops with new skills, rapidly expand swarm capabilities by installing, validating, and wiring skills into automation.

### Workflow

```
1. ACQUIRE release notes (GitHub releases, raw markdown)
2. EXTRACT new skills from notes
3. SEARCH hub for exact identifiers (names in notes ≠ hub names)
4. INSTALL across agent profiles with --yes
5. VALIDATE with live demos
6. WIRE into cron no_agent watchdog jobs
7. DOCUMENT scoping report to vault
```

### Step 1: Acquire Release Notes

```bash
curl -sL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/RELEASE_v{VERSION}.md
```

**Pitfall:** Release note summaries may be truncated by web_extract. Always fetch raw markdown via curl.

### Step 2: Extract New Skills

Look for sections like "N new optional skills", "New skills:", "Skills ecosystem", "Skills Hub". Extract: skill name, category, description, PR number.

### Step 3: Search Hub for Exact Identifiers

**CRITICAL:** Release note names often don't match hub identifiers. Some items in notes are built-in tools, not installable skills.

```bash
hermes skills search <keyword>
hermes skills inspect <identifier>   # preview before install
```

### Step 4: Install Across Profiles

```bash
hermes skills install <identifier> --profile <agent> --yes
```

**Pitfall:** Without `--yes`, the TUI blocks on confirmation in automated contexts.
**Pitfall:** `hermes skills view` does not exist — use `hermes skills inspect`.

### Step 5: Validate with Live Demos

```bash
SCRIPT=~/.hermes/profiles/<agent>/skills/<category>/<skill>/scripts/<entry>.py
python3 $SCRIPT <args>
```

**Validation checklist:**
- [ ] Script runs without import errors
- [ ] Output is parseable (JSON, markdown, etc.)
- [ ] No API key required OR key already configured
- [ ] State/watermark files write successfully

### Step 6: Wire Into Cron no_agent Watchdog Jobs

Watcher scripts are designed for `no_agent` cron mode — they run silently and deliver only when new content appears.

```bash
mkdir -p ~/.hermes/scripts/cron-watchers
cp <source-script> ~/.hermes/scripts/cron-watchers/

# Wrapper script invokes the watcher with --name, --url, and limits.
hermes cron create \
  --name "<job-name>" \
  --script cron-watchers/<wrapper>.sh \
  --no-agent \
  --profile <agent> \
  "0 */6 * * *"
```

**Pitfall:** Cron create uses **positional** `schedule` argument, not `--schedule`.
**Pitfall:** `--script` paths must be relative to `~/.hermes/scripts/` (not absolute).
**Pitfall:** `--no-agent` mode delivers script stdout directly. Empty stdout = silent (no spam).

### Step 7: Document Scoping Report

Write to `<vault>/Reports/swarm-skill-scoping-v{VERSION}.md` with sections:
1. Install summary (skill × agent × status table)
2. Agent-by-agent capability map
3. Live demo results
4. New cron jobs (schedule, next run, mode)
5. Validation log per skill
6. Security notes (scan verdicts, exfiltration flags)
7. Next actions (ranked, assigned)

### Built-in Tools vs Skills

Some release "features" are built-in tools, not installable skills (e.g. `x_search`, `vision_analyze`, `video_generate`, `browser_console`). These require auth/config in `~/.hermes/.env`, not installation. Always check whether an entry is a tool or a skill before attempting `skills install`.

## Success Metrics

- Time from "we need X" to assignment: < 10 minutes
- Agent acceptance rate (no reassignment needed): > 90%
- Documentation completeness (workflows exist for subscription tools): 100%
- Human visibility (all assignments announced): 100%
- Release-to-install latency: < 1 day for critical skills
- Demo-to-cron wiring latency: < 1 hour for validated skills

---

*Complements: cron-skill-review, agent-optimization-infrastructure, paperclip-fleet-analyzer*
