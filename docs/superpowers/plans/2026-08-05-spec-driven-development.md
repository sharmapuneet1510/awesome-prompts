# Spec-Driven Development for the Agent Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make spec-driven development (requirements → design → tasks → implement, each gated on user approval) the enforced methodology for this repo's agent pipeline.

**Architecture:** One new skill (`skills/spec_driven_development_skill.md`) owns the artifact templates and approval-checkpoint logic. One new rule (RULE 11) in `instructions/master_instruction_set.md` makes the gate constitutional. Four existing agent docs (`orchestrator`, `architect`, `implementer`, `quality`) get a short section each wiring their existing functions to the gate. No new agents, no new agent functions, no application code — this is a documentation/prompt-engineering change to `.md` files.

**Tech Stack:** Markdown (skill/agent/instruction files), bash/grep for verification (no test runner exists for this content — grep-based content checks stand in for automated tests).

## Global Constraints

- Spec at `docs/superpowers/specs/2026-08-05-spec-driven-development-design.md` is the source of truth — every task must trace to a section in it.
- RULE 11 wording is fixed by the spec: reuse it verbatim, do not paraphrase.
- Gate applies to feature work only; trivial fixes/config/doc edits are exempt (must be stated explicitly in RULE 11 text).
- `specs/<feature-name>/` (downstream project root) is the artifact location — never write per-feature artifacts into `docs/superpowers/specs/` (reserved for this repo's own brainstorming design docs) or `docs/context/` (reserved for `context_builder_skill` output).
- No new agent functions (no `orchestrator:specify`) — reuse `orchestrator:plan` and `architect:design`.
- Match existing file conventions exactly: skill frontmatter shape (see `skills/context_builder_skill.md`), `## RULE N — Title` heading shape (see `instructions/master_instruction_set.md`), `## FUNCTION: <agent>:<fn>` heading shape (see `agents/architect_agent.md`).

---

### Task 1: Create the spec-driven-development skill

**Files:**
- Create: `skills/spec_driven_development_skill.md`

**Interfaces:**
- Produces: A skill document that Tasks 4–7 will reference by path (`skills/spec_driven_development_skill.md`) and by section anchor (`## Artifact Templates`, `## Approval Checkpoint`, `## Traceability Rule`).

- [ ] **Step 1: Write the skill file**

```markdown
---
name: Spec-Driven Development Skill
version: 1.0
description: >
  Reusable skill implementing the spec-driven development gate: requirements.md
  → design.md → tasks.md → implementation, each stage gated on explicit user
  approval. Referenced by orchestrator, architect, implementer, and quality
  agents. Enforced by RULE 11 in instructions/master_instruction_set.md.
---

# Spec-Driven Development Skill — v1.0

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
| specify | `orchestrator:plan` | `specs/<feature>/requirements.md` | none (first artifact) |
| plan | `architect:design` | `specs/<feature>/design.md` | `requirements.md` must be `Status: Approved` |
| tasks | `implementer` (via `tools/task_generator.py`) | `specs/<feature>/tasks.md` | `design.md` must be `Status: Approved` |
| implement | `implementer:build` / `implementer:full` | code, tests, docs | `tasks.md` must be `Status: Approved` |

`quality:review` additionally runs the Traceability Rule (below) against
delivered code.

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

`tools/task_generator.py` already generates individual numbered task spec
files (e.g. `task-01-database-schema.md`, `task-02-backend-api.md`). This
skill adds one file that indexes them against requirement IDs:

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
3. Asks the user to review and either approve (agent flips `Status:` to
   `Approved`) or request changes (agent revises and re-presents).
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
```

- [ ] **Step 2: Verify the file was created with required sections**

Run: `grep -n "^## " skills/spec_driven_development_skill.md`
Expected output includes: `## Purpose`, `## Stage Mapping`, `## Artifact Templates`, `## Approval Checkpoint`, `## Traceability Rule`

- [ ] **Step 3: Commit**

```bash
git add skills/spec_driven_development_skill.md
git commit -m "feat: add spec-driven-development skill"
```

---

### Task 2: Add RULE 11 to the constitution and update its pointer in CLAUDE.md

**Files:**
- Modify: `instructions/master_instruction_set.md:510-600` (insert new rule before `## Attribution & Integration`, update frontmatter version and the Attribution paragraph)
- Modify: `CLAUDE.md:14` (the "See instructions/master_instruction_set.md..." line and the "New in v2.0" callout)

**Interfaces:**
- Consumes: Nothing from Task 1 directly, but references `skills/spec_driven_development_skill.md` by path in the rule text.
- Produces: `## RULE 11 — Spec-Driven Gate` heading, referenced by Tasks 4–7.

- [ ] **Step 1: Bump the frontmatter version**

In `instructions/master_instruction_set.md`, change:

```yaml
version: 2.0
```
to:
```yaml
version: 2.1
```

- [ ] **Step 2: Insert RULE 11 before the Attribution section**

Find the line `## Attribution & Integration` (currently line 597) and insert immediately before it:

```markdown
## RULE 11 — Spec-Driven Gate

**No agent may generate implementation code for a feature until
`specs/<feature>/requirements.md`, `design.md`, and `tasks.md` exist and
each carries an explicit `Status: Approved` marker, set by the user (not by
an agent).**

- `architect:design` refuses to run without an approved `requirements.md`.
- `implementer:build`/`implementer:full` refuses to run without an approved
  `tasks.md`.
- This gate applies to feature work only — trivial one-line fixes, config
  tweaks, and doc edits are exempt.
- See `skills/spec_driven_development_skill.md` for artifact templates and
  the approval-checkpoint workflow.

**When to apply:** Every feature request that reaches `orchestrator:plan`,
`architect:design`, or `implementer:build`/`implementer:full`.

---

```

- [ ] **Step 3: Update the Attribution paragraph**

Change:
```markdown
These 10 rules + 4 Foundational Principles together form the **Master Instruction Set v2.0**.
```
to:
```markdown
These 11 rules + 4 Foundational Principles together form the **Master Instruction Set v2.1**.
```

- [ ] **Step 4: Update CLAUDE.md**

In `CLAUDE.md`, change:
```markdown
See `instructions/master_instruction_set.md` (FOUNDATIONAL PRINCIPLES + RULES 0-10 sections) for details.

**New in v2.0:** RULE 10 adds five token-efficient practices: Surgical Modification, Diff-Only Outputs, Graph-Style Context Curation, Token & Memory Efficiency, and Execution Workflow (master_instruction_set.md lines 510-595).
```
to:
```markdown
See `instructions/master_instruction_set.md` (FOUNDATIONAL PRINCIPLES + RULES 0-11 sections) for details.

**New in v2.0:** RULE 10 adds five token-efficient practices: Surgical Modification, Diff-Only Outputs, Graph-Style Context Curation, Token & Memory Efficiency, and Execution Workflow (master_instruction_set.md lines 510-595).

**New in v2.1:** RULE 11 adds the Spec-Driven Gate — no feature code without an approved requirements → design → tasks chain. See `skills/spec_driven_development_skill.md`.
```

- [ ] **Step 5: Verify**

Run: `grep -n "RULE 11\|version: 2.1\|11 rules" instructions/master_instruction_set.md`
Expected: three matches — the heading, the frontmatter version, the Attribution line.

Run: `grep -n "RULE 11\|v2.1" CLAUDE.md`
Expected: two matches — the RULES 0-11 pointer line and the New in v2.1 callout.

- [ ] **Step 6: Commit**

```bash
git add instructions/master_instruction_set.md CLAUDE.md
git commit -m "feat: add RULE 11 spec-driven gate to master instruction set"
```

---

### Task 3: Register the skill in skills/README.md

**Files:**
- Modify: `skills/README.md:5-33` (Quick Navigation table)

**Interfaces:**
- Consumes: `skills/spec_driven_development_skill.md` from Task 1 (path must match exactly).

- [ ] **Step 1: Add a table row**

In `skills/README.md`, after the row for `| 25 | [JIRA Incremental Spec Generator]...`, add:

```markdown
| 26 | [Spec-Driven Development](spec_driven_development_skill.md) | Requirements → design → tasks gate before implementation | Language-agnostic | Orchestrator, Architect, Implementer, Quality |
```

And update the section heading:
```markdown
## Quick Navigation (25 Skills)
```
to:
```markdown
## Quick Navigation (26 Skills)
```

- [ ] **Step 2: Verify**

Run: `grep -n "Spec-Driven Development\|26 Skills" skills/README.md`
Expected: two matches.

- [ ] **Step 3: Commit**

```bash
git add skills/README.md
git commit -m "docs: register spec-driven-development skill in skills index"
```

---

### Task 4: Wire orchestrator:plan into the gate

**Files:**
- Modify: `agents/orchestrator_agent.md` (insert new `## Spec-Driven Mode` section after `## Operating Philosophy`, before `## Workflow: 7-Phase Orchestration`, currently between lines 47 and 82)

**Interfaces:**
- Consumes: `skills/spec_driven_development_skill.md` (Task 1), RULE 11 (Task 2).

- [ ] **Step 1: Insert the section**

Insert immediately before the `## Workflow: 7-Phase Orchestration` heading:

```markdown
## Spec-Driven Mode

For feature work, `orchestrator:plan` is the **specify** stage of the
spec-driven pipeline (see `skills/spec_driven_development_skill.md`,
governed by RULE 11 in `instructions/master_instruction_set.md`):

1. Produce `specs/<feature-name>/requirements.md` using the skill's EARS
   template — one `REQ-N` per acceptance criterion.
2. Present it to the user and stop. Do not proceed to `architect:design`
   or `implementer:build` until the user sets `Status: Approved`.
3. Trivial, non-feature requests (typos, config tweaks, doc edits) skip
   this stage entirely — RULE 11's exemption applies.

`orchestrator:build`'s auto-chain into `architect:design` and
`implementer:build` (see Workflow below) only fires once
`requirements.md` is Approved.

---
```

- [ ] **Step 2: Verify**

Run: `grep -n "## Spec-Driven Mode" agents/orchestrator_agent.md`
Expected: one match, positioned before `## Workflow: 7-Phase Orchestration`.

- [ ] **Step 3: Commit**

```bash
git add agents/orchestrator_agent.md
git commit -m "docs: wire orchestrator:plan into the spec-driven gate"
```

---

### Task 5: Wire architect:design into the gate

**Files:**
- Modify: `agents/architect_agent.md:253` (start of `## FUNCTION: architect:design`)

**Interfaces:**
- Consumes: `skills/spec_driven_development_skill.md` (Task 1), RULE 11 (Task 2).

- [ ] **Step 1: Insert a gate note immediately after the `## FUNCTION: architect:design` heading**

```markdown
## FUNCTION: architect:design

> **Spec-Driven Gate (RULE 11):** Before running, confirm
> `specs/<feature-name>/requirements.md` exists and is `Status: Approved`.
> If it isn't, stop and tell the user to complete `orchestrator:plan`
> (the specify stage) first — do not proceed to design. On completion,
> write `specs/<feature-name>/design.md` per
> `skills/spec_driven_development_skill.md`, present it, and wait for
> `Status: Approved` before any implementer function runs.
```

(Keep all existing content of the function that currently follows the
heading — this is an insertion, not a replacement.)

- [ ] **Step 2: Verify**

Run: `grep -n "Spec-Driven Gate (RULE 11)" agents/architect_agent.md`
Expected: one match, directly under `## FUNCTION: architect:design`.

- [ ] **Step 3: Commit**

```bash
git add agents/architect_agent.md
git commit -m "docs: wire architect:design into the spec-driven gate"
```

---

### Task 6: Wire implementer:build and implementer:full into the gate

**Files:**
- Modify: `agents/implementer_agent.md:326` (start of `## Function 1: implementer:build`)
- Modify: `agents/implementer_agent.md:1659` (start of `## Function 7: implementer:full`)

**Interfaces:**
- Consumes: `skills/spec_driven_development_skill.md` (Task 1), RULE 11 (Task 2), `design.md` produced in Task 5.

- [ ] **Step 1: Insert a gate note after `## Function 1: implementer:build`**

```markdown
## Function 1: `implementer:build`

> **Spec-Driven Gate (RULE 11):** Before generating code for feature work,
> confirm `specs/<feature-name>/design.md` is `Status: Approved` and
> `specs/<feature-name>/tasks.md` exists. If `tasks.md` doesn't exist yet,
> generate it via `tools/task_generator.py` per
> `skills/spec_driven_development_skill.md`, present it, and wait for
> `Status: Approved` before writing any code. Trivial/non-feature work is
> exempt per RULE 11.
```

(Insertion only — keep existing function content that follows.)

- [ ] **Step 2: Insert the same gate note after `## Function 7: implementer:full`**

```markdown
## Function 7: `implementer:full`

> **Spec-Driven Gate (RULE 11):** Same gate as `implementer:build` — this
> function runs build+test+doc in one context, so the `tasks.md` approval
> check happens once, before any of the three sub-phases start.
```

- [ ] **Step 3: Verify**

Run: `grep -n "Spec-Driven Gate (RULE 11)" agents/implementer_agent.md`
Expected: two matches — one under Function 1, one under Function 7.

- [ ] **Step 4: Commit**

```bash
git add agents/implementer_agent.md
git commit -m "docs: wire implementer:build/full into the spec-driven gate"
```

---

### Task 7: Add the traceability check to quality:review

**Files:**
- Modify: `agents/quality_agent.md:150` (start of `## FUNCTION 1: quality:review`)

**Interfaces:**
- Consumes: `skills/spec_driven_development_skill.md`'s Traceability Rule (Task 1).

- [ ] **Step 1: Insert a traceability check after the `## FUNCTION 1: quality:review` heading**

```markdown
## FUNCTION 1: quality:review

> **Spec-Driven Traceability (RULE 11):** If the feature under review has
> `specs/<feature-name>/` artifacts, run the Traceability Rule from
> `skills/spec_driven_development_skill.md` before sign-off: every
> `tasks.md` entry cites a `REQ-N`, every `REQ-N` is cited by at least one
> task, and `design.md` was Approved before any task was marked complete.
> Report violations as review findings — do not silently pass them.
```

(Insertion only — keep existing function content that follows.)

- [ ] **Step 2: Verify**

Run: `grep -n "Spec-Driven Traceability (RULE 11)" agents/quality_agent.md`
Expected: one match, directly under `## FUNCTION 1: quality:review`.

- [ ] **Step 3: Commit**

```bash
git add agents/quality_agent.md
git commit -m "docs: add spec-driven traceability check to quality:review"
```

---

### Task 8: Update the pipeline diagrams

**Files:**
- Modify: `agents/README.md:33-52` (the `## Linear Execution Pipeline` section)
- Modify: `CLAUDE.md` (the "Skill-Based Architecture" pipeline diagram, in the section added by Task 2's edit — same file, different section)

**Interfaces:**
- Consumes: The stage mapping table from Task 1's skill file (specify/plan/tasks/implement).

- [ ] **Step 1: Read the current pipeline diagram**

Run: `sed -n '33,52p' agents/README.md`

Note the existing arrow chain (e.g. `orchestrator:plan → orchestrator:build → ...`) and insert the gate stages into it without removing any existing step — add `[specify]`, `[plan]`, `[tasks]` annotations next to the corresponding existing steps rather than replacing the diagram wholesale.

- [ ] **Step 2: Annotate `agents/README.md`'s pipeline**

Add a line directly below the existing diagram in `## Linear Execution Pipeline`:

```markdown
**Spec-driven gate (RULE 11):** `orchestrator:plan` = specify
(`requirements.md`), `architect:design` = plan (`design.md`),
`implementer` task generation = tasks (`tasks.md`) — each must be
`Status: Approved` before the next stage runs. See
`skills/spec_driven_development_skill.md`.
```

- [ ] **Step 3: Annotate the `CLAUDE.md` pipeline diagram**

In the `### Skill-Based Architecture` code block in `CLAUDE.md`, add a
comment line above `orchestrator:plan → orchestrator:build`:

```
    (specify: requirements.md → plan: design.md → tasks: tasks.md, each Approved — RULE 11)
```

- [ ] **Step 4: Verify**

Run: `grep -n "Spec-driven gate (RULE 11)" agents/README.md`
Expected: one match.

Run: `grep -n "RULE 11" CLAUDE.md`
Expected: at least three matches now (pointer line, New in v2.1 callout, pipeline annotation).

- [ ] **Step 5: Commit**

```bash
git add agents/README.md CLAUDE.md
git commit -m "docs: annotate pipeline diagrams with the spec-driven gate"
```

---

## Self-Review Notes

- **Spec coverage:** constitution (Task 2) · specify/orchestrator:plan (Task 4) · plan/architect:design (Task 5) · tasks/implementer (Task 6) · quality:review traceability (Task 7) · skill artifact templates + approval checkpoint (Task 1) · specs/<feature>/ location convention (documented in Task 1's templates and Global Constraints) · doc/README updates (Task 3, Task 8). All spec sections have a task.
- **No placeholders:** every step includes literal markdown/text to insert, not descriptions.
- **Type/name consistency:** `specs/<feature-name>/{requirements,design,tasks}.md`, `Status: Approved`, `REQ-N`, and `skills/spec_driven_development_skill.md` are used identically across all 8 tasks.
