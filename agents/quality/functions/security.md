---
name: quality:security Function
description: Security audit - OWASP scanning, vulnerability detection, compliance checks
prefix: quality:security
version: 3.0
---

# quality:security

**Security audit** with OWASP Top 10 scanning, vulnerability detection, and compliance verification.

## Inputs

```
quality:security path="./"
```

- `path` (string, required) — Path to codebase
- `framework` (string, optional) — Security framework (owasp, cwe, sans)

## Outputs

```
✓ SECURITY_REPORT.md          — Vulnerabilities and fixes
✓ OWASP_FINDINGS.json         — OWASP Top 10 findings
✓ REMEDIATION_PLAN.md         — Fix timeline
```

## Example

```bash
quality:security path=./
```

## Related Functions

- `quality:audit` — Code health audit
- `quality:review` — PR review with security focus
