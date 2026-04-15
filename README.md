# Awesome Prompts — Enterprise-Grade AI Coding Assistant Repository

A comprehensive, production-ready collection of **AI agent definitions**, **coding skills**, and **prompt templates** for software engineering workflows. Compatible with GitHub Copilot, Claude, Cursor, Windsurf, Gemini CLI, Continue.dev, OpenAI API, and Aider.

**Version:** 3.0.0 | **Status:** ✅ Production Ready | 26 Skills | 8 Agents | 8 Platform Exports

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

---

## 📦 What's Included

### Skills (26 total)

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

### Agents (8 total, organized by role)

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

```bash
# Export all skills + agents to all platforms
python3 tools/exporter.py

# Validate all skills
python3 tools/skill_validator.py

# Fix code block language tags
python3 tools/fix_code_blocks.py

# Run tests
python3 -m pytest tests/ -v
```

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Skills | 26 |
| Agents | 8 |
| Agent Roles | 4 |
| Platform Exports | 8 |
| Test Coverage | 79 tests passing |
| Dependencies | 0 (stdlib only) |

---

## 📖 Documentation

- **[CLAUDE.md](CLAUDE.md)** — Repository instructions for Claude Code
- **[agents/README.md](agents/README.md)** — Agent role guide
- **[tools/README.md](tools/README.md)** — Exporter documentation
- **[instructions/master_instruction_set.md](instructions/master_instruction_set.md)** — Universal rules

---

## 📋 Changelog

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
