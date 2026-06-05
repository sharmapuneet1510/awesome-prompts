# 🤖 AI Agents Directory (v3.0 — 4-Role Architecture)

> Lean, role-based AI agents with function dispatch. **5 agents, 24 skills, 31 callable functions.**  
> **New in v3.0:** Consolidated 13 specialized agents into 4 primary roles + 1 utility agent. Linear execution pipeline prevents context loss.

## Quick Navigation (5 Agents)

| # | Agent | Role | Functions | Purpose | Version | Status |
|---|-------|------|-----------|---------|---------|--------|
| 1 | [Orchestrator](orchestrator_agent.md) | Strategy & Orchestration | plan, build, context, pr, review, tradeoff, risk | Full-stack generation & technical leadership | v3.0 | ✅ Ready |
| 2 | [Architect](architect_agent.md) | Architecture & Design | design, refactor, frontend, schema, api, a11y | System topology, API contracts, DB schema, UI architecture | v3.0 | ✅ Ready |
| 3 | [Implementer](implementer_agent.md) | Implementation & Execution | build, test, doc, pipeline, docker, iac, full | Code generation, testing, documentation, deployment | v3.0 | ✅ Ready |
| 4 | [Quality](quality_agent.md) | QA, Security & Performance | review, audit, security, perf, debug, report | PR validation, security audit, optimization, debugging | v3.0 | ✅ Ready |
| 5 | [Business Analyst](business_analyst_agent.md) | Utility — Backlog | report, parse | JIRA parsing, backlog visualization | v1.0 | ✅ Ready |

---

## Linear Execution Pipeline

```
User Requirement
    ↓
orchestrator:plan          ← Parse requirement, break into tasks
    ↓
architect:design           ← System topology, API contracts, DB schema
    ↓
implementer:full           ← BUILD + TEST + DOC (same context window, no loss)
    ↓
quality:review             ← Validate, score, generate report
    ↓
orchestrator:pr            ← Package and open GitHub PR
```

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
```

**See [AGENTS_FUNCTIONS.md](../AGENTS_FUNCTIONS.md) for all 31 callable functions with detailed inputs, outputs, and examples.**

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
Reusable Skills Layer (22 skills)
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

## 🔍 Implementation Agent (v3.0)

**File:** [`implementation_agent.md`](implementation_agent.md)

| Aspect | Details |
|--------|---------|
| **Purpose** | Full-lifecycle feature builder |
| **Input** | Requirement (free text / JIRA / file) |
| **Steps** | 7-step process (parse → plan → code → test → doc → PR) |
| **Output** | Complete code + tests + docs + GitHub PR |
| **Tech** | Java, Python, React, TypeScript, Node.js, SQL |

**When to use:** Building features, adding endpoints, implementing logic

---

## 🔍 Code Review Agent (v3.0)

**File:** [`code_review_agent.md`](code_review_agent.md)

| Aspect | Details |
|--------|---------|
| **Purpose** | Requirement-driven code validation |
| **Input** | PR/MR + JIRA requirement |
| **Analysis** | 6-phase (requirement → quality → testing → docs → scoring) |
| **Output** | Interactive HTML report + MR comment |
| **Grade** | A-F with weighted scorecard |

**Features:**
- 🎯 Requirement validation (AC coverage %)
- 📊 Weighted scorecard (Req 40% + Quality 30% + Testing 20% + Docs 10%)
- 📈 Interactive HTML reports
- 💬 MR comment summaries

**When to use:** Reviewing PRs, validating requirements, rating code quality

---

## 🏗️ Systems Architect Agent (v2.0) ⭐ MERGED

**File:** [`architecture_agent.md`](architecture_agent.md)

| Aspect | Details |
|--------|---------|
| **Purpose** | Design new systems (greenfield) OR refactor existing ones (brownfield) |
| **Greenfield** | API contracts, database schema, caching, deployment topology, code stubs |
| **Brownfield** | Current state assessment, problem diagnosis, phased migration plan, rollback strategies |
| **Output** | System topology diagrams, API contracts, DB schemas, phased roadmap, migration guides |

**Merged from:**
- ✅ `backend_systems_architect_agent` (new system design)
- ✅ `architecture_refactorer_agent` (existing system refactoring)

**When to use:** Designing new systems OR refactoring existing monoliths/legacy code

---

## 🧪 Test Case Generator (v1.0)

**File:** [`test_case_generator_agent.md`](test_case_generator_agent.md)

**Purpose:** Generate tests with 100% coverage + business validation

**Process:**
1. Fetch JIRA acceptance criteria
2. Analyze code context
3. Generate unit + integration tests
4. Validate all ACs covered
5. Run test suite (100% coverage)

**Output:** Complete test suite with JIRA validation

**When to use:** Need complete test coverage, JIRA-driven testing

---

## 📚 Documentation Engineer Agent (v2.0) ⭐ MERGED

**File:** [`documentation_agent.md`](documentation_agent.md)

**Purpose:** Comprehensive documentation across all levels

**Covers:**
- Code-level docs (Javadoc, docstrings, JSDoc)
- Architecture docs (context.json, architecture.md, tech-stack.md)
- API specifications (OpenAPI/Swagger)
- README + quick-start guides
- Interactive HTML documentation site

**Merged from:**
- ✅ `writer_agent` (code-level + API docs)
- ✅ `technical_documentation_agent` (architecture + HTML site)

**When to use:** Need any documentation (code docs, architecture, API, README, HTML site)

---

## 📊 Business Analyst Agent (v1.0) ⭐ NEW

**File:** [`business_analyst_agent.md`](business_analyst_agent.md)

| Aspect | Details |
|--------|---------|
| **Purpose** | Parse JIRA exports, generate interactive backlog reports |
| **Input** | Local JIRA JSON or CSV export |
| **Output** | Single-file HTML report (self-contained, no CDN) |
| **Features** | Filtering (status, priority, assignee, sprint), sorting, stats header, row expansion |

**When to use:** Need to visualize JIRA backlog, generate backlog reports, share with stakeholders

---

## ⚙️ Integration Agent (v1.0)

**File:** [`integration_agent.md`](integration_agent.md)

**Purpose:** CI/CD pipelines and deployment automation

**Generates:**
- GitHub Actions workflows
- Docker configuration
- Infrastructure as Code (Terraform)
- Monitoring & alerts
- Cloud deployment configs

**Supports:** AWS, GCP, Azure, Kubernetes

**When to use:** Need CI/CD setup, Docker, deployment automation

---

## 🚀 Autonomous Dev Agent (v1.0)

**File:** [`autonomous/autonomous_dev_agent.md`](autonomous/autonomous_dev_agent.md)

**Purpose:** Full-stack project orchestrator

**Scope:** Complete system generation (DB + API + UI + tests)

**Process:** 14-step orchestration
1. Parse requirement
2. Create database schema
3. Generate backend API
4. Create frontend UI
5. Write tests (100% coverage)
6. Generate documentation
7. Create GitHub PR
8. Ready for production

**When to use:** Building complete systems, MVPs, starting new projects

[📖 Full Guide](../AUTONOMOUS_DEVELOPER_README.md)

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

- **[Skills Directory](../skills/README.md)** — Reusable skill modules (23 total)
- **[Tools Documentation](../tools/README.md)** — Utility scripts
- **[Master Rules](../instructions/master_instruction_set.md)** — Non-negotiable standards
- **[Main README](../README.md)** — Project overview
- **[Autonomous Dev Guide](../AUTONOMOUS_DEVELOPER_README.md)** — Full-stack generation

---

**Last Updated:** June 3, 2026 | **Version:** 2.0.0 (Consolidated) | **Agents:** 13 | **Skills:** 22
