---
name: quality:review Function
description: PR validation, code quality scoring, and requirement verification
prefix: quality:review
version: 3.0
---

# quality:review

**Review pull requests** with 6-phase analysis: correctness, security, performance, testing, documentation, requirements.

## Inputs

```
quality:review pr=123
```

- `pr` (number, required) — GitHub PR number
- `depth` (string, optional) — Review depth (low, medium, high)

## Outputs

```
✓ REVIEW.md                   — Detailed findings
✓ comments/                   — Inline PR comments
✓ SCORE.json                  — Quality metrics
```

## Phases

1. **Correctness** — Logic errors, edge cases, type safety
2. **Security** — OWASP top 10, injection, auth, secrets
3. **Performance** — Efficiency, caching, algorithms
4. **Testing** — Coverage, test quality, business validation
5. **Documentation** — Docstrings, examples, clarity
6. **Requirements** — Business requirement fulfillment

## Example

```bash
quality:review pr=123
```

## Related Functions

- `quality:audit` — Codebase audit
- `quality:security` — Security-focused review
- `orchestrator:review` — Higher-level review
