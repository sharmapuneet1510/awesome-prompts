# 🤖 AI Agents Directory (v3.0 — 4-Role Architecture)

> Lean, role-based AI agents with function dispatch. **5 agents, 35 skills, 42 callable functions.**  
> **New in v3.0:** Consolidated 13 specialized agents into 4 primary roles + 1 utility agent. Linear execution pipeline prevents context loss.

## 🎯 Foundational Principles (Guide All Agents)

All agents operate under **four core behavioral principles** that guide every decision:

| Principle | What It Means | Applies To |
|-----------|--------------|-----------|,
| **Think Before Coding** | State assumptions, surface tradeoffs, present options before committing | Orchestrator, Architect, all agents |
| **Simplicity First** | Minimum code solving the problem; no overengineering or speculation | Implementer, all code generation |
| **Surgical Changes** | Touch only what you must; clean up only your own mess | Implementer, all code modifications |
| **Goal-Driven Execution** | Define success criteria upfront; loop until verified | Quality, all agents |

See `instructions/master_instruction_set.md` (FOUNDATIONAL PRINCIPLES section) for details.

---

## Quick Navigation (5 Agents)

| # | Agent | Role | Functions | Purpose | Version | Status |
|---|-------|------|-----------|---------|---------|--------|
| 1 | [Orchestrator](orchestrator_agent.md) | Strategy & Orchestration | plan, build, context, pr, review, tradeoff, risk, ideate, solve | Full-stack generation, technical leadership, ideation & design solving | v3.2 | ✅ Ready |
| 2 | [Architect](architect_agent.md) | Architecture & Design + Developer Companion | design, refactor, frontend, schema, api, a11y, **analyse, adr, spec** | System topology, API contracts, DB schema, UI architecture, technical analysis, ADRs, Current Technical Specification | v3.2 | ✅ Ready |
| 3 | [Implementer](implementer_agent.md) | Implementation & Execution + Coding Companion | build, test, doc, pipeline, docker, iac, full | Code generation, testing, documentation, deployment (gated on approved spec + ADR) | v3.2 | ✅ Ready |
| 4 | [Quality](quality_agent.md) | QA, Security & Performance + Review/QA Companions | review, audit, security, perf, debug, report, batch-review, diagnose, **observe, qa** | PR validation, security audit, optimization, debugging, conformance observation, 5 reusable suites | v3.2 | ✅ Ready |
| 5 | [Business Analyst](business_analyst_agent.md) | Backlog + BA Companion | report, parse, create, **discover, clarify, brd, trace** | JIRA parsing, backlog visualization, requirement discovery, BRD, traceability | v1.2 | ✅ Ready |

---

> **Which command at which stage?** See **[the SDLC playbook](../docs/01-workflows/sdlc-playbook.md)** —
> all 16 lifecycle stages, the commands available at each, the exit gate for
> each, and short paths for trivial changes, bug fixes, and greenfield work.

---

## Linear Execution Pipeline

```
User Requirement
    ↓
orchestrator:plan          ← Parse requirement, produce requirements.md
    ↓
architect:design           ← System topology, API contracts, DB schema
    ↓
implementer:full           ← BUILD + TEST + DOC (same context window, no loss)
    ↓
quality:review             ← Validate, score, generate report
    ↓
orchestrator:pr            ← Package and open GitHub PR
```

**Spec-driven gate (RULE 11):** `orchestrator:plan` = specify
(`requirements.md`), `architect:design` = plan (`design.md`),
`implementer` task generation = tasks (`tasks.md`) — each must be
`Status: Approved` before the next stage runs. See
`skills/spec_driven_development_skill.md`.

---

## Companion Pipeline (v3.2)

The five AI companions map onto the same five agents — no new agents. This is
the long-form pipeline, used when a change starts from a business discussion
rather than a written requirement.

```
Business discussion
    ↓
ba:discover → ba:clarify → ba:brd → ba:create   ← BA Companion
    ↓                                              Jira + acceptance criteria
architect:analyse                                ← Developer Companion
    ↓                                              current flow, options, risks (FACT/INFERENCE)
architect:adr        (continuous, not a phase)   ← one ADR per decision
    ↓                                              PROPOSAL → human → DECISION
architect:spec                                   ← Current Technical Specification
    ↓                                              regenerated from Accepted ADRs
orchestrator:plan → implementer:full             ← Coding Companion (gated)
    ↓
orchestrator:pr
    ↓
quality:observe                                  ← Review Companion (observations only)
    ↓
quality:qa                                       ← QA Companion (5 reusable suites)
    ↓
ba:trace                                         ← chain validation, 18 checks
    ↓
Project Context updated
```

**ADR gate (RULE 11a):** a change to a contract, data shape, dependency, or
failure mode needs an Accepted ADR before code is written. `architect:adr` is
the only function that writes one; `quality:observe` may propose one but never
writes it.

**Epistemic labelling (RULE 12):** every substantive claim is FACT, INFERENCE,
PROPOSAL, or DECISION. Only a human-approved DECISION changes the Current
Technical Specification. See `skills/adr_skill.md`,
`skills/current_tech_spec_skill.md`, `skills/project_context_skill.md`,
`skills/traceability_skill.md`.

**Key Innovation:** `implementer:full` runs build → test → doc in a single execution, maintaining full context awareness through all phases. This prevents the state-transfer overhead that existed in v2.0.

---

## 🎯 Function Dispatch Syntax (v3.0)

**Invoke specific agent functions** instead of full workflows:

```
agent:function [path=...] [option=value]

Examples:
  orchestrator:plan                    → Parse requirement, create task breakdown
  orchestrator:build path=./design     → Full-stack generation
  architect:design                     → Greenfield system design
  architect:refactor path=./src        → Brownfield migration plan
  implementer:build path=./api-spec    → Generate code only
  implementer:test path=./src          → Generate tests only
  implementer:doc path=./src           → Generate docs only
  implementer:full path=./design       → Build + test + doc (no context loss)
  quality:review pr=123                → PR validation & scoring
  quality:audit path=./src             → Full codebase audit
  quality:security path=./src          → OWASP security audit
  quality:perf path=./src              → Performance optimization analysis
  quality:debug stack_trace="..."      → Root cause analysis
  quality:report pr=123                → Unified quality synthesis
  quality:batch-review from=./reviews  → Multi-PR review with HTML report
  quality:diagnose problem="..."       → Conversational problem solver
  ba:report path=./jira-export.json    → Parse JIRA → HTML backlog

Companion functions (v3.2):
  ba:discover source="..."             → Requirements from a business discussion
  ba:clarify                           → Resolve ambiguity, one question at a time
  ba:brd                               → BRD + Business Context + MVP scope
  ba:trace scope=release version=2.4.0 → Validate the 8-hop traceability chain
  architect:analyse jira=PROJ-123      → Technical analysis against the codebase
  architect:adr jira=PROJ-123          → Mint an Engineering Decision Record
  architect:spec                       → Regenerate the Current Technical Specification
  quality:observe pr=123               → 4-way conformance gaps, observations only
  quality:qa suite=regression          → Maintain the 5 reusable quality suites
```

**See [the function reference](../docs/02-reference/functions.md) for all 42 callable functions with detailed inputs, outputs, and examples.**
---

## 📖 Complete Examples Guide

**See [the examples](../docs/04-examples/README.md) for real-world usage examples of 28 of the 42 functions:**

- **Orchestrator** (9 functions) — plan, build, context, review, tradeoff, risk, pr, ideate, solve
- **Architect** (9 functions) — design, refactor, frontend, schema, api, a11y, analyse, adr, spec
- **Implementer** (7 functions) — build, test, doc, pipeline, docker, iac, full
- **Quality** (10 functions) — review, audit, security, perf, debug, report, batch-review, diagnose, observe, qa
- **Business Analyst** (7 functions) — report, parse, create, discover, clarify, brd, trace

The nine companion functions (analyse, adr, spec, observe, qa, discover,
clarify, brd, trace) are documented in their own function files under
`agents/<agent>/functions/`; the example library predates them.

Each function includes:
✓ Real-world examples | ✓ Parameters explained | ✓ Expected outputs | ✓ When to use


---

## 🎯 Consolidation Summary (v2.0 → v3.0)

**Reduction from 13 agents to 5:**

### Merged Into Orchestrator (2 agents)
- `autonomous_dev_agent` → orchestrator (plan, build, context, pr)
- `technical_lead_agent` → orchestrator (review, tradeoff, risk)

### Merged Into Architect (2 agents)
- `architecture_agent` → architect (design, refactor, schema, api)
- `senior_frontend_engineer_agent` → architect (frontend, a11y)

### Merged Into Implementer (4 agents)
- `implementation_agent` → implementer (build)
- `integration_agent` → implementer (pipeline, docker, iac)
- `test_case_generator_agent` → implementer (test)
- `documentation_agent` → implementer (doc)

### Merged Into Quality (5 agents)
- `code_review_agent` → quality (review)
- `codebase_auditor_agent` → quality (audit)
- `security_auditor_agent` → quality (security)
- `performance_optimizer_agent` → quality (perf)
- `production_debugger_agent` → quality (debug)

### Kept Unchanged (1 agent)
- `business_analyst_agent` → ba (report, parse)

---

## Architecture Pattern

```
User Requirement
    ↓
Role-Based Agent (Orchestrator, Architect, Implementer, Quality)
    ├─ Parse context
    ├─ Dispatch to specific function (agent:function syntax)
    ├─ Apply skill(s)
    └─ Generate + validate + document
    ↓
Reusable Skills Layer (35 skills)
    ├─ Code Documentation (Javadoc, docstrings, JSDoc)
    ├─ Database (DDL, migrations, schema design)
    ├─ Backend API (REST, OpenAPI)
    ├─ Frontend (React, TypeScript)
    ├─ Testing (JUnit5, pytest, Jest)
    ├─ Advanced patterns (Java, Python, React, T-SQL, Spring, Camel, Pulsar, etc.)
    └─ [etc.]
    ↓
Output (Production-Ready)
    ├─ Code (with master_instruction_set compliance)
    ├─ Tests (95%+ coverage with business validation)
    ├─ Documentation (inline + architecture + API)
    └─ GitHub PR (ready for review)
```

---

## Agent Details

Each agent's full definition, including its dispatch table and per-function
behaviour, lives in its own file:

| Agent | Definition | Functions |
|---|---|---|
| Orchestrator | [orchestrator_agent.md](orchestrator_agent.md) | [orchestrator/functions/](orchestrator/functions/) |
| Architect | [architect_agent.md](architect_agent.md) | [architect/functions/](architect/functions/) |
| Implementer | [implementer_agent.md](implementer_agent.md) | [implementer/functions/](implementer/functions/) |
| Quality | [quality_agent.md](quality_agent.md) | [quality/functions/](quality/functions/) |
| Business Analyst | [business_analyst_agent.md](business_analyst_agent.md) | [business_analyst/functions/](business_analyst/functions/) |

For a narrative description of what each agent owns and why the roles are split
this way, see [../docs/02-reference/agents.md](../docs/02-reference/agents.md).

> **Removed 2026-08-21.** This section previously documented eight agents —
> `implementation_agent`, `code_review_agent`, `architecture_agent`,
> `test_case_generator_agent`, `documentation_agent`, `integration_agent`,
> `autonomous_dev_agent`, and a separate systems architect — all of which were
> consolidated into the five above in v4.0.0 (June 2026). The sections had
> outlived the files they described. See
> [../CHANGELOG.md](../CHANGELOG.md) for the 13 → 5 mapping.

---

## 🔗 Common Workflows

### Workflow 1: Build a Feature
1. **Implementation Engineer** → Code + tests + docs
2. **Code Reviewer** → Validate against JIRA
3. **DevOps Engineer** → Deploy to production

### Workflow 2: Audit Existing Codebase
1. **Codebase Auditor** → Scan for issues, tech debt, violations
2. **Production Debugger** → Deep-dive on critical issues
3. **Performance Optimizer** → Identify bottlenecks
4. **Systems Architect** → Design refactoring roadmap

### Workflow 3: Build New System
1. **Systems Architect** → Design topology, API contracts, DB schema
2. **Implementation Engineer** → Build backend
3. **Senior Frontend Engineer** → Build frontend
4. **Test Engineer** → Generate 100% coverage tests
5. **Security Auditor** → Vulnerability audit
6. **DevOps Engineer** → CI/CD + deployment
7. **Documentation Engineer** → Auto-generate docs

### Workflow 4: Refactor Existing System
1. **Systems Architect** → Analyze current state, design target state, create phased plan
2. **Implementation Engineer** → Execute each phase
3. **Code Reviewer** → Validate each phase
4. **Test Engineer** → Ensure coverage
5. **Production Debugger** → Handle issues
6. **Documentation Engineer** → Update architecture docs

---

## 📋 Quick Reference Matrix

| Task | Agent | Estimated Time |
|------|-------|-----------------|
| Build a feature | Implementation Engineer | 5-10 min |
| Review a PR | Code Reviewer | 2-5 min |
| Generate tests | Test Engineer | 3-7 min |
| Document code/API | Documentation Engineer | 2-10 min |
| Setup CI/CD | DevOps Engineer | 10-15 min |
| Full system from scratch | Autonomous Dev | 20-30 min |
| Design new system | Systems Architect | 15-30 min |
| Refactor existing system | Systems Architect | 30-120 min |
| Audit codebase | Codebase Auditor | 10-30 min |
| Find production bug | Production Debugger | 15-60 min |
| Optimize performance | Performance Optimizer | 20-60 min |
| Security review | Security Auditor | 15-45 min |
| Visualize backlog | Business Analyst | 2-5 min |

---

## 🔗 Links

- **[Skills Directory](../skills/README.md)** — Reusable skill modules (31 total)
- **[Tools Documentation](../tools/README.md)** — Utility scripts
- **[Master Rules](../instructions/master_instruction_set.md)** — Non-negotiable standards
- **[Main README](../README.md)** — Project overview
- **[Workflows](../docs/01-workflows/README.md)** — 14 use cases, each a complete path

---

**Last Updated:** June 3, 2026 | **Version:** 2.0.0 (Consolidated) | **Agents:** 5 | **Skills:** 31
