---
name: quality:batch-review Function
description: Multi-PR review with unified HTML report and metrics comparison
prefix: quality:batch-review
version: 3.0
---

# quality:batch-review

**Review multiple PRs** with unified HTML report, metrics comparison, and team metrics.

## Inputs

```
quality:batch-review from="./reviews.json"
```

- `from` (string, required) — Path to reviews JSON file with PR numbers
- `format` (string, optional) — Output format (html, json, markdown)

## Outputs

```
✓ BATCH_REVIEW.html           — Interactive comparison report
✓ METRICS_COMPARISON.md       — Side-by-side metrics
✓ TEAM_METRICS.json           — Team performance data
```

## Example

```bash
quality:batch-review from=./reviews.json
```

## Related Functions

- `quality:review` — Single PR review
- `quality:report` — Individual PR report
