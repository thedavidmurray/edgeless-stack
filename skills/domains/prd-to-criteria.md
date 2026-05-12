---
name: prd-to-criteria
description: >
  Transform Product Requirement Document acceptance criteria into machine-verifiable
  completion checks. Converts human-readable requirements like "API returns 200"
  into executable validation commands with pass/fail assertions for automated
  task verification and quality gates.
metadata:
  tags:
  - prd
  - criteria
  - verification
  - acceptance
  - requirements
  tier: task-specific
  domain: product
when_to_apply: When converting PRD acceptance criteria into machine-verifiable completion checks
---
# PRD-to-Criteria Generator

Transforms Product Requirement Document acceptance criteria into machine-verifiable completion criteria for the task verification system.

## Purpose

PRDs contain human-readable acceptance criteria like:
- "API returns 200 for valid requests"
- "Error messages are user-friendly"
- "Tests cover edge cases"

This skill converts them to machine-executable checks:
```yaml
completion_criteria:
  required:
    - command: "curl -s localhost:8000/api/user/1 -w '%{http_code}' | tail -1 | grep 200"
      description: "API returns 200 for valid requests"
```

## When to Use

- After writing or receiving a PRD
- When creating a new task from requirements
- When acceptance criteria exist but completion checks don't
- To ensure requirements are actually testable

## Usage

```bash
# Generate criteria from PRD file
/prd-to-criteria path/to/prd.md

# Generate and add to existing task file
/prd-to-criteria path/to/prd.md --add-to .backlog/tasks/task-150.md

# Preview without writing
/prd-to-criteria path/to/prd.md --dry-run

# Specify output format
/prd-to-criteria path/to/prd.md --format yaml
/prd-to-criteria path/to/prd.md --format markdown
```

## Input: PRD Format

The PRD should have an acceptance criteria section:

```markdown
## Acceptance Criteria

- [ ] User can create account with email/password
- [ ] API validates email format
- [ ] API returns 400 for invalid email
- [ ] API returns 201 for successful creation
- [ ] New user appears in database
- [ ] Welcome email is sent
```

Or structured format:

```markdown
## Acceptance Criteria

### Functional
1. User registration endpoint accepts POST /api/users
2. Valid registration returns 201 with user object
3. Invalid email returns 400 with error message

### Non-Functional
1. Registration completes in < 500ms
2. Passwords are hashed before storage
```

## Output: Completion Criteria

```yaml
completion_criteria:
  required:
    # From: "User registration endpoint accepts POST /api/users"
    - command: "curl -s -X POST localhost:8000/api/users -H 'Content-Type: application/json' -d '{\"email\":\"test@test.com\",\"password\":\"test123\"}' -w '%{http_code}' | tail -1 | grep -E '2[0-9]{2}'"
      description: "Registration endpoint accepts POST requests"
      timeout: 10

    # From: "Valid registration returns 201 with user object"
    - command: "curl -s -X POST localhost:8000/api/users -H 'Content-Type: application/json' -d '{\"email\":\"test2@test.com\",\"password\":\"test123\"}' -w '%{http_code}' | tail -1 | grep 201"
      description: "Valid registration returns 201"
      timeout: 10

    # From: "Invalid email returns 400 with error message"
    - command: "curl -s -X POST localhost:8000/api/users -H 'Content-Type: application/json' -d '{\"email\":\"invalid\",\"password\":\"test123\"}' -w '%{http_code}' | tail -1 | grep 400"
      description: "Invalid email returns 400"
      timeout: 10

    # From: "Tests cover edge cases"
    - command: "pytest tests/test_registration.py -v"
      description: "Registration tests pass"
      timeout: 120

  optional:
    # From: "Registration completes in < 500ms"
    - command: "curl -s -X POST localhost:8000/api/users -H 'Content-Type: application/json' -d '{\"email\":\"perf@test.com\",\"password\":\"test123\"}' -w '%{time_total}' -o /dev/null | awk '{if ($1 < 0.5) exit 0; else exit 1}'"
      description: "Registration completes in < 500ms"
      timeout: 10
```

## Transformation Rules

| Criterion Type | Generated Check |
|----------------|-----------------|
| "API returns XXX" | `curl` command checking status code |
| "File exists" | `file_exists` check |
| "Tests pass" | `pytest` or `npm test` command |
| "No errors/warnings" | Linting command with exit code check |
| "Output contains X" | `output_match` with regex |
| "Database has X" | SQL query via command |
| "Performance < Xms" | Timing command with threshold |

## Interactive Mode

For complex criteria, the skill will ask clarifying questions:

```
Criterion: "User receives confirmation email"

How should this be verified?
1. Check email service mock was called
2. Check email queue has message
3. Check test mailbox received email
4. Skip (mark as manual verification)

> 1

Generated:
- command: "pytest tests/test_email.py::test_confirmation_sent -v"
  description: "Confirmation email service called"
```

## Criteria That Can't Be Automated

Some criteria require manual verification:
- "UI is user-friendly"
- "Documentation is clear"
- "Performance feels snappy"

These are flagged as manual:

```yaml
# MANUAL VERIFICATION REQUIRED:
# - "UI is user-friendly" - Requires human judgment
# - "Documentation is clear" - Subjective assessment
```

## Implementation Steps

1. **Parse PRD** - Extract acceptance criteria section
2. **Classify Each Criterion** - API, file, test, performance, manual
3. **Generate Checks** - Transform to machine-verifiable commands
4. **Validate** - Ensure commands are syntactically correct
5. **Output** - YAML format ready for task frontmatter

## Example Workflow

```bash
# 1. You have a PRD with acceptance criteria
cat docs/prd-user-auth.md

# 2. Generate completion criteria
/prd-to-criteria docs/prd-user-auth.md --dry-run

# 3. Review generated criteria, adjust if needed

# 4. Add to task file
/prd-to-criteria docs/prd-user-auth.md --add-to .backlog/tasks/task-150.md

# 5. Verify task completion
/verify task-150
```

## Tips for Good PRDs

Write acceptance criteria that ARE verifiable:
- "API returns 200" (testable)
- "Response time < 100ms" (measurable)
- "Test coverage > 80%" (quantifiable)

Avoid criteria that AREN'T verifiable:
- "Code is clean" (subjective)
- "Users are happy" (unmeasurable)
- "Performance is good" (vague)

## Related Skills

- `/verify` - Run the generated criteria
- `/interview-mode` - Clarify requirements before generating
- `/test` - Run tests referenced in criteria

## Command Reference

Corresponds to `/prd-to-criteria` command.
