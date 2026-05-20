# Agents — Role-Based AI Assistant Definitions

This directory contains **simplified, role-based AI agents** that focus on workflow and use **skills** for implementation details.

---

## 🎯 Core Principle

**Agents = Roles + Workflows**  
**Skills = Tech-Specific Implementation Details**

Instead of separate agents for Java, Python, React developers, we have **ONE implementation agent** that:
1. Takes your requirement
2. Detects your tech stack
3. Builds complete feature: code + tests + documentation

This eliminates duplication and ensures every feature is fully delivered.

---

## 📁 Directory Structure

```
agents/
├── implementation_agent.md               ← Build features end-to-end (any tech)
├── code_review_agent.md                 ← Review code (any tech)
├── writer_agent.md                      ← Write documentation (JSDoc/docstrings)
├── integration_agent.md                 ← CI/CD & automation
├── technical_documentation_agent.md     ← Generate project technical docs
├── context/
│   └── context_builder_agent.md         ← Build architecture context
├── autonomous/
│   └── autonomous_dev_agent.md          ← Orchestrate full projects
└── README.md
```

---

## 🚀 The 6 Agents

### 1️⃣ Implementation Agent

**File:** `implementation_agent.md`

**What it does:** Complete end-to-end feature implementation. Takes requirement → Creates code → Tests → Documents → Commits

**Full Lifecycle:**
1. Gathers requirement (free text, JIRA, file, or auto-detect)
2. Detects tech stack (auto or from project)
3. Plans implementation
4. Generates production-ready code
5. Creates comprehensive tests (≥95% coverage)
6. Auto-generates documentation
7. Commits with clear messages

**When to use:**
- Building new features with complete delivery
- Need code + tests + documentation together
- Want auto-updated project context
- Requirements in free text, JIRA, or files
- Rapid feature implementation

**Example:**
```
User: "Implement user registration with email validation"

Agent:
1. Gathers requirement
2. Detects: Python + FastAPI
3. Plans: Models, Routes, Email Service
4. Creates: Routes, Pydantic schemas, email sending
5. Tests: pytest with ≥95% coverage
6. Docs: Auto-generated docstrings
7. Commits: Feature branch + commit
```

---

### 2️⃣ Code Review Agent

**File:** `code_review_agent.md`

**What it does:** Analyzes code for design quality, SOLID principles, performance, security, and maintainability (tech-agnostic)

**Review checklist:**
- Structure & design
- SOLID principles
- Design patterns
- Performance (N+1 queries, inefficient algorithms)
- Security (SQL injection, validation, secrets)
- Testing & documentation

**When to use:**
- Code quality review
- Design feedback
- Performance optimization
- Security audit
- SOLID principles enforcement

**Example:**
```
User: "Review this Python function for design quality"

Agent: Returns detailed report:
- P0: SQL injection vulnerability
- P1: N+1 query problem
- P2: SRP violation (too many responsibilities)
- P3: Missing error handling
```

---

### 3️⃣ Writer Agent

**File:** `writer_agent.md`

**What it does:** Generates Javadoc, docstrings, JSDoc, README files, architecture docs, API specifications

**Supports:**
- Javadoc (Java)
- Google-style docstrings (Python)
- JSDoc (TypeScript/JavaScript)
- Architecture documentation
- README files with quick start

**When to use:**
- Add documentation to code
- Generate API docs
- Write architecture documentation
- Create README and quick start guides
- Explain complex code with comments

**Example:**
```
User: "Generate Javadoc for this Java service"

Agent: Adds:
- Javadoc with @param, @return, @throws
- Usage examples
- Related methods
- Performance notes
```

---

### 4️⃣ Integration Agent

**File:** `integration_agent.md`

**What it does:** Builds CI/CD pipelines, automates testing, deployments, and infrastructure

**Supports:**
- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI
- Docker & Kubernetes
- Terraform / CloudFormation
- Monitoring & alerting

**When to use:**
- Set up CI/CD pipelines
- Automate testing and deployments
- Create Infrastructure as Code
- Build monitoring and alerting
- Orchestrate releases

**Example:**
```
User: "Create a GitHub Actions workflow that runs tests and deploys"

Agent: Generates:
- Run tests on every PR
- Build Docker image on main
- Deploy to AWS ECS
- Health checks and rollbacks
```

---

### 5️⃣ Technical Documentation Agent

**File:** `technical_documentation_agent.md`

**What it does:** Generates comprehensive technical documentation by analyzing your project

**Documentation includes:**
- Code workflows and request/response cycles
- Database schema and relationships
- Middleware and integration documentation
- Dependency analysis (from package.json, pom.xml, requirements.txt, etc.)
- API endpoint reference
- Deployment guides
- Interactive HTML visualization
- Markdown files for all aspects

**When to use:**
- Onboarding new team members
- Documenting existing projects
- Creating architecture diagrams
- Before major refactors
- Building knowledge base
- Preparing for external audits

**Example:**
```
User: "Generate complete technical documentation for this project"

Agent: Creates:
- Interactive HTML with architecture diagrams
- 10 markdown files covering all aspects
- Tech stack analysis
- Code workflow diagrams
- Database schema documentation
- Middleware documentation
- Deployment guide
```

---

### 6️⃣ Autonomous Developer Agent

**Location:** `autonomous/autonomous_dev_agent.md`

**What it does:** Orchestrates **end-to-end code generation** from plain-text requirements

**5-phase pipeline:**
1. Database schema + migrations
2. Backend API (REST, GraphQL)
3. Frontend UI (React components)
4. Comprehensive tests (unit, integration, E2E)
5. Deployment configuration

**When to use:**
- Building complete projects from requirements
- Rapid prototyping
- Full-stack development
- Want everything at once (DB + backend + frontend + tests)

**Example:**
```
User: "Generate a complete auth system"

Agent: Creates:
- PostgreSQL schema with migrations
- FastAPI backend with JWT
- React login/register UI
- pytest + Jest tests (95% coverage)
- GitHub PR with all code
```

---

## 🔗 Agents + Skills Architecture

### How It Works

```
User Request
    ↓
Agent (role-based workflow)
    ↓
Detect tech stack
    ↓
Load appropriate skill
    ↓
Load master instruction set
    ↓
Generate code/docs
```

### Skill Mapping

| Tech Stack | Skill | Used By |
|-----------|-------|---------|
| **Java** | `java_advanced_skill.md` | implementation_agent |
| **Python** | `python_advanced_skill.md` | implementation_agent |
| **React/TypeScript** | `react_advanced_skill.md` | implementation_agent |
| **SQL Server** | `mssql_advanced_skill.md` | implementation_agent |
| **Code Review** | `code_health_skill.md` | code_review_agent |
| **All Agents** | `master_instruction_set.md` | (universal) |

---

## 💡 Benefits of Simplified Architecture

### Before (Old: Tech-Specific Agents)
```
Developer Agents:
- java_advanced_agent.md (15 KB)
- python_advanced_agent.md (14 KB)
- react_advanced_agent.md (12 KB)
- mssql_advanced_agent.md (19 KB)

Problem: 90% duplicate code, maintenance nightmare
```

### After (New: Role-Based Agents)
```
Implementation Agent: (8 KB)
- Gathers requirements
- Detects tech stack
- Full lifecycle: code + tests + docs
- 1 agent, infinite tech stacks

Result: DRY, complete delivery, maintainable
```

---

## 🎓 How to Use

### 1. Direct Invocation (Claude Code, Copilot)

```bash
# Implementation agent (any tech, complete feature)
"Implement user registration with email validation"
"Build a Spring Boot order API endpoint with tests"
"Create a React dashboard with data fetching"

# Code Review agent
"Review this code for design issues"
"Check this for performance problems"

# Writer agent
"Generate Javadoc for this service"
"Write API documentation"

# Integration agent
"Create a GitHub Actions CI/CD pipeline"
"Build a Docker + Kubernetes setup"

# Autonomous agent
"Generate a complete e-commerce system from requirements"
```

### 2. Chaining Workflows

```
Step 1: Use Implementation Agent
→ "Implement user registration with email verification"
→ Returns: Code + tests + docs + commit

Step 2: Use Code Review Agent (if needed)
→ "Review the generated code for quality"
→ Returns: Issues and recommendations

Step 3: Use Writer Agent (for additional docs)
→ "Generate API documentation from comments"
→ Returns: OpenAPI spec, Swagger UI

Step 4: Use Integration Agent
→ "Create a CI/CD pipeline for deployment"
→ Returns: GitHub Actions workflow
```

---

## 🔄 Migration from Old Agents

**Old way (tech-specific agents):**
```
"Use Jarvis to build a Java service"
→ Loads java_advanced_agent.md (15 KB, duplicate code)
→ Returns only code, no tests/docs
```

**New way (role-based with full lifecycle):**
```
"Implement user registration in Java"
→ Implementation Agent (8 KB)
→ Detects Java + Spring Boot
→ Returns: Code + tests + docs + commit
→ Includes context generation
```

Old agents are archived in `_deprecated/` for reference but not exported.

---

## 📚 Related Documentation

- **[../CLAUDE.md](../CLAUDE.md)** — Project overview
- **[../skills/](../skills/)** — Tech-specific skills (Java, Python, React, etc.)
- **[../instructions/](../instructions/)** — Universal rules all agents follow
- **[../README.md](../README.md)** — Main project README

---

## ⚡ Quick Reference

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| **Implementation** | Build features end-to-end | "Implement X feature" | Code + tests + docs + context + commit |
| **Code Review** | Inspect quality | "Review this code" | Issues + severity + fixes |
| **Writer** | Document code | "Write docs for this" | Javadoc/docstrings/README/API specs |
| **Technical Documentation** | Generate project docs | "Document this project" | HTML + Markdown docs + diagrams |
| **Integration** | CI/CD & DevOps | "Create pipeline for X" | CI/CD workflow + IaC + monitoring |
| **Autonomous** | Full projects | "Build Y from Z requirements" | Complete system (DB + backend + frontend + tests) |

---

**Version:** 3.0 (Simplified Role-Based Architecture)  
**Last Updated:** 2026-05-20
