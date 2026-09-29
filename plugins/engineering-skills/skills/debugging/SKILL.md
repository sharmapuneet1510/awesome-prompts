---
name: debugging
description: A bug, failing test, or incident needs a root cause — `quality:debug`, `quality:diagnose`
---

# Debugging Skill — v1.1

## Quick Card

> Read this card first. Load a section below only when the task needs it.

| | |
|---|---|
| **Use when** | A bug, failing test, or incident needs a root cause — `quality:debug`, `quality:diagnose` |
| **Skip when** | Cause already known and fix trivial — just fix it with a regression test |
| **Inputs** | Symptom, stack trace or logs, the smallest repro you can get |
| **Produces** | Root cause, minimal fix, regression test |
| **Steps** | 1. Reproduce → 2. Isolate → 3. One falsifiable hypothesis → 4. Test it before fixing → 5. Fix the cause → 6. Regression test that fails first |
| **Done when** | Regression test fails before the fix and passes after; no unrelated changes bundled |
| **Load on demand** | §1 the loop · §3 isolation techniques · §4 hypothesis discipline |
| **Run report** | `html_report_skill` — adds: Hypotheses tried (confirmed / discarded) · Root cause |
| **Pairs with** | `test_skill`, `logger_skill`, `opentelemetry_skill` |

---

## 1. The Loop

Debugging is not "stare at the code until something looks wrong." Follow this loop, in order, every time:

1. **Reproduce** — get a minimal, reliable repro before touching anything. If you can't reproduce it, you don't understand it yet.
2. **Isolate** — narrow the failure to the smallest unit that still exhibits it (bisect: comment out, binary-search commits, strip inputs).
3. **Hypothesize** — form one specific, falsifiable hypothesis about the cause. Not "something's wrong with the cache" — "the cache key doesn't include the tenant ID, so tenant B reads tenant A's entry."
4. **Test the hypothesis** — add a log line, a debugger breakpoint, or a targeted assertion that would prove or disprove it. Don't fix yet.
5. **Fix** — once confirmed, make the smallest change that addresses the root cause, not the symptom.
6. **Verify with a regression test** — write a test that fails before the fix and passes after. Without this, the bug can come back silently.

## 2. Anti-Patterns

- **Shotgun debugging** — changing multiple things at once "to see if it helps." If it works, you don't know why; if it doesn't, you've added noise.
- **Fixing the symptom** — catching an exception and returning a default instead of finding why the exception happens.
- **Skipping repro** — patching based on a stack trace alone when the failure is intermittent or environment-dependent.
- **No regression test** — the fastest way to see the same bug again in three weeks.

## 3. Isolation Techniques

- **Bisection**: for regressions, binary-search commit history (`git bisect`) instead of reading diffs manually.
- **Minimal repro**: strip the input down to the smallest case that still fails — delete code/data until the bug disappears, then back up one step.
- **Differential debugging**: compare a working case against a failing case side by side (same inputs, different environment; or different inputs, same environment) and isolate what's different.
- **Log at boundaries**: instrument the boundaries between components (function entry/exit, network calls, DB queries) rather than scattering prints inside logic — boundaries tell you which component owns the bug.

## 4. Hypothesis Discipline

A good hypothesis names a mechanism, not just a location:
- Bad: "It's something in the auth module."
- Good: "The token refresh happens after the request is already in flight, so the first retry uses the stale token."

If the evidence doesn't match the hypothesis, discard it completely — don't bend it to fit ("well, maybe it's *also* timing-related").

## 5. Checklist

✅ Reproduced reliably before making changes
✅ Isolated to the smallest failing unit
✅ Hypothesis is specific and falsifiable
✅ Hypothesis tested before fixing
✅ Fix addresses root cause, not symptom
✅ Regression test added (fails before fix, passes after)
✅ No unrelated changes bundled into the fix

---
> Inspired by ideas from [ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts) (GPL-3.0) — content rewritten, not copied. See `docs/reference/credits.md`.
