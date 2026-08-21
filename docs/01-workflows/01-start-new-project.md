# 01 — Start a New Project

**Greenfield. Nothing exists yet.** From an idea to a running system with code,
tests, docs, and a PR.

Covers [SDLC](sdlc-playbook.md) stages 0, 6–10.

---

## When to use this

- There is no codebase yet.
- The idea may still be vague — `orchestrator:ideate` exists to sharpen it.

**Not this workflow if** the codebase exists. Use
[02](02-feature-from-conversation.md) or [03](03-feature-from-requirement.md).

## Prerequisites

None. This is the only workflow with no upstream dependency.

---

## The chain

```
(orchestrator:ideate idea="...")     ← only if the idea is still vague
    ↓
orchestrator:plan                     → requirements.md          ◆ GATE
    ↓
architect:design requirements="..."   → design.md                ◆ GATE
    ↓
[task generation]                     → tasks.md                 ◆ GATE
    ↓
implementer:full path=./design        → code + tests + docs
    ↓
implementer:docker · :pipeline · :iac  → deployable
    ↓
quality:review                        → validation + score
    ↓
orchestrator:pr                       → pull request
```

`orchestrator:build path=./design` auto-chains design → implementation if you
want one command instead of three. You lose the per-stage checkpoints, so prefer
the explicit chain the first time through a new domain.

---

## Gates

| After | You approve | Blocks if unapproved |
|---|---|---|
| `orchestrator:plan` | `requirements.md` | `architect:design` refuses |
| `architect:design` | `design.md` | Task generation refuses |
| Task generation | `tasks.md` | `implementer:full` refuses |

You will be asked three times. That is deliberate — a greenfield project is
where wrong assumptions are cheapest to fix and most expensive to discover late.

---

## Artifacts

| Path | From |
|---|---|
| `docs/project-context/` | Bootstrapped at first run |
| `specs/<feature>/requirements.md` | `orchestrator:plan` |
| `specs/<feature>/design.md` | `architect:design` |
| `specs/<feature>/tasks.md` | Task generation |
| `src/`, `tests/`, docs | `implementer:full` |
| `Dockerfile`, CI workflow, IaC manifests | `implementer:docker`, `:pipeline`, `:iac` |
| Pull request | `orchestrator:pr` |

---

## Narrowing the design stage

`architect:design` produces the full topology. When you only need one piece:

| Command | Produces |
|---|---|
| `architect:api` | OpenAPI contract — unblocks parallel front-end and back-end work |
| `architect:schema` | DDL, relationships, indices |
| `architect:frontend` | Component hierarchy, prop APIs, TypeScript interfaces |
| `architect:a11y` | WCAG 2.1 AA plan — retrofitting costs roughly three times as much |

Running `architect:api` early is the highest-leverage move in this workflow: an
agreed contract lets front-end and back-end proceed at once.

---

## Do you need ADRs here?

Yes, for the decisions that will outlive the first release — datastore choice,
service boundaries, auth model. On greenfield everything feels like a decision;
apply the trigger rule from [05](05-record-a-decision.md) and record only what
changes a contract, a data shape, a dependency, or a failure mode.

Record them as you go, via `architect:adr`, not in a batch at the end. A
decision reconstructed a month later is a guess about your own reasoning.

---

## Worked example

[../04-examples/orchestrator.md](../04-examples/orchestrator.md) — E-Commerce MVP,
requirements through launch.
[../04-examples/architect.md](../04-examples/architect.md) — Real-Time Chat,
topology through accessibility.

---

## Next

- [11 — Set up CI/CD](11-set-up-cicd.md) for deployment depth
- [13 — Ship a release](13-ship-a-release.md) once it is merged
