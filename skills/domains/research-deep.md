---
name: research-deep
description: >
  Conducts thorough research and analysis with multi-step investigation.
  Use when researching complex topics, investigating issues, or exploring
  questions requiring multiple sources.
metadata:
  tags: [research, analysis, investigation, web-search, deep-dive, synthesis]
  tier: task-specific
  domain: knowledge
when_to_apply: >
  When researching a complex topic requiring multi-step investigation,
  web search, and synthesis across sources
---

# Research Deep Skill

## Overview

Conduct thorough research and analysis using multi-step investigation
and web search integration.

## Trigger

- **Command**: `/research`
- **Keywords**: research, analyze, investigate, explore, understand, deep dive

## Research Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH WORKFLOW                         │
├─────────────────────────────────────────────────────────────┤
│  1. Initial Analysis    ->  Understand the problem          │
│  2. Memory Search       ->  Check existing knowledge        │
│  3. Web Research         ->  Current information            │
│  4. Code Analysis       ->  Codebase-specific insights      │
│  5. Synthesis           ->  Combine all findings            │
└─────────────────────────────────────────────────────────────┘
```

## Search Query Rules

<!-- CUSTOMIZE: Adapt to your search tools -->

1. Never include years in search queries -- use date filters instead
2. Never include relative-time words (latest, recent, current) -- use date filters
3. Decompose broad queries into multiple specific facets with proper nouns

## Research Patterns

### Pattern 1: Quick Lookup
```
/research "what is asyncio" --mode quick
```
- 1-2 steps
- Memory search only
- < 30 seconds

### Pattern 2: Standard Research
```
/research "best practices for Python error handling"
```
- 3-4 steps
- Memory + web search
- ~2 minutes

### Pattern 3: Deep Investigation
```
/research "architectural patterns for microservices" --mode thorough
```
- 5+ steps
- All sources
- Full synthesis
- ~5 minutes

## Tools

<!-- CUSTOMIZE: Replace with your available tools.
     Common options:
     - Perplexity API (web search)
     - WebFetch/WebSearch (built-in)
     - ChromaDB queries (memory search)
     - Code analysis tools
-->

### Primary
- Multi-step reasoning tool (thinkdeep pattern)
- Web search API

### Supporting
- Code analysis
- Memory/vector store search
- Brainstorming tools

## Output Format

```markdown
## Research: [Topic]

### Summary
[2-3 sentence overview]

### Key Findings
1. Finding one
2. Finding two
3. Finding three

### Details
[Detailed analysis by area]

### Recommendations
- Recommendation 1
- Recommendation 2

### Sources
- [Source 1](link)
- [Source 2](link)

### Confidence
[exploring|low|medium|high|very_high|certain]
```

## Integration with Memory

Research results can be saved to your vector store for future retrieval:

```python
# CUSTOMIZE: Your vector store client
store.add_documents(
    collection="research_results",
    documents=["research findings..."],
    ids=["research_YYYYMMDD_topic"],
    metadata=[{"topic": "...", "date": "..."}]
)
```

## Related Skills

- `memory-system` -- Load context before research
- `content-research-writer` -- Turn research into articles
- `retrospective-learning` -- Persist research insights
