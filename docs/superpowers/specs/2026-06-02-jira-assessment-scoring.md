# JIRA Change Request Assessment Scoring System

**Date:** 2026-06-02  
**Version:** 1.0  
**Status:** Design Review  
**Author:** Puneet Sharma

## Executive Summary

Enhance the Code Review Agent to evaluate JIRA change requests using a weighted scoring system based on 8 criteria. This enables objective, data-driven assessment of ticket quality and completeness before code review.

**Impact:**
- Identifies low-quality tickets early (before implementation)
- Guides teams on what makes a good requirement
- Provides actionable improvement recommendations
- Calculates impact of each improvement ("Quick Wins")

---

## Problem Statement

JIRA tickets often lack critical information, making implementation harder:
- ❌ Missing acceptance criteria → unclear requirements
- ❌ No story points → can't estimate effort
- ❌ Poor descriptions → implementation delays
- ❌ Inconsistent labels → bad discoverability
- ❌ Missing version → release tracking issues

**Current State:**
Code Review Agent validates code against requirements but doesn't assess the requirements themselves.

**Desired State:**
System automatically assesses JIRA tickets and provides:
1. Objective quality score (0-100)
2. Category breakdown (what's strong, what's weak)
3. Specific violations and recommendations
4. Quick wins (easy-to-fix improvements with point values)
5. Projected score after improvements

---

## Solution Design

### 1. Scoring Framework

**8 Weighted Categories:**

| # | Category | Weight | Max Points | Purpose |
|---|----------|--------|-----------|---------|
| 1 | Acceptance Criteria | 25% | 100 | Requirement clarity and coverage |
| 2 | Description Quality | 20% | 100 | Complete context and context |
| 3 | Naming Conventions | 15% | 100 | Title clarity and length |
| 4 | Linking | 15% | 100 | Relationship tracking |
| 5 | Labels | 10% | 100 | Categorization and discoverability |
| 6 | Version Management | 8% | 100 | Release/sprint tracking |
| 7 | Priority | 5% | 100 | Priority alignment |
| 8 | Story Points | 2% | 100 | Effort estimation |

**Score Calculation:**
```
Final Score = Σ(Category_Score × Category_Weight)

Example:
- AC (100 × 0.25) = 25.00
- Desc (70 × 0.20) = 14.00
- Naming (50 × 0.15) = 7.50
- Linking (100 × 0.15) = 15.00
- Labels (40 × 0.10) = 4.00
- Version (0 × 0.08) = 0.00
- Priority (100 × 0.05) = 5.00
- Points (50 × 0.02) = 1.00
─────────────────────────
TOTAL: 71.50/100
```

### 2. Thresholds

| Threshold | Score | Meaning | Action |
|-----------|-------|---------|--------|
| **PASS** | ≥ 60 | Good to proceed | Implement |
| **MINIMUM** | 60 | Acceptable | Review needed |
| **BLOCKER** | 40 | Critical issues | Return to requester |
| **FAIL** | < 40 | Major problems | Reject, request revision |

### 3. Category Validation Rules

#### Category 1: Acceptance Criteria (25%)
**Max Score: 100 points**

**Scoring Rules:**
- 100 pts: 5+ Given-When-Then criteria with positive AND negative scenarios
- 75 pts: 3-4 criteria, mixed scenarios
- 50 pts: 1-2 criteria or missing some scenarios
- 25 pts: Acceptance criteria mentioned but not well-defined
- 0 pts: No acceptance criteria

**Assessment:**
```
✓ Strengths:
  - 5 Given-When-Then criteria across 2 rules
  - Clear positive and negative test scenarios
  - Excellent coverage

⚠️ Violations:
  - Missing edge case scenarios
  - Unclear given/when/then boundaries
```

#### Category 2: Description Quality (20%)
**Max Score: 100 points**

**Required Sections:**
1. User Story Format: "As a [role], I want [feature], so that [benefit]"
2. Technical Notes: Implementation approach, constraints, dependencies
3. Files to Modify: Explicit list of files that will change
4. Acceptance Criteria: (separate from this category, but referenced)

**Scoring Rules:**
- 100 pts: All 4 sections complete and clear
- 75 pts: 3 sections complete
- 50 pts: 2 sections complete or incomplete
- 25 pts: 1 section or vague descriptions
- 0 pts: No meaningful description

**Example Violation:**
```
⚠️ Description Quality (70/100)
Strengths:
  - Rules clearly stated with descriptions
  - Acceptance criteria per rule

Violations:
  - Missing: User Story format ("As a...")
  - Missing: Technical Notes
  - Missing: Files to Modify
```

#### Category 3: Naming Conventions (15%)
**Max Score: 100 points**

**Rules for Story Tickets:**
- Recommended length: 5-15 words
- Should be: Specific, action-oriented, no special characters
- Should NOT: Contain pipes (|), semicolons, or line breaks
- Should NOT: Be generic ("Fix bug", "Add feature")

**Scoring Rules:**
- 100 pts: 5-15 words, clear, no special chars
- 75 pts: 16-20 words, clear
- 50 pts: 21-25 words OR contains special chars
- 25 pts: 26+ words OR multiple issues
- 0 pts: Completely unclear or no title

**Example Violation:**
```
⚠️ Naming Conventions (50/100)

Violation: Title is 22 words
  Current: "DQ Validation: CDE 2.31 Initial margin posted by the reporting 
           counterparty (pre-haircut) – Data Quality Validation Rules | Test"
  Recommended length: 5-15 words
  Suggestion: "DQ Validation: CDE 2.31 IM Posted Pre-Haircut"
```

#### Category 4: Linking (15%)
**Max Score: 100 points**

**Validation:**
- Parent ticket exists and is linked via "tracks" or "relates to"
- Child issues linked if applicable
- Blocked by / blocks relationships identified

**Scoring Rules:**
- 100 pts: Parent linked + "tracks" relationship + child issues linked
- 75 pts: Parent linked with tracks relationship
- 50 pts: Parent exists but not linked
- 25 pts: Vague relationship or missing parent
- 0 pts: No linking information

**Example Success:**
```
✓ Linking (100/100)

Linked to parent: TROYJFSA-2151 
  (Phase II DQ Rules for JFSA) via "tracks" relationship
```

#### Category 5: Labels (10%)
**Max Score: 100 points**

**Rules:**
- Recommended: 3-5 labels per ticket
- Should include: Feature domain (data-quality, validation, api, etc.)
- Should include: Team/component (backend, frontend, database)
- Should include: Priority indicator (if not separate field)

**Scoring Rules:**
- 100 pts: 4-5 well-chosen labels
- 75 pts: 3 relevant labels
- 50 pts: 2 labels or 6+ labels
- 25 pts: 1 label only
- 0 pts: No labels

**Example Violation:**
```
⚠️ Labels (40/100)

Violations:
  - Only 1 label (DQ_OutboundCategory)
  - Recommended: 3-5 labels

Recommendations:
  - Add labels like: data-quality, validation, JFSA
```

#### Category 6: Version Management (8%)
**Max Score: 100 points**

**Validation:**
- Fix Version field is set
- Version matches sprint/release plan
- Sprint is assigned (if using sprints)

**Scoring Rules:**
- 100 pts: Fix Version set + Sprint assigned
- 75 pts: Fix Version set
- 50 pts: Sprint assigned but no Fix Version
- 25 pts: Version in discussion/unclear
- 0 pts: No version or sprint set

**Example Violation:**
```
✗ Version Management (0/100)

Violations:
  - No Fix Version set

Recommendation:
  - Set a Fix Version for sprint/release tracking
```

#### Category 7: Priority (5%)
**Max Score: 100 points**

**Validation:**
- Priority field is set
- Priority aligns with business impact
- Consistent with other tickets

**Scoring Rules:**
- 100 pts: Priority set, aligns with impact
- 75 pts: Priority set, slightly misaligned
- 50 pts: Priority set but unjustified
- 25 pts: Priority unclear or missing
- 0 pts: No priority set

#### Category 8: Story Points (2%)
**Max Score: 100 points**

**Validation:**
- Estimate provided (even if rough)
- Estimate is reasonable for complexity
- Estimate communicated to team

**Scoring Rules:**
- 100 pts: Story points estimated
- 75 pts: T-shirt size or rough estimate
- 50 pts: Estimate in discussion
- 0 pts: No estimation

---

## Quick Wins System

Identify easy-to-fix improvements and their point impact:

**Example:**
```
Quick Wins (Easy to Fix):
1. Set Fix Version → +8.00 points
2. Add 2-3 more labels → +6.00 points
3. Shorten title → +3.75 points

Potential Score After Quick Wins:
  Current: 71.50/100
  After fixes: 89.25/100 (+17.75 points)
```

**Implementation:**
1. Scan each category for common quick wins
2. Calculate point impact
3. Sort by effort (easiest first)
4. Show before/after scores

---

## Report Format

### Phase Structure

```
Phase 1: Requirement Analysis
  ↓
Phase 2: JIRA Assessment (NEW)
  ├─ Category Breakdown (8 categories)
  ├─ Overall Score & Pass/Fail
  ├─ Threshold Analysis
  ├─ Detailed Findings (per category)
  └─ Quick Wins
  ↓
Phase 3: Code Quality Review (existing)
Phase 4: Test Coverage Analysis (existing)
Phase 5: Documentation Analysis (existing)
Phase 6: Scorecard Calculation (existing)
```

### Output Example

```markdown
# JIRA Assessment Report: TROYJFSA-2243

## Overall Score: 71.50/100 ✓ PASS

### Category Breakdown

| Category | Score | Weight | Contribution | Status |
|----------|-------|--------|--------------|--------|
| Acceptance Criteria | 100 | 0.25 | 25.00 | ✓ |
| Description Quality | 70 | 0.20 | 14.00 | ⚠️ |
| Naming Conventions | 50 | 0.15 | 7.50 | ⚠️ |
| Linking | 100 | 0.15 | 15.00 | ✓ |
| Labels | 40 | 0.10 | 4.00 | ⚠️ |
| Version Management | 0 | 0.08 | 0.00 | ✗ |
| Priority | 100 | 0.05 | 5.00 | ✓ |
| Story Points | 50 | 0.02 | 1.00 | ⚠️ |

### Threshold Analysis

- **Minimum Score (60):** ✓ Exceeded by 11.50 points
- **Blocker Score (40):** ✓ Exceeded by 31.50 points

### Detailed Findings

#### ✓ Acceptance Criteria (100/100)
- 5 Given-When-Then criteria across 2 rules
- Clear positive and negative test scenarios

#### ⚠️ Description Quality (70/100)
- Strengths: Rules clearly stated with descriptions
- Missing: User Story format, Technical Notes, Files to Modify

#### ⚠️ Naming Conventions (50/100)
- Title is 22 words (recommended 5-15)
- Suggestion: "DQ Validation: CDE 2.31 IM Posted Pre-Haircut"

... (more findings)

### Quick Wins (Easy to Fix)

1. **Set Fix Version** → +8.00 points
2. **Add 2-3 more labels** → +6.00 points
3. **Shorten title** → +3.75 points

**Potential Score After Quick Wins: 71.50 → 89.25 (+17.75)**

### Next Steps

1. Review and address recommendations above
2. Re-run `/kspec:score-jira TROYJFSA-2243` to verify improvements
3. Proceed with implementation
```

---

## Integration Points

### Code Review Agent Enhancements

**New Phase 2: JIRA Assessment** (before code review)

```python
class CodeReviewAgent:
    def phase_2_jira_assessment(self, jira_ticket):
        """Assess JIRA ticket quality before reviewing code"""
        assessment = {
            'acceptance_criteria': self.score_acceptance_criteria(ticket),
            'description_quality': self.score_description(ticket),
            'naming': self.score_naming(ticket),
            'linking': self.score_linking(ticket),
            'labels': self.score_labels(ticket),
            'version_mgmt': self.score_version_management(ticket),
            'priority': self.score_priority(ticket),
            'story_points': self.score_story_points(ticket),
        }
        return self.calculate_final_score(assessment)
```

### CLI Commands

```bash
# Score a JIRA ticket
/kspec:score-jira TROYJFSA-2243

# Re-score after fixes
/kspec:score-jira TROYJFSA-2243 --verify

# Score all open tickets in sprint
/kspec:score-sprint BACKLOG --sprint "Sprint 42"
```

---

## Success Criteria

✅ **Phase 2 Complete When:**
1. All 8 categories implemented with validation rules
2. Scoring calculations accurate (tested against example)
3. Quick Wins system identifies and ranks improvements
4. Reports generated in HTML and markdown
5. Integration with Code Review Agent workflow
6. CLI commands working (`/kspec:score-jira`)
7. Documentation updated with examples
8. 100% test coverage for scoring logic

---

## Implementation Plan

See: `docs/superpowers/plans/2026-06-02-jira-assessment-implementation.md`

**Estimated Effort:** 40-50 hours  
**Priority:** HIGH (improves requirement quality upstream)  
**Team:** Code Review Agent + JIRA Integration Team

---

## Questions & Discussion

- Should we integrate with JIRA webhooks to auto-score on ticket creation?
- Should passing score threshold be 60 or higher (65/70)?
- Should Quick Wins be actionable (auto-fix suggestions)?
- Should scoring be part of CI/CD validation?
