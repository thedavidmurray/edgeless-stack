---
name: test-runner
description: Runs tests, generates test scaffolds, and manages test coverage with auto-detection of project test framework. This skill should be used when running tests, generating test files, or checking coverage.
metadata:
  tags:
  - testing
  - test-runner
  - coverage
  - pytest
  - jest
  - vitest
  tier: general
  domain: product
when_to_apply: When running tests, generating test scaffolds, or checking coverage across any project test framework
---
# Test Runner Skill

## Overview
Run tests, generate test scaffolds, and manage test coverage. Auto-detects project test framework.

## Trigger
- **Command**: `/test`
- **Keywords**: test, tests, run tests, coverage, unittest, pytest, jest, vitest

## Test Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                     TEST WORKFLOW                            │
├─────────────────────────────────────────────────────────────┤
│  1. Detect Framework  →  jest, vitest, pytest, mocha        │
│  2. Parse Arguments   →  scope, options, patterns           │
│  3. Run Tests         →  Execute with appropriate runner    │
│  4. Collect Results   →  Parse output, failures, coverage   │
│  5. Generate Report   →  Summary with recommendations       │
└─────────────────────────────────────────────────────────────┘
```

## Framework Detection

```javascript
// Auto-detect test framework
function detectFramework() {
  const pkg = readPackageJson();
  
  // Check scripts first
  if (pkg?.scripts?.test) {
    if (pkg.scripts.test.includes('jest')) return 'jest';
    if (pkg.scripts.test.includes('vitest')) return 'vitest';
    if (pkg.scripts.test.includes('mocha')) return 'mocha';
    if (pkg.scripts.test.includes('ava')) return 'ava';
  }
  
  // Check devDependencies
  const deps = { ...pkg?.devDependencies, ...pkg?.dependencies };
  if (deps['jest']) return 'jest';
  if (deps['vitest']) return 'vitest';
  if (deps['mocha']) return 'mocha';
  
  // Python checks
  if (fileExists('pytest.ini') || fileExists('pyproject.toml')) return 'pytest';
  if (fileExists('setup.py')) return 'unittest';
  
  return null;
}
```

## Commands by Framework

### Jest (Node.js)
```bash
# All tests
npx jest

# Specific file
npx jest path/to/file.test.js

# Pattern match
npx jest --testNamePattern="should handle"

# Coverage
npx jest --coverage

# Watch mode
npx jest --watch

# CI mode
npx jest --ci --coverage --maxWorkers=2
```

### Vitest (Node.js)
```bash
# All tests
npx vitest run

# Watch mode
npx vitest

# Coverage
npx vitest run --coverage

# Specific file
npx vitest run src/utils.test.ts
```

### Pytest (Python)
```bash
# All tests
pytest

# Verbose
pytest -v

# Specific file
pytest tests/test_module.py

# Pattern match
pytest -k "test_user"

# Coverage
pytest --cov=src --cov-report=term-missing

# Stop on first failure
pytest -x
```

## Test Generation

When `/test generate <file>` is invoked:

### Step 1: Analyze Source File
```
Use zen-mcp testgen tool:
mcp__zen__testgen(
    step="Analyzing source file for test generation",
    relevant_files=[target_file],
    model="o3",
    thinking_mode="medium"
)
```

### Step 2: Identify Test Cases
- All exported functions/classes
- Edge cases (null, empty, boundary values)
- Error scenarios (invalid input, exceptions)
- Async behavior (if applicable)
- Integration points (mocks needed)

### Step 3: Generate Test File

**JavaScript/TypeScript pattern:**
```javascript
import { describe, it, expect, vi } from 'vitest';
import { functionName } from '../src/module';

describe('functionName', () => {
  it('should handle normal input', () => {
    expect(functionName('input')).toBe('expected');
  });

  it('should handle edge case: empty input', () => {
    expect(functionName('')).toBe('');
  });

  it('should throw on invalid input', () => {
    expect(() => functionName(null)).toThrow();
  });
});
```

**Python pattern:**
```python
import pytest
from src.module import function_name

class TestFunctionName:
    def test_normal_input(self):
        assert function_name('input') == 'expected'
    
    def test_empty_input(self):
        assert function_name('') == ''
    
    def test_invalid_input_raises(self):
        with pytest.raises(ValueError):
            function_name(None)
```

## Coverage Report Format

```
┌────────────────────────────────────────────────────────────┐
│                    COVERAGE REPORT                          │
├────────────────────────────────────────────────────────────┤
│ Overall Coverage: 78.5%                                     │
├──────────────────┬──────────┬──────────┬──────────┬────────┤
│ File             │ Stmts    │ Branch   │ Funcs    │ Lines  │
├──────────────────┼──────────┼──────────┼──────────┼────────┤
│ src/utils.js     │   92%    │   85%    │  100%    │   92%  │
│ src/api.js       │   67%    │   50%    │   80%    │   67%  │
│ src/helpers.js   │   45%    │   30%    │   60%    │   45%  │ ⚠️
├──────────────────┴──────────┴──────────┴──────────┴────────┤
│ Uncovered Lines:                                            │
│ - src/api.js: 45-52, 78-80                                 │
│ - src/helpers.js: 12-34, 67-89                             │
└────────────────────────────────────────────────────────────┘
```

## Integration Points

### With /precommit
```javascript
// precommit should auto-run tests
async function precommitHook() {
  const testResult = await runCommand('/test --ci --bail');
  if (testResult.exitCode !== 0) {
    return { blocked: true, reason: 'Tests failed' };
  }
}
```

### With /review
```javascript
// review should check test coverage for changed files
async function reviewHook(changedFiles) {
  const coverage = await runCommand('/test coverage --json');
  const uncovered = changedFiles.filter(f => coverage[f] < 80);
  if (uncovered.length) {
    warn(`Low coverage: ${uncovered.join(', ')}`);
  }
}
```

## Options Reference

| Option | Short | Description |
|--------|-------|-------------|
| `--watch` | `-w` | Re-run on file changes |
| `--coverage` | `-c` | Generate coverage report |
| `--verbose` | `-v` | Detailed output |
| `--bail` | `-b` | Stop on first failure |
| `--ci` | | CI-friendly mode |
| `--update-snapshots` | `-u` | Update snapshot tests |
| `--pattern <regex>` | `-p` | Filter by test name |

## Examples

```bash
/test                           # Run all tests
/test src/utils.js              # Test specific file
/test --coverage                # With coverage report
/test generate src/api.js       # Generate tests for file
/test "authentication" -v       # Verbose, pattern match
/test --watch                   # TDD watch mode
/test --ci --bail               # CI: fail fast
```

## Error Handling

| Error | Resolution |
|-------|------------|
| No framework detected | Suggest: `npm install -D jest` or `pip install pytest` |
| No tests found | Offer `/test generate` to create scaffolds |
| Tests timeout | Check for hanging async, suggest `--bail` |
| Coverage below threshold | Highlight uncovered files, suggest tests |
