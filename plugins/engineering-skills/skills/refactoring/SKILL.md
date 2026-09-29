---
name: refactoring
description: Restructuring code without changing behaviour — `architect:refactor`, or before a feature that the current shape blocks
---

# Refactoring Skill — v1.1

## Quick Card

> Read this card first. Load a section below only when the task needs it.

| | |
|---|---|
| **Use when** | Restructuring code without changing behaviour — `architect:refactor`, or before a feature that the current shape blocks |
| **Skip when** | The change also alters behaviour — split it: refactor commit, then behaviour commit |
| **Inputs** | The code, a concrete trigger, characterization tests |
| **Produces** | Smaller, reviewable refactor commits with tests green after each |
| **Steps** | 1. Characterize behaviour with tests → 2. Confirm the trigger → 3. Bound the scope → 4. Small moves, tests after each → 5. Commit separately from behaviour changes |
| **Done when** | §5 checklist passes; public contracts unchanged unless that was the goal |
| **Load on demand** | §2 before you start · §3 safe moves · §4 never mix |
| **Run report** | `html_report_skill` — adds: Moves applied, in order |
| **Pairs with** | `test_skill`, `oop_skill`, `adr_skill` (Refactoring type) |

---

## 1. Definition

Refactoring changes code's internal structure without changing its observable behavior. If behavior changes, it's not a refactor — it's a feature change or a bug fix, and it needs its own commit and its own tests.

## 2. Before You Start

1. **Characterize current behavior.** If there's no test covering the code you're about to restructure, write one first (a characterization test — it documents what the code *does*, not what it *should* do).
2. **Confirm the trigger.** Refactor because a specific task needs it (adding a feature is hard because of tangled state; a bug is hiding because of duplicated logic), not speculatively. "This could be cleaner" is not a trigger on its own.
3. **Scope it.** Decide the boundary up front — one class, one module — and don't let it creep while you're in there.

## 3. Safe Refactoring Moves

Small, reversible, test-after-each-step:
- **Extract function/method** — pull a block into a named function; verify tests still pass.
- **Rename** — for clarity, never as a drive-by; use IDE rename tooling to catch every reference.
- **Inline** — collapse a needless indirection (a wrapper that does nothing but call through).
- **Move** — relocate a method/field to the class that actually owns the responsibility.
- **Replace conditional with polymorphism** — when a type-switch keeps growing, model the variants as types instead.
- **Introduce parameter object** — when a function's parameter list keeps growing, group related parameters.

Each move should be small enough that if it breaks something, `git diff` immediately shows why.

## 4. Never Mix Refactoring With Behavior Change

The #1 way refactors go wrong: "while I'm in here, let me also fix this bug / add this feature." This makes the diff impossible to review confidently, since a reviewer can't tell if a given line changed *because* of the restructuring or is an *actual* behavior change.

- Refactor first, commit, then make the behavior change as a separate commit.
- Or, if the bug fix is trivial and unrelated to the refactor's scope, do it first as its own commit, then refactor on top.

## 5. Checklist

✅ Characterization test exists (or was added) before restructuring
✅ Trigger for the refactor is a concrete task, not speculation
✅ Scope is bounded and stated up front
✅ Moves are small and independently verifiable
✅ Tests pass after every move, not just at the end
✅ No behavior change bundled into the same commit
✅ Public interfaces/contracts unchanged unless that was the explicit goal

---
> Inspired by ideas from [ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts) (GPL-3.0) — content rewritten, not copied. See `docs/reference/credits.md`.
