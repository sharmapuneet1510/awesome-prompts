---
name: ba:parse Function
description: Parse text requirements into JIRA issues and BDD feature cards
prefix: ba:parse
version: 3.0
---

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
