---
name: quality:observe Function
description: Four-way conformance comparison — Requirement↔Code, ADR↔Code, Spec↔Code, Tests↔AC. Observations only.
prefix: quality:observe
version: 1.0
---

# quality:observe

**Report gaps between what was agreed and what was built.** Produces
observations only — it never edits code, never mints an ADR, and never scores.
Scoring and fix proposals are `quality:review`; this function exists to keep
conformance separate from opinion.

## Inputs

```
quality:observe pr=123
quality:observe jira=PROJ-123
quality:observe path=./src feature=checkout
```

- `pr` (number) | `jira` (string) | `path` (string) — what to observe
- `feature` (string, optional) — the `specs/<feature>/` to compare against

## Outputs

```
✓ docs/observations/<PR|JIRA>-observations.md
✓ docs/project-context/open-questions.md    — appended for unresolved gaps
```

## The Four Comparisons

Requirement §3, in order. Each is a gap report in both directions.

### 1. Requirement ↔ Code

| Direction | Gap |
|---|---|
| Requirement with no code | Unimplemented requirement |
| Code with no requirement | Unrequested work — scope creep |

### 2. ADR ↔ Code

| Direction | Gap |
|---|---|
| ADR decision not reflected in code | Decision not honoured |
| Code contradicting an Accepted ADR | Undocumented reversal — the most serious finding |
| Decision-bearing code with no ADR | Missing ADR (RULE 11a violation) |

### 3. Technical Spec ↔ Code

| Direction | Gap |
|---|---|
| Spec section with no implementation | Spec ahead of code |
| Behaviour absent from the spec | Spec stale — regenerate |

### 4. Tests ↔ Acceptance Criteria

| Direction | Gap |
|---|---|
| AC with no test | Unverified criterion |
| Test asserting behaviour no AC requires | Over-specified test, or a missing AC |

## Workflow

1. Load the artifact set: `specs/<feature>/requirements.md`, `docs/adr/`,
   `docs/current-technical-specification.md`, and the diff or path.
2. Run the four comparisons, both directions each.
3. Run traceability checks T-3, T-6, and T-8 from `traceability_skill`.
4. Report each finding as FACT (what is there, with `file:line`) plus PROPOSAL
   (what should happen). Never both diagnose and fix.
5. Report Project Context staleness — any node untouched for 90+ days while
   its area changed.
6. Stop. Hand PROPOSALs to `architect:adr`, `implementer:build`, or
   `ba:clarify` as appropriate.

## Output Format

```markdown
# Observations — <PR 123 / PROJ-123>
**Compared:** requirements v<n> · <k> ADRs · spec v<n> · <m> tests

## Summary
| Comparison | Conforming | Gaps |
|---|---|---|
| Requirement ↔ Code | 8 | 1 |
| ADR ↔ Code | 5 | 2 |
| Spec ↔ Code | 10 | 0 |
| Tests ↔ AC | 12 | 3 |

## Gaps
### ADR ↔ Code — decision not honoured
FACT: ADR-0012 requires an Idempotency-Key header; `src/order/api.py:44`
accepts the request without reading one.
**Comparison:** ADR ↔ Code · **Direction:** decision → code
PROPOSAL: implement per ADR-0012, or supersede ADR-0012 via `architect:adr`.
```

## Boundaries

| Never | Instead |
|---|---|
| Edit code | Emit a PROPOSAL |
| Write or accept an ADR | Propose one; `architect:adr` writes it |
| Assign a quality score | That is `quality:review` |
| Regenerate the spec | Propose it; `architect:spec` does it |
| Resolve an ambiguous requirement | Log it in `open-questions.md` |

## Related Functions

- `quality:review` — scoring PR validation, may propose fixes
- `quality:qa` — the five reusable test suites
- `ba:trace` — the full 18-check traceability run

## Related Skills

- `skills/adr_skill.md` · `skills/current_tech_spec_skill.md`
- `skills/traceability_skill.md` · `skills/project_context_skill.md`
