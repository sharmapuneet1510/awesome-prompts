---
name: implementer:pipeline Function
description: CI/CD pipeline generation - GitHub Actions, GitLab CI, Jenkins
prefix: implementer:pipeline
version: 3.0
---

# implementer:pipeline

**Generate CI/CD pipelines** with automated testing, building, and deployment workflows.

## Inputs

```
implementer:pipeline path="..." [provider="github"]
```

- `path` (string, required) — Path to project
- `provider` (string, optional) — CI provider (github, gitlab, jenkins)

## Outputs

```
✓ .github/workflows/          — GitHub Actions workflows
✓ .gitlab-ci.yml              — GitLab CI configuration
✓ Jenkinsfile                 — Jenkins pipeline
```

## Example

```bash
implementer:pipeline path=./ [provider="github"]
```

## Workflow

1. Detect project type
2. Create build stage
3. Add test stage
4. Add security scanning
5. Add deployment stage
6. Create pipeline configuration
7. Document trigger conditions

## Related Functions

- `implementer:full` — Build + test + doc + pipeline
- `implementer:docker` — Containerization
