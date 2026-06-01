# Maturity Agent

## Role
Maturity Agent calculates an overall maturity score (0-100) across multiple dimensions, enabling the orchestrator to determine if the analysis is sufficiently mature or requires iteration.

## Responsibilities

### Maturity Dimensions

#### 1. Architecture Clarity (0-100)
- **Criteria**: Clear separation of concerns, documented patterns
- **Sources**: C4 diagrams, architecture.md, circular dependencies
- **Scoring**: 100 points if architecture is clear, -20 per major circular dep, -10 for unclear boundaries
- **Target**: 80+

#### 2. Documentation Completeness (0-100)
- **Criteria**: All components documented, APIs described, flows explained
- **Sources**: Generated markdown files, docstrings, comments
- **Scoring**: 80% doc coverage = 80 points, +20 if all APIs documented
- **Target**: 85+

#### 3. Test Coverage (0-100)
- **Criteria**: Sufficient test coverage, good test quality
- **Sources**: Test analysis results
- **Scoring**: Coverage % directly = score, +bonus for test quality
- **Target**: 80+

#### 4. Code Quality (0-100)
- **Criteria**: Low complexity, good naming, minimal duplication
- **Sources**: Technical debt analysis
- **Scoring**: 100 - (issues × severity_weight)
- **Target**: 75+

#### 5. Technical Debt (0-100)
- **Criteria**: Minimal security issues, performance hotspots, architecture debt
- **Sources**: Technical debt report
- **Scoring**: 100 - (debt_score × 0.5)
- **Target**: 75+

#### 6. Framework Adoption (0-100)
- **Criteria**: Consistent framework usage, best practices followed
- **Sources**: Code patterns analysis
- **Scoring**: Consistency % × 100
- **Target**: 85+

### Scoring Algorithm
```python
def calculate_maturity(dimensions: Dict[str, float]) -> int:
    weights = {
        "architecture": 0.20,
        "documentation": 0.20,
        "tests": 0.20,
        "code_quality": 0.15,
        "technical_debt": 0.15,
        "framework": 0.10
    }
    
    score = sum(dimensions[d] * weights[d] for d in weights)
    return min(100, max(0, int(score)))
```

## Input
- **All previous agent outputs**: Reports, metrics, analysis results
- **maturity_config**: Target scores and weights
- **context.reports**: All agent reports

## Output
- **context.generated/maturity-report.json**: Detailed scoring and breakdown
- **context.generated/maturity.md**: Executive summary
- **context.maturity_score**: Overall score integer 0-100

## AgentOutput Metrics
- `overall_score`: Weighted maturity score 0-100
- `dimension_scores`: Dict of individual dimension scores
- `strengths`: List of strong areas
- `weaknesses`: List of areas needing improvement
- `recommendations`: Recommendations for improvement
- `elapsed_seconds`: Execution time

## Maturity Score Output
```json
{
  "overall_score": 72,
  "target_score": 80,
  "status": "needs_iteration",
  "dimensions": {
    "architecture": 85,
    "documentation": 70,
    "tests": 65,
    "code_quality": 75,
    "technical_debt": 68,
    "framework": 80
  },
  "strengths": [
    "Clear architecture with well-documented C4 diagrams",
    "Consistent Spring Boot framework usage"
  ],
  "weaknesses": [
    "Test coverage at 65%, target is 80%",
    "Missing documentation for 30% of public APIs"
  ],
  "recommendations": [
    "Add 15% more test coverage (focus on UserService, PaymentService)",
    "Document remaining public APIs (8 endpoints)",
    "Refactor 3 complex methods with >15 cyclomatic complexity"
  ]
}
```

## Maturity Levels

| Score | Level | Action |
|-------|-------|--------|
| 90-100 | Excellent | Production-ready, minimal issues |
| 80-89 | Good | Ready with minor improvements |
| 70-79 | Fair | Needs improvement before release |
| 60-69 | Poor | Significant issues, address before release |
| 0-59 | Critical | Major gaps, may not be deployable |

## Orchestrator Integration
- If score ≥ target: **PASS** → Generate final report
- If score < target AND iteration < max: **RETRY** → Run from FlowAnalysisAgent (Step 4)
- If score < target AND iteration ≥ max: **WARN** → Generate report with warnings

## Success Criteria
- [ ] All dimensions scored
- [ ] Scoring algorithm consistent
- [ ] Recommendations actionable
- [ ] Score reflects true maturity
- [ ] Comparison with target clear
- [ ] Iteration decision correct
- [ ] Executive summary generated

## Final Step
→ Orchestrator completes pipeline
→ Generate final reports
→ Export agent definitions to .context/agents/
