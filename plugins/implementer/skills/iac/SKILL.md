---
name: iac
description: Infrastructure as Code - Terraform, CloudFormation, Kubernetes manifests
argument-hint: path="..." [provider="terraform"]
disable-model-invocation: true
---

Role and rules: read ${CLAUDE_PLUGIN_ROOT}/reference/agent.md and ${CLAUDE_PLUGIN_ROOT}/reference/rules.md for the sections this function needs.

# implementer:iac

**Generate Infrastructure as Code** with Terraform, CloudFormation, or Kubernetes manifests.

## Inputs

```
implementer:iac path="..." [provider="terraform"]
```

- `path` (string, required) — Path to project
- `provider` (string, optional) — IaC tool (terraform, cloudformation, kubernetes)
- `cloud` (string, optional) — Cloud provider (aws, gcp, azure)

## Outputs

```
✓ terraform/                  — Terraform configuration
✓ manifests/                  — Kubernetes YAML
✓ cloudformation/             — CloudFormation templates
✓ IaC.md                      — Infrastructure documentation
```

## Example

```bash
implementer:iac path=./ [provider="terraform"] [cloud="aws"]
```

## Workflow

1. Analyze project requirements
2. Plan infrastructure topology
3. Create IaC templates
4. Add networking configuration
5. Configure security groups
6. Set up monitoring
7. Document infrastructure

## Related Functions

- `implementer:full` — Build + test + doc + docker + iac
- `implementer:docker` — Containerization
