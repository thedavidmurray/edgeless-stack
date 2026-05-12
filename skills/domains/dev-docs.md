---
name: dev-docs
description: Generates development documentation for code, APIs, and systems with consistent formatting. This skill should be used when creating READMEs, API docs, architecture records, or inline documentation.
metadata:
  tags:
  - documentation
  - readme
  - api-docs
  - architecture
  - developer-docs
  tier: general
  domain: product
when_to_apply: When generating README files, API documentation, architecture decision records, or inline code documentation
---
# Dev Docs Skill

## Overview
Generate development documentation for code, APIs, and systems with consistent formatting and comprehensive coverage.

## Trigger
- **Command**: `/dev-docs`
- **Keywords**: document, documentation, readme, api docs, generate docs

## Documentation Types

```
┌─────────────────────────────────────────────────────────────┐
│                   DOCUMENTATION TYPES                        │
├───────────────┬─────────────────────────────────────────────┤
│   code        │  Inline docs, docstrings, type hints        │
│   api         │  API reference, endpoints, schemas          │
│   readme      │  Project README with usage examples         │
│   guide       │  How-to guides and tutorials                │
│   arch        │  Architecture decision records (ADRs)       │
└───────────────┴─────────────────────────────────────────────┘
```

## Tools Used

### Primary: zen-mcp docgen
```
mcp__zen__docgen(
    step="Documenting module...",
    step_number=N,
    total_steps=M,
    next_step_required=true/false,
    findings="Documentation analysis...",
    document_complexity=true,
    document_flow=true,
    update_existing=true,
    comments_on_complex_logic=true,
    num_files_documented=X,
    total_files_to_document=Y
)
```

### Supporting Tools
- `mcp__zen__analyze` - Code structure analysis
- `LSP` - Symbol extraction and code intelligence

## Documentation Templates

### README Template
```markdown
# Project Name

Brief description.

## Quick Start

```bash
# Installation
pip install project-name

# Usage
project-name --help
```

## Features

- Feature 1
- Feature 2

## Documentation

- [API Reference](docs/api.md)
- [User Guide](docs/guide.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License
```

### API Documentation Template
```markdown
# API Reference

## Endpoints

### GET /api/resource

Description.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| id   | int  | Yes      | Resource ID |

**Response:**
```json
{
  "id": 1,
  "name": "example"
}
```

**Errors:**
| Code | Description |
|------|-------------|
| 404  | Not found   |
```

### Function Documentation Template
```markdown
## function_name

Brief description.

### Signature

```python
def function_name(param1: Type1, param2: Type2 = default) -> ReturnType:
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| param1 | Type1 | - | Description |
| param2 | Type2 | default | Description |

### Returns

`ReturnType` - Description of return value.

### Raises

- `ValueError` - When condition
- `TypeError` - When condition

### Example

```python
result = function_name("value", param2=123)
```

### Complexity

- Time: O(n)
- Space: O(1)
```

## Documentation Styles

### Brief
- Function signature
- One-line description
- Basic example

### Detailed
- Full parameter docs
- Return value docs
- Exception docs
- Examples

### Comprehensive
- Everything above
- Complexity analysis
- Call flow
- Related functions
- Edge cases

## Output Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| Markdown | .md | GitHub, general |
| reStructuredText | .rst | Sphinx, Python |
| HTML | .html | Standalone docs |

## Integration with Obsidian Vault

Documentation can be linked to vault:
```
<your-vault>/Knowledge/
├── API/
│   └── [generated-api-docs].md
├── Code/
│   └── [code-documentation].md
└── Guides/
    └── [how-to-guides].md
```

## Best Practices

1. **Keep docs close to code** - Update when code changes
2. **Use type hints** - Self-documenting code
3. **Include examples** - Show, don't just tell
4. **Document edge cases** - What breaks?
5. **Version docs** - Match code versions

## Related Skills
- `capture-state` - Capture context for docs
- `research-deep` - Research documentation patterns
