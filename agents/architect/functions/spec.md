---
name: architect:spec Function
description: Regenerate the Current Technical Specification as a projection of Accepted-or-later ADRs
prefix: architect:spec
version: 1.0
---

# architect:spec

**Regenerate the current-state document.** The Current Technical Specification
is a projection of the ADR log, never hand-authored. This function rebuilds it
from scratch every time.

## Inputs

```
architect:spec
architect:spec since=ADR-0009
architect:spec dry-run=true
```

- `since` (string, optional) — summarise changes since this ADR
- `dry-run` (boolean, optional) — show the diff without writing

## Outputs

```
✓ docs/current-technical-specification.md         — regenerated, version bumped
✓ docs/project-context/technical-context.md       — synced
✓ docs/project-context/architecture-context.md    — synced
```

## Workflow

1. Read every file in `docs/adr/`.
2. Select ADRs at **Accepted, Implemented, or Verified**. Exclude Draft and
   Proposed (not yet decided), Superseded and Archived (no longer current).
3. **Detect conflicts** between selected ADRs. If two accepted ADRs disagree,
   stop and report it as a missing supersede link. Do not pick a winner — that
   would be an agent making a decision, which RULE 12 forbids.
4. Group ADRs into the ten sections by decision type (mapping in
   `current_tech_spec_skill.md`).
5. Regenerate the whole document. **Do not** carry forward prose from the
   previous version that no surviving ADR supports — that text is exactly the
   drift this function exists to remove.
6. Cite the source ADR IDs in every section. A section with no citation is a
   finding, not something to leave quiet.
7. Append the pending list (Draft and Proposed ADRs) so a reader sees what is
   about to change.
8. Bump the version, diff against the previous, and summarise what changed and
   which ADR caused each change.
9. Sync technical and architecture context in the Project Context.

## Invariants

- Only a human-approved DECISION triggers regeneration. FACT, INFERENCE, and
  PROPOSAL never mutate this document.
- Every spec section carries at least one ADR citation.
- No other function may write `current-technical-specification.md`.

## Example

```bash
architect:spec since=ADR-0009
```

**Output:** spec v7, sourced from 11 accepted ADRs; section 4 (APIs) changed
because ADR-0012 added the idempotency contract; ADR-0003 dropped out of
section 7 because ADR-0009 superseded it; one Proposed ADR listed as pending.

## Related Functions

- `architect:adr` — the only source of spec content
- `ba:trace` — validates spec ↔ ADR ↔ code links
- `quality:observe` — compares the spec against the code

## Related Skills

- `skills/current_tech_spec_skill.md` — projection rule, template, versioning
- `skills/adr_skill.md` · `skills/traceability_skill.md`
