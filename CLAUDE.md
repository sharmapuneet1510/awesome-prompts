# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

A collection of AI/LLM prompt templates, reusable skills, and full agent definitions for software engineering workflows, plus a Python-based code parser for field derivation analysis in multi-module Maven repositories.

## Directory Structure

```
awesome-prompts/
├── instructions/                     ← Universal rules and project intake forms
│   ├── master_instruction_set.md     ← Non-negotiable rules all agents must follow
│   ├── java_project_intake.md        ← Java/Spring Boot Q&A intake template (33 questions)
│   └── python_project_intake.md      ← Python Q&A intake template with OOP patterns
│
├── prompts/                          ← Categorised prompt templates
│   ├── email/                        ← Email writing & review prompts
│   ├── code-review/                  ← Code review agent prompts
│   ├── testing/                      ← Test generation prompts
│   ├── codebase-analysis/            ← Codebase mapping, tracing, auditing
│   ├── project-management/           ← User stories, workflow mapping, Jira reader
│   ├── incident-management/          ← Production issue investigation
│   └── reporting/                    ← HTML report generation
│
├── agents/                           ← Full agent definitions (organized by role)
│   ├── developer/                    ← Code generation & implementation agents
│   │   ├── java_advanced_agent.md    ← "Jarvis" — Java 17+ / Spring Boot developer
│   │   ├── python_advanced_agent.md  ← "Pyra" — Python 3.11+ / FastAPI developer
│   │   ├── react_advanced_agent.md   ← "Rexa" — React 18+ / TypeScript developer
│   │   ├── mssql_advanced_agent.md   ← "Sigma" — SQL Server DBA & T-SQL
│   │   └── jira_implementation_agent.md ← Implementation task breakdown & tracking
│   ├── reviewer/                     ← Code review & quality inspection agents
│   │   ├── code_health_inspector_agent.md ← "Sherlock" — 6-phase code health scan
│   │   ├── code_review_agent.md      ← Pattern & design review
│   │   └── git-review-2.md           ← Git / PR review
│   ├── writer/                       ← Documentation & comment generation agents
│   │   └── jira_documentation_agent.md ← Technical documentation writer
│   ├── integration/                  ← CI/CD & automation agents
│   │   └── jira_mr_sync_review.agent.md ← Pipeline orchestration
│   └── README.md                     ← Agent role guide
│
├── skills/                           ← Reusable skill modules (consumed by agents)
│   ├── java_advanced_skill.md        ← Java 17+ coding standards & patterns
│   ├── python_advanced_skill.md      ← Python 3.11+ coding standards & patterns
│   ├── react_advanced_skill.md       ← React 18+ / TypeScript coding standards
│   ├── mssql_advanced_skill.md       ← T-SQL coding standards & patterns
│   ├── code_health_skill.md          ← Issue taxonomy, severity scale, scan checklist
│   ├── apache_camel_skill.md         ← Apache Camel integration framework & EIP patterns
│   ├── spring_advanced_skill.md      ← Spring Framework / Spring Boot advanced patterns
│   └── apache_pulsar_skill.md        ← Apache Pulsar messaging & streaming patterns
│
├── parser/                           ← Python field derivation analysis tool
└── CLAUDE.md
```

## Agents by Role

Agents are organized by responsibility. See `agents/README.md` for detailed descriptions.

### Developer Agents (Code Generation)

| Agent | File | Role | Technologies |
|-------|------|------|---------------|
| **Jarvis** | `agents/developer/java_advanced_agent.md` | Java/Spring Boot | Java 17+, Spring Boot 3.x, JPA, Maven, Gradle |
| **Pyra** | `agents/developer/python_advanced_agent.md` | Python/FastAPI | Python 3.11+, FastAPI, SQLAlchemy 2.x, asyncio |
| **Rexa** | `agents/developer/react_advanced_agent.md` | React/Frontend | React 18+, TypeScript, TanStack Query, Zustand |
| **Sigma** | `agents/developer/mssql_advanced_agent.md` | SQL Server DBA | SQL Server 2019/2022, T-SQL, indexing, DMVs |

### Reviewer Agents (Code Quality & Inspection)

| Agent | File | Role | Focus |
|-------|------|------|-------|
| **Sherlock** | `agents/reviewer/code_health_inspector_agent.md` | Code Health Inspector | Performance, error handling, delays, security, reliability |
| **Code Reviewer** | `agents/reviewer/code_review_agent.md` | Design Reviewer | Patterns, architecture, best practices |
| **Git Reviewer** | `agents/reviewer/git-review-2.md` | PR Reviewer | Commits, structure, conflicts |

### Writer Agents (Documentation)

| Agent | File | Role |
|-------|------|------|
| **Documentarian** | `agents/writer/jira_documentation_agent.md` | Technical Writer |

### Integration Agents (CI/CD & Automation)

| Agent | File | Role |
|-------|------|------|
| **CI/CD Orchestrator** | `agents/integration/jira_mr_sync_review.agent.md` | Pipeline Automation |

## Skills

Skills in `skills/` are reusable coding standard modules referenced by agents. They define language idioms, patterns, quality rules, and output format expectations.

## Prompt Categories

| Category | Contents |
|----------|---------|
| `prompts/email/` | SHORT, LONG, and AGENT variants of the email review prompt |
| `prompts/code-review/` | Conversational MCP-enabled code review agent |
| `prompts/testing/` | Conversational test case generator |
| `prompts/codebase-analysis/` | Codebase cartographer, regulatory code auditor, field tracing agent |
| `prompts/project-management/` | User story generator (Ajita), workflow mapper, Jira reader |
| `prompts/incident-management/` | Production issue investigator (Detective) |
| `prompts/reporting/` | HTML report generation prompt |

## Tools — Exporter

`tools/exporter.py` is a Python utility that exports skills **and agent definitions** to platform-native instruction files. Writes one file per skill and one file per agent — no merging.

```bash
# Export all skills and agents to all platforms
python tools/exporter.py

# Export specific skills/agents to specific platforms
python tools/exporter.py --target copilot claude --skills java,spring --agents developer

# List all available skills and agents
python tools/exporter.py --list

# Dry run — preview without writing
python tools/exporter.py --dry-run

# Remove all exported files
python tools/exporter.py --clean
```

**Supported platforms:** copilot, claude, cursor, windsurf, gemini, continue, openai, aider

See `tools/README.md` for full documentation.


## All Agents Follow Master Rules

All agents follow universal conventions from `instructions/master_instruction_set.md`:
- Always check versions first (Step 0)
- Use meaningful test names: `givenXxx_whenYyy_thenZzz()`
- Follow AAA testing pattern (Arrange-Act-Assert)
- Implement all OOP pillars with examples
- Keep methods ≤ 20 lines, classes ≤ 300 lines
- Document with Javadoc/docstrings/JSDoc
- Secure code: parameterized queries, input validation, no secrets in logs
- Always include comprehensive tests with new code

## Parser Commands

```bash
# Install dependencies
pip install -r parser/requirements.txt

# Run the orchestrator (requires local repo paths)
python parser/orcastrator.py
```

Key dependencies: `javalang` (Java AST parsing), `lxml` (XML/XSLT parsing), `networkx` (graph analysis), `pydantic` (data models).
