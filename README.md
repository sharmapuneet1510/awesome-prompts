# 🤖 Awesome Prompts — AI-Driven Development System

> **Enterprise-grade AI agents + reusable skills for autonomous code generation, comprehensive testing, and auto-documentation across Java, Python, React, and TypeScript.**

[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square)]()
[![Version](https://img.shields.io/badge/Version-4.1.0-blueviolet?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)]()
[![Last Updated](https://img.shields.io/badge/Updated-May%202026-blueviolet?style=flat-square)]()

Compatible with: **Claude Code** • **GitHub Copilot** • **Cursor** • **Windsurf** • **VS Code** • **Gemini CLI** • **Continue.dev** • **OpenAI** • **Aider**

---

## 🎯 What This Is

**Awesome Prompts** is a comprehensive system of **5 AI agents** + **7 reusable skills** that transform requirements into production-ready code with:

✅ **100% test coverage** — Unit, integration, and E2E tests  
✅ **Complete documentation** — JSDoc, docstrings, Javadoc (auto-generated)  
✅ **JIRA integration** — Fetch requirements, validate acceptance criteria  
✅ **Business validation** — Ensure tests verify real requirements, not just code  
✅ **Multi-tech support** — Java, Python, React, TypeScript, Node.js  
✅ **Auto-context generation** — architecture.md, context.json, interactive visualization  
✅ **Autonomous orchestration** — Build complete systems (DB + API + UI + tests)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       User Requirement                           │
│         (Free text / JIRA / File / Auto-detect)                │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
        ┌────────────────────────────────────┐
        │  Implementation Agent v3.0         │
        │  Full-Lifecycle Feature Builder    │
        │  • Gather requirements             │
        │  • Detect tech stack               │
        │  • Generate code + tests + docs    │
        └────────────────────────────────────┘
                         ↓
        ┌────────────────────────────────────┐
        │ Code Documentation Skill v1.0      │
        │ (JSDoc/docstrings/Javadoc)        │
        │ • 100% method coverage             │
        │ • Parameters + returns + examples  │
        │ • Business requirement links       │
        └────────────────────────────────────┘
                         ↓
        ┌────────────────────────────────────┐
        │ Test Case Generator Agent v1.0     │
        │ 100% Coverage + Business Validation│
        │ • Unit + integration + E2E tests   │
        │ • JIRA acceptance criteria check   │
        │ • Auto-documented test methods     │
        └────────────────────────────────────┘
                         ↓
        ┌────────────────────────────────────┐
        │   Code Review Agent v2.0           │
        │   Quality + Security + Patterns    │
        │   • SOLID principles enforcement   │
        │   • Performance analysis           │
        │   • Documentation validation       │
        └────────────────────────────────────┘
                         ↓
        ┌────────────────────────────────────┐
        │ Autonomous Dev Agent v1.0          │
        │ Full-Stack Orchestrator            │
        │ • DB + Backend + Frontend + Tests  │
        │ • Knowledge graph generation       │
        │ • GitHub PR creation               │
        └────────────────────────────────────┘
                         ↓
              ✅ PRODUCTION-READY CODE
         (Code + 100% Tests + Documentation + Context)
```

---

## 📦 Core Components

### **5 AI Agents**

| Agent | Purpose | Input | Output | Coverage |
|-------|---------|-------|--------|----------|
| **Implementation** | Build features end-to-end | Requirement | Code + tests + docs | Full lifecycle |
| **Test Generator** | Generate 100% coverage tests | Code files + test type | Comprehensive test suite | 100% coverage |
| **Code Review** | Analyze design + quality | Source code | Issues + severity + fixes | Design + perf + security |
| **Writer** | Auto-generate documentation | Code files | JSDoc/docstrings/Javadoc | 100% APIs |
| **Autonomous Dev** | Orchestrate full projects | Requirement | Complete system | DB + API + UI + tests |

### **7 Reusable Skills**

| Skill | Purpose | Tech Stack | Used By |
|-------|---------|-----------|---------|
| **code_documentation** | JSDoc/docstrings/Javadoc | JS/TS/Python/Java | All agents |
| **database** | SQL schema + migrations | PostgreSQL/MySQL | Autonomous Dev |
| **backend** | REST APIs + services | FastAPI/Spring Boot | Implementation + Autonomous |
| **frontend** | React components + hooks | React/TypeScript | Implementation + Autonomous |
| **test** | Test generation | JUnit5/pytest/Jest | Test Generator |
| **context_builder** | Architecture understanding | All stacks | All agents |
| **apache_camel** | Integration patterns | Camel/Java | Integration Agent |

---

## 🚀 Quick Start

### **Option 1: Interactive Setup** (Recommended)

```bash
python tools/exporter.py --interactive

# Asks:
# 1. Project root directory?
# 2. Target platforms? (select multiple)
# 3. Ready to export?
# Result: Creates folder structure in your project and copies files there
```

**What it does:**
- Creates platform-specific folders (`.github/instructions`, `.github/copilot/agents`, etc.)
- Copies skills and agents to your target project
- Ready to use immediately in your IDE

### **Option 2: In Claude Code / Copilot**

```
"Implement user registration with email validation"
↓
→ Requirement input
→ Code generation
→ Test generation (100% coverage)
→ Auto-documentation
→ Git commit
```

### **Option 3: JIRA-Driven Development**

```
"Generate tests for AUTH-789"
↓
→ Fetch JIRA ticket
→ Extract acceptance criteria
→ Plan test cases (mapped to criteria)
→ Validate all criteria tested
→ 100% coverage + business validated
```

---

## 📋 Complete Workflows

### **Workflow 1: Feature Implementation** (Code + Tests + Docs)

```
User Request:
  "Build password reset feature with email sending"
              ↓
Implementation Agent (7 steps):
  1. STEP 0: Gather requirement (free text)
  2. STEP 1: Load context (detect Python + FastAPI)
  3. STEP 2: Confirm requirement
  4. STEP 3: Plan (email service + reset flow)
  5. STEP 4: Apply backend_skill
  6. STEP 5-6: Implement + test with pytest
  7. STEP 7: Apply code_documentation_skill
              ↓
Output:
  ✅ routes/reset_password.py
  ✅ services/email_service.py
  ✅ test_reset_password.py (100% coverage)
  ✅ Docstrings on all methods
  ✅ Git commit: "feat: add password reset with email"
```

### **Workflow 2: Test Generation** (100% Coverage + Business Validation)

```
User Request:
  "Generate tests for AUTH-789"
              ↓
Test Case Generator (10 steps):
  1. STEP 0: Fetch JIRA AUTH-789
  2. STEP 1: Test type = unit + integration
  3. STEP 2-3: Analyze LoginService code
  4. STEP 4: Plan 8 test cases
  5. STEP 5-6: Generate JUnit5 tests
  6. STEP 7: Document with JSDoc
  7. STEP 8: Validate all 4 acceptance criteria covered ✓
  8. STEP 9: Run tests (all 8 pass)
  9. STEP 10: Commit
              ↓
Output:
  ✅ LoginServiceTest.java (8 tests)
  ✅ 100% line coverage
  ✅ All 4 JIRA criteria tested
  ✅ JSDoc on every test method
  ✅ Coverage report with business validation
  ✅ Git commit: "test: add AUTH-789 tests (4/4 criteria)"
```

### **Workflow 3: Full-Stack Generation** (DB + API + UI + Tests)

```
User Request:
  "Build e-commerce shopping cart with checkout"
              ↓
Autonomous Dev Agent (14 steps):
  1. Parse requirements
  2. Build context (architecture.md, context.json)
  3. Generate task specs (01-05)
  4. Execute sequentially:
     • Task 01: Database schema (PostgreSQL)
     • Task 02: Cart API (FastAPI routes)
     • Task 03: Checkout UI (React components)
     • Task 04: Integration tests
     • Task 05: Deployment config
  5. Apply code_documentation_skill (final pass)
  6. Create GitHub PR
              ↓
Output:
  ✅ Database migrations + schema
  ✅ REST API endpoints (CRUD operations)
  ✅ React UI (cart, checkout, forms)
  ✅ 40+ tests (unit + integration + E2E)
  ✅ JSDoc/docstrings on all code
  ✅ Architecture visualization (design.html)
  ✅ GitHub PR ready for review
```

---

## 📁 Directory Structure

```
awesome-prompts/
├── agents/                              # AI agent definitions
│   ├── implementation_agent.md           # Full-lifecycle feature builder
│   ├── test_case_generator_agent.md      # 100% coverage test generation
│   ├── code_review_agent.md              # Code quality + security
│   ├── writer_agent.md                   # Auto-generate documentation
│   ├── integration_agent.md              # CI/CD + DevOps
│   ├── context/
│   │   └── context_builder_agent.md      # Interactive project analysis
│   ├── autonomous/
│   │   └── autonomous_dev_agent.md       # Full-stack orchestrator
│   └── README.md                         # Agent reference guide
│
├── skills/                              # Reusable implementation skills
│   ├── code_documentation_skill.md       # JSDoc/docstrings/Javadoc (NEW)
│   ├── database_skill.md                 # SQL schema + migrations
│   ├── backend_skill.md                  # REST API generation
│   ├── frontend_skill.md                 # React component generation
│   ├── test_skill.md                     # Test case generation
│   ├── context_builder_skill.md          # Architecture scanning
│   ├── spring_advanced_skill.md          # Spring Boot patterns
│   └── apache_camel_skill.md             # Integration patterns
│
├── instructions/                        # Universal rules for all agents
│   ├── master_instruction_set.md         # Non-negotiable standards
│   ├── java_project_intake.md            # Java-specific questions
│   └── python_project_intake.md          # Python-specific questions
│
├── tools/                               # Python utilities
│   ├── exporter.py                      # Export to 8 platforms
│   ├── requirement_parser.py             # Parse requirements
│   ├── context_builder.py                # Build project context
│   ├── task_generator.py                 # Create task specs
│   ├── graphify_integrator.py            # Knowledge graphs
│   ├── github_sync.py                    # GitHub PR creation
│   ├── generate_design_html.py           # Interactive visualization
│   └── update_checker.py                 # Auto-update checker
│
├── docs/                                # Documentation
│   ├── requirement_input_guide.md        # How to provide requirements
│   ├── AUTONOMOUS_DEVELOPER_README.md    # Full system overview
│   ├── superpowers/specs/                # Design specifications
│   └── superpowers/plans/                # Implementation plans
│
├── AUTONOMOUS_DEVELOPER_README.md        # v3.0 system overview
├── README.md                             # This file
└── CLAUDE.md                             # Project-specific instructions
```

---

## 🛠️ Tech Stack Support

| Layer | Technologies | Test Framework | Documentation |
|-------|--------------|----------------|-------------|
| **Backend** | Java, Python, Node.js | JUnit5, pytest, Jest | Javadoc, docstrings, JSDoc |
| **Frontend** | React, Vue, Angular | Jest, React Testing Library | JSDoc, TypeScript types |
| **Database** | PostgreSQL, MySQL, MongoDB | Integration tests | Schema docs |
| **Testing** | Unit, Integration, E2E | All frameworks | Test documentation |

---

## ✨ Key Features

### **1. Intelligent Requirement Gathering**
- Free text input with AI parsing
- JIRA ticket fetching (via MCP)
- Requirement file parsing (.md, .txt, .yaml)
- Auto-detect from project root

### **2. Full-Lifecycle Development**
- **Create** — Generate production code
- **Test** — 100% coverage with business validation
- **Document** — Auto-generate JSDoc/docstrings/Javadoc
- **Commit** — Clear git messages with references

### **3. Business Requirement Validation**
- JIRA integration for acceptance criteria
- Test coverage mapping (3/4 criteria tested?)
- Business commentary in code
- Validation reports

### **4. Professional Documentation**
- JSDoc for JavaScript/TypeScript
- Google docstrings for Python
- Javadoc for Java
- Examples + edge cases + performance notes

### **5. Context Generation**
- architecture.md with Mermaid diagrams
- context.json (machine-readable)
- tech-stack.md with skill mappings
- design.html (interactive visualization)

### **6. Multi-Platform Export**
- Claude Code, Copilot, Cursor, Windsurf, VS Code, Gemini, Continue, OpenAI, Aider

---

## 📊 Quality Standards

| Metric | Standard | Status |
|--------|----------|--------|
| **Test Coverage** | 95%+ | ✅ Automated |
| **Documentation** | 100% APIs | ✅ Auto-generated |
| **Code Quality** | SOLID + Design Patterns | ✅ Validated |
| **Security** | Input validation + SQL injection prevention | ✅ Built-in |
| **Performance** | <100ms endpoints | ✅ Verified |
| **Accessibility** | WCAG 2.1 AA | ✅ Checked |

---

## 🎓 Examples

### Example 1: Login Feature with Tests
```
User: "Build JWT login endpoint"
Output:
  ✅ LoginController (Spring Boot)
  ✅ LoginService (Business logic)
  ✅ 8 JUnit5 tests (100% coverage)
  ✅ Javadoc on all methods
  ✅ Error handling + validation
```

### Example 2: JIRA-Driven Tests
```
User: "Generate tests for AUTH-456"
→ Fetch JIRA (4 acceptance criteria)
→ Plan 8 test cases
→ Generate pytest tests
→ Validate all 4 criteria tested
Output: 100% coverage + business validated
```

### Example 3: React Component with Tests
```
User: "Build LoginForm component"
Output:
  ✅ LoginForm.tsx (React + TypeScript)
  ✅ LoginForm.test.tsx (Jest + RTL)
  ✅ JSDoc on all methods
  ✅ 85%+ component coverage
  ✅ Accessibility verified (A11Y)
```

---

## 🔧 Installation & Setup

### Requirements
- Python 3.9+ (auto-detected: works with `python` or `python3`)
- Node.js 16+ (for JavaScript projects)
- Java 17+ (for Java projects)

### Quick Start

```bash
# Clone
git clone https://github.com/sharmapuneet1510/awesome-prompts.git
cd awesome-prompts

# Install dependencies
pip install -r requirements.txt

# Interactive setup (recommended)
# Creates folder structure in your project, copies files there
# Works on Windows, Linux, macOS
python tools/exporter.py --interactive

# Alternative on systems with python3
python tools/exporter.py --interactive
```

### Alternative: Direct Export

```bash
# Export to specific project directory with platform choice
python tools/exporter.py --target-project /path/to/your/project --target copilot

# Export to Claude Code (creates .claude/skills/, .claude/agents/)
python tools/exporter.py --target-project /path/to/your/project --target claude

# Export to all platforms
python tools/exporter.py --target-project /path/to/your/project --target copilot claude cursor windsurf
```

### Python Detection

The exporter automatically detects your Python installation:
- **Linux/macOS:** Tries `python3` first, then `python`
- **Windows:** Tries `python`, `python3`, then `py` launcher

**Check your Python setup:**
```bash
# See which Python version is available
python --version
# OR
python3 --version
```

**Platform Options:**
- `claude` → `.claude/skills/`, `.claude/agents/`
- `copilot` → `.github/instructions/`, `.github/copilot/agents/`
- `cursor` → `.cursor/rules/`, `.cursor/rules/agents/`
- `windsurf` → `.windsurf/rules/`, `.windsurf/rules/agents/`
- `gemini` → `.gemini/skills/`, `.gemini/agents/`
- `continue` → `.continue/prompts/`, `.continue/prompts/agents/`
- `openai` → `tools/output/openai/skills/`, `tools/output/openai/agents/`
- `aider` → `.aider/skills/`, `.aider/agents/`

---

## 📚 Documentation

**Quick Links:**
- [Requirement Input Guide](./docs/requirement_input_guide.md) — How to provide requirements
- [Autonomous Developer Guide](./AUTONOMOUS_DEVELOPER_README.md) — Full system overview
- [Agent Reference](./agents/README.md) — All agents explained
- [Implementation Agent](./agents/implementation_agent.md) — Feature builder guide
- [Test Case Generator](./agents/test_case_generator_agent.md) — 100% coverage testing
- [Code Documentation Skill](./skills/code_documentation_skill.md) — Auto-documentation

---

## 🌟 What's New in v4.1.0

✨ **NEW: Test Case Generator Agent**
- Generate 100% coverage tests (unit, integration, E2E)
- JIRA acceptance criteria validation
- Auto-documented test methods

✨ **NEW: Code Documentation Skill**
- JSDoc/docstrings/Javadoc auto-generation
- 100% method documentation
- Business requirement links

✨ **RENAMED: Developer Agent → Implementation Agent**
- Clearer scope (code + test + docs)
- Full-lifecycle feature builder

✨ **UPDATED: All Agents**
- Now use code_documentation_skill
- Improved documentation workflows
- Better quality gates

---

## 🚀 Get Started in 3 Steps

### Step 1: Provide Requirement
```
"Build user registration with email validation and tests"
```

### Step 2: Implementation Agent Generates
```
✅ Code (routes, models, services)
✅ Tests (100% coverage)
✅ Documentation (JSDoc/docstrings)
✅ Git commit
```

### Step 3: Deploy & Review
```
✅ All tests passing
✅ 100% documented
✅ Ready for production
```

---

## 📞 Support & Links

| Link | Purpose |
|------|---------|
| [GitHub Issues](https://github.com/sharmapuneet1510/awesome-prompts/issues) | Report bugs |
| [GitHub Discussions](https://github.com/sharmapuneet1510/awesome-prompts/discussions) | Ask questions |
| [Email](mailto:puneet@techmavericks.dev) | Direct contact |
| [LinkedIn](https://linkedin.com/in/sharmapuneet1510) | Connect |
| [Tech Mavericks](https://techmavericks.dev) | Newsletter |

---

<div align="center">

**Architecting intelligence into development. One agent at a time.**

🚀 **v4.1.0** • **May 2026** • **Production Ready**

[⭐ Star on GitHub](https://github.com/sharmapuneet1510/awesome-prompts) | [📖 Read Docs](./docs/) | [🎯 Get Started](./AUTONOMOUS_DEVELOPER_README.md)

</div>
