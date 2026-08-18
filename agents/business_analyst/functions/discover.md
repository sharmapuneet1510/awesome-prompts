---
name: ba:discover Function
description: Requirement discovery from an unstructured business discussion — extract goals, actors, flows, and rules
prefix: ba:discover
version: 1.0
---

# ba:discover

**Turn a business conversation into structured requirement material.** The
first hop of the traceability chain. Nothing downstream exists until this runs.

## Inputs

```
ba:discover source="<transcript, notes, email thread, or free text>"
ba:discover path=./discussion-notes.md
```

- `source` (string) — the raw discussion text
- `path` (string) — a file containing it
- `domain` (string, optional) — business domain, to seed the glossary

One of `source` or `path` is required.

## Outputs

```
✓ discovery-notes.md    — goals, actors, flows, rules, constraints, unknowns
✓ open-questions.md     — appended: every ambiguity found
```

## Workflow

1. Read `docs/project-context/business-context.md` if it exists — do not
   re-discover what is already recorded.
2. Extract, keeping the stakeholder's own words where possible:
   - **Goals** — the outcome wanted, and how they would measure it
   - **Actors** — who does what, and who is affected but not present
   - **Business flows** — trigger → steps → outcome
   - **Business rules** — statements that could be true or false of a system
   - **Constraints** — regulatory, budget, timeline, existing systems
3. Label everything per RULE 12. A goal the stakeholder stated is FACT (cite
   the line). A goal you deduced from context is INFERENCE.
4. Separate what was **said** from what was **meant**. Where they differ, that
   is an open question, not a decision to make on their behalf.
5. Record every ambiguity in `open-questions.md` — do not resolve them here.
   Resolution is `ba:clarify`.
6. Do **not** propose solutions. Discovery captures the problem space; a
   solution proposed this early anchors everything that follows.

## Anti-Patterns

| Don't | Do |
|---|---|
| Invent acceptance criteria | Leave them for `ba:brd` |
| Silently resolve vague terms ("fast", "secure") | Log as `Q-n` |
| Merge two stakeholders' conflicting goals | Record both, flag the conflict |
| Skip the "who is affected but absent" question | Ask it every time |

## Related Functions

- `ba:clarify` — resolve the open questions this produced
- `ba:brd` — turn resolved discovery into a BRD
- `ba:create` — generate Jira issues with BDD acceptance criteria

## Related Skills

- `skills/project_context_skill.md` — where business context lands
- `skills/traceability_skill.md` — hop 1 of the chain
