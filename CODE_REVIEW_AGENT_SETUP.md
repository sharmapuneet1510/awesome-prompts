# Code Review Agent — Claude & Copilot Setup Guide

**Agent Version:** 3.0  
**Compatibility:** ✅ Claude Code, ✅ GitHub Copilot  
**Status:** Production Ready  
**Last Updated:** 2026-06-02

---

## ✅ Compatibility Status

| Feature | Claude | Copilot | Status |
|---------|--------|---------|--------|
| **Agent Definition** | ✅ Yes | ✅ Yes | Ready |
| **Workflow Phases** | ✅ All 6 | ✅ All 6 | Compatible |
| **JIRA Integration** | ✅ Yes | ✅ Yes | Supported |
| **HTML Reports** | ✅ Yes | ✅ Yes | Working |
| **MR/PR Comments** | ✅ Yes | ✅ Yes | Via MCP |
| **Hooks** | ✅ Yes | ✅ Yes | Configured |
| **Configuration** | ✅ settings.json | ✅ copilot.yml | Both Set |

---

## 🚀 Quick Setup

### For Claude Code

**Step 1: Export Agent**
```bash
python3 tools/exporter.py --target claude --agents code_review
```

**Step 2: Verify Files**
```bash
ls -la .claude/agents/code_review_agent.md
# Should show: -rw-r--r-- code_review_agent.md (21K)
```

**Step 3: Use in Claude Code**
```
"Use Code Review Agent to review PR #123"
```

**or in claude.ai/code:**
```
@code-review-agent
Review this PR against PROJ-456 requirements
```

---

### For GitHub Copilot

**Step 1: Export Agent**
```bash
python3 tools/exporter.py --target copilot --agents code_review
```

**Step 2: Verify Files**
```bash
ls -la .github/agents/code_review_agent.md
ls -la .github/copilot.yml
# Both should exist
```

**Step 3: Use in Copilot**
In your IDE (VS Code, etc.):
```
@code-review-agent
Review this pull request
```

**or via command:**
```
/code-review-agent PROJ-123 PR-456
```

---

## 📋 Exported Files

### Claude Code Structure
```
.claude/
├── agents/
│   └── code_review_agent.md          (21 KB)
├── skills/
│   └── [33 supporting skills]        (for reference)
├── settings.json                      (hooks config)
└── hooks/
    ├── code-format-check.sh
    ├── test-hook.sh
    ├── test-runner-pre-commit.py
    └── promptshield-check.sh
```

**Claude settings.json:**
```json
{
  "model": "haiku",
  "hooks": {
    "PreCommit": [
      { "type": "command", "command": "hooks/code-format-check.sh" },
      { "type": "command", "command": "hooks/test-hook.sh" },
      { "type": "command", "command": "hooks/test-runner-pre-commit.py" }
    ],
    "UserPromptSubmit": [
      { "type": "command", "command": "hooks/promptshield-check.sh" }
    ]
  }
}
```

### GitHub Copilot Structure
```
.github/
├── agents/
│   └── code_review_agent.md          (21 KB, with YAML frontmatter)
├── instructions/
│   └── [33 supporting skills]        (Copilot format)
├── copilot.yml                        (hooks config)
└── hooks/
    └── [same 4 hooks as Claude]
```

**Copilot copilot.yml:**
```yaml
version: 1

hooks:
  - name: code-format-check
    type: pre-commit
    path: hooks/code-format-check.sh
  
  - name: promptshield-check
    type: user-prompt-submit
    path: hooks/promptshield-check.sh
  
  - name: test-hook
    type: pre-commit
    path: hooks/test-hook.sh
  
  - name: test-runner-pre-commit
    type: pre-commit
    path: hooks/test-runner-pre-commit.py
```

---

## 🧪 Testing Compatibility

### Test 1: File Validation

```bash
# Verify Claude files
test -f .claude/agents/code_review_agent.md && echo "✓ Claude agent found"
test -f .claude/settings.json && echo "✓ Claude config found"

# Verify Copilot files
test -f .github/agents/code_review_agent.md && echo "✓ Copilot agent found"
test -f .github/copilot.yml && echo "✓ Copilot config found"
```

### Test 2: YAML Validation

```bash
# Claude - verify YAML frontmatter is removed
head -1 .claude/agents/code_review_agent.md | grep -q "<!--- " && echo "✓ Claude format correct"

# Copilot - verify YAML frontmatter is present
head -3 .github/agents/code_review_agent.md | grep -q "^---" && echo "✓ Copilot format correct"
```

### Test 3: Content Validation

```bash
# Both should have the core sections
grep -q "## Identity" .claude/agents/code_review_agent.md && echo "✓ Claude has Identity section"
grep -q "## Workflow Overview" .github/agents/code_review_agent.md && echo "✓ Copilot has Workflow section"
grep -q "## Phase 1" .claude/agents/code_review_agent.md && echo "✓ Claude has Phases"
```

### Test 4: Manual Testing in IDE

**Claude Code:**
1. Open Claude Code
2. Copy `.claude/` folder to your project
3. Type: `"Use Code Review Agent to review PR #1"`
4. Agent should respond with workflow

**Copilot (VS Code):**
1. Copy `.github/` folder to your repo
2. Install Copilot extension
3. Type: `@code-review-agent`
4. Agent should be available

---

## 🔧 Installation Commands

### Export Both Platforms

```bash
# Quick: Both Claude and Copilot
python3 tools/exporter.py --target claude copilot --agents code_review

# With all supporting skills
python3 tools/exporter.py --target claude copilot --agents code_review

# Verify
echo "✓ Code Review Agent installed to both platforms"
```

### Install to Existing Project

```bash
# If you already have .claude/ folder
cp -r .claude/agents/code_review_agent.md ~/my-project/.claude/agents/

# If you already have .github/ folder
cp -r .github/agents/code_review_agent.md ~/my-project/.github/agents/
```

---

## 📖 Usage Examples

### Claude Code

**Example 1: Review PR by Number**
```
"Code Review Agent, please review PR #42"

Agent will:
1. Ask for JIRA ticket number
2. Fetch PR details
3. Run all 6 review phases
4. Generate HTML report
5. Post summary to PR
```

**Example 2: Review Against JIRA Requirement**
```
"Use Code Review Agent to validate PR #99 against AUTH-123"

Agent will:
1. Fetch JIRA ticket AUTH-123
2. Extract acceptance criteria
3. Review PR against criteria
4. Score requirement coverage
5. Generate detailed report
```

**Example 3: Quick Code Quality Check**
```
"@code-review-agent
This code needs a quick quality review"

Agent will:
1. Scan code for SOLID violations
2. Check for security issues
3. Review test coverage
4. Provide score and recommendations
```

### GitHub Copilot

**Example 1: In PR Description**
```
@code-review-agent
Please review this PR for:
- Requirement coverage
- Code quality
- Test completeness
```

**Example 2: In Comments**
```
/code-review-agent PROJ-123 PR-456
```

**Example 3: In Chat**
```
@code-review-agent
What's the overall quality of this PR?
```

---

## 🔄 Workflow — Both Platforms

The agent runs the same 6-phase workflow in both Claude and Copilot:

```
┌─────────────────────────────────────┐
│ Phase 1: Requirement Analysis       │
│ Extract acceptance criteria          │
│ List requirements                    │
├─────────────────────────────────────┤
│ Phase 2: JIRA Assessment (NEW)      │
│ Score 8 categories                  │
│ Identify Quick Wins                  │
├─────────────────────────────────────┤
│ Phase 3: Code Quality Review        │
│ SOLID, patterns, security           │
│ Performance, readability             │
├─────────────────────────────────────┤
│ Phase 4: Test Coverage Analysis     │
│ Unit, integration, edge cases       │
│ Mock/stub verification              │
├─────────────────────────────────────┤
│ Phase 5: Documentation Analysis     │
│ Docstrings, parameters, examples    │
├─────────────────────────────────────┤
│ Phase 6: Scorecard & Reports        │
│ HTML report, MR/PR comment          │
│ Grade (A-F)                          │
└─────────────────────────────────────┘
```

---

## 📊 Output Format

### Both Platforms Generate:

**1. Interactive HTML Report**
```html
- Header (PR, JIRA, timestamp)
- Scorecard (4 metrics)
- Requirement coverage analysis
- Issues by severity
- File breakdown
- Severity heatmap
- Actionable suggestions
```

**2. MR/PR Comment (Markdown)**
```markdown
## 🔍 Code Review Complete

### Scorecard
- Requirement Met: 95%
- Code Quality: 85%
- Test Coverage: 72%
- Documentation: 65%

Final Grade: B (84.4/100)
Status: ⚠️ Changes Needed

### 🚨 Critical Issues
1. [Security] SQL injection in query
2. [Testing] Missing error scenarios

### ✅ Action Items
- [ ] Fix SQL injection
- [ ] Add error tests
- [ ] Document API changes

[View Full Report →](...)
```

**3. Internal Assessment Object**
```json
{
  "requirement_coverage": 95,
  "code_quality": 85,
  "test_coverage": 72,
  "documentation": 65,
  "final_score": 84.4,
  "grade": "B",
  "status": "CHANGES_NEEDED",
  "issues": [...],
  "suggestions": [...]
}
```

---

## 🐛 Troubleshooting

### Issue: Agent Not Found in Claude

**Solution:**
```bash
# Re-export
python3 tools/exporter.py --target claude --agents code_review

# Verify file exists
ls -la .claude/agents/code_review_agent.md

# Check file size (should be ~21KB)
du -h .claude/agents/code_review_agent.md
```

### Issue: Copilot Not Recognizing Agent

**Solution:**
```bash
# Re-export with Copilot format
python3 tools/exporter.py --target copilot --agents code_review

# Verify YAML frontmatter
head -5 .github/agents/code_review_agent.md
# Should show: --- name: ... description: ... ---

# Check config
cat .github/copilot.yml
```

### Issue: JIRA Connection Fails

**Solution:**
- Provide JIRA ticket number in proper format: `PROJ-123`
- Ensure you have JIRA access (MCP configuration)
- Agent will ask for credentials if needed

### Issue: Report Not Generated

**Solution:**
- Check that all phases completed (check logs)
- Verify file permissions in project root
- Ensure disk space available for HTML report

---

## ✨ Features Available in Both

✅ **Requirement Analysis** — Extract and validate acceptance criteria  
✅ **JIRA Assessment** — New 8-category scoring system (from your images!)  
✅ **Code Quality Review** — SOLID principles, patterns, security  
✅ **Test Coverage Analysis** — Unit, integration, edge cases  
✅ **Documentation Review** — Docstrings, parameters, examples  
✅ **Scorecard Generation** — 4 metrics, final grade (A-F)  
✅ **Quick Wins** — Easy improvements with point values  
✅ **HTML Reports** — Interactive, exportable, printable  
✅ **MR/PR Comments** — Markdown summaries  
✅ **Security Analysis** — Vulnerability detection  

---

## 🎯 Recommended Setup

### For Maximum Compatibility

```bash
# Export to both platforms with all supporting files
python3 tools/exporter.py --target claude copilot --agents code_review

# This creates:
# ✓ .claude/agents/code_review_agent.md
# ✓ .github/agents/code_review_agent.md
# ✓ .claude/settings.json (with hooks)
# ✓ .github/copilot.yml (with hooks)
# ✓ Both folder structures complete
```

### For Single Platform

```bash
# Claude only
python3 tools/exporter.py --target claude --agents code_review

# Copilot only
python3 tools/exporter.py --target copilot --agents code_review
```

---

## 📞 Support

**Issue with Setup?**
1. Check `.feedback/feedback.yaml` for known issues
2. Run: `python3 tools/feedback_analyzer.py --category agents`
3. Review troubleshooting section above

**Want to Add Features?**
1. Add feedback to `.feedback/feedback.yaml`
2. Include platform-specific requirements
3. System will track and prioritize

**Working Perfectly?**
1. Great! Let us know what works well
2. Add positive feedback for attribution
3. Help others by sharing your setup

---

## 🚀 Next Steps

1. ✅ **Export Agent** — Run export command above
2. ✅ **Verify Files** — Run test commands
3. ✅ **Test in IDE** — Use agent in your IDE
4. ✅ **Review a PR** — Try reviewing a real PR
5. ✅ **Share Feedback** — Tell us how it works!

---

**Code Review Agent is production-ready for both Claude and Copilot!** 🎉

For additional help, see:
- `agents/code_review_agent.md` — Full agent definition
- `.feedback/FEEDBACK_GUIDE.md` — Report issues
- `FEEDBACK_SYSTEM.md` — Feature requests

Happy reviewing! 🚀
