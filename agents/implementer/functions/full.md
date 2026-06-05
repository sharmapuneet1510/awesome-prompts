---
name: implementer:full Function
description: Complete implementation - code + tests + docs + pipeline in one execution (NO CONTEXT LOSS)
prefix: implementer:full
version: 3.0
---

# implementer:full

**Complete implementation in ONE execution:** code generation → tests → documentation → CI/CD → containerization.

🎯 **Key Innovation:** Runs build → test → doc → pipeline → docker in a SINGLE context window with ZERO state transfer overhead.

## Inputs

```
implementer:full path="..." [tech_stack="..."]
```

- `path` (string, required) — Path to design/spec/requirements
- `tech_stack` (string, optional) — Target tech (Python, Java, React, Node.js, etc.)
- `include_pipeline` (bool, optional) — Include CI/CD (default: true)
- `include_docker` (bool, optional) — Include Docker (default: true)

## Outputs (All in one pass)

```
✓ src/                        — Generated source code
✓ tests/                      — 95%+ coverage tests
✓ docs/                       — Complete documentation
✓ .github/workflows/          — CI/CD pipelines
✓ Dockerfile + docker-compose.yml
✓ IMPLEMENTATION.md           — Summary & next steps
```

## Example

```bash
implementer:full path=./design/system-architecture.md [tech_stack="Python, FastAPI, PostgreSQL"]
```

**Output (single execution):**
- FastAPI backend with models, routes, error handling
- pytest tests with 95%+ coverage
- API documentation
- GitHub Actions workflow
- Dockerfile and docker-compose
- Setup and deployment guides

## Workflow (Single Context, No Loss)

1. **[Phase 1]** Parse design/spec
2. **[Phase 2]** Generate code (build)
3. **[Phase 3]** Generate tests (test)
4. **[Phase 4]** Generate docs (doc)
5. **[Phase 5]** Generate pipeline (pipeline)
6. **[Phase 6]** Generate containers (docker)
7. **[Phase 7]** Create GitHub PR ready for review

**Why This Works:** All phases execute in the SAME context window, so code generation context is fully available to test generation, documentation generation has complete code context, etc. No state serialization/deserialization overhead.

## vs. Running Separately

### ❌ Separate Executions (v2.0 pattern)
```
implementer:build path=./design
  → Output: src/
  → Context LOST

implementer:test path=./src
  → Input: regenerated code from src/
  → Context LOST again

implementer:doc path=./src
  → Input: regenerated code from src/
  → Less complete documentation
```

### ✅ Single Execution (v3.0 innovation)
```
implementer:full path=./design
  → Build code (context: design + requirements)
  → Test code (context: design + requirements + generated code)
  → Document (context: all above + test coverage)
  → Pipeline (context: all above + deployment needs)
  → Output: Complete system ready for deployment
```

## Related Functions

- `implementer:build` — Code generation only
- `implementer:test` — Test generation only
- `implementer:doc` — Documentation only
- `implementer:pipeline` — CI/CD only
- `implementer:docker` — Containerization only
- `orchestrator:build` — Full workflow with design phase
