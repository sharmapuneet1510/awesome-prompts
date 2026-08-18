---
name: architect:adr Function
description: Mint an Engineering Decision Record — allocate ID, draft options, propose, and record the approved decision
prefix: architect:adr
version: 1.0
---

# architect:adr

**The only function that writes an ADR.** Every significant engineering
decision passes through here. Continuous, not a phase — an ADR is written when
the decision is made, not batched at the end of a sprint.

## Inputs

```
architect:adr decision="use Redis for idempotency keys" jira=PROJ-123
architect:adr jira=PROJ-123 from=./docs/analysis/PROJ-123-technical-analysis.md
architect:adr supersede=ADR-0003 decision="drop the Redis session cache"
```

- `decision` (string) — the decision to record
- `jira` (string, required) — Parent Jira
- `from` (string, optional) — technical analysis to source options from
- `supersede` (string, optional) — ADR ID this one replaces
- `type` (string, optional) — decision type; inferred if omitted

## Outputs

```
✓ docs/adr/ADR-<NNNN>-<slug>.md
✓ docs/adr/ADR-<target>.md                      — reciprocal edit, if superseding
✓ docs/project-context/technical-debt.md        — new TD row, if debt incurred
```

## Workflow

1. **Apply the trigger rule.** Does this change a contract, a data shape, a
   dependency, or a failure mode? If not, say so and stop. An ADR log nobody
   reads is worth as much as no log.
2. Allocate the next ID by scanning `docs/adr/` — see `adr_skill.md`.
3. Read the parent Jira, the technical analysis if given, and any related or
   superseded ADRs.
4. Draft all 13 fields. Every field is mandatory; `none` is valid, blank is not.
5. State **at least two genuine options**. If the second option is a strawman,
   the decision was not actually made — go find the real alternative.
6. Fill `Consequences` honestly, including what gets worse. An ADR with only
   upside is marketing.
7. Set `Status: Proposed`. Present the file path and ask for approval.
8. **Wait.** Proposed → Accepted is human-only. Never infer approval from
   silence or a vague acknowledgement.
9. On explicit approval:
   - Set `Status: Accepted`.
   - If superseding: write `Superseded By` into the target and flip it to
     `Superseded`. Leave the target's body untouched.
   - If `Technical Debt` is non-empty: add the `TD-n` row.
   - Hand off to `architect:spec`.

## Refusals

Refuse and report, rather than guessing, when:

- The change does not meet the trigger rule.
- The supersede target does not exist, is already Superseded, or is still at
  Draft/Proposed.
- The decision contradicts an Accepted ADR that is not being superseded.
- No Parent Jira is supplied.

## Example

```bash
architect:adr jira=PROJ-123 from=./docs/analysis/PROJ-123-technical-analysis.md
```

**Output:** `docs/adr/ADR-0012-idempotency-keys-in-redis.md` at `Proposed`,
with two options, the trade-off that decides between them, the accepted
downside (a new Redis dependency on the write path), and the affected
components and tests.

## Related Functions

- `architect:analyse` — surfaces the decisions this records
- `architect:spec` — regenerates the spec from accepted ADRs
- `quality:observe` — may propose an ADR; may not write one

## Related Skills

- `skills/adr_skill.md` — template, lifecycle, decision types, supersede rules
- `instructions/master_instruction_set.md` — RULE 11a, RULE 12
