---
name: ba:brd Function
description: Generate the Business Requirements Document — goals, rules, flows, glossary — and populate Business Context
prefix: ba:brd
version: 1.0
---

# ba:brd

**Produce the BRD and the business half of the Project Context.** This is the
artifact the technical companions read before they touch anything.

## Inputs

```
ba:brd
ba:brd path=./discovery-notes.md
```

- `path` (string, optional) — clarified discovery notes
- `scope` (string, optional) — `mvp` to restrict output to MVP scope

## Outputs

```
✓ docs/brd.md                                    — the Business Requirements Document
✓ docs/project-context/business-context.md       — goals, stakeholders, flows, rules, glossary
✓ docs/project-context/mvp-scope.md              — in scope, out of scope, definition of done
```

## Workflow

1. Confirm `open-questions.md` has no unanswered High-cost question. If it
   does, stop and run `ba:clarify` first.
2. Assign stable IDs: `G-n` goals, `BR-n` business rules, `BF-n` flows. These
   IDs are cited by acceptance criteria, ADRs, and tests forever — choose them
   once and never renumber.
3. Write each business rule as a **testable statement**. "Orders must be
   validated" is not a rule; "an order with zero line items is rejected" is.
4. Build the domain glossary with a `Does not mean` column. Most integration
   defects trace to two teams using one word for two things.
5. Fill `mvp-scope.md`, including the **out of scope** table. What was
   deliberately excluded, and why, is as valuable as what was included.
6. Label per RULE 12 — stakeholder-stated goals are FACT with a citation,
   derived goals are INFERENCE, and anything you are recommending is PROPOSAL.
7. Present for approval. The BRD is a gate: `architect:analyse` should not
   run against an unapproved BRD.

## Quality Bar

- Every goal has a metric. A goal without one cannot be shown to be met.
- Every business rule names where it will be enforced.
- Every assumption states what happens if it turns out to be wrong.
- No requirement contains "etc.", "and so on", or "as appropriate".

## Related Functions

- `ba:clarify` — must run first
- `ba:create` — generates Jira issues with BDD acceptance criteria from this
- `architect:analyse` — the next hop

## Related Skills

- `skills/ba_create_skill.md` — Jira issue and acceptance-criteria generation
- `skills/project_context_skill.md` — business context templates
