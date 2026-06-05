---
name: implementer:build Function
description: Code generation from specifications, architecture, or requirements
prefix: implementer:build
version: 3.0
---

# implementer:build

**Generate production-ready code** from specifications, architecture documents, or requirements.

## Inputs

```
implementer:build path="..." [tech_stack="..."]
```

- `path` (string, required) — Path to spec, design, or requirements file
- `tech_stack` (string, optional) — Target tech (Java, Python, React, Node.js, etc.)
- `style` (string, optional) — Code style (conventional, google, airbnb)

## Outputs

```
✓ src/                        — Generated source code
✓ ARCHITECTURE.md             — Code structure documentation
✓ BUILD.md                    — Build and deployment guide
```

## Example

```bash
implementer:build path=./api-spec.yaml [tech_stack="Python, FastAPI"]
```

**Output:**
- FastAPI routes with type hints
- Pydantic models
- Docstrings
- Error handling

## Workflow

1. Parse specification/design
2. Detect or use specified tech stack
3. Generate code structure
4. Implement functions/classes
5. Add error handling
6. Generate documentation
7. Create build configuration

## Related Functions

- `implementer:full` — Build + test + doc in one pass
- `implementer:test` — Test generation
- `implementer:doc` — Documentation generation
- `architect:design` — System design (input)
