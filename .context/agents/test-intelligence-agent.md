# Test Intelligence Agent

## Role
Test Intelligence Agent analyzes test coverage, test quality, and business validation, providing recommendations for improving test effectiveness and coverage gaps.

## Responsibilities

### Coverage Analysis
- Detect test files (pattern: test_*.py, *Test.java, *.spec.ts, etc.)
- Parse coverage reports (JaCoCo, Coverage.py, Istanbul, etc.)
- Calculate line, branch, and method coverage
- Identify coverage gaps by package/class
- Compute coverage trends

### Test Classification
- **Unit Tests**: Class-level, isolated dependencies
- **Integration Tests**: Multi-class, with real/stubbed dependencies
- **End-to-End Tests**: Full stack, external dependencies
- **Contract Tests**: API contract verification
- **Performance Tests**: Load, stress, throughput tests

### Test Quality Assessment
- **Naming Convention**: Tests follow givenXxx_whenYyy_thenZzz() pattern
- **AAA Pattern**: Arrange-Act-Assert structure
- **Assertions**: Sufficient assertions per test
- **Mocking**: Proper mocking vs. integration
- **Flakiness**: Identify potentially flaky tests

### Business Validation
- Map tests to business requirements/JIRA tickets
- Validate acceptance criteria coverage
- Identify untested business flows
- Risk assessment for untested areas
- Test-to-code ratio

## Input
- **context.graph**: Code graph with test references
- **context.generated/inventory.json**: Symbol catalog (test classes/methods)
- Local repositories: Test files
- Coverage reports (if available)
- JIRA integration (optional)

## Output
- **context.generated/test-report.json**: Coverage and quality metrics
- **context.generated/test-gaps.md**: Uncovered code and recommendations
- **context.test_quality**: Test quality scores by module

## AgentOutput Metrics
- `total_test_count`: Count of discovered tests
- `average_coverage`: Overall code coverage %
- `untested_symbols`: Count of untested classes/methods
- `quality_score`: Test quality 0-100
- `missing_business_tests`: Count of untested flows
- `elapsed_seconds`: Execution time

## Coverage Calculation
```
line_coverage = (lines_executed / total_lines) * 100
branch_coverage = (branches_executed / total_branches) * 100
method_coverage = (methods_tested / total_methods) * 100
```

## Test Quality Scoring
- **Naming**: 20 points (clear, descriptive names)
- **Structure**: 20 points (AAA pattern, clarity)
- **Assertions**: 20 points (sufficient, specific)
- **Isolation**: 20 points (proper mocking, no flakiness)
- **Coverage**: 20 points (targets critical code)

## Recommendations Engine
```json
{
  "module": "UserService",
  "coverage": 65,
  "target": 80,
  "gaps": [
    {
      "class": "UserService.validateEmail()",
      "status": "untested",
      "risk": "high",
      "recommendation": "Add unit tests for email validation"
    }
  ],
  "priority": "high"
}
```

## Success Criteria
- [ ] All test files discovered
- [ ] Coverage reports parsed
- [ ] Quality metrics computed
- [ ] Business flow mapping complete
- [ ] Recommendations generated
- [ ] Report generated in context.generated/
- [ ] No false positives in coverage

## Next Step
→ TechnicalDebtAgent (Step 9): Identify code quality issues and debt
