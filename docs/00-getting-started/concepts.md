# Concepts

**Four words that get confused**, and the idea that ties them together.

---

## Agent, skill, function, gate

| Term | Is | Count | Example |
|---|---|---|---|
| **Agent** | A role that decides and dispatches | 5 | Architect |
| **Function** | One callable capability of an agent | 42 | `architect:adr` |
| **Skill** | Implementation knowledge a function loads | 35 | `adr_skill` |
| **Gate** | A refusal that blocks progress until you approve | 6 | RULE 11a, ADR accepted |

```
You invoke a FUNCTION on an AGENT.
The function loads whichever SKILLS it needs.
A GATE may stop it and ask you to approve something.
```

An agent knows *what*; a skill knows *how*. That split is why adding Rust
support means adding one skill rather than one agent.

---

## Why decisions are separate from state

The idea the whole system is built on: **what is true now** and **why it became
true** are different documents, and conflating them destroys both.

| Question | Document | Property |
|---|---|---|
| How does this work today? | `current-technical-specification.md` | Regenerated. Only current truth |
| Why is it like this? | `docs/adr/` | Immutable. Includes paths not taken |

The specification is a **projection** of Accepted ADRs, rebuilt from scratch
each time. It never contains an outdated claim, because prose no surviving
decision supports is dropped on regeneration.

ADRs are never edited or deleted, even when superseded. A superseded ADR is not
wrong — it was correct when written, and that record is what stops someone
re-introducing the design it replaced.

Ordinary documentation fails at exactly this point: it accumulates. A file
gathers three years of decisions, half of them reversed, and no reader can tell
which sentences are still true.

---

## Labels

Every substantive claim an agent makes carries one of four labels (RULE 12):

| Label | Means |
|---|---|
| **FACT** | Verified, with a citation |
| **INFERENCE** | Reasoned; could be wrong |
| **PROPOSAL** | Awaiting your approval |
| **DECISION** | You approved it |

```
FACT: OrderService.submit() has no idempotency key (src/order/service.py:88).
INFERENCE: retries during the payment timeout window likely double-charge.
PROPOSAL: add an Idempotency-Key header, deduped in Redis.
DECISION: approved 2026-08-18 — see ADR-0012.
```

**Only DECISION changes the specification.** This exists to stop the most common
failure in AI-assisted engineering: a plausible guess written down, read back as
truth, and used as the foundation for three more decisions.

If you see an agent treat its own PROPOSAL as settled, that is a bug.

---

## Gates

Six gates. All are **refusals, not warnings** — an agent stops rather than
proceeding with a caveat, because a warning gets scrolled past.

| Gate | Blocks | You release it by |
|---|---|---|
| Requirements approved | `architect:design` | Approving `requirements.md` |
| Design approved | Task generation | Approving `design.md` |
| Tasks approved | `implementer:build` | Approving `tasks.md` |
| ADR accepted | Decision-bearing code | Approving the ADR |
| Traceability clean | Build, release | Resolving High findings |
| Label discipline | Specification changes | Only DECISION qualifies |

**Trivial work is exempt** from the spec gates — one-line fixes, config tweaks,
small doc edits.

Detail: [../02-reference/rules.md](../02-reference/rules.md).

---

## The companions

Five roles from the platform requirement, mapped onto the same five agents
rather than adding new ones:

| Companion | Is |
|---|---|
| BA | `ba:discover` → `clarify` → `brd` → `create` |
| Developer | `architect:analyse` → `adr` → `spec` |
| Coding | `implementer:full` |
| Review | `quality:observe` — observations only |
| QA | `quality:qa` — five reusable suites |

---

## Two artifact destinations

Frequently confused:

| Location | Holds |
|---|---|
| **The project you are working on** | `docs/adr/`, `docs/project-context/`, `specs/<feature>/` |
| **This repository** | Only this repo's own design records, in `docs/superpowers/` |

Unless stated otherwise, artifacts land in the project being worked on.

---

## What this is not

**Not a runtime.** No service, no database, no UI. Every "agent" is a markdown
file of instructions that an AI assistant reads. The gates are behavioural
instructions, not enforced by software — they work because the agent follows
them.

**Not Claude-only.** Everything exports to eight platforms —
[../01-workflows/14-export-to-platforms.md](../01-workflows/14-export-to-platforms.md).

---

## Next

- [quick-start.md](quick-start.md) — run something
- [../01-workflows/README.md](../01-workflows/README.md) — pick your task
- [../02-reference/](../02-reference/) — look something up
