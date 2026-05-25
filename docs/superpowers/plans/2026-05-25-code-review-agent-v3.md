# Code Review Agent v3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Code Review Agent v3 that validates PRs against JIRA requirements while reviewing code quality, test coverage, and documentation.

**Architecture:** Three-layer system — skill (pure review logic) → tool (report generation) → agent (orchestration). Skill is reusable; tools handle presentation; agent manages MCP integration and workflow.

**Tech Stack:** Python (tools), Markdown (skill & agent), HTML5/CSS/JavaScript (reports), MCP (data abstraction)

---

### Task 1: Create Code Review Skill (Reusable Logic)

**Files:**
- Create: `skills/code_review_skill.md`

- [ ] **Step 1: Write the skill header and identity section**

```markdown
---
name: Code Review Skill
version: 3.0
description: >
  Reusable review logic: 6-phase analysis (requirement validation,
  code quality, testing, documentation), scorecard calculation,
  issue categorization by severity. Tech-stack agnostic.
---

# Code Review Skill — v3.0

## Identity

You are a **Code Review Analyst** that systematically validates code against requirements and quality standards. You analyze code in 6 phases: requirement validation, code quality, test coverage, documentation, and scoring.

Your motto: **"Every line of code should implement something and be maintainable."**
```

- [ ] **Step 2: Add Phase 1 — Requirement Analysis**

(See full plan section in brainstorming output for complete content)

- [ ] **Step 3: Add Phase 2 — Requirement Validation**

(See full plan section in brainstorming output for complete content)

- [ ] **Step 4: Add Phase 3 — Code Quality Review**

(See full plan section in brainstorming output for complete content)

- [ ] **Step 5: Add Phase 4 — Test Coverage Analysis**

(See full plan section in brainstorming output for complete content)

- [ ] **Step 6: Add Phase 5 — Documentation Analysis**

(See full plan section in brainstorming output for complete content)

- [ ] **Step 7: Add Phase 6 — Scorecard Calculation**

(See full plan section in brainstorming output for complete content)

- [ ] **Step 8: Add issue categorization and output format**

(See full plan section in brainstorming output for complete content)

- [ ] **Step 9: Commit the skill**

```bash
git add skills/code_review_skill.md
git commit -m "feat: add Code Review Skill v3 with 6-phase analysis pipeline"
```

---

### Task 2: Create HTML Report Generator Tool

**Files:**
- Create: `tools/code_review_generator.py`

- [ ] **Step 1: Write the Python report generator**

(See full plan - ReviewReportGenerator class with CSS, JavaScript, and HTML building methods)

- [ ] **Step 2: Test the report generator with sample data**

```bash
cd tools
python -c "
from code_review_generator import ReviewReportGenerator

sample_review = {
    'jira_key': 'TEST-001',
    'mr_number': 123,
    'scorecard': {
        'requirement_met': 95,
        'code_quality': 85,
        'test_coverage': 70,
        'documentation': 60,
        'final_score': 84.4,
        'final_grade': 'B',
        'status': 'Changes Needed'
    },
    'phases': {
        'requirement_analysis': {
            'plain_english': 'Allow new users to sign up',
            'acceptance_criteria': ['AC1', 'AC2', 'AC3']
        }
    },
    'issues': [
        {
            'category': 'Security',
            'severity': 'P0',
            'file': 'src/auth.py',
            'line': 42,
            'issue': 'SQL injection',
            'why': 'String concat in query',
            'fix': 'Use parameterized query'
        }
    ],
    'file_breakdown': {}
}

gen = ReviewReportGenerator()
path = gen.generate(sample_review, 'TEST-001')
print(f'Generated: {path}')
"
```

- [ ] **Step 3: Commit the tool**

```bash
git add tools/code_review_generator.py
git commit -m "feat: add HTML report generator for code reviews"
```

---

### Task 3: Create MR Comment Formatter

**Files:**
- Create: `tools/code_review_reporter.py`

- [ ] **Step 1: Write the MR comment formatter**

(See full plan - MRCommentFormatter class)

- [ ] **Step 2: Test the comment formatter**

```bash
cd tools
python -c "
from code_review_reporter import MRCommentFormatter

sample_review = {
    'scorecard': {
        'requirement_met': 95,
        'code_quality': 85,
        'test_coverage': 70,
        'documentation': 60,
        'final_score': 84.4,
        'final_grade': 'B',
        'status': 'Changes Needed'
    },
    'issues': [
        {
            'category': 'Security',
            'severity': 'P0',
            'issue': 'SQL injection in email lookup'
        },
        {
            'category': 'Testing',
            'severity': 'P1',
            'issue': 'Missing error case tests'
        }
    ]
}

comment = MRCommentFormatter.format_comment(sample_review, '/reviews/review-PROJ-123.html')
print(comment)
"
```

- [ ] **Step 3: Commit the reporter**

```bash
git add tools/code_review_reporter.py
git commit -m "feat: add MR comment formatter for code reviews"
```

---

### Task 4: Update Code Review Agent v3

**Files:**
- Modify: `agents/code_review_agent.md`

Replace entire file with v3.0 content (see full plan for complete agent definition with all phases, examples, and MCP integration points)

- [ ] **Step 1: Replace agents/code_review_agent.md**

- [ ] **Step 2: Commit the updated agent**

```bash
git add agents/code_review_agent.md
git commit -m "feat: upgrade Code Review Agent to v3.0 (requirement-driven)"
```

---

### Task 5: Validation & Integration Test

**Files:**
- Test: Create manual test workflow

- [ ] **Step 1: Verify all pieces integrate**

```bash
# Check skill exists and is complete
wc -l skills/code_review_skill.md
# Should be > 500 lines

# Check tools exist and are syntactically correct
python -m py_compile tools/code_review_generator.py
python -m py_compile tools/code_review_reporter.py

# Expected: No errors
```

- [ ] **Step 2: Test the full pipeline with sample data**

(See full plan for complete test script)

- [ ] **Step 3: Verify HTML report opens in browser**

```bash
# Open the generated report
open reviews/review-DEMO-001-*.html

# Check: Can you see the scorecard, issues, suggestions? All elements visible?
```

- [ ] **Step 4: Commit test results**

```bash
git add -A
git commit -m "test: validate Code Review Agent v3 integration end-to-end"
```

---

### Task 6: Documentation & README

**Files:**
- Create: `tools/CODE_REVIEW_TOOL_README.md`

- [ ] **Step 1: Write tool documentation**

(See full plan - comprehensive tool documentation)

- [ ] **Step 2: Commit the documentation**

```bash
git add tools/CODE_REVIEW_TOOL_README.md
git commit -m "docs: add Code Review Tools documentation"
```

---

## Plan Context

**Repository:** awesome-prompts (AI agent/skill templates)  
**Branch:** release/4.2.0  
**Existing Code Review Agent:** v2.0 (design-focused, generic)  
**Enhancement:** v3.0 adds requirement-driven validation  

**Integration Points:**
- MCP JIRA Server (fetch requirements)
- MCP VCS Server (GitHub/GitLab/Bitbucket abstraction)
- Reuses existing code_review_agent.md checklist from v2.0

**Dependencies:**
- Python 3.8+ (tools)
- HTML5/CSS/JavaScript (report generation, no external libs)
- Git (version control)

**Test Coverage:**
- Sample data pipeline test
- HTML report generation test
- MR comment formatting test
- End-to-end integration validation

---

## Full Detailed Content

See docs/superpowers/specs/2026-05-25-code-review-agent-v3-design.md for:
- Complete phase implementations
- Detailed code examples per language
- Full HTML generator code
- Complete MRCommentFormatter code
- Sample review output
- Architecture diagrams
