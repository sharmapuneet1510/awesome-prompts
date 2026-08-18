---
name: ADR Skill
version: 1.0
description: >
  Reusable skill for Engineering Decision Records. Defines the ADR record,
  its seven-state lifecycle, the ten decision types, ID allocation, and the
  supersede chain. Owned by architect:adr; read by current_tech_spec_skill,
  traceability_skill, and quality:observe. Enforced by RULE 11 in
  instructions/master_instruction_set.md.
---

# ADR Skill — v1.0

## Purpose

Capture every significant engineering decision as a lightweight, immutable
record so that the *reasoning* behind a system is preserved separately from
its *current state*. Current state lives in the Current Technical
Specification; reasoning lives here.

This skill is **internal** — called by agents, not invoked directly by users.
`architect:adr` is its only writer.

---

## Artifact Location

ADRs live in the **downstream project** being built, not in this repo:

```
<project-root>/docs/adr/
├── ADR-0001-postgres-over-mongo.md
├── ADR-0002-idempotent-order-endpoint.md
└── ADR-0003-drop-redis-session-cache.md
```

Keep distinct from `specs/<feature-name>/` (the RULE 11 requirements → design
→ tasks chain, see `spec_driven_development_skill.md`) and from
`docs/project-context/` (see `project_context_skill.md`).

---

## When a Decision Earns an ADR

Write an ADR when the decision changes **a contract, a data shape, a
dependency, or a failure mode**. Concretely:

| Earns an ADR | Does not |
|---|---|
| Choosing PostgreSQL over MongoDB | Choosing a table's column order |
| Making an endpoint idempotent | Renaming a local variable |
| Adding a queue between two services | Extracting a private helper method |
| Changing a retry policy from 3 to unlimited | Bumping a patch dependency version |
| Denormalising a table for read performance | Reformatting a file |
| Accepting a known race condition | Adding a log line |

If unsure, ask: *would a new engineer six months from now be confused about
why this is the way it is?* If yes, write the ADR.

Over-producing ADRs is as damaging as under-producing them — a decision log
nobody reads has the same value as no log at all.

---

## ID Allocation

1. Scan `docs/adr/` for filenames matching `ADR-(\d{4})-`.
2. Take the highest number found; the new ID is that plus one. If the
   directory is empty or absent, start at `ADR-0001`.
3. Zero-pad to four digits. IDs are monotonic and **never reused**, even if
   an ADR is archived or deleted.
4. Filename: `ADR-<NNNN>-<kebab-slug>.md`, where the slug is a three-to-six
   word summary of the decision, not the problem.

---

## Record Template

```markdown
# ADR-<NNNN>: <decision, stated as an outcome>

**Status:** Draft
**Decision Type:** <one of the ten types below>
**Parent Jira:** <PROJ-123>
**Date:** <YYYY-MM-DD>
**Supersedes:** <ADR-NNNN | none>
**Superseded By:** <ADR-NNNN | none>
**Related ADRs:** <ADR-NNNN, ADR-NNNN | none>

## Context
FACT: <what is true about the system today; cite files, tickets, or metrics>

## Problem
<the specific question this ADR answers, in one or two sentences>

## Options
### Option A — <name>
<description> · Pros: <...> · Cons: <...>

### Option B — <name>
<description> · Pros: <...> · Cons: <...>

## Decision
DECISION: <what was chosen, in the active voice>

## Rationale
<why this option beat the others; reference the specific trade-off that
decided it>

## Consequences
**Accepted:** <what gets worse, and that this is knowingly accepted>
**Enabled:** <what becomes possible>
**Technical Debt:** <debt incurred, or "none" — if non-empty, this must be
mirrored into docs/project-context/technical-debt.md>

## Affected Components
- <path/to/component> — <how it changes>

## Affected Tests
- <path/to/test> — <new | modified | obsolete>
```

Every field is mandatory. `none` is a valid value; a blank is not.

The `FACT:` and `DECISION:` prefixes are RULE 12 labels — see
`instructions/master_instruction_set.md`.

---

## Decision Types

Exactly one per ADR. Closed enum — do not invent new types.

| Type | Covers |
|---|---|
| `Architecture` | Topology, service boundaries, layering, sync vs async |
| `API` | Endpoint contracts, versioning, auth schemes, error shapes |
| `Database` | Engine choice, schema shape, indexing, partitioning, migration |
| `Performance` | Caching, batching, denormalisation, concurrency limits |
| `Security` | AuthN/AuthZ, secrets, encryption, threat mitigations |
| `Testing` | Test strategy, coverage targets, fixture and mock policy |
| `Deployment` | Environments, rollout strategy, IaC, rollback mechanism |
| `Refactoring` | Structural change with no behaviour change |
| `Business Logic` | Domain rules encoded in code, calculation policy |
| `Monitoring` | Metrics, traces, logs, alert thresholds, SLOs |

If a decision genuinely spans two types, pick the one a reader would search
for first and list the other in `Related ADRs`.

---

## Lifecycle

```
Draft ──▶ Proposed ──▶ Accepted ──▶ Implemented ──▶ Verified
                          │              │              │
                          └──────────────┴──────────────┴──▶ Superseded ──▶ Archived
  │
  └──▶ Archived  (abandoned before proposal)
```

| From | To | Who | Condition |
|---|---|---|---|
| Draft | Proposed | agent | All template fields populated, at least two options |
| Draft | Archived | agent | Decision abandoned before review |
| Proposed | Accepted | **human only** | Explicit user approval |
| Proposed | Draft | agent | User requested changes |
| Accepted | Implemented | agent | Code merged in the PR that cites this ADR |
| Implemented | Verified | agent | Affected Tests pass and `quality:observe` finds no ADR↔Code gap |
| Accepted / Implemented / Verified | Superseded | agent | A newer ADR declares `Supersedes:` this one |
| Superseded | Archived | agent | Affected components no longer exist |

**Rules:**

- Proposed → Accepted is the only human-gated edge. An agent may write the
  status into the file, but only after the user explicitly approves — never
  inferred from silence or a vague acknowledgement.
- No transition may skip a state. Any other transition is illegal; refuse it
  and name the legal ones.
- Only ADRs at **Accepted or later** feed the Current Technical Specification.
  Draft and Proposed ADRs are listed as pending and excluded from the
  projection.
- A Superseded or Archived ADR is **immutable**. It is never edited (beyond
  the one-time `Superseded By` stamp) and never deleted. This is what keeps
  historical reasoning separate from current state.

---

## Supersede Chain

When ADR-0009 replaces ADR-0003:

1. ADR-0009 sets `Supersedes: ADR-0003`.
2. The agent **must** make the reciprocal edit: ADR-0003 gets
   `Superseded By: ADR-0009` and `Status: Superseded`.
3. ADR-0003's body is left untouched. The reasoning it recorded was correct
   at the time; superseding is not a correction.
4. ADR-0009 inherits nothing automatically — it restates its own Context,
   Consequences, and Affected Components in full.

**Refuse and report** if the target does not exist, is already Superseded, or
is still at Draft/Proposed (nothing accepted to supersede yet).

A one-way link is a chain violation. `traceability_skill` checks for it.

---

## Workflow (`architect:adr`)

1. Confirm the decision meets the trigger rule above. If not, say so and stop.
2. Allocate the next ID.
3. Read `docs/project-context/` for existing constraints, and `docs/adr/` for
   ADRs this one relates to or supersedes.
4. Draft the record. State at least two genuine options — a single-option ADR
   is a decision that was never actually made.
5. Label every claim per RULE 12. Context is FACT (cited) or INFERENCE.
   The proposed choice is PROPOSAL until the user approves.
6. Move to Proposed. Present the file path and ask for approval.
7. On explicit approval: set Accepted, apply any supersede edits, and mirror
   non-empty Technical Debt into `docs/project-context/technical-debt.md`.
8. Hand off to `architect:spec` to regenerate the Current Technical
   Specification.

---

## Related

- `skills/current_tech_spec_skill.md` — projects Accepted ADRs into the spec
- `skills/traceability_skill.md` — validates ADR links and supersede chains
- `skills/project_context_skill.md` — receives technical debt from ADRs
- `skills/spec_driven_development_skill.md` — the requirements/design/tasks gate
- `instructions/master_instruction_set.md` — RULE 11, RULE 12
