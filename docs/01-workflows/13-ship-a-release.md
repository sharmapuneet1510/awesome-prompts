# 13 — Ship a Release

**Package it, prove the chain holds, ship it.** The traceability run is the part
that distinguishes a release from a deploy.

Covers [SDLC](sdlc-playbook.md) stage 13.

---

## When to use this

- Work is complete, reviewed, and QA has passed.
- Cutting a release that bundles several merged changes.

## Prerequisites

- [06 — Review a pull request](06-review-a-pull-request.md) complete, no High
  findings open.
- QA suites updated and passing.

---

## The chain

```
orchestrator:pr                             → pull request
    ↓
ba:trace scope=release version=2.4.0        → 18 checks, all hops
    ↓
[merge + deploy]
    ↓
Final Implementation Record + release-history.md
```

---

## The 18 checks

`ba:trace` at release scope runs all of them. They divide three ways:

**Forward — nothing stranded** (T-1 to T-7)
Every requirement is cited by a task. Every decision-bearing Jira item has an
ADR. Every Accepted ADR is cited by a spec section. Affected component and test
paths exist. Every acceptance criterion maps to a test. Every merged PR appears
in a release row.

**Backward — nothing unexplained** (T-8 to T-12)
Every spec section cites an ADR. Every ADR names a Parent Jira. Every task cites
a requirement. Every implementation record row has a non-empty `Satisfies`.
Every quality scenario cites a business rule or requirement.

**Integrity — the graph is well-formed** (T-13 to T-18)
Every `Supersedes` has a reciprocal `Superseded By`. No supersede cycles. No ADR
at Implemented under a spec that never cited it. Every ADR with technical debt
has a `TD-n` row. No two Accepted ADRs contradict each other. IDs unique and
never reused.

**High findings block the release.** Medium and Low are reported and, if
unresolved, recorded in `open-questions.md`.

---

## Findings are not auto-fixed

A missing link is usually a missing decision. Writing the link would hide that —
so `ba:trace` reports FACT plus PROPOSAL and stops:

```
### T-2 (High) — Jira item with no ADR
FACT: PROJ-114 changed the order-submission contract; no ADR cites it as
Parent Jira.
Impact: the contract change has no recorded rationale.
PROPOSAL: run architect:adr for PROJ-114 before release.
```

Unresolved findings carry forward to the next run, so a break cannot quietly
persist across releases.

---

## The Final Implementation Record

Written once per Jira item after merge. It is what makes a shipped change
auditable months later, when the people involved have moved on.

| Section | Contents |
|---|---|
| ADRs Applied | Every ADR and its status |
| Pull Request | PR, merge date, reviewer |
| Code Components | Paths, changes, and what each satisfies |
| Tests | Paths, types, and the criteria covered |
| Technical Debt Incurred | `TD-n` rows |
| Release | Version, date, environment |

An empty `Satisfies` or `Covers AC` cell is a traceability violation, caught by
check T-11.

---

## Release history closes the loop

Every release adds a row to `docs/project-context/release-history.md` naming the
**ADRs it shipped**. This is hop 7 of the chain, and the reason you can ask
"which release introduced this behaviour" and get an answer.

---

## Artifacts

| Path | From |
|---|---|
| Pull request | `orchestrator:pr` |
| `docs/traceability-report-<date>.md` | `ba:trace` |
| `docs/implementation-records/<JIRA>-final-implementation-record.md` | `architect:spec` |
| `docs/project-context/release-history.md` — new row | orchestrator |
| `docs/project-context/open-questions.md` | Unresolved findings |

---

## Next

- [14 — Export to platforms](14-export-to-platforms.md) to share the setup
- [07 — Fix a production incident](07-fix-production-incident.md) if it goes wrong
