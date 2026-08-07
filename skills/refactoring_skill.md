---
name: Refactoring Skill
version: 1.0
description: >
  Safe refactoring discipline — characterize existing behavior before changing
  structure, move in small reversible steps, never mix refactoring with feature work.
applies_to: [java, python, javascript, react, refactoring]
tags: [refactoring, code-quality, technical-debt]
---

# Refactoring Skill — v1.0

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
> Inspired by ideas from [ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts) (GPL-3.0) — content rewritten, not copied. See `CREDITS.md`.
