# 04 — Understand a Codebase

**You inherited something and need your bearings.** Produces the shared context
every other workflow reads from.

Covers [SDLC](sdlc-playbook.md) stages 0, 3, 15.

---

## When to use this

- New to a repository.
- `docs/project-context/` does not exist — most other workflows list it as a
  prerequisite, and this is what creates it.
- Before estimating work in an unfamiliar area.

## Prerequisites

Read access to the code. Nothing else.

---

## The chain

```
orchestrator:context path=./        → docs/context/ + bootstrapped project-context
    ↓
quality:audit path=./src            → health, SOLID violations, duplication, debt
    ↓
architect:analyse jira=PROJ-123     → deep dive on one area, when you have a target
```

Run the first two on any unfamiliar repository. Run the third when you have a
specific change in mind.

---

## What each command gives you

**`orchestrator:context`** — scans the repository and writes `docs/context/`:
`architecture.md` with a Mermaid diagram, `tech-stack.md`, machine-readable
`context.json`, and an interactive `design.html` with four tabs. This is
breadth: what exists, how it is wired, what it is built from.

**`quality:audit`** — depth on quality: architecture assessment, SOLID
violations, duplication, tech debt scoring, and a refactoring roadmap. Read the
debt scores before promising any timeline.

**`architect:analyse`** — depth on one change: how the affected path works
today, with `file:line` citations, plus the decisions the change will require.
Every claim about current behaviour is FACT and cited — if it was not read, it
is not asserted.

---

## Bootstrapping the Project Context

First run creates `docs/project-context/`, the 14-node tree every companion
reads. Nodes it cannot fill are stubbed `not yet populated` rather than guessed.

An empty node is honest. A hallucinated one is worse than nothing, because the
next agent will read it as established fact.

Ownership — who fills each node, and when:

| Node | Owner | Filled during |
|---|---|---|
| `project-overview.md`, `risks.md`, `release-history.md` | orchestrator | This workflow, then release |
| `business-context.md`, `mvp-scope.md` | business_analyst | [02](02-feature-from-conversation.md) |
| `technical-context.md`, `architecture-context.md`, `known-behaviours.md`, `technical-debt.md` | architect | This workflow and [05](05-record-a-decision.md) |
| `quality/*.md` | quality | [08](08-audit-security.md), [09](09-optimise-performance.md), and QA |
| `dependencies.md` | implementer | On dependency change |
| `open-questions.md`, `ai-memory.md` | any | Continuously |

Full detail: `skills/project_context_skill.md`.

---

## Artifacts

| Path | From |
|---|---|
| `docs/context/architecture.md`, `tech-stack.md`, `context.json`, `design.html` | `orchestrator:context` |
| `docs/project-context/` (14 nodes) | Bootstrapped here |
| Audit report with debt scores | `quality:audit` |
| `docs/analysis/<JIRA>-technical-analysis.md` | `architect:analyse` |

---

## What to record that the code cannot tell you

`ai-memory.md` is append-only. Use it for what a file read would never reveal:
dead ends already explored, why an obvious approach fails here, tribal knowledge
from a conversation.

Do **not** record what reading the code would show. That is duplication that
goes stale.

---

## Worked example

[../04-examples/quality.md](../04-examples/quality.md) — codebase audit scenario.

---

## Next

- [10 — Modernise a legacy system](10-modernise-legacy-system.md) if the audit is grim
- [02](02-feature-from-conversation.md) or [03](03-feature-from-requirement.md) to build
