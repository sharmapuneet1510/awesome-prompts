# Rules Reference

**Four principles and thirteen rules** that every agent follows without
exception. Source: `instructions/master_instruction_set.md` (v2.2).

---

## Foundational principles

Not rules to satisfy — how the agents operate.

| Principle | Means | Applies to |
|---|---|---|
| **Think Before Coding** | State assumptions. Present two or three interpretations when ambiguous. Push back with simpler approaches. Stop when confused rather than guessing. | Every task |
| **Simplicity First** | The minimum code that solves the problem. No speculative abstraction. | All generation |
| **Surgical Changes** | Touch only what you must. Clean up only your own mess. | All modification |
| **Goal-Driven Execution** | Define success criteria upfront; loop until verified. | Every task |

---

## RULES 0–9 — the working rules

| Rule | Requires |
|---|---|
| **0 — Check Before You Code** | Verify versions and existing patterns first |
| **1 — Ask Before You Build** | New projects start with an intake Q&A |
| **2 — Always Generate Tests** | Every change ships tests. `givenXxx_whenYyy_thenZzz` naming, Arrange-Act-Assert structure |
| **3 — OOP Principles** | All four pillars plus SOLID, with examples |
| **4 — Documentation** | Javadoc, docstrings, JSDoc — written for the next developer |
| **5 — Simple Code** | No cleverness. Methods ≤ 20 lines, classes ≤ 300 |
| **6 — Code Output Format** | Consistent presentation of generated code |
| **7 — Project Structure** | Conventional layout per stack |
| **8 — Security** | Parameterised queries, input validation, no secrets in logs |
| **9 — When Unsure, Ask** | Ask rather than guess |

---

## RULE 10 — Surgical Precision & Token Efficiency

Five practices: surgical modification, diff-only outputs, graph-style context
curation, token and memory efficiency, and a defined execution workflow.

Applies to every implementation task, refactor, and multi-file change.

---

## RULE 11 — Spec-Driven Gate

**No implementation code for a feature until `requirements.md`, `design.md`, and
`tasks.md` all exist and carry `Status: Approved`** — set by you, never inferred
by an agent.

| Stage | Function | Artifact | Blocked until |
|---|---|---|---|
| specify | `orchestrator:plan` | `specs/<feature>/requirements.md` | — |
| plan | `architect:design` | `specs/<feature>/design.md` | requirements approved |
| tasks | task generation | `specs/<feature>/tasks.md` | design approved |
| implement | `implementer:build` / `:full` | code, tests, docs | tasks approved |

**Exempt:** one-line fixes, config tweaks, small documentation edits.
**Not exempt:** substantive changes to agent, skill, or instruction files.

An agent may write `Status: Approved` into a file, but only after you have
explicitly said so — never from silence or a vague acknowledgement.

---

## RULE 11a — ADR Gate

**A change that alters a contract, a data shape, a dependency, or a failure mode
requires an Accepted ADR before the code is written.**

- `architect:adr` is the only function that mints an ADR. `quality:observe` may
  propose one; it may not write one.
- Proposed → Accepted is human-only.
- `implementer:build` / `:full` refuses a decision-bearing change with no
  Accepted ADR citing its Parent Jira.
- Accepting an ADR triggers `architect:spec`. Nothing else may edit the Current
  Technical Specification.

Trigger examples in [../01-workflows/05-record-a-decision.md](../01-workflows/05-record-a-decision.md).

---

## RULE 12 — Label What You Know

**Every substantive claim carries one of four labels. Only a DECISION may change
the Current Technical Specification.**

This prevents the most common failure in AI-assisted engineering: a plausible
guess gets written down, read back as established truth, and becomes the
foundation for the next three decisions.

| Label | Means | Obligation |
|---|---|---|
| **FACT** | Verified from code, docs, tool output, or a cited source | Must cite. An uncited FACT is an INFERENCE in disguise |
| **INFERENCE** | Reasoned from facts; probably right; could be wrong | State what it rests on |
| **PROPOSAL** | A recommendation awaiting a human | Never self-approve. Never implement |
| **DECISION** | Approved by a human | Only ever recorded by an agent, never originated |

**Applies to:** technical analysis, ADRs, review findings, audit reports,
traceability reports, architecture proposals, Project Context.

**Does not apply to:** conversational replies, code comments, commit messages,
docstrings. Labelling everything makes labelling worthless.

```
FACT: OrderService.submit() has no idempotency key (src/order/service.py:88).
INFERENCE: retries during the payment timeout window likely double-charge —
  based on the retry policy in config/http.yaml and the missing key above.
PROPOSAL: add a client-supplied Idempotency-Key header, deduped in Redis.
DECISION: approved 2026-08-18 — see ADR-0012.
```

**Legal transitions:** INFERENCE → FACT (once verified, with a citation) and
PROPOSAL → DECISION (once a human approves). An agent performing the second on
its own is the most serious violation in the instruction set.

---

## Gate summary

| Gate | Rule | Blocks | Released by |
|---|---|---|---|
| Requirements approved | 11 | `architect:design` | You approve `requirements.md` |
| Design approved | 11 | Task generation | You approve `design.md` |
| Tasks approved | 11 | `implementer:build` / `:full` | You approve `tasks.md` |
| ADR accepted | 11a | Implementing a decision-bearing change | You approve the ADR |
| Traceability clean | 11a | `implementer:build`, release | High findings resolved |
| Label discipline | 12 | Specification mutation | Only a human-approved DECISION |

---

## See also

- `instructions/master_instruction_set.md` — the full text
- [../01-workflows/README.md](../01-workflows/README.md) — where each gate lands
- [skills.md](skills.md) — `spec_driven_development_skill`, `adr_skill`, `traceability_skill`
