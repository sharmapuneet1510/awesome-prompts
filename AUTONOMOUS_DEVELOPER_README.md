# 🤖 Autonomous Developer System

**End-to-end code generation and testing pipeline** that transforms plain-text requirements into production-ready, fully tested code with auto-updating architecture documentation.

## 🎯 Overview

The Autonomous Developer System is a fully autonomous AI-driven development platform that:

- **Reads** plain-text `requirement.txt` files
- **Generates** production-ready code across frontend, backend, and database
- **Tests** everything automatically (Playwright for UI, pytest for Python, JUnit for Java)
- **Documents** architecture and context automatically
- **Tracks** task completion in JSON format
- **Syncs** results to GitHub and Claude Code

```
requirement.txt (plain text)
        ↓
    [Autonomous Developer Orchestrator]
        ↓
┌───────┴───────┬───────────┬───────────┬──────────┐
↓               ↓           ↓           ↓          ↓
Database      Backend     Frontend    Tests    Deployment
Schema        API         UI          & QA     Setup
        ↓               ↓               ↓
    Production-Ready Code + Full Test Coverage + Auto-Docs
```

---

## 📋 System Components

### 1. **Foundation Tools** (PHASE 1)
Parse requirements and understand project context.

- **`requirement_parser.py`** - Converts plain text requirements to structured markdown
- **`project_detector.py`** - Detects new vs existing projects, scans tech stack
- **`context_builder.py`** - Builds JSON context from project structure

### 2. **Task Generation** (PHASE 2)
Break requirements into executable tasks.

- **`task_generator.py`** - Creates 5 task specifications (DB, Backend, Frontend, Tests, Deploy)

### 3. **Core Skills** (PHASE 3)
Specialized code generation skills.

- **`database_skill.md`** - Generates SQL schemas with migrations
- **`backend_skill.md`** - Generates API routes, models, services
- **`frontend_skill.md`** - Generates React components, pages, styling
- **`test_skill.md`** - Generates and runs tests, coverage reports

### 4. **Orchestration** (PHASE 4)
Master agent that coordinates everything.

- **`autonomous_dev_agent.md`** - Main orchestrator agent

### 5. **Integration** (PHASE 5)
Platform integration and tracking.

- **`graphify_integrator.py`** - Knowledge graph generation + token caching
- **`github_sync.py`** - GitHub PR creation
- **`task_tracker.py`** - JSON task completion tracking

---

## 🚀 Quick Start

### Option 1: Interactive Setup (Recommended)

```bash
python3 tools/exporter.py --interactive
```

This will ask you:
1. **Project Root Directory** - Where to set up the system
2. **Target Platforms** - Which platforms you use (Claude, Copilot, Cursor, etc.)
3. **Confirmation** - Review before copying

Then it automatically copies all skills and instructions to your project.

### Option 2: Manual Setup

```bash
# Copy to Claude Code
python3 tools/exporter.py --target claude --all

# Copy to GitHub Copilot
python3 tools/exporter.py --target copilot --all

# Copy to all platforms
python3 tools/exporter.py --all
```

### Option 3: Using the Agent Directly

```bash
# 1. Create a requirement.txt file
cat > requirement.txt << 'EOF'
We need a user authentication system with JWT tokens.
Use React for frontend, Python FastAPI for backend, PostgreSQL for database.
Support login, registration, and profile management.
Timeline: 2 weeks.
EOF

# 2. Invoke the autonomous developer agent
# (In Claude Code or Copilot)
# Type: /autonomous-developer

# 3. Watch it generate code, tests, and documentation automatically
```

---

## 📊 Workflow Diagram

### Complete Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Input: requirement.txt                  │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│         Step 1: Parse Requirements & Generate requirement.md     │
├─────────────────────────────────────────────────────────────────┤
│  • Extract project name, tech stack, features                    │
│  • Generate structured markdown with sections                    │
│  • Output: docs/requirement.md                                   │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│         Step 2: Detect Project & Build Context                  │
├─────────────────────────────────────────────────────────────────┤
│  • Scan for .git repo and existing code                          │
│  • If existing: scan codebase + read docs + analyze git history  │
│  • If new: ask user about tech stack preferences                 │
│  • Output: docs/architecture.md, ._context/context.json          │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│       Step 3: Generate Knowledge Graph (Graphify)                │
├─────────────────────────────────────────────────────────────────┤
│  • Parse codebase structure and dependencies                     │
│  • Build knowledge graph of components                           │
│  • Cache embeddings for token efficiency                         │
│  • Output: ._context/graph.json, embeddings cache               │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│         Step 4: Generate Task Specifications                    │
├─────────────────────────────────────────────────────────────────┤
│  • Create 5 task specs: DB, Backend, Frontend, Tests, Deploy    │
│  • Each task includes requirements, acceptance criteria          │
│  • Output: tasks/01-05/spec.md files                             │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│    Step 5a: Execute Task 01 - Database Schema                   │
├─────────────────────────────────────────────────────────────────┤
│  • Invoke database_skill                                         │
│  • Generate schema.sql + migrations/                             │
│  • Update context.json with table definitions                    │
│  • Output: tasks/01-database-schema/generated/                   │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│    Step 5b: Execute Task 02 - Backend API                       │
├─────────────────────────────────────────────────────────────────┤
│  • Invoke backend_skill (FastAPI or Spring Boot)                │
│  • Generate routes/, models/, services/                          │
│  • Generate unit tests with ≥95% coverage                        │
│  • Update context.json with API endpoints                        │
│  • Output: tasks/02-backend-api/generated/                       │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│    Step 5c: Execute Task 03 - Frontend UI                       │
├─────────────────────────────────────────────────────────────────┤
│  • Invoke frontend_skill (React + TypeScript)                   │
│  • Generate components/, pages/, hooks/                          │
│  • Generate component tests with ≥85% coverage                   │
│  • Responsive design (mobile-first)                              │
│  • Output: tasks/03-frontend-ui/generated/                       │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│    Step 5d: Execute Task 04 - Integration Tests                 │
├─────────────────────────────────────────────────────────────────┤
│  • Invoke test_skill                                             │
│  • Generate E2E tests (Playwright)                               │
│  • Generate integration tests                                    │
│  • Generate coverage reports (target: ≥95%)                      │
│  • Output: tasks/04-integration-tests/generated/                 │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│    Step 5e: Execute Task 05 - Deployment Setup                  │
├─────────────────────────────────────────────────────────────────┤
│  • Create Dockerfile for backend + frontend                      │
│  • Generate docker-compose.yml                                   │
│  • Create GitHub Actions CI/CD workflow                          │
│  • Output: tasks/05-deployment/generated/                        │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 6: Update Architecture & Create GitHub PR                 │
├─────────────────────────────────────────────────────────────────┤
│  • Regenerate architecture.md with all components                │
│  • Update context.json with final state                          │
│  • Create feature branch: feature/auto-generated-YYYY-MM-DD      │
│  • Commit all generated code                                     │
│  • Open PR with detailed summary                                 │
│  • Output: GitHub PR with full context                           │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│   Step 7: Sync to Claude Code & Generate Report                 │
├─────────────────────────────────────────────────────────────────┤
│  • Export skills to .claude/skills/                              │
│  • Export agent to .claude/agents/                               │
│  • Copy task-completion.json to project root                     │
│  • Generate final completion report                              │
│  • Output: Complete autonomous development session               │
└─────────────────────────┬────────────────────────────────────────┘
                         ↓
              ✅ PRODUCTION-READY CODE
         (with tests, docs, and full coverage)
```

---

## 🏗️ Architecture Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Autonomous Developer Agent                 │
│                   (Master Orchestrator)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┬─────────────┐
        ↓            ↓            ↓            ↓             ↓
   ┌────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐  ┌──────────┐
   │Database│  │ Backend  │  │Frontend│  │  Tests   │  │  Arch    │
   │ Skill  │  │  Skill   │  │ Skill  │  │  Skill   │  │  Skill   │
   └────┬───┘  └────┬─────┘  └────┬───┘  └────┬─────┘  └────┬─────┘
        │           │             │           │             │
        ↓           ↓             ↓           ↓             ↓
    schema.sql  routes.py    LoginForm.tsx  tests/      docs/
    migrations  models.py    Dashboard.tsx  coverage/   diagrams/
               services.py   hooks/
```

### Data Flow

```
Input Files                Internal State              Output Files
─────────────              ──────────────              ─────────────

requirement.txt    ───→  requirement.md     ────→  docs/
                         (parsed data)           architecture.md
                              │                  context.json
                              ↓
                        ._context/
                        ├─ context.json
                        ├─ graph.json
                        └─ embeddings/

                              │
                              ↓
                        tasks/01-05/
                        ├─ spec.md
                        └─ generated/
                           ├─ schema.sql
                           ├─ routes/
                           ├─ components/
                           ├─ tests/
                           └─ docker/

                              │
                              ↓
                        task-completion.json  ────→  GitHub PR
                        (json tracking)              Claude Code
```

### Component Interaction

```
┌──────────────────────────────────────────────────────────────┐
│              requirement.txt (User Input)                     │
└────────────────────┬─────────────────────────────────────────┘
                     │
     ┌───────────────▼────────────────┐
     │  RequirementParser             │
     │  • Extract project name        │
     │  • Extract tech stack          │
     │  • Extract features            │
     └───────────────┬────────────────┘
                     │
                     ↓ requirement.md
     ┌───────────────────────────────────────┐
     │  ProjectDetector                      │
     │  • Scan .git                          │
     │  • Find code files                    │
     │  • Detect tech stack                  │
     └───────────────┬───────────────────────┘
                     │
                     ↓ project info
     ┌──────────────────────────────────────┐
     │  ContextBuilder                      │
     │  • Build file structure              │
     │  • Infer API endpoints               │
     │  • Detect database schema            │
     └──────────────────┬───────────────────┘
                        │
                        ↓ context.json
     ┌──────────────────────────────────────┐
     │  GraphifyIntegrator                  │
     │  • Build knowledge graph             │
     │  • Cache embeddings                  │
     └──────────────────┬───────────────────┘
                        │
                        ↓ graph.json
     ┌──────────────────────────────────────┐
     │  TaskGenerator                       │
     │  • Create 5 task specs               │
     │  • Add acceptance criteria           │
     └──────────────────┬───────────────────┘
                        │
        ┌───────────────┼───────────────┬──────────────┬──────────┐
        ↓               ↓               ↓              ↓          ↓
    database_skill  backend_skill  frontend_skill  test_skill  arch_skill
        │               │               │              │          │
        ↓               ↓               ↓              ↓          ↓
    schema.sql     routes.py      LoginForm.tsx    tests/     docs/
    migrations/    models.py      Dashboard.tsx    coverage/  diagrams/
                   services.py    hooks/
        │               │               │              │          │
        └───────────────┼───────────────┴──────────────┴──────────┘
                        │
                        ↓
        task-completion.json (tracking)
                        │
                        ↓
    ┌─────────────────────────────────┐
    │  GitHubSync                     │
    │  • Create feature branch        │
    │  • Commit all code              │
    │  • Open PR                      │
    └─────────────────────────────────┘
```

---

## 📝 How to Use

### 1. **Interactive Setup** (First Time)

```bash
# Run interactive setup
python3 tools/exporter.py --interactive

# Answer the prompts:
# 1. Enter your project root directory: /path/to/your/project
# 2. Select platforms (use space to select multiple):
#    - Claude Code
#    - GitHub Copilot
#    - Cursor
#    - Windsurf
# 3. Confirm and copy

# Result:
# ✅ Skills copied to .claude/skills/, .copilot/skills/, etc.
# ✅ Agent copied to .claude/agents/, .copilot/agents/, etc.
# ✅ Setup complete!
```

### 2. **Provide Requirements (Multiple Ways)**

**Option A: Create a requirement file**

```bash
cat > requirement.txt << 'EOF'
We need a user authentication system with JWT tokens.

Use React 18+ for frontend, Python FastAPI for backend, PostgreSQL for database.

Features:
- User registration with email validation
- User login with JWT tokens
- User profile management
- Activity logging

Security:
- Password hashing with bcrypt
- JWT token expiration (1 hour)
- CORS protection

Timeline: 2 weeks
Team: 1 (autonomous agent)
EOF
```

**Option B: Use free text input**

The agent will ask for requirements interactively:
```
Agent: "How would you like to provide requirements?"
  a) Free text description
  b) JIRA ticket/story
  c) Requirement file
  d) Auto-detect from project

You: "a) Free text"

Agent: "Describe what you want to build..."
```

**Option C: Use JIRA ticket**

```
Agent: "Provide JIRA ticket link or key (e.g., PROJ-123)"

You: "PROJ-123"

Agent: (Fetches JIRA details via MCP integration)
```

**Option D: Let agent auto-detect**

If requirements.md or requirements.txt exists in project root:
```
Agent: "Auto-detect from project"

Agent: (Finds and loads requirements automatically)
```

**For detailed information, see:** [`docs/requirement_input_guide.md`](./docs/requirement_input_guide.md)

### 3. **Invoke the Agent**

**In Claude Code:**
```
Type or paste in Claude Code chat:
/autonomous-developer
```

**In GitHub Copilot:**
```
@autonomous-developer What should we build based on our requirements?
```

**Or run directly:**
```bash
# The agent reads requirement.txt and starts the pipeline
python3 -m autonomous_dev_agent  # (when available)
```

### 4. **Monitor Progress**

Watch the agent:
1. Parse requirements
2. Build context and architecture
3. Generate tasks (5 stages)
4. Execute each task sequentially
5. Create GitHub PR with results
6. Sync to Claude Code

Check `task-completion.json` for detailed status:

```bash
cat task-completion.json | jq '.summary'

# Output:
# {
#   "total_tasks": 5,
#   "completed": 3,
#   "in_progress": 1,
#   "pending": 1,
#   "overall_progress": 60
# }
```

### 5. **Review Generated Code**

```
Generated in these folders:
├─ tasks/01-database-schema/generated/
│  ├─ schema.sql
│  └─ migrations/
├─ tasks/02-backend-api/generated/
│  ├─ routes/
│  ├─ models/
│  └─ services/
├─ tasks/03-frontend-ui/generated/
│  ├─ components/
│  ├─ pages/
│  └─ hooks/
├─ tasks/04-integration-tests/generated/
│  ├─ e2e/
│  ├─ api_integration/
│  └─ coverage/
└─ tasks/05-deployment/generated/
   ├─ docker-compose.yml
   ├─ Dockerfile
   └─ .github/workflows/
```

### 6. **Review GitHub PR**

The agent creates a GitHub PR with:
- Summary of all tasks
- Links to generated files
- Test coverage reports
- Architecture diagrams
- Next steps

---

## 🔧 Configuration

### Default Settings

```python
# Core settings (in agents/autonomous_dev_agent.md)
TASK_EXECUTION: Sequential (one after another)
TEST_COVERAGE_TARGET: 95% overall, 90% per component
BRANCH_NAMING: feature/auto-generated-{YYYY-MM-DD}
AUTO_COMMIT: Yes (after each task)
AUTO_PR: Yes (when all tasks complete)
GRAPHIFY_CACHING: Yes (token optimization)
```

### Customize Tech Stack

Edit `requirement.txt`:
```
# For Java Spring Boot instead of Python:
Use React for frontend, Java Spring Boot for backend

# For MongoDB instead of PostgreSQL:
Use MongoDB for database

# For other stacks:
Use Vue for frontend, Go for backend, etc.
```

---

## 📊 Output Structure

### Generated Files

```
project-root/
├─ requirement.md          # Normalized requirements
├─ docs/
│  ├─ architecture.md      # Auto-generated architecture
│  └─ requirement.md       # (same as root)
├─ ._context/
│  ├─ context.json         # Project context (updated per task)
│  ├─ graph.json           # Knowledge graph
│  └─ graph_embeddings/
│     └─ embeddings.json   # Cached embeddings (for tokens)
├─ tasks/
│  ├─ 01-database-schema/
│  │  ├─ spec.md
│  │  ├─ generated/
│  │  │  ├─ schema.sql
│  │  │  └─ migrations/
│  │  └─ status.json
│  ├─ 02-backend-api/
│  ├─ 03-frontend-ui/
│  ├─ 04-integration-tests/
│  └─ 05-deployment/
└─ task-completion.json    # Overall tracking (JSON)

On GitHub:
├─ feature/auto-generated-2026-05-20  # Branch
├─ Pull Request #1                     # PR with summary
└─ Commits (one per task)
```

### task-completion.json Format

```json
{
  "project": "User Manager",
  "generated_at": "2026-05-20T14:30:00Z",
  "requirement_version": "1.0",
  "tasks": [
    {
      "id": "01-database-schema",
      "status": "completed",
      "started_at": "2026-05-20T14:35:00Z",
      "completed_at": "2026-05-20T14:45:00Z",
      "skill_used": "database_skill",
      "files_generated": ["schema.sql", "migrations/001_init.sql"],
      "test_coverage": 100
    }
  ],
  "summary": {
    "total_tasks": 5,
    "completed": 3,
    "overall_progress": 60
  }
}
```

---

## 🎓 Examples

### Example 1: Simple Todo App

```bash
# Create requirement.txt
cat > requirement.txt << 'EOF'
Todo application with user accounts.
React frontend, FastAPI backend, PostgreSQL database.
Features: Create, read, update, delete todos. User login.
EOF

# Run agent
# Result: Full-stack todo app in 30 minutes with tests
```

### Example 2: E-commerce Platform

```bash
# Create requirement.txt
cat > requirement.txt << 'EOF'
E-commerce platform with products, cart, checkout.
React, Spring Boot, MySQL.
Features: Product catalog, user profiles, order history, payment processing.
Timeline: 3 weeks
EOF

# Run agent
# Result: Complete e-commerce backend + frontend + tests
```

### Example 3: Microservices API

```bash
# Create requirement.txt
cat > requirement.txt << 'EOF'
Microservices API with authentication, users, and products services.
Python FastAPI with JWT auth, PostgreSQL.
Deployed to Docker with Kubernetes ready.
EOF

# Run agent
# Result: Docker-ready microservices with CI/CD
```

---

## 🚨 Troubleshooting

### Issue: "requirement.txt not found"
**Solution:** Create the file in project root before running the agent

### Issue: "Git repo not detected"
**Solution:** The agent creates a new project. It's working as expected.

### Issue: "Tests failing after generation"
**Solution:** Check `task-completion.json` for details, review generated code specs

### Issue: "GitHub PR not created"
**Solution:** Ensure `gh` CLI is installed and authenticated:
```bash
gh auth login
```

---

## 📚 Architecture Diagrams

### MVC Pattern for Generated Projects

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                          │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
         ┌───────────▼──────────────┐
         │   React Frontend         │
         │  ├─ components/          │
         │  ├─ pages/               │
         │  ├─ hooks/               │
         │  └─ services/            │
         └────────────┬─────────────┘
                      │ API calls
         ┌────────────▼──────────────┐
         │  FastAPI/Spring Backend   │
         │  ├─ routes/               │
         │  ├─ models/               │
         │  ├─ services/             │
         │  └─ middleware/           │
         └────────────┬──────────────┘
                      │ SQL
         ┌────────────▼──────────────┐
         │   PostgreSQL/MySQL        │
         │   ├─ tables               │
         │   ├─ indexes              │
         │   └─ migrations           │
         └───────────────────────────┘
```

### Deployment Pipeline

```
Git Push
   │
   ├─→ GitHub Actions CI/CD
   │   ├─ Run tests (pytest, jest, playwright)
   │   ├─ Build Docker images
   │   └─ Push to registry
   │
   └─→ Docker Compose (dev)
       ├─ Backend service
       ├─ Frontend service
       ├─ Database service
       └─ Redis cache (optional)
```

---

## 📖 Documentation

- **Specification:** `docs/superpowers/specs/2026-05-20-autonomous-dev-system-design.md`
- **Implementation Plan:** `docs/superpowers/plans/2026-05-20-autonomous-dev-system-implementation.md`
- **Skills Directory:** `skills/`
- **Agents Directory:** `agents/`
- **Tools Directory:** `tools/`

---

## 📞 Support

For issues or questions:
1. Check `task-completion.json` for detailed status
2. Review generated code specs in `tasks/*/spec.md`
3. Check GitHub PR for detailed summary
4. Refer to individual skill documentation in `skills/`

---

## 🎉 Quick Links

- **Setup:** Run `python3 tools/exporter.py --interactive`
- **Use Agent:** In Claude Code, type `/autonomous-developer`
- **View Progress:** `cat task-completion.json | jq '.summary'`
- **Review Code:** Check `tasks/` directory
- **See PR:** Check your GitHub repository

---

**Version:** 1.0  
**Status:** Production Ready  
**Last Updated:** 2026-05-20
