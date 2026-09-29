---
name: orchestrator:build Function
version: 1.0
description: "Execute full-stack generation across all tasks (DB → API → UI → Tests → Deploy)"
prefix: orchestrator:build
---

# orchestrator:build

**Input:** requirement.md + context.json + task specifications

**Output:**
- Generated code for all 5 tasks
- Tests with 95%+ coverage
- Full documentation (docstrings/JSDoc/Javadoc)
- task-completion.json (execution log)
- Updated architecture.md + context.json

**Steps per task (01-05):**
1. Load task specification + full context
2. Call appropriate skill (database/backend/frontend/test/architecture)
3. Apply code_documentation_skill to all generated code
4. Generate tests with 95%+ coverage
5. Validate acceptance criteria met
6. Update task-completion.json with completion status
7. Regenerate context.json + graph.json
8. Move to next task

**Final steps (documentation + integration):**
1. Apply code_documentation_skill to all code again
2. Generate API documentation (OpenAPI/Swagger)
3. Create README.md + Getting Started
4. Validate all tasks integrate seamlessly
5. Check for conflicts/duplicates
6. Update final architecture.md
