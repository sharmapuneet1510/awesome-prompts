# 🤖 AI Agents Directory

> Complete guide to all AI agents in the Awesome Prompts system

**Quick Navigation**
| Agent | Purpose | Version | Status |
|-------|---------|---------|--------|
| [Implementation](implementation_agent.md) | Feature builder | v3.0 | ✅ Ready |
| [Code Review](code_review_agent.md) | Requirement validation | v3.0 | ✅ Ready |
| [Test Generator](test_case_generator_agent.md) | 100% coverage tests | v1.0 | ✅ Ready |
| [Writer](writer_agent.md) | Auto-documentation | v1.0 | ✅ Ready |
| [Integration](integration_agent.md) | CI/CD automation | v1.0 | ✅ Ready |
| [Autonomous Dev](autonomous/autonomous_dev_agent.md) | Full-stack | v1.0 | ✅ Ready |
| [Tech Docs](technical_documentation_agent.md) | Architecture docs | v1.0 | ✅ Ready |
| [Architecture Refactorer](architecture_refactorer_agent.md) | Code restructuring | v1.0 | ✅ NEW |

---

## 🎯 Agent Overview

### Architecture Pattern

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

## 🏗️ Architecture Refactorer Agent (v1.0) ⭐ NEW

**File:** [`architecture_refactorer_agent.md`](architecture_refactorer_agent.md)

| Aspect | Details |
|--------|---------|
| **Purpose** | Restructure messy production codebase |
| **Input** | Existing code, architectural pain points |
| **Analysis** | 8-phase (assessment → diagnosis → design → refactoring → migration) |
| **Output** | Clean layered architecture + refactored code + migration guide |
| **Key Pattern** | Domain-Driven Design (DDD) with clean architecture layers |

**Features:**
- 🔍 Architectural problem diagnosis (coupling, god modules, circular deps)
- 🎯 Clean architecture design (presentation → application → domain ← infrastructure)
- 📊 Phased refactoring roadmap (3-5 incremental, deployable phases)
- 💻 Production code examples (before/after transformations)
- 🛡️ Zero-downtime migration strategy (feature flags, rollback procedures)
- ✅ 100% backward compatibility (no functionality changes)

**When to use:** Untangling tight coupling, fixing god classes, improving testability, scaling blockers

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

## 📚 Writer Agent (v1.0)

**File:** [`writer_agent.md`](writer_agent.md)

**Purpose:** Auto-generate documentation

**Generates:**
- JSDoc (JavaScript/TypeScript)
- docstrings (Python)
- Javadoc (Java)
- README updates
- Changelog entries
- API documentation

**When to use:** Need documentation, README updates, API docs

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

## 📊 Technical Documentation Agent (v1.0)

**File:** [`technical_documentation_agent.md`](technical_documentation_agent.md)

**Purpose:** Auto-generate project documentation

**Generates:**
- `architecture.md` — System design with Mermaid diagrams
- `tech-stack.md` — Technology reference table
- `context.json` — Machine-readable metadata
- `design.html` — Interactive visualization

**When to use:** Need architecture docs, project documentation, knowledge graphs

---

## 📋 Agent Decision Matrix

| Need | Agent | Time |
|------|-------|------|
| Build a feature | Implementation | 5-10 min |
| Review a PR | Code Review | 2-5 min |
| Generate tests | Test Generator | 3-7 min |
| Document code | Writer | 2-4 min |
| Setup CI/CD | Integration | 10-15 min |
| Full system | Autonomous Dev | 20-30 min |
| Architecture docs | Tech Docs | 5-10 min |
| Refactor messy code | Architecture Refactorer | 30-120 min |

---

## 🔗 Links

- **[Skills Directory](../skills/README.md)** — Reusable skill modules
- **[Tools Documentation](../tools/README.md)** — Utility scripts
- **[Master Rules](../instructions/master_instruction_set.md)** — Non-negotiable standards
- **[Main README](../README.md)** — Project overview
- **[Autonomous Dev Guide](../AUTONOMOUS_DEVELOPER_README.md)** — Full-stack generation

---

**Last Updated:** May 27, 2026 | **Version:** 4.3.0
