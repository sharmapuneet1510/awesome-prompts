# Agents — Role-Based AI Assistant Definitions

This directory contains **simplified, role-based AI agents** that focus on workflow and use **skills** for implementation details.

---

## 🎯 Core Principle

**Agents = Roles + Workflows**  
**Skills = Tech-Specific Implementation Details**

Instead of separate agents for Java, Python, React developers, we have **ONE developer agent** that:
1. Detects your tech stack
2. Loads the appropriate skill
3. Applies best practices for that tech

This eliminates duplication and makes skills reusable.

---

## 📁 Directory Structure

```
agents/
├── developer_agent.md           ← Write code (any tech)
├── code_review_agent.md         ← Review code (any tech)
├── writer_agent.md              ← Write documentation
├── integration_agent.md          ← CI/CD & automation
├── autonomous/
│   └── autonomous_dev_agent.md  ← End-to-end generation
├── developer/
│   └── jira_implementation_agent.md  ← Task breakdown
├── _deprecated/                 ← Old agents (archived)
│   ├── java_advanced_agent.md
│   ├── python_advanced_agent.md
│   ├── react_advanced_agent.md
│   └── ... (9 old tech-specific agents)
└── README.md
```

---

## 🚀 The 5 Agents

### 1️⃣ Developer Agent

**File:** `developer_agent.md`

**What it does:** Writes production-ready code in any tech stack (Java, Python, React, TypeScript, SQL, etc.)

**How it works:**
1. You tell it your tech stack (or it detects from files)
2. It loads the appropriate skill (java_advanced_skill, python_advanced_skill, etc.)
3. It applies that skill's best practices to generate code

**When to use:**
- Building new features
- Writing backend services
- Creating frontend components
- Writing database queries
- Implementing business logic

**Example:**
```
User: "Build a Spring Boot REST API for orders"

Agent:
1. Detects: Java + Spring Boot
2. Loads: java_advanced_skill.md
3. Generates: Controller, Service, JPA Entity, JUnit5 tests, Javadoc
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

### 5️⃣ Autonomous Developer Agent

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
| **Java** | `java_advanced_skill.md` | developer_agent |
| **Python** | `python_advanced_skill.md` | developer_agent |
| **React/TypeScript** | `react_advanced_skill.md` | developer_agent |
| **SQL Server** | `mssql_advanced_skill.md` | developer_agent |
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
Developer Agent: (6 KB)
- Detects tech stack
- References appropriate skill
- 1 agent, infinite tech stacks

Result: DRY, maintainable, scalable
```

---

## 🎓 How to Use

### 1. Direct Invocation (Claude Code, Copilot)

```bash
# Developer agent (any tech)
"Build a Spring Boot REST API for users"
"Create a FastAPI async endpoint"
"Write a React login form"

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
Step 1: Use Developer Agent
→ "Build a user authentication service"

Step 2: Use Code Review Agent  
→ "Review the generated code for quality"

Step 3: Use Writer Agent
→ "Add Javadoc to the reviewed code"

Step 4: Use Integration Agent
→ "Create a CI/CD pipeline for deployment"
```

---

## 🔄 Migration from Old Agents

**Old way (tech-specific):**
```
"Use Jarvis to build a Java service"
→ Loads java_advanced_agent.md
```

**New way (generic):**
```
"Build a Java service"
→ Developer agent detects Java
→ Loads java_advanced_skill.md
→ Same result, less duplication
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
| **Developer** | Write code | "Build X in Y tech" | Code + tests + docs |
| **Code Review** | Inspect quality | "Review this code" | Issues + fixes |
| **Writer** | Document | "Write docs for this" | Javadoc/docstrings/README |
| **Integration** | CI/CD & DevOps | "Create pipeline for X" | CI/CD config + IaC |
| **Autonomous** | Full projects | "Build Y from Z requirements" | Complete project |

---

**Version:** 3.0 (Simplified Role-Based Architecture)  
**Last Updated:** 2026-05-20
