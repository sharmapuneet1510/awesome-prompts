# 🛠️ Skills Directory (v2.0 — Consolidated)

> Reusable, tech-specific implementation modules used by agents. 23 skills, zero orphans.

## Quick Navigation (23 Skills)

| # | Skill | Purpose | Language | Used By |
|---|-------|---------|----------|---------|
| 1 | [Code Documentation](code_documentation_skill.md) | Javadoc, docstrings, JSDoc | Java/Python/JS | Most agents |
| 2 | [Code Review](code_review_skill.md) | 6-phase PR analysis + scoring | All languages | Code Reviewer |
| 3 | [Code Health](code_health_skill.md) | Issue taxonomy, severity scoring | All languages | Codebase Auditor |
| 4 | [Code Formatting](code_formatting_skill.md) | Indentation, line length, naming | Java/Python/JS | All agents |
| 5 | [Database](database_skill.md) | SQL schema, migrations, indexing | PostgreSQL/MySQL/MSSQL | Autonomous Dev, Architecture |
| 6 | [Backend API](backend_skill.md) | REST API generation (wrapper) | FastAPI/Spring Boot | Implementation |
| 7 | [Frontend](frontend_skill.md) | React components (wrapper) | React/TypeScript | Implementation |
| 8 | [Testing](test_skill.md) | Unit/integration/E2E tests | JUnit5/pytest/Jest | Test Engineer |
| 9 | [Context Builder](context_builder_skill.md) | Project scanning, architecture.md | All stacks | All agents |
| 10 | [Error Handling](error_handling_skill.md) | Try-catch, exceptions, recovery | Java/Python/JavaScript | All agents |
| 11 | [Java Advanced](java_advanced_skill.md) | Java 17/21, Spring Boot 3.x | Java | Implementation |
| 12 | [Python Advanced](python_advanced_skill.md) | Python 3.11+, async, FastAPI | Python | Implementation |
| 13 | [React Advanced](react_advanced_skill.md) | React 18+, TypeScript, hooks | React/TypeScript | Implementation, Frontend Engineer |
| 14 | [MSSQL Advanced](mssql_advanced_skill.md) | T-SQL, stored procedures, optimization | SQL Server | Implementation |
| 15 | [OOP Patterns](oop_skill.md) | Encapsulation, inheritance, polymorphism, SOLID | All languages | All agents |
| 16 | [Apache Camel](apache_camel_skill.md) | EIP patterns, routes, components | Java/Spring Boot | Advanced integrations |
| 17 | [Apache Pulsar](apache_pulsar_skill.md) | Messaging, producers, consumers | Java/Python | Advanced messaging |
| 18 | [Spring Advanced](spring_advanced_skill.md) | Spring Framework, Spring Boot internals | Java/Spring Boot | Advanced Java |
| 19 | [OpenTelemetry](opentelemetry_skill.md) | Tracing, metrics, observability | Java/Spring Boot | Advanced monitoring |
| 20 | [Logger](logger_skill.md) | SLF4J, Logback, structured logging | Java | All Java agents |
| 21 | [Lombok](lombok_skill.md) | @Data, @Builder, boilerplate reduction | Java | Advanced Java |
| 22 | [JIRA HTML Report](jira_html_report_skill.md) | Parse JIRA, generate HTML backlog | Language-agnostic | Business Analyst |
| 23 | [BA Create](ba_create_skill.md) | Parse plain-text requirements → JIRA JSON + BDD HTML cards | Language-agnostic | Business Analyst |
| 24 | [Multi-Review HTML](multi_review_html_skill.md) | Batch PR review HTML with sidebar tabs + summary dashboard | Language-agnostic | Quality Agent |

---

## 🎯 Skill Organization

### Core Skills (Used by Most Agents)
- `code_documentation_skill` — Code docs
- `context_builder_skill` — Project context
- `test_skill` — Testing
- `backend_skill` — REST APIs
- `frontend_skill` — UI components

### Language-Specific Skills
- **Java:** `java_advanced_skill`, `spring_advanced_skill`, `logger_skill`, `lombok_skill`
- **Python:** `python_advanced_skill`
- **React/TypeScript:** `react_advanced_skill`
- **SQL/Database:** `database_skill`, `mssql_advanced_skill`

### Advanced/Specialized Skills
- `apache_camel_skill` — Integration patterns
- `apache_pulsar_skill` — Messaging
- `opentelemetry_skill` — Observability
- `error_handling_skill` — Exception handling
- `oop_skill` — Design patterns
- `code_health_skill` — Issue taxonomy
- `code_review_skill` — PR analysis
- `code_formatting_skill` — Code style

### Business Analyst Skills (Backlog & Requirements)
- `jira_html_report_skill` — Parse JIRA exports, generate HTML backlog reports
- `ba_create_skill` — Parse plain-text requirements, generate JIRA JSON + BDD HTML cards

### Quality Agent Skills (Batch Review)
- `multi_review_html_skill` — Batch PR review HTML with sidebar tabs, summary dashboard, export options

---

## 📝 Consolidated in v2.0

**Removed (12 Orphaned Skills):**
- ❌ `documentation_skill` — Duplicate of `code_documentation_skill`
- ❌ `java11_skill`, `java17_skill` — Subsumed by `java_advanced_skill`
- ❌ `rest_api_java_skill`, `rest_api_python_skill` — Subsumed by `backend_skill`
- ❌ `testing_junit5_skill`, `testing_pytest_skill`, `testing_react_skill` — Subsumed by `test_skill`
- ❌ `camel_exception_handling_skill` — Consolidated into `apache_camel_skill`
- ❌ `camel_pulsar_integration_skill` — Consolidated into `apache_camel_skill`
- ❌ `spring_camel_integration_skill` — Consolidated into `apache_camel_skill`
- ❌ `sonarqube_vulnerability_skill` — Consolidated into `code_health_skill`

**New Skills Added:**
- ✅ `jira_html_report_skill` — Parse JIRA exports, generate HTML backlog reports

---

## 🏗️ Skills Architecture

```
Implementation Agent
    ↓
Detect tech stack
    ├─ Java? → java_advanced_skill + spring_advanced_skill
    ├─ Python? → python_advanced_skill
    ├─ React? → react_advanced_skill
    ├─ SQL? → database_skill + mssql_advanced_skill
    └─ All → code_documentation_skill + test_skill + error_handling_skill
    ↓
Skill executes implementation
    ├─ Code patterns
    ├─ Best practices
    ├─ Quality standards
    └─ Testing approach
    ↓
Generate complete code
```

---

## 📚 Skill Categories

### Code Quality & Documentation
- `code_documentation_skill` — JSDoc/docstrings/Javadoc
- `code_review_skill` — 6-phase PR analysis
- `code_health_skill` — Issue taxonomy + severity
- `code_formatting_skill` — Style standards

### Testing
- `test_skill` — Unit/integration/E2E tests (orchestrator)
- ~~`testing_junit5_skill`~~ (subsumed)
- ~~`testing_pytest_skill`~~ (subsumed)
- ~~`testing_react_skill`~~ (subsumed)

### Database & Persistence
- `database_skill` — Schema design, migrations, indexing
- `mssql_advanced_skill` — T-SQL + SQL Server optimization

### Backend Development
- `backend_skill` — REST API generation (FastAPI, Spring Boot)
- `java_advanced_skill` — Java 17+ patterns
- `python_advanced_skill` — Python 3.11+ patterns
- `spring_advanced_skill` — Spring internals

### Frontend Development
- `frontend_skill` — React components (orchestrator)
- `react_advanced_skill` — React 18+, hooks, TypeScript

### Integration & Messaging
- `apache_camel_skill` — EIPs, route DSL
- `apache_pulsar_skill` — Messaging patterns
- ~~`camel_exception_handling_skill`~~ (consolidated)
- ~~`camel_pulsar_integration_skill`~~ (consolidated)
- ~~`spring_camel_integration_skill`~~ (consolidated)

### Observability & Logging
- `opentelemetry_skill` — Tracing, metrics, logs
- `logger_skill` — SLF4J, Logback, structured logging

### Cross-Cutting
- `error_handling_skill` — Exception handling
- `oop_skill` — Design patterns, SOLID
- `context_builder_skill` — Project context, architecture

### Business Analysis
- `jira_html_report_skill` — JIRA export → HTML backlog

---

## 🔗 Links

- **[Agents Directory](../agents/README.md)** — Agent definitions (13 total)
- **[Tools Documentation](../tools/README.md)** — Utility scripts
- **[Master Rules](../instructions/master_instruction_set.md)** — Non-negotiable standards
- **[Main README](../README.md)** — Project overview

---

**Last Updated:** June 4, 2026 | **Version:** 2.0.0 (Consolidated) | **Skills:** 24 | **Agents:** 5
