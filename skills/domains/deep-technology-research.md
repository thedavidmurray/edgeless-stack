---
name: deep-technology-research
description: >
  Deep research and comparative analysis of open-source repositories for
  technology selection and strategic decision-making
metadata:
  tags: [research, tech-evaluation, open-source, strategic-analysis]
  tier: task-specific
  domain: knowledge
when_to_apply: >
  When investigating a technology or comparing OSS repos for a strategic
  build/buy/switch decision.
---

# Deep Technology Research & Strategic Analysis

## Purpose

Perform comprehensive investigation of open-source repositories and technologies to support strategic build-vs-buy, continue-vs-switch, or enhancement decisions.

## When to Use

- Technology selection for critical infrastructure
- Evaluating alternatives to current systems
- Strategic architecture decisions with >2 week implementation time
- Understanding capability gaps in existing solutions
- Research for product strategy or competitive analysis

## Methodology

### Phase 1: Discovery (cast wide net)

1. **Multi-source search strategy**
   ```
   GitHub repository search (MCP)
   Web search for recent articles/arXiv papers
   Search code patterns (filename:x OR content:y)
   ```

2. **Screening criteria** (filter within 10 minutes)
   - Stars/forks indicate community adoption
   - Recent commits indicate maintenance
   - README clarity indicates author maturity
   - Test coverage visible in repo structure

3. **Expect API failures** and have fallbacks
   - GitHub search may fail (permissions, rate limits)
   - Web search may fail (auth issues)
   - Have terminal/git clone as backup

### Phase 2: Deep Inspection (2-4 candidates)

For each promising candidate:

1. **Repository structure analysis**
   ```
   List root files (README, package.json, requirements.txt)
   List src/ directory (architecture patterns)
   Identify entry points and core modules
   ```

2. **README deep read**
   - Architecture diagrams
   - Feature lists
   - Configuration requirements
   - Deployment patterns

3. **Source code sampling**
   - Core algorithm implementation (position_sizer.py, risk_manager.py)
   - Configuration schemas
   - Test coverage

4. **Dependency analysis**
   - package.json / requirements.txt / Cargo.toml
   - Estimate complexity by dependency count
   - Identify key framework choices

### Phase 3: Comparative Analysis

**Build capability matrix:**

| Capability | Current | Candidate A | Candidate B | Importance |
|------------|---------|-------------|-------------|------------|
| Feature X | ✓/✗ | ✓/✗ | ✓/✗ | Critical/High/Med |

**Key dimensions:**
- Feature parity (table checkmarks)
- Architecture complexity (lines of code, dependencies)
- Maturity (version, tests, production status)
- Risk factors (oracle protection, circuit breakers, etc.)
- Integration cost (language, runtime, existing investment)

### Phase 4: Strategic Options Framework

**Define 3-4 strategic options:**

1. **Enhance Current**
   - What to port/borrow
   - Keep existing value
   - Migration risk: Low

2. **Fork and Adapt**
   - Start from best candidate
   - Add missing features
   - Migration risk: Medium

3. **Hybrid Architecture**
   - Current as "X layer"
   - Candidate as "Y layer"
   - Migration risk: High complexity

4. **Switch Completely**
   - Abandon current
   - Full migration
   - Migration risk: High

**Decision criteria for recommendation:**
- Existing investment preservation
- Risk management (avoid losing working systems)
- Differentiation alignment (keep what makes you unique)
- Implementation timeline reality

### Phase 5: Implementation Roadmap

If recommendation is "Enhance":
```
Phase 1: Critical modules (urgent - 1-2 days)
Phase 2: High-value additions (2-3 days)
Phase 3: Nice-to-have (optional)
```

With specific file paths and integration approach.

## Output Format

**Dispatch to decision-maker should include:**

1. **Executive Summary** (3 bullets)
2. **Candidate Analysis** (1 paragraph each)
3. **Comparative Matrix** (markdown table)
4. **Strategic Options** (A/B/C/D with pros/cons)
5. **Critical Gaps** (in current system)
6. **Recommended Path** with reasoning
7. **Implementation Roadmap** (phased)

## Pitfalls to Avoid

- **Don't skip working systems**: If something is in production with real users/money, switching has hidden costs
- **Don't chase shiny**: Latest version != best choice. Maturity > novelty.
- **Watch for stubs**: README claims != implemented code. Check src/ exists and has substance.
- **Consider runtime fit**: Python module in TS ecosystem adds friction. Weigh carefully.
- **Document blockers**: Missing features that are "critical" vs "can add later"

## Example: Prediction Market Bot Research

**Discovery:**
- Searched: `polymarket trading bot kelly criterion`
- Found: 10+ repos, filtered to 4 mature candidates

**Key Finding:**
- Current system (Pamela/ElizaOS): Social features, web dashboard, but no Kelly sizing, no oracle protection
- JDDavenport (Python): Kelly criterion, risk management, edge sources -- but no social
- amorr42: Oracle protection (critical for prediction markets!), paper trading -- but BTC-only

**Strategic Insight:**
"Switch" would lose working web dashboard and $250 funded wallet. "Enhance" by porting specific Python modules to TypeScript preserves investment while closing critical gaps.

**Recommendation:**
Phase 1: Port risk_manager.py (circuit breakers)
Phase 2: Port position_sizer.py (Kelly criterion)
Phase 3: Add oracle protection (from amorr42)

## Tools Used

- `mcp_github_search_repositories`
- `mcp_github_get_file_contents` (multiple paths)
- `web_search` (for recent developments)
- `mcp_filesystem_write_file` (dispatch creation)

## Success Metrics

- Decision-maker has clear options with trade-offs
- Implementation path is phased and reversible
- Critical gaps are identified with specific file references
- Comparative matrix enables quick scanning
