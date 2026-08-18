---
name: ba:clarify Function
description: Resolve ambiguity in discovered requirements — one question at a time, until nothing material is unknown
prefix: ba:clarify
version: 1.0
---

# ba:clarify

**Close the open questions before they become expensive.** Ambiguity resolved
here costs one message; the same ambiguity found during review costs a
re-implementation.

## Inputs

```
ba:clarify
ba:clarify path=./discovery-notes.md
```

- `path` (string, optional) — discovery notes; defaults to the most recent
- `focus` (string, optional) — restrict to one area (`rules`, `scope`, `data`)

## Outputs

```
✓ discovery-notes.md    — updated with resolved answers
✓ open-questions.md     — answered rows filled, unresolvable rows escalated
```

## Workflow

1. Read `open-questions.md` and the discovery notes.
2. Rank questions by **cost of being wrong**, not by order found. A question
   that changes the data model outranks one that changes a label.
3. Ask **one question at a time**. Prefer multiple choice — a stakeholder
   picks faster than they compose.
4. For each answer, write it into `open-questions.md` and propagate the
   consequence into the discovery notes.
5. Stop when every remaining question is either answered or explicitly
   deferred with a named owner and a trigger for revisiting.
6. Where an answer changes a decision already recorded, say so and hand off to
   `architect:adr` — an answer that invalidates a decision needs a new ADR,
   not a quiet edit.

## Question Quality

A good clarifying question is **decidable** (has a small set of answers),
**consequential** (the answers lead to different systems), and **framed in the
stakeholder's language** (no schema talk).

| Weak | Strong |
|---|---|
| "How should this work?" | "When payment times out, do we cancel the order or hold it for retry?" |
| "What are the performance requirements?" | "Is a 3-second checkout acceptable, or is sub-1-second required?" |
| "Any security concerns?" | "Can support staff see full card numbers, or only the last four?" |

## Related Functions

- `ba:discover` — produces the questions this resolves
- `ba:brd` — consumes the clarified output

## Related Skills

- `skills/project_context_skill.md` — `open-questions.md` format
- `instructions/master_instruction_set.md` — RULE 9, RULE 12
