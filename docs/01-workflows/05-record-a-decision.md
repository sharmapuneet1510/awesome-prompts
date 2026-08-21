# 05 — Record a Decision

**Write the ADR, then regenerate the specification.** The mechanism that keeps
*why* separate from *what*.

Covers [SDLC](sdlc-playbook.md) stages 4–5.

---

## When to use this

Whenever a decision meets the trigger rule — which is more often than it feels,
and always *at the moment of deciding*, never batched at the end of a sprint.

A decision reconstructed a month later is a guess about your own reasoning.

## Prerequisites

- A parent Jira item. Every ADR names one.
- Ideally a technical analysis from
  [04](04-understand-a-codebase.md) — `architect:adr` can source its options
  from one directly.

---

## The trigger rule

Write an ADR when the change alters **a contract, a data shape, a dependency,
or a failure mode**.

| Earns an ADR | Does not |
|---|---|
| Choosing PostgreSQL over MongoDB | Choosing a table's column order |
| Making an endpoint idempotent | Renaming a local variable |
| Adding a queue between two services | Extracting a private helper |
| Changing a retry policy from 3 to unlimited | Bumping a patch dependency |
| Denormalising a table for reads | Reformatting a file |
| Accepting a known race condition | Adding a log line |

Unsure? Ask whether a new engineer six months from now would be confused about
why this is the way it is. If yes, write it.

**Over-producing ADRs is as damaging as under-producing them.** A decision log
nobody reads has the same value as no log at all.

---

## The chain

```
architect:adr jira=PROJ-123 from=./docs/analysis/PROJ-123-technical-analysis.md
    ↓  Status: Proposed — presented for approval
    ↓
    ◆ GATE — you approve: Proposed → Accepted
    ↓
architect:spec                      → Current Technical Specification regenerated
```

Superseding an earlier decision:

```
architect:adr supersede=ADR-0003 decision="drop the Redis session cache" jira=PROJ-140
    ↓  ADR-0003 gets Superseded By: ADR-0009 and flips to Superseded
    ↓  ADR-0003's body is left untouched
architect:spec
```

---

## The lifecycle

```
Draft ──▶ Proposed ──▶ Accepted ──▶ Implemented ──▶ Verified
                          │              │              │
                          └──────────────┴──────────────┴──▶ Superseded ──▶ Archived
```

**Proposed → Accepted is the only human-gated edge in the entire system.** An
agent writes the status into the file, but only after you explicitly approve —
never inferred from silence or a vague acknowledgement.

No transition may skip a state. Only ADRs at Accepted or later feed the
specification; Draft and Proposed are listed as pending.

---

## The record

Thirteen mandatory fields. `none` is a valid value; blank is not.

| Field | Notes |
|---|---|
| ID | `ADR-<NNNN>`, monotonic, never reused |
| Parent Jira | Mandatory — this is hop 2 of the traceability chain |
| Status | One of the seven lifecycle states |
| Decision Type | Exactly one of ten (see below) |
| Context | FACT, with citations |
| Problem | The specific question this answers |
| Options | **At least two genuine ones** |
| Decision | DECISION, active voice |
| Rationale | The specific trade-off that decided it |
| Consequences | Accepted / Enabled / Technical Debt |
| Affected Components | Paths, and how each changes |
| Affected Tests | New, modified, or obsolete |
| Related / Supersedes / Superseded By | Cross-links |

**Decision types** (closed enum, exactly one): Architecture · API · Database ·
Performance · Security · Testing · Deployment · Refactoring · Business Logic ·
Monitoring.

---

## Two rules that carry the weight

**At least two genuine options.** A single-option ADR is a decision that was
never actually made. If the second option is a strawman, go find the real
alternative — it exists, or the decision was trivial and did not need an ADR.

**Consequences must include what gets worse.** An ADR with only upside is
marketing. The `Accepted:` field exists to record the downside you knowingly
took on.

---

## Superseding never rewrites history

When ADR-0009 replaces ADR-0003:

1. ADR-0009 declares `Supersedes: ADR-0003`.
2. ADR-0003 gets `Superseded By: ADR-0009` and flips to Superseded.
3. **ADR-0003's body is left exactly as written.** The reasoning was correct at
   the time; superseding is not a correction.
4. ADR-0009 inherits nothing — it restates its own context and consequences.

A one-way link is a chain violation, caught by `ba:trace` check T-13.

---

## The specification is a projection

`architect:spec` regenerates `docs/current-technical-specification.md` from
scratch every time, from ADRs at Accepted or later.

**Never hand-edit it.** Change an ADR and regenerate. Text that outlives its
decision is exactly the drift this design prevents.

If two Accepted ADRs conflict, `architect:spec` **stops and reports it** rather
than picking a winner. A conflict means a missing supersede link, and picking a
winner would be an agent making a decision — which RULE 12 forbids.

---

## Artifacts

| Path | From |
|---|---|
| `docs/adr/ADR-<NNNN>-<slug>.md` | `architect:adr` |
| `docs/adr/ADR-<target>.md` (reciprocal edit) | When superseding |
| `docs/project-context/technical-debt.md` | New `TD-n` row, if debt incurred |
| `docs/current-technical-specification.md` | `architect:spec` |

---

## Who may write an ADR

Only `architect:adr`. `quality:observe` may emit a PROPOSAL-tagged finding
saying one is needed, but it cannot write one. That separation keeps the
reviewer from also being the decider.

---

## Reference

`skills/adr_skill.md` — the full template, transition table, and supersede rules.
