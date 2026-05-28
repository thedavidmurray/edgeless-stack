---

name: mcp-to-skill-proxy
description: >
  Convert MCP (Model Context Protocol) servers into Hermes skills with
  progressive disclosure. Wraps MCP tool calls in a skill interface so tool
  schemas only load when the skill is explicitly invoked, not at session start.
  Reduces context overhead by thousands of tokens per converted server. Supports
  stdio and SSE MCP transports. version: 1.0.0 author: Beau (Paperclip Agent)
  license: MIT metadata: tags: [mcp, skills, optimization, proxy,
  progressive-disclosure] tier: task-specific domain: devops color: cyan
  prerequisites: commands: [python3, uvx, node, npx] files:
  [~/.hermes/skills/devops/mcp-to-skill-proxy/mcp_skill_proxy.py]
metadata:
  tags: [mcp, skill, proxy, conversion]
  tier: task-specific
  domain: tooling
when_to_apply: >
  When converting an MCP server into a Hermes skill via the proxy pattern.
---
# MCP-to-Skill Proxy

Convert MCP servers into on-demand Hermes skills to eliminate upfront context overhead.

## Identity

An infrastructure automation skill that bridges the gap between MCP's eager-loading
architecture and Hermes' progressive skill disclosure. Acts as a translator between
MCP tool schemas and lazy-loaded skill interfaces.

## When to Use

- Converting an MCP server to a skill for progressive disclosure
- Reducing session startup context usage by 1000+ tokens per MCP server
- Wrapping stdio-based MCP servers (uvx, npx, node, python)
- Wrapping SSE-based MCP servers (HTTP endpoint)
- Building skill-based alternatives to native MCP integrations

## When NOT to Use

- MCP servers that MUST load at session start for core functionality
- Simple MCP servers with <3 tools (overhead not worth it)
- When native Hermes MCP support already handles lazy loading
- For one-off MCP interactions → use mcporter CLI directly

## Core Mission

Eliminate per-session MCP context overhead by converting eager-loading MCP servers
into lazy-loaded Hermes skills that only fetch tool schemas when explicitly invoked.

## Critical Rules

1. **ALWAYS preserve tool signatures** — inputs/outputs must match original MCP exactly
2. **NEVER remove MCP server requirements** — skill still needs same env vars/dependencies
3. **MUST validate tool parity** — same inputs/outputs after conversion
4. **MUST measure token reduction** — document before/after context usage
5. **ALWAYS use subprocess isolation** — don't import MCP modules directly

## Instructions

### Step 1: Analyze MCP Server Configuration

From `.mcp.json`, identify candidate servers:

```bash
# High-value targets (many tools or rarely used)
- supadata      → 5+ tools, rarely used per session
- twozero_td    → TouchDesigner, niche use
- tradingview   → Trading tools, specialized
- chroma        → Vector DB, large schema

# Low-value (skip for now)
- fetch         → Simple, 1 tool
- paperclip     → Core infrastructure, always needed
```

### Step 2: Create Skill Directory

```bash
mkdir -p ~/.hermes/skills/{category}/{skill-name}
```

Category selection:
- `media` → supadata (YouTube/TikTok/Instagram)
- `creative` → twozero_td (TouchDesigner)
- `research` → perplexity-mcp (search)
- `trading` → tradingview (market data)

### Step 3: Generate Skill Files

Use the proxy generator:

```bash
python3 ~/.hermes/skills/devops/mcp-to-skill-proxy/mcp_skill_proxy.py generate \
  --mcp-name supadata \
  --category media \
  --output-dir ~/.hermes/skills/media/supadata-skill
```

This creates:
```
supadata-skill/
├── SKILL.md              # Skill interface
├── proxy.py              # MCP bridge implementation
└── manifest.json         # Tool schema cache (generated)
```

### Step 4: Configure Lazy Loading

In `SKILL.md` frontmatter, set:
```yaml
metadata:
  lazy_load: true          # Signal to Hermes: defer loading
  mcp_source: supadata     # Original MCP server name
```

### Step 5: Validate Tool Parity

Test that skill tools match MCP tools exactly:

```bash
python3 ~/.hermes/skills/devops/mcp-to-skill-proxy/mcp_skill_proxy.py validate \
  --mcp-name supadata \
  --skill-dir ~/.hermes/skills/media/supadata-skill
```

### Step 6: Update MCP Configuration

Disable original MCP server in `.mcp.json`:
```json
{
  "mcpServers": {
    "supadata": {
      "disabled": true,  // ← Add this
      ...
    }
  }
}
```

### Step 7: Measure Context Reduction

Document token savings:

```bash
# Before: Check CLAUDE.md or session init logs
# After: Verify skill loads only on `skill_view('supadata-skill')`

Expected savings per server:
- supadata: ~800-1200 tokens
- twozero_td: ~600-900 tokens
- tradingview: ~500-700 tokens
- chroma: ~2000-4000 tokens (large schema)
```

## Deliverables

| Output | Location | Description |
|--------|----------|-------------|
| Proxy script | `~/.hermes/skills/devops/mcp-to-skill-proxy/mcp_skill_proxy.py` | Core bridge implementation |
| Skill template | `~/.hermes/skills/devops/mcp-to-skill-proxy/templates/skill.md.j2` | SKILL.md Jinja2 template |
| Generated skill | `~/.hermes/skills/{category}/{skill-name}/` | Converted MCP-as-skill |
| Validation report | `mcp-skill-parity-report.json` | Tool parity check results |
| Token audit | `docs/mcp-skill-token-savings.md` | Before/after context usage |

## Success Metrics

| Metric | Target |
|--------|--------|
| Tool parity | 100% — all MCP tools available in skill |
| Context reduction | ≥800 tokens saved per converted server |
| Load time | <500ms from skill invocation to tool availability |
| Functionality | Zero regression — all tools work identically |
| Coverage | 2+ MCP servers converted as proof of concept |

## Cross-References

- Native MCP support → `mcporter` CLI for ad-hoc MCP calls
- Skill creation standards → `skill-creator` skill
- Original MCP config → `.mcp.json` in project root

## Implementation Pattern

The proxy uses subprocess-based MCP communication to maintain isolation:

```python
# Lazy loading: schema only fetched when skill_view() called
# NOT at Hermes session start

class MCPSkillProxy:
    def __init__(self, mcp_config):
        self.config = mcp_config
        self._schema = None  # ← Lazy: not loaded yet
    
    def get_tools(self):
        if self._schema is None:
            self._schema = self._fetch_mcp_schema()
        return self._schema
    
    def _fetch_mcp_schema(self):
        # Spawn MCP server, request tool list via stdio/SSE
        # Return structured tool definitions
        pass
```

## Memory

- Each converted MCP server should document original server name in `mcp_source` metadata
- Track token savings per server in `docs/mcp-skill-token-savings.md`
- Maintain parity report for validation regressions
