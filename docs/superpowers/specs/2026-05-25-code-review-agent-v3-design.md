# Code Review Agent v3 (Requirement-Driven) — Design Spec

**Date:** 2026-05-25  
**Status:** Design Phase  
**Version:** 3.0  

---

## 1. Overview

**Code Review Agent v3** enhances the existing Code Review Agent (v2.0) by adding **requirement-driven validation**. Instead of reviewing code in isolation, it validates that PR/MR changes actually implement what was requested in the JIRA ticket.

### Purpose
To ensure that:
- ✅ Code implements the requirement (100% requirement coverage)
- ✅ Code is well-designed (SOLID, patterns, security)
- ✅ Code is testable (adequate test coverage)
- ✅ Code is documented (API docs, comments)

### Key Innovation
Combines **requirement validation** (new) + **code quality review** (existing v2.0 checklist) in a single agent with detailed scoring and interactive reporting.

---

## 2. Input & Data Access

### Input
- **JIRA Number** (e.g., `PROJ-123`)
- User provides the number or system provides it

### Data Sources (via MCP)
The agent receives pre-fetched data from MCP servers:

| Source | Data | Handled By | Notes |
|--------|------|-----------|-------|
| JIRA | Requirement text, acceptance criteria, description | MCP JIRA server | Agent receives already-formatted text |
| PR/MR | Code diff, commit messages, files changed | MCP VCS server (GitHub/GitLab/Bitbucket) | Agent receives diff + file contents |
| VCS | Comment posting capability | MCP VCS server | Agent calls MCP to post comments |

**Agent Responsibility:** Review logic only. Data fetching is abstracted.

---

## 3. Processing Pipeline

### Phase 1: Requirement Analysis
**Input:** JIRA ticket text  
**Output:** Layman's terms summary + acceptance criteria list

```
Step 1: Parse requirement
  - Extract feature description
  - List acceptance criteria (AC1, AC2, ...)
  - Identify scope boundaries

Step 2: Translate to layman's terms
  - Simplify technical jargon
  - Highlight "what success looks like"
  - Note any assumptions or constraints

Output Example:
  Feature: User Registration
  In Plain English: "Allow new users to sign up with email and password"
  Acceptance Criteria:
  - User can enter email and password
  - Email validation is enforced
  - Passwords are hashed securely
  - Success notification sent
```

### Phase 2: Requirement Validation (New)
**Input:** Code diff + Requirement  
**Output:** Coverage % + gaps

```
Step 1: Map changes to requirements
  - Which files implement which AC?
  - Are all ACs addressed in code?
  - Any over-engineering (unnecessary features)?

Step 2: Score requirement coverage
  - 100% = All AC implemented + no extra scope
  - 90-99% = All AC implemented, minor gaps
  - 75-89% = Most AC implemented, notable gaps
  - <75% = Incomplete implementation

Output: Requirement Met: 95% (with gap list)
```

### Phase 3: Code Quality Review (Existing v2.0 + Enhanced)
**Input:** Code diff  
**Output:** Issues by category + severity

Reuse existing `code_review_agent.md` checklist:
- Structure & Design (SRP, abstraction)
- SOLID Principles
- Patterns & Best Practices
- Performance & Scalability
- Security
- Testing & Documentation

**Enhanced for v3:** Rate each category as % completion:
- Design Quality: 85%
- SOLID Adherence: 90%
- Pattern Usage: 80%
- Performance: 95%
- Security: 100%
- Testing: 70%
- Documentation: 60%

### Phase 4: Test Coverage Analysis
**Input:** Code diff + test files  
**Output:** Coverage % + gaps

```
Analysis:
- Lines of code added/modified
- Test lines added
- Inferred coverage % (code changes / test coverage)
- Missing test scenarios:
  - Happy path tests: ✓
  - Error cases: ✗
  - Edge cases: ⚠️
```

### Phase 5: Documentation Analysis
**Input:** Code diff  
**Output:** Documentation % + gaps

```
Analysis:
- Public methods documented? (JSDoc/docstrings/Javadoc)
- Parameters documented?
- Return values documented?
- Exceptions documented?
- Usage examples provided?
- Complex logic explained with comments?
```

### Phase 6: Scorecard Calculation
**Input:** All % scores from phases 1-5  
**Output:** Final grade

```
Scorecard:
- Requirement Met: 95%
- Code Quality: 85%
- Test Coverage: 70%
- Documentation: 60%

Final Grade: B (weighted average)
  = (95 * 0.4) + (85 * 0.3) + (70 * 0.2) + (60 * 0.1)
  = 38 + 25.5 + 14 + 6 = 83.5 → B
```

**Grading Scale:**
- A (90-100): Excellent — minimal issues
- B (80-89): Good — some improvements needed
- C (70-79): Fair — notable gaps
- D (60-69): Weak — significant issues
- F (<60): Failing — not ready to merge

---

## 4. Output Artifacts

### 4.1 Local HTML Report
**File:** `reviews/review-{JIRA-NUMBER}-{timestamp}.html`  
**Format:** Self-contained HTML + CSS + JavaScript (no external dependencies)

#### Sections:

**Section 1: Scorecard & Executive Summary**
```
┌─────────────────────────────────────┐
│ JIRA: PROJ-123                      │
│ PR: #456 (main ← feature/user-auth) │
│                                     │
│ Requirement Met:   95% ████████░   │
│ Code Quality:      85% ███████░░   │
│ Test Coverage:     70% ██████░░░   │
│ Documentation:     60% ██████░░░░  │
│                                     │
│ Final Grade: B (83.5/100)          │
│ Status: ⚠️ Changes Needed            │
└─────────────────────────────────────┘

Summary: Feature mostly complete. Needs better test coverage and docs.
```

**Section 2: Requirement Validation**
- Requirement description (plain English)
- Acceptance criteria checklist:
  - ✅ AC1: Email validation enforced
  - ✅ AC2: Password hashing implemented
  - ⚠️ AC3: Notification email sending (partial)
  - ❌ AC4: Rate limiting (not implemented)
- Gaps identified + severity

**Section 3: Code Quality Issues**
- Grouped by severity (P0, P1, P2, P3)
- Grouped by category (Design, SOLID, Security, etc.)
- Expandable per issue:
  - File & line number
  - Issue description
  - Why it matters
  - Suggested fix
  - Code example
  - Reference (SOLID principle, pattern, etc.)

**Section 4: File-by-File Breakdown**
- List of changed files with expandable details:
  ```
  src/auth/register.py (89 lines added)
    - Issues: 1 P1, 2 P2
    - Coverage: 75%
    - Docs: 80%
    [Expand ▼]
  
  tests/test_register.py (45 lines added)
    - Issues: None
    - Coverage: Good
    [Expand ▼]
  ```

**Section 5: Visual Heatmap**
- File matrix showing severity of issues per file (color-coded)
- Darker = more issues
- Help identify problem areas at a glance

**Section 6: Comparison View**
- Side-by-side: "What was asked" vs "What was delivered"
- Requirement text on left, code snippets on right
- Highlighting for matches/gaps

**Section 7: Suggestions & Fixes**
- Ranked by impact
- Code examples provided
- Estimated effort to fix

**Section 8: Test & Documentation Analysis**
- Coverage gap analysis (missing test scenarios)
- Documentation gap analysis (missing docs)
- Recommendations for improvements

---

### 4.2 MR Comment (Posted to VCS)
**Format:** Concise summary posted to PR/MR via MCP

```markdown
## 🔍 Code Review Complete

### Scorecard
- Requirement Met: 95% ████████░
- Code Quality: 85% ███████░░
- Test Coverage: 70% ██████░░░
- Documentation: 60% ██████░░░░

**Final Grade: B** (Changes Needed)

---

### Critical Issues (P0/P1)
1. **[Security] P0** — SQL injection risk in user lookup
2. **[Testing] P1** — Missing error case tests (400, 500)

---

### Action Items Before Merge
- [ ] Fix SQL injection vulnerability
- [ ] Add error case test coverage
- [ ] Document the rate-limiting strategy

---

### Full Analysis
See detailed report: `/reviews/review-PROJ-123-20260525T143022.html`

_Review generated by Code Review Agent v3_
```

---

## 5. Integration Points

### MCP Servers Required
1. **JIRA MCP Server**
   - Fetch requirement by ticket number
   - Parse description, AC, acceptance criteria
   - Return structured format

2. **VCS MCP Server** (GitHub/GitLab/Bitbucket abstraction)
   - Fetch PR/MR details (diff, files, commits)
   - Post comments to PR/MR
   - Return structured diff

### Agent Responsibilities
- Review logic only
- Scoring & grading
- HTML generation
- Issue categorization
- Suggestion generation

---

## 6. Architecture

### File Structure
```
agents/
  code_review_agent.md          ← Updated with v3 enhancements
  
skills/
  code_review_skill.md          ← New (reusable review logic)
  
tools/
  code_review_generator.py      ← Generate HTML reports
  
reviews/                        ← Output directory (local)
  review-PROJ-123-*.html
```

### Workflow
```
User Input (JIRA number)
    ↓
MCP JIRA Server (fetch requirement)
    ↓
MCP VCS Server (fetch PR/MR code)
    ↓
Code Review Agent v3 (5-phase review)
    ↓
Generate HTML report (local file)
    ├─ Scorecard
    ├─ Requirement validation
    ├─ Code issues
    ├─ File breakdown
    ├─ Heatmap
    └─ Suggestions
    ↓
Post MR comment (via MCP VCS)
    ↓
Output: "Review complete. See /path/to/report.html"
```

---

## 7. Data Model

### JIRA Requirement (Input)
```json
{
  "key": "PROJ-123",
  "summary": "User Registration with Email Validation",
  "description": "Allow new users to sign up...",
  "acceptance_criteria": [
    "User can enter email and password",
    "Email validation is enforced",
    "Passwords are hashed securely",
    "Success notification sent"
  ],
  "scope_notes": "Desktop and mobile friendly"
}
```

### Review Result (Internal)
```json
{
  "jira_key": "PROJ-123",
  "mr_number": 456,
  "phases": {
    "requirement_analysis": {
      "plain_english": "...",
      "acceptance_criteria": [...]
    },
    "requirement_validation": {
      "coverage": 95,
      "gaps": [...]
    },
    "code_quality": {
      "design": 85,
      "solid": 90,
      "patterns": 80,
      "performance": 95,
      "security": 100,
      "testing": 70,
      "documentation": 60
    },
    "test_coverage": 70,
    "documentation": 60
  },
  "scorecard": {
    "requirement_met": 95,
    "code_quality": 85,
    "test_coverage": 70,
    "documentation": 60,
    "final_grade": "B",
    "final_score": 83.5
  },
  "issues": [
    {
      "category": "Security",
      "severity": "P0",
      "file": "src/auth/register.py",
      "line": 42,
      "issue": "SQL injection vulnerability",
      "suggestion": "Use parameterized queries"
    }
  ]
}
```

---

## 8. Success Criteria

### Phase Completion
- ✅ Requirement analysis accurate (plain English + ACs)
- ✅ Requirement validation detects missing features
- ✅ Code quality review consistent with v2.0 standards
- ✅ Scorecard calculation is transparent (weights visible)
- ✅ HTML report is readable and interactive
- ✅ MR comment is actionable and concise
- ✅ Issues are prioritized by severity
- ✅ Suggestions include code examples

### Quality Gates
- No false positives (issues that aren't real)
- All P0/P1 issues must be real & actionable
- Grade distribution: F=never, D=rare, C=acceptable, B=good, A=excellent
- Report generation <30 seconds

---

## 9. Future Enhancements (Not in v3.0)

- Auto-fix suggestions (generate patches)
- AI-powered code suggestions (LLM-based)
- Trend tracking (grade history per repo)
- Custom scoring weights per team
- Integration with CI/CD (block merge on F grade)
- Diff comments (inline on PR/MR)

---

## 10. FAQ

**Q: Why not post the full review as a comment?**  
A: MR comments should be scannable. Full details in HTML keeps comments readable.

**Q: What if JIRA requirement is vague?**  
A: Agent translates to best understanding; notes vagueness in report. Suggest clarification with team.

**Q: Does it work with all programming languages?**  
A: Yes—patterns are universal. Code examples might be language-specific.

**Q: Can teams customize the scorecard weights?**  
A: Yes—future enhancement. Default: Requirement (40%), Code Quality (30%), Testing (20%), Docs (10%).

**Q: What if no tests exist?**  
A: Test coverage scored as low; noted as critical gap in suggestions.

---

## 11. Related Documents

- **Existing Agent:** `agents/code_review_agent.md` (v2.0 — design review focused)
- **Checklist Reference:** Code Review Checklist (6 phases: Structure, SOLID, Patterns, Performance, Security, Testing)
- **Master Rules:** `instructions/master_instruction_set.md`
- **Severity Scale:** P0 (critical), P1 (significant), P2 (quality), P3 (minor)

---

## Sign-Off

- **Design Date:** 2026-05-25
- **Designer:** Claude Code
- **Status:** Ready for implementation plan
