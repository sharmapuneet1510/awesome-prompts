---
title: SDLC Playbook
description: The complete software development lifecycle, stage by stage, with the exact command to run at each stage and the gate that must pass before the next one starts
version: 1.0
---

# SDLC Playbook

**Which command do I run, at which stage, and what must be true before I move on.**

Sixteen stages from business discussion to evolution. Every stage names its
owner, its commands, the artifacts it produces, and its **exit gate** — the
condition that must hold before the next stage may start.

- For *worked examples* of individual stages, see [Examples](../04-examples/README.md).
- For *per-function* inputs and outputs, see [Function reference](../02-reference/functions.md).
- For the *rules* the gates enforce, see [instructions/master_instruction_set.md](../02-reference/rules.md).

---

## The Cycle

```
                    ┌─────────────────────────────────────────────┐
                    │                                             │
   0 Inception ─▶ 1 Discovery ─▶ 2 Requirements                   │
                                      │                           │
                                      ▼                           │
                              3 Technical Analysis                │
                                      │                           │
                                      ▼                           │
                              4 Decision (ADR) ◀── GATE 11a       │
                                      │                           │
                                      ▼                           │
                              5 Specification                     │
                                      │                           │
                                      ▼                           │
      6 Planning ◀── GATE 11 ──▶ 7 Design ──▶ 8 Task Breakdown    │
                                      │                           │
                                      ▼                           │
                              9 Implementation                    │
                                      │                           │
                                      ▼                           │
                          10 Packaging & Infrastructure           │
                                      │                           │
                                      ▼                           │
                          11 Review & Conformance                 │
                                      │                           │
                                      ▼                           │
                                  12 QA                           │
                                      │                           │
                                      ▼                           │
                              13 Release                          │
                                      │                           │
                          ┌───────────┴───────────┐               │
                          ▼                       ▼               │
                    14 Operate              15 Evolve ────────────┘
```

Stages 3–5 repeat continuously. An ADR is written the moment a decision is
made, not batched at the end of a sprint.

---

## Stage Reference

| # | Stage | Owner | Primary commands | Exit gate |
|---|---|---|---|---|
| 0 | Inception | Orchestrator | `orchestrator:context`, `orchestrator:ideate`, `ba:parse` | Project Context tree exists |
| 1 | Discovery | BA | `ba:discover`, `ba:clarify` | No unanswered high-cost question |
| 2 | Requirements | BA | `ba:brd`, `ba:create` | BRD approved; Jira + ACs exist |
| 3 | Technical Analysis | Architect | `architect:analyse`, `quality:audit`, `orchestrator:solve` | "Decisions Required" list produced |
| 4 | Decision | Architect | `architect:adr` | **ADR at `Accepted` — human-approved (RULE 11a)** |
| 5 | Specification | Architect | `architect:spec` | Spec regenerated; no ADR conflicts |
| 6 | Planning | Orchestrator | `orchestrator:plan`, `orchestrator:risk` | **`requirements.md` = `Status: Approved` (RULE 11)** |
| 7 | Design | Architect | `architect:design`, `:api`, `:schema`, `:frontend`, `:a11y`, `:refactor` | **`design.md` = `Status: Approved` (RULE 11)** |
| 8 | Task Breakdown | Implementer | `tools/task_generator.py` | **`tasks.md` = `Status: Approved` (RULE 11)** |
| 9 | Implementation | Implementer | `implementer:full` (or `:build`, `:test`, `:doc`) | Code + tests + docs; tests green |
| 10 | Packaging & Infra | Implementer | `implementer:pipeline`, `:docker`, `:iac` | Deployable artifact builds |
| 11 | Review & Conformance | Quality | `quality:observe`, `:review`, `:security`, `:perf` | No High findings open |
| 12 | QA | Quality | `quality:qa` | Five suites updated and passing |
| 13 | Release | Orchestrator + BA | `orchestrator:pr`, `ba:trace` | Traceability chain intact (18 checks) |
| 14 | Operate | Quality | `quality:diagnose`, `:debug`, `:report` | Incident closed; regression scenario added |
| 15 | Evolve | Architect + Quality | `quality:audit`, `architect:refactor`, `architect:adr` | Debt recorded; superseding ADR accepted |

---

## Stage 0 — Inception

**Understand the ground before touching anything.** Run once per project, then
only when the landscape changes.

| Command | Use when |
|---|---|
| `orchestrator:context path=./` | Brownfield — scan the codebase, build `docs/context/` |
| `orchestrator:ideate idea="..."` | The idea is still vague and needs shaping into a project |
| `ba:parse path=./jira-export.json` | A backlog already exists and needs normalising |
| `ba:report path=./jira-export.json` | Stakeholders need a visual backlog |

**Produces:** `docs/context/` (architecture.md, tech-stack.md, context.json,
design.html) and the bootstrapped `docs/project-context/` tree.

**Exit gate:** `docs/project-context/README.md` exists with every node stubbed.
Leave unknown nodes marked `not yet populated` — an empty node is honest, a
hallucinated one is worse than nothing.

---

## Stage 1 — Discovery

**Capture the problem space. Propose no solutions.**

| Command | Use when |
|---|---|
| `ba:discover source="<transcript>"` | Starting from a conversation, email thread, or notes |
| `ba:discover path=./notes.md` | The discussion is already in a file |
| `ba:clarify` | Discovery surfaced ambiguities that need resolving |
| `ba:clarify focus=rules` | Only one area is unclear |

**Produces:** `discovery-notes.md`, and one `Q-n` row in
`open-questions.md` per ambiguity.

**Exit gate:** every question whose wrong answer would be expensive is answered
or explicitly deferred with a named owner. `ba:clarify` asks one question at a
time — a batch of six questions gets three answered.

**Do not** invent acceptance criteria here, and do not resolve vague terms
("fast", "secure") on the stakeholder's behalf. Both belong to later stages.

---

## Stage 2 — Requirements

**Turn the clarified problem into a specification stakeholders can approve.**

| Command | Use when |
|---|---|
| `ba:brd` | Discovery is clarified and needs a Business Requirements Document |
| `ba:brd scope=mvp` | Restricting output to MVP scope |
| `ba:create path=./requirements.txt` | Generating Jira issues with BDD acceptance criteria |

**Produces:** `docs/brd.md`, `docs/project-context/business-context.md`,
`docs/project-context/mvp-scope.md`, Jira issues with ACs.

**Exit gate:** the BRD is approved. Every goal has a metric, every business
rule (`BR-n`) is a testable statement, and the out-of-scope table is filled —
what was deliberately excluded is what stops scope creep being re-litigated
every sprint.

---

## Stage 3 — Technical Analysis

**Explain how it works today. Decide nothing.**

| Command | Use when |
|---|---|
| `architect:analyse jira=PROJ-123` | A Jira item needs technical grounding |
| `architect:analyse jira=PROJ-123 path=./src` | Restricting the read to a subtree |
| `quality:audit path=./src` | The area is unfamiliar and needs a health assessment first |
| `orchestrator:solve problem="..."` | A design bottleneck needs multi-angle options |
| `orchestrator:tradeoff` | Two approaches need explicit comparison |

**Produces:** `docs/analysis/<JIRA>-technical-analysis.md` with current flow
(FACT, cited to `file:line`), affected surface, constraints, at least two
genuine options, and a **Decisions Required** list.

**Exit gate:** the Decisions Required list exists. That list is the input to
Stage 4 — an analysis that produces no decisions either found nothing or
smuggled its decisions into prose.

---

## Stage 4 — Decision · **GATE (RULE 11a)**

**One ADR per decision, written when the decision is made.**

| Command | Use when |
|---|---|
| `architect:adr jira=PROJ-123 from=./docs/analysis/PROJ-123-technical-analysis.md` | Recording a decision the analysis surfaced |
| `architect:adr decision="..." jira=PROJ-123` | Recording a decision made in conversation |
| `architect:adr supersede=ADR-0003 decision="..."` | Replacing an earlier decision |

**Trigger rule** — write an ADR when the change alters **a contract, a data
shape, a dependency, or a failure mode**. Renaming a variable does not qualify.
An ADR log nobody reads is worth as much as no log at all.

**Exit gate:** `Status: Accepted`. Proposed → Accepted is the **only
human-gated edge in the entire lifecycle**. An agent writes the status into the
file, but only after the user explicitly approves — never inferred from silence.

`quality:observe` may *propose* an ADR. Only `architect:adr` writes one.

---

## Stage 5 — Specification

**Regenerate the current-state document from the decisions.**

| Command | Use when |
|---|---|
| `architect:spec` | Any ADR just reached Accepted |
| `architect:spec since=ADR-0009` | Summarising what changed since a known point |
| `architect:spec dry-run=true` | Previewing the diff without writing |

**Produces:** `docs/current-technical-specification.md` (version bumped), plus
synced `technical-context.md` and `architecture-context.md`.

**Exit gate:** regeneration completed with no unresolved conflict between two
Accepted ADRs. A conflict means a missing supersede link — `architect:spec`
stops and reports it rather than picking a winner, because picking one would be
an agent making a decision, which RULE 12 forbids.

The spec is a **projection, never a source**. Do not hand-edit it; change an
ADR and regenerate.

---

## Stage 6 — Planning · **GATE (RULE 11 · specify)**

| Command | Use when |
|---|---|
| `orchestrator:plan` | Turning an approved requirement into `requirements.md` |
| `orchestrator:risk` | Assessing failure modes before committing |
| `orchestrator:review` | Validating an existing design against the requirement |

**Produces:** `specs/<feature-name>/requirements.md` with EARS-format
acceptance criteria and stable `REQ-n` IDs.

**Exit gate:** `**Status:** Approved` in `requirements.md`, set only after the
user explicitly approves.

---

## Stage 7 — Design · **GATE (RULE 11 · plan)**

`architect:design` refuses to run without an approved `requirements.md`.

| Command | Use when |
|---|---|
| `architect:design requirements="..."` | Greenfield — full topology |
| `architect:refactor path=./src` | Brownfield — phased migration roadmap |
| `architect:api` | API contract only (unblocks parallel front/back work) |
| `architect:schema` | Database schema only |
| `architect:frontend` | Component hierarchy and prop APIs |
| `architect:a11y` | WCAG 2.1 AA planning — retrofitting costs ~3x |

**Produces:** `specs/<feature-name>/design.md`, plus the artifact for whichever
narrow function was used.

**Exit gate:** `**Status:** Approved` in `design.md`.

---

## Stage 8 — Task Breakdown · **GATE (RULE 11 · tasks)**

| Command | Use when |
|---|---|
| `python tools/task_generator.py` | Seeding task structure from the design |

**Produces:** `specs/<feature-name>/tasks.md`, where **every row cites at least
one `REQ-n`**. A row with no requirement ID is a traceability violation.

**Exit gate:** `**Status:** Approved` in `tasks.md`.

---

## Stage 9 — Implementation

`implementer:build` runs a four-check gate first and **refuses** rather than
warning: approved `tasks.md`, an Accepted ADR for decision-bearing changes,
no High traceability findings, and every task citing a `REQ-n`.

| Command | Use when |
|---|---|
| `implementer:full path=./design` | **Default.** Build + test + doc in one context window — no state-transfer loss |
| `implementer:build path=./spec` | Code only |
| `implementer:test path=./src` | Tests only |
| `implementer:doc path=./src` | Docs only |

Prefer `implementer:full`. Splitting build / test / doc across three
invocations loses the context that connects them.

**Exit gate:** tests pass. Not "tests written" — tests *run and green*.

---

## Stage 10 — Packaging & Infrastructure

| Command | Use when |
|---|---|
| `implementer:pipeline` | CI/CD workflow needed |
| `implementer:docker` | Containerisation needed |
| `implementer:iac` | Kubernetes manifests / infrastructure as code |

**Exit gate:** the deployable artifact builds from a clean checkout.

---

## Stage 11 — Review & Conformance

Two distinct activities. Run `quality:observe` **first** — conformance before
opinion.

| Command | Answers |
|---|---|
| `quality:observe pr=123` | Does the code match what was agreed? Four comparisons: Requirement↔Code, ADR↔Code, Spec↔Code, Tests↔AC. **Observations only** — never edits, never scores |
| `quality:review pr=123` | Is the code any good? Scored PR validation; may propose fixes |
| `quality:security path=./src` | Can it be abused? OWASP audit |
| `quality:perf path=./src` | Is it fast enough? Profiling and bottlenecks |
| `quality:audit path=./src` | Whole-codebase health, SOLID, duplication, debt |
| `quality:batch-review from=./reviews` | Several PRs at once, single HTML report |
| `quality:report pr=123` | Synthesis of all the above into one executive report |

The sharpest finding `quality:observe` produces is **code contradicting an
Accepted ADR** — an undocumented reversal. Fixing that means either
implementing per the ADR or superseding it via `architect:adr`; never quietly
editing the ADR to match the code.

**Exit gate:** no High findings open.

---

## Stage 12 — QA

**Five reusable suites that accumulate across features**, not per-feature test
runs.

| Command | Suite | Constraint |
|---|---|---|
| `quality:qa suite=sanity` | Is it fundamentally alive? | Must run in under 5 minutes |
| `quality:qa suite=regression` | Did a fixed defect return? | Each row cites its originating incident |
| `quality:qa suite=integration` | Do the seams hold? | Names external systems and test doubles |
| `quality:qa suite=performance` | Fast enough under load? | Numeric threshold + load profile per row |
| `quality:qa suite=security` | Can it be abused? | Each row maps to an OWASP category |
| `quality:qa` | All five | |

Add `mode=generate` to write the tests; the default plans scenarios only.

**Extend, never replace** — a deleted scenario is lost coverage. Superseded
scenarios are marked obsolete with a reason, not removed.

**Exit gate:** suites updated and passing; every acceptance criterion covered
by at least one scenario.

---

## Stage 13 — Release

| Command | Use when |
|---|---|
| `orchestrator:pr` | Packaging deliverables and opening the GitHub PR |
| `ba:trace scope=release version=2.4.0` | Validating the full chain before shipping |

`ba:trace` runs all 18 checks at release scope: 7 forward (nothing stranded),
5 backward (nothing unexplained), 6 integrity (the graph is well-formed).

**Produces:** the PR, `docs/traceability-report-<date>.md`, a
`release-history.md` row naming the ADRs shipped, and the Final Implementation
Record.

**Exit gate:** no High traceability findings. High findings block the RULE 11
gate.

---

## Stage 14 — Operate

| Command | Use when |
|---|---|
| `quality:diagnose problem="..."` | Symptom is known, cause is not — conversational investigation |
| `quality:debug stack_trace="..."` | A stack trace or reproduction exists |
| `quality:report` | Synthesising an incident into an executive summary |

**Close the loop:** every incident adds a `REG-n` row to the regression suite
citing that incident, via `quality:qa suite=regression`. An incident that
produces no regression scenario will happen again.

If the root cause reveals a wrong decision, that is Stage 15 — supersede the
ADR, do not edit it.

---

## Stage 15 — Evolve

| Command | Use when |
|---|---|
| `quality:audit path=./src` | Periodic health check; tech debt scoring |
| `architect:refactor path=./src` | Structural change with no behaviour change |
| `architect:adr supersede=ADR-000X` | A past decision no longer holds |
| `architect:spec` | Regenerating after the superseding ADR is accepted |

Superseding never rewrites history. ADR-0003's body stays exactly as written —
the reasoning was correct at the time, and superseding is not a correction.

**Exit gate:** debt recorded as `TD-n` rows; the superseding ADR is Accepted and
the spec regenerated.

---

## Gate Reference

| Gate | Rule | Blocks | Released by |
|---|---|---|---|
| Requirements approved | RULE 11 | `architect:design` | User approves `requirements.md` |
| Design approved | RULE 11 | Task generation | User approves `design.md` |
| Tasks approved | RULE 11 | `implementer:build` / `:full` | User approves `tasks.md` |
| ADR accepted | RULE 11a | `implementer:build` on decision-bearing changes | User approves the ADR |
| Traceability clean | RULE 11a | `implementer:build`, release | High findings resolved |
| Label discipline | RULE 12 | Spec mutation | Only a human-approved DECISION |

**Exempt from RULE 11:** one-line fixes, config tweaks, small documentation
edits. Substantive changes to agent, skill, or instruction files are *not*
exempt.

**RULE 12 in one line:** every substantive claim is a FACT (cited),
INFERENCE (reasoned), PROPOSAL (awaiting a human), or DECISION (approved) —
and only a DECISION changes the Current Technical Specification.

---

## Short Paths

Not everything needs sixteen stages.

### One-line fix / config tweak
```
implementer:build → quality:review → orchestrator:pr
```
Exempt from RULE 11. No ADR unless it changes a contract, data shape,
dependency, or failure mode.

### Bug fix with a known cause
```
quality:debug → architect:adr (only if the fix changes a contract)
              → implementer:full → quality:qa suite=regression
              → quality:review → orchestrator:pr
```

### Feature from a written requirement (spec-driven, no discovery)
```
orchestrator:plan → architect:design → tasks → implementer:full
                  → quality:observe → quality:review → orchestrator:pr
```

### Feature from a business conversation (full cycle)
```
ba:discover → ba:clarify → ba:brd → ba:create
            → architect:analyse → architect:adr → architect:spec
            → orchestrator:plan → architect:design → tasks
            → implementer:full
            → quality:observe → quality:qa → orchestrator:pr → ba:trace
```

### Greenfield project
```
orchestrator:ideate → orchestrator:plan → architect:design
                    → orchestrator:build (auto-chains the pipeline)
                    → quality:review → orchestrator:pr
```

### Legacy modernisation
```
orchestrator:context → quality:audit → architect:analyse
                     → architect:adr (per migration decision)
                     → architect:refactor → implementer:full → quality:review
```

---

## Command Index by Stage

All 42 callable functions, mapped to where they belong.

| Command | Stage(s) |
|---|---|
| `ba:parse` | 0 |
| `ba:report` | 0 |
| `orchestrator:context` | 0, 15 |
| `orchestrator:ideate` | 0 |
| `ba:discover` | 1 |
| `ba:clarify` | 1 |
| `ba:brd` | 2 |
| `ba:create` | 2 |
| `architect:analyse` | 3, 15 |
| `orchestrator:solve` | 3 |
| `orchestrator:tradeoff` | 3, 6 |
| `architect:adr` | 4, 15 |
| `architect:spec` | 5, 15 |
| `orchestrator:plan` | 6 |
| `orchestrator:risk` | 6 |
| `orchestrator:review` | 6, 7 |
| `architect:design` | 7 |
| `architect:api` | 7 |
| `architect:schema` | 7 |
| `architect:frontend` | 7 |
| `architect:a11y` | 7 |
| `architect:refactor` | 7, 15 |
| `implementer:build` | 9 |
| `implementer:test` | 9 |
| `implementer:doc` | 9 |
| `implementer:full` | 9 |
| `orchestrator:build` | 9 (auto-chains 7–9) |
| `implementer:pipeline` | 10 |
| `implementer:docker` | 10 |
| `implementer:iac` | 10 |
| `quality:observe` | 11 |
| `quality:review` | 11 |
| `quality:security` | 11 |
| `quality:perf` | 11 |
| `quality:audit` | 3, 11, 15 |
| `quality:batch-review` | 11 |
| `quality:report` | 11, 14 |
| `quality:qa` | 12, 14 |
| `orchestrator:pr` | 13 |
| `ba:trace` | 9 (gate), 13 |
| `quality:diagnose` | 14 |
| `quality:debug` | 14 |

---

## Artifacts by Stage

Everything below lands in the **downstream project**, not in this repo.

| Stage | Artifact |
|---|---|
| 0 | `docs/context/`, `docs/project-context/` |
| 1 | `discovery-notes.md`, `open-questions.md` |
| 2 | `docs/brd.md`, `business-context.md`, `mvp-scope.md`, Jira + ACs |
| 3 | `docs/analysis/<JIRA>-technical-analysis.md` |
| 4 | `docs/adr/ADR-<NNNN>-<slug>.md` |
| 5 | `docs/current-technical-specification.md` |
| 6 | `specs/<feature>/requirements.md` |
| 7 | `specs/<feature>/design.md` |
| 8 | `specs/<feature>/tasks.md` |
| 9 | `src/`, `tests/`, docs |
| 10 | CI workflow, `Dockerfile`, IaC manifests |
| 11 | `docs/observations/<PR>-observations.md`, review reports |
| 12 | `docs/project-context/quality/*.md`, test suites |
| 13 | PR, `docs/traceability-report-<date>.md`, Final Implementation Record, `release-history.md` |
| 14 | RCA report, new `REG-n` scenarios |
| 15 | `technical-debt.md` rows, superseding ADRs |

---

## Related Documentation

- **[Examples](../04-examples/README.md)** — worked examples per agent
- **[Function reference](../02-reference/functions.md)** — per-function inputs and outputs
- **[Function reference](../02-reference/functions.md)** — one-page cheat sheets
- **[Agent reference](../02-reference/agents.md)** — nine specialist role modes
- **[agents/README.md](../../agents/README.md)** — agent descriptions and dispatch syntax
- **[skills/README.md](../02-reference/skills.md)** — the 35 reusable skills
- **[instructions/master_instruction_set.md](../02-reference/rules.md)** — RULES 0–12
