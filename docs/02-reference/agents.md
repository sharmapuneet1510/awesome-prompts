# Agent Reference

**Five agents, zero role overlap.** Each owns a responsibility and dispatches to
[skills](skills.md) for implementation.

---

## The five

| # | Agent | Role | Functions | Companion role |
|---|---|---|---|---|
| 1 | Orchestrator | Strategy & orchestration | 9 | — |
| 2 | Architect | Architecture & design | 9 | Developer Companion |
| 3 | Implementer | Implementation & execution | 7 | Coding Companion |
| 4 | Quality | QA, security & performance | 10 | Review + QA Companions |
| 5 | Business Analyst | Backlog & requirements | 7 | BA Companion |

Definitions live in `agents/<name>_agent.md`; per-function detail in
`agents/<name>/functions/*.md`.

---

## Why five and not thirteen

Until v4.0.0 there were thirteen agents, many tech-specific — one for Java, one
for Python, one for React. They duplicated each other constantly: every agent
needed its own testing guidance, its own documentation rules, its own error
handling.

The consolidation split **orchestration** from **implementation**. An agent now
decides *what* and dispatches; a [skill](skills.md) knows *how*. Adding Rust
support means adding one skill, not one agent.

```
agent  = orchestration + dispatch    (5)
skill  = implementation knowledge    (35)
```

The 13 → 5 mapping is in [../../CHANGELOG.md](../../CHANGELOG.md) under 4.0.0.

---

## Orchestrator

**Strategy, planning, and shipping.** The entry point for greenfield work and
the exit point for releases.

`plan` · `build` · `context` · `pr` · `review` · `tradeoff` · `risk` · `ideate` · `solve`

Owns `project-overview.md`, `risks.md`, and `release-history.md` in the Project
Context. Use it when the question is "what should we build and in what order",
not "how does this code work".

---

## Architect

**Design, and every recorded decision.** Absorbed the Developer Companion role
in v5.0.0, which made it the busiest agent.

`design` · `refactor` · `frontend` · `schema` · `api` · `a11y` · `analyse` · `adr` · `spec`

Two halves:

- **Design** (`design`, `refactor`, `frontend`, `schema`, `api`, `a11y`) —
  producing the shape of a system.
- **Decisions** (`analyse`, `adr`, `spec`) — understanding what exists,
  recording what was decided, and projecting decisions into the current
  specification.

`architect:adr` is **the only function in the system that can write an ADR.**
Every other agent may propose one.

Owns `technical-context.md`, `architecture-context.md`, `known-behaviours.md`,
and `technical-debt.md`.

---

## Implementer

**Code, tests, docs, and deployment.** The narrowest remit and the strictest gate.

`full` · `build` · `test` · `doc` · `pipeline` · `docker` · `iac`

`implementer:full` runs build → test → doc in one context window. Prefer it —
splitting the three across separate invocations loses the context connecting
code to its tests to its documentation.

This is the only agent that **refuses to start**. `implementer:build` checks the
spec chain, the ADR gate, traceability, and requirement citations before writing
a line. See [rules.md](rules.md).

Owns `dependencies.md`.

---

## Quality

**Two distinct jobs, deliberately kept apart.**

`observe` · `review` · `audit` · `security` · `perf` · `debug` · `diagnose` · `qa` · `report` · `batch-review`

**Conformance** (`observe`) asks whether the code matches what was agreed. It
produces observations only — never edits, never scores, never writes an ADR.

**Judgement** (`review`, `audit`, `security`, `perf`) asks whether the code is
any good. It scores and proposes fixes.

Merging them produces a reviewer that fixes what is easy instead of reporting
what matters. Run `observe` first.

Owns the five `quality/*.md` suites.

---

## Business Analyst

**From conversation to backlog, and the traceability proof.**

`discover` · `clarify` · `brd` · `create` · `parse` · `report` · `trace`

Was a two-function utility until v5.0.0 added the BA Companion role. It now
holds both ends of the chain: `discover` creates the first artifact, `trace`
verifies the last one connects back to it.

Owns `business-context.md` and `mvp-scope.md`.

---

## Specialist modes

Nine specialist roles map onto the five agents. There is no separate "security
auditor agent" — there is `quality:security`.

| Specialist role | Invoke |
|---|---|
| Full-stack engineer | `orchestrator:build` |
| Systems architect | `architect:design` |
| Frontend expert | `architect:frontend` |
| Code auditor | `quality:audit` |
| Debugging expert | `quality:debug` |
| Performance expert | `quality:perf` |
| Security auditor | `quality:security` |
| Technical lead | `orchestrator:review` / `:tradeoff` / `:risk` |
| DevOps engineer | `implementer:pipeline` / `:docker` / `:iac` |

The former `SPECIALIST_AGENT_MODES.md` and `SPECIALIST_MODES_MAPPING.md` are in
[../99-archive/superseded/](../99-archive/superseded/).

---

## Foundational principles

All five operate under four behavioural principles, woven into agent
definitions rather than enforced as a checklist:

| Principle | Means |
|---|---|
| **Think Before Coding** | State assumptions, surface trade-offs, present options |
| **Simplicity First** | Minimum code that solves it; no speculation |
| **Surgical Changes** | Touch only what you must; clean up only your own mess |
| **Goal-Driven Execution** | Define success criteria upfront; loop until verified |

Detail in [rules.md](rules.md).

---

## See also

- [functions.md](functions.md) — all 42 functions
- [skills.md](skills.md) — the 35 skills agents dispatch to
- [../01-workflows/](../01-workflows/) — which agent for which job
