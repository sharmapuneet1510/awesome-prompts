# Skills Playbook

**Which skills load at each stage — requirement to release.**

The [SDLC playbook](sdlc-playbook.md) answers *which command, and which gate*.
This page answers the next question: *which of the 44 skills does that command
load, and what does it leave behind?* Same 16 stages, same numbering. Every
command here is one of the [43 real functions](../02-reference/functions.md).

---

## How a skill is used in a run

```
command (agent:function)
   │
   ├─ reads each skill's Quick Card        ← always; short
   ├─ loads one numbered section           ← only when a step needs it
   ├─ does the work, keeping a step log
   └─ writes one HTML run report           ← only if files changed (html_report_skill)
```

That is the whole token budget story: cards are read, bodies are loaded on
demand, and the report is written once from the step log. Pass `report=none`
to skip the report or `report=md` for Markdown.

---

## Stage map

| # | Stage | Commands | Skills loaded | Leaves behind |
|---|---|---|---|---|
| 0 | Inception | `orchestrator:context` · `orchestrator:ideate` · `ba:parse` | `project_setup_skill` (new project) · `context_builder_skill` · `project_context_skill` (bootstrap) · `jira_html_report_skill` | `docs/project-setup/` · `AGENTS.md` · `docs/context/` · `docs/project-context/` |
| 1 | Discovery | `ba:discover` · `ba:clarify` | `project_context_skill` · `traceability_skill` | `discovery-notes.md` · `open-questions.md` |
| 2 | Requirements | `ba:brd` · `ba:create` | `ba_create_skill` · `project_context_skill` · `jira_incremental_spec_generator_skill` (existing Jira project) | `docs/brd.md` · `requirements.json` · `requirements-cards.html` |
| 3 | Technical analysis | `architect:analyse` · `quality:audit` · `orchestrator:solve` | `context_builder_skill` · `project_context_skill` · `adr_skill` · `code_health_skill` | `docs/analysis/<JIRA>-technical-analysis.md` |
| 4 | **Decision** — gate | `architect:adr` | `adr_skill` · `nemesis_skill` (if policy enables it) | `docs/adr/ADR-<NNNN>-<slug>.md` at `Accepted` |
| 5 | Specification | `architect:spec` | `current_tech_spec_skill` · `adr_skill` · `traceability_skill` | `docs/current-technical-specification.md` |
| 6 | **Planning** — gate | `orchestrator:plan` · `orchestrator:risk` | `spec_driven_development_skill` | `specs/<feature>/requirements.md` — Approved |
| 7 | **Design** — gate | `architect:design` · `:api` · `:schema` · `:frontend` · `:a11y` · `:refactor` | `spec_driven_development_skill` · `backend_skill` · `database_skill` · `frontend_skill` · `react_advanced_skill` · `oop_skill` · `refactoring_skill` · `mcp_server_skill` (when designing agent tools) | `specs/<feature>/design.md` — Approved |
| 8 | **Task breakdown** — gate | implementer, seeded by `tools/task_generator.py` (library, no CLI) | `spec_driven_development_skill` · `traceability_skill` (T-10) | `specs/<feature>/tasks.md` — Approved |
| 9 | Implementation | `implementer:full` (or `:build` · `:test` · `:doc`) | `jira_implementation_skill` (work driven by one Jira ticket) · Gate: `spec_driven_development_skill` · `adr_skill` · `traceability_skill` · `project_context_skill` — then by stack, below | `src/` · `tests/` · docs |
| 10 | Packaging & infra | `implementer:pipeline` · `:docker` · `:iac` | `maven_skill` · `python_project_skill` (build, image) · `ansible_skill` (hosts) · `opentelemetry_skill` | CI workflow · `Dockerfile` · playbooks · manifests |
| 11 | Review & conformance | `quality:observe` · `:review` · `:security` · `:perf` · `:batch-review` | `adr_skill` · `current_tech_spec_skill` · `traceability_skill` (observe) · `code_review_skill` · `security_audit_skill` · `code_health_skill` (PERF) · `mssql_dba_skill` (SQL Server) · `multi_review_html_skill` | `docs/observations/<PR>-observations.md` · review reports |
| 12 | QA | `quality:qa` | `test_skill` · `security_audit_skill` · `project_context_skill` | `docs/project-context/quality/*.md` · suites |
| 13 | **Release** — gate | `ba:trace` · `orchestrator:pr` | `traceability_skill` · `current_tech_spec_skill` (Final Implementation Record) · `nemesis_skill` (optional, before the release PR) | PR · `docs/traceability-report-<date>.md` |
| 14 | Operate | `quality:diagnose` · `:debug` · `:report` | `debugging_skill` · `logger_skill` · `opentelemetry_skill` · `error_handling_skill` · `mssql_dba_skill` (blocking, deadlocks) | RCA · new `REG-n` scenario |
| 15 | Evolve | `quality:audit` · `architect:refactor` · `architect:adr` | `code_health_skill` · `refactoring_skill` · `adr_skill` | `technical-debt.md` rows · superseding ADRs |

Any stage: `orchestrator:nemesis target=…` loads `nemesis_skill` to attack a
finished conclusion. Every stage that changes files writes its report per
`html_report_skill`.

---

## Stage 9 — skills by stack

`implementer:build` detects the stack and loads only what it finds.

| Detected | Loads |
|---|---|
| Java | `java_advanced_skill` · `spring_advanced_skill` · `lombok_skill` · `logger_skill` · `maven_skill` |
| Python | `python_advanced_skill` · `backend_skill` · `python_project_skill` |
| React / TypeScript | `react_advanced_skill` · `frontend_skill` |
| SQL | `database_skill` · `mssql_advanced_skill` (SQL Server) |
| Messaging / integration | `apache_pulsar_skill` · `apache_camel_skill` |
| Observability work | `opentelemetry_skill` · `logger_skill` |
| Building an MCP server | `mcp_server_builder_skill` + `mcp_server_skill` |
| **Always** | `error_handling_skill` · `oop_skill` · `test_skill` · `code_documentation_skill` · `code_formatting_skill` |

Each coding skill's Quick Card carries **senior defaults** — the handful of
advanced rules that matter most for that stack. Examples:

| Skill | A senior default |
|---|---|
| `java_advanced_skill` | Sealed interfaces + exhaustive `switch` for closed result types |
| `python_advanced_skill` | Never block the event loop — sync DB session means a plain `def` route |
| `backend_skill` | Verify a dummy hash for unknown users so login timing cannot enumerate accounts |
| `lombok_skill` | Never `@Data` on a JPA entity — id-based `equals`, constant `hashCode` |
| `test_skill` | Mutation score, not line coverage, proves a suite |
| `opentelemetry_skill` | OTLP everywhere — the Jaeger exporters are gone |
| `maven_skill` | A custom Surefire `argLine` without `@{argLine}` silently skips the coverage gate |
| `mssql_dba_skill` | Fix the head blocker, never the victims |

---

## Worked path — conversation to release

A stakeholder says: *"customers get charged twice when checkout retries."*

```text
ba:discover source="call notes 2026-09-28"     project_context_skill, traceability_skill
ba:clarify                                     project_context_skill
ba:brd                                         ba_create_skill, project_context_skill
ba:create path=docs/brd.md                     ba_create_skill
        ↓
architect:analyse jira=PAY-88                  context_builder_skill, adr_skill
architect:adr jira=PAY-88                      adr_skill          → human approves → Accepted
architect:spec                                 current_tech_spec_skill
        ↓
orchestrator:plan                              spec_driven_development_skill  → approve requirements.md
architect:design                               backend_skill, database_skill  → approve design.md
(implementer writes tasks.md)                  spec_driven_development_skill  → approve tasks.md
implementer:full path=specs/checkout-idempotency
                                               python_advanced_skill, backend_skill, database_skill,
                                               error_handling_skill, test_skill, code_documentation_skill
        ↓
quality:observe pr=412                         adr_skill, current_tech_spec_skill, traceability_skill
quality:security path=src/checkout             security_audit_skill
quality:qa suite=regression mode=generate      test_skill
ba:trace scope=release version=2.4.0           traceability_skill
orchestrator:pr                                traceability_skill
```

Each line that changed files leaves one report in `docs/reports/`. Read them
in date order and you have the whole story: what each step was asked, what it
did, which files it touched, which claims were facts and which were proposals,
and which gates passed.

---

## Short paths

| Situation | Start at | Skills you will actually load |
|---|---|---|
| One-line fix, config tweak | Stage 9, exempt from spec gates | stack skill · `test_skill` |
| Bug with a known cause | Stage 14 → 9 | `debugging_skill` · stack skill · `test_skill` |
| Bug with an unknown cause | Stage 14 | `debugging_skill` · `logger_skill` · `opentelemetry_skill` |
| Written requirement | Stage 6 | `spec_driven_development_skill` → stage 7–13 skills |
| New project, nothing decided | Stage 0 | `project_setup_skill` → then stage 1 |
| Inherited codebase | Stage 0 → 3 | `context_builder_skill` · `code_health_skill` · `project_context_skill` |
| Slow or blocked SQL Server | Stage 14 | `mssql_dba_skill` |
| Legacy modernisation | Stage 3 → 15 | `code_health_skill` · `refactoring_skill` · `adr_skill` |
| One Jira ticket, end to end | Stage 3 (or 0 for a new project) | `jira_implementation_skill` — it routes to the class's skills and gates |
| Writing a new skill | — | `agent_skill_design_skill` |

---

## See also

- [sdlc-playbook.md](sdlc-playbook.md) — commands, gates, and exit criteria per stage
- [../02-reference/skills.md](../02-reference/skills.md) — every skill, grouped
- [../02-reference/SUPER_SKILLS_ENHANCEMENT.md](../02-reference/SUPER_SKILLS_ENHANCEMENT.md) — the Quick Card standard and what changed
- [README.md](README.md) — the 15 task workflows
