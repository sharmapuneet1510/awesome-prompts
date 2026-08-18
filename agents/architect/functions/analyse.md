---
name: architect:analyse Function
description: Technical analysis of a Jira item against the existing codebase — current flow, impact, options, risks
prefix: architect:analyse
version: 1.0
---

# architect:analyse

**Understand before deciding.** Reads a Jira item and the codebase, explains
how the affected area works today, and identifies what the change touches.
Produces no decisions — decisions are `architect:adr`.

## Inputs

```
architect:analyse jira=PROJ-123
architect:analyse jira=PROJ-123 path=./src
```

- `jira` (string, required) — the Jira item to analyse
- `path` (string, optional) — restrict codebase reading to a subtree
- `depth` (string, optional) — `shallow` (entry points only) | `full` (default)

## Outputs

```
✓ docs/analysis/<JIRA>-technical-analysis.md
✓ docs/project-context/known-behaviours.md    — appended if a quirk is found
✓ docs/project-context/open-questions.md      — appended for each unknown
```

## Analysis Template

```markdown
# Technical Analysis — <PROJ-123>

## Current Flow
FACT: <how the affected path works today, with file:line citations>

## Affected Surface
| Component | Current behaviour | Why the change touches it |
|---|---|---|

## Constraints
FACT: <invariants from architecture-context.md and existing ADRs that bound this>

## Options
### Option A — <name>
<approach> · Cost: <effort> · Risk: <what could go wrong> · Reversible: <yes/no>

### Option B — <name>
...

## Recommendation
PROPOSAL: <option, and the single trade-off that decides it>

## Decisions Required
| # | Question | Blocks | Suggested ADR type |
|---|---|---|---|

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
```

## Workflow

1. Read `docs/project-context/` — technical context, architecture context,
   known behaviours, technical debt. Do not re-derive what is recorded.
2. Read `docs/adr/` for decisions that constrain this area. An existing ADR is
   a boundary, not a suggestion; contradicting one requires superseding it.
3. Read the code. Every claim about current behaviour is FACT and must cite
   `file:line`. If you did not read it, you do not know it.
4. Trace the actual flow end to end — entry point, branches, data mutations,
   failure paths, external calls.
5. Present at least two genuine options. A single-option analysis is a
   decision smuggled in as an analysis.
6. Label rigorously per RULE 12. Current behaviour is FACT. Predicted impact
   is INFERENCE, with its basis named. Your recommendation is PROPOSAL.
7. List every decision this change requires, with the ADR type each would
   take. This list is the input to `architect:adr`.
8. Stop. Do not write code, and do not write the ADRs — present the analysis.

## Anti-Patterns

| Don't | Do |
|---|---|
| Describe how the code *should* work | Describe how it *does*, with citations |
| Recommend without naming the losing option's merits | Show the real trade-off |
| Fold a decision into the analysis prose | Put it in "Decisions Required" |
| Skip the failure paths | Trace them — that is where the ADRs come from |

## Related Functions

- `architect:adr` — records each decision this analysis surfaced
- `architect:spec` — regenerates the spec once ADRs are accepted
- `architect:design` — greenfield design when there is no existing flow

## Related Skills

- `skills/adr_skill.md` · `skills/project_context_skill.md`
- `skills/context_builder_skill.md` — if `docs/context/` is missing
