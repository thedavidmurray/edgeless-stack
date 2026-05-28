---

name: content-research-writer
description: >
  Writing partner for research, outlining, drafting, and refinement.
  Transforms writing from solo effort to collaborative partnership with
  research, citations, hook improvement, and section-by-section feedback.
metadata:
  tags: [writing, research, blog, articles, newsletter, outlining, drafting]
  tier: task-specific
  domain: knowledge
  extends: research-deep
when_to_apply: >
  When writing blog posts, articles, or newsletters that require research,
  outlining, and collaborative refinement
---
# Content Research Writer

Acts as your writing partner for blog posts, articles, newsletters, and
documentation. Helps research, outline, draft, and refine content while
maintaining your unique voice.

## Trigger

- **Command**: `/write` or `/content-writer`
- **Keywords**: write article, blog post, research and write, outline, draft

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    WRITING WORKFLOW                          │
├─────────────────────────────────────────────────────────────┤
│  1. Collaborative Outline  ->  Structure ideas              │
│  2. Research + Citations   ->  Find sources, add refs       │
│  3. Hook Improvement       ->  Strengthen opening           │
│  4. Section Feedback       ->  Review as you write          │
│  5. Voice Preservation     ->  Maintain writer's style      │
│  6. Final Polish           ->  Comprehensive review         │
└─────────────────────────────────────────────────────────────┘
```

## When to Use

- Writing blog posts, articles, newsletters
- Creating educational content or tutorials
- Drafting thought leadership pieces
- Researching and writing case studies
- Technical documentation with sources

## Key Features

### 1. Collaborative Outlining
- Hook + introduction structure
- Main sections with key points
- Research to-do list
- Iterative refinement

### 2. Research Assistance
Leverages `/research` skill:
- Find relevant information
- Extract key facts, quotes, data
- Add citations in requested format
- Verify sources

### 3. Hook Improvement
Analyze and strengthen openings:
- What works / what doesn't
- Multiple alternative hooks
- Emotional impact analysis
- Audience alignment check

### 4. Section-by-Section Feedback
Real-time review as you write:
- Strengths identification
- Clarity improvements
- Flow suggestions
- Evidence gaps
- Style consistency

### 5. Voice Preservation
Maintain writer's unique style:
- Learn from existing samples
- Suggest, don't replace
- Match tone consistently
- Respect writer's choices

### 6. Citation Management
Handle references based on preference:
- Inline citations: `(Author, Year)`
- Numbered: `[1]`
- Footnotes: `^1`

## Instructions for the Agent

When user requests writing assistance:

1. **Understand the Project** -- Topic, audience, length, goal, style
2. **Collaborative Outlining** -- Identify research gaps, iterate
3. **Conduct Research** -- Use research skill, find credible sources
4. **Improve Hooks** -- Provide 3 alternatives with rationale
5. **Section-by-Section Feedback** -- Clarity, flow, evidence, style
6. **Preserve Voice** -- Suggest options, don't dictate
7. **Citation Management** -- Maintain running citations list
8. **Final Review** -- Overall assessment, pre-publish checklist

## Writing Workflows

### Blog Post
1. Outline together -> 2. Research -> 3. Write intro (feedback) -> 4. Body sections (feedback each) -> 5. Conclusion -> 6. Polish

### Newsletter
1. Hook ideas -> 2. Quick outline -> 3. Draft -> 4. Clarity review -> 5. Quick polish

### Technical Tutorial
1. Outline steps -> 2. Code examples -> 3. Explanations -> 4. Test instructions -> 5. Troubleshooting -> 6. Accuracy check

### Thought Leadership
1. Unique angle -> 2. Research perspectives -> 3. Develop thesis -> 4. Write with POV -> 5. Evidence -> 6. Compelling conclusion

## File Organization

<!-- CUSTOMIZE: Set your writing projects directory -->

```
writing/article-name/
├── outline.md
├── research.md
├── draft-v1.md
├── draft-v2.md
├── final.md
├── feedback.md
└── sources/
```

## Pro Tips

1. Work one section at a time for incremental feedback
2. Save research separately from drafts
3. Version your drafts: draft-v1.md, draft-v2.md
4. Read aloud to identify clunky sentences
5. Set deadlines to maintain momentum

## Related Skills

- `research-deep` -- Deep research and analysis
- `memory-system` -- Access previous writing for voice consistency
