# Artifact Reference

**Every file the system produces, what writes it, and where it lands.**

The recurring question this answers: *is this file mine, or does the tooling own
it?* Some artifacts are regenerated wholesale and must never be hand-edited.

---

## Where artifacts live

Two destinations, easily confused:

| Location | Holds | Example |
|---|---|---|
| **The project being worked on** | Everything the agents produce for your codebase | `docs/adr/`, `specs/<feature>/` |
| **This repository** | Only this repo's own design records | `docs/superpowers/specs/` |

Unless a document says otherwise, artifacts land in **the project being worked
on**, not here.

---

## By stage

| Stage | Artifact | Written by |
|---|---|---|
| 0 Inception | `docs/context/architecture.md`, `tech-stack.md`, `context.json`, `design.html` | `orchestrator:context` |
| 0 | `docs/project-context/` — 14 nodes | Bootstrapped, then per-owner |
| 1 Discovery | `discovery-notes.md`, `open-questions.md` | `ba:discover`, `ba:clarify` |
| 2 Requirements | `docs/brd.md`, `business-context.md`, `mvp-scope.md` | `ba:brd` |
| 2 | `requirements.json`, `requirements-cards.html` | `ba:create` |
| 3 Analysis | `docs/analysis/<JIRA>-technical-analysis.md` | `architect:analyse` |
| 4 Decision | `docs/adr/ADR-<NNNN>-<slug>.md` | `architect:adr` |
| 5 Specification | `docs/current-technical-specification.md` | `architect:spec` |
| 6 Planning | `specs/<feature>/requirements.md` | `orchestrator:plan` |
| 7 Design | `specs/<feature>/design.md` | `architect:design` |
| 8 Tasks | `specs/<feature>/tasks.md` | Task generation |
| 9 Implementation | `src/`, `tests/`, code docs | `implementer:full` |
| 10 Infrastructure | CI workflow, `Dockerfile`, IaC manifests | `implementer:pipeline`, `:docker`, `:iac` |
| 11 Review | `docs/observations/<PR>-observations.md` | `quality:observe` |
| 11 | Review, audit, security, performance reports | `quality:*` |
| 12 QA | `docs/project-context/quality/*.md` | `quality:qa` |
| 13 Release | `docs/traceability-report-<date>.md` | `ba:trace` |
| 13 | `docs/implementation-records/<JIRA>-final-implementation-record.md` | `architect:spec` |
| 13 | `docs/project-context/release-history.md` | orchestrator |
| 14 Operate | RCA report, new `REG-n` scenarios | `quality:debug`, `quality:qa` |
| 15 Evolve | `technical-debt.md` rows, superseding ADRs | `architect:adr` |

---

## Never hand-edit these

| Artifact | Why | Change it by |
|---|---|---|
| `docs/current-technical-specification.md` | A projection of Accepted ADRs, regenerated from scratch every time | Editing an ADR, then `architect:spec` |
| A Superseded or Archived ADR | Immutable. It recorded what was correct at the time | Writing a new ADR that supersedes it |
| `docs/project-context/ai-memory.md` | Append-only | Adding a newer entry that supersedes the old |

Editing a generated specification is the most common way this system's
guarantees get quietly broken: the text stops matching the decisions, and
nothing detects it because the drift is invisible until the next regeneration
wipes it.

---

## Approval-gated artifacts

Four files carry a `Status:` line that only you may advance:

| Artifact | Draft → Approved gates |
|---|---|
| `specs/<feature>/requirements.md` | `architect:design` |
| `specs/<feature>/design.md` | Task generation |
| `specs/<feature>/tasks.md` | `implementer:build` / `:full` |
| `docs/adr/ADR-<NNNN>.md` | Implementing a decision-bearing change |

An agent may write the marker into the file — only after you explicitly approve.

---

## The Project Context tree

```
docs/project-context/
├── README.md                index
├── project-overview.md      orchestrator
├── business-context.md      business_analyst
├── technical-context.md     architect
├── architecture-context.md  architect
├── known-behaviours.md      architect
├── technical-debt.md        architect
├── mvp-scope.md             business_analyst
├── quality/
│   ├── sanity.md            quality — under 5 minutes
│   ├── regression.md        quality — each row cites its incident
│   ├── integration.md       quality — names external systems
│   ├── performance.md       quality — numeric threshold + load profile
│   └── security.md          quality — mapped to OWASP
├── dependencies.md          implementer
├── risks.md                 orchestrator
├── release-history.md       orchestrator
├── open-questions.md        any — owner writes the answer
└── ai-memory.md             any — append-only
```

**Read before acting, write after deciding.** Non-owners never edit a node
directly; they raise it in `open-questions.md` and let the owner resolve it.

---

## Stable IDs

Never reused, never renumbered — every citation elsewhere points at them.

| ID | Names | Defined in |
|---|---|---|
| `REQ-n` | Requirement | `requirements.md` |
| `AC-<REQ-n>.<m>` | Acceptance criterion | `requirements.md` |
| `BR-n` | Business rule | `business-context.md` |
| `ADR-<NNNN>` | Decision | `docs/adr/` |
| `TD-n` | Technical debt | `technical-debt.md` |
| `R-n` | Risk | `risks.md` |
| `Q-n` | Open question | `open-questions.md` |
| `SAN-`/`REG-`/`INT-`/`PERF-`/`SEC-n` | Quality scenario | `quality/*.md` |

An obsolete item is **marked obsolete, not removed**. Deleting it breaks every
citation pointing at it.

---

## The traceability chain

Each hop is a named field on a concrete artifact — nothing implicit.

| Hop | From → To | Carried by |
|---|---|---|
| 1 | Requirement → Jira | `Jira:` in `requirements.md` |
| 2 | Jira → ADR | `Parent Jira:` in each ADR |
| 3 | ADR → Specification | `*Decided by: ADR-NNNN*` per section |
| 4 | Specification → Implementation | `Affected Components` in each ADR |
| 5 | Implementation → Tests | `Affected Tests` in each ADR |
| 6 | Tests → PR | Final Implementation Record |
| 7 | PR → Release | `release-history.md` row |
| 8 | Release → Requirement | `Satisfies` column |

Hop 8 closes the loop, which is what makes orphan detection possible in both
directions. Verified by `ba:trace` — see
[../01-workflows/13-ship-a-release.md](../01-workflows/13-ship-a-release.md).

---

## See also

- [functions.md](functions.md) — what writes each artifact
- [rules.md](rules.md) — the gates that govern them
- `skills/project_context_skill.md` — node templates
