---
name: parse
description: Parse text requirements into JIRA issues and BDD feature cards
argument-hint: file="requirements.txt"
disable-model-invocation: true
---

Role and rules: read ${CLAUDE_PLUGIN_ROOT}/reference/agent.md and ${CLAUDE_PLUGIN_ROOT}/reference/rules.md for the sections this function needs.

# ba:parse

**Parse text requirements** into JIRA-compatible issues and BDD feature cards with acceptance criteria.

## Inputs

```
ba:parse file="requirements.txt"
```

- `file` (string, required) — Path to requirements file (txt, md)
- `format` (string, optional) — Output format (jira, bdd, both)

## Outputs

```
✓ JIRA_ISSUES.json            — JIRA-compatible issue format
✓ BDD_FEATURES.md             — Gherkin/BDD feature files
✓ BACKLOG.html                — Interactive backlog
```

## Example

```bash
ba:parse file=./requirements.txt
```

**Output:**
- JIRA stories with acceptance criteria
- BDD scenarios in Gherkin format
- Task breakdown and dependencies
- Effort estimates

## Related Functions

- `ba:report` — JIRA report generation
- `orchestrator:plan` — Requirement parsing
