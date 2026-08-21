# 10 — Modernise a Legacy System

**Large, old, and load-bearing.** The workflow that runs in phases over weeks
rather than in one pass.

Covers [SDLC](sdlc-playbook.md) stages 0, 3–5, 7, 15.

---

## When to use this

- Structural change: monolith to services, framework migration, datastore
  replacement, dependency the vendor has abandoned.
- The system is in production and cannot stop.

**Not this workflow** for a large feature. Size is not the trigger — *structural
change to something already running* is.

## Prerequisites

- [04 — Understand a codebase](04-understand-a-codebase.md), completed. Never
  start here.

---

## The chain

```
orchestrator:context path=./        → what exists
quality:audit path=./src            → debt scoring, refactoring roadmap
    ↓
architect:analyse                   → current flow, migration options, risks
orchestrator:tradeoff               → compare approaches explicitly
orchestrator:risk                   → failure modes, mitigations
    ↓
architect:adr                       → one ADR per migration decision  ◆ GATE
architect:spec                      → target-state specification
    ↓
architect:refactor path=./src       → phased roadmap, migration guide, rollback
    ↓
[per phase] implementer:full → quality:observe → quality:qa → orchestrator:pr
```

The final line repeats. Each phase is a full trip through
[03](03-feature-from-requirement.md).

---

## Why this one is decision-heavy

Modernisation is mostly decisions and only incidentally code. A migration
carries more ADRs than any other workflow — typically one per boundary, per data
migration, per compatibility shim, plus the rollback strategy for each phase.

Record them **before** the phase they govern, not after. An ADR written after
the migration is a report, not a decision.

Expect these Decision Types: `Architecture`, `Database`, `Deployment`,
`Refactoring`, and — for anything touching data — `Business Logic`.

---

## The rollback story is part of the design

`architect:refactor` produces the phased roadmap, the migration guide, and
**rollback strategies per phase**. Every phase needs an answer to "what if we
have to undo this on a Friday afternoon", including the data implications.

Section 10 of the Current Technical Specification exists for exactly this.

---

## Superseding is the normal case

Most modernisation decisions replace an earlier one. Do it properly:

- The new ADR declares `Supersedes: ADR-000X`.
- The old ADR gets `Superseded By:` and flips to Superseded.
- **The old ADR's body is left untouched.** It recorded what was correct at the
  time.

The superseded chain is the most valuable artifact this workflow produces. In
two years it is the only record of why the old design existed, which is what
stops someone re-introducing it.

---

## Known behaviours are not bugs

An old system is full of surprising behaviour that is load-bearing. Record it in
`docs/project-context/known-behaviours.md` before changing anything, split three
ways:

| Category | Meaning |
|---|---|
| Expected behaviour | Surprising but correct — say why |
| Intentional limitations | Chosen deliberately — name the ADR and when to revisit |
| Known quirks | Wrong but tolerated — say why it is not fixed |

This is what stops a well-meaning migration from "fixing" something a downstream
consumer depends on.

---

## Artifacts

| Path | From |
|---|---|
| `docs/context/`, `docs/project-context/` | `orchestrator:context` |
| Audit report, debt scores, refactoring roadmap | `quality:audit` |
| Trade-off and risk analyses | `orchestrator:tradeoff`, `:risk` |
| `docs/adr/` — many, with supersede chains | `architect:adr` |
| Phased roadmap, migration guide, rollback strategies | `architect:refactor` |
| `docs/project-context/known-behaviours.md`, `technical-debt.md` | Throughout |

---

## Worked example

[../04-examples/orchestrator.md](../04-examples/orchestrator.md) — legacy
modernisation, monolith to microservices.
[../04-examples/architect.md](../04-examples/architect.md) — brownfield
refactoring with a strangler pattern and zero-downtime migration.

---

## Next

- [13 — Ship a release](13-ship-a-release.md) per phase
