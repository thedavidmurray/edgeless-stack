---
name: prompt-engineering
description: Use this skill when writing commands, hooks, skills for Agent, or prompts for sub-agents or any other LLM interaction, including optimizing prompts, improving LLM outputs, or designing production prompt templates.
metadata:
  tags:
  - prompt-engineering
  - llm
  - agents
  - instructions
  - optimization
  tier: task-specific
  domain: product
when_to_apply: When writing agent instructions, skill prompts, hooks, or any LLM-facing prompt that needs optimization
---
# Prompt Engineering Patterns

Advanced prompt engineering techniques to maximize LLM performance, reliability, and controllability.

## When to Use

- Writing agent instructions, hooks, or skills
- Creating prompts for sub-agents or external LLM calls
- Optimizing existing prompts for better performance
- Designing production prompt templates
- Improving consistency and reliability of LLM outputs
- Debugging unexpected LLM behavior

## Core Capabilities

### 1. Few-Shot Learning

Teach the model by showing examples instead of explaining rules. Include 2-5 input-output pairs that demonstrate the desired behavior.

**When to use**: Need consistent formatting, specific reasoning patterns, or handling of edge cases.

**Token balance**: More examples improve accuracy but consume tokens—balance based on task complexity.

### 2. Chain-of-Thought Prompting

Request step-by-step reasoning before the final answer.

**Techniques**:
- Zero-shot: Add "Let's think step by step"
- Few-shot: Include example reasoning traces

**Use for**: Complex problems requiring multi-step logic, debugging, or transparency in decision-making.

### 3. Prompt Optimization

Systematically improve prompts through testing and refinement.

**Process**:
1. Start simple
2. Measure performance
3. Iterate based on failures
4. Test edge cases
5. Version and document

### 4. Template Systems

Build reusable prompt structures with variables, conditional sections, and modular components.

**Benefits**:
- Consistency across use cases
- Easy A/B testing
- Version control
- Maintainability

### 5. System Prompt Design

Set global behavior and constraints that persist across the conversation.

**Include**:
- Role definition
- Global constraints
- Output format requirements
- Error handling instructions

## Key Patterns

### Progressive Disclosure
Start with simple prompts, add complexity only when needed. Avoid over-engineering on first iteration.

### Instruction Hierarchy
```
[System Context] → [Task Instruction] → [Examples] → [Input Data] → [Output Format]
```

Follow this order for maximum clarity and control.

### Error Recovery
Build prompts that gracefully handle failures:
- Include fallback instructions
- Request confidence scores
- Define partial success criteria
- Specify what to do on uncertainty

## Persuasion Principles for Agent Communication

LLMs respond to the same persuasion principles as humans. See `references/persuasion-principles.md` for detailed examples and applications.

**Quick Reference**:
1. **Authority** - Imperative language ("YOU MUST", "Never", "Always")
2. **Commitment** - Require announcements, force explicit choices
3. **Scarcity** - Time-bound requirements, sequential dependencies
4. **Social Proof** - Universal patterns, failure mode warnings
5. **Unity** - Collaborative language, shared goals
6. **Reciprocity** - Use sparingly
7. **Liking** - Avoid for compliance (creates sycophancy)

## Best Practices

1. **Be Specific** - Vague prompts produce inconsistent results
2. **Show, Don't Tell** - Examples beat descriptions
3. **Test Extensively** - Evaluate on diverse inputs
4. **Iterate Rapidly** - Small changes have large impacts
5. **Monitor Performance** - Track metrics in production
6. **Version Control** - Treat prompts as code
7. **Document Intent** - Explain why prompts are structured this way

## The Conciseness Rule

**The context window is a public good.**

Only add context Claude doesn't already have. Challenge each piece: "Does Claude really need this explanation?"

**Before adding**:
- Is this obvious to an LLM with training on the internet?
- Would a human expert need this explanation?
- Does this change behavior or just add noise?

**When to add**:
- Company-specific context
- Non-obvious constraints
- Edge cases and failure modes
- Behavioral requirements that differ from defaults

## Common Anti-Patterns

### Over-Explanation
Don't explain basic concepts. LLMs already know them.

**Bad**: "A function is a reusable block of code that performs a specific task..."
**Good**: "Write a function to validate email addresses"

### Politeness Overhead
LLMs don't need motivation or encouragement.

**Bad**: "Please try your best to create a great solution..."
**Good**: "Create a solution that..."

### Redundant Instructions
Don't repeat yourself. LLMs have perfect recall within context.

**Bad**: Multiple mentions of the same constraint
**Good**: State once, reference as needed

### Anthropomorphizing
Don't treat LLMs as human collaborators needing emotional support.

**Bad**: "I know this is challenging, but..."
**Good**: [Just state the requirement]

## Output Format Specification

Always specify expected output format:

```markdown
## Output Format

Return a JSON object with:
- `analysis`: string (2-3 sentences)
- `recommendations`: array of strings
- `confidence`: number (0-1)

Example:
{
  "analysis": "...",
  "recommendations": ["...", "..."],
  "confidence": 0.85
}
```

## Related Skills

- `skill-creator` - Apply these patterns when creating new skills
- `dev-docs` - Document prompting strategies
- `research-deep` - Use for researching prompt engineering techniques

## References

- `references/persuasion-principles.md` - Detailed persuasion principles with examples
