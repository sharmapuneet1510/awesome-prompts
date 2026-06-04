# Documentation

Complete guide to awesome-prompts v3.0 architecture, agents, skills, and workflows.

## 📚 Contents

### Getting Started
- **[QUICK_START.md](QUICK_START.md)** — Installation and 5-minute tutorial
- **[API_REFERENCE.md](API_REFERENCE.md)** — Complete function reference (31 functions)

### Usage & Workflows
- **[guides/01-code-review-tool.md](guides/01-code-review-tool.md)** — Code review setup & examples
- **[guides/02-exporting-to-platforms.md](guides/02-exporting-to-platforms.md)** — Export to Claude, Copilot, Cursor, etc
- **[guides/03-python-setup.md](guides/03-python-setup.md)** — Python environment & token_optimizer
- **[guides/04-requirement-input.md](guides/04-requirement-input.md)** — Parse requirements from JIRA, files, text
- **[EXAMPLES.md](EXAMPLES.md)** — Workflow examples with code samples

### Architecture & Design
- **[architecture/](architecture/)** — System design documents
  - `agent-architecture.md` — Agent pipeline & function dispatch
  - `skill-architecture.md` — Skill design & reusability
  - `system-design.md` — Overall system topology

### Framework & Migrations
- **[FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md)** — Instructions framework & middleware
- **[MIGRATION.md](MIGRATION.md)** — Migration guides for previous versions

### Plans & Specifications
- **[superpowers/plans/](superpowers/plans/)** — Implementation roadmaps
- **[superpowers/specs/](superpowers/specs/)** — Design specifications

---

## 🎯 Quick Navigation

**I want to:**
- **Build a new feature** → [QUICK_START.md](QUICK_START.md)
- **Review code** → [guides/01-code-review-tool.md](guides/01-code-review-tool.md)
- **Export to my IDE** → [guides/02-exporting-to-platforms.md](guides/02-exporting-to-platforms.md)
- **Understand the architecture** → [architecture/](architecture/)
- **See examples** → [EXAMPLES.md](EXAMPLES.md)
- **Use token_optimizer** → [guides/03-python-setup.md](guides/03-python-setup.md)
- **Parse requirements** → [guides/04-requirement-input.md](guides/04-requirement-input.md)

---

## 📖 Documentation Structure

```
docs/
├── README.md (you are here)
├── QUICK_START.md
├── API_REFERENCE.md
├── EXAMPLES.md
├── FRAMEWORK_GUIDE.md
├── MIGRATION.md
│
├── guides/
│   ├── 01-code-review-tool.md
│   ├── 02-exporting-to-platforms.md
│   ├── 03-python-setup.md
│   └── 04-requirement-input.md
│
├── architecture/
│   ├── agent-architecture.md
│   ├── skill-architecture.md
│   └── system-design.md
│
└── superpowers/
    ├── plans/ (implementation roadmaps)
    └── specs/ (design specifications)
```

---

## 🚀 Key Concepts

### Agents (5 total with AP: prefix)
- **AP:Orchestrator** — Planning & strategy
- **AP:Architect** — System design
- **AP:Implementer** — Code generation, testing, documentation
- **AP:Quality** — Code review, security, performance
- **AP:Business Analyst** — JIRA & backlog management

### Skills (24 total)
Reusable coding standard modules for specific domains (Java, Python, React, etc).

### Functions (31 total)
Callable functions using `agent:function` syntax (e.g., `quality:review pr=456`).

---

## 📞 Support

- **Report Issues** → GitHub issues
- **Feature Requests** → GitHub discussions
- **Questions** → Check [EXAMPLES.md](EXAMPLES.md) first

See [QUICK_START.md](QUICK_START.md) to get started in 5 minutes!
