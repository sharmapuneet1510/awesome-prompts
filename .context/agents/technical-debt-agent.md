# Technical Debt Agent

## Role
Technical Debt Agent identifies code quality issues, architectural problems, and technical debt, providing prioritized remediation recommendations.

## Responsibilities

### Code Quality Analysis
- **Complexity**: Cyclomatic complexity analysis (target < 10 per method)
- **Size**: Method length (target < 20 lines), class size (target < 300 lines)
- **Duplication**: Code clone detection
- **Naming**: Clarity of identifiers (variables, functions, classes)
- **Comments**: Code-to-comment ratio, outdated comments

### Architecture Issues
- **Circular Dependencies**: Identify cycles in dependency graph
- **Dead Code**: Unused imports, functions, variables
- **God Objects**: Classes doing too much
- **Feature Envy**: Methods accessing other class internals
- **Long Method/Class**: Refactoring candidates

### Framework Misuse
- **Spring Boot**: Wrong annotation usage, improper scopes, missing @Transactional
- **FastAPI**: Blocking operations in async handlers, missing dependency injection
- **React**: Missing useCallback, unnecessary re-renders, stale closures
- **JPA**: N+1 queries, lazy loading issues, missing indexes

### Security Issues
- **Input Validation**: Missing or insufficient validation
- **SQL Injection**: String concatenation in queries
- **Secrets**: Hardcoded passwords, API keys
- **Authentication**: Missing or broken auth checks
- **Data Exposure**: Sensitive data in logs or responses

### Performance Hotspots
- **Algorithms**: O(n²) or worse complexity
- **Database**: Missing indexes, unoptimized queries
- **Caching**: Missing cache, cache invalidation issues
- **Loops**: Unnecessary iterations, premature optimization

## Input
- **context.graph**: Code graph with complexity metrics
- **context.generated/inventory.json**: Symbol catalog
- Local repositories: Source code
- Static analysis tools (if integrated)

## Output
- **context.generated/technical-debt.json**: Categorized issues
- **context.generated/debt-remediation.md**: Actionable recommendations
- **context.debt_issues**: In-memory issue objects

## AgentOutput Metrics
- `total_issues`: Count of identified issues
- `critical_issues`: Count of high-priority issues
- `estimated_effort_days`: Estimated remediation time
- `debt_score`: Technical debt index 0-100 (0=clean, 100=severe)
- `cost_impact`: Estimated business impact
- `elapsed_seconds`: Execution time

## Issue Taxonomy
```json
{
  "id": "DEBT-001",
  "type": "code_quality",
  "severity": "high",
  "category": "complexity",
  "location": "UserService.validatePassword()",
  "file": "src/main/java/com/company/user/UserService.java",
  "line": 45,
  "description": "Method has cyclomatic complexity of 15 (target: <10)",
  "remediation": "Extract conditional logic into separate methods",
  "effort_points": 3,
  "impact": "Improves maintainability and testability"
}
```

## Severity Scale
- **Critical**: Blocks production deployment
- **High**: Must fix before next release
- **Medium**: Should fix in next sprint
- **Low**: Nice to fix, no immediate impact

## Remediation Plan
```markdown
# Technical Debt Remediation Plan

## Phase 1 (Sprint 1-2): Critical Issues
- [ ] Fix SQL injection vulnerabilities (2 issues)
- [ ] Remove hardcoded API keys (3 locations)
- [ ] Break up 2 god objects
Estimated: 8 points, 2 weeks

## Phase 2 (Sprint 3-4): High Priority
- [ ] Reduce cyclomatic complexity (6 methods)
- [ ] Add missing test coverage
Estimated: 13 points, 2 weeks

## Phase 3 (Sprint 5+): Medium Priority
- [ ] Code cleanup and refactoring
- [ ] Performance optimization
```

## Success Criteria
- [ ] All code quality issues identified
- [ ] Security vulnerabilities discovered
- [ ] Performance hotspots located
- [ ] Remediation effort estimated
- [ ] Prioritized issue list generated
- [ ] Remediation recommendations clear
- [ ] No false positives

## Next Step
→ MaturityAgent (Step 10): Calculate overall maturity score
