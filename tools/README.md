# 🔧 Tools Documentation

> Utility scripts and generators for the Awesome Prompts system

**Quick Navigation**

| Tool | Purpose | Usage | Output |
|------|---------|-------|--------|
| [Exporter](exporter.py) | Export to 9 platforms | `python exporter.py` | Agents & skills for Claude, Copilot, Cursor, etc. |
| [Context Builder](context_builder.py) | Generate architecture docs | `python context_builder.py` | architecture.md, tech-stack.md, context.json |
| [Report Generator](code_review_generator.py) | Create HTML reports | `ReviewReportGenerator().generate()` | Interactive HTML reviews |
| [Comment Formatter](code_review_reporter.py) | Format MR comments | `MRCommentFormatter.format_comment()` | Markdown comments |
| [Requirement Parser](requirement_parser.py) | Parse requirements | `python requirement_parser.py` | Structured requirements |
| [Task Generator](task_generator.py) | Break down tasks | `python task_generator.py` | Task specifications |

---

## 🚀 Exporter Tool

**File:** `exporter.py`

**Purpose:** Export agents and skills to 9 platforms

**Supported Platforms:**
- Claude Code
- GitHub Copilot
- Cursor
- Windsurf
- VS Code
- Gemini CLI
- Continue.dev
- OpenAI
- Aider

**Usage:**

```bash
# Export all
python tools/exporter.py

# Export specific platforms
python tools/exporter.py --target claude copilot cursor

# Export specific items
python tools/exporter.py --skills java,spring --agents developer

# List available
python tools/exporter.py --list

# Dry run (preview)
python tools/exporter.py --dry-run

# Clean up
python tools/exporter.py --clean
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

**Output:**
```
output/
├── claude/
│   ├── implementation_agent.md
│   ├── code_review_agent.md
│   └── ...skills...
├── copilot/
│   └── [same files]
└── cursor/
    └── [same files]
```

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

| Tool | Input | Output | Use Case |
|------|-------|--------|----------|
| Exporter | All agents/skills | Platform-specific files | Multi-platform distribution |
| Context Builder | Project structure | Docs + JSON + HTML | Architecture documentation |
| Report Generator | Review data | HTML file | Code review reports |
| Comment Formatter | Review data | Markdown text | MR/PR comments |
| Requirement Parser | Various formats | Structured requirement | Requirement processing |
| Task Generator | Requirement | Task list | Task breakdown |
| Design HTML | Project info | Interactive HTML | Visualization |

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

### Example 1: Export to All Platforms

```bash
cd awesome-prompts/tools

# Export all agents and skills
python exporter.py

# Use in your tools:
# - Claude Code: Copy from output/claude/
# - Copilot: Copy from output/copilot/
# - Cursor: Copy from output/cursor/
# - etc.
```

### Example 2: Generate Architecture Docs

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

**Last Updated:** May 25, 2026 | **Version:** 4.2.0
