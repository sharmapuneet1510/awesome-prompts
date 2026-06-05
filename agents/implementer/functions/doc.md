---
name: implementer:doc Function
description: Auto-documentation generation - docstrings, architecture guides, API reference
prefix: implementer:doc
version: 3.0
---

# implementer:doc

**Generate comprehensive documentation** with inline docstrings, architecture guides, and API references.

## Inputs

```
implementer:doc path="..."
```

- `path` (string, required) — Path to source code directory
- `style` (string, optional) — Doc style (javadoc, sphinx, jsdoc)

## Outputs

```
✓ src/                        — Inline docstrings/JSDoc
✓ docs/API.md                 — API reference
✓ docs/ARCHITECTURE.md        — Architecture guide
✓ docs/SETUP.md               — Setup instructions
```

## Example

```bash
implementer:doc path=./src
```

## Workflow

1. Analyze source code
2. Generate inline documentation
3. Create API reference
4. Write architecture guide
5. Generate setup guide
6. Create examples
7. Validate documentation completeness

## Related Functions

- `implementer:full` — Build + test + doc
- `implementer:build` — Code generation
