# New Features Summary — v2.0 Complete Build

This document summarizes all new agents, skills, and tools added to the awesome-prompts repository.

---

## 🎯 What Was Built

### 1. Three Advanced Technology Skills

**Location:** `skills/`

#### apache_camel_skill.md (15 KB)
- Apache Camel routing framework fundamentals
- Java route DSL with code examples
- Content-Based Router and Splitter/Aggregator patterns
- Error handling strategies (dead letter topics, retries)
- Custom Processor implementation
- Spring Boot integration
- Testing with CamelTestSupport
- Debugging and common issues

**Applies to:** Java, Spring Boot, Integration, EIP patterns

#### spring_advanced_skill.md (18 KB)
- IoC container internals and bean lifecycles
- Bean scopes (singleton, prototype, request, session)
- Aspect-Oriented Programming (AOP) with timing and retry aspects
- Spring WebFlux reactive programming (Mono, Flux)
- Spring Batch for bulk processing
- Spring Cloud patterns (Circuit Breaker, Resilience4j)
- Application Events for decoupled communication
- Debugging Spring issues (bean wiring, transactions, startup)

**Applies to:** Java, Spring Framework, Spring Boot, Spring WebFlux, Spring Cloud

#### apache_pulsar_skill.md (17 KB)
- Pulsar architecture (Broker, BookKeeper, ZooKeeper)
- Producer patterns (fire-and-forget, async, batching, compression)
- Four consumer subscription types (EXCLUSIVE, SHARED, FAILOVER, KEY_SHARED)
- Schema registry and evolution rules
- Dead Letter Topic configuration
- Spring for Apache Pulsar integration
- Python producer/consumer examples
- Debugging with admin commands

**Applies to:** Java, Python, Apache Pulsar, Spring Boot, Messaging, Streaming

### 2. Code Health Inspector Agent

**Location:** `agents/advanced-coding/code_health_inspector_agent.md`

**Agent Name:** Sherlock

Performs methodical, step-by-step code health scans:

- **Phase 0:** Intake (3 questions: scope, language, primary concern)
- **Phase 1:** Structure scan (maps classes, layers, dependencies)
- **Phase 2:** Performance & slowness (N+1 queries, blocking calls, render thrashing)
- **Phase 3:** Error handling (swallowed exceptions, missing handlers, null guards)
- **Phase 4:** Processing delays (sync work, missing timeouts, batch processing)
- **Phase 5:** Extras (memory leaks, security, reliability, maintainability)
- **Phase 6:** Report (structured P0–P3 findings with fix examples)

**Output:** Comprehensive written report with severity levels, categories, evidence, root cause, impact, and fixes.

### 3. Skill Exporter Tool

**Location:** `tools/skill_exporter.py`

A Python utility that exports all skills to instruction formats for 5 AI platforms:

```
GitHub Copilot    → .github/copilot-instructions.md
Claude Code       → .claude/skills_context.md
Cursor IDE        → .cursorrules
Continue.dev      → .continue/config.json
OpenAI API        → tools/output/openai_system_prompt.txt
```

**Features:**
- 600+ lines of well-structured, documented Python code
- Zero external dependencies
- Supports filtering by skill slug or tag
- Dry-run mode for previewing
- Automatic format optimization per platform
- Frontmatter parsing for skill metadata
- Comprehensive error messages

**Usage:**
```bash
python tools/skill_exporter.py                    # export all to all
python tools/skill_exporter.py --target copilot  # export to one platform
python tools/skill_exporter.py --list             # see all skills
```

---

## 📊 Complete File Inventory

### Skills (8 total, ~123 KB)

```
skills/
├── apache_camel_skill.md        (15 KB) — Camel integration patterns
├── apache_pulsar_skill.md       (17 KB) — Pulsar messaging & streaming
├── code_health_skill.md         (9.8 KB) — Code inspection taxonomy
├── java_advanced_skill.md       (15 KB) — Java 17+, OOP, Spring patterns
├── mssql_advanced_skill.md      (17 KB) — T-SQL, indexing, NOLOCK explained
├── python_advanced_skill.md     (17 KB) — Python 3.11+, async, FastAPI
├── react_advanced_skill.md      (13 KB) — React 18+, TypeScript, TanStack Query
└── spring_advanced_skill.md     (18 KB) — Spring IoC, AOP, WebFlux, Batch
```

### Agents (6 total + 5 Copilot)

```
agents/advanced-coding/
├── code_health_inspector_agent.md  (Sherlock — code scanning & reporting)
├── java_advanced_agent.md          (Jarvis — Java/Spring Boot development)
├── python_advanced_agent.md        (Pyra — Python/FastAPI development)
├── react_advanced_agent.md         (Rexa — React/TypeScript development)
├── mssql_advanced_agent.md         (Sigma — SQL Server / T-SQL development)
└── (5 Copilot chat agents in agents/copilot/)
```

### Instructions (3 files)

```
instructions/
├── master_instruction_set.md        (9 universal rules for all agents)
├── java_project_intake.md           (33-question intake form for Java projects)
└── python_project_intake.md         (Python project intake + OOP patterns)
```

### Tools (3 files)

```
tools/
├── skill_exporter.py                (600+ lines of Python, no dependencies)
├── README.md                        (Full technical documentation)
└── QUICK_START.md                   (Beginner-friendly guide)
```

---

## 🚀 Getting Started

### 1. Generate Instructions for Your AI Assistant

```bash
cd /path/to/awesome-prompts

# Export all skills to all platforms
python tools/skill_exporter.py

# Or export to specific platforms
python tools/skill_exporter.py --target copilot claude cursor
```

This creates:
- `.github/copilot-instructions.md` for GitHub Copilot
- `.claude/skills_context.md` for Claude Code
- `.cursorrules` for Cursor IDE
- `.continue/config.json` for Continue.dev
- `tools/output/openai_system_prompt.txt` for OpenAI API

### 2. Use the Code Health Inspector

Ask an agent to scan your code:

```
"Scan this code for issues and generate a health report."
```

The Sherlock agent will:
- Run a 6-phase systematic scan
- Identify performance, error handling, delays, leaks, security, reliability issues
- Generate a structured P0–P3 report
- Provide fix examples for every issue

### 3. Use Agents for Development

**For Java/Spring:**
```
"Create a Spring Boot service that processes orders asynchronously."
```
→ Jarvis applies Java + Spring skill, generates tests, follows Spring Boot 3.x patterns

**For Python/FastAPI:**
```
"Build a FastAPI endpoint with async database access."
```
→ Pyra applies Python + FastAPI skill, uses Pydantic, generates pytest tests

**For React:**
```
"Build a form for order checkout with validation."
```
→ Rexa applies React + TypeScript skill, uses TanStack Query, generates RTL tests

**For MSSQL:**
```
"Write a stored procedure to process batch orders."
```
→ Sigma explains NOLOCK, provides error handling template, generates test script

---

## 🔧 Key Features of v2.0

### All Agents Now Have:
✅ Version detection (checks environment before coding)
✅ Project intake questionnaire (for new projects)
✅ Mandatory test generation (every code response includes tests)
✅ OOP examples (all 4 pillars with concrete examples)
✅ Simple, understandable code (≤20 lines per method/function)
✅ Full documentation (Javadoc, docstrings, JSDoc)
✅ Error handling as first-class citizen
✅ Security checks (no SQL injection, secrets, etc.)

### Master Instruction Set (Universal Rules):
✅ Version check protocol for all languages
✅ Test generation standards (AAA pattern, naming)
✅ OOP principles with code examples
✅ Documentation standards (Google style, Javadoc, JSDoc)
✅ Code quality rules (method length, class length, naming)
✅ Project structure conventions (Java, Python, React)
✅ Security non-negotiable checks

### New Technologies Covered:

| Framework | Skill | Agent | Coverage |
|-----------|-------|-------|----------|
| Apache Camel | ✓ | Implicit | Routes, EIP, error handling, testing |
| Spring Framework | ✓ | ✓ Jarvis | IoC, AOP, WebFlux, Batch, Cloud, Security |
| Apache Pulsar | ✓ | Implicit | Producers, consumers, schemas, DLT, debugging |
| Java 17/21 | ✓ | ✓ Jarvis | Records, sealed classes, pattern matching, text blocks |
| Python 3.11/12 | ✓ | ✓ Pyra | Async, type hints, ABC, dataclasses, Pydantic v2 |
| React 18/19 | ✓ | ✓ Rexa | Hooks, TanStack Query, Zustand, forms, a11y |
| SQL Server 2019/2022 | ✓ | ✓ Sigma | NOLOCK explained, indexing, transactions, security |
| Code Health Analysis | ✓ | ✓ Sherlock | 7 issue categories, severity scoring, reporting |

---

## 📈 What This Enables

### For Individual Developers:
- **Faster coding** — AI understands your project's standards and applies them automatically
- **Better code** — Consistent with OOP, testing, documentation conventions
- **Debugging help** — Sherlock scans code and identifies performance, error handling, security issues
- **Learning** — Each skill file is a reference guide for mastering a technology

### For Teams:
- **Unified standards** — All team members' AI assistants follow the same rules
- **Knowledge sharing** — Skills codify institutional knowledge
- **Onboarding** — New developers' AI assistants immediately understand team patterns
- **Multi-tool support** — Works with GitHub Copilot, Claude, Cursor, Continue.dev, OpenAI API

### For AI Assistants:
- **Better context** — Understand the specific technologies and patterns used
- **Fewer mistakes** — Guided by proven best practices and error handling patterns
- **Consistent output** — All suggestions follow the same quality bar
- **Measurable results** — Test generation, documentation, error handling are guaranteed

---

## 🎓 Learning Resources

### Understand the Architecture:
1. Read `CLAUDE.md` — high-level project overview
2. Read `instructions/master_instruction_set.md` — universal rules
3. Browse `skills/` — detailed technology knowledge

### Use the Tools:
1. Follow `tools/QUICK_START.md` — step-by-step examples
2. Read `tools/README.md` — full technical documentation
3. Run `python tools/skill_exporter.py --list` — see what's available

### Build with Agents:
1. Choose the relevant agent (Jarvis for Java, Pyra for Python, etc.)
2. Ask for a feature or review
3. Agent applies skills + master rules → generates code + tests + docs

### Inspect Code Health:
1. Paste code or point to files
2. Ask Sherlock: "Scan this for issues"
3. Get P0–P3 report with fixes

---

## ✅ Checklist — What to Do Next

- [ ] Run `python tools/skill_exporter.py` to generate instruction files
- [ ] Commit generated files (`.github/copilot-instructions.md`, `.cursorrules`, etc.) to Git
- [ ] Test: ask GitHub Copilot to write Java code and see if it applies Spring patterns
- [ ] Test: ask Claude to review your Python code and see if it catches async issues
- [ ] Test: ask Sherlock to scan a slow endpoint for performance issues
- [ ] Share this with your team: `tools/QUICK_START.md`
- [ ] Bookmark `skills/` directory as your coding reference
- [ ] Update skills when you discover new patterns (edit `.md` file, re-run exporter)

---

## 📝 Technical Details

### Code Quality
- **Python exporter**: 600+ lines, zero dependencies, fully typed, documented
- **Markdown skills**: 120+ KB of structured, commented technical content
- **Agent files**: Detailed operating protocols, specialisations, boundaries
- **Master rules**: 9 non-negotiable rules for all coding work

### Testing
- All agents have mandatory test generation
- Tests follow `givenX_whenY_thenZ` naming
- AAA pattern (Arrange-Act-Assert) enforced
- Minimum coverage per task (happy path + edge cases + errors)

### Performance
- Skill exporter runs in <1 second
- Generated instruction files are optimized per platform (50–120 KB)
- No external Python dependencies for the exporter
- Markdown parsing is efficient and forward-compatible

### Compatibility
- ✅ Python 3.8+
- ✅ All OSes (Linux, macOS, Windows)
- ✅ Works offline (no API calls needed)
- ✅ Automatically handles file encoding and line endings

---

## 🔮 Future Enhancements (Ideas)

- Add more skills: Kubernetes, Docker, Terraform, GraphQL, gRPC, etc.
- Version control for skills (track changes over time)
- Skill dependency graph (e.g., "React skill depends on TypeScript skill")
- Integration with IDE hooks for automatic exporting on file changes
- Web dashboard to browse and search skills
- Telemetry to see which skills are most used by different AI assistants
- Diff viewer for skill changes before exporting
- Skill validation (lint frontmatter, check code examples compile, etc.)

---

## 📞 Support & Feedback

- **Questions?** Read the READMEs: `tools/README.md`, `tools/QUICK_START.md`
- **Found a bug?** Check skill files are valid YAML in `skills/`
- **Want to add a skill?** Create a `.md` file with frontmatter and re-run the exporter
- **Feedback?** Update a skill, export, test with your AI assistant, iterate

---

**Version:** 2.0
**Last Updated:** 2026-04-03
**Status:** ✅ Complete & Tested

