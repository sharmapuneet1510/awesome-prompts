---
name: BA Create Skill
version: 1.0
description: >
  Parse plain-text requirements (free-form, Markdown, or Gherkin format) and generate structured JIRA-ready issues with auto-generated BDD Given-When-Then acceptance criteria. Output: requirements.json (structured data) and requirements-cards.html (interactive card visualization with editable scenarios).
---

# BA Create Skill — v1.0

## Purpose

Transform natural-language requirements into JIRA-structured issues with BDD acceptance criteria. This skill accepts plain-text requirements files (free-form prose, Markdown, or Gherkin format) and produces two deliverables: `requirements.json` (machine-readable, JIRA-importable) and `requirements-cards.html` (interactive UI for browsing, editing, and exporting scenarios).

## Input Specification

**Format:** Plain text file (.txt, .md, or no extension)

**Supported input formats:**

- **Free-form prose:** "Users should be able to reset their password via email"
- **Markdown:** "## Requirement Title" or "### Subtitle", "---" separators, numbered lists
- **Gherkin (Cucumber):** "Feature: ...", "Scenario: ...", "Given/When/Then/And"

**Auto-detection:** Skill peeks at first 200 characters to determine format:
- Contains "Feature:", "Scenario:", "Given ", "When ", "Then " → Gherkin
- Contains "## ", "### ", "---", "1.", "2." → Markdown
- Otherwise → Free-form prose (default)

**File size:** Up to 50K characters recommended

## Output Specification

**Two files generated (in same directory as input):**

1. **`requirements.json`** — JIRA-importable structured issues (array of issue objects)
   - Machine-readable format, UTF-8 encoding
   - Can be imported directly into Jira via REST API or bulk import tools

2. **`requirements-cards.html`** — Self-contained interactive HTML visualization
   - Single file with all CSS and JavaScript inline (no external CDN dependencies)
   - Browser support: All modern browsers (Chrome, Firefox, Safari, Edge)
   - Features: expand/collapse cards, edit, delete, add scenarios, copy JSON, filters, export

**JSON schema:** See "Phase 5 — JSON Output Specification" section below

**HTML features:** See "Phase 6 — HTML Generation" section below

## Parsing Logic

### Phase 1: Auto-detect input format

```
Scan first 200 characters of input file:
  If contains "Feature:", "Scenario:", "Given ", "When ", "Then "
    → Gherkin (Cucumber format)
  Else if contains "## ", "### ", "---", "1.", "2.", numbered headers
    → Markdown format
  Else
    → Free-form prose (default)
```

### Phase 2: Split requirements by auto-detected separator

Scan document for separators in priority order:

1. **Markdown heading:** "## Title" or "### Title" (starts a new requirement)
2. **Horizontal rule:** "---" or "===" (separates requirements)
3. **Numbered prefix:** "1. Title", "2. Title" (each is a requirement)
4. **Gherkin block:** "Feature: ..." or "Scenario: ..." (each Feature is a requirement)
5. **Fallback:** Paragraph breaks (double blank lines separate requirements)

Once separator pattern is detected, split entire file by that pattern. Each resulting block becomes one requirement.

### Phase 3: Parse each requirement block into issue fields

| Field | Extraction Logic | Example |
|-------|-----------------|---------|
| `key` | Auto-generate: `REQ-001`, `REQ-002`, ... (based on position in file) | `"key": "REQ-001"` |
| `summary` | First sentence or heading line (truncate at 150 chars, remove markdown) | `"summary": "Password reset via email"` |
| `type` | Keyword matching:<br>• "As a" / "As an" / "want to" / "need to" → **Story**<br>• "Fix" / "Bug" / "Broken" / "Error" → **Bug**<br>• "Set up" / "Configure" / "Deploy" / "Install" → **Task**<br>• "Module" / "Epic" / "Feature" / "Phase" / "Platform" → **Epic**<br>• Default → **Story** | `"type": "Story"` |
| `priority` | Keyword matching:<br>• "critical" / "urgent" / "P0" / "before launch" / "ASAP" → **Critical**<br>• "high" / "must" / "required" / "essential" / "P1" → **High**<br>• "should" / "nice to have" / "optional" / "low" / "P3" → **Low**<br>• Default → **Medium** | `"priority": "High"` |
| `description` | All text after summary line (preserve original wording, collapse multiple paragraphs to 200-500 chars) | `"description": "Users need to reset..."` |
| `labels` | Extract from `#tag` syntax in text OR extract 3-4 domain nouns from description (lowercased, hyphens for multi-word) | `"labels": ["auth", "email", "reset"]` |
| `story_points` | Heuristic based on complexity:<br>• >3 distinct actors OR >2 external systems → **5**<br>• 2 actors + 1 system → **3**<br>• Single action / simple flow → **2**<br>• Default → **3** | `"story_points": 3` |
| `status` | Always → **"Open"** | `"status": "Open"` |
| `confidence` | Score 0.0–1.0 based on parsing quality:<br>• Well-structured (clear subject + verb + outcome) → **0.85–1.0**<br>• Some ambiguity (vague pronouns, unclear actions) → **0.65–0.84**<br>• Poor structure (fragments, missing context) → **0.0–0.64** | `"confidence": 0.9` |

### Phase 4: Auto-generate BDD acceptance criteria (3 scenarios per requirement)

For each requirement, generate exactly **3 scenarios** following BDD Given-When-Then format.

**Scenario 1: Happy Path (✅ Success case)**

```
Name: Successful [action from requirement verb]
GIVEN: Extract subject (user type) from "As a..." or requirement context
       "a registered user is on the [location]"
WHEN:  Extract main action verb from requirement (submit, login, delete, reset, etc.)
       "user clicks [button] and [primary action]"
THEN:  Infer success outcome from verb phrase
       "the expected result is displayed and confirmed"

Rules by verb:
  • "submit" → "confirmation message is displayed"
  • "login" / "authenticate" → "user is redirected to dashboard"
  • "delete" / "remove" → "[item] is removed from the system"
  • "reset" → "reset link/email is sent"
  • "update" / "edit" → "changes are saved and reflected"
  • "create" / "add" → "[item] is created and shown in list"
```

**Scenario 2: Edge Case / Validation (⚠ Boundary or invalid input)**

```
Name: [Invalid/Boundary condition] entered
GIVEN: Same context as happy path OR varied initial state
       "a user is on the [same form/page]"
WHEN:  Negate or vary the precondition
       "user submits [empty/duplicate/invalid] [field]"
THEN:  System prevents/rejects the action
       "an error message is displayed and [no side effect occurs]"

Variations (choose based on requirement):
  • Empty field: "When user submits without entering [required field]"
  • Duplicate: "When user enters a [field value] that already exists"
  • Invalid format: "When user enters an invalid [email/phone/ID] format"
  • Boundary: "When user enters [edge case value like empty string / max length]"
  • Permission: "When user without [required permission] attempts action"
```

**Scenario 3: Error Path / Failure (❌ System unavailable or unexpected error)**

```
Name: [External service/system] unavailable
GIVEN: Prerequisite that will fail
       "the [external service] is [down/unavailable/overloaded]"
WHEN:  User attempts the action
       "user requests [action]"
THEN:  User sees error and can retry
       "an error page is displayed and the user is asked to try again later"

Failure modes (choose based on requirement):
  • Network: "GIVEN the network connection is unavailable..."
  • Service: "GIVEN the email service is down..."
  • Auth: "GIVEN the user is not authenticated..."
  • Permission: "GIVEN the user lacks permission to [action]..."
  • Timeout: "GIVEN the request times out after 30 seconds..."
  • Database: "GIVEN the database is unavailable..."
```

**Auto-generation algorithm:**

1. Extract `subject` from "As a X" phrase or infer from requirement context (user, admin, guest, etc.)
2. Extract `action_verb` (primary verb: submit, login, delete, reset, create, update, etc.)
3. Extract `object` (what is being acted on: password, profile, item, email, etc.)
4. Extract `location` (where action happens: page, form, modal, dashboard, etc.)
5. Build 3 scenarios using templates above

## JSON Output Specification

### Phase 5

**File:** `requirements.json` (in same directory as input file)

**Schema:**

```json
{
  "generated_at": "ISO 8601 timestamp (e.g., 2026-06-03T14:00:00Z)",
  "source_file": "requirements.txt",
  "total": 3,
  "stats": {
    "by_type": {
      "Story": 2,
      "Bug": 1,
      "Task": 0,
      "Epic": 0
    },
    "by_priority": {
      "Critical": 0,
      "High": 2,
      "Medium": 1,
      "Low": 0
    },
    "total_story_points": 9,
    "avg_confidence": 0.87
  },
  "issues": [
    {
      "key": "REQ-001",
      "summary": "Password reset via email",
      "type": "Story",
      "priority": "High",
      "status": "Open",
      "description": "Users should be able to reset their password via email link when they forget it.",
      "labels": ["auth", "email", "security"],
      "story_points": 3,
      "confidence": 0.9,
      "acceptance_criteria": [
        {
          "scenario": "Successful password reset",
          "type": "happy_path",
          "icon": "✅",
          "given": "a registered user is on the login page",
          "when": "the user clicks Forgot Password and enters their email",
          "then": "a reset link is sent to the email and a confirmation message is displayed",
          "and": ""
        },
        {
          "scenario": "Unregistered email entered",
          "type": "edge_case",
          "icon": "⚠",
          "given": "a user is on the password reset form",
          "when": "the user submits an email not registered in the system",
          "then": "an error message is shown and no email is sent",
          "and": ""
        },
        {
          "scenario": "Email service unavailable",
          "type": "error_path",
          "icon": "❌",
          "given": "the email delivery service is down",
          "when": "the user requests a password reset",
          "then": "an error page is displayed",
          "and": "the user is asked to try again later"
        }
      ]
    }
  ]
}
```

## HTML Generation

### Phase 6: Interactive Requirement Cards

**File:** `requirements-cards.html` (in same directory as input file)

**Design principles:**
- CSS Grid card layout: `repeat(auto-fill, minmax(380px, 1fr))`
- Responsive: 1 card on mobile, 2–3 cards on desktop
- All CSS and JavaScript inline (no external CDN)
- Smooth animations for expand/collapse

### Page Sections

**A. Header (Gradient banner)**

```html
<header style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
               padding: 2rem; color: white; text-align: center;">
  <h1 style="margin: 0; font-size: 2.5rem;">Requirement Cards</h1>
  <p style="margin: 0.5rem 0 0; font-size: 1rem; opacity: 0.9;">
    Generated from requirements.txt on [date]
  </p>
</header>
```

**B. Stats Bar (CSS Grid with 4 stat cards)**

```
Displays 4 stat cards, each with icon and value:
  • Total Requirements: [N]
  • By Type: [Story: X, Bug: Y, Task: Z, Epic: W]
  • By Priority: [Critical: X, High: Y, Medium: Z, Low: W]
  • Total Story Points: [N]
Color-coded type/priority badges
```

**C. Filter Bar**

```html
<div style="padding: 1.5rem; background: #f5f5f5; display: flex; gap: 1rem; flex-wrap: wrap;">
  <select id="typeFilter">
    <option value="">All Types</option>
    <option value="Story">📖 Story</option>
    <option value="Bug">🐛 Bug</option>
    <option value="Task">✅ Task</option>
    <option value="Epic">🎯 Epic</option>
  </select>
  
  <select id="priorityFilter">
    <option value="">All Priorities</option>
    <option value="Critical">🔴 Critical</option>
    <option value="High">🟠 High</option>
    <option value="Medium">🟡 Medium</option>
    <option value="Low">🟢 Low</option>
  </select>
  
  <select id="completeFilter">
    <option value="">All Completeness</option>
    <option value="complete">Complete (3/3 scenarios)</option>
    <option value="partial">Partial (1-2 scenarios)</option>
  </select>
  
  <input id="searchBox" type="text" placeholder="Search by summary or key...">
  
  <button id="resetFilters">Reset Filters</button>
</div>
```

**D. Card Grid (Main Content)**

**Collapsed Card (default view):**

```
┌─────────────────────────────────────────┐
│ REQ-001  📖 Story  🟠 High  ⭐ 3pts     │
│ #auth #email #security                  │
│                                         │
│ Password reset via email                │
│ (max 2 lines, truncate with ...)        │
│                                         │
│ ▶ 3 scenarios  Confidence: 90%          │
│                                         │
│ [Edit] [Delete]                         │
└─────────────────────────────────────────┘
```

**Expanded Card (after click toggle):**

```
┌──────────────────────────────────────────────────────┐
│ REQ-001  📖 Story  🟠 High  ⭐ 3pts                 │
│ #auth #email #security                               │
├──────────────────────────────────────────────────────┤
│ Password reset via email                              │
│ Users should be able to reset their password via     │
│ email link when they forget it.                      │
├──────────────────────────────────────────────────────┤
│ BDD Acceptance Criteria                               │
│                                                      │
│ ✅ Scenario 1: Successful password reset             │
│   GIVEN  a registered user is on the login page     │
│   WHEN   user clicks Forgot Password + enters email │
│   THEN   reset link sent, confirmation displayed    │
│                                                      │
│ ⚠  Scenario 2: Unregistered email entered           │
│   GIVEN  user is on the reset form                  │
│   WHEN   user submits an unregistered email         │
│   THEN   error shown, no email sent                 │
│                                                      │
│ ❌ Scenario 3: Email service down                   │
│   GIVEN  email service is unavailable               │
│   WHEN   user requests password reset               │
│   THEN   error page shown, retry requested          │
│                                                      │
│ [+ Add Scenario]  [✏ Edit All]  [📋 Copy JSON]     │
└──────────────────────────────────────────────────────┘
```

**Type icons:** 📖 Story, 🐛 Bug, ✅ Task, 🎯 Epic
**Priority badges:** 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low
**Scenario icons:** ✅ happy path, ⚠ edge case, ❌ error path

### JavaScript Functionality

All functions must be self-contained with no external libraries:

- **`toggleCard(key)`** — Expand/collapse card with smooth animation
- **`editCard(key)`** — Make summary, description, and labels fields contentEditable; show Save/Cancel buttons
- **`deleteCard(key)`** — Remove card from DOM (does not delete from JSON file)
- **`addScenario(key)`** — Append new Given-When-Then block with empty fields
- **`copyJSON(key)`** — Copy single issue JSON to clipboard (show toast confirmation)
- **`filterCards()`** — Show/hide cards based on type/priority/search filters
- **`exportAllJSON()`** — Download all issues as `requirements.json` file
- **`exportFilteredJSON()`** — Download only visible cards as `requirements-filtered.json` file
- **`resetFilters()`** — Clear all filter selections and show all cards

## Color Scheme

| Element | Color | Hex |
|---------|-------|-----|
| Header gradient (start) | Blue | #667eea |
| Header gradient (end) | Purple | #764ba2 |
| Story type badge | Blue | #1976d2 |
| Bug type badge | Red | #d32f2f |
| Task type badge | Green | #388e3c |
| Epic type badge | Purple | #7b1fa2 |
| Critical priority badge | Red | #d32f2f |
| High priority badge | Orange | #f57c00 |
| Medium priority badge | Yellow | #fbc02d |
| Low priority badge | Green | #388e3c |
| Happy path scenario (✅) | Green | #4caf50 |
| Edge case scenario (⚠) | Orange | #ff9800 |
| Error scenario (❌) | Red | #f44336 |
| Card background | White | #ffffff |
| Card border | Light gray | #e0e0e0 |
| Card hover | Very light gray | #f9f9f9 |
| Filter bar background | Light gray | #f5f5f5 |
| Footer background | Dark gray | #333333 |

## Example Output

### Input file (requirements.txt)

```
## Password Reset
Users should be able to reset their password via email link. This is a high priority feature for security.

## User Profile
As a logged-in user, I want to edit my profile picture and display name so I can keep my account current.

---

Fix the broken pagination on the search results page. Only 10 results showing instead of the full result set.
```

### Generated outputs

1. **`requirements.json`** — 3 issues with 9 total BDD scenarios (3 per issue)
   - REQ-001: Password Reset (Story, High, 3pts)
   - REQ-002: User Profile (Story, Medium, 3pts)
   - REQ-003: Fix pagination (Bug, Medium, 2pts)

2. **`requirements-cards.html`** — Interactive card visualization
   - Header with stats
   - Filter bar (type, priority, completeness, search)
   - 3 expandable cards with BDD scenarios
   - Edit, delete, add scenario, copy JSON buttons
   - Export JSON functionality
   - Responsive CSS Grid layout

## Acceptance Criteria

- ✓ Input format auto-detected (Gherkin / Markdown / free-form)
- ✓ Multiple requirements split correctly by separator
- ✓ Each field extracted: summary, type, priority, description, labels, story_points, confidence
- ✓ 3 BDD scenarios per requirement (happy path / edge case / error path)
- ✓ JSON schema valid and JIRA-importable (can be used with Jira REST API)
- ✓ HTML renders correctly in all modern browsers (Chrome, Firefox, Safari, Edge)
- ✓ Cards expand/collapse with smooth CSS animation
- ✓ Edit button makes fields contentEditable with Save/Cancel confirmation
- ✓ Delete button removes card from DOM (visual feedback)
- ✓ Add Scenario button appends new Given-When-Then block
- ✓ Copy JSON copies single issue JSON to clipboard (toast notification)
- ✓ Export JSON downloads requirements.json (current state, all issues)
- ✓ Export Filtered JSON downloads only visible cards
- ✓ Filters work independently (type, priority, completeness, search)
- ✓ Reset Filters clears all selections and shows all cards
- ✓ No external CDN dependencies (all CSS/JS inline)
- ✓ Self-contained single HTML file with embedded styling and scripts
