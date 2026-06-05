---
name: implementer:test Function
description: Comprehensive test generation with 95%+ coverage and business validation
prefix: implementer:test
version: 3.0
---

# implementer:test

**Generate comprehensive test suites** with 95%+ code coverage and business requirement validation.

## Inputs

```
implementer:test path="..."
```

- `path` (string, required) — Path to source code directory
- `framework` (string, optional) — Test framework (pytest, jest, junit5)
- `coverage_target` (number, optional) — Target coverage % (default: 95)

## Outputs

```
✓ tests/test_*.py             — Unit tests with AAA pattern
✓ tests/integration/          — Integration tests
✓ COVERAGE_REPORT.md          — Coverage analysis
✓ TEST_RESULTS.md             — Test execution results
```

## Example

```bash
implementer:test path=./src
```

**Output:**
- Unit tests (95%+ coverage)
- Integration tests
- Edge case testing
- Business requirement validation
- Coverage report

## Workflow

1. Analyze source code
2. Identify test scenarios
3. Generate unit tests (AAA pattern)
4. Generate integration tests
5. Add edge case coverage
6. Validate business requirements
7. Run tests and report coverage

## Related Functions

- `implementer:full` — Build + test + doc
- `implementer:build` — Code generation
- `quality:review` — Test quality review
