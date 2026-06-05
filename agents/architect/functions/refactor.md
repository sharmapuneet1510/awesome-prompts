---
name: architect:refactor Function
description: Brownfield migration planning - refactor monoliths, modernize legacy systems
prefix: architect:refactor
version: 3.0
---

# architect:refactor

**Plan brownfield refactoring** of existing systems: monolith-to-microservices, legacy modernization, tech stack upgrades.

## Inputs

```
architect:refactor path="..." [target_architecture="..."]
```

- `path` (string, required) — Path to existing codebase
- `target_architecture` (string, optional) — Target design (microservices, serverless, etc.)
- `constraints` (string, optional) — Business constraints (timeline, budget, team size)

## Outputs

```
✓ migration-plan.md           — Step-by-step refactoring phases
✓ dependency-graph.md         — Service dependency visualization
✓ rollback-strategy.md        — Rollback procedures for each phase
✓ risk-assessment.md          — Migration risks and mitigations
✓ success-criteria.md         — Metrics and validation checkpoints
```

## Example

```bash
architect:refactor path=./monolith [target_architecture="microservices"]
```

**Output:**
- Phase 1: Extract auth service
- Phase 2: Extract order service
- Phase 3: Extract payment service
- Rollback procedures for each phase
- Success metrics and monitoring

## Workflow

1. Analyze existing codebase structure
2. Identify service boundaries and dependencies
3. Plan extraction phases (minimize coupling)
4. Define rollback procedures
5. Assess risks and mitigations
6. Create success criteria and monitoring
7. Generate migration timeline

## Related Functions

- `architect:design` — Greenfield design
- `architect:schema` — Database schema refactoring
- `quality:audit` — Current codebase analysis
