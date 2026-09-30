---
name: Spec-Driven Development Skill
version: 1.1
description: >
  Reusable skill implementing the spec-driven development gate: requirements.md
  → design.md → tasks.md → implementation, each stage gated on explicit user
  approval. Referenced by orchestrator, architect, implementer, and quality
  agents. Enforced by RULE 11 in instructions/master_instruction_set.md.
applies_to: [all-languages, spec-driven, governance]
---

# Spec-Driven Development Skill — v1.1

## Quick Card

> Read this card first. Load a section below only when the task needs it.

| | |
|---|---|
| **Use when** | Any feature work — RULE 11: requirements → design → tasks, each approved before the next |
| **Skip when** | Trivial changes: one-line fixes, config tweaks, small doc edits |
| **Inputs** | The feature request |
| **Produces** | `specs/<feature>/requirements.md`, `design.md`, `tasks.md`, each ending `Status: Approved` |
| **Steps** | 1. `orchestrator:plan` writes requirements (EARS) → 2. Approve → 3. `architect:design` → 4. Approve → 5. Tasks citing REQ IDs → 6. Approve → 7. Implement |
| **Done when** | All three at `Status: Approved` by explicit user approval; every task cites a REQ |
| **Load on demand** | §Stage Mapping · §Artifact Templates · §Approval Checkpoint · §Traceability Rule |
| **Run report** | `html_report_skill` — adds: Stage status (Draft / Approved) per artifact |
| **Pairs with** | `traceability_skill`, `adr_skill` |

---

## Purpose

Formalize the specify → plan → tasks → implement workflow so no agent
generates implementation code for a feature before the feature's
requirements, design, and task breakdown exist and are explicitly approved
by the user. This skill is **internal** — called by agents, not invoked
directly by users.

Governed by **RULE 11 — Spec-Driven Gate** in
`instructions/master_instruction_set.md`.

---

## Stage Mapping

| Stage | Owner | Artifact | Gate |
|---|---|---|---|
| constitution | `instructions/master_instruction_set.md` | — | n/a (pre-existing) |
| specify | `orchestrator:plan` | `specs/<feature-name>/requirements.md` | none (first artifact) |
| plan | `architect:design` | `specs/<feature-name>/design.md` | `requirements.md` must be `Status: Approved` |
| tasks | `implementer` (via `tools/task_generator.py`) | `specs/<feature-name>/tasks.md` | `design.md` must be `Status: Approved` |
| implement | `implementer:build` / `implementer:full` | code, tests, docs | `tasks.md` must be `Status: Approved` |

`quality:review` additionally runs the Traceability Rule (below) against
delivered code.


## The Gate

This section is the gate's only full definition. RULE 11 and 11a, the agents
and the functions link here instead of restating it.

**The chain.** Feature code needs `specs/<feature>/requirements.md`, then
`design.md`, then `tasks.md`, each approved in that order. `architect:design`
needs approved requirements; task generation needs an approved design;
`implementer:build` and `implementer:full` need all three.

**What counts as approval.** Only the user approves, never the model's
inference that they would.
- With the `spec-gate` plugin active (installed, and `.spec-gate.json` in the
  project): the user types `/spec-gate:approve <file>`. The hook writes
  `Status: Approved` and records the file's hash; editing the file afterwards
  voids the approval.
- Without it: the user's explicit approval in the conversation. Only then may
  the agent write `Status: Approved` into the file.

**ADRs (RULE 11a).** A change to a contract, data shape, dependency or
failure mode needs an ADR at `Status: Accepted`, approved the same way:
`/spec-gate:approve docs/adr/ADR-NNNN-….md` with spec-gate, the user's
explicit approval without it. Whether a change is decision-bearing is a
judgement the agent must surface, not decide away.

**Trivial work** — a one-line fix, a config tweak, a small doc edit — skips
the chain only when the user says so: `/spec-gate:trivial <reason>` with
spec-gate (valid until their next message, and logged), their explicit
say-so without it. Substantive changes to agent, skill or instruction files
are never trivial.

**What spec-gate enforces, and its limit.** Gated source edits through
Claude's file tools and the common shell write forms are blocked until the
chain is approved; approval markers in spec files and ADRs can only be
written by the hook. A write disguised in a script is not detected — see
the plugin's README.

---

## Artifact Location

`specs/<feature-name>/` lives at the root of the *downstream* project being
built — not in this repo's own `docs/` tree. Keep it distinct from:
- `docs/superpowers/specs/` — this repo's own brainstorming design docs,
  produced via the `superpowers:brainstorming` skill.
- `docs/context/` — `context_builder_skill` output (architecture.md,
  tech-stack.md, context.json, design.html), which documents an existing
  codebase rather than gating new feature work.

---

## Artifact Templates

### `requirements.md` (written during `orchestrator:plan`)

EARS-format acceptance criteria. Every requirement gets a stable ID.

```markdown
# <Feature Name> — Requirements

**Status:** Draft
**Feature:** <feature-name>

## REQ-1: <short title>

**User Story:** As a <role>, I want <capability>, so that <benefit>.

**Acceptance Criteria:**
- WHEN <trigger> THE SYSTEM SHALL <behavior>
- WHEN <trigger> THE SYSTEM SHALL <behavior>

## REQ-2: <short title>
...
```

Once the user approves, the agent changes `**Status:** Draft` to
`**Status:** Approved` in place — this is the only edit permitted after
approval without restarting the stage.

### `design.md` (written during `architect:design`)

```markdown
# <Feature Name> — Design

**Status:** Draft
**Feature:** <feature-name>
**Requirements:** specs/<feature-name>/requirements.md (Approved)

## Architecture
<2-3 sentences: overall approach>

## Components
<one subsection per component: responsibility, inputs, outputs>

## Data Flow
<how data moves between components>

## Error Handling
<what can fail and how it's handled>
```

### `tasks.md` (written by `implementer` via `tools/task_generator.py`)

Derive tasks from `design.md`, optionally seeding structure from
`tools/task_generator.py`'s templates (database schema, backend API,
frontend UI, integration tests, deployment) — the tool returns task data
in memory; the agent writes `tasks.md` itself as the index below.

```markdown
# <Feature Name> — Tasks

**Status:** Draft
**Feature:** <feature-name>
**Design:** specs/<feature-name>/design.md (Approved)

- [ ] task-01-database-schema.md — satisfies REQ-1
- [ ] task-02-backend-api.md — satisfies REQ-1, REQ-2
- [ ] task-03-frontend-ui.md — satisfies REQ-2
- [ ] task-04-integration-tests.md — satisfies REQ-1, REQ-2
```

Every row must cite at least one requirement ID. A row with no requirement
ID is a Traceability Rule violation (see below).

---

## Approval Checkpoint

After writing `requirements.md`, `design.md`, or `tasks.md`, the agent:

1. Stops before proceeding to the next stage.
2. Tells the user exactly what was written and where (file path).
3. Asks the user to review and either approve (agent writes `Status:
   Approved` into the file, but only once the user has explicitly said to
   approve — never inferred from silence or a vague acknowledgement) or
   request changes (agent revises and re-presents).
4. Does not advance to the next stage until `Status: Approved` is set.

This is the same approval UX used by the `superpowers:brainstorming` skill.

---

## Traceability Rule

`quality:review` checks, before sign-off on any spec-driven feature:

1. Every entry in `tasks.md` cites at least one requirement ID from
   `requirements.md`.
2. Every `REQ-N` in `requirements.md` is cited by at least one `tasks.md`
   entry (no orphaned requirements).
3. `design.md` references `requirements.md` as Approved before any
   `tasks.md` entry is marked complete.

Any violation is reported as a review finding, not silently ignored.
