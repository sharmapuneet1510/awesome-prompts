---
name: Current Technical Specification Skill
version: 1.0
description: >
  Reusable skill for the Current Technical Specification — the latest approved
  design only, generated as a projection of Accepted-or-later ADRs, never
  hand-authored. Also carries the Final Implementation Record. Owned by
  architect:spec.
---

# Current Technical Specification Skill — v1.0

## Purpose

Answer "how does this system work **today**?" in one document, with every claim
traceable to the decision that produced it.

The core rule: **the specification is a projection, never a source.** ADRs are
the source. If a line in the spec has no ADR behind it, either the ADR is
missing or the line is wrong.

This is what separates current state from historical reasoning — requirement
§1. The spec shows only what is true now; the ADR log shows how it got that
way, including the paths not taken.

This skill is **internal** — called by agents, not invoked directly by users.
`architect:spec` is its only writer.

---

## Artifact Location

Downstream project:

```
<project-root>/docs/
├── current-technical-specification.md
└── implementation-records/
    └── PROJ-123-final-implementation-record.md
```

---

## The Projection Rule

The spec is regenerated, never edited in place:

1. Read every file in `docs/adr/`.
2. Select ADRs at status **Accepted, Implemented, or Verified**.
   Exclude Draft and Proposed (not yet decided) and Superseded and Archived
   (no longer current).
3. Where two selected ADRs conflict, the later ID wins — and this indicates a
   missing supersede link. Report it rather than silently resolving it.
4. Group the selected ADRs into the ten sections below by their Decision Type.
5. Write each section from the ADRs' Decision and Consequences fields, citing
   the ADR IDs.
6. Append the pending list: every Draft and Proposed ADR, so a reader can see
   what is about to change.

**Never** carry forward prose from the previous spec version that no surviving
ADR supports. Regeneration is how the spec stays honest — text that outlives
its decision is exactly the drift this skill exists to prevent.

Section-to-type mapping:

| Spec section | Fed by Decision Type |
|---|---|
| Architecture | `Architecture`, `Refactoring` |
| Flow | `Architecture`, `Business Logic` |
| Components | `Architecture`, `Refactoring` |
| APIs | `API` |
| Data Model | `Database` |
| Error Handling | `Architecture`, `Business Logic`, `Monitoring` |
| Performance | `Performance` |
| Security | `Security` |
| Testing | `Testing` |
| Rollback | `Deployment` |

An ADR may legitimately land in more than one section; cite it in each.

---

## Specification Template

```markdown
# Current Technical Specification

**Version:** <N>
**Generated:** <YYYY-MM-DD> by architect:spec
**Source ADRs:** <count> accepted-or-later
**Supersedes spec version:** <N-1>

> Generated from ADRs. Do not edit by hand — change an ADR and regenerate.

## 1. Architecture
<current topology and style>
*Decided by: ADR-0001, ADR-0007*

## 2. Flow
<end-to-end request and data flow through the system>
*Decided by: ADR-0004*

## 3. Components
| Component | Responsibility | Depends on | ADR |
|---|---|---|---|

## 4. APIs
| Endpoint | Method | Auth | Idempotent | ADR |
|---|---|---|---|---|

## 5. Data Model
<entities, relationships, ownership>
*Decided by: ADR-0002*

## 6. Error Handling
| Failure | Detected by | Response | Retry policy | ADR |
|---|---|---|---|---|

## 7. Performance
| Path | Target | Measured | Mechanism | ADR |
|---|---|---|---|---|

## 8. Security
| Control | Protects | Mechanism | ADR |
|---|---|---|---|

## 9. Testing
<test strategy, coverage targets, suite layout>
*Decided by: ADR-0011*

## 10. Rollback
<how each deployable is rolled back, and the data implications>
*Decided by: ADR-0009*

---

## Pending Decisions
| ADR | Status | Would change |
|---|---|---|
| ADR-0014 | Proposed | Section 4 — APIs |

## Superseded Since Version <N-1>
| ADR | Superseded by | Section affected |
|---|---|---|
```

Every section must carry at least one ADR citation. A section with no citation
means either the ADR was never written or the section is speculation — both are
findings, not something to paper over.

---

## Versioning

The spec version increments by one on every regeneration that changes content.
Keep the previous version at
`docs/implementation-records/spec-v<N-1>.md` when a Final Implementation Record
cites it; otherwise git history is sufficient.

Only a **DECISION** — a human-approved ADR — triggers regeneration. FACT,
INFERENCE, and PROPOSAL never mutate the spec. This is requirement §10,
enforced.

---

## Final Implementation Record

Written once per Jira item, after the PR merges. Fields from requirement §8.
This is the artifact that makes a shipped change auditable after the fact.

```markdown
# Final Implementation Record — <PROJ-123>

**Completed:** <YYYY-MM-DD>
**Jira:** <PROJ-123> — <title>
**Spec version at merge:** v<N>

## ADRs Applied
| ADR | Decision Type | Status |
|---|---|---|

## Pull Request
| PR | Merged | Reviewer |
|---|---|---|

## Code Components
| Path | Change | Satisfies |
|---|---|---|

## Tests
| Path | Type | Covers AC |
|---|---|---|

## Technical Debt Incurred
| TD ID | Issue | Priority |
|---|---|---|

## Release
| Version | Date | Environment |
|---|---|---|
```

`Satisfies` and `Covers AC` cite requirement IDs and acceptance criteria from
`specs/<feature-name>/requirements.md`. An empty cell is a traceability
violation — see `traceability_skill.md`.

---

## Workflow (`architect:spec`)

1. Read all of `docs/adr/`.
2. Apply the projection rule; collect the selected set and the pending set.
3. Detect conflicts between selected ADRs. If any exist, stop and report them
   as missing supersede links — do not guess which wins.
4. Regenerate the spec from scratch into the template.
5. Diff against the previous version and summarise what changed and which ADR
   caused each change.
6. Update `docs/project-context/technical-context.md` and
   `architecture-context.md` to match.
7. On PR merge, write the Final Implementation Record.

---

## Related

- `skills/adr_skill.md` — the source of everything in this document
- `skills/project_context_skill.md` — durable context this spec updates
- `skills/traceability_skill.md` — validates spec ↔ ADR ↔ code links
- `instructions/master_instruction_set.md` — RULE 11, RULE 12
