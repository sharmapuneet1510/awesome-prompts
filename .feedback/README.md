# 💬 Feedback System

This directory contains tools for collecting, analyzing, and using feedback to continuously improve the exporter and AI system.

## Quick Start

### Add Feedback
```bash
# Edit feedback file
nano feedback.yaml

# Add a new item:
- date: 2026-06-01
  category: exporter
  type: bug
  title: "Your issue here"
  description: "Details about the issue"
  severity: medium
  status: open
  labels: [exporter, bug]
```

### View Feedback
```bash
# See all feedback summary
python3 ../tools/feedback_analyzer.py --summary

# See top issues
python3 ../tools/feedback_analyzer.py

# Filter by category
python3 ../tools/feedback_analyzer.py --category exporter

# Filter by severity
python3 ../tools/feedback_analyzer.py --severity high
```

### Generate Tasks
```bash
# See improvement tasks from feedback
python3 ../tools/feedback_processor.py --generate-tasks

# See detailed analysis
python3 ../tools/feedback_processor.py --analyze
```

## Files in This Directory

| File | Purpose |
|------|---------|
| `README.md` | This file — overview and quick start |
| `FEEDBACK_GUIDE.md` | Complete guide on how to add feedback |
| `feedback.yaml` | The feedback database (add your items here!) |
| `FEEDBACK_SUMMARY.md` | Auto-generated summary of all feedback |

## File Structure

```
.feedback/
├── README.md                    ← You are here
├── FEEDBACK_GUIDE.md            ← How to add feedback
├── feedback.yaml                ← Add your feedback here
├── FEEDBACK_SUMMARY.md          ← Auto-generated summary
├── .cache/                      ← Cached analysis (auto-generated)
│   ├── analysis.json
│   └── improvement_tasks.json
└── .github/
    └── workflows/               ← Future: auto-generate tasks
```

## The Feedback Loop

```
┌──────────────────┐
│  ADD FEEDBACK    │ ← You add issues/suggestions
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│  ANALYZE         │ ← System reads feedback.yaml
│  PATTERNS        │ ← Identifies trends
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│  GENERATE        │ ← Creates improvement tasks
│  TASKS           │ ← Prioritizes by severity
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│  IMPLEMENT       │ ← Changes made to fix/improve
│  FIX/FEATURE     │ ← Code and documentation updated
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│  MARK RESOLVED   │ ← Feedback status updated
│  UPDATE FEEDBACK │ ← Loop continues
└──────────────────┘
```

## What Can You Feedback About?

### 🐛 Bugs
- "Export fails when path has spaces"
- "Interactive mode freezes on large projects"
- "Agent names are truncated in menu"

### ⭐ Features
- "Need search when selecting skills"
- "Add --json output format"
- "Support for new programming language"

### 💡 Improvements
- "Menu items should be grouped better"
- "More verbose error messages"
- "Faster discovery caching"

### 📚 Documentation
- "Missing examples for Python projects"
- "No guide on customizing exported agents"
- "Unclear troubleshooting steps"

### 🚀 Performance
- "Discovery takes too long"
- "Memory usage is high"
- "Export should have progress bar"

### 🔒 Security
- "Agent examples might expose API keys"
- "Credentials could be logged"

## Example Feedback Items

### Good Bug Report
```yaml
- date: 2026-06-01
  category: exporter
  type: bug
  title: "Export fails with paths containing spaces"
  description: |
    Tried to export to "/Users/me/My Project/test"
    Got error: "/Users/me/My: no such directory"
    
    Workaround: Rename to remove spaces
    Cause: Path not quoted in subprocess
  severity: high
  status: open
  labels: [bug, exporter, blocking]
```

### Good Feature Request
```yaml
- date: 2026-06-01
  category: interactive-mode
  type: feature-request
  title: "Add search to skill selection menu"
  description: |
    Problem: With 33 skills, hard to find the one you need
    Requested: Type to filter (e.g., "python" shows Python skills)
    Benefit: Faster selection, better UX
  severity: low
  status: open
  labels: [feature-request, ux, search]
```

### Good Documentation Request
```yaml
- date: 2026-06-01
  category: documentation
  type: documentation
  title: "Add Java project example to EXPORTER_QUICK_START"
  description: |
    Currently only Python and React examples
    Need: Spring Boot / Java example
    Link to section: "Common Use Cases"
  severity: low
  status: open
  labels: [docs, java, examples]
```

## Feedback Status Workflow

```
┌─────────────────┐
│  OPEN (default) │  ← You just reported it
└────────┬────────┘
         │ (someone starts working on it)
         ↓
┌────────────────────┐
│  IN-PROGRESS       │  ← Being fixed/discussed
└────────┬───────────┘
         │ (fix is complete)
         ↓
┌────────────────────┐
│  RESOLVED          │  ← Fixed and merged
└────────┬───────────┘
         │ (you can verify)
         ↓
   Closed / Archived

Alternative paths:
  DUPLICATE  → Refers to existing issue
  WONTFIX    → Rejected with explanation
```

## Analyzing Feedback

### View Summary
```bash
python3 ../tools/feedback_analyzer.py --summary
```

Output:
```
📊 FEEDBACK SUMMARY
────────────────────────────────────────────────────────
Total Items:        15
Open:               9
Resolved:           6
Resolution Rate:    40.0%

BY CATEGORY:
  • exporter              4 items
  • interactive-mode      3 items
  • documentation         2 items
  • performance           2 items

BY SEVERITY:
  • high                  2 items
  • medium                4 items
  • low                   9 items

BY TYPE:
  • feature-request       6 items
  • bug                   5 items
  • improvement           3 items
  • documentation         1 item
```

### View Top Issues
```bash
python3 ../tools/feedback_analyzer.py --top-issues 5
```

### View by Category
```bash
python3 ../tools/feedback_analyzer.py --category exporter
```

### View by Severity
```bash
python3 ../tools/feedback_analyzer.py --severity high
```

## Generating Tasks

### Show All Tasks
```bash
python3 ../tools/feedback_processor.py --generate-tasks
```

Output:
```
📋 IMPROVEMENT TASKS (Generated from Feedback)
════════════════════════════════════════════════════
1. 🚨 Fix 2 critical issues
2. ⭐ Implement top 3 feature requests
3. 📚 Fill 2 documentation gaps
4. 🚀 Optimize 2 performance issues
5. 🔧 Export fails with paths containing spaces
6. 🔧 Interactive mode freezes on large projects
════════════════════════════════════════════════════
```

### Show Detailed Analysis
```bash
python3 ../tools/feedback_processor.py --analyze
```

## Integration with CI/CD

Add to your GitHub Actions or CI pipeline:

```yaml
# .github/workflows/feedback-analysis.yml
name: Feedback Analysis
on: [push, pull_request]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: python3 tools/feedback_processor.py --summary
      - run: python3 tools/feedback_analyzer.py --top-issues 5
```

## Tips for Good Feedback

✅ **DO:**
- Be specific and actionable
- Include steps to reproduce (for bugs)
- Suggest solutions if you have them
- Include context (what were you doing?)
- Add labels to group related items

❌ **DON'T:**
- "It doesn't work" (what doesn't work?)
- "Too slow" (how slow? compared to what?)
- "Bad UI" (which part? what's confusing?)
- Report the same issue multiple times
- Mix multiple issues in one item

## FAQ

**Q: How often is feedback reviewed?**
A: Analyzed daily, discussed weekly, prioritized monthly

**Q: Will my feedback be acknowledged?**
A: Yes, the feedback file will be updated with status changes

**Q: How are issues prioritized?**
A: By severity (critical → high → medium → low), then by frequency

**Q: Can I see what others reported?**
A: Yes, feedback.yaml is readable, and FEEDBACK_SUMMARY.md is public

**Q: Can feedback be confidential?**
A: Not currently, but we can add a private section if needed

**Q: What if I made a mistake in my feedback?**
A: Edit feedback.yaml directly to fix it

## Contact & Support

- **Have questions?** See `FEEDBACK_GUIDE.md`
- **Want to contribute?** Add feedback to `feedback.yaml`
- **Find a bug?** Report it (see FEEDBACK_GUIDE.md)
- **Suggest a feature?** Open a feature request

## Next Steps

1. **Read** `FEEDBACK_GUIDE.md` for detailed instructions
2. **Add** your first feedback item to `feedback.yaml`
3. **Watch** it get triaged and resolved
4. **Celebrate** improvements in the tool!

---

Thank you for helping improve this system! Your feedback makes it better for everyone. 🙏
