# 🔧 Tools Documentation

> Utility scripts and generators for the Awesome Prompts system

**Quick Navigation**

| Tool | Purpose | Usage | Output |
|------|---------|-------|--------|
| **[Interactive Exporter](interactive_exporter.py)** | **Guided agent/skill selection → Export to 8 platforms** | **`python interactive_exporter.py`** | **User-friendly setup wizard** |
| [Exporter](exporter.py) | Batch export to 8 platforms (CLI mode) | `python exporter.py --target claude copilot` | Platform-specific agent & skill files |
| [Context Builder](context_builder.py) | Generate architecture docs | `python context_builder.py` | architecture.md, tech-stack.md, context.json |
| [Report Generator](code_review_generator.py) | Create HTML reports | `ReviewReportGenerator().generate()` | Interactive HTML reviews |
| [Comment Formatter](code_review_reporter.py) | Format MR comments | `MRCommentFormatter.format_comment()` | Markdown comments |
| [Requirement Parser](requirement_parser.py) | Parse requirements | `python requirement_parser.py` | Structured requirements |
| [Task Generator](task_generator.py) | Break down tasks | `python task_generator.py` | Task specifications |

---

## 🚀 Exporter Tool

**Files:** `exporter.py` + `interactive_exporter.py`

**Purpose:** Export agents and skills to 8 platforms

**Supported Platforms:**
- Claude Code — `.claude/`
- GitHub Copilot — `.github/`
- Cursor IDE — `.cursor/`
- Windsurf IDE — `.windsurf/`
- Google Gemini — `.gemini/`
- Continue IDE — `.continue/`
- OpenAI — `tools/output/openai/`
- Aider CLI — `.aider/`

### Quick Start: Interactive Mode (Recommended)

The enhanced interactive exporter guides you through the process with visual menus:

```bash
python3 tools/interactive_exporter.py
```

**What you'll see:**
```
Step 1: Project Root Directory
Where should the autonomous developer system be set up?

Step 2: Target Platforms
Available platforms:
  1. [✓] Claude Code (Default)
  2. [ ] GitHub Copilot
  3. [ ] Cursor IDE
  ... (8 total)

Step 3: Skills & Agents
Quick options:
  1. [ ] All available skills and agents (33 + 18)
  2. [ ] Core skills only (4 essential skills)
  3. [ ] Custom selection (interactive multi-select)
  4. [ ] Minimal (just core agents)

Step 4: Summary & Confirmation
Project Root:    /path/to/my/project
Platforms:       2 selected (Claude, Copilot)
Skills:          33 skills
Agents:          18 agents

Step 5: Export!
✓ Exporting to 2 platform(s)...
```

**Features:**
- ✅ Dynamic discovery of all 33 skills and 18 agents
- ✅ Interactive multi-select with visual checkmarks
- ✅ Grouped by role (agents) and tags (skills)
- ✅ Four quick presets for different use cases
- ✅ Summary before export
- ✅ Color-coded output with helpful hints

### Interactive Mode: Custom Selection

Choose option 3 for custom selection:

```
Step 3a: Select Agents

Found 18 agent(s). Group by role:

DEVELOPER
   1. [ ] Implementation Agent
       Takes requirements and builds complete...
   2. [ ] Autonomous Developer Agent
       Full-stack project generation with...

REVIEWER
   3. [ ] Code Review Agent
   4. [ ] Security Auditor Agent
   ... (18 total)

Selection: 1 2 5
Selected: autonomous_dev_agent, code_review_agent, ...
```

**How to use:**
- Type numbers separated by spaces: `1 3 5`
- Type same number again to deselect: `1` → deselects
- Press Enter with no input to confirm

### Command-Line Mode (For Automation)

If you prefer command-line:

```bash
# Export all to all platforms
python tools/exporter.py

# Export to specific platforms
python tools/exporter.py --target claude copilot cursor

# Export specific items
python tools/exporter.py --skills java,spring --agents developer

# List available
python tools/exporter.py --list

# Dry run (preview)
python tools/exporter.py --dry-run

# Clean up previous exports
python tools/exporter.py --clean
```

### Interactive Exporter Usage Examples

**Example 1: Export everything to Claude**
```bash
$ python3 tools/interactive_exporter.py

Step 2: Target Platforms
Selection: 1  # Claude
Selection: 
✓ Selected platforms:
  • Claude Code (Default)

Step 3: Skills & Agents
Choose option: 1  # All available

Step 4: Summary & Confirmation
Project Root:    /Users/me/my-project
Platforms:       1 selected
Skills:          33 skills
Agents:          18 agents
Proceed with setup? (y/n): y

✓ Exporting...
✓ Setup Complete!
```

**Example 2: Export to multiple platforms with core skills**
```bash
$ python3 tools/interactive_exporter.py

Step 2: Target Platforms
Selection: 1 2 3  # Claude, Copilot, Cursor
Selection: 
✓ Selected platforms:
  • Claude Code
  • GitHub Copilot
  • Cursor IDE

Step 3: Skills & Agents
Choose option: 2  # Core skills only

✓ Selected 4 core skills (database, backend, frontend, test)

Proceed? (y/n): y
✓ Export complete to 3 platforms!
```

**Example 3: Custom agent + skill selection**
```bash
$ python3 tools/interactive_exporter.py

Step 3: Skills & Agents
Choose option: 3  # Custom selection

Step 3a: Select Agents
DEVELOPER
   1. [ ] Implementation Agent
   2. [ ] Autonomous Developer Agent
REVIEWER
   3. [ ] Code Review Agent
   4. [ ] Security Auditor Agent
...

Selection: 1 2 3
Selected: autonomous_dev_agent, code_review_agent, implementation_agent

Step 3b: Select Skills
BACKEND
   1. [ ] Backend API Generation Skill
   2. [ ] Database Skill
TESTING
   3. [ ] Test Generation Skill
...

Selection: 1 2 3
Selected: backend_skill, database_skill, test_skill

✓ Ready to export selected items
```

### Export Output Structure

When exporting to a project directory:

```
my-project/
├── .claude/
│   ├── skills/
│   │   ├── backend_skill.md
│   │   ├── database_skill.md
│   │   └── ...
│   └── agents/
│       ├── implementation_agent.md
│       ├── code_review_agent.md
│       └── ...
├── .github/
│   ├── instructions/
│   │   ├── backend_skill.instructions.md
│   │   └── ...
│   └── agents/
├── .cursor/
│   └── rules/
│       └── ...
└── ... (other platforms)
```

### Exporting Hooks

Hooks are automatically discovered from the `hooks/` directory and exported to all platforms:

```bash
# Export hooks with skills and agents
python3 tools/exporter.py

# Export only specific hooks
python3 tools/exporter.py --hooks promptshield,test-runner

# Export hooks to specific platforms
python3 tools/exporter.py --target claude copilot --hooks promptshield
```

See `hooks/README.md` for hook format and examples.

---

## 🎯 Interactive Exporter (Enhanced)

**File:** `interactive_exporter.py`

**Purpose:** User-friendly guided setup with dynamic agent/skill discovery and selection

**Key Features:**

1. **Dynamic Discovery** (Automatic)
   - Scans source files for all skills and agents
   - Parses metadata from YAML frontmatter
   - Groups by role and tags for easy browsing
   - Results: 33 skills, 18 agents discovered

2. **Interactive Platform Selection**
   - Visual display with checkmarks: `[✓] Claude Code`
   - Toggle with numbers: `1 3 5` (space-separated)
   - Descriptions for each platform
   - Reusable — add more platforms to existing project

3. **Four Selection Presets**
   - **All available:** 33 skills + 18 agents (comprehensive)
   - **Core skills:** 4 essentials (database, backend, frontend, test)
   - **Custom:** Interactive multi-select per agent and skill
   - **Minimal:** Just core agents for lightweight setup

4. **Interactive Multi-Select (Custom mode)**
   - Agents grouped by role with descriptions
   - Skills grouped by technology tags
   - Number-based toggle (same number = deselect)
   - Real-time selection feedback
   - Press Enter to confirm

5. **Summary & Confirmation**
   - Shows exact stats before export
   - Lists all platforms, skills, agents
   - One final confirmation before writing

6. **User-Friendly UX**
   - Color-coded output (green = success, yellow = warning)
   - Helpful hints and descriptions
   - Clear step progression
   - Keyboard interrupt support (Ctrl+C)

**Complete Workflow:**

```
┌─────────────────────────────────┐
│ Step 1: Project Root            │  ← Choose destination
├─────────────────────────────────┤
│ Step 2: Platform Selection       │  ← Toggle with numbers
├─────────────────────────────────┤
│ Step 3: Skills & Agents         │  ← Choose preset or custom
├─────────────────────────────────┤
│ Step 3a: Agent Selection (opt)  │  ← Interactive if custom
├─────────────────────────────────┤
│ Step 3b: Skill Selection (opt)  │  ← Interactive if custom
├─────────────────────────────────┤
│ Step 4: Summary & Confirmation  │  ← Review before export
├─────────────────────────────────┤
│ Step 5: Export                  │  ← Files written
├─────────────────────────────────┤
│ Step 6: Next Steps              │  ← Usage instructions
└─────────────────────────────────┘
```

**Selection Mechanics:**

```
Available platforms:
  1. [ ] Claude Code
  2. [✓] GitHub Copilot         (already selected)
  3. [ ] Cursor IDE

Input: 1 3                      (select 1 and 3)
Input: 2                        (deselect 2)
Input: (press Enter)            (confirm selection)
```

**Documentation:**

See `INTERACTIVE_EXPORTER_README.md` for:
- Detailed feature descriptions
- Complete workflow examples
- Troubleshooting guide
- Advanced usage (batch export, CI/CD integration)
- Programmatic usage examples

**Statistics:**

- **Skills discovered:** 33
  - Backend: 6 (database, backend, REST, task, etc.)
  - Frontend: 3 (React, TypeScript, UI components)
  - Advanced: 15+ (Java, Python, Spring, Pulsar, etc.)
  - Cross-cutting: 9+ (testing, docs, review, etc.)

- **Agents discovered:** 18
  - Developers: Implementation, Autonomous Dev
  - Reviewers: Code Review, Security Auditor
  - Architects: Architecture Refactorer, Systems Architect
  - Coordinators: AI Engineering Team Coordinator
  - And more...

---

## 🏗️ Context Builder Tool

**File:** `context_builder.py`

**Purpose:** Automatically generate project documentation

**Generates:**
- `architecture.md` — System design with Mermaid diagrams
- `tech-stack.md` — Technology reference table
- `context.json` — Machine-readable metadata
- `design.html` — Interactive visualization

**Usage:**

```bash
python tools/context_builder.py

# Output:
# docs/context/
# ├── architecture.md
# ├── tech-stack.md
# ├── context.json
# └── design.html
```

**Features:**
- ✅ Analyzes project structure
- ✅ Detects technologies used
- ✅ Extracts key dependencies
- ✅ Maps module interactions
- ✅ Generates diagrams
- ✅ Creates interactive visualization

---

## 📊 Code Review Report Generator

**File:** `code_review_generator.py`

**Purpose:** Generate interactive HTML code review reports

**Class:** `ReviewReportGenerator`

**Usage:**

```python
from tools.code_review_generator import ReviewReportGenerator

# Create generator
gen = ReviewReportGenerator(output_dir="reviews")

# Generate report
review_data = {
    'jira_key': 'PROJ-123',
    'mr_number': 456,
    'scorecard': {
        'requirement_met': 95,
        'code_quality': 85,
        'test_coverage': 72,
        'documentation': 65,
        'final_score': 84.4,
        'final_grade': 'B',
        'status': 'Changes Needed'
    },
    'phases': {...},
    'issues': [...]
}

path = gen.generate(review_data, 'PROJ-123')
# Output: reviews/review-PROJ-123-20260525T143022.html
```

**Report Sections:**
1. Header (JIRA, PR, timestamp)
2. Scorecard (4 metrics + grade)
3. Requirement analysis
4. Issues by severity
5. File breakdown
6. Severity heatmap
7. Suggestions
8. Footer

**Features:**
- ✅ Self-contained HTML (no external dependencies)
- ✅ Responsive design (mobile-friendly)
- ✅ Animated progress bars
- ✅ Color-coded severity
- ✅ Interactive sections
- ✅ Export-friendly

---

## 💬 MR Comment Formatter

**File:** `code_review_reporter.py`

**Purpose:** Format code review results as markdown comments

**Class:** `MRCommentFormatter`

**Usage:**

```python
from tools.code_review_reporter import MRCommentFormatter

# Format comment for MR/PR
comment = MRCommentFormatter.format_comment(review_data, "/path/to/report.html")

# Post to GitHub/GitLab via MCP:
# mcp_vcs.post_comment(pr_id, comment)
```

**Output Example:**

```markdown
## 🔍 Code Review Complete

### Scorecard
- **Requirement Met:** 95%
- **Code Quality:** 85%
- **Test Coverage:** 72%
- **Documentation:** 65%

**Final Grade: B (84.4/100)**

**Status:** ⚠️ Changes Needed

### 🚨 Critical Issues (P0/P1)

1. **[Security] P0** — SQL injection in email lookup
2. **[Testing] P1** — Missing error case tests

### ✅ Action Items Before Merge

- [ ] Fix SQL injection vulnerability
- [ ] Add error case tests
- [ ] Document rate limiting strategy

### 📊 Full Analysis

See detailed report: `/reviews/review-PROJ-123-20260525T143022.html`

---
_Review generated by Code Review Agent v3_
```

**Features:**
- ✅ 7-section format
- ✅ Scorecard summary
- ✅ Critical issues only (P0/P1)
- ✅ Action items checklist
- ✅ Link to full report
- ✅ Emoji for visual clarity

---

## 📋 Requirement Parser

**File:** `requirement_parser.py`

**Purpose:** Parse requirements from various sources

**Supports:**
- Free text
- JIRA tickets
- Files (Markdown, PDF)
- Auto-detect from code

**Usage:**

```bash
python tools/requirement_parser.py --source "Build user registration"

python tools/requirement_parser.py --jira PROJ-123

python tools/requirement_parser.py --file requirements.md

python tools/requirement_parser.py --auto  # Auto-detect from codebase
```

---

## 📌 Task Generator

**File:** `task_generator.py`

**Purpose:** Break down requirements into bite-sized tasks

**Usage:**

```bash
python tools/task_generator.py --requirement "Build e-commerce checkout" --count 10
```

**Output:**

```
Task 1: Create order database schema
Task 2: Implement payment gateway integration
Task 3: Build order API endpoints
Task 4: Create checkout UI components
Task 5: Implement inventory checks
Task 6: Add order confirmation email
Task 7: Write integration tests
Task 8: Add order tracking
Task 9: Create admin dashboard
Task 10: Deploy to production
```

---

## 📊 Design HTML Generator

**File:** `generate_design_html.py`

**Purpose:** Create interactive HTML visualizations

**Generates:**
- System architecture diagrams
- Technology stack table
- File tree visualization
- API endpoint explorer
- Interactive tabs

**Features:**
- D3.js visualization
- Responsive layout
- Export-friendly
- Print support

---

## Tool Comparison

| Tool | Input | Output | Use Case | Mode |
|------|-------|--------|----------|------|
| **Interactive Exporter** | **User choices** | **Platform dirs** | **First-time setup (recommended)** | **GUI/Interactive** |
| Exporter | CLI args | Platform dirs | Batch export, automation | CLI |
| Context Builder | Project structure | Docs + JSON + HTML | Architecture documentation | CLI |
| Report Generator | Review data | HTML file | Code review reports | Library |
| Comment Formatter | Review data | Markdown text | MR/PR comments | Library |
| Requirement Parser | Various formats | Structured requirement | Requirement processing | CLI/Library |
| Task Generator | Requirement | Task list | Task breakdown | CLI |
| Design HTML | Project info | Interactive HTML | Visualization | CLI |

---

## Installation & Setup

```bash
# Clone repository
git clone https://github.com/sharmapuneet1510/awesome-prompts.git
cd awesome-prompts

# Install Python dependencies (if any)
pip install -r tools/requirements.txt

# Run exporter
python tools/exporter.py

# Run context builder
python tools/context_builder.py

# Use as library
from tools.code_review_generator import ReviewReportGenerator
from tools.code_review_reporter import MRCommentFormatter
```

---

## Workflow Examples

### Example 1: Interactive Export (Recommended for First-Time Setup)

```bash
# From anywhere in your project
python3 /path/to/awesome-prompts/tools/interactive_exporter.py

# Follow the guided wizard:
# - Choose where to install (your project directory)
# - Select platforms (Claude, Copilot, Cursor, etc.)
# - Choose skills & agents (quick presets or custom)
# - Confirm summary
# - Done! Files are installed

# Result: Your project now has .claude/, .github/, .cursor/, etc.
# with all the agents and skills ready to use
```

**Use cases:**
- ✅ First-time setup (easiest way to start)
- ✅ New team member onboarding
- ✅ Adding new platforms to existing project
- ✅ Learning what's available

### Example 2: Batch Export to All Platforms (Command-Line)

```bash
cd awesome-prompts/tools

# Export all agents and skills to all 8 platforms
python exporter.py

# Use in your tools:
# - Claude Code: Copy from .claude/
# - Copilot: Copy from .github/
# - Cursor: Copy from .cursor/
# - etc.
```

**Use cases:**
- ✅ Automation and CI/CD
- ✅ Bulk export without interaction
- ✅ Scripted deployments

### Example 3: Generate Architecture Docs

```bash
cd awesome-prompts/tools

python context_builder.py

# Check output:
# ls ../docs/context/
# ├── architecture.md
# ├── tech-stack.md
# ├── context.json
# └── design.html
```

### Example 3: Create Code Review Report

```python
from tools.code_review_generator import ReviewReportGenerator
from tools.code_review_reporter import MRCommentFormatter

# Setup
gen = ReviewReportGenerator()

# Generate HTML report
review_data = {...}  # From Code Review Agent
path = gen.generate(review_data, 'PROJ-123')

# Format MR comment
comment = MRCommentFormatter.format_comment(review_data, path)

# Post to GitHub (via MCP)
mcp_vcs.post_comment(pr_id, comment)
```

---

## Extending Tools

### Creating a New Tool

```python
# tools/my_tool.py

class MyTool:
    """Custom tool for specific purpose"""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def process(self, input_data):
        """Process input and return output"""
        # Implementation
        return output
    
    def export(self, format='json'):
        """Export results in specified format"""
        # Implementation
        return formatted_output
```

### Integrating with Agents

```python
# In implementation_agent.md or skill:

from tools.my_tool import MyTool

tool = MyTool(config)
result = tool.process(data)
```

---

## Performance & Optimization

### Report Generation
- HTML reports: ~17-26 KB
- Generation time: <1 second
- Memory usage: 2-5 MB
- Supports 100+ issues

### Context Builder
- Analysis time: 5-10 seconds
- Output size: 50-200 KB
- Supports projects with 100+ files

---

## 🔗 Links

- **[Agents Directory](../agents/README.md)** — Agent catalog
- **[Skills Directory](../skills/README.md)** — Skill modules
- **[Master Rules](../instructions/master_instruction_set.md)** — Standards
- **[Main README](../README.md)** — Project overview

---

**Last Updated:** June 1, 2026 | **Version:** 5.0.0 (Interactive Exporter added)
