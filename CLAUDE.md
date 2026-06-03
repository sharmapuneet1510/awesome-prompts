# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

A collection of AI/LLM prompt templates, reusable skills, and full agent definitions for software engineering workflows, plus production-ready Python libraries (token_optimizer for intelligent query analysis) and a Python-based code parser for field derivation analysis in multi-module Maven repositories.

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
├── agents/                           ← Role-based agent definitions (13 agents)
│   ├── implementation_agent.md       ← Full-lifecycle feature builder
│   ├── code_review_agent.md          ← PR validation + quality scoring
│   ├── documentation_agent.md        ← Code docs + architecture docs + HTML sites
│   ├── architecture_agent.md         ← Design new systems OR refactor existing
│   ├── business_analyst_agent.md     ← JIRA parsing + HTML backlog reports
│   ├── test_case_generator_agent.md  ← 100% coverage tests with business validation
│   ├── security_auditor_agent.md     ← Vulnerability scanning + threat modeling
│   ├── performance_optimizer_agent.md ← Bottleneck analysis + optimization
│   ├── production_debugger_agent.md  ← Root cause analysis + edge case discovery
│   ├── codebase_auditor_agent.md     ← Tech debt + violations scanning
│   ├── integration_agent.md          ← CI/CD + Docker + Terraform + monitoring
│   ├── technical_lead_agent.md       ← Architecture reviews + tech decisions
│   ├── senior_frontend_engineer_agent.md ← React/TypeScript component design
│   ├── autonomous/
│   │   ├── autonomous_dev_agent.md   ← Full-stack orchestrator (DB + API + UI + tests)
│   │   └── README.md                 ← Autonomous development guide
│   └── README.md                     ← Agent directory (consolidated v2.0)
│
├── skills/                           ← Reusable implementation skills (23 skills)
│   ├── code_documentation_skill.md   ← JSDoc/docstrings/Javadoc auto-generation
│   ├── code_review_skill.md          ← 6-phase PR analysis + scoring
│   ├── code_health_skill.md          ← Issue taxonomy + severity scoring
│   ├── code_formatting_skill.md      ← Code style standards
│   ├── database_skill.md             ← SQL schema + migrations (PostgreSQL/MySQL/MSSQL)
│   ├── backend_skill.md              ← REST API generation (FastAPI/Spring Boot)
│   ├── frontend_skill.md             ← React component generation + hooks
│   ├── test_skill.md                 ← Test generation (JUnit5/pytest/Jest)
│   ├── context_builder_skill.md      ← Project architecture & tech stack analysis
│   ├── java_advanced_skill.md        ← Java 17/21 coding standards & patterns
│   ├── python_advanced_skill.md      ← Python 3.11+ coding standards & patterns
│   ├── react_advanced_skill.md       ← React 18+ / TypeScript coding standards
│   ├── mssql_advanced_skill.md       ← T-SQL coding standards & patterns
│   ├── spring_advanced_skill.md      ← Spring Framework / Spring Boot internals
│   ├── error_handling_skill.md       ← Exception handling + recovery patterns
│   ├── oop_skill.md                  ← OOP pillars + SOLID + design patterns
│   ├── apache_camel_skill.md         ← Apache Camel integration & EIP patterns
│   ├── apache_pulsar_skill.md        ← Apache Pulsar messaging & streaming
│   ├── opentelemetry_skill.md        ← Observability + tracing + metrics
│   ├── logger_skill.md               ← SLF4J + Logback + structured logging
│   ├── lombok_skill.md               ← Lombok annotations + boilerplate reduction
│   ├── jira_html_report_skill.md     ← Parse JIRA + generate HTML backlog
│   └── README.md                     ← Skills directory (consolidated v2.0)
│
├── parser/                           ← Python field derivation analysis tool
│
├── token_optimizer/                  ← Python library for intelligent query analysis
│   ├── __init__.py                   ← Package exports
│   ├── analyzer.py                   ← Main QueryAnalyzer orchestrator (120 lines)
│   ├── models.py                     ← Data models: enums, dataclasses, type-safe output
│   ├── config.py                     ← Configuration with default/strict/lenient modes
│   ├── scoring.py                    ← Scoring engines: clarity, context, feasibility
│   ├── detector.py                   ← Detection engines: web search, external data, tokens
│   └── README.md                     ← Full documentation with examples
│
├── tests/
│   └── test_token_optimizer.py       ← 35 comprehensive tests (all passing)
│
└── CLAUDE.md
```

## Agents by Role (v2.0 — Consolidated)

Agents are organized by responsibility using a **role-based generic architecture**. See `agents/README.md` for detailed descriptions.

**Total: 13 agents (down from 19) — zero role overlap**

| # | Role | Agent | File | Purpose | Tech-Agnostic |
|---|------|-------|------|---------|---------------|
| 1 | **Orchestrator** | Autonomous Dev | `agents/autonomous/autonomous_dev_agent.md` | Full-stack project generation (DB + API + UI + tests from requirements) | ✅ Yes |
| 2 | **Feature Builder** | Implementation Engineer | `agents/implementation_agent.md` | Code + tests + docs for single features/modules | ✅ Yes |
| 3 | **Systems Architect** | Architecture | `agents/architecture_agent.md` | Design new systems OR refactor existing ones (greenfield + brownfield) | ✅ Yes |
| 4 | **QA / Code Review** | Code Reviewer | `agents/code_review_agent.md` | PR validation against JIRA, quality scoring, HTML reports | ✅ Yes |
| 5 | **Testing** | Test Engineer | `agents/test_case_generator_agent.md` | 100% coverage tests with business validation | ✅ Yes |
| 6 | **Security** | Security Auditor | `agents/security_auditor_agent.md` | Vulnerability scanning, threat modeling, OWASP compliance | ✅ Yes |
| 7 | **Performance** | Performance Optimizer | `agents/performance_optimizer_agent.md` | Bottleneck analysis, optimization strategies, benchmarking | ✅ Yes |
| 8 | **Debugging** | Production Debugger | `agents/production_debugger_agent.md` | Root cause analysis, stack trace investigation, edge cases | ✅ Yes |
| 9 | **Code Health** | Codebase Auditor | `agents/codebase_auditor_agent.md` | Scan for violations, tech debt, security issues, roadmaps | ✅ Yes |
| 10 | **DevOps/Deployment** | DevOps Engineer | `agents/integration_agent.md` | CI/CD pipelines, Docker, Terraform, monitoring (AWS/GCP/Azure/K8s) | ✅ Yes |
| 11 | **Documentation** | Documentation Engineer | `agents/documentation_agent.md` | Code docs, architecture guides, API specs, HTML sites | ✅ Yes |
| 12 | **Strategy** | Technical Lead | `agents/technical_lead_agent.md` | Architecture reviews, tech decisions, team coordination | ✅ Yes |
| 13 | **Backlog Analysis** | Business Analyst | `agents/business_analyst_agent.md` | JIRA parsing, HTML backlog reports, filtering, stats | ✅ Yes |

### Skill-Based Architecture

Instead of tech-specific agents (Jarvis for Java, Pyra for Python, etc.), the system uses **generic role-based agents** that delegate to **reusable skills**:

```
implementation_agent (generic)
    ↓
    Detects tech stack
    ↓
    Applies appropriate skill:
    • java_advanced_skill (for Java/Spring Boot)
    • python_advanced_skill (for Python/FastAPI)
    • react_advanced_skill (for React/TypeScript)
    • mssql_advanced_skill (for SQL Server/T-SQL)
    • database_skill (for database design)
    • backend_skill (for REST API generation)
    • frontend_skill (for UI component generation)
    • code_documentation_skill (for JSDoc/docstrings/Javadoc)
    ✓ Generates complete code + tests + documentation
```

**Benefits:**
- ✅ Less duplication (one agent per role, not per tech)
- ✅ Easier to maintain (update skill, all agents benefit)
- ✅ Simpler to extend (add new skill = all agents can use it)
- ✅ Clear separation of concerns (agent = orchestration, skill = implementation)

## Skills

Skills in `skills/` are reusable coding standard modules referenced by agents. They define language idioms, patterns, quality rules, and output format expectations.

## Key Tools

| Tool | Purpose |
|------|---------|
| `tools/exporter.py` | Export agents & skills to 8 platforms (Claude, Copilot, Cursor, Windsurf, VS Code, Gemini, Continue, OpenAI, Aider) |
| `tools/requirement_parser.py` | Parse requirements from free text, JIRA, files, or auto-detect from project |
| `tools/context_builder.py` | Scan projects, generate architecture.md, tech-stack.md, context.json, design.html |
| `tools/generate_design_html.py` | Create interactive HTML visualization (4 tabs: architecture, tech stack, file tree, API endpoints) |
| `tools/task_generator.py` | Break down requirements into bite-sized task specifications |
| `tools/graphify_integrator.py` | Generate knowledge graphs with token caching |
| `tools/github_sync.py` | Create GitHub PRs with generated code |

## Python Libraries

### token_optimizer (v1.0.0)

Production-ready library for intelligent query analysis before Claude dispatch.

**Location:** `token_optimizer/` (package) + `tests/test_token_optimizer.py` (35 tests)

**Features:**
- Multi-dimensional query scoring (clarity, context, feasibility)
- Web search detection for trending/current/live data
- Intent classification (research, coding, analysis, creative, instruction)
- Token estimation and smart routing recommendations
- Structured feedback with actionable suggestions
- Configurable thresholds (default/strict/lenient modes)

**Installation:**
```bash
pip install -e token_optimizer/
```

**Quick Start:**
```python
from token_optimizer import QueryAnalyzer

analyzer = QueryAnalyzer()
result = analyzer.analyze("your query here")
print(result.feedback.recommendation)  # 'claude', 'web_search', etc.
```

**Key Classes:**
- `QueryAnalyzer` - Main orchestrator
- `ScoringMetrics` - Clarity, context, feasibility scores
- `QueryFeedback` - Status, issues, suggestions
- `Config` - Configurable thresholds and weights

See `token_optimizer/README.md` for full documentation and examples.

## Project Structure & Artifacts

When **implementation_agent** or **autonomous_dev_agent** runs, they generate:

```
project-root/
├── docs/context/                    ← Project architecture documentation
│   ├── context.json                 ← Machine-readable project metadata
│   ├── architecture.md              ← Mermaid diagram + design narrative
│   ├── tech-stack.md                ← Technology reference table
│   └── design.html                  ← Interactive visualization (4 tabs)
├── requirements.md                  ← Parsed requirement specification
└── [generated code, tests, docs]
```

## Workflow Examples

### Workflow 1: Feature Implementation (Free Text → Code + Tests + Docs)
```
User: "Build user registration with email validation"
         ↓
implementation_agent (STEP 0-7)
  1. Gather requirement (free text parsing)
  2. Load context (check docs/context/)
  3. Confirm requirements
  4. Plan implementation
  5. Apply skill (e.g., backend_skill)
  6. Generate code + tests
  7. Auto-document (code_documentation_skill)
         ↓
Output: routes/register.py, models/user.py, tests/test_register.py (100% docs)
```

### Workflow 2: Test Generation (JIRA → 100% Coverage Tests + Validation)
```
User: "Generate tests for AUTH-789"
         ↓
test_case_generator_agent (STEP 0-10)
  1. Fetch JIRA ticket AUTH-789
  2. Extract acceptance criteria
  3. Analyze code context
  4. Plan test cases
  5. Generate tests (unit + integration)
  6. Auto-document test methods
  7. Validate all criteria covered ✓
  8. Run tests (100% coverage)
         ↓
Output: tests/test_login.py (8 tests, 100% coverage, all criteria validated)
```

### Workflow 3: Full-Stack Generation (Requirement → Complete System)
```
User: "Build e-commerce shopping cart with checkout"
         ↓
autonomous_dev_agent (14 steps)
  1. Parse requirement
  2. Build context (architecture.md, context.json)
  3. Generate task specs (01-05)
  4. Execute tasks sequentially:
     • Task 01: Database (schema.sql)
     • Task 02: Backend API (FastAPI routes)
     • Task 03: Frontend UI (React components)
     • Task 04: Tests (100% coverage)
     • Task 05: Deployment (docker-compose)
  5. Final documentation pass
  6. Create GitHub PR
         ↓
Output: Complete system with code, tests, docs, PR ready for review
```

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
