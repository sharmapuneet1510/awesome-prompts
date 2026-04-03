# Agents — Role-Based AI Assistant Definitions

This directory contains specialized AI agent definitions organized by **role and responsibility**.

## 📁 Directory Structure

```
agents/
├── developer/          ← Write code, implement features
├── reviewer/           ← Review code, inspect quality
├── writer/             ← Write documentation, comments
├── integration/        ← CI/CD, automation workflows
└── README.md           ← This file
```

---

## 👨‍💻 Developer Agents (Write Code)

**Location:** `agents/developer/`

Agents that generate code, implement features, and develop applications.

| Agent | File | Role | Technologies |
|-------|------|------|---------------|
| **Jarvis** | `java_advanced_agent.md` | Java/Spring Boot Developer | Java 17+, Spring Boot 3.x, JPA, Maven, Gradle |
| **Pyra** | `python_advanced_agent.md` | Python/FastAPI Developer | Python 3.11+, FastAPI, SQLAlchemy, asyncio |
| **Rexa** | `react_advanced_agent.md` | React/Frontend Developer | React 18+, TypeScript, TanStack Query, Zustand |
| **Sigma** | `mssql_advanced_agent.md` | SQL Server DBA | SQL Server 2019/2022, T-SQL, indexing |
| **Implementer** | `jira_implementation_agent.md` | Jira-driven Development | Task breakdown, implementation tracking |

**When to use:**
- Ask for new features: "Create a REST API endpoint for orders"
- Generate boilerplate: "Set up a new Spring Boot service"
- Write database migrations: "Add a table for customer preferences"
- Build components: "Create a React form with validation"

---

## 🔍 Reviewer Agents (Review & Inspect Code)

**Location:** `agents/reviewer/`

Agents that analyze code quality, identify issues, and provide recommendations.

| Agent | File | Role | Focus |
|-------|------|------|-------|
| **Sherlock** | `code_health_inspector_agent.md` | Code Health Inspector | Slowness, error handling, delays, security, reliability |
| **Code Reviewer** | `code_review_agent.md` | Code Reviewer | Design, patterns, best practices, architecture |
| **Git Reviewer** | `git-review-2.md` | Git/PR Reviewer | Commit history, PR structure, merge conflicts |

**When to use:**
- Ask for code review: "Review this service for performance issues"
- Health check: "Scan this code for potential bugs"
- Inspect PR: "Check this pull request for quality"
- Security audit: "Find vulnerabilities in this code"

---

## ✍️ Writer Agents (Documentation)

**Location:** `agents/writer/`

Agents that write documentation, comments, and explanations.

| Agent | File | Role | Focus |
|-------|------|------|-------|
| **Documentarian** | `jira_documentation_agent.md` | Technical Writer | API docs, requirements, design docs |

**When to use:**
- Generate docs: "Write API documentation for this endpoint"
- Add comments: "Add detailed comments to this method"
- Create guides: "Write a guide for using this library"

---

## 🔧 Integration Agents (CI/CD & Automation)

**Location:** `agents/integration/`

Agents for CI/CD pipelines, automation, and workflow orchestration.

| Agent | File | Role | Focus |
|-------|------|------|-------|
| **CI/CD Orchestrator** | `jira_mr_sync_review.agent.md` | Pipeline & Automation | Build, test, deploy workflows |

**When to use:**
- Set up CI/CD: "Create a GitHub Actions workflow"
- Automate testing: "Generate a test automation script"
- Deploy orchestration: "Write a deployment pipeline"

---

## 🎯 How to Use Each Agent

### Asking for Code (Developer)

```
"Use Jarvis to create a Spring Boot REST API for managing orders"
→ Jarvis generates code with:
  - Spring Boot 3.x patterns
  - Constructor injection
  - Proper DTOs and error handling
  - JUnit5 tests
  - Javadoc documentation
```

### Getting Code Review (Reviewer)

```
"Ask Sherlock to scan this service for performance issues"
→ Sherlock performs 6-phase scan:
  - Structure analysis
  - Performance detection (N+1, blocking calls)
  - Error handling gaps
  - Processing delays
  - Memory/security issues
  - Generates P0-P3 report with fixes
```

### Writing Documentation (Writer)

```
"Have the Documentarian write API documentation"
→ Generates:
  - Endpoint descriptions
  - Request/response examples
  - Error codes
  - Usage guides
```

---

## 📋 Agent Capabilities

### What Each Agent Type Does

**Developers:**
- ✅ Write production-ready code
- ✅ Follow language best practices
- ✅ Generate unit tests
- ✅ Add comprehensive documentation
- ✅ Implement design patterns

**Reviewers:**
- ✅ Identify performance bottlenecks
- ✅ Find error handling gaps
- ✅ Spot security vulnerabilities
- ✅ Suggest architectural improvements
- ✅ Generate actionable reports

**Writers:**
- ✅ Generate API documentation
- ✅ Write inline comments
- ✅ Create user guides
- ✅ Document design decisions
- ✅ Explain complex code

**Integration:**
- ✅ Create CI/CD pipelines
- ✅ Automate testing
- ✅ Orchestrate deployments
- ✅ Set up monitoring

---

## 🔗 Relationship to Skills

All agents use **skills** from the `skills/` directory:

- `skills/java_advanced_skill.md` → Used by Jarvis
- `skills/python_advanced_skill.md` → Used by Pyra
- `skills/react_advanced_skill.md` → Used by Rexa
- `skills/mssql_advanced_skill.md` → Used by Sigma
- `skills/error_handling_skill.md` → Used by all developers
- `skills/testing_junit5_skill.md` → Used by Jarvis tests
- `skills/testing_pytest_skill.md` → Used by Pyra tests
- `skills/rest_api_java_skill.md` → Used by Jarvis
- `skills/code_formatting_skill.md` → Used by all
- `skills/documentation_skill.md` → Used by Writers
- `skills/sonarqube_vulnerability_skill.md` → Used by Sherlock

---

## 💡 Tips

1. **Be Specific** — Tell the agent exactly what you need: "Create a FastAPI endpoint" not just "Write code"
2. **Provide Context** — Share existing code or requirements for better results
3. **Stack Reviewers** — Use Sherlock first for health, then Code Reviewer for design
4. **Chain Workflows** — Use Developer → Reviewer → Writer pipeline
5. **Check Skills** — Read the corresponding skill files to understand what the agent knows

---

## 📚 Related Documentation

- **[CLAUDE.md](../CLAUDE.md)** — Project overview and structure
- **[instructions/](../instructions/)** — Universal rules all agents follow
- **[skills/](../skills/)** — Knowledge modules used by agents
- **[prompts/](../prompts/)** — Reusable prompt templates

---

**Last Updated:** 2026-04-03
**Version:** 2.0
