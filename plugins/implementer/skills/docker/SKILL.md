---
name: docker
description: Container configuration - Dockerfile, docker-compose, image optimization
argument-hint: path="..."
disable-model-invocation: true
---

Role and rules: read ${CLAUDE_PLUGIN_ROOT}/reference/agent.md and ${CLAUDE_PLUGIN_ROOT}/reference/rules.md for the sections this function needs.

# implementer:docker

**Generate container configurations** with optimized Dockerfiles and docker-compose stacks.

## Inputs

```
implementer:docker path="..."
```

- `path` (string, required) — Path to project
- `base_image` (string, optional) — Base image (python:3.11, node:18, etc.)

## Outputs

```
✓ Dockerfile                  — Optimized container image
✓ docker-compose.yml          — Multi-container stack
✓ .dockerignore               — Docker ignore patterns
✓ DOCKER.md                   — Docker usage guide
```

## Example

```bash
implementer:docker path=./
```

## Workflow

1. Detect project type
2. Choose optimized base image
3. Create build stages
4. Optimize layer caching
5. Generate docker-compose
6. Add health checks
7. Document usage

## Related Functions

- `implementer:full` — Build + test + doc + docker
- `implementer:iac` — Infrastructure as code
