---
name: skill-creator
description: >
  Guide for creating and updating Claude Code skills. Use when a user wants to
  create a new skill, update an existing skill, add frontmatter to a skill,
  convert a skill to the standard format, validate skill structure, or design
  bundled resources. Triggers on: "create a skill", "update skill", "new skill
  for X", "add a /command", "skill for doing Y", "skill frontmatter standard",
  "scaffold a skill", "skill template", "convert to skill format", "validate skill",
  "skill anatomy", "skill best practices", "what category is this skill",
  "which pattern should I use", "skill workflow pattern".
metadata:
  tags: [skill, meta, creation, frontmatter, standard, scaffold, template, validation, anthropic-patterns]
  tier: general
  domain: kernel
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
when_to_apply: When creating a new skill, updating an existing skill's frontmatter, or converting documentation to the standard skill format
---

# Skill Creator

Create well-structured skills that extend Claude Code's capabilities using official Anthropic patterns.

## About Skills

Skills are modular packages that extend Claude's capabilities by providing specialized knowledge, workflows, and tools. They transform Claude from a general-purpose agent into a specialized one equipped with procedural knowledge.

### What Skills Provide

1. **Specialized workflows** - Multi-step procedures for specific domains
2. **Tool integrations** - Instructions for working with specific file formats or APIs
3. **Domain expertise** - Company-specific knowledge, schemas, business logic
4. **Bundled resources** - Scripts, references, and assets for complex tasks

### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (required)
│   │   ├── name: (required)
│   │   ├── description: (required — multi-line OK, pack with trigger terms)
│   │   └── metadata: (required — tags, tier, domain)
│   └── Markdown instructions (required)
│       ├── ## When to Use (required — explicit trigger list)
│       └── ## Instructions or ## Workflow (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash)
    ├── references/       - Documentation loaded as needed
    └── assets/           - Files used in output (templates, etc.)
```

**File Index Contract**: If a skill has sub-files (scripts/, references/, assets/), SKILL.md MUST
explicitly list every file with a one-line description. The agent cannot know what exists without
this index.

## YAML Frontmatter Standard

All skills MUST use this frontmatter schema:

```yaml
---
name: skill-name          # kebab-case, matches folder name exactly
description: >
  Long description packed with trigger terms for AI routing.
  Include synonyms, use-case phrases, keyword matches.
  Use third person. Be specific about trigger conditions.
  Example: "Use when user asks to X, Y, or Z. Triggers on: 'do X', 'help with Y'."
metadata:
  tags: [tag1, tag2, tag3]       # Lowercase, specific
  tier: general | task-specific  # general = broad applicability
  domain: kernel | ingestion | observability | knowledge | product | creative | workflow | tooling
---
```

### Description Quality: WHAT + WHEN Pattern

The `description` field is the most critical for skill routing. It MUST include:
- **WHAT** the skill does (functionality, capabilities)
- **WHEN** to use it (trigger phrases, use cases)

**Good Example:**
```yaml
description: >
  Rotate, merge, split, and annotate PDF files. Use when user provides a PDF
  and asks to combine pages, rotate, extract sections, or add annotations.
  Triggers on: 'rotate PDF', 'merge these PDFs', 'split PDF at page X'.
```

**Bad Examples:**
```yaml
# BAD: Vague WHAT
description: "A skill for doing things with PDFs"

# BAD: Missing WHEN
description: "PDF manipulation tool with rotation and merging capabilities"

# BAD: No trigger phrases
description: "This skill helps users work with PDF documents"
```

### Field Guidance

**`description`** (most important field):
- This is what the routing layer reads to decide whether to load the skill
- Pack with synonyms, use-case phrases, and explicit trigger terms
- Include "Triggers on: ..." or "Use when user says ..." phrasing
- Multi-line YAML block scalar (`>`) preferred for longer descriptions
- MUST be under 1024 characters
- MUST include both WHAT and WHEN

**`tier`**:
- `general` — Applies across many contexts (memory, backlog, session planning)
- `task-specific` — Domain-scoped (job search, trading bot, generative art)

**`domain`**:
- `kernel` — Core agent infrastructure (hooks, memory, completion, skill creation)
- `ingestion` — Content capture, transformation, storage
- `observability` — Monitoring, health, logging, alerting
- `knowledge` — ChromaDB, retrieval, personas, research
- `product` — Vault integration, taxonomy, public-facing tools
- `creative` — Generative art, experiments, side projects
- `workflow` — Cross-cutting execution patterns, planning, review loops, and operator procedures
- `tooling` — Specific tool integrations, CLIs, third-party systems, and utility workflows

## Three Skill Categories

When creating a skill, first identify which category it belongs to:

### Category 1: Document & Asset Creation
**Purpose:** Creating consistent documents, presentations, apps, designs, code

**Characteristics:**
- Uses embedded style guides, templates, quality checklists
- No external tools (MCPs) required
- Focus on consistency and quality

**Examples:**
- `frontend-design` — Apply design system to components
- `brand-guidelines` — Enforce brand colors, typography
- `document-generator` — Create formatted reports

**Template Starter:**
```markdown
## When to Use
Use when user needs to create [document type] following [standard].
Triggers on: "generate [doc]", "create [doc] with [style]".

## Workflow
1. **Understand Requirements** — Gather content, audience, constraints
2. **Select Template** — Choose from assets/ based on document type
3. **Apply Style Guide** — Reference embedded standards
4. **Quality Check** — Validate against checklist
5. **Deliver Output** — Generate final document
```

### Category 2: Workflow Automation
**Purpose:** Multi-step processes with consistent methodology

**Characteristics:**
- Step-by-step workflows with validation gates
- Iterative refinement loops
- State tracking across steps

**Examples:**
- `skill-creator` — This skill itself
- `onboarding-checklist` — Employee setup workflow
- `deploy-pipeline` — Release validation sequence

**Template Starter:**
```markdown
## When to Use
Use when user needs to execute [process] following [methodology].
Triggers on: "run [process]", "execute [workflow]", "start [procedure]".

## Workflow
1. **Initialization** — Set up state, validate prerequisites
2. **Phase 1: [Name]** — [Description]
   - Validation gate: [Criteria]
3. **Phase 2: [Name]** — [Description]
   - Validation gate: [Criteria]
4. **Finalization** — [Completion steps]
```

### Category 3: MCP Enhancement
**Purpose:** Workflow guidance for MCP tool access

**Characteristics:**
- Coordinates multiple MCP calls
- Embeds domain expertise for tool usage
- Handles auth, errors, rate limits

**Examples:**
- `sentry-code-review` — Pull error data, correlate with code
- `linear-triage` — Sync Linear issues with external state
- `notion-sync` — Bidirectional data sync

**Template Starter:**
```markdown
## When to Use
Use when user needs to [action] using [MCP tool].
Triggers on: "[action] with [tool]", "sync [X] to [Y]".

## Workflow
1. **Auth Check** — Verify MCP connection and credentials
2. **Data Retrieval** — Call [MCP:operation] with [params]
3. **Transform** — Process data for [purpose]
4. **Action** — Execute [MCP:operation]
5. **Verify** — Confirm success via [check]
```

## Five Workflow Patterns

Choose the pattern that fits your skill's structure:

### Pattern 1: Sequential Workflow Orchestration
**Use when:** Explicit step ordering with dependencies

**Structure:**
- Step N must complete before Step N+1
- Validation at each stage
- Rollback instructions for failures

**Example:**
```markdown
## Workflow (Sequential)
1. **Setup** — Initialize environment
2. **Extract** — Parse input data (depends on Setup)
3. **Transform** — Process data (depends on Extract)
4. **Load** — Save results (depends on Transform)
```

### Pattern 2: Multi-MCP Coordination
**Use when:** Using multiple MCP tools together

**Structure:**
- Clear phase separation across services
- Data passing between MCPs
- Validation before moving to next phase

**Example:**
```markdown
## Workflow (Multi-MCP)
1. **GitHub Phase**
   - Fetch PR data via MCP:github
   - Validate: PR exists and accessible
2. **Linear Phase**
   - Create issue via MCP:linear
   - Pass PR URL as attachment
   - Validate: Issue created successfully
3. **Slack Phase**
   - Notify channel via MCP:slack
   - Include Linear issue link
```

### Pattern 3: Iterative Refinement
**Use when:** Draft → Review → Improve cycles

**Structure:**
- Initial draft → Quality check → Refinement loop → Finalization
- Explicit quality criteria
- Know when to stop iterating (max iterations or quality threshold)

**Example:**
```markdown
## Workflow (Iterative)
1. **Draft** — Generate initial output
2. **Quality Check** — Evaluate against criteria:
   - [ ] Criterion 1
   - [ ] Criterion 2
3. **Refinement Loop** (max 3 iterations)
   - If criteria not met: improve and re-check
   - If criteria met: proceed
4. **Finalize** — Deliver polished result
```

### Pattern 4: Context-Aware Tool Selection
**Use when:** Decision trees based on context

**Structure:**
- Decision trees based on input
- Fallback options
- Transparency about choices

**Example:**
```markdown
## Workflow (Context-Aware)
1. **Analyze Input** — Determine input type:
   - If PDF: → Use pdftk tools
   - If Image: → Use imagemagick
   - If Unknown: → Ask user for clarification
2. **Select Tool** — Based on analysis
3. **Execute** — Apply selected tool
4. **Report** — Explain which tool was used and why
```

### Pattern 5: Domain-Specific Intelligence
**Use when:** Deep domain expertise required

**Structure:**
- Compliance checks before action
- Domain expertise embedded in logic
- Comprehensive audit trails

**Example:**
```markdown
## Workflow (Domain-Specific)
1. **Compliance Check** — Verify against [regulation]:
   - [ ] Requirement 1
   - [ ] Requirement 2
2. **Domain Analysis** — Apply [domain] expertise:
   - Check [specific rule]
   - Validate against [standard]
3. **Execute with Audit** — Perform action with logging
4. **Report** — Document decisions for audit trail
```

## Skill Creation Process

### Step 1: Identify Category and Pattern

Ask clarifying questions:
- "What functionality should this skill support?"
- "Can you give examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"
- **Which category fits best?** (Document/Asset, Workflow, MCP Enhancement)
- **Which pattern fits best?** (Sequential, Multi-MCP, Iterative, Context-Aware, Domain-Specific)

### Step 2: Plan the Reusable Contents

For each use case, identify:
1. What code gets rewritten repeatedly? → `scripts/`
2. What documentation is referenced? → `references/`
3. What templates or assets are used? → `assets/`

### Step 3: Initialize the Skill

Run the initialization script:

```bash
bash .claude/skills/skill-creator/scripts/init_skill.sh <skill-name>
```

This creates:
- Skill directory with proper structure
- Template SKILL.md with frontmatter
- Empty resource directories

### Step 4: Edit the Skill

#### YAML Frontmatter (Required)

Use the full standard schema above. Key requirements:
- `name` matches folder name exactly
- `description` is multi-line, trigger-term-rich, includes WHAT + WHEN
- `metadata.tags`, `metadata.tier`, `metadata.domain` all present

#### Markdown Body

Required sections:
1. `## When to Use` — Explicit list of trigger conditions and phrases
2. `## Instructions` or `## Workflow` — Step-by-step procedure using selected pattern

**Writing Style**: Use imperative form (verb-first), not second person.
- Good: "To accomplish X, do Y"
- Avoid: "You should do X"

#### File Index (Required if sub-files exist)

If any of `scripts/`, `references/`, or `assets/` contain files, add a section:

```markdown
## File Index

| File | Purpose |
|------|---------|
| `scripts/validate.py` | Runs linting and type checks |
| `references/api-schema.md` | OpenAPI spec for the target service |
| `assets/template.html` | Output template for reports |
```

### Step 5: Add Bundled Resources

#### Scripts (`scripts/`)

Executable code for tasks needing deterministic reliability.

- **When to include**: Code rewritten repeatedly or needing reliability
- **Benefits**: Token efficient, deterministic, may run without loading
- **Example**: `scripts/validate.py` for validation tasks

#### References (`references/`)

Documentation loaded into context as needed.

- **When to include**: Documentation Claude should reference while working
- **Examples**: API schemas, company policies, workflow guides
- **Best practice**: Keep SKILL.md lean; move details to references/

#### Assets (`assets/`)

Files used in output, not loaded into context.

- **When to include**: Templates, images, boilerplate
- **Examples**: `assets/template.html`, `assets/logo.png`

## Progressive Disclosure

Skills use three-level loading to manage context:

1. **Metadata** (name + description) — Always in context (~100 words)
2. **SKILL.md body** — When skill triggers (<5k words)
3. **Bundled resources** — As needed by Claude (unlimited)

Keep SKILL.md under 200 lines. If longer, move detailed reference material to `references/`.

## Quality Checklist

Before considering a skill complete, verify:

### Structural Checklist
- [ ] YAML frontmatter has `name`, `description`, and `metadata` block
- [ ] `description` is multi-line with explicit trigger terms
- [ ] `description` includes both WHAT and WHEN
- [ ] `metadata.tags`, `metadata.tier`, `metadata.domain` all set
- [ ] `## When to Use` section is explicit with trigger phrases
- [ ] `## Instructions` or `## Workflow` section present
- [ ] If sub-files exist, `## File Index` documents every one
- [ ] SKILL.md is under 200 lines (move excess to references/)
- [ ] Unnecessary empty resource directories removed

### Testing Checklist (Reference A)
Before upload, verify:
- [ ] **Triggering Test** — Skill loads on obvious relevant queries
- [ ] **Paraphrase Test** — Skill loads on rephrased versions
- [ ] **Negative Test** — Skill does NOT load on unrelated topics
- [ ] **Functional Test** — Valid outputs, API success, error handling
- [ ] **Edge Case Test** — Handles empty inputs, large inputs, errors

### Success Criteria
**Quantitative:**
- Skill triggers on 90%+ of relevant queries
- Completes workflow in expected tool calls
- 0 failed API calls per workflow

**Qualitative:**
- Users don't need to prompt about next steps
- Workflows complete without correction
- Consistent results across sessions

## Command

```
/skill-creator                    # Interactive skill creation
/skill-creator init <name>        # Initialize new skill
/skill-creator validate <path>    # Validate existing skill
/skill-creator category <name>    # Show category template
/skill-creator pattern <name>     # Show pattern template
```

## File Index

| File | Purpose |
|------|---------|
| `scripts/init_skill.sh` | Scaffolds a new skill directory with template SKILL.md and empty resource subdirectories |
| `references/category-templates.md` | Starter templates for each of the three skill categories |
| `references/pattern-examples.md` | Detailed examples of the five workflow patterns |

## Examples

### Example: Creating a "PDF Editor" Skill (Category 1: Document & Asset Creation)

1. **Identify**: Category 1 — Document creation, Pattern 4 — Context-Aware (different tools for different PDF operations)
2. **Plan**: `scripts/rotate_pdf.py` for rotation logic
3. **Initialize**: `bash scripts/init_skill.sh pdf-editor`
4. **Edit**: Add workflow using Pattern 4 structure, reference pdftk documentation
5. **Test**: Verify skill triggers on "rotate this PDF"

### Example: Creating a "Brand Guidelines" Skill (Category 1: Document & Asset Creation)

1. **Identify**: Category 1 — Document consistency, Pattern 3 — Iterative Refinement
2. **Plan**: `assets/brand-colors.css`, `references/style-guide.md`
3. **Initialize**: Create skill structure
4. **Edit**: Document brand rules, color palettes, typography using iterative workflow
5. **Test**: Verify skill triggers on "use our brand guidelines"

### Example: Creating a "Sentry Code Review" Skill (Category 3: MCP Enhancement)

1. **Identify**: Category 3 — MCP coordination, Pattern 2 — Multi-MCP
2. **Plan**: Integrate Sentry MCP + GitHub MCP
3. **Initialize**: `bash scripts/init_skill.sh sentry-review`
4. **Edit**: Workflow pulls Sentry errors, correlates with GitHub commits
5. **Test**: Verify integration works end-to-end

## Related Skills

- `dev-docs` - Document skills after creation
- `retrospective-learning` - Learn from skill usage patterns

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Skill won't upload | Check SKILL.md naming (case-sensitive), YAML delimiters, kebab-case name |
| Doesn't trigger | Add more trigger phrases to description, include WHAT + WHEN pattern |
| Triggers too often | Add negative triggers, be more specific, clarify scope |
| MCP calls fail | Verify connection, check auth, test MCP independently |
| Instructions not followed | Keep concise, put critical info at top, use explicit language |
