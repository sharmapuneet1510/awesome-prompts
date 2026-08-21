# 07 — Fix a Production Incident

**Something is broken now.** Find the cause, fix it, and make sure it cannot
come back unnoticed.

Covers [SDLC](sdlc-playbook.md) stages 14, 9, 12.

---

## When to use this

- Production is misbehaving.
- A bug report needs root-causing.

## Prerequisites

None — this workflow starts from a symptom. More context makes it faster, not
possible.

---

## The chain

```
quality:diagnose problem="..."      ← symptom known, cause unknown
    or
quality:debug stack_trace="..."     ← you have a trace or a reproduction
    ↓
(architect:adr)                     ← only if the fix changes a contract  ◆ GATE
    ↓
implementer:full                    → fix + tests + docs
    ↓
quality:qa suite=regression         → ◆ the step people skip
    ↓
quality:review → orchestrator:pr
```

---

## Which entry point

**`quality:diagnose`** — conversational. You know the symptom, not the cause.
It asks clarifying questions, then investigates code, database, and config. Use
this when you would otherwise start guessing.

**`quality:debug`** — you have a stack trace, a failing test, or a reliable
reproduction. Goes straight to root cause analysis, failure mechanism, edge case
discovery, and regression test generation.

Starting with `debug` when you only have a vague symptom wastes the trace-driven
machinery. Starting with `diagnose` when you have a clean stack trace wastes a
round of questions.

---

## Close the loop

**Every incident adds a regression scenario.** This is the step that gets
skipped under time pressure, and skipping it is why the same class of bug
recurs.

```
quality:qa suite=regression
```

Each row cites the incident that created it:

```
| REG-14 | Given a cancelled order, when the payment webhook arrives late,
           then no charge is captured | BR-7, INC-2291 | yes |
           tests/regression/test_late_webhook.py | 2026-08-21 |
```

An incident that produces no regression scenario will happen again.

---

## Does the fix need an ADR?

Usually not — most fixes restore intended behaviour, which was already decided.

It does when the fix **changes** a decision: a new retry policy, a different
consistency guarantee, a knowingly accepted race condition, a new dependency on
the hot path.

If root cause reveals that an earlier decision was wrong, supersede its ADR —
see [05](05-record-a-decision.md). Do not edit the old one; it recorded what was
believed at the time, and that record is the point.

---

## Under pressure

The gates still apply, but RULE 11's trivial-work exemption covers genuine
one-line fixes. A hotfix that changes one comparison operator does not need a
requirements → design → tasks chain.

What it does need: a regression scenario. That is not the exempt part.

---

## Artifacts

| Path | From |
|---|---|
| RCA report — root cause, failure mechanism, edge cases | `quality:debug` |
| Investigation notes | `quality:diagnose` |
| Fix, tests, docs | `implementer:full` |
| `docs/project-context/quality/regression.md` — new `REG-n` row | `quality:qa` |
| Incident synthesis | `quality:report` |
| `docs/adr/` — if a decision changed | `architect:adr` |

---

## Worked example

[../04-examples/quality.md](../04-examples/quality.md) — bug debugging scenario.

---

## Next

- [09 — Optimise performance](09-optimise-performance.md) if the cause was load
- [08 — Audit security](08-audit-security.md) if the cause was an abuse path
