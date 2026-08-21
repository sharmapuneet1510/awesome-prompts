# 02 — Feature from a Conversation

**The long form.** A stakeholder describes a problem; you end up with shipped
code that is traceable back to what they actually meant.

Covers [SDLC](sdlc-playbook.md) stages 1–13 — the full cycle.

---

## When to use this

- The input is a conversation, email thread, meeting transcript, or a vague ask.
- The codebase already exists.
- The change is substantial enough that implementing the wrong thing would hurt.

**Not this workflow if** you already have an agreed written requirement — use
[03](03-feature-from-requirement.md) and skip to stage 6.

## Prerequisites

- `docs/project-context/` exists. If not, run
  [04 — Understand a codebase](04-understand-a-codebase.md) first.

---

## The chain

```
BA COMPANION ─ what do they actually want?
  ba:discover source="..."      → goals, actors, flows, rules; ambiguities logged
  ba:clarify                    → one question at a time until nothing material is unknown
  ba:brd                        → BRD + business-context.md + mvp-scope.md
  ba:create                     → Jira issues with BDD acceptance criteria
      ↓
DEVELOPER COMPANION ─ how does it work, and what must we decide?
  architect:analyse jira=PROJ-123 → current flow (FACT, cited), options, decisions required
  architect:adr jira=PROJ-123     → one ADR per decision              ◆ GATE
  architect:spec                  → Current Technical Specification regenerated
      ↓
PLANNING ─ the spec-driven gate
  orchestrator:plan             → requirements.md                     ◆ GATE
  architect:design              → design.md                           ◆ GATE
  [task generation]             → tasks.md                            ◆ GATE
      ↓
CODING COMPANION
  implementer:full              → code + tests + docs
      ↓
REVIEW & QA COMPANIONS
  quality:observe               → 4-way conformance gaps, observations only
  quality:qa                    → the five reusable suites
      ↓
RELEASE
  orchestrator:pr               → pull request
  ba:trace                      → 18 traceability checks
```

---

## Why the first four stages are not optional

`ba:discover` and `ba:clarify` look like overhead. They are the cheapest part of
the workflow, and they replace the most expensive failure: building precisely
the wrong thing.

Three rules that make them work:

1. **Discovery proposes no solutions.** A solution offered this early anchors
   everything downstream. Capture the problem space only.
2. **`ba:clarify` asks one question at a time.** A batch of six gets three
   answered, and the three that get skipped are usually the awkward ones that
   mattered.
3. **Questions are ranked by cost of being wrong**, not by the order they were
   found. A question that changes the data model outranks one that changes a
   label.

---

## Gates

| After | You approve | Notes |
|---|---|---|
| `architect:adr` | Each ADR: Proposed → Accepted | **The only human-gated edge in the whole system.** Never inferred from silence |
| `orchestrator:plan` | `requirements.md` | RULE 11 |
| `architect:design` | `design.md` | RULE 11 |
| Task generation | `tasks.md` | RULE 11 |

---

## Artifacts

| Path | From |
|---|---|
| `discovery-notes.md`, `open-questions.md` | `ba:discover`, `ba:clarify` |
| `docs/brd.md`, `business-context.md`, `mvp-scope.md` | `ba:brd` |
| Jira issues + acceptance criteria | `ba:create` |
| `docs/analysis/<JIRA>-technical-analysis.md` | `architect:analyse` |
| `docs/adr/ADR-<NNNN>-<slug>.md` | `architect:adr` |
| `docs/current-technical-specification.md` | `architect:spec` |
| `specs/<feature>/requirements.md`, `design.md`, `tasks.md` | Planning stages |
| `src/`, `tests/`, docs | `implementer:full` |
| `docs/observations/<PR>-observations.md` | `quality:observe` |
| `docs/project-context/quality/*.md` | `quality:qa` |
| `docs/traceability-report-<date>.md` | `ba:trace` |

---

## Labels you will see

Every substantive claim carries one, per RULE 12:

```
FACT: OrderService.submit() has no idempotency key (src/order/service.py:88).
INFERENCE: retries during the payment timeout window likely double-charge.
PROPOSAL: add a client-supplied Idempotency-Key header, deduped in Redis.
DECISION: approved 2026-08-18 — see ADR-0012.
```

**Only DECISION changes the Current Technical Specification.** If you see an
agent treat its own PROPOSAL as settled, that is a bug worth reporting.

---

## Worked example

None yet. The example library predates the companion functions. Until it
catches up, the function files are the closest thing to a walkthrough:
`agents/business_analyst/functions/` and `agents/architect/functions/`.

---

## Next

- [05 — Record a decision](05-record-a-decision.md) for ADR mechanics in depth
- [13 — Ship a release](13-ship-a-release.md)
