# Spec-Driven Development for the Agent Pipeline — Design Specification

**Date:** August 5, 2026
**Status:** Approved Design
**Version:** 1.0

---

## Executive Summary

Introduce spec-driven development (SDD) as the governing methodology for the agent pipeline in this repository. Every *feature* request must pass through requirements → design → tasks artifacts, each explicitly approved by the user, before any agent generates implementation code. Trivial/non-feature work (typos, config tweaks, doc edits) is exempt.

This is implemented as one new skill (`skills/spec_driven_development_skill.md`), one new rule in `instructions/master_instruction_set.md` (RULE 11), and short "Spec-Driven Mode" additions to the four existing role agents. No new agents or agent functions are introduced.

---

## Problem Statement

**Current state:**
- `orchestrator:plan` and `architect:design` exist, but nothing *requires* them to run, or requires their output to be reviewed, before `implementer:build`/`implementer:full` generates code.
- There is no single, consistently-named artifact trail (requirements → design → tasks) that ties a feature's acceptance criteria to the code and tests that implement it.
- `docs/superpowers/specs/` already holds design docs for changes made *to this repository itself* (via the brainstorming skill) — a different, human-authored convention that should not be conflated with per-feature SDD artifacts generated for downstream projects.

**Desired state:**
- Every feature built through this pipeline produces `specs/<feature-name>/requirements.md`, `design.md`, and `tasks.md`, each gated on explicit user approval before the next stage or implementation begins.
- The gate is enforced as a constitutional rule (`master_instruction_set.md`), not a convention agents may silently skip.
- The mechanism is reusable and centralized in one skill file, consistent with this repo's existing skill-based architecture (agents delegate to skills; they don't each reimplement logic).

---

## Solution: `spec_driven_development_skill.md` + RULE 11

### Stage mapping

No new agents. SDD is implemented as four stages mapped onto existing agent functions:

| Stage | Owner | Artifact |
|---|---|---|
| constitution | `instructions/master_instruction_set.md` (existing) | — (governing rules, unchanged in role) |
| specify | `orchestrator:plan` | `specs/<feature>/requirements.md` |
| plan | `architect:design` | `specs/<feature>/design.md` |
| tasks | `implementer` (via existing `tools/task_generator.py`) | `specs/<feature>/tasks.md` |
| implement | `implementer:build` / `implementer:full` | code, tests, docs |

`quality:review` gets one addition: verify delivered code/tests against `tasks.md` acceptance criteria (traceability check), in addition to its existing quality checks.

### RULE 11 — Spec-Driven Gate

Added to `instructions/master_instruction_set.md` alongside RULE 10:

> **RULE 11 — Spec-Driven Gate.** No agent may generate implementation code for a feature until `specs/<feature>/requirements.md`, `design.md`, and `tasks.md` exist and each carries an explicit `Status: Approved` marker, set by the user (not by an agent). `architect:design` refuses to run without an approved `requirements.md`. `implementer:build`/`implementer:full` refuses to run without an approved `tasks.md`. This gate applies to feature work only — trivial one-line fixes, config tweaks, and doc edits are exempt.

This mirrors the HARD-GATE pattern already used by the brainstorming skill in this environment.

### Skill contents (`skills/spec_driven_development_skill.md`)

1. **Artifact templates:**
   - `requirements.md` — EARS-format acceptance criteria (`WHEN <trigger> THE SYSTEM SHALL <behavior>`), one user story per requirement, each with a stable requirement ID (e.g. `REQ-1`).
   - `design.md` — architecture, components, data flow; same shape as existing docs under `docs/superpowers/specs/`.
   - `tasks.md` — checklist of discrete, independently-verifiable implementation steps, each referencing the requirement ID(s) it satisfies. Reuses `tools/task_generator.py`'s existing output format rather than inventing a new one.
2. **Approval checkpoint:** after writing each artifact, the responsible agent stops and asks the user to review/approve before advancing to the next stage — the same UX already used in this brainstorming conversation.
3. **Traceability rule:** every task must cite the requirement ID it satisfies; `quality:review` checks this mapping exists and is unbroken before sign-off.

### Artifact location

`specs/<feature-name>/` at the repo root of the *downstream* project being built — kept separate from:
- `docs/superpowers/specs/` — human-authored design docs for changes to *this* repository, produced via the brainstorming skill.
- `docs/context/` — `context_builder_skill` output (architecture.md, tech-stack.md, context.json, design.html), which documents an existing codebase rather than gating new feature work.

### Documentation touch points

- `agents/orchestrator_agent.md`, `agents/architect_agent.md`, `agents/implementer_agent.md`, `agents/quality_agent.md` — each gets a short "Spec-Driven Mode" section referencing the skill and stating the RULE 11 obligation relevant to that agent's functions.
- `agents/README.md` and top-level `CLAUDE.md` — pipeline diagram updated to show the specify → plan → tasks → implement gate.

---

## Out of Scope

- No new agent or agent function (e.g. no `orchestrator:specify`) — reuses `orchestrator:plan` and `architect:design`.
- No changes to `docs/superpowers/specs/` conventions or the brainstorming skill.
- No retroactive spec generation for already-shipped features in this repo.
