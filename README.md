# Awesome Prompts — Enterprise-Grade AI Coding Assistant Repository

A comprehensive, production-ready collection of **AI agent definitions**, **coding skills**, and **prompt templates** for software engineering workflows. Compatible with GitHub Copilot, Claude, Cursor IDE, Continue.dev, and OpenAI API.

**Status:** ✅ Complete & Shareable | 18 Skills | 4 Agent Roles | 5 Platform Exports | Zero Dependencies

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

### Skills (18 total, 312 KB)

Advanced knowledge modules covering:

**API & Backend:**
- `rest_api_java_skill.md` — Spring Boot REST patterns
- `rest_api_python_skill.md` — FastAPI patterns
- `spring_advanced_skill.md` — Spring Framework internals
- `apache_camel_skill.md` — Integration & routing
- `apache_pulsar_skill.md` — Messaging & streaming

**Language Standards:**
- `java_advanced_skill.md` — Java 17+ patterns
- `python_advanced_skill.md` — Python 3.11+ patterns
- `react_advanced_skill.md` — React 18+ patterns
- `mssql_advanced_skill.md` — T-SQL & indexing

**Testing & Quality:**
- `testing_junit5_skill.md` — JUnit5 with Mockito
- `testing_pytest_skill.md` — pytest with fixtures
- `testing_react_skill.md` — React Testing Library
- `code_health_skill.md` — Quality inspection taxonomy

**Code Standards:**
- `error_handling_skill.md` — Exception patterns
- `camel_exception_handling_skill.md` — Camel error routes
- `code_formatting_skill.md` — Formatting standards
- `documentation_skill.md` — Javadoc/docstrings/JSDoc
- `sonarqube_vulnerability_skill.md` — Security & OWASP Top 10

### Agents (11 total, organized by role)

**Developer Agents** (agents/developer/)
- `java_advanced_agent.md` (Jarvis)
- `python_advanced_agent.md` (Pyra)
- `react_advanced_agent.md` (Rexa)
- `mssql_advanced_agent.md` (Sigma)
- `jira_implementation_agent.md`

**Reviewer Agents** (agents/reviewer/)
- `code_health_inspector_agent.md` (Sherlock)
- `code_review_agent.md`
- `git-review-2.md`

**Writer Agents** (agents/writer/)
- `jira_documentation_agent.md`

**Integration Agents** (agents/integration/)
- `jira_mr_sync_review.agent.md`

### Instructions (3 files)

Universal rules all agents follow:
- `instructions/master_instruction_set.md` — 9 non-negotiable rules
- `instructions/java_project_intake.md` — 33-question Java/Spring intake
- `instructions/python_project_intake.md` — Python project setup guide

### Tools

**Skill Exporter** (`tools/skill_exporter.py`)
- Exports all skills to 5 platforms in one command
- Validates skills before export
- Supports filtering by skill/target

**Skill Validator** (`tools/skill_validator.py`)
- Enforces YAML frontmatter correctness
- Checks required fields, markdown structure, naming
- Guard rail for code quality

**Code Block Fixer** (`tools/fix_code_blocks.py`)
- Adds language tags to code blocks
- Infers language intelligently
- Ensures markdown compliance

---

## 🚀 Quick Start

### 1. Export Skills to Your Platform

```bash
# Export all 18 skills to all 5 platforms
python3 tools/skill_exporter.py

# Or to one platform
python3 tools/skill_exporter.py --target copilot claude cursor
```

This generates:
- `.github/copilot-instructions.md` (GitHub Copilot)
- `.claude/skills_context.md` (Claude)
- `.cursorrules` (Cursor IDE)
- `.continue/config.json` (Continue.dev)
- `tools/output/openai_system_prompt.txt` (OpenAI API)

### 2. Use with Your AI Assistant

**GitHub Copilot** — Automatically reads `.github/copilot-instructions.md`

**Claude** — Reference in conversation: "Use the skills from `.claude/skills_context.md`"

**Cursor** — Automatically loads `.cursorrules`

**Continue.dev** — Automatically reads `.continue/config.json`

**OpenAI API** — Copy `tools/output/openai_system_prompt.txt` to API calls

### 3. Ask for Code

```
"Use Jarvis to create a Spring Boot REST API for orders with proper error handling"
→ Generates code with:
  - Spring Boot 3.x patterns
  - Constructor injection
  - DTO validation
  - Global error handler
  - JUnit5 tests
  - Javadoc docs
```

---

## 📁 Directory Structure

```
awesome-prompts/
├── agents/                           ← AI agents organized by role
│   ├── developer/                    ← Code generation (Jarvis, Pyra, Rexa, Sigma)
│   ├── reviewer/                     ← Code quality (Sherlock, Code Reviewer)
│   ├── writer/                       ← Documentation (Documentarian)
│   ├── integration/                  ← CI/CD (Orchestrator)
│   └── README.md                     ← Agent guide
│
├── skills/                           ← Reusable knowledge modules (18 total)
│   ├── rest_api_java_skill.md
│   ├── rest_api_python_skill.md
│   ├── error_handling_skill.md
│   ├── testing_*.md                  ← 3 testing skills
│   ├── code_formatting_skill.md
│   ├── documentation_skill.md
│   ├── sonarqube_vulnerability_skill.md
│   └── ... (more skills)
│
├── instructions/                     ← Universal rules & intake forms
│   ├── master_instruction_set.md     ← 9 rules all agents follow
│   ├── java_project_intake.md        ← 33-question intake form
│   └── python_project_intake.md      ← Python intake form
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
│   ├── skill_exporter.py             ← Export to 5 platforms
│   ├── skill_validator.py            ← Validate skills
│   ├── fix_code_blocks.py            ← Fix markdown
│   └── output/                       ← Generated files
│
├── .github/copilot-instructions.md   ← (Generated by exporter)
├── .claude/skills_context.md         ← (Generated by exporter)
├── .cursorrules                      ← (Generated by exporter)
├── .continue/config.json             ← (Generated by exporter)
│
├── CLAUDE.md                         ← This repo's own instructions
├── .gitignore                        ← Git exclusions
└── README.md                         ← This file
```

---

## 🎓 Agent Usage Examples

### Ask Jarvis (Java Developer)

```
"Create a Spring Boot service that processes orders asynchronously"

Jarvis will generate:
✓ Spring Boot 3.x REST controller
✓ Service layer with Spring transactions
✓ JPA/Hibernate entity mappings
✓ Constructor injection (no autowired fields)
✓ @Valid request validation
✓ Global error handler
✓ Async @Transactional methods
✓ JUnit5 tests with Mockito
✓ Full Javadoc documentation
```

### Ask Sherlock (Code Inspector)

```
"Scan this service for performance issues"

Sherlock will:
✓ Analyze 6 phases: structure → performance → errors → delays → memory/sec/reliability
✓ Identify N+1 queries, blocking calls, missing indexes
✓ Find swallowed exceptions, missing error handlers
✓ Detect async bottlenecks
✓ Generate P0-P3 severity report
✓ Suggest fixes with code examples
```

### Ask Pyra (Python Developer)

```
"Build a FastAPI endpoint with async database access"

Pyra will generate:
✓ FastAPI app with dependency injection
✓ Pydantic request/response schemas
✓ Async SQLAlchemy with selectinload
✓ Error handling with custom exceptions
✓ Input validation with field constraints
✓ pytest tests with fixtures
✓ Type hints throughout
✓ Docstrings in Google style
```

---

## ✨ Key Features

### All Agents Follow Master Rules

Every agent applies these 9 principles:

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

- **Java** — Spring Boot 3.x, JUnit5, Maven/Gradle
- **Python** — FastAPI, pytest, asyncio, Pydantic v2
- **React** — React 18+, TypeScript, TanStack Query
- **SQL Server** — T-SQL, DMVs, indexing strategies
- **Apache** — Camel, Pulsar, Kafka patterns

### Platform Compatibility

| Platform | Format | Auto-Load | File |
|----------|--------|-----------|------|
| GitHub Copilot | Markdown | ✅ Yes | `.github/copilot-instructions.md` |
| Claude Code | Markdown | ⚠️ Manual ref | `.claude/skills_context.md` |
| Cursor IDE | Markdown | ✅ Yes | `.cursorrules` |
| Continue.dev | JSON | ✅ Yes | `.continue/config.json` |
| OpenAI API | Plain text | Manual | `tools/output/openai_system_prompt.txt` |

---

## 🔒 Git-Ready & Shareable

✅ **No secrets** — All examples use safe patterns
✅ **No generated code** — Skills are templates, not output
✅ **Small footprint** — 312 KB of knowledge, not build artifacts
✅ **Clean .gitignore** — Excludes only cache, IDE settings, secrets
✅ **Documented structure** — Every directory has README.md
✅ **Validated** — skill_validator.py ensures quality
✅ **No external dependencies** — Pure Python tools, no npm/pip install needed

```bash
# Clone and use immediately
git clone <repo>
cd awesome-prompts
python3 tools/skill_exporter.py
# Done! Ready to commit
```

---

## 🛠 Tools Usage

### Validate All Skills

```bash
python3 tools/skill_validator.py
# Output: 18 valid ✓ | 0 errors | 0 warnings
```

### Export to Specific Platforms

```bash
# Just Copilot and Claude
python3 tools/skill_exporter.py --target copilot claude

# Just Java and Spring skills
python3 tools/skill_exporter.py --skills java,spring

# Dry run (no write)
python3 tools/skill_exporter.py --dry-run
```

### Fix Code Blocks

```bash
python3 tools/fix_code_blocks.py
# Automatically adds language tags to all code blocks
```

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Skills | 18 |
| Agents | 11 |
| Agent Roles | 4 (Developer, Reviewer, Writer, Integration) |
| Platform Exports | 5 |
| Code Examples | 200+ |
| Total Knowledge | 312 KB (skills) |
| Total Exports | 908.6 KB |
| Validation Status | ✅ 18/18 valid |
| Lines of Code in Tools | 1000+ |
| Dependencies | 0 |

---

## 🚀 Next Steps

1. **Clone the repo** — `git clone <repo>`
2. **Export to your platform** — `python3 tools/skill_exporter.py`
3. **Commit & push** — Everything is git-ready
4. **Share with your team** — Send them this README
5. **Ask your AI assistant** for code — It will apply the skills
6. **Update skills** — Edit `.md` files and re-export anytime

---

## 📖 Documentation

- **[CLAUDE.md](CLAUDE.md)** — Repository instructions for Claude Code
- **[agents/README.md](agents/README.md)** — Detailed agent guide
- **[instructions/master_instruction_set.md](instructions/master_instruction_set.md)** — Universal rules
- **[tools/README.md](tools/README.md)** — Skill exporter documentation
- **[tools/QUICK_START.md](tools/QUICK_START.md)** — Quick reference guide

---

## 💡 Tips

1. **Start with agents/README.md** — Understand each agent's role
2. **Read skills you'll use** — Skills are learning resources, not just for AI
3. **Validate before committing** — `python3 tools/skill_validator.py`
4. **Re-export after updates** — Edit skills, then `python3 tools/skill_exporter.py`
5. **Add to CI/CD** — Run validation in GitHub Actions before merge

---

## 📝 License

This repository is **sharable**, **reusable**, and **open for teams**.

---

## 🎉 Credits

**Built for:** Enterprise software engineering teams using AI coding assistants

**Tested with:**
- GitHub Copilot (VSCode, GitHub.com)
- Claude (claude.ai, extensions)
- Cursor IDE
- Continue.dev
- OpenAI API (gpt-4, gpt-4-turbo)

---

**Version:** 2.0 Complete
**Last Updated:** 2026-04-03
**Status:** ✅ Production Ready

