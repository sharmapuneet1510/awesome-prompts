---
name: Traceability Skill
version: 1.0
description: >
  Reusable skill defining the eight-hop traceability chain (Requirement → Jira
  → ADR → Technical Specification → Implementation → Tests → PR → Release),
  the link fields each artifact must carry, and the validation checks that
  detect breaks. Owned by ba:trace; read by quality:observe.
---

# Traceability Skill — v1.0

## Purpose

Make it possible to answer, for any line of production code, "which business
requirement is this here for?" — and for any requirement, "where did it ship?"

Requirement §9 states the chain. This skill makes it checkable.

This skill is **internal** — called by agents, not invoked directly by users.

---

## The Chain

```
Requirement ──▶ Jira ──▶ ADR ──▶ Technical Specification
                                        │
                                        ▼
                              Implementation ──▶ Tests ──▶ PR ──▶ Release
```

Each hop is a named field on a concrete artifact. Nothing is implicit.

| Hop | From | To | Carried by |
|---|---|---|---|
| 1 | Requirement | Jira | `Jira:` in `specs/<feature>/requirements.md` |
| 2 | Jira | ADR | `Parent Jira:` in each ADR |
| 3 | ADR | Technical Spec | `*Decided by: ADR-NNNN*` per spec section |
| 4 | Technical Spec | Implementation | `Affected Components` in each ADR |
| 5 | Implementation | Tests | `Affected Tests` in each ADR |
| 6 | Tests | PR | Final Implementation Record `Tests` table |
| 7 | PR | Release | `release-history.md` row naming its PRs |
| 8 | Release | Requirement | Final Implementation Record `Satisfies` column |

Hop 8 closes the loop, which is what makes orphan detection possible in both
directions.

---

## ID Conventions

| Artifact | ID form | Defined in |
|---|---|---|
| Requirement | `REQ-<n>` | `spec_driven_development_skill.md` |
| Business rule | `BR-<n>` | `project_context_skill.md` |
| Acceptance criterion | `AC-<REQ-n>.<m>` | `spec_driven_development_skill.md` |
| ADR | `ADR-<NNNN>` | `adr_skill.md` |
| Technical debt | `TD-<n>` | `project_context_skill.md` |
| Risk | `R-<n>` | `project_context_skill.md` |
| Quality scenario | `SAN-`/`REG-`/`INT-`/`PERF-`/`SEC-<n>` | `project_context_skill.md` |
| Open question | `Q-<n>` | `project_context_skill.md` |

IDs are stable and never reused. Renumbering breaks every citation pointing at
the old ID, so an obsolete item is marked obsolete, not removed.

---

## Validation Checks

Run by `ba:trace`. Each check reports findings; **none of them auto-fix**.

### Forward checks — nothing is stranded

| ID | Check | Severity |
|---|---|---|
| T-1 | Every `REQ-n` is cited by at least one `tasks.md` entry | High |
| T-2 | Every decision-bearing Jira item has at least one ADR | High |
| T-3 | Every Accepted-or-later ADR is cited by a spec section | High |
| T-4 | Every ADR's `Affected Components` paths exist in the repo | Medium |
| T-5 | Every ADR's `Affected Tests` paths exist | Medium |
| T-6 | Every acceptance criterion maps to at least one test | High |
| T-7 | Every merged PR appears in a `release-history.md` row | Low |

### Backward checks — nothing is unexplained

| ID | Check | Severity |
|---|---|---|
| T-8 | Every spec section cites at least one ADR | High |
| T-9 | Every ADR names a `Parent Jira` | High |
| T-10 | Every `tasks.md` entry cites at least one `REQ-n` | High |
| T-11 | Every Final Implementation Record row has a non-empty `Satisfies` | Medium |
| T-12 | Every quality scenario cites a `BR-n` or `REQ-n` | Medium |

### Integrity checks — the graph is well-formed

| ID | Check | Severity |
|---|---|---|
| T-13 | Every `Supersedes:` has a reciprocal `Superseded By:` | High |
| T-14 | No supersede cycle | High |
| T-15 | No ADR at Implemented or Verified under a spec that never cited it | High |
| T-16 | Every ADR with non-empty Technical Debt has a `TD-n` row | Medium |
| T-17 | No two ADRs at Accepted-or-later contradict each other | High |
| T-18 | ADR IDs are unique and contiguous with no reuse | Low |

**High** findings block the RULE 11 gate. **Medium** and **Low** are reported
and recorded in `open-questions.md` if unresolved.

---

## Report Format

```markdown
# Traceability Report — <YYYY-MM-DD>

**Scope:** <feature | release | whole project>
**Checks run:** 18 · **Passed:** <n> · **Findings:** <n>

## Chain Coverage
| Hop | Complete | Broken |
|---|---|---|
| Requirement → Jira | 12/12 | — |
| Jira → ADR | 9/12 | PROJ-114, PROJ-118, PROJ-121 |

## Findings
### T-2 (High) — Jira item with no ADR
FACT: PROJ-114 changed the order-submission contract; no ADR cites it as Parent Jira.
**Impact:** the contract change has no recorded rationale.
PROPOSAL: run `architect:adr` for PROJ-114 before release.

## Unresolved from Previous Run
| Finding | First seen | Owner |
|---|---|---|
```

Findings carry RULE 12 labels. A traceability finding is a FACT about the
document graph plus a PROPOSAL about what to do — never a unilateral fix.

---

## When to Run

| Trigger | Scope |
|---|---|
| Before `implementer:build` | Feature — T-1, T-2, T-10, T-13 (gate checks) |
| After `architect:spec` | Feature — T-3, T-8, T-13, T-15, T-17 |
| Before a release | Whole project — all 18 |
| Inside `quality:observe` | Feature — T-3, T-6, T-8 |

---

## Related

- `skills/adr_skill.md` — hops 2–5
- `skills/current_tech_spec_skill.md` — hops 3, 6, 8
- `skills/project_context_skill.md` — hop 7, ID conventions
- `skills/spec_driven_development_skill.md` — hop 1 and its own traceability rule
- `instructions/master_instruction_set.md` — RULE 11, RULE 12
