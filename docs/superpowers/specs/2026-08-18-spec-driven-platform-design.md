# AI Spec-Driven Development Platform — Design

**Date:** 2026-08-18
**Source requirement:** `requirements-18082026.md`
**Status:** Approved

## Problem

`requirements-18082026.md` describes an AI-first engineering platform where the
specification is the single source of truth, engineering decisions are captured
as immutable ADRs, and five role-based companions collaborate through a shared
Project Context.

This repository already implements a thin slice of that vision: RULE 11 (the
spec-driven gate), `skills/spec_driven_development_skill.md`, and five
role-based agents. Four pieces of the requirement do not exist yet:

1. The ADR system — template, lifecycle, decision types, supersede chain.
2. The Central Project Context — the 14-node knowledge tree.
3. The Current Technical Specification — a latest-approved-design-only artifact.
4. The FACT / INFERENCE / PROPOSAL / DECISION labelling rule.

## Decisions taken

| Question | Decision |
|---|---|
| Deliverable form | Prompt-layer artifacts only — markdown skills, agent functions, instruction rules. No new runtime. |
| Increment size | All of it in one pass. |
| Companion mapping | Extend the existing 5 agents with new functions. Do not add new agents. |
| Artifact location | Downstream project (`docs/adr/`, `docs/project-context/`), not this repo. |
| Template location | Inline inside skills, matching `spec_driven_development_skill.md`. No new top-level `templates/` directory. |

## Architecture

Nothing runs. The platform is a set of instructions that agents load, so the
"architecture" is a dependency graph between markdown files.

```
instructions/master_instruction_set.md
  ├── RULE 11 (extended) ── gates code on approved spec + ADR
  └── RULE 12 (new) ─────── epistemic labelling, binds all 5 agents
          │
          ▼
skills/
  ├── adr_skill.md ─────────────── owns the ADR record and its lifecycle
  ├── current_tech_spec_skill.md ─ projects Accepted ADRs into the spec
  ├── project_context_skill.md ─── owns the 14-node knowledge tree
  ├── traceability_skill.md ────── validates the 8-hop chain
  └── spec_driven_development_skill.md (existing) ── requirements/design/tasks
          │
          ▼
agents/
  ├── business_analyst : discover, clarify, brd, trace   (new)
  ├── architect        : analyse, adr, spec              (new)
  ├── implementer      : build (gated), full             (existing)
  └── quality          : observe, qa                     (new)
```

`adr_skill` is the root dependency: `current_tech_spec_skill` reads ADRs,
`traceability_skill` validates links through them, and `project_context_skill`
cites them. Nothing depends on `traceability_skill`, which makes it safe to
change last.

## Components

### `skills/adr_skill.md`

The 13-field record from requirement §5, plus the mechanics the requirement
leaves unspecified:

- **ID allocation.** `ADR-<NNNN>`, zero-padded to four digits, monotonic.
  Allocated by scanning `docs/adr/` for the highest existing number and adding
  one. Filename is `ADR-<NNNN>-<kebab-slug>.md`.
- **Lifecycle.** Draft → Proposed → Accepted → Implemented → Verified →
  Superseded → Archived, with a table of legal transitions. Proposed → Accepted
  is the human-approval edge; an agent may never cross it alone.
- **Supersede chain.** Writing `Supersedes: ADR-000X` forces a reciprocal
  `Superseded By:` edit on the target and flips it to Superseded. Superseded
  ADRs are never edited otherwise and never deleted — this is what separates
  current state from historical reasoning.
- **Decision types.** The ten from §5 as a closed enum. Exactly one per ADR.
- **Trigger rule.** What earns an ADR: a change to a contract, a data shape, a
  dependency, or a failure mode. Naming a variable does not.

### `skills/project_context_skill.md`

Renders requirement §4's tree as `docs/project-context/`, one file per node,
each with an inline template. Adds an **ownership matrix** the requirement does
not specify — which companion writes each node, and on what event:

| Node | Owner | Written when |
|---|---|---|
| Business Context | `business_analyst` | after `brd` |
| Technical / Architecture Context | `architect` | after `spec` |
| Technical Debt | `architect` | on ADR with a debt consequence |
| Quality Context (5 suites) | `quality` | after `qa` |
| Risks, Release History | `orchestrator` | at plan and release |
| AI Memory | any | append-only, timestamped |

### `skills/current_tech_spec_skill.md`

The Current Technical Specification is a **projection, never hand-authored**.
It is regenerated from the set of ADRs at status Accepted or later, using the
ten sections from requirement §7. Every section cites the ADR IDs that produced
it, so any line can be traced back to a decision. The same skill carries the
Final Implementation Record from §8.

### `skills/traceability_skill.md`

The eight-hop chain from §9 (Requirement → Jira → ADR → Technical Specification
→ Implementation → Tests → PR → Release), expressed as link fields on each
artifact plus a set of validation checks — orphan detection in both directions,
supersede-chain integrity, and status-ordering (no Implemented ADR under a Draft
spec).

### RULE 12 — Epistemic Labelling

Requirement §10 becomes a universal rule. Every substantive claim an agent makes
carries one of four labels: **FACT** (verified, must cite a source), **INFERENCE**
(reasoned, may be wrong), **PROPOSAL** (awaiting a human), **DECISION**
(human-approved). Only DECISION mutates the Current Technical Specification.

Scoped to analysis, ADR, review, and spec output. It does not apply to
conversational replies or code comments, which would make it unusable.

### Companion functions

Nine new function files, in the existing `agents/<agent>/functions/*.md` idiom,
each registered as a row in its parent agent's dispatch table.

| Function | Companion role (§3) |
|---|---|
| `ba:discover`, `ba:clarify`, `ba:brd`, `ba:trace` | BA Companion |
| `architect:analyse`, `architect:adr`, `architect:spec` | Developer Companion |
| `implementer:full` (existing, gate added to `build`) | Coding Companion |
| `quality:observe` | Review Companion |
| `quality:qa` | QA Companion |

`quality:observe` is deliberately distinct from the existing `quality:review`:
review scores and may propose fixes; observe only reports the four comparisons
from §3 (Requirement↔Code, ADR↔Code, Spec↔Code, Tests↔AC) and never edits code.
Both are kept.

## Resolved ambiguity

Requirement §3 says the Review Companion produces observations only, while §5
says ADRs are created continuously by the Developer Companion. The requirement
does not say what happens when review observes a gap that should become an ADR.

**Resolution:** `quality:observe` emits a PROPOSAL-tagged finding. Only
`architect:adr` can mint an ADR.

## Data flow

```
business discussion
  → ba:discover → ba:clarify → ba:brd → ba:create        (Jira + acceptance criteria)
  → architect:analyse                                     (technical analysis, FACT/INFERENCE)
  → architect:adr        (continuous, one per decision)   (PROPOSAL → human → DECISION)
  → architect:spec       (projection of Accepted ADRs)    (Current Technical Specification)
  → orchestrator:plan                                     (implementation plan)
  → implementer:full                                      (code + tests + docs)
  → orchestrator:pr                                       (pull request)
  → quality:observe                                       (4 comparisons, observations only)
  → quality:qa                                            (5 suites)
  → ba:trace                                              (chain validation)
  → project_context_skill                                 (context updated)
```

## Error handling

Failure modes are refusals, not exceptions:

- Missing ADR for a decision-bearing change → `implementer:build` refuses,
  citing RULE 11.
- ADR at Draft or Proposed when the spec is regenerated → excluded from the
  projection, listed as pending.
- Illegal lifecycle transition → refuse and name the legal transitions.
- Supersede target missing or already superseded → refuse and report the chain.
- Traceability orphan → reported as a finding by `ba:trace`, never auto-fixed.

## Testing / verification

No runtime code, so verification is structural:

1. Every new skill and function file resolves from its parent dispatch table.
2. `python tools/exporter.py --list` picks up all skills and functions.
3. `python tools/exporter.py --dry-run` completes without error.
4. No dangling cross-references between new and existing files.
5. Counts in `CLAUDE.md`, `README.md`, `agents/README.md`, and
   `skills/README.md` match the filesystem.

## Out of scope

- Any runtime, service, datastore, or UI.
- Live Jira API integration — companions read exports, as `ba:parse` already does.
- Migrating existing repo docs into the new Project Context format.
