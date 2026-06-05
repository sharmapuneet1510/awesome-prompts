---
name: quality:debug Function
description: Root cause analysis and production issue investigation
prefix: quality:debug
version: 3.0
---

# quality:debug

**Investigate production issues** with root cause analysis, debugging strategies, and remediation.

## Inputs

```
quality:debug stack_trace="..." [context="..."]
```

- `stack_trace` (string, required) — Error stack trace or logs
- `context` (string, optional) — Additional context (config, environment)
- `reproduction` (string, optional) — Steps to reproduce

## Outputs

```
✓ ROOT_CAUSE.md               — Identified root cause
✓ SOLUTION.md                 — Fix implementation
✓ PREVENTION.md               — Future prevention
```

## Example

```bash
quality:debug stack_trace="NullPointerException at line 42 in..."
```

## Related Functions

- `quality:review` — Code review
- `quality:audit` — Codebase audit
