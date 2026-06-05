---
name: quality:report Function
description: Unified quality report - PR review + audit + security + performance synthesis
prefix: quality:report
version: 3.0
---

# quality:report

**Generate unified quality report** synthesizing PR review, audit, security, and performance findings.

## Inputs

```
quality:report pr=123
```

- `pr` (number, required) — GitHub PR number
- `include_audit` (bool, optional) — Include codebase audit (default: false)

## Outputs

```
✓ QUALITY_REPORT.html         — Interactive HTML report
✓ SUMMARY.md                  — Executive summary
✓ metrics.json                — Quality metrics
```

## Example

```bash
quality:report pr=123
```

## Related Functions

- `quality:review` — PR review
- `quality:batch-review` — Multiple PRs
