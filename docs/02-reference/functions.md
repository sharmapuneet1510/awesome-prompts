# Function Reference

**All 42 callable functions.** One source of truth — this file replaces the five
overlapping documents now in [../99-archive/superseded/](../99-archive/superseded/).

Invoke with `agent:function [key=value ...]`. With a function named, the agent
runs only that function's steps and skips its intro workflow.

For *when* to use each, see [../01-workflows/](../01-workflows/).
For stage mapping, see [../01-workflows/sdlc-playbook.md](../01-workflows/sdlc-playbook.md).

---

## At a glance

| Agent | Prefix | Count | Functions |
|---|---|---|---|
| [Orchestrator](#orchestrator) | `orchestrator` | 9 | plan, build, context, pr, review, tradeoff, risk, ideate, solve |
| [Architect](#architect) | `architect` | 9 | design, refactor, frontend, schema, api, a11y, analyse, adr, spec |
| [Implementer](#implementer) | `implementer` | 7 | build, test, doc, pipeline, docker, iac, full |
| [Quality](#quality) | `quality` | 10 | review, audit, security, perf, debug, report, batch-review, diagnose, observe, qa |
| [Business Analyst](#business-analyst) | `ba` | 7 | parse, report, create, discover, clarify, brd, trace |

---

## Orchestrator

Strategy, orchestration, and technical leadership.

| Function | Does | Key inputs | Workflow |
|---|---|---|---|
| `orchestrator:plan` | Parse requirement, produce `requirements.md`, break into tasks | — | [01](../01-workflows/01-start-new-project.md), [03](../01-workflows/03-feature-from-requirement.md) |
| `orchestrator:context` | Scan project, build `docs/context/` and bootstrap Project Context | `path` | [04](../01-workflows/04-understand-a-codebase.md) |
| `orchestrator:build` | Full-stack generation across all tasks, auto-chaining design → implementation | `path` | [01](../01-workflows/01-start-new-project.md) |
| `orchestrator:pr` | Package deliverables, open the GitHub PR, sync artifacts | — | [13](../01-workflows/13-ship-a-release.md) |
| `orchestrator:review` | Architecture review, design validation, gap analysis | — | [01](../01-workflows/01-start-new-project.md) |
| `orchestrator:tradeoff` | Complexity vs. simplicity, three-option comparison | — | [10](../01-workflows/10-modernise-legacy-system.md) |
| `orchestrator:risk` | Risk assessment, failure modes, mitigations | — | [10](../01-workflows/10-modernise-legacy-system.md) |
| `orchestrator:ideate` | Turn a vague idea into a validated project plan | `idea` | [01](../01-workflows/01-start-new-project.md) |
| `orchestrator:solve` | Solve a design bottleneck with multi-dimensional options | `problem` | [10](../01-workflows/10-modernise-legacy-system.md) |

`ideate` and `solve` use three shared modules: `ideation_engine`,
`design_solver`, `expert_panel_generator` (`agents/orchestrator/modules/`).

---

## Architect

Architecture, design, and — since v5.0.0 — the Developer Companion role:
technical analysis, decisions, and the specification.

| Function | Does | Key inputs | Workflow |
|---|---|---|---|
| `architect:design` | Greenfield design: C4 topology, API contracts, schema, deployment | `requirements`, `tech_stack` | [01](../01-workflows/01-start-new-project.md) |
| `architect:refactor` | Brownfield: current state, phased roadmap, migration guide, rollback | `path` | [10](../01-workflows/10-modernise-legacy-system.md) |
| `architect:frontend` | Component hierarchy, composition, prop APIs, TypeScript interfaces | — | [01](../01-workflows/01-start-new-project.md) |
| `architect:schema` | DDL, migrations, indexes, normalisation, partitioning | — | [01](../01-workflows/01-start-new-project.md) |
| `architect:api` | OpenAPI spec, endpoints, auth, rate limiting, error codes | — | [01](../01-workflows/01-start-new-project.md) |
| `architect:a11y` | WCAG 2.1 AA planning, keyboard navigation, semantic HTML, ARIA | — | [01](../01-workflows/01-start-new-project.md) |
| `architect:analyse` | Technical analysis against the codebase: current flow, options, risks | `jira`, `path`, `depth` | [02](../01-workflows/02-feature-from-conversation.md), [04](../01-workflows/04-understand-a-codebase.md) |
| `architect:adr` | **Mint an ADR — the only function that writes one** | `jira`, `decision`, `from`, `supersede`, `type` | [05](../01-workflows/05-record-a-decision.md) |
| `architect:spec` | Regenerate the Current Technical Specification from Accepted ADRs | `since`, `dry-run` | [05](../01-workflows/05-record-a-decision.md) |

---

## Implementer

Code generation and execution. The Coding Companion.

| Function | Does | Key inputs | Workflow |
|---|---|---|---|
| `implementer:full` | **Build + test + doc in one context window** — prefer this | `path` | [03](../01-workflows/03-feature-from-requirement.md) |
| `implementer:build` | Code only. Runs the four-check gate first | `path`, `tech_stack`, `style` | [03](../01-workflows/03-feature-from-requirement.md) |
| `implementer:test` | Tests only | `path` | [03](../01-workflows/03-feature-from-requirement.md) |
| `implementer:doc` | Documentation only | `path` | [03](../01-workflows/03-feature-from-requirement.md) |
| `implementer:pipeline` | CI/CD workflow | — | [11](../01-workflows/11-set-up-cicd.md) |
| `implementer:docker` | Dockerfile, compose, image build | — | [11](../01-workflows/11-set-up-cicd.md) |
| `implementer:iac` | Kubernetes manifests / infrastructure as code | — | [11](../01-workflows/11-set-up-cicd.md) |

**`implementer:build` gate** — refuses, rather than warns, when: `tasks.md` is
missing or unapproved; the change is decision-bearing and no Accepted ADR cites
its Parent Jira; `ba:trace` reports a High finding on T-1, T-2, T-10, or T-13;
or a task cites no requirement ID.

---

## Quality

QA, security, performance — plus the Review and QA Companion roles.

| Function | Does | Key inputs | Workflow |
|---|---|---|---|
| `quality:observe` | **Four-way conformance. Observations only** — never edits, never scores | `pr`, `jira`, `path`, `feature` | [06](../01-workflows/06-review-a-pull-request.md) |
| `quality:review` | PR validation: requirement mapping, quality scoring, coverage, docs | `pr` | [06](../01-workflows/06-review-a-pull-request.md) |
| `quality:audit` | Codebase audit: architecture, SOLID, duplication, debt, roadmap | `path` | [04](../01-workflows/04-understand-a-codebase.md) |
| `quality:security` | OWASP audit: authn, authz, injection, API, data protection | `path` | [08](../01-workflows/08-audit-security.md) |
| `quality:perf` | Profiling, bottlenecks, optimisation strategies, scalability | `path` | [09](../01-workflows/09-optimise-performance.md) |
| `quality:debug` | Root cause analysis, failure mechanism, edge cases, regression tests | `stack_trace` | [07](../01-workflows/07-fix-production-incident.md) |
| `quality:diagnose` | Conversational problem solving — symptom known, cause unknown | `problem` | [07](../01-workflows/07-fix-production-incident.md) |
| `quality:qa` | Maintain the five reusable suites | `suite`, `feature`, `mode` | [08](../01-workflows/08-audit-security.md), [09](../01-workflows/09-optimise-performance.md) |
| `quality:report` | Synthesise review + audit + security + perf + debug into one report | `pr` | [06](../01-workflows/06-review-a-pull-request.md) |
| `quality:batch-review` | Multi-PR review, one HTML report with sidebar tabs | `from` | [06](../01-workflows/06-review-a-pull-request.md) |

**`quality:qa` suites** — `sanity` (under 5 minutes) · `regression` (each row
cites its incident) · `integration` (names external systems) · `performance`
(numeric threshold + load profile) · `security` (mapped to OWASP). Add
`mode=generate` to write tests; default plans scenarios only.

---

## Business Analyst

Backlog handling, plus the BA Companion role.

| Function | Does | Key inputs | Workflow |
|---|---|---|---|
| `ba:discover` | Requirements from an unstructured discussion | `source`, `path`, `domain` | [02](../01-workflows/02-feature-from-conversation.md) |
| `ba:clarify` | Resolve ambiguity, one question at a time | `path`, `focus` | [02](../01-workflows/02-feature-from-conversation.md) |
| `ba:brd` | BRD + Business Context + MVP scope | `scope` | [02](../01-workflows/02-feature-from-conversation.md) |
| `ba:create` | Plain text → Jira issues with BDD acceptance criteria | `path` | [12](../01-workflows/12-manage-backlog.md) |
| `ba:parse` | Parse a Jira export (JSON or CSV), normalise fields | `path` | [12](../01-workflows/12-manage-backlog.md) |
| `ba:report` | Interactive HTML backlog with filters and statistics | `path` | [12](../01-workflows/12-manage-backlog.md) |
| `ba:trace` | Validate the eight-hop chain — 18 checks | `scope`, `feature`, `version`, `severity` | [13](../01-workflows/13-ship-a-release.md) |

---

## Dispatch rules

| Invocation | Behaviour |
|---|---|
| `agent:function` | Runs only that function's steps, skipping intro questions |
| `agent` alone | Full agent workflow with scope selection |
| `agent:function path=./dir` | Passes the path directly, skipping file prompts |

---

## Function files vs. dispatch entries

42 functions are declared in agent dispatch tables; 34 have standalone files
under `agents/<agent>/functions/`. The difference is documentation depth, not
capability — all 42 are callable.

Without a standalone file: `orchestrator:plan`, `:build`, `:pr`, `:review`,
`:risk`, and `ba:create`, all documented inside their parent agent file.

---

## Where the old documents went

| Was | Now |
|---|---|
| `AGENTS_FUNCTIONS.md` | This file |
| `AGENTS_FUNCTIONS_VERIFIED.md` | This file — it documented 28 functions |
| `FUNCTION_EXAMPLES.md` | [../04-examples/](../04-examples/) |
| `FUNCTION_QUICK_REFERENCE.md` | The at-a-glance table above |
| `docs/API_REFERENCE.md` | This file — it documented 31 functions |

All preserved in [../99-archive/superseded/](../99-archive/superseded/).
