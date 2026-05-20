# Awesome Prompts — Enterprise-Grade AI Coding Assistant Repository

A comprehensive, production-ready collection of **AI agent definitions**, **coding skills**, and **prompt templates** for software engineering workflows. Compatible with GitHub Copilot, Claude, Cursor, Windsurf, Gemini CLI, Continue.dev, OpenAI API, and Aider.

**Version:** 4.0.0 | **Status:** ✅ Production Ready | 30 Skills | 9 Agents | 8 Platform Exports | 🤖 Autonomous Code Generation

---

## 🎯 What This Is

This repository provides **shareable, git-friendly instructions** for AI coding assistants. Instead of starting from scratch, your AI assistant applies proven patterns for:

- ✅ **REST API design** (Java, Python)
- ✅ **Error handling** (retry logic, circuit breaker)
- ✅ **Testing** (JUnit5, pytest, React Testing Library)
- ✅ **Code quality** (SonarQube, security, formatting)
- ✅ **Documentation** (Javadoc, docstrings, JSDoc)
- ✅ **Architecture patterns** (Spring, FastAPI, Camel, Pulsar)

**Agents are role-based:**
- 👨‍💻 **Developer** — Generate code
- 🔍 **Reviewer** — Inspect quality
- ✍️ **Writer** — Write docs
- 🔧 **Integration** — Automate CI/CD
- 🤖 **Autonomous Developer** — End-to-end code generation

---

## 🤖 NEW: Autonomous Developer System

The **Autonomous Developer Agent** reads plain-text requirements and generates production-ready code end-to-end:

```
Input: requirement.txt
├─ Parse requirements → Detect project type
├─ Generate database schema + migrations
├─ Build backend API (REST, GraphQL, services)
├─ Create frontend UI (React components)
├─ Write comprehensive tests (pytest, Jest, E2E)
└─ Output: Full GitHub PR with production code
```

**Features:**
- 🚀 Fully autonomous 5-phase code generation
- 📊 Intelligent project detection (new vs existing)
- 🧪 Test-driven development (TDD) for all phases
- 📈 Task completion tracking (JSON format)
- 🧠 Knowledge graph integration (graphify)
- 🔄 GitHub PR creation with auto-sync
- 📚 Auto-updating documentation

**Quick Start:**
```bash
# Interactive setup (recommended)
python3 tools/exporter.py --interactive

# Or direct: export autonomous developer system
python3 tools/exporter.py --target claude --all

# Then in Claude Code: /autonomous-developer
```

See **[AUTONOMOUS_DEVELOPER_README.md](AUTONOMOUS_DEVELOPER_README.md)** and **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for complete documentation.

---

## 📦 What's Included

### Skills (30 total)

**Autonomous Development (NEW):**
- `database_skill.md` — SQL schema generation with migrations
- `backend_skill.md` — API generation (FastAPI, Spring Boot)
- `frontend_skill.md` — React component generation with TypeScript
- `test_skill.md` — Comprehensive testing (pytest, Jest, Playwright, E2E)

**API & Backend:**
- `rest_api_java_skill.md` — Spring Boot REST patterns
- `rest_api_python_skill.md` — FastAPI patterns
- `spring_advanced_skill.md` — Spring Framework internals
- `spring_camel_integration_skill.md` — Spring + Camel integration
- `apache_camel_skill.md` — Integration & EIP routing
- `camel_exception_handling_skill.md` — Camel error routes
- `camel_pulsar_integration_skill.md` — Camel + Pulsar integration
- `apache_pulsar_skill.md` — Messaging & streaming

**Language Standards:**
- `java_advanced_skill.md` — Java 17+ patterns
- `java17_skill.md` — Java 17 modern features
- `java11_skill.md` — Java 11 LTS features
- `python_advanced_skill.md` — Python 3.11+ patterns
- `react_advanced_skill.md` — React 18+ / TypeScript patterns
- `mssql_advanced_skill.md` — T-SQL & indexing
- `oop_skill.md` — OOP principles & patterns
- `lombok_skill.md` — Project Lombok

**Testing & Quality:**
- `testing_junit5_skill.md` — JUnit5 with Mockito
- `testing_pytest_skill.md` — pytest with fixtures
- `testing_react_skill.md` — React Testing Library
- `code_health_skill.md` — Quality inspection taxonomy
- `sonarqube_vulnerability_skill.md` — Security & OWASP Top 10

**Code Standards:**
- `error_handling_skill.md` — Exception patterns
- `code_formatting_skill.md` — Formatting standards
- `documentation_skill.md` — Javadoc/docstrings/JSDoc
- `logger_skill.md` — Logging best practices
- `opentelemetry_skill.md` — Distributed tracing & observability

### Agents (9 total, organized by role)

**Autonomous Developer** (NEW)
- `autonomous_dev_agent.md` — 🤖 Autonomous code generation end-to-end

**Developer Agents** (`agents/developer/`)
- `java_advanced_agent.md` — Jarvis (Java 17+ / Spring Boot)
- `python_advanced_agent.md` — Pyra (Python 3.11+ / FastAPI)
- `react_advanced_agent.md` — Rexa (React 18+ / TypeScript)
- `mssql_advanced_agent.md` — Sigma (SQL Server DBA)
- `jira_implementation_agent.md` — Task breakdown & tracking

**Reviewer Agents** (`agents/reviewer/`)
- `code_health_inspector_agent.md` — Sherlock (6-phase code scan)
- `code_review_agent.md` — Pattern & design review

**Writer Agents** (`agents/writer/`)
- `jira_documentation_agent.md` — Technical documentation

**Integration Agents** (`agents/integration/`)
- `jira_mr_sync_review.agent.md` — CI/CD pipeline orchestration

### Instructions (3 files)

- `instructions/master_instruction_set.md` — Universal rules all agents follow
- `instructions/java_project_intake.md` — 33-question Java/Spring intake form
- `instructions/python_project_intake.md` — Python project setup guide

---

## 🚀 Quick Start

### 1. Export to Your Platform

```bash
# Export all 26 skills + 8 agents to all 8 platforms
python3 tools/exporter.py

# Specific platforms only
python3 tools/exporter.py --target copilot claude cursor

# Filter by skill/agent
python3 tools/exporter.py --skills java,spring --agents developer

# Preview without writing
python3 tools/exporter.py --dry-run

# List everything discovered
python3 tools/exporter.py --list
```

### 2. Platform Output Locations

| Platform | Skills | Agents |
|----------|--------|--------|
| GitHub Copilot | `.github/instructions/<slug>.instructions.md` | `.github/copilot/agents/<slug>.md` |
| Claude Code | `.claude/skills/<slug>.md` | `.claude/agents/<slug>.md` |
| Cursor IDE | `.cursor/rules/<slug>.mdc` | `.cursor/rules/agents/<slug>.mdc` |
| Windsurf | `.windsurf/rules/<slug>.md` | `.windsurf/rules/agents/<slug>.md` |
| Gemini CLI | `.gemini/skills/<slug>.md` | `.gemini/agents/<slug>.md` |
| Continue.dev | `.continue/prompts/<slug>.prompt` | `.continue/prompts/agents/<slug>.prompt` |
| OpenAI API | `tools/output/openai/skills/<slug>.txt` | `tools/output/openai/agents/<slug>.txt` |
| Aider | `.aider/skills/<slug>.md` | `.aider/agents/<slug>.md` |

### 3. Ask for Code

```
"Use Jarvis to create a Spring Boot REST API for orders with proper error handling"
→ Generates: Spring Boot 3.x controller, service, JPA entities, JUnit5 tests, Javadoc
```

---

## 📁 Directory Structure

```
awesome-prompts/
├── agents/                           ← AI agents organized by role
│   ├── autonomous/                   ← 🤖 autonomous_dev_agent (end-to-end generation)
│   ├── developer/                    ← Jarvis, Pyra, Rexa, Sigma
│   ├── reviewer/                     ← Sherlock, Code Reviewer
│   ├── writer/                       ← Documentarian
│   ├── integration/                  ← CI/CD Orchestrator
│   └── README.md
│
├── skills/                           ← Reusable knowledge modules (26 total)
│
├── instructions/                     ← Universal rules & intake forms
│   ├── master_instruction_set.md
│   ├── java_project_intake.md
│   └── python_project_intake.md
│
├── prompts/                          ← Reusable prompt templates
│   ├── code-review/
│   ├── testing/
│   ├── codebase-analysis/
│   ├── project-management/
│   ├── incident-management/
│   └── email/
│
├── tools/                            ← Python utilities
│   ├── exporter.py                   ← Export to 8 platforms (v3.0)
│   ├── skill_validator.py            ← Validate skill frontmatter
│   ├── fix_code_blocks.py            ← Fix markdown code blocks
│   └── README.md
│
├── tests/                            ← Test suite for tools
│   └── tools/
│       └── test_exporter.py          ← 79 tests, all passing
│
├── CLAUDE.md                         ← Claude Code instructions
├── .gitignore
└── README.md
```

---

## 🎓 Agent Usage Examples

### Jarvis (Java Developer)

```
"Create a Spring Boot service that processes orders asynchronously"
✓ Spring Boot 3.x REST controller + service layer
✓ JPA/Hibernate entities, constructor injection
✓ @Valid request validation, global error handler
✓ JUnit5 + Mockito tests, full Javadoc
```

### Sherlock (Code Inspector)

```
"Scan this service for performance issues"
✓ 6-phase analysis: structure → performance → errors → delays → memory → security
✓ N+1 queries, blocking calls, swallowed exceptions
✓ P0–P3 severity report with fix examples
```

### Pyra (Python Developer)

```
"Build a FastAPI endpoint with async database access"
✓ FastAPI + Pydantic schemas, async SQLAlchemy
✓ Dependency injection, custom exceptions
✓ pytest fixtures, type hints, Google-style docstrings
```

---

## 📚 Detailed Skill & Agent Guide

### 🤖 Autonomous Developer System

#### autonomous_dev_agent.md
**What it does:** End-to-end code generation orchestrator. Reads plain-text requirements and automatically generates production-ready code across 5 phases: database schema, backend API, frontend UI, tests, and deployment.

**When to use it:**
- Building new projects from requirements
- Rapid prototyping with database + backend + frontend
- Need complete project with tests and GitHub PR
- Want test-driven development (TDD) throughout

**How to use it:**
```bash
# 1. Interactive setup
python3 tools/exporter.py --interactive

# 2. Create requirements file
cat > requirement.txt << 'EOF'
We need a user authentication system.
Use React 18+ for frontend, Python FastAPI for backend, PostgreSQL for database.
Features: User registration, login with JWT, profile management.
Timeline: 2 weeks
EOF

# 3. In Claude Code, invoke agent
/autonomous-developer

# 4. Monitor progress
cat task-completion.json | jq '.summary'
```

See **[AUTONOMOUS_DEVELOPER_README.md](AUTONOMOUS_DEVELOPER_README.md)** and **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for complete documentation.

---

#### database_skill.md
**What it does:** Generates SQL database schemas with proper indexing, constraints, and migrations. Supports PostgreSQL, MySQL, and SQL Server.

**When to use it:**
- Need schema for new database
- Creating migrations for schema changes
- Want proper indexes and constraints
- Need to convert requirements to DDL

**How to use it:**
```
Invoke with autonomous agent or directly:
"Generate a PostgreSQL schema for a user authentication system with email validation and JWT token storage"
→ Outputs: schema.sql, migration files, indexes, constraints
```

---

#### backend_skill.md
**What it does:** Generates REST API routes, models, services, and error handling for FastAPI (Python) or Spring Boot (Java).

**When to use it:**
- Building backend API from requirements
- Need CRUD endpoints with validation
- Want service layer + repository pattern
- Need error handling and logging

**How to use it:**
```
"Create FastAPI endpoints for user registration and login with JWT token handling"
→ Outputs: routes.py, models.py, services.py, JWT middleware, input validation
```

---

#### frontend_skill.md
**What it does:** Generates React components with TypeScript, hooks, form validation, and responsive design using Tailwind CSS.

**When to use it:**
- Building React UI from requirements
- Need form components (login, registration, profiles)
- Want proper accessibility and responsive design
- Need type-safe React with TypeScript

**How to use it:**
```
"Create a login form component with email/password validation and error handling"
→ Outputs: LoginForm.tsx, useAuth hook, styled components, accessibility attributes
```

---

#### test_skill.md
**What it does:** Generates comprehensive test suites including unit tests (pytest for Python), component tests (Jest for React), and E2E tests (Playwright).

**When to use it:**
- Need tests for generated code
- Want ≥95% code coverage
- Need unit + integration + E2E tests
- Want test data factories and fixtures

**How to use it:**
```
"Generate tests for the user authentication endpoints with coverage report"
→ Outputs: test_auth.py (pytest), test_auth.tsx (Jest), e2e_auth.spec.ts (Playwright)
```

---

### 👨‍💻 Developer Agents

#### Jarvis (java_advanced_agent.md)
**What it does:** Expert Java 17+ developer. Generates Spring Boot 3.x services with JPA, Maven/Gradle, dependency injection, and comprehensive JUnit5 tests.

**When to use it:**
- Building Java microservices
- Spring Boot REST APIs
- Enterprise applications with Spring ecosystem
- Need constructor injection and immutability

**How to use it:**
```
"Create a Spring Boot service for processing payment orders with async job handling"
→ Generates: Spring Boot controller, service layer, JPA entities, JUnit5 tests, Javadoc
```

---

#### Pyra (python_advanced_agent.md)
**What it does:** Expert Python 3.11+ developer. Generates FastAPI APIs with async/await, SQLAlchemy 2.x, Pydantic validation, and pytest fixtures.

**When to use it:**
- Building async Python APIs
- FastAPI with modern Python features
- Need type hints and validation
- Want async database access

**How to use it:**
```
"Create a FastAPI endpoint for fetching paginated user profiles with caching"
→ Generates: async routes, SQLAlchemy queries, Pydantic schemas, pytest tests, type hints
```

---

#### Rexa (react_advanced_agent.md)
**What it does:** Expert React 18+ developer. Generates TypeScript React components with hooks, TanStack Query, Zustand state management, and React Testing Library.

**When to use it:**
- Building modern React frontends
- Need complex state management
- Want type-safe React with TypeScript
- Need data fetching and caching

**How to use it:**
```
"Create a product listing component with filtering, sorting, and pagination"
→ Generates: React component, hooks, TanStack Query, Zustand store, RTL tests
```

---

#### Sigma (mssql_advanced_agent.md)
**What it does:** SQL Server DBA expert. Generates T-SQL queries, indexing strategies, query optimization, and DMV-based monitoring.

**When to use it:**
- Optimizing SQL Server performance
- Creating complex queries with CTEs
- Need index strategies and execution plans
- Want stored procedures with error handling

**How to use it:**
```
"Optimize a slow product search query returning 100K rows"
→ Generates: optimized T-SQL, index recommendations, execution plan analysis, DMV queries
```

---

### 🔍 Reviewer Agents

#### Sherlock (code_health_inspector_agent.md)
**What it does:** Code health scanner. Performs 6-phase analysis: structure, performance, error handling, delayed operations, memory leaks, and security vulnerabilities.

**When to use it:**
- Need code quality audit
- Looking for performance bottlenecks
- Want security vulnerability scan
- Need structured quality report

**How to use it:**
```
"Scan this service for performance and security issues"
→ Outputs: P0-P3 severity issues, N+1 queries, blocking calls, missing error handling, fixes
```

---

#### Code Review Agent (code_review_agent.md)
**What it does:** Design and pattern reviewer. Checks architecture, SOLID principles, naming conventions, and design patterns.

**When to use it:**
- Code quality and design review
- Need architectural feedback
- Want SOLID principles enforcement
- Check pattern usage

**How to use it:**
```
"Review this REST API for design quality and SOLID principles"
→ Outputs: Pattern recommendations, SOLID violations, naming feedback, architectural suggestions
```

---

#### Git Review Agent (git-review-2.md)
**What it does:** Git history and PR reviewer. Analyzes commits, branching strategy, code organization, and pull request structure.

**When to use it:**
- Review commit quality and messages
- Check PR organization and structure
- Analyze branching strategy
- Ensure git best practices

**How to use it:**
```
"Review this branch for commit quality and PR structure"
→ Outputs: Commit message feedback, branching suggestions, PR structure analysis
```

---

### 📋 Integration & Orchestration Agents

#### JIRA Implementation Agent (jira_implementation_agent.md)
**What it does:** Task breakdown and tracking agent. Converts user stories and requirements into actionable implementation tasks with subtasks and acceptance criteria.

**When to use it:**
- Breaking down user stories into tasks
- Creating sprint planning from requirements
- Generating acceptance criteria
- Need structured task hierarchy

**How to use it:**
```
"Break down this user story into implementation tasks"
→ Outputs: Main task, subtasks, acceptance criteria, story points estimation
```

---

#### CI/CD Orchestrator (jira_mr_sync_review.agent.md)
**What it does:** Pipeline automation agent. Orchestrates CI/CD workflows, syncs JIRA with merge requests, and automates release processes.

**When to use it:**
- Setting up CI/CD pipelines
- Automating JIRA ↔ MR sync
- Creating release automation
- Building deployment pipelines

**How to use it:**
```
"Create a CI/CD pipeline that syncs JIRA tasks with merge requests"
→ Outputs: Pipeline config, webhook setup, automation rules, release flow
```

---

### ✍️ Supporting Skills by Category

#### **Integration & Messaging:**
- **apache_camel_skill.md** — Enterprise Integration Patterns (EIP) and routing
- **apache_pulsar_skill.md** — Pulsar messaging and stream processing
- **camel_exception_handling_skill.md** — Camel error routes and Dead Letter queues
- **camel_pulsar_integration_skill.md** — Camel + Pulsar integration patterns

#### **Code Quality & Standards:**
- **code_health_skill.md** — Quality inspection taxonomy and severity scale
- **sonarqube_vulnerability_skill.md** — OWASP Top 10, SonarQube rules, security scanning
- **error_handling_skill.md** — Exception patterns, try-catch strategies, recovery
- **code_formatting_skill.md** — Formatting standards, naming conventions, style guides

#### **Testing & Observability:**
- **testing_junit5_skill.md** — JUnit5, Mockito, parameterized tests
- **testing_pytest_skill.md** — pytest, fixtures, parametrization, coverage
- **testing_react_skill.md** — React Testing Library, user-centric testing
- **logger_skill.md** — Logging patterns, log levels, structured logging
- **opentelemetry_skill.md** — Distributed tracing, metrics, observability

#### **Language & Framework Standards:**
- **java_advanced_skill.md** — Java 17+ records, sealed classes, pattern matching
- **java17_skill.md** — Java 17 modern features and best practices
- **java11_skill.md** — Java 11 LTS features and long-term support patterns
- **python_advanced_skill.md** — Python 3.11+ type hints, async/await, dataclasses
- **react_advanced_skill.md** — React 18+ hooks, concurrent features, Suspense
- **mssql_advanced_skill.md** — T-SQL, indexes, query optimization, DMVs

#### **Framework Specific:**
- **spring_advanced_skill.md** — Spring dependency injection, AOP, transactions
- **spring_camel_integration_skill.md** — Spring with Camel integration
- **rest_api_java_skill.md** — REST API patterns for Spring Boot
- **rest_api_python_skill.md** — REST API patterns for FastAPI
- **lombok_skill.md** — Project Lombok annotations and usage

#### **Architecture & Design:**
- **oop_skill.md** — OOP pillars: encapsulation, inheritance, polymorphism, abstraction
- **documentation_skill.md** — Javadoc, docstrings, JSDoc, comment best practices

---

## ✨ Key Features

### All Agents Follow Master Rules

1. **Version Check First** — Check environment before coding
2. **Test Generation** — Every feature gets tests (AAA pattern)
3. **OOP Principles** — All 4 pillars with concrete examples
4. **Clean Code** — ≤20 lines per method, ≤300 lines per class
5. **Documentation** — Javadoc/docstrings/JSDoc mandatory
6. **Security** — Parameterized queries, input validation, no secrets in logs
7. **Error Handling** — Try-catch, logging, recovery strategies
8. **Code Quality** — Formatting, naming, alignment
9. **Project Intake** — Ask questions before generating code

### Multi-Language Support

- **Java** — Spring Boot 3.x, JUnit5, Maven/Gradle, Lombok
- **Python** — FastAPI, pytest, asyncio, Pydantic v2
- **React** — React 18+, TypeScript, TanStack Query
- **SQL Server** — T-SQL, DMVs, indexing strategies
- **Apache** — Camel EIP patterns, Pulsar messaging

---

## 🛠 Tools

### Exporter
```bash
# Export all skills + agents to all platforms
python3 tools/exporter.py

# Interactive setup (recommended)
python3 tools/exporter.py --interactive

# Export to specific platform
python3 tools/exporter.py --target claude

# List all available skills and agents
python3 tools/exporter.py --list

# Preview without writing
python3 tools/exporter.py --dry-run

# Remove all exported files
python3 tools/exporter.py --clean
```

### Auto-Update Checker
```bash
# Check for available updates
python3 tools/update_checker.py --check

# Download and apply latest version
python3 tools/update_checker.py --apply

# Show current version
python3 tools/update_checker.py --version
```

### Other Tools
```bash
# Validate all skills have proper frontmatter
python3 tools/skill_validator.py

# Fix code block language tags in markdown
python3 tools/fix_code_blocks.py

# Run test suite
python3 -m pytest tests/ -v
```

---

## 📖 Getting Started Workflows

### Workflow 1: First-Time Setup (Recommended)

```bash
# Step 1: Check for latest version
python3 tools/update_checker.py --check

# Step 2: If update available, apply it
python3 tools/update_checker.py --apply

# Step 3: Run interactive setup
python3 tools/exporter.py --interactive

# Follow prompts to select:
# - Project root directory
# - Target platforms (Claude, Copilot, Cursor, etc.)
# - Skills and agents to export
```

### Workflow 2: Manual Setup

```bash
# Step 1: Check and apply updates
python3 tools/update_checker.py --apply

# Step 2: Export to Claude Code
python3 tools/exporter.py --target claude

# Step 3: List what's available
python3 tools/exporter.py --list

# Step 4: Export specific skills
python3 tools/exporter.py --target claude --skills java,spring,testing

# Step 5: Export specific agents
python3 tools/exporter.py --target claude --agents developer
```

### Workflow 3: Multi-Platform Setup

```bash
# Export to multiple platforms at once
python3 tools/exporter.py --target claude copilot cursor windsurf

# Or export to all platforms
python3 tools/exporter.py
```

### Workflow 4: Keeping Updated

```bash
# Daily: Check for updates
python3 tools/update_checker.py --check

# When update available: Apply it
python3 tools/update_checker.py --apply

# Then re-export: Ensure latest skills are in your IDE
python3 tools/exporter.py
```

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Skills | 30 |
| Agents | 9 |
| Agent Roles | 5 |
| Platform Exports | 8 |
| Autonomous Phases | 5 (DB → Backend → Frontend → Tests → Deployment) |
| Test Coverage | 95+ tests passing |
| Dependencies | 0 (stdlib only) |

---

## 📖 Documentation

- **[CLAUDE.md](CLAUDE.md)** — Repository instructions for Claude Code
- **[agents/README.md](agents/README.md)** — Agent role guide
- **[tools/README.md](tools/README.md)** — Exporter documentation
- **[instructions/master_instruction_set.md](instructions/master_instruction_set.md)** — Universal rules

---

## 📋 Changelog

### v4.0.0 — 2026-05-20

**Major Release: Autonomous Developer System**

**New:**
- 🤖 **Autonomous Developer Agent** — End-to-end code generation from plain-text requirements
- 4 core generation skills:
  - `database_skill.md` — SQL schema + migrations for PostgreSQL/MySQL/SQL Server
  - `backend_skill.md` — REST API generation (FastAPI, Spring Boot)
  - `frontend_skill.md` — React component generation (TypeScript, Tailwind)
  - `test_skill.md` — Comprehensive testing (pytest, Jest, Playwright, E2E)
- **AUTONOMOUS_DEVELOPER_README.md** — Complete system architecture with workflow diagrams
- **SETUP_GUIDE.md** — Quick 2-minute setup guide
- **tools/interactive_exporter.py** — Interactive CLI wizard for platform selection
- Project detection — Automatically detects new vs existing projects
- Task tracking — JSON-based task completion monitoring
- Knowledge graph integration — graphify for smart context
- GitHub PR auto-sync — Automatic PR creation with generated code

**Updated:**
- `tools/exporter.py` — Added `--interactive/-i` flag for guided setup
- `.gitignore` — Allow committed superpowers docs (specs, plans)

**Statistics:**
- Now 30 skills (up from 26)
- Now 9 agents (up from 8)
- 5-phase autonomous pipeline
- 95+ tests passing
- Interactive setup experience

---

### v3.0.0 — 2026-04-15

**Breaking changes:**
- `tools/skill_exporter.py` removed — replaced by `tools/exporter.py`
- Platform output format changed from merged single files to one file per skill/agent
- Output directories changed (see Platform Output Locations above)

**New:**
- `tools/exporter.py` — unified exporter replacing `skill_exporter.py`
- Agent export support — all 8 agents now exported alongside skills
- 3 new platform targets: Windsurf, Gemini CLI, Aider
- One file per skill, one file per agent — no merging
- `--agents` CLI flag to filter agents by slug/role
- `--clean` CLI flag to remove all exported files
- 79 automated tests (`tests/tools/test_exporter.py`)
- Platform-native frontmatter per target (Copilot `applyTo`, Cursor `description/globs/alwaysApply`, Continue.dev `name/description`)

**Skills added (8 new):**
- `java11_skill.md`, `java17_skill.md`
- `logger_skill.md`, `opentelemetry_skill.md`
- `lombok_skill.md`, `oop_skill.md`
- `spring_camel_integration_skill.md`, `camel_pulsar_integration_skill.md`

---

### v2.0.0 — 2026-04-03

**New:**
- 8 new skills: Camel, Spring, logging, observability
- `tools/skill_exporter.py` — export to 5 platforms
- `tools/skill_validator.py`, `tools/fix_code_blocks.py`
- Agent definitions for all 4 roles
- Instructions directory with master rule set and intake forms

---

### v1.0.0 — Initial release

- Core prompt templates (email, code review, testing, project management)
- Python field derivation parser
- Basic agent and skill structure

---

## 📝 License

This repository is **sharable**, **reusable**, and **open for teams**.

---

**Tested with:** GitHub Copilot, Claude Code, Cursor IDE, Windsurf, Gemini CLI, Continue.dev, OpenAI API, Aider
