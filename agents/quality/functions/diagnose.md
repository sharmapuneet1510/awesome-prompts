---
name: quality:diagnose Function
description: Conversational problem solving for system issues and architectural questions
prefix: quality:diagnose
version: 3.0
---

# quality:diagnose

**Conversational problem solver** for system issues, architectural questions, and design feedback.

## Inputs

```
quality:diagnose problem="..."
```

- `problem` (string, required) — Problem description or question
- `context` (string, optional) — Codebase or architecture context
- `constraints` (string, optional) — Time/resource constraints

## Outputs

```
✓ DIAGNOSIS.md                — Analysis and recommendations
✓ SOLUTIONS.md                — Multiple solution options
✓ TRADEOFFS.md                — Option tradeoffs
```

## Example

```bash
quality:diagnose problem="API is slow when listing 1M items"
```

**Output:**
- Root cause analysis
- Solution options (pagination, caching, indexing)
- Performance impact of each
- Implementation roadmap

## Related Functions

- `quality:debug` — Technical debugging
- `quality:perf` — Performance analysis
- `architect:refactor` — Architectural redesign
