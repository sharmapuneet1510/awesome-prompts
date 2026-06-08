# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Foundational Principles

**All work follows four core behavioral principles** from Andrej Karpathy's observations on LLM coding pitfalls:

1. **Think Before Coding** — Clarify assumptions, surface tradeoffs, present options
2. **Simplicity First** — Minimum code, no overengineering, no speculation
3. **Surgical Changes** — Touch only what you must, clean up only your mess
4. **Goal-Driven Execution** — Define success criteria, loop until verified

See `instructions/master_instruction_set.md` (FOUNDATIONAL PRINCIPLES section) for details.

---

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
├── agents/                           ← Role-based agent definitions (5 agents, v3.0) + modules/functions
│   ├── orchestrator_agent.md         ← Strategy & Orchestration (plan, build, context, pr, review, tradeoff, risk)
│   ├── architect_agent.md            ← Architecture & Design (design, refactor, frontend, schema, api, a11y)
│   ├── implementer_agent.md          ← Implementation & Execution (build, test, doc, pipeline, docker, iac, full)
│   ├── quality_agent.md              ← QA & Security (review, audit, security, perf, debug, report)
│   ├── business_analyst_agent.md     ← Utility — Backlog (report, parse)
│   ├── orchestrator/                 ← Orchestrator agent modules & functions
│   │   ├── modules/                  ← Orchestrator modules (design_solver, expert_panel_generator, ideation_engine)
│   │   ├── functions/                ← Orchestrator functions (ideate, solve)
│   │   └── README.md
│   └── README.md                     ← Agent directory (v3.0 with linear pipeline)
│
├── hooks/                            ← Hook scripts for platform automation
│
├── skills/                           ← Reusable implementation skills (22 skills)
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
├── tools/
│   ├── exporter.py                   ← Multi-platform export tool (skills, agents, hooks)
│   └── [other tools]
│
└── CLAUDE.md
```

## Agents by Role (v3.0 — 4-Role Architecture)

Agents are organized by responsibility using a **lean, role-based architecture**. See `agents/README.md` and `AGENTS_FUNCTIONS.md` for detailed descriptions and function dispatch.

**Total: 5 agents (down from 13) + 28 callable functions — zero role overlap**

| # | Role | Agent | Functions | Purpose | Tech-Agnostic |
|---|------|-------|-----------|---------|---------------|
| 1 | **Strategy & Orchestration** | Orchestrator | plan, build, context, pr, review, tradeoff, risk | Full-stack generation + technical leadership + requirements parsing | ✅ Yes |
| 2 | **Architecture & Design** | Architect | design, refactor, frontend, schema, api, a11y | System topology, greenfield/brownfield design, API contracts, DB schema, UI architecture, accessibility | ✅ Yes |
| 3 | **Implementation & Execution** | Implementer | build, test, doc, pipeline, docker, iac, full | Code generation, testing, documentation, CI/CD, containerization, infrastructure (key: `full` runs build+test+doc with no context loss) | ✅ Yes |
| 4 | **QA, Security & Performance** | Quality | review, audit, security, perf, debug, report | PR validation, codebase audit, OWASP security scan, performance optimization, RCA, unified quality synthesis | ✅ Yes |
| 5 | **Utility — Backlog** | Business Analyst | report, parse | JIRA parsing + HTML backlog visualization | ✅ Yes |

### Skill-Based Architecture

Instead of tech-specific agents (Jarvis for Java, Pyra for Python, etc.), the system uses **lean role-based agents** (5 total) that delegate to **reusable skills** (22 total):

```
orchestrator:plan → orchestrator:build
    ↓
architect:design (topology, API, schema)
    ↓
implementer:full (runs in same context window)
    ├─ implementer:build (detects tech stack)
    │   ↓
    │   Applies appropriate skill:
    │   • java_advanced_skill (for Java/Spring Boot)
    │   • python_advanced_skill (for Python/FastAPI)
    │   • react_advanced_skill (for React/TypeScript)
    │   • database_skill (for DB design)
    │   • backend_skill (for REST APIs)
    │   • frontend_skill (for React components)
    │   ↓ Generates code
    │
    ├─ implementer:test
    │   ↓ Generates tests (95%+ coverage)
    │
    └─ implementer:doc
        ↓ Generates docs + architecture + API reference
        
    ✓ Complete code + tests + documentation (no context loss between phases)
    ↓
quality:review (validate + score)
    ↓
orchestrator:pr (open GitHub PR)
```

**Benefits:**
- ✅ **Fewer agents** (5 vs 13) = lower token cost
- ✅ **Linear pipeline** = explicit handoffs with full context
- ✅ **implementer:full** = no state transfer loss between build/test/doc
- ✅ **22 reusable skills** = no duplication across agents
- ✅ **28 callable functions** = fine-grained control via `agent:function` syntax
- ✅ Clear separation: agent = orchestration + dispatch, skill = implementation

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

## Specialist Agent Modes

Nine specialized agent modes for common engineering roles have been integrated into your system. See [SPECIALIST_AGENT_MODES.md](SPECIALIST_AGENT_MODES.md) for quick reference:

| Specialist Role | Agent:Function | Use When |
|---|---|---|
| **Full-Stack Engineer** | `orchestrator:build` | New project from scratch |
| **Code Auditor** | `quality:audit` | Analyzing existing codebase |
| **Debugging Expert** | `quality:debug` | Production incident RCA |
| **Technical Lead** | `orchestrator:review/tradeoff/risk` | Strategic decisions needed |
| **Performance Expert** | `quality:perf` | Optimization & scaling |
| **Systems Architect** | `architect:design` | Infrastructure design |
| **Frontend Expert** | `architect:frontend` | UI component architecture |
| **Security Auditor** | `quality:security` | Vulnerability assessment |
| **DevOps Engineer** | `implementer:pipeline/docker/iac` | Deployment & infrastructure |

**Enhanced function files** (v3.1) include detailed behavioral instructions for each specialist mode.

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
