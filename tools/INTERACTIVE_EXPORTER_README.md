# Interactive Exporter — Enhanced Agent & Skill Selection

The enhanced `interactive_exporter.py` provides an interactive CLI for discovering, selecting, and exporting agents and skills to multiple AI assistant platforms.

## Features

### 1. **Dynamic Discovery**
- Automatically discovers all skills and agents from source files
- Parses YAML frontmatter for metadata (name, description, tags, roles)
- Groups agents by role and skills by tags for better organization

### 2. **Interactive Platform Selection**
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
```

**Features:**
- Toggle selection with numbers (e.g., `1 3 5` selects Claude, Cursor, Gemini)
- Press Enter to confirm
- Visual checkmarks show selected platforms
- Descriptions for each platform

### 3. **Interactive Agent Selection** (Custom mode only)
Groups agents by role with descriptions:
- Shows agent name and full description
- Numbers for easy selection/toggling
- Groups by role (developers, reviewers, architects, etc.)
- Press Enter to confirm

### 4. **Interactive Skill Selection** (Custom mode only)
Groups skills by primary tag:
- Shows skill name and what technologies it applies to
- Numbers for easy selection/toggling
- Groups by tag (java, python, database, frontend, etc.)
- Press Enter to confirm

### 5. **Quick Presets** (Step 3)
Choose from quick options:
1. **All available** - Export everything (33 skills, 18 agents)
2. **Core skills only** - 4 essential skills (database, backend, frontend, test)
3. **Custom selection** - Interactive multi-select for agents and skills
4. **Minimal** - Just core agents, no extra skills

### 6. **Summary & Confirmation**
Before exporting, shows:
- Project root directory
- Number of platforms selected
- Number of skills selected
- Number of agents selected
- Full list of what will be exported

## Usage

### Basic (Interactive mode)
```bash
python3 tools/interactive_exporter.py
```

Or from anywhere in the repo:
```bash
python3 -m tools.interactive_exporter
```

### Command-line (Non-interactive)
If you prefer the original command-line mode:
```bash
python3 tools/exporter.py --target claude copilot --skills java,python --agents developer
```

## Workflow

1. **Step 1: Project Root** - Choose where to install (current directory by default)
2. **Step 2: Platforms** - Select target platforms (Claude, Copilot, Cursor, etc.)
3. **Step 3: Skills & Agents** - Quick presets or custom selection
   - Option 1: All available items
   - Option 2: Core skills only
   - Option 3: Custom interactive selection
   - Option 4: Minimal setup
4. **Step 4: Confirmation** - Review what will be exported
5. **Step 5: Export** - Files are copied/generated to your project
6. **Step 6: Next Steps** - Get instructions on how to use exported items

## Export Results

When you choose a project root directory other than the awesome-prompts repo, the tool copies/generates:

### For Claude (`--target claude`)
```
<project>/.claude/
├── skills/
│   ├── database_skill.md
│   ├── backend_skill.md
│   └── ... (other selected skills)
└── agents/
    ├── developer_agent.md
    ├── reviewer_agent.md
    └── ... (other selected agents)
```

### For GitHub Copilot (`--target copilot`)
```
<project>/.github/
├── instructions/
│   ├── database_skill.instructions.md
│   └── ...
└── agents/
    ├── developer_agent.md
    └── ...
```

### Similar structure for all 8 platforms

## Discovery Statistics

When running `discover_skills_and_agents()`:
- **33 Skills** across all technology stacks
  - Backend: database, backend, REST API, task generation
  - Frontend: React, TypeScript, UI components
  - Advanced: Java, Python, Spring Boot, Pulsar, Camel
  - Cross-cutting: Testing, documentation, code review
  
- **18 Agents** with specialized roles
  - Developers: Implementation Agent, Autonomous Dev Agent
  - Reviewers: Code Review Agent, Security Auditor
  - Architects: Architecture Refactorer, Backend Systems Architect
  - Coordinators: AI Engineering Team Coordinator
  - And more...

## Sample Output

```
Step 3: Skills & Agents to Export

Quick options:
  1. [ ] All available skills and agents
  2. [ ] Core skills only (database, backend, frontend, test)
  3. [ ] Custom selection
  4. [ ] Minimal (just core agents)

Choose option (1-4, or press Enter for #1): 3

Step 3a: Select Agents

Found 18 agent(s). Group by role:

DEVELOPER
   1. [ ] Implementation Agent
       Takes requirements and builds complete, tested, documented...
   2. [ ] Autonomous Developer Agent
       Full-stack project generation with database, API, UI, tests...

REVIEWER
   3. [ ] Code Review Agent
       Design patterns, SOLID, performance, security review...
   4. [ ] Security Auditor Agent
       Comprehensive security assessment and threat modeling...

...

Enter agent numbers to toggle (space-separated), or press Enter to continue:
Selection: 1 2
Selected: autonomous_dev_agent, implementation_agent
```

## Options Explained

### Quick Preset 1: All Available
- Exports all 33 skills
- Exports all 18 agents
- Best for comprehensive setup
- Good for learning what's available

### Quick Preset 2: Core Skills
- Exports 4 essential skills:
  - `database_skill` - Database schema and migrations
  - `backend_skill` - REST API generation
  - `frontend_skill` - React components
  - `test_skill` - Test generation
- No agents selected
- Good for minimal setup focused on core functionality

### Quick Preset 3: Custom Selection
- Interactive selection of agents (grouped by role)
- Interactive selection of skills (grouped by tags)
- Toggle items on/off with numbers
- Confirm with Enter
- Best for precise control

### Quick Preset 4: Minimal
- Only core agents (e.g., Autonomous Developer)
- No extra skills
- Best for lean setup

## Tips

1. **First time?** Start with "All available" (option 1) to see what's available
2. **Know what you want?** Use option 3 (Custom) for precise selection
3. **Quick start?** Use option 2 (Core skills) or 4 (Minimal)
4. **Testing?** Use Claude + Cursor for quick testing with two platforms
5. **Full setup?** Select all 8 platforms to have consistent tooling across all IDEs

## Troubleshooting

**Q: "Could not discover items"**
- Make sure you're running from the awesome-prompts directory or specify `--repo-root`

**Q: Platform descriptions are truncated**
- This is normal for wide screens; descriptions are shortened to fit
- Full descriptions are in the source files

**Q: Numbers not working in selection**
- Use space-separated numbers (e.g., `1 3 5`, not `135`)
- Invalid numbers will show a warning but won't break the flow

**Q: Can't toggle selections**
- Each number press toggles on/off
- Press the same number again to deselect
- Empty input (just press Enter) confirms current selection

## Advanced Usage

### Rerun on Existing Project
If you already exported to a project and want to add more platforms:
```bash
python3 tools/interactive_exporter.py
```
And choose the same project root — it will add the new platforms alongside existing ones.

### From Different Directory
```bash
cd /path/to/my/project
python3 /path/to/awesome-prompts/tools/interactive_exporter.py
```

### Programmatic Use
```python
from pathlib import Path
from tools.interactive_exporter import discover_skills_and_agents

repo_root = Path("/path/to/awesome-prompts")
skills, agents = discover_skills_and_agents(repo_root)

for skill in skills:
    print(f"{skill.name} - {skill.description}")
    print(f"  Applies to: {', '.join(skill.applies_to)}")
```

## Integration with Other Tools

The enhanced exporter works seamlessly with:
- `exporter.py` — Main export logic
- `config_generator.py` — Generates platform config files
- `update_checker.py` — Checks for available updates

## Related Commands

```bash
# List all skills and agents (non-interactive)
python3 tools/exporter.py --list

# Dry run (see what would be exported)
python3 tools/exporter.py --dry-run

# Clean up previously exported files
python3 tools/exporter.py --clean

# Export via command line (non-interactive)
python3 tools/exporter.py --target claude copilot --skills java,python
```

## Performance

- **Discovery:** 100-200ms (reads ~50 .md files)
- **Interactive selection:** Instant (no network calls)
- **Export:** 1-5 seconds (depends on number of items and platforms)
- **Total:** Usually under 10 seconds

## Version

Interactive Exporter v2.0 — Enhanced with dynamic discovery and multi-select UI (2026-06)
