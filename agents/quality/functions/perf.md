---
name: quality:perf Function
description: Performance optimization analysis and recommendations
prefix: quality:perf
version: 3.0
---

# quality:perf

**Performance analysis** with optimization recommendations for bottlenecks, caching, and scalability.

## Inputs

```
quality:perf path="./"
```

- `path` (string, required) — Path to codebase
- `metrics` (string, optional) — Metrics to analyze (latency, throughput, memory)

## Outputs

```
✓ PERFORMANCE_REPORT.md       — Analysis and recommendations
✓ BOTTLENECKS.json            — Identified bottlenecks
✓ OPTIMIZATION_PLAN.md        — Implementation timeline
```

## Example

```bash
quality:perf path=./
```

## Related Functions

- `quality:audit` — Code health audit
- `quality:review` — PR review
