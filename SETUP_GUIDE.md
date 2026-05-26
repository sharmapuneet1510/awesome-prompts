# 🚀 Autonomous Developer System - Quick Setup Guide

## Installation (2 minutes)

### Option 1: Interactive Setup (Recommended ⭐)

```bash
python3 tools/exporter.py --interactive
```

This will guide you through:
1. **Select project directory** - Where to install the system
2. **Choose platforms** - Claude Code, GitHub Copilot, Cursor, etc.
3. **Confirm and copy** - Skills and agents are automatically copied

### Option 2: Command Line Setup

```bash
# Install for Claude Code only
python3 tools/exporter.py --target claude --all

# Install for multiple platforms
python3 tools/exporter.py --target claude copilot cursor --all

# Install everything (all platforms)
python3 tools/exporter.py --all
```

### Option 3: Check What's Available

```bash
# List all available skills and agents
python3 tools/exporter.py --list
```

---

## Getting Started (5 minutes)

### 1️⃣ Create Your Requirements File

```bash
cat > requirement.txt << 'EOF'
We need a user authentication system with JWT tokens.

Use React 18+ for frontend, Python FastAPI for backend, PostgreSQL for database.

Features:
- User registration with email validation
- Secure login with JWT tokens
- User profile management
- Activity tracking

Timeline: 2 weeks
EOF
```

### 2️⃣ Invoke the Agent

**In Claude Code:**
```
Type in chat: /autonomous-developer
```

**In GitHub Copilot:**
```
Type in chat: @autonomous-developer
```

**In Terminal (when available):**
```bash
python3 -m autonomous_dev_agent
```

### 3️⃣ Watch It Build

The agent will:
- ✅ Parse your requirements
- ✅ Generate database schema with migrations
- ✅ Create backend API (routes, models, services)
- ✅ Build React UI (components, pages, styling)
- ✅ Write tests (unit, integration, E2E)
- ✅ Set up Docker & CI/CD
- ✅ Create GitHub PR with all code

### 4️⃣ Monitor Progress

```bash
# Check task completion status
cat task-completion.json | jq '.summary'

# Output example:
# {
#   "total_tasks": 5,
#   "completed": 3,
#   "in_progress": 1,
#   "pending": 1,
#   "overall_progress": 60
# }
```

### 5️⃣ (Optional) Configure Hooks

Hooks are security and development automation scripts that run at key moments.

```bash
# Export hooks to your Claude environment
python3 tools/exporter.py --target claude --hooks promptshield,test-runner
```

After export, hooks will automatically run:
- **Before you send messages** — security validation
- **Before git commits** — test and format checking
- **After commits** — cleanup and notifications

See `hooks/README.md` for available hooks and how to create custom ones.

### 6️⃣ Review Generated Code

```bash
# View all generated files
ls -la tasks/

# Check database schema
cat tasks/01-database-schema/generated/schema.sql

# Check API routes
cat tasks/02-backend-api/generated/routes.py

# Check React components
ls -la tasks/03-frontend-ui/generated/components/

# Review tests
ls -la tasks/04-integration-tests/generated/

# Check deployment files
ls -la tasks/05-deployment/generated/
```

---

## What Gets Generated

```
your-project/
├─ requirement.md              ← Structured requirements
├─ docs/
│  └─ architecture.md          ← Auto-generated architecture
├─ ._context/
│  ├─ context.json             ← Project metadata
│  ├─ graph.json               ← Knowledge graph
│  └─ graph_embeddings/        ← Cached embeddings
├─ tasks/
│  ├─ 01-database-schema/
│  ├─ 02-backend-api/
│  ├─ 03-frontend-ui/
│  ├─ 04-integration-tests/
│  └─ 05-deployment/
└─ task-completion.json        ← Detailed tracking
```

---

## Features

### ✨ Autonomous Generation
- Reads plain-text requirements
- Generates production-ready code
- Tests everything automatically
- Updates documentation

### 🔄 Smart Context
- Detects new vs existing projects
- Scans existing codebase
- Maintains knowledge graph for efficiency
- Caches embeddings for token optimization

### 🧪 Comprehensive Testing
- Unit tests (≥95% coverage)
- Integration tests
- E2E tests (Playwright)
- Coverage reports

### 📊 Auto Documentation
- Architecture diagrams
- Context files
- Task specifications
- Completion reports

### 🔀 Multi-Platform
- Claude Code
- GitHub Copilot
- Cursor IDE
- Windsurf
- Google Gemini
- Continue IDE
- OpenAI
- Aider CLI

---

## Example Requirements

### Simple Todo App
```
Todo application with user authentication.
React frontend, Python FastAPI backend, PostgreSQL database.
Features: Create, read, update, delete todos. User login and registration.
```

### E-Commerce Platform
```
E-commerce platform with products, shopping cart, and checkout.
React frontend, Java Spring Boot backend, MySQL database.
Features: Product catalog, user profiles, order history, payment processing.
Timeline: 4 weeks
```

### Microservices API
```
Microservices architecture with auth, users, and products services.
Python FastAPI with JWT authentication, PostgreSQL, Docker deployment.
Deploy to Kubernetes.
```

---

## Troubleshooting

### "requirement.txt not found"
```bash
# Create it first
cat > requirement.txt << 'EOF'
Your requirements here
EOF
```

### "Git repo not detected"
This is normal! The agent creates a new project. To use with existing repo:
```bash
cd /path/to/existing/project
python3 tools/exporter.py --target claude --all
```

### "Tests failing"
Check `task-completion.json` for details:
```bash
cat task-completion.json | jq '.tasks[] | select(.status=="failed")'
```

### "GitHub PR not created"
Ensure GitHub CLI is installed and authenticated:
```bash
gh auth login
```

---

## Next Steps

1. **Read Full Documentation:** `AUTONOMOUS_DEVELOPER_README.md`
2. **Understand Architecture:** See workflow diagrams in README
3. **Run Interactive Setup:** `python3 tools/exporter.py --interactive`
4. **Create Requirements:** `cat > requirement.txt`
5. **Invoke Agent:** In your IDE or terminal
6. **Monitor Progress:** Watch `task-completion.json`
7. **Review Code:** Check `tasks/` directory
8. **Submit PR:** Review generated GitHub PR

---

## Platform-Specific Setup

### Claude Code
```bash
python3 tools/exporter.py --target claude --all
# Then invoke in Claude Code chat: /autonomous-developer
```

### GitHub Copilot
```bash
python3 tools/exporter.py --target copilot --all
# Then invoke in Copilot chat: @autonomous-developer
```

### Cursor
```bash
python3 tools/exporter.py --target cursor --all
# Cursor will automatically discover the rules
```

### Windsurf
```bash
python3 tools/exporter.py --target windsurf --all
# Windsurf will automatically discover the rules
```

### All Platforms
```bash
python3 tools/exporter.py --all
# Skills and agents copied to all platform directories
```

---

## Support & Documentation

- **Main README:** `AUTONOMOUS_DEVELOPER_README.md` (comprehensive guide with all diagrams)
- **This Guide:** `SETUP_GUIDE.md` (quick start)
- **Technical Spec:** `docs/superpowers/specs/2026-05-20-autonomous-dev-system-design.md`
- **Implementation Plan:** `docs/superpowers/plans/2026-05-20-autonomous-dev-system-implementation.md`
- **Skills:** `skills/` directory
- **Agents:** `agents/` directory

---

**Ready to build?** Start with: `python3 tools/exporter.py --interactive`

Happy coding! 🚀
