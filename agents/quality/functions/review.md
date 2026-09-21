---
name: quality:review Function
description: PR validation, code quality scoring, and requirement verification
prefix: quality:review
version: 3.0
---

# quality:review

**Review pull requests** with 6-phase analysis: correctness, security, performance, testing, documentation, requirements.

## Inputs

```
quality:review pr=123
```

- `pr` (number, required) — GitHub PR number
- `depth` (string, optional) — Review depth (low, medium, high)

## Outputs

```
✓ REVIEW.md                   — Detailed findings
✓ comments/                   — Inline PR comments
✓ SCORE.json                  — Quality metrics
```

## Phases

1. **Correctness** — Logic errors, edge cases, type safety
2. **Security** — OWASP top 10, injection, auth, secrets
3. **Performance** — Efficiency, caching, algorithms
4. **Testing** — Coverage, test quality, business validation
5. **Documentation** — Docstrings, examples, clarity
6. **Requirements** — Business requirement fulfillment

## NEMESIS gate (optional)

After a `PASS`, if `docs/nemesis/nemesis.yml` exists, is not `enabled: false`, and an `auto_activate` rule
matches this change (`critical_change`, `security_change` or `payment_change`; use the project's
`policy_match` entries, if it has them), run `orchestrator:nemesis target=<review id> trigger=policy` and
report its verdict beside yours. `DEFEATED`, `CHALLENGED` or `INSUFFICIENT EVIDENCE` overrides the `PASS`
until its findings are resolved or its missing evidence is supplied; `SURVIVED WITH CONDITIONS` keeps the
`PASS` and copies its conditions into your report. After two consecutive `DEFEATED` or `CHALLENGED`
results for the same change, stop and hand the decision to a human instead of re-reviewing again. Skip
this section when the file is absent, and when you are yourself running as a NEMESIS challenger.

## Example

```bash
quality:review pr=123
```

## Related Functions

- `quality:audit` — Codebase audit
- `quality:security` — Security-focused review
- `orchestrator:review` — Higher-level review
