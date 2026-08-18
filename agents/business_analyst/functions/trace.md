---
name: ba:trace Function
description: Validate the eight-hop traceability chain from requirement to release and report every break
prefix: ba:trace
version: 1.0
---

# ba:trace

**Prove the chain is intact.** Runs the 18 validation checks from
`traceability_skill` and reports breaks. Reports only — it never repairs the
graph, because a missing link is usually a missing decision, and inventing the
link would hide that.

## Inputs

```
ba:trace
ba:trace scope=feature feature=checkout
ba:trace scope=release version=2.4.0
```

- `scope` (string, optional) — `feature` | `release` | `project` (default `project`)
- `feature` (string) — required when `scope=feature`
- `version` (string) — required when `scope=release`
- `severity` (string, optional) — minimum severity to report (`high` | `medium` | `low`)

## Outputs

```
✓ docs/traceability-report-<date>.md    — coverage table + findings
✓ docs/project-context/open-questions.md — unresolved findings appended
```

## Workflow

1. Load the artifact set for the scope: `specs/*/requirements.md`,
   `docs/adr/`, `docs/current-technical-specification.md`,
   `docs/implementation-records/`, `docs/project-context/release-history.md`.
2. Run the forward checks (T-1 to T-7) — nothing stranded.
3. Run the backward checks (T-8 to T-12) — nothing unexplained.
4. Run the integrity checks (T-13 to T-18) — the graph is well-formed.
5. Build the chain-coverage table hop by hop.
6. Report each finding as FACT (what the graph shows, with file citations)
   plus PROPOSAL (what to do). Never write the missing link yourself.
7. Carry forward unresolved findings from the previous run so a break cannot
   quietly persist across releases.

## Gate Behaviour

High-severity findings block the RULE 11 gate. When invoked before
`implementer:build`, `ba:trace` returns a pass/fail on T-1, T-2, T-10, and
T-13 only — the full 18-check run is for releases.

## Example

```bash
ba:trace scope=feature feature=checkout severity=high
```

**Output:** coverage per hop, then findings such as *T-2 (High) — PROJ-114
changed the order-submission contract with no ADR citing it as Parent Jira.*

## Related Functions

- `quality:observe` — runs a subset (T-3, T-6, T-8) during review
- `architect:adr` — the fix for most High findings

## Related Skills

- `skills/traceability_skill.md` — the 18 checks and the chain definition
