# 📝 Feedback System Guide

This feedback system allows you to report issues, suggest improvements, and help the exporter and tools evolve based on real usage.

## How to Add Feedback

### Option 1: Quick Feedback (Recommended)

Add your feedback to `feedback.yaml` in this directory:

```yaml
- date: 2026-06-01
  category: exporter
  type: bug
  title: "Interactive exporter times out on large projects"
  description: "When exporting 33 skills to 8 platforms, it takes >30 seconds"
  severity: medium
  status: open
  assignee: ""
  labels: [performance, exporter]

- date: 2026-06-01
  category: interactive-mode
  type: feature-request
  title: "Add search/filter to skill selection"
  description: "Hard to find specific skills when there are 33 of them. Need search."
  severity: low
  status: open
  labels: [ux, search, filtering]

- date: 2026-06-01
  category: documentation
  type: improvement
  title: "Add more examples for custom Java project setup"
  description: "EXPORTER_QUICK_START only shows Python and React examples"
  severity: low
  status: open
  labels: [docs, java, examples]
```

### Option 2: Structured Feedback File

Each feedback item should have:
- **date**: When you noticed the issue (YYYY-MM-DD)
- **category**: Which tool/component (exporter, interactive-mode, agents, skills, documentation, cli, etc.)
- **type**: bug, feature-request, improvement, performance, security, documentation
- **title**: Short, clear summary
- **description**: Details, steps to reproduce, expected vs actual
- **severity**: critical, high, medium, low
- **status**: open, in-progress, resolved, duplicate, wontfix
- **assignee**: Empty or team member name
- **labels**: Tags for grouping ([performance], [ux], [java], etc.)

---

## Feedback Categories

### 1. Exporter Issues
```yaml
category: exporter
# Issues with export functionality, file generation, platforms
```

**Examples:**
- "Export times out with 8 platforms"
- "Generated .cursor/ files have wrong format"
- "Missing support for [new platform]"

### 2. Interactive Mode
```yaml
category: interactive-mode
# Issues with the guided wizard workflow
```

**Examples:**
- "Can't deselect all platforms"
- "Selection menu loops infinitely"
- "Need keyboard shortcuts for selection"

### 3. Agents/Skills
```yaml
category: agents
category: skills
# Feedback about specific agents or skills
```

**Examples:**
- "Implementation Agent doesn't handle async code well"
- "Database Skill missing PostgreSQL specific patterns"
- "Need a mobile app development skill"

### 4. Documentation
```yaml
category: documentation
# Documentation gaps, unclear instructions, missing examples
```

**Examples:**
- "EXPORTER_QUICK_START doesn't explain custom selection"
- "No examples for Go/Rust projects"

### 5. CLI
```yaml
category: cli
# Command-line interface improvements
```

**Examples:**
- "Add --json output format"
- "Need progress bar for exports"

### 6. Performance
```yaml
category: performance
# Speed, memory, resource usage
```

**Examples:**
- "Discovery takes 5 seconds, too slow"
- "Memory usage spikes with large projects"

---

## Feedback Types

### Bug 🐛
```yaml
type: bug
severity: high
description: |
  What happens: Export fails silently
  Expected: Error message with cause
  Steps to reproduce:
    1. Run interactive_exporter.py
    2. Select > 100 files
    3. Click export
```

### Feature Request ⭐
```yaml
type: feature-request
severity: medium
description: |
  Would like to: Export only agent files (skip skills)
  Why: Our team uses custom skills, not the built-in ones
  Example: python3 exporter.py --agents-only
```

### Improvement 💡
```yaml
type: improvement
severity: low
description: |
  Current: Menu shows all platforms in alphabetical order
  Better: Group by IDE type (IDEs, CLIs, APIs)
  Benefit: Easier to find related platforms
```

### Performance 🚀
```yaml
type: performance
severity: high
description: |
  Issue: Exporting to all 8 platforms takes 45 seconds
  Expected: < 10 seconds
  Bottleneck: File discovery or writing?
```

### Security 🔒
```yaml
type: security
severity: critical
description: |
  Issue: Agent files might contain API keys in examples
  Risk: Credentials exposed if committed to public repo
  Solution: Scan for sensitive patterns in frontmatter
```

### Documentation 📚
```yaml
type: documentation
severity: low
description: |
  Missing: How to use agents in Python projects
  Link: tools/INTERACTIVE_EXPORTER_README.md
  Needs: Python-specific workflow example
```

---

## Severity Levels

### Critical 🔴
- **Impact:** System broken, cannot use exported files
- **Fix Time:** Urgent (< 1 day)
- **Examples:** Export generates invalid YAML, wizard crashes

### High 🟠
- **Impact:** Major feature broken or significantly impaired
- **Fix Time:** High priority (< 1 week)
- **Examples:** Performance degrades 10x, UI unresponsive

### Medium 🟡
- **Impact:** Feature partially broken or inconvenient
- **Fix Time:** Normal priority (< 2 weeks)
- **Examples:** Custom selection needs 3 steps instead of 1

### Low 🟢
- **Impact:** Nice to have, workaround exists
- **Fix Time:** Low priority (< 1 month)
- **Examples:** Add more documentation, improve message wording

---

## Status Tracking

| Status | Meaning | Next Step |
|--------|---------|-----------|
| **open** | Reported, not yet looked at | Needs triage |
| **in-progress** | Someone is working on it | Monitor progress |
| **resolved** | Fixed, merged, or documented | Verify fix |
| **duplicate** | Already reported (see labels) | Reference original |
| **wontfix** | Rejected reason in comments | Accept as-is |

---

## Labels for Organization

Use labels to group related feedback:

**By Technology:**
- `[java]` `[python]` `[typescript]` `[go]` `[rust]`

**By Component:**
- `[exporter]` `[interactive-mode]` `[discovery]` `[export]`
- `[agents]` `[skills]` `[documentation]`

**By Severity/Impact:**
- `[performance]` `[security]` `[ux]` `[api]`
- `[blocking]` `[regression]` `[enhancement]`

**By Platform:**
- `[claude]` `[copilot]` `[cursor]` `[windsurf]` `[gemini]`

---

## Real-World Examples

### Example 1: Bug Report

```yaml
- date: 2026-06-01
  category: exporter
  type: bug
  title: "Export fails when project path contains spaces"
  description: |
    Tried to export to "/Users/me/My Projects/test"
    Got error: "/Users/me/My: no such directory"
    
    Workaround: Rename folder to remove spaces
    
    Root cause: Path not quoted in subprocess call
  severity: high
  status: open
  labels: [bug, exporter, blocking]
```

### Example 2: Feature Request

```yaml
- date: 2026-06-01
  category: interactive-mode
  type: feature-request
  title: "Add 'recommended' preset for team setup"
  description: |
    Currently options are: all, core, custom, minimal
    
    Need: "Team Standard" preset that includes:
    - Code Review Agent
    - Security Auditor Agent
    - All backend skills
    - All testing skills
    
    This is what every team should start with
  severity: low
  status: open
  labels: [feature-request, ux, preset]
```

### Example 3: Performance

```yaml
- date: 2026-06-01
  category: performance
  type: performance
  title: "Discovery takes 8 seconds with 50 skill files"
  description: |
    Measured time from start to "Found X skills":
    - 33 skills: 2.1 seconds
    - 50 skills: 8.3 seconds
    - 100 skills: 22 seconds
    
    Seems exponential, not linear
    Likely cause: Parsing YAML 50+ times in loop
    
    Suggestion: Parse once, cache results
  severity: medium
  status: open
  labels: [performance, discovery, optimization]
```

### Example 4: Documentation

```yaml
- date: 2026-06-01
  category: documentation
  type: documentation
  title: "Missing: How to customize exported agents"
  description: |
    User can export agents, but no docs on:
    - How to modify an agent after export
    - How to create a custom agent based on exported one
    - How to override agent behavior in IDE
    
    Add section to EXPORTER_QUICK_START.md
  severity: low
  status: open
  labels: [docs, agents, customization]
```

---

## How Feedback is Used

### System Monitoring 📊
The system reads `feedback.yaml` daily to:
- Count issues by category and severity
- Identify top 5 pain points
- Track resolution time
- Measure improvement over time

### Improvement Cycle 🔄
1. **Collect** — You add feedback to `feedback.yaml`
2. **Analyze** — System groups by severity and frequency
3. **Prioritize** — High-impact items get worked on first
4. **Implement** — Code changes or documentation updates
5. **Verify** — Feedback marked as resolved
6. **Close** — User confirms fix works

### AI Agent Self-Improvement 🤖
The Feedback Analyzer Agent:
- Reads all feedback weekly
- Generates improvement tasks
- Updates agent behavior based on common issues
- Suggests documentation improvements

---

## Adding Feedback

### Via YAML (Recommended)

```bash
# Edit the feedback file
nano .feedback/feedback.yaml

# Or append new feedback
cat >> .feedback/feedback.yaml << 'EOF'
- date: 2026-06-01
  category: exporter
  type: bug
  title: "Your issue here"
  description: "Details..."
  severity: medium
  status: open
  labels: [tag1, tag2]
EOF
```

### Via Script (Coming Soon)

```bash
# Future: interactive feedback prompt
python3 tools/feedback_submit.py
# Guided wizard to create structured feedback
```

### Via GitHub Issues (Alternative)

If you prefer GitHub, issues tagged with `[feedback]` are automatically synced to this file:
- Create issue: `[feedback] Title of issue`
- System reads it and adds to `feedback.yaml`

---

## Reviewing Feedback

### See All Feedback

```bash
# View human-readable summary
cat .feedback/FEEDBACK_SUMMARY.md

# View raw YAML
cat .feedback/feedback.yaml

# See stats
python3 tools/feedback_analyzer.py --stats
```

### See Feedback by Category

```bash
python3 tools/feedback_analyzer.py --category exporter
python3 tools/feedback_analyzer.py --category agents
python3 tools/feedback_analyzer.py --severity high
```

### See Most Common Issues

```bash
python3 tools/feedback_analyzer.py --top-issues 10
```

---

## Feedback Impact Examples

### Feedback → Feature: "Need search in skill selection"
```
Feedback date: 2026-06-01
Status: in-progress
Impact: 5 people reported same issue
Solution: Added search/filter to interactive mode
Merged: 2026-06-15
```

### Feedback → Performance: "Export takes too long"
```
Feedback date: 2026-06-01
Status: resolved
Root cause: YAML parsing 33 times (should be once)
Fix: Cache parsed results
Speed improvement: 8s → 1.2s (85% faster)
Merged: 2026-06-10
```

### Feedback → Documentation: "No Python examples"
```
Feedback date: 2026-06-01
Status: resolved
Action: Added Python workflow to EXPORTER_QUICK_START.md
Merged: 2026-06-08
```

---

## Guidelines

✅ **Good Feedback:**
- Specific and actionable
- Includes steps to reproduce (for bugs)
- Has context (what were you trying to do?)
- Suggests solution if known

❌ **Unclear Feedback:**
- "It doesn't work" (what doesn't work? when?)
- "Too slow" (compared to what? how slow?)
- "Bad UI" (which part? what's confusing?)

---

## Questions?

- **How often is feedback reviewed?** → Weekly, with daily automated analysis
- **Will my feedback be acknowledged?** → Yes, status will update as it's triaged
- **Can I see what feedback others gave?** → Yes, `FEEDBACK_SUMMARY.md` is public
- **What if my feedback is marked wontfix?** → Reasoning will be explained
- **Can I edit feedback after submitting?** → Yes, just update `feedback.yaml`

---

## Next Steps

1. **Read** — This guide (you just did!)
2. **Add** — Your first feedback item to `feedback.yaml`
3. **Track** — Watch it get triaged and resolved
4. **Celebrate** — See improvement in the tool

Thank you for helping make this system better! 🙏
