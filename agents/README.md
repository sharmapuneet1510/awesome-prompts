# 🤖 AI Agents Directory (v2.0 — Consolidated with Function Dispatch)

> Role-based AI agents using reusable skills. 13 agents, 22 skills, zero overlap.  
> **New:** Use `agent_name:function` syntax to call specific agent workflows (see [AGENTS_FUNCTIONS.md](../AGENTS_FUNCTIONS.md))

## Quick Navigation (13 Agents)

| # | Agent | Role | Purpose | Version | Status |
|---|-------|------|---------|---------|--------|
| 1 | [Autonomous Dev](autonomous/autonomous_dev_agent.md) | Orchestrator | Full-stack project generation (DB + API + UI + tests) | v1.0 | ✅ Ready |
| 2 | [Implementation Engineer](implementation_agent.md) | Feature Builder | Code + tests + docs for single features or modules | v3.0 | ✅ Ready |
| 3 | [Systems Architect](architecture_agent.md) | Architecture | Design new systems or refactor existing ones (greenfield + brownfield) | v2.0 | ✅ Ready |
| 4 | [Code Reviewer](code_review_agent.md) | QA | PR validation against JIRA requirements, quality scoring | v3.0 | ✅ Ready |
| 5 | [Test Engineer](test_case_generator_agent.md) | Testing | 100% coverage tests with business validation | v1.0 | ✅ Ready |
| 6 | [Security Auditor](security_auditor_agent.md) | Security | Vulnerability scanning, threat modeling, OWASP compliance | v1.0 | ✅ Ready |
| 7 | [Performance Optimizer](performance_optimizer_agent.md) | Performance | Bottleneck analysis, optimization strategies, benchmarking | v1.0 | ✅ Ready |
| 8 | [Production Debugger](production_debugger_agent.md) | Debugging | Root cause analysis, stack trace investigation, edge cases | v1.0 | ✅ Ready |
| 9 | [Codebase Auditor](codebase_auditor_agent.md) | Code Health | Scan for violations, tech debt, security issues, roadmaps | v1.0 | ✅ Ready |
| 10 | [DevOps Engineer](integration_agent.md) | Deployment | CI/CD pipelines, containerization (Docker), IaC (Terraform), monitoring | v1.0 | ✅ Ready |
| 11 | [Documentation Engineer](documentation_agent.md) | Documentation | Code docs (Javadoc/docstrings), architecture guides, API specs, HTML sites | v2.0 | ✅ Ready |
| 12 | [Technical Lead](technical_lead_agent.md) | Strategy | Architecture reviews, tech decisions, team coordination | v1.0 | ✅ Ready |
| 13 | [Business Analyst](business_analyst_agent.md) | Backlog | JIRA parsing, HTML backlog reports, filtering, stats | v1.0 | ✅ Ready |

---

## 🎯 Function Dispatch Syntax (v2.0 NEW)

**Call specific agent functions** instead of full workflows:

```
agent_name:function [path=...] [option=value]

Examples:
  documentation:context path=./my-project         → Build project context only
  documentation:code path=./src                   → Generate code docs only
  architecture:design requirements="e-commerce"  → Design new system
  ba:report file=jira-export.json                 → Parse JIRA → HTML backlog
  implementation:build requirement="..."         → Build code only
  security:audit path=./src                      → Full security audit
  test:generate files=src/**                      → Generate tests only
  autonomous:build file=requirements.txt         → Full-stack generation
```

**See [AGENTS_FUNCTIONS.md](../AGENTS_FUNCTIONS.md) for all 54 callable functions with inputs, outputs, and examples.**

---

## 🎯 Agent Organization (Role-Based)

**Consolidated Structure (v2.0):**
- **19 agents → 13 agents** (removed 7 overlapping agents)
- **34 skills → 22 skills** (removed 12 orphaned skills)
- **Zero role overlap** (each agent has a single, clear responsibility)
- **54 callable functions** (agent:function dispatch for targeted workflows)

### Removed in Consolidation

**Overlapping Agents Merged:**
- ❌ `ai_engineering_team_coordinator_agent` → Merged into `autonomous_dev_agent` (orchestration)
- ❌ `super_agent_orchestrator` → Merged into `autonomous_dev_agent` (orchestration)
- ❌ `context_builder_agent` → Wrapper; logic in `context_builder_skill`
- ❌ `writer_agent` → Merged into `documentation_agent`
- ❌ `technical_documentation_agent` → Merged into `documentation_agent`
- ❌ `backend_systems_architect_agent` → Merged into `architecture_agent`
- ❌ `architecture_refactorer_agent` → Merged into `architecture_agent`

**Orphaned Skills Removed:**
- ❌ `documentation_skill` (duplicate of `code_documentation_skill`)
- ❌ `java11_skill`, `java17_skill` (subsumed by `java_advanced_skill`)
- ❌ `rest_api_java_skill`, `rest_api_python_skill` (subsumed by `backend_skill`)
- ❌ `testing_junit5_skill`, `testing_pytest_skill`, `testing_react_skill` (subsumed by `test_skill`)
- ❌ `camel_exception_handling_skill`, `camel_pulsar_integration_skill`, `spring_camel_integration_skill` (consolidated into `apache_camel_skill`)
- ❌ `sonarqube_vulnerability_skill` (consolidated into `code_health_skill`)

---

## 🎯 Architecture Pattern

```
User Requirement
    ↓
Orchestration Layer (Agent)
    ├─ Parse requirement
    ├─ Detect tech stack
    ├─ Apply skill
    └─ Generate + test + document
    ↓
Skill Layer (Reusable)
    ├─ Code Documentation
    ├─ Database
    ├─ Backend API
    ├─ Frontend
    ├─ Testing
    └─ [etc.]
    ↓
Output (Production-Ready)
    ├─ Code
    ├─ Tests (100% coverage)
    ├─ Documentation
    └─ GitHub PR
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
