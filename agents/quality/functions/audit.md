---
name: quality:audit Function
description: Codebase audit - code health, technical debt, patterns analysis
prefix: quality:audit
version: 3.0
---

# quality:audit

**Audit entire codebase** for health, technical debt, patterns, and improvement opportunities.

## Inputs

```
quality:audit path="./"
```

- `path` (string, required) — Path to codebase
- `scope` (string, optional) — Audit scope (full, critical, targeted)

## Outputs

```
✓ AUDIT_REPORT.md             — Findings and recommendations
✓ HEALTH_METRICS.json         — Code health scores
✓ TECHNICAL_DEBT.md           — Debt inventory and timeline
```

## Example

```bash
quality:audit path=./
```

## Related Functions

- `quality:review` — PR review
- `quality:security` — Security audit
- `quality:perf` — Performance audit
