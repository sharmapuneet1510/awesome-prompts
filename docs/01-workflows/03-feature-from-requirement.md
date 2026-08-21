# 03 — Feature from a Requirement

**The common case.** You have a ticket or a written requirement. Turn it into
merged code without losing the thread between them.

Covers [SDLC](sdlc-playbook.md) stages 6–13.

---

## When to use this

- A written requirement, Jira ticket, or spec already exists and is agreed.
- The codebase exists.

**Not this workflow if** the requirement is really a conversation that has not
been pinned down yet — use [02](02-feature-from-conversation.md). The tell is
whether you can state the acceptance criteria without asking anyone.

## Prerequisites

- A written requirement or ticket.
- `docs/project-context/` — see [04](04-understand-a-codebase.md) if missing.

---

## The chain

```
(architect:analyse jira=PROJ-123)   ← if the affected area is unfamiliar
(architect:adr jira=PROJ-123)       ← if the change is decision-bearing  ◆ GATE
    ↓
orchestrator:plan                   → requirements.md                   ◆ GATE
    ↓
architect:design                    → design.md                         ◆ GATE
    ↓
[task generation]                   → tasks.md                          ◆ GATE
    ↓
implementer:full path=./specs/<feature>
    ↓
quality:observe pr=<n>              → conformance gaps
quality:review pr=<n>               → score + fix proposals
    ↓
orchestrator:pr
```

---

## When do I need an ADR?

Apply the trigger rule. Does the change alter **a contract, a data shape, a
dependency, or a failure mode**?

| Needs an ADR | Does not |
|---|---|
| Making an endpoint idempotent | Renaming a local variable |
| Adding a queue between two services | Extracting a private helper |
| Changing a retry policy | Bumping a patch dependency |
| Denormalising a table for reads | Reformatting a file |
| Accepting a known race condition | Adding a log line |

If it does, `implementer:build` **refuses** without an Accepted ADR. That is
RULE 11a, and it is a refusal rather than a warning on purpose — a warning gets
scrolled past.

Detail: [05 — Record a decision](05-record-a-decision.md).

---

## Gates

| After | You approve |
|---|---|
| `architect:adr` (if used) | ADR: Proposed → Accepted |
| `orchestrator:plan` | `requirements.md` |
| `architect:design` | `design.md` |
| Task generation | `tasks.md` |

`requirements.md` uses EARS-format acceptance criteria with stable `REQ-n` IDs.
Those IDs are cited by tasks, tests, and the traceability report — they are
permanent, so do not renumber them later.

---

## Artifacts

| Path | From |
|---|---|
| `specs/<feature>/requirements.md` | `orchestrator:plan` |
| `specs/<feature>/design.md` | `architect:design` |
| `specs/<feature>/tasks.md` | Task generation — every row cites a `REQ-n` |
| `src/`, `tests/`, docs | `implementer:full` |
| `docs/observations/<PR>-observations.md` | `quality:observe` |

---

## Prefer `implementer:full`

`implementer:build`, `:test`, and `:doc` exist for when you need one piece. For
a whole feature, run `implementer:full` — it does all three in one context
window. Splitting them across three invocations loses the context that connects
the code to its tests to its documentation, and the seams show.

---

## Worked example

[../04-examples/implementer.md](../04-examples/implementer.md) — Auth service:
build, test, doc, then pipeline, Docker, and Kubernetes.

---

## Next

- [06 — Review a pull request](06-review-a-pull-request.md)
- [13 — Ship a release](13-ship-a-release.md)
