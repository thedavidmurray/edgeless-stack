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

---

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

---

## Workflow Overview

```
┌────────────────────────────────────────────────────────────────┐
│  1. SURVEY                                                    │
│     └─→ List skills by category (skills_list)                │
│     └─→ View relevant skills (skill_view)                      │
├────────────────────────────────────────────────────────────────┤
│  2. CATALOG                                                   │
│     └─→ Subscription tools vs local tools                     │
│     └─→ API keys vs managed access                          │
│     └─→ Agent affinity mapping                               │
├────────────────────────────────────────────────────────────────┤
│  3. DOCUMENT                                                  │
│     └─→ Create workflow guides                               │
│     └─→ Create skill-to-agent mapping                        │
│     └─→ Save to canonical vault location                     │
├────────────────────────────────────────────────────────────────┤
│  4. ASSIGN                                                    │
│     └─→ Create Paperclip issue                               │
│     └─→ Assign to specific agent by role                     │
│     └─→ Set priority/acceptance criteria                     │
├────────────────────────────────────────────────────────────────┤
│  5. NOTIFY                                                    │
│     └─→ Post to #bot-backroom ([TO:AGENT] [TYPE:ASSIGNED])  │
│     └─→ Post kickoff to #general (human visibility)           │
└────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Survey Skills Inventory

### List Skills by Category

```python
from hermes_tools import skills_list

# Survey all categories
categories = [
    "nous",        # Subscription tools (image gen, web, TTS, browser)
    "creative",    # Art, design, animation, diagrams
    "mlops",       # ML training, inference, evaluation
    "devops",      # Infrastructure, automation, monitoring
    "software-development",  # Code patterns, debugging, planning
    "media",       # Audio, video, transcription
    "productivity", # Documents, spreadsheets, notes
    "research",    # Papers, scraping, knowledge bases
]

for cat in categories:
    skills = skills_list(category=cat)
    print(f"{cat}: {skills.count} skills")
```

### View Specific Skills

For any skill that looks relevant:

```python
skill_view(name="touchdesigner-generative-art")
# → Returns: description, triggers, required_env, linked_files
```

**Key fields to extract:**
- `triggers`: When should this skill activate?
- `required_environment_variables`: What setup needed?
- `required_commands`: External tools required?
- `linked_files`: Templates, examples, references

---

## Step 2: Catalog Capabilities

### Subscription vs Local Matrix

| Category | Subscription (Nous) | Local/Open | Setup Required |
|----------|---------------------|------------|----------------|
| Image Gen | FLUX 2 Pro, Imagen 2, GPT Image 2 | Stable Diffusion | None |
| Web Tools | Firecrawl search/extract | curl, requests | None |
| Browser | Browserbase automation | Playwright/Selenium | None |
| TTS | OpenAI TTS | whisper, local TTS | None |
| ML Training | — | Axolotl, TRL, Unsloth | GPU, configs |
| Vector DB | — | ChromaDB | pip install |
| Discord | — | discli, webhooks | Bot tokens |

### Agent-to-Skill Affinity Mapping

Based on agent role/title, map primary and secondary skills:

```
Specimen (Generative Art Producer):
  Primary: touchdesigner-generative-art, p5js, pixel-art
  Secondary: image_generate (Nous), stable-diffusion, audiocraft
  
Scribe (Knowledge Curator):
  Primary: obsidian, chroma, notion
  Secondary: web_search, web_extract, youtube-content
  
Curator (Research Analyst):
  Primary: web_search, web_extract, browser automation
  Secondary: dsp, manim-video, baoyu-infographic
  
Kilo (Execution Specialist):
  Primary: codex, claude-code, tdd, systematic-debugging
  Secondary: All mlops, modal-serverless-gpu
  
Builder (Implementation Engineer):
  Primary: claude-code, tdd, requesting-code-review
  Secondary: browser automation (SaaS setup)
  
Minter (On-Chain Deployment):
  Primary: image_generate, pixel-art, claude-design
  Secondary: browser automation (marketplace listing)
  
Critic (Aesthetic Scoring):
  Primary: clip, segment-anything-model, illustration-consistency
  Secondary: image_generate (comparison baselines)
  
NGA-Scout (Open Data Explorer):
  Primary: web_search, web_extract, browser automation
  Secondary: —
```

---

## Step 3: Document Workflows

### Create Tool Workflow Guide

For subscription tools or complex local tools, create dedicated workflow doc:

**File**: `claude-vault/03-Knowledge/Workflows/{tool}-workflow.md`

**Structure**:
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
- Condition 1
- Condition 2

## When NOT to Use
- Alternative tool for X
- Alternative tool for Y

## Tool Reference
| Function | Purpose | Example |
|----------|---------|---------|
| `tool_fn()` | Description | `tool_fn(args)` |

## Agent Mapping
| Agent | Use Case |
|-------|----------|
| Agent A | Specific use |

## Workflow Patterns
1. Pattern A
2. Pattern B
```

### Create Skill-to-Agent Mapping

**File**: `claude-vault/03-Knowledge/Workflows/hermes-skills-agent-mapping.md`

**Structure**:
- Table of all skills by category
- Agent profiles with primary/secondary skills
- Workflow triggers (which skill fires on what input)
- Dependency graph (skill A → skill B chains)

---

## Step 4: Assign Work

### Select Agent by Skill Affinity

```python
def select_agent_for_task(task_description: str, skill_mapping: dict) -> str:
    """
    Match task to agent based on skill keywords in task description.
    """
    keywords_to_agents = {
        ("touchdesigner", "generative art", "animation", "render"): "Specimen",
        ("research", "extract", "web search", "knowledge base"): "Scribe",
        ("code", "implement", "debug", "ship"): "Kilo",
        ("design", "ui", "prototype", "web page"): "Builder",
        ("nft", "image", "artwork", "generat"): "Minter",
        ("score", "aesthetic", "quality", "review"): "Critic",
        ("data", "government", "portal", "explor"): "NGA-Scout",
    }
    
    task_lower = task_description.lower()
    for keywords, agent in keywords_to_agents.items():
        if any(k in task_lower for k in keywords):
            return agent
    
    return "Builder"  # Default implementation agent
```

### Create Paperclip Issue

```python
import subprocess
import json

API_BASE = "http://127.0.0.1:3100/api"
COMPANY_ID = "{your-company-id}"
AGENT_IDS = {
    "Specimen": "...",
    "Scribe": "...",
    # ... etc
}

def assign_to_agent(task_title: str, task_description: str, agent_name: str, priority: str = "medium"):
    agent_id = AGENT_IDS[agent_name]
    
    issue_payload = {
        "title": task_title,
        "description": task_description,
        "priority": priority,
        "status": "in_progress",
        "assigneeAgentId": agent_id
    }
    
    result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         f"{API_BASE}/companies/{COMPANY_ID}/issues",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(issue_payload)],
        capture_output=True, text=True
    )
    
    data = json.loads(result.stdout)
    return data.get("identifier")
```

---

## Step 5: Notify

### Discord Bot-Backroom (Agent Coordination)

```python
def notify_agent_in_backroom(agent_name: str, issue_id: str, task_summary: str, eta: str):
    """
    Post structured message to #bot-backroom using anti-loop protocol.
    """
    payload = {
        "content": (
            f"`[{timestamp}]` **[FROM:Hive]** **[TO:{agent_name.upper()}]** "
            f"[TYPE:ASSIGNED] [REF:{issue_id}]**\\n"
            f"ETA: {eta}\\n\\n"
            f"{task_summary}"
        )
    }
    
    # POST to 1498530774062858240 (#bot-backroom)
```

### Discord General (Human Visibility)

```python
def announce_kickoff_to_general(agent_name: str, issue_id: str, task_title: str, eta: str):
    """
    Post kickoff notice to #general for human awareness.
    """
    payload = {
        "content": (
            f"🎯 **{task_title}**\\n\\n"
            f"**{issue_id}** assigned to **@{agent_name}**\\n"
            f"ETA: {eta}\\n\\n"
            f"Agent is ON IT. 🔥"
        )
    }
    
    # POST to 1463643624100335618 (#general)
```

---

## Complete Example: TouchDesigner Live Session

### Scenario
User says: "I have TouchDesigner open — I need parameter sweep variations generated."

### Execution

```python
# 1. SURVEY — Check if TouchDesigner skill exists
skills = skills_list(category="creative")
# → Found: touchdesigner-generative-art

skill_view(name="touchdesigner-generative-art")
# → Requires: TOUCHDESIGNER_PATH environment variable
# → Templates: noise_flow, fractal_mountains, audio_reactive

# 2. CATALOG — Subscription? Local?
# → Local tool (requires TD installation)
# → User confirms TD installed at /Applications/TouchDesigner.app/...

# 3. DOCUMENT — Create/update workflow
# → File: nous-subscription-tools-workflow.md (broader context)
# → File: hermes-skills-agent-mapping.md (updated with TD skill)

# 4. ASSIGN — Select Specimen (Generative Art Producer)
issue_id = assign_to_agent(
    task_title="TouchDesigner Live Session — Parameter Sweep Generation",
    task_description="""
    User has TouchDesigner GUI open NOW.
    
    OBJECTIVE: Generate 20+ parameter sweep variations
    
    PHASES:
    1. Verify TD setup (5 min)
    2. Parameter sweep: seed 1-20, speed 0.1-2.0 (30 min)
    3. Render 5 champions @ 300 frames (30 min)
    4. Document & notify (10 min)
    
    OUTPUT: ~/claude-projects/output/td_sweep_YYYY-MM-DD/
    """,
    agent_name="Specimen",
    priority="urgent"
)
# → Returns: EDGA-XXX

# 5. NOTIFY — Bot-backroom + General
notify_agent_in_backroom(
    agent_name="Specimen",
    issue_id=issue_id,
    task_summary="TouchDesigner live session — 20 variations + 5 renders",
    eta="75 minutes"
)

announce_kickoff_to_general(
    agent_name="Specimen",
    issue_id=issue_id,
    task_title="TouchDesigner Live Session",
    eta="75 minutes"
)
```

---

## Output Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Tool Workflow Guide | `claude-vault/03-Knowledge/Workflows/{tool}-workflow.md` | When/how to use specific tools |
| Skill-Agent Mapping | `claude-vault/03-Knowledge/Workflows/hermes-skills-agent-mapping.md` | Reference for delegation decisions |
| Paperclip Issue | EDGA-XXX | Tracked work assignment |
| Discord Backroom | #bot-backroom | Agent coordination (structured tags) |
| Discord General | #general | Human visibility of active work |

---

## Integration with Other Skills

| Skill | Relationship |
|-------|--------------|
| `cron-skill-review` | This skill complements automated gap detection with manual capability audits |
| `agent-optimization-infrastructure` | Uses telemetry from this skill's assignments for dynamic delegation optimization |
| `paperclip-fleet-analyzer` | Uses assignment data for fleet health reports |
| `paperclip-api` | Underlying API for issue creation/assignment |
| `discord-swarm-handoff-protocol` | Structured messaging format for notifications |

---

## Common Patterns

### Pattern A: New Tool Discovery
User: "Can we use [tool] for [purpose]?"

1. `skills_list` all categories → Find if skill exists
2. `skill_view` → Check requirements, triggers
3. Document in workflow guide if complex
4. Map to appropriate agent(s)
5. Create test issue if needed

### Pattern B: Complex Multi-Step Assignment
User: "Do [complex thing] with [toolset]"

1. Survey all required skills
2. Identify primary vs supporting agents
3. Create parent issue with sub-tasks
4. Assign sub-tasks to respective agents
5. Post coordination messages linking dependencies

### Pattern C: Subscription Audit
User: "What do we get from [subscription]?"

1. `skills_list(category="nous")` or relevant
2. Catalog subscription vs local capabilities
3. Create subscription workflow guide
4. Update agent mappings for new tools
5. Notify agents of new capabilities

---

## Pitfalls & Solutions

| Pitfall | Solution |
|---------|----------|
| Agent not responding | Check if agent has `reportsTo` set; escalate to boss |
| Skill requires setup | Document setup steps in workflow guide before assigning |
| Subscription tool expired | Check auth status first; fallback to local alternatives |
| Unclear which agent | Use keyword matching; default to Builder for implementation |
| Issue creation fails | Verify `assigneeAgentId` present; check Paperclip API response |
| Discord rate limits | Use structured tags instead of @mentions; post once to each channel |

---

## Section: Skill Allocation & Redundancy Design

When designing optimal agent-skill mappings (not just auditing existing ones):

### Token Budget Planning Per Agent Role

| Agent Role | Token Budget | Rationale |
|------------|--------------|-----------|
| Coordinator | 8-12k | Fast routing, minimal context |
| Code Executor | 15-20k | Code context, tests, files |
| Research Planner | 10-15k | VPS logs, infrastructure |
| Knowledge Curator | 12-18k | Long docs, KB articles |
| Architecture Lead | 20-30k | Deep reasoning, specifications |

### Intentional Redundancy Patterns

**Critical skills should exist on multiple agents** for bus factor:

| Skill | Primary Agent | Backup Agent(s) | Rationale |
|-------|---------------|-----------------|-----------|
| `hermes-multi-agent-discord` | Hive (coordinator) | Beau (VPS) | Split-brain recovery |
| `github-code-review-v2` | Kilo (Codex) | Edgeless-CC (Claude) | Speed vs depth |
| `systematic-debugging` | Kilo | Edgeless-CC | Different reasoning patterns |
| `paperclip-api` | Hive | Beau | Fleet vs infra auditing |

**Gateway tools** (`nous-portal-*`) should be enabled on ALL agents — they use shared subscription quota, no per-agent cost.

### Model Fallback Chain Configuration

Configure primary → secondary → tertiary models per agent for resilience:

```yaml
# Kilo (Code Execution)
model:
  default: gpt-5.3-codex  # Primary: frontier code gen
fallback_providers:
  - nous  # Secondary: Claude Sonnet (fast)
  - fireworks  # Tertiary: Kimi K2.5 (flat rate fallback)

# Edgeless-CC (Architecture)
model:
  default: claude-opus-4.7  # Primary: deep reasoning
fallback_providers:
  - nous  # Secondary: o3 Deep Research
  - fireworks  # Tertiary: Kimi K2 Thinking
```

### Subscription Gateway Optimization

Route expensive operations through Nous Portal gateway when subscription active:

| Operation | Without Gateway | With Gateway (Nous) |
|-----------|-----------------|----------------------|
| Image gen | FAL_KEY metered | Included |
| Web extract | Firecrawl API key | Included |
| Browser automation | Browserbase credits | Included |
| TTS | OpenAI API key | Included |

**Config pattern**:
```yaml
web:
  backend: firecrawl
  use_gateway: true  # ← Uses subscription
image_gen:
  use_gateway: true
browser:
  cloud_provider: browser-use
  use_gateway: true
tts:
  provider: nous  # ← Not openai directly
  use_gateway: true
```

### Cross-Training Decision Matrix

| Same skill on different agents? | When YES | When NO |
|-------------------------------|----------|---------|
| YES | Critical coordination skills, different model backends provide different reasoning patterns | Token overhead not worth marginal gain |
| NO | Exclusive specializations (e.g., codex requires specific OAuth), unique agent roles | Most standard operations |

---

## Section: Expensive Model Guardrails & Token Protection

When some agents run metered models (Claude Opus, GPT-4o) while others run flat-rate (Kimi K2.5), implement strict entry filters to prevent budget burn.

### Cost Model Reference (Approximate)

| Model | Input/1M tokens | Output/1M tokens | vs Kimi K2.5 |
|-------|-----------------|------------------|--------------|
| Kimi K2.5 (Fireworks) | $0 (flat rate) | $0 (flat rate) | 1× baseline |
| Claude Sonnet 4 | ~$3 / ~$15 | ~20× |
| Claude Opus 4.6 | ~$15 / ~$75 | ~100× |
| GPT-5.3-Codex | ~$10 / ~$30 | ~50× |

### Mandatory Pre-Response Checklist (Agent SOUL.md)

Add to expensive agents' `SOUL.md` or `AGENTS.md`:

```markdown
## When to Act — TOKEN GUARDRAILS (CRITICAL)

**⚠️ EXPENSIVE MODEL WARNING:** You run on [MODEL] via [PROVIDER] 
(metered, ~[N]× cost of Kimi K2.5). Minimize invocations aggressively.

**MANDATORY pre-check before ANY response:**
1. Is this genuine [ARCH/REASONING]-level work requiring deep analysis?
2. Could a cheaper agent (Kimi-based) handle this directly?
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

Add to coordinator's routing logic:

```python
EXPENSIVE_AGENTS = {
    "Edgeless-CC": {"model": "claude-opus-4.6", "cost_mult": 100},
    "Kilo": {"model": "gpt-5.3-codex", "cost_mult": 50},  # But necessary for code
}

def route_with_cost_guard(request: str, estimated_complexity: str) -> str:
    """
    Route to appropriate agent with cost protection.
    """
    # Check if cheap agents can handle
    if is_simple_query(request):
        return "Hive"  # Kimi/free
    
    if is_implementation_task(request):
        return "Kilo"  # Codex - expensive but necessary
    
    if is_research_query(request):
        return "Beau"  # Kimi/free
    
    if is_documentation_task(request):
        return "Scribe"  # Kimi/free
    
    # ONLY route to expensive architecture agent if:
    if (
        "architecture" in request.lower() or
        "design" in request.lower() or
        "[ARCH]" in request or
        complexity == "cross_system"
    ):
        return "Edgeless-CC"
    
    # Default to cheap coordinator if unclear
    return "Hive"
```

### Agent Configuration Pattern

**Expensive agent profile** (e.g., `~/.hermes/profiles/edgeless-cc/config.yaml`):

```yaml
model:
  default: anthropic/claude-opus-4.6
  provider: nous  # Uses subscription, still metered
providers:
  tts: nous
  web: nous
  image_gen: nous
  browser: nous
# Note: No fallback to even more expensive models
```

**Cheap agent profile** (e.g., `~/.hermes/profiles/hive/config.yaml`):

```yaml
model:
  default: accounts/fireworks/models/kimi-k2p5
  provider: custom
  api_key: ${FIREWORKS_API_KEY}
  base_url: https://api.fireworks.ai/inference/v1
# Flat rate - invoke freely
```

### Cost Monitoring & Alerting

Track in daily alignment reports:

```python
DAILY_COST_REPORT = {
    "Edgeless-CC": {
        "invocations": 12,
        "input_tokens": 45000,
        "output_tokens": 18000,
        "estimated_cost": 1.35,  # $1.35
        "alert_threshold": 5.00,  # Alert if > $5/day
    },
    "Hive": {
        "invocations": 245,
        "cost": 0,  # Flat rate
    }
}
```

Alert if expensive agent invocations exceed 10% of total activity.

### Example Routing Decisions

| Request | Bad Routing | Good Routing | Why |
|---------|-------------|--------------|-----|
| "Fix this bug" | Edgeless-CC (Opus) | Kilo (Codex) | Implementation, not architecture |
| "Design agent bus" | Direct to Edgeless-CC | Edgeless-CC with [ARCH] tag | Genuine system design ✓ |
| "Review this PR" | Edgeless-CC (Opus) | Kilo (Codex) | Code review, faster/cheaper |
| "What's status of X?" | Edgeless-CC (Opus) | Hive (Kimi/free) | Status query, no reasoning needed |
| "Plan architecture" | Ask user first | Edgeless-CC | Clear arch scope ✓ |

### Pitfall: Silent Budget Burn

**Problem**: Expensive agent responds to every @mention by default.

**Solution**: Explicit exit criteria in SOUL.md requiring pre-check.

---

## Pattern D: Release-Driven Skill Expansion

When a new Hermes release drops with new skills, rapidly expand swarm capabilities by installing, validating, and wiring skills into automation. This is the full lifecycle from release notes → live automation.

### Workflow

```
1. ACQUIRE release notes (GitHub releases, raw markdown, X posts)
2. EXTRACT new skills from release notes
3. SEARCH hub for exact identifiers (names in notes ≠ hub names)
4. INSTALL across agent profiles with --yes
5. VALIDATE with live demos
6. WIRE into cron no_agent watchdog jobs
7. DOCUMENT scoping report to vault
```

### Step 1: Acquire Release Notes

```bash
# GitHub raw markdown (most reliable)
curl -sL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/RELEASE_v{VERSION}.md

# GitHub releases page (extract via browser or web_extract)
# Tags page for version chronology
```

**Pitfall:** Release note summaries may be truncated by web_extract. Always fetch the raw markdown file directly via curl.

### Step 2: Extract New Skills

Look for sections like:
- "9 new optional skills"
- "New skills:"
- "Skills ecosystem"
- "Skills Hub"

Extract: skill name, category, description, PR number.

### Step 3: Search Hub for Exact Identifiers

**CRITICAL:** Release note names often don't match hub identifiers.

| Release Note Name | Actual Hub Identifier |
|-------------------|----------------------|
| yahoo-finance | `official/finance/stocks` |
| unified-evm | `official/blockchain/evm` |
| api-testing | Does not exist in hub |
| x_search | Built-in tool (not a skill) |

```bash
# Search for exact identifier
hermes skills search <keyword>

# Inspect before install
hermes skills inspect <identifier>
```

### Step 4: Install Across Profiles

```bash
# Install with --yes to skip confirmation prompts
hermes skills install <identifier> --profile <agent> --yes

# Example: install to multiple agents
hermes skills install official/blockchain/hyperliquid --profile trader --yes
hermes skills install official/devops/watchers --profile beau --yes
hermes skills install official/research/osint-investigation --profile hive --yes
```

**Pitfall:** Without `--yes`, the TUI blocks on confirmation and install appears to hang or fail silently in automated contexts.

**Pitfall:** The `hermes skills view` command does not exist. Use `hermes skills inspect <identifier>` to preview a skill before install.

### Step 5: Validate with Live Demos

Run the skill's scripts directly to verify functionality:

```bash
# Example: stocks skill (Yahoo Finance)
SCRIPT=~/.hermes/profiles/trader/skills/finance/stocks/scripts/stocks_client.py
python3 $SCRIPT quote AAPL
python3 $SCRIPT crypto BTC
python3 $SCRIPT compare NVDA TSLA

# Example: watchers skill (RSS polling)
SCRIPT=~/.hermes/profiles/beau/skills/devops/watchers/scripts/watch_rss.py
python3 $SCRIPT --name hn_test --url https://news.ycombinator.com/rss --max 5
```

**Validation checklist:**
- [ ] Script runs without import errors
- [ ] Output is parseable (JSON, markdown, etc.)
- [ ] No API key required OR key is already configured
- [ ] State/watermark files write successfully

### Step 6: Wire Into Cron no_agent Watchdog Jobs

The `watchers` skill scripts are designed for `no_agent` cron mode — they run silently and only deliver when new content appears.

**Step 6a: Copy script to canonical cron scripts directory**

```bash
mkdir -p ~/.hermes/scripts/cron-watchers
cp ~/.hermes/profiles/beau/skills/devops/watchers/scripts/watch_rss.py \
   ~/.hermes/scripts/cron-watchers/
```

**Step 6b: Create wrapper script**

```bash
# ~/.hermes/scripts/cron-watchers/watch-hermes-releases.sh
#!/bin/bash
SCRIPT="${HERMES_HOME}/skills/devops/watchers/scripts/watch_rss.py"
python3 "$SCRIPT" \
  --name hermes_releases \
  --url "https://github.com/NousResearch/hermes-agent/releases.atom" \
  --max 5
```

**Step 6c: Create cron job (positional schedule syntax)**

```bash
# WRONG: hermes cron create --schedule "0 */6 * * *"  (flag syntax doesn't work)
# RIGHT: positional schedule argument

hermes cron create \
  --name "hermes-release-watcher" \
  --script cron-watchers/watch-hermes-releases.sh \
  --no-agent \
  --profile beau \
  "0 */6 * * *"
```

**Pitfall:** Cron create uses **positional** `schedule` argument, not `--schedule` flag. The schedule string comes after all options.

**Pitfall:** `--script` paths must be relative to `~/.hermes/scripts/` (not absolute paths). The script file must physically exist under `~/.hermes/scripts/`.

**Pitfall:** `--no-agent` mode delivers script stdout directly. Empty stdout = silent (no spam). Only fires when there's new content.

### Step 7: Document Scoping Report

Write a comprehensive report to vault:

**File:** `claude-vault/13-Reports/swarm-skill-scoping-v{VERSION}.md`

**Sections:**
1. Install summary (table: skill × agent × status)
2. Agent-by-agent capability map
3. Live demo results (quotes, output samples)
4. New cron jobs (schedule, next run, mode)
5. Validation log (test result per skill)
6. Security notes (scan verdicts, exfiltration flags)
7. Next actions (ranked, assigned to agents)

### Built-in Tools vs Skills

Some v0.14.0 "features" are built-in tools, not installable skills:

| Feature | Type | Activation |
|---------|------|------------|
| `x_search` | built-in tool | Configure X OAuth/API key in `~/.hermes/.env` |
| `vision_analyze` | built-in tool | Ready when model supports vision |
| `video_generate` | built-in tool | Ready with provider config |
| `browser_console` | built-in tool | Ready (180x faster in v0.14.0) |

These require auth/config, not installation.

### Complete Example: v0.14.0 Foundation Release

```bash
# 1. Acquire
curl -sL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/RELEASE_v0.14.0.md

# 2. Extract: 9 new skills: hyperliquid, stocks, evm, api-testing,
#    darwinian-evolver, osint-investigation, pinggy-tunnel, watchers, notion

# 3. Search hub identifiers
hermes skills search hyperliquid    # → official/blockchain/hyperliquid
hermes skills search yahoo          # → official/finance/stocks
hermes skills search evm              # → official/blockchain/evm
hermes skills search api-testing      # → NOT FOUND (skip)

# 4. Install across profiles
hermes skills install official/blockchain/hyperliquid --profile trader --yes
hermes skills install official/finance/stocks --profile trader --yes
hermes skills install official/blockchain/evm --profile trader --yes
hermes skills install official/devops/watchers --profile beau --yes
hermes skills install official/research/osint-investigation --profile hive --yes
hermes skills install official/devops/pinggy-tunnel --profile kilo --yes
hermes skills install official/research/darwinian-evolver --profile scribe --yes
hermes skills install skills-sh/openai/skills/notion-research-documentation --profile scribe --yes

# 5. Validate
python3 ~/.hermes/profiles/trader/skills/finance/stocks/scripts/stocks_client.py quote AAPL
python3 ~/.hermes/profiles/beau/skills/devops/watchers/scripts/watch_rss.py --name hn --url https://news.ycombinator.com/rss --max 5

# 6. Wire cron jobs
hermes cron create --name "hermes-release-watcher" \
  --script cron-watchers/watch-hermes-releases.sh --no-agent --profile beau \
  "0 */6 * * *"

hermes cron create --name "hn-frontpage-watcher" \
  --script cron-watchers/watch-hn-frontpage.sh --no-agent --profile beau \
  "*/30 * * * *"

# 7. Document
# → claude-vault/13-Reports/swarm-skill-scoping-v0.14.0.md
```

## Success Metrics

Track effectiveness of capability audits:
- Time from "we need X" to assignment: < 10 minutes
- Agent acceptance rate (no reassignment needed): > 90%
- Documentation completeness (workflows exist for subscription tools): 100%
- Human visibility (all assignments announced in #general): 100%
- Release-to-install latency: < 1 day for critical skills
- Demo-to-cron wiring latency: < 1 hour for validated skills

---

*Created: 2026-04-28*  
*Updated: 2026-05-20 — Added release-driven skill expansion pattern with cron wiring, hub identifier mapping, and no_agent watchdog configuration*
*Complements: cron-skill-review, agent-optimization-infrastructure, paperclip-fleet-analyzer*
