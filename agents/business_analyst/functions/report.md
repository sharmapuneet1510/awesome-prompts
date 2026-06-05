---
name: ba:report Function
description: Parse JIRA exports and generate interactive HTML backlog reports
prefix: ba:report
version: 3.0
---

# ba:report

**Parse JIRA exports** and generate interactive HTML backlog reports with metrics and visualization.

## Inputs

```
ba:report file="jira-export.json"
```

- `file` (string, required) — Path to JIRA JSON/CSV export
- `project` (string, optional) — Filter by project
- `status` (string, optional) — Filter by status

## Outputs

```
✓ BACKLOG.html                — Interactive backlog report
✓ METRICS.json                — Epic/story metrics
✓ BURNDOWN.html               — Burndown visualization
```

## Example

```bash
ba:report file=./jira-export.json
```

**Output:**
- Interactive backlog with filtering
- Epic/story hierarchy visualization
- Burndown charts and metrics
- Sprint planning data

## Related Functions

- `ba:create` — Create JIRA issues from text
