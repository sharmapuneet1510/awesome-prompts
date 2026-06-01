# 🚀 Exporter Quick Start Guide

## TL;DR — Just Want to Get Started?

Run this one command:

```bash
python3 tools/interactive_exporter.py
```

That's it! The interactive wizard will guide you through everything.

---

## What is the Exporter?

The exporter takes **33 AI agent skills** and **18 specialized agents** from this repository and installs them into your project for use with:

- **Claude Code** (VSCode plugin + claude.ai/code)
- **GitHub Copilot** 
- **Cursor IDE**
- **Windsurf IDE**
- **Google Gemini**
- **Continue IDE**
- **OpenAI**
- **Aider CLI**

## Three Ways to Use It

### 1️⃣ Interactive Mode (Easiest — Recommended)

**Command:**
```bash
python3 tools/interactive_exporter.py
```

**What happens:**
- Asks where you want to install (your project directory)
- Shows all 8 platforms to choose from
- Lets you pick which agents/skills to install
- Confirms everything before installing
- Done! Your project has the files

**Best for:** First-time setup, learning what's available, team onboarding

---

### 2️⃣ Command-Line Mode (For Automation)

**Export everything to all platforms:**
```bash
python3 tools/exporter.py
```

**Export specific platforms:**
```bash
python3 tools/exporter.py --target claude copilot cursor
```

**Export specific skills:**
```bash
python3 tools/exporter.py --skills database,backend,frontend --agents developer
```

**List what's available:**
```bash
python3 tools/exporter.py --list
```

**Preview without exporting:**
```bash
python3 tools/exporter.py --dry-run
```

**Best for:** Batch exports, CI/CD pipelines, automation scripts

---

### 3️⃣ Programmatic Mode (For Code)

```python
from tools.exporter import ExportOrchestrator

orchestrator = ExportOrchestrator(Path("/path/to/awesome-prompts"))

# Discover
all_skills = orchestrator.discover_skills()
all_agents = orchestrator.discover_agents()

# Filter
skills = orchestrator.filter_skills(all_skills, ["java", "python"])
agents = orchestrator.filter_agents(all_agents, ["developer"])

# Export
results = orchestrator.run(
    targets=["claude", "copilot"],
    skill_filter=["backend", "database"],
    agent_filter=["autonomous"],
    dry_run=False
)
```

**Best for:** Custom tools, build scripts, integrations

---

## What Gets Installed?

### Directory Structure

After running the exporter, your project will have:

```
my-project/
├── .claude/
│   ├── skills/
│   │   ├── database_skill.md
│   │   ├── backend_skill.md
│   │   ├── frontend_skill.md
│   │   ├── test_skill.md
│   │   └── ... (28 more skills)
│   └── agents/
│       ├── implementation_agent.md
│       ├── code_review_agent.md
│       ├── autonomous_dev_agent.md
│       └── ... (15 more agents)
├── .github/
│   ├── instructions/
│   │   └── ... (Copilot format)
│   └── agents/
├── .cursor/
│   └── rules/
│       └── ... (Cursor IDE format)
└── ... (other platforms)
```

### What's Inside

**Skills:** Reusable coding patterns and standards for:
- 🗄️ Databases (schema, migrations, queries)
- 🔧 Backend APIs (REST, async, services)
- 🎨 Frontend (React, TypeScript, components)
- 🧪 Testing (unit, integration, coverage)
- ☕ Java + Spring Boot
- 🐍 Python + FastAPI
- 📦 Apache Camel, Pulsar, Kafka
- 📚 Documentation generation
- 🔍 Code review patterns
- 🔐 Security standards

**Agents:** Specialized AI agents for:
- 👨‍💻 Implementation (build features end-to-end)
- 🔍 Code Review (design patterns, SOLID, performance)
- 🏗️ Architecture (design systems, refactoring)
- 🔐 Security (vulnerability scanning, threat modeling)
- 📊 Performance (optimization, profiling)
- 🤝 Coordination (multi-agent orchestration)
- 📝 Documentation (API docs, README, changelog)
- 🚀 DevOps (CI/CD, deployment, infrastructure)

---

## Interactive Mode: Step-by-Step

### Step 1: Choose Project Location

```
Where should the autonomous developer system be set up?
(Current directory: /Users/me/my-project)

Enter project root directory (or press Enter for current): 
```

Press Enter to use current directory, or type a path.

### Step 2: Select Platforms

```
Available platforms:
  1. [✓] Claude Code (Default)
  2. [ ] GitHub Copilot
  3. [ ] Cursor IDE
  4. [ ] Windsurf IDE
  5. [ ] Google Gemini
  6. [ ] Continue IDE
  7. [ ] OpenAI
  8. [ ] Aider CLI

Enter numbers to toggle (space-separated): 
```

Examples:
- `1` — Select/deselect Claude
- `1 3 5` — Select Claude, Cursor, Gemini
- Just press Enter — Accept current selection

### Step 3: Select Skills & Agents

```
Quick options:
  1. [ ] All available skills and agents (33 + 18)
  2. [ ] Core skills only (database, backend, frontend, test)
  3. [ ] Custom selection (interactive multi-select)
  4. [ ] Minimal (just core agents)

Choose option (1-4): 
```

**Option 1 (All):** Get everything — 33 skills + 18 agents

**Option 2 (Core):** Just the 4 essentials:
- database_skill
- backend_skill
- frontend_skill
- test_skill

**Option 3 (Custom):** Interactively select exactly what you want

**Option 4 (Minimal):** Just the core agents

### Step 4: Review Summary

```
Setup Summary:

Project Root:    /Users/me/my-project
Platforms:       2 selected
                 • Claude Code
                 • GitHub Copilot
Skills:          33 skills
Agents:          18 agents

Proceed with setup? (y/n): 
```

Type `y` to proceed or `n` to cancel.

### Step 5: Export Completes

```
✓ Running export...
✓ Files exported successfully
✓ Setup Complete!
```

---

## Custom Selection Example

If you choose option 3, you get interactive agent/skill selection:

```
Step 3a: Select Agents

Found 18 agent(s). Grouped by role:

DEVELOPER
   1. [ ] Implementation Agent
       Full-lifecycle feature implementation...
   2. [ ] Autonomous Developer Agent
       Full-stack project generation...

REVIEWER
   3. [ ] Code Review Agent
       Design patterns, SOLID, performance...
   4. [ ] Security Auditor Agent
       Vulnerability scanning, threat modeling...

Selection: 1 2 3 4
Selected: implementation_agent, autonomous_dev_agent, 
          code_review_agent, security_auditor_agent

Enter agent numbers to toggle (space-separated), or press Enter to continue:
Selection: 
```

Same process for skills:

```
Step 3b: Select Skills

Found 33 skill(s). Grouped by tags:

BACKEND
   1. [ ] Backend API Generation Skill
       Applies to: Python, Node.js
   2. [ ] Database Skill
       Applies to: SQL, PostgreSQL, MongoDB

TESTING
   3. [ ] Test Generation Skill
       Applies to: Python, JavaScript

Selection: 1 2 3
Selected: backend_skill, database_skill, test_skill
```

---

## Common Use Cases

### "I want everything"
```bash
python3 tools/interactive_exporter.py
# Choose: Option 1 (All available)
```

### "I'm setting up a Python/FastAPI project"
```bash
python3 tools/interactive_exporter.py
# Choose: Option 3 (Custom)
# Select: backend_skill, database_skill, test_skill, python_advanced_skill
```

### "I'm setting up a React/TypeScript project"
```bash
python3 tools/interactive_exporter.py
# Choose: Option 3 (Custom)
# Select: frontend_skill, test_skill, react_advanced_skill
```

### "I just want the core agents and 4 core skills"
```bash
python3 tools/interactive_exporter.py
# Choose: Option 4 (Minimal)
# Then: Option 2 (Core skills)
```

### "Add to existing project that already has Claude setup"
```bash
python3 tools/interactive_exporter.py
# Choose same project directory
# Select: Additional platforms (Copilot, Cursor, etc.)
# It will add those alongside existing .claude/
```

---

## Files Generated

### For Claude Code (`.claude/`)

```
.claude/
├── skills/
│   ├── database_skill.md              → Database patterns
│   ├── backend_skill.md               → REST API patterns
│   ├── frontend_skill.md              → React/component patterns
│   ├── test_skill.md                  → Testing patterns
│   ├── java_advanced_skill.md         → Java 17+ patterns
│   ├── python_advanced_skill.md       → Python 3.11+ patterns
│   └── ... (27 more skills)
└── agents/
    ├── implementation_agent.md        → Full-lifecycle builder
    ├── code_review_agent.md           → Design/SOLID reviewer
    ├── autonomous_dev_agent.md        → Full-stack generator
    ├── security_auditor_agent.md      → Security analyzer
    └── ... (14 more agents)
```

### For Other Platforms

GitHub Copilot → `.github/instructions/` + `.github/agents/`
Cursor → `.cursor/rules/` + `.cursor/rules/agents/`
Windsurf → `.windsurf/rules/` + `.windsurf/rules/agents/`
(And so on...)

---

## Next Steps After Installing

### 1. Use in Claude Code
- Copy agent/skill files into your project
- They're automatically available in Claude Code
- Mention them in your prompts

### 2. Use in Copilot
- Files go into `.github/instructions/`
- GitHub Copilot reads them automatically
- Reference them with `@skill-name`

### 3. Use in Cursor
- Files go into `.cursor/rules/`
- Cursor applies them to all your work
- Settings → Rules auto-applies them

### 4. Create Your First Feature
- Pick an agent (e.g., Implementation Agent)
- Give it a requirement (free text, JIRA ticket, or file)
- It will generate: code + tests + documentation

### 5. Review the Code
- Use Code Review Agent to review what was generated
- Iterate until you're happy
- Merge to main

---

## Troubleshooting

### "Command not found: python3"
Use `python` instead:
```bash
python tools/interactive_exporter.py
```

### "ModuleNotFoundError"
Run from the awesome-prompts directory:
```bash
cd /path/to/awesome-prompts
python3 tools/interactive_exporter.py
```

### "Could not discover items"
Make sure you're in the awesome-prompts repository or specify the path:
```bash
python3 /path/to/awesome-prompts/tools/interactive_exporter.py
```

### "Skills/agents not appearing in my IDE"
- Copy files from `.claude/` to your project's `.claude/`
- Restart the IDE
- Check that files have `---` YAML frontmatter at the top

### "Too many options, what should I choose?"
Start with **Option 2 (Core skills)** — it's the minimal, essential set:
- database_skill
- backend_skill  
- frontend_skill
- test_skill

Then add more later if needed.

---

## Advanced Topics

### Exporting to a Different Project

```bash
python3 /path/to/awesome-prompts/tools/interactive_exporter.py
# Step 1: Enter /path/to/my-other-project
# Rest is the same
```

### Command-Line Bulk Export

```bash
# Export specific items to specific platforms
python3 tools/exporter.py \
  --target claude copilot cursor \
  --skills java,python,backend \
  --agents developer,reviewer
```

### Dry Run (Preview)

```bash
python3 tools/exporter.py --dry-run --target claude
# Shows what would be exported without actually exporting
```

### List All Available

```bash
python3 tools/exporter.py --list
# Shows all 33 skills and 18 agents
```

### Clean Up Previous Exports

```bash
python3 tools/exporter.py --clean
# Removes all previously exported files
```

---

## Documentation

For more details:
- **Interactive Exporter Details:** `tools/INTERACTIVE_EXPORTER_README.md`
- **Exporter CLI Docs:** `tools/exporter.py --help`
- **Main Tools Docs:** `tools/README.md`
- **All Agents:** `agents/README.md`
- **All Skills:** See `skills/*.md` files

---

## Still Have Questions?

1. **How do I use an agent?** → `agents/README.md`
2. **What does this skill do?** → Read the `.md` file in `skills/`
3. **I want to customize something** → Edit the `.md` files after export
4. **Can I use these with other tools?** → Yes! The exporter supports 8 platforms

---

**Ready to start?**

```bash
python3 tools/interactive_exporter.py
```

Questions? Check the full docs in `tools/README.md` and `tools/INTERACTIVE_EXPORTER_README.md`.
