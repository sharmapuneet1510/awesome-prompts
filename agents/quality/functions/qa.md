---
name: quality:qa Function
description: Maintain the five reusable quality suites — sanity, regression, integration, performance, security
prefix: quality:qa
version: 1.0
---

# quality:qa

**Own the five suites as living, reusable scenario sets** — not per-feature
test runs. Scenarios accumulate across features so coverage compounds instead
of resetting each sprint.

## Inputs

```
quality:qa
quality:qa suite=regression
quality:qa suite=performance feature=checkout
```

- `suite` (string, optional) — `sanity` | `regression` | `integration` |
  `performance` | `security`; all five if omitted
- `feature` (string, optional) — add scenarios for a specific feature
- `mode` (string, optional) — `plan` (scenarios only) | `generate` (write tests)

## Outputs

```
✓ docs/project-context/quality/<suite>.md    — scenario table, updated
✓ tests/<suite>/...                          — generated tests, when mode=generate
```

## The Five Suites

| Suite | Answers | Constraint |
|---|---|---|
| **Sanity** | Is the system fundamentally alive? | Must run in under 5 minutes |
| **Regression** | Did a previously fixed defect return? | Every row cites its originating incident |
| **Integration** | Do the seams hold? | Names external systems and their test doubles |
| **Performance** | Is it fast enough under load? | Every row carries a numeric threshold and load profile |
| **Security** | Can it be abused? | Every row maps to an OWASP category |

## Scenario Format

```markdown
| ID | Scenario | Covers | Automated | Location | Last run |
|---|---|---|---|---|---|
| REG-14 | Given a cancelled order, when payment webhook arrives late, then no charge is captured | BR-7, INC-2291 | yes | tests/regression/test_late_webhook.py | 2026-08-17 |
```

Scenarios are written in given/when/then and cite the business rule (`BR-n`) or
requirement (`REQ-n`) they protect. A scenario citing neither is untraceable —
nobody will know whether it may be deleted.

## Workflow

1. Read `docs/project-context/quality/` for existing scenarios. **Extend,
   never replace** — a deleted scenario is lost coverage.
2. Read the acceptance criteria and the ADRs for the feature in scope. An ADR
   with `Affected Tests` names work this function owns.
3. For each suite, identify what the change adds:
   - **Sanity** — only if a new critical path exists. Guard the 5-minute budget.
   - **Regression** — one row per defect fixed, citing the incident.
   - **Integration** — one row per new seam or changed contract.
   - **Performance** — one row per path with a stated target in an ADR.
   - **Security** — one row per new trust boundary or input surface.
4. Deduplicate against existing scenarios before adding.
5. Mark superseded scenarios as obsolete with a reason. Do not delete them.
6. In `mode=generate`, write the tests using `test_skill` conventions —
   AAA structure and `givenXxx_whenYyy_thenZzz` naming per RULE 2.
7. Update the suite tables and `Last run` dates.

## Coverage Gaps

Report, do not silently fill:

- An acceptance criterion with no scenario in any suite.
- A performance ADR with no threshold row.
- A security-relevant ADR with no `SEC-n` row.
- A regression row whose test has not run in 90 days.

## Related Functions

- `quality:observe` — reports Tests ↔ AC gaps this function closes
- `implementer:test` — generates feature-level tests
- `quality:security` — deep OWASP audit feeding the security suite
- `quality:perf` — profiling that sets performance thresholds

## Related Skills

- `skills/test_skill.md` · `skills/project_context_skill.md`
- `skills/security_audit_skill.md`
- `instructions/master_instruction_set.md` — RULE 2
