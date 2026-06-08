---
name: JIRA Incremental Specification Generator
description: Read JIRA tickets incrementally by prefix, aggregate requirements, generate comprehensive application specification document in book-like structure
version: 1.0
tags: [jira, requirements, specification, documentation, book-format]
---

# JIRA Incremental Specification Generator Skill

## Overview

This skill **reads JIRA tickets incrementally** by auto-incrementing ticket numbers (e.g., PROJ-1, PROJ-2, PROJ-3, ...) and generates a **comprehensive application specification document** in professional book format with organized chapters, sections, and cross-references.

**Key Features:**
- ✓ Automatic incremental ticket discovery (PROJ-1 → PROJ-2 → PROJ-3, etc.)
- ✓ Stop condition: 10 consecutive missing tickets
- ✓ Comprehensive aggregation (all tickets in one document)
- ✓ Professional book-like structure (chapters, TOC, index)
- ✓ Functional & technical requirements merged
- ✓ Acceptance criteria cross-referenced
- ✓ Dependencies and relationships mapped

---

## Input Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `jira_prefix` | string | Yes | JIRA project prefix to increment | "PROJ", "AUTH", "ORDER" |
| `start_number` | integer | No | Starting ticket number (default: 1) | 1, 100 |
| `max_consecutive_misses` | integer | No | Stop after N missing tickets (default: 10) | 10, 5, 15 |
| `output_format` | string | No | Document format (default: markdown) | "markdown", "html", "pdf" |
| `include_acceptance_criteria` | boolean | No | Include AC in spec (default: true) | true, false |
| `include_dependencies` | boolean | No | Map ticket dependencies (default: true) | true, false |

---

## Algorithm: Incremental Discovery

```
INITIALIZE:
  current_number = start_number
  consecutive_misses = 0
  all_tickets = []
  missing_numbers = []

LOOP:
  ticket_id = jira_prefix + "-" + current_number
  
  TRY fetch_jira(ticket_id):
    IF found:
      all_tickets.append(ticket_id)
      consecutive_misses = 0
    ELSE:
      consecutive_misses += 1
      missing_numbers.append(current_number)
    
    IF consecutive_misses >= max_consecutive_misses:
      BREAK
    
    current_number += 1
  
RETURN all_tickets
```

**Example Execution:**
```
Prefix: PROJ
Start: 1
Max Consecutive Misses: 10

PROJ-1    ✓ Found (type: Story)         → consecutive_misses = 0
PROJ-2    ✓ Found (type: Task)          → consecutive_misses = 0
PROJ-3    ✗ Not found                   → consecutive_misses = 1
PROJ-4    ✓ Found (type: Bug)           → consecutive_misses = 0
PROJ-5    ✓ Found (type: Subtask)       → consecutive_misses = 0
PROJ-6    ✗ Not found                   → consecutive_misses = 1
PROJ-7    ✗ Not found                   → consecutive_misses = 2
PROJ-8    ✗ Not found                   → consecutive_misses = 3
PROJ-9    ✗ Not found                   → consecutive_misses = 4
PROJ-10   ✗ Not found                   → consecutive_misses = 5
PROJ-11   ✗ Not found                   → consecutive_misses = 6
PROJ-12   ✗ Not found                   → consecutive_misses = 7
PROJ-13   ✗ Not found                   → consecutive_misses = 8
PROJ-14   ✗ Not found                   → consecutive_misses = 9
PROJ-15   ✗ Not found                   → consecutive_misses = 10 (STOP)

Result: Found 5 tickets [PROJ-1, PROJ-2, PROJ-4, PROJ-5, ...]
```

---

## Workflow: 7-Phase Document Generation

### PHASE 1: Incremental Discovery
**Goal:** Fetch all JIRA tickets by incrementing ticket number

**Steps:**
1. Initialize counter at `start_number`
2. Loop: fetch ticket with ID `{prefix}-{counter}`
3. If found → add to collection, reset consecutive_miss counter
4. If not found → increment consecutive_miss counter
5. If consecutive_miss >= limit → STOP and return all found tickets
6. Otherwise → increment counter and continue loop

**Output:**
```json
{
  "discovered_tickets": ["PROJ-1", "PROJ-2", "PROJ-4", "PROJ-5"],
  "total_found": 4,
  "total_attempts": 15,
  "missing_numbers": [3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
  "discovery_rate": "26.7%"
}
```

### PHASE 2: Data Aggregation
**Goal:** Extract structured data from all discovered tickets

**Extract from each ticket:**
- Title & description
- Type (Story, Task, Bug, Subtask, Epic)
- Status & priority
- Assignee & reporter
- Acceptance criteria
- Dependencies (links to other tickets)
- Story points / estimate
- Created & updated dates
- Labels & components

**Output:**
```json
{
  "PROJ-1": {
    "title": "User Authentication",
    "type": "Story",
    "status": "Done",
    "priority": "High",
    "description": "...",
    "acceptance_criteria": [
      "Users can log in with email/password",
      "Sessions persist for 24 hours",
      "Logout clears session"
    ],
    "dependencies": ["PROJ-2", "PROJ-4"],
    "points": 8
  },
  ...
}
```

### PHASE 3: Requirements Classification
**Goal:** Categorize tickets into functional/technical requirements

**Classifications:**
- **Functional Requirements** — User-facing features (Stories)
- **Technical Requirements** — Infrastructure, tech debt (Tasks, Subtasks)
- **Bug Fixes** — Production issues (Bugs)
- **Non-Functional Requirements** — Performance, security, scaling (Epic, Labels)

**Output:**
```
Functional Requirements (Stories): 12 tickets
Technical Requirements (Tasks): 8 tickets
Bug Fixes: 4 tickets
Non-Functional (Performance, Security): 6 tickets
Total: 30 tickets
```

### PHASE 4: Dependency Analysis
**Goal:** Map ticket relationships and build dependency graph

**Analyze:**
1. Direct dependencies (JIRA links)
2. Indirect dependencies (inferred from descriptions)
3. Blocking relationships
4. Sequential constraints
5. Parallel capabilities

**Output:**
```
Dependency Graph:
  PROJ-1 (Auth)
    ├─ blocks PROJ-2 (Profile)
    └─ blocks PROJ-5 (Dashboard)
  
  PROJ-4 (Database)
    ├─ blocks PROJ-1
    └─ blocks PROJ-2

Dependency Order (topological sort):
  1. PROJ-4 (Database) — 0 dependencies
  2. PROJ-1 (Auth) — depends on PROJ-4
  3. PROJ-2 (Profile) — depends on PROJ-1, PROJ-4
  4. PROJ-5 (Dashboard) — depends on PROJ-1
```

### PHASE 5: Document Structure Creation
**Goal:** Organize tickets into book-like chapters

**Book Structure:**
```
I.    Executive Summary
      - Overview
      - Key statistics
      - Timeline & milestones

II.   Functional Requirements (by feature area)
      - Chapter 1: Authentication & User Management
      - Chapter 2: Core Business Logic
      - Chapter 3: Reporting & Analytics

III.  Technical Requirements & Architecture
      - Chapter 4: Database & Data Model
      - Chapter 5: API & Integration
      - Chapter 6: Performance & Scaling

IV.   Non-Functional Requirements
      - Chapter 5: Security Requirements
      - Chapter 6: Performance Goals
      - Chapter 7: Accessibility & UX

V.    Acceptance Criteria & Testing
      - All ACs listed with references
      - Test scenarios
      - Success metrics

VI.   Dependencies & Implementation Order
      - Topological sort of tickets
      - Critical path
      - Parallel work streams

VII.  Appendices
      - Full ticket reference
      - Glossary
      - Cross-reference index
```

### PHASE 6: Content Generation
**Goal:** Write professional specification content for each chapter

**For each chapter:**
1. **Chapter Title & Overview** — What this section covers
2. **Requirements** — Each ticket as a subsection
   - Requirement statement
   - Acceptance criteria
   - Related tickets (dependencies, links)
   - Success metrics
3. **Design notes** — Architecture implications
4. **Implementation notes** — Technical considerations

**Example Chapter:**
```
## Chapter 2: User Authentication & Authorization

### Overview
This chapter covers all user identity management, session handling, and 
access control requirements. These form the foundation for the entire 
application and must be implemented first.

### PROJ-1: User Registration

**Requirement:**
Users must be able to register with email and password, receive a 
confirmation email, and activate their account.

**Acceptance Criteria:**
✓ Users can register with email + password
✓ Passwords must be ≥8 chars with complexity
✓ Confirmation email sent within 5 minutes
✓ User must click link to activate
✓ Accounts inactive > 7 days are deleted

**Related Tickets:**
- Blocks: PROJ-2 (User Profile)
- Related: PROJ-4 (Email Service)

**Implementation Notes:**
- Must be completed before PROJ-2
- Requires PROJ-4 (Email Service)
- Database changes in PROJ-8

### PROJ-2: User Profile

...
```

### PHASE 7: Document Assembly & Export
**Goal:** Assemble all content into final document

**Steps:**
1. Generate table of contents (auto-indexed)
2. Generate introduction & executive summary
3. Assemble all chapters in order
4. Add cross-references & linkages
5. Generate index & glossary
6. Export to requested format

**Output Files:**
```
application-spec.md                          ← Main document
├── TOC (auto-generated)
├── Executive Summary
├── Chapter 1: Functional Reqs...
├── Chapter 2: Technical Reqs...
└── Appendices
    ├── Full Ticket Reference
    ├── Glossary
    └── Index

application-spec.html                        ← Formatted version
application-spec.pdf                         ← Print-ready version
tickets-dependency-graph.mermaid             ← Visual graph
tickets-data.json                            ← Machine-readable format
```

---

## Output Structure: Book Format

### Executive Summary
```markdown
# Application Specification Document

## Executive Summary

### Overview
[High-level description of the application]

### Key Statistics
- Total Requirements: 30
- Functional Requirements: 12
- Technical Requirements: 8
- Bug Fixes: 4
- Non-Functional Requirements: 6

### Timeline & Milestones
- Phase 1 (Foundation): Weeks 1-2
  - Database schema, authentication, core APIs
  - Tickets: PROJ-4, PROJ-1, PROJ-2
- Phase 2 (Features): Weeks 3-5
  - User profiles, dashboard, reporting
  - Tickets: PROJ-5, PROJ-6, PROJ-7
- Phase 3 (Polish): Weeks 6-8
  - Performance optimization, documentation
  - Tickets: PROJ-28, PROJ-29, PROJ-30

### Key Dependencies
```

### Chapters with Requirements
```markdown
## Chapter 1: User Authentication & Authorization

### Overview
[Chapter introduction]

### PROJ-1: User Registration
**Type:** Story | **Priority:** High | **Points:** 8

**Requirement:**
[Description from JIRA]

**Acceptance Criteria:**
- [ ] Users can register with email + password
- [ ] Email confirmation required
- [ ] Sessions persist for 24 hours

**Implementation Order:** 1 (no dependencies)

---

### PROJ-2: User Profile Management
[Similar structure]

---
```

### Dependencies & Implementation Order
```markdown
## Implementation Roadmap

### Critical Path
1. PROJ-4 (Database) — 5 points, 1 week
   ↓ (blocks)
2. PROJ-1 (Auth) — 8 points, 1.5 weeks
   ├─ (blocks) PROJ-2 (Profile)
   └─ (blocks) PROJ-5 (Dashboard)

### Parallel Work Streams
**Stream A (Backend):**
- PROJ-4 → PROJ-1 → PROJ-2 → PROJ-7 (APIs)

**Stream B (Frontend):**
- PROJ-10 (UI Framework) → PROJ-11 → PROJ-12

**Can run in parallel:** Streams A & B
```

### Full Reference & Index
```markdown
## Appendix A: Full Ticket Reference

| ID | Title | Type | Status | Points |
|----|-------|------|--------|--------|
| PROJ-1 | User Registration | Story | Done | 8 |
| PROJ-2 | User Profile | Story | In Progress | 5 |
| ... | ... | ... | ... | ... |

## Appendix B: Glossary

**User Story:** A feature requirement from an end-user perspective...
**Acceptance Criteria:** Specific conditions that must be met...
**Dependency:** A ticket that must be completed before another...

## Appendix C: Index

Authentication... Page 15, 23, 45
Database Schema... Page 8, 102
User Management... Page 15-45
...
```

---

## Example Usage

### Command
```bash
orchestrator:jira-spec-generator \
  jira_prefix="MYAPP" \
  start_number=1 \
  max_consecutive_misses=10 \
  output_format="markdown" \
  include_dependencies=true
```

### What Happens
```
[Step 1] Discovering tickets...
  MYAPP-1  ✓ User Registration (Story)
  MYAPP-2  ✓ User Profile (Story)
  MYAPP-3  ✗ (skip)
  MYAPP-4  ✓ Database Schema (Task)
  MYAPP-5  ✓ API Layer (Story)
  MYAPP-6  ✗ (skip)
  ...
  MYAPP-15 ✗ (10th consecutive miss - STOP)

[Step 2] Aggregating 12 found tickets...
[Step 3] Classifying requirements...
[Step 4] Analyzing dependencies...
[Step 5] Building document structure...
[Step 6] Generating content...
[Step 7] Assembling final document...

✓ Generated: myapp-specification.md (47 KB, 156 pages)
✓ Generated: myapp-specification.html (formatted)
✓ Generated: myapp-dependency-graph.mermaid
✓ Generated: tickets-reference.json
```

### Output Document (Markdown)
```markdown
# MYAPP Application Specification

## Table of Contents
1. Executive Summary (Page 3)
2. Functional Requirements (Page 5)
3. Technical Requirements (Page 45)
4. Non-Functional Requirements (Page 95)
5. Implementation Order & Dependencies (Page 130)
6. Appendices (Page 145)

---

## Executive Summary

### Project Overview
MYAPP is a comprehensive user management and analytics platform...

### Key Figures
- 12 Functional Requirements (Stories)
- 8 Technical Requirements (Tasks)
- 4 Bug Fixes
- Total Story Points: 145
- Estimated Timeline: 16 weeks

### Dependency Chain
MYAPP-4 (Database)
  ↓ (must be first)
MYAPP-1 (Authentication)
  ↓ (blocks)
MYAPP-2 (User Profile) & MYAPP-5 (Dashboard)
  ↓
MYAPP-6, MYAPP-7, MYAPP-8 (Features)

---

## Part I: Functional Requirements

### Chapter 1: User Management

#### MYAPP-1: User Registration

**Requirement Statement:**
Users must be able to self-register with email and password...

**Type:** Story  
**Priority:** High  
**Story Points:** 8  
**Status:** Done

**Acceptance Criteria:**
1. Users can register with email + password
   - Email must be valid (RFC 5322)
   - Password must be ≥8 chars, mixed case, numbers
2. Confirmation email sent within 5 minutes
   - Email includes activation link
   - Link expires after 7 days
3. User must click link to activate account
   - Unactivated accounts deleted after 7 days
4. Duplicate emails rejected with 400 error

**Dependencies:**
- Blocks: MYAPP-2 (User Profile)
- Requires: MYAPP-4 (Database Schema)
- Related: MYAPP-8 (Email Service)

**Implementation Notes:**
- Must use bcrypt for password hashing
- Implement rate limiting (5 attempts/minute per IP)
- Consider GDPR implications for data storage

**Test Scenarios:**
✓ Valid registration creates user
✓ Invalid email rejected
✓ Weak password rejected
✓ Duplicate email rejected
✓ Confirmation email sent
✓ Activation link works
✓ Expired link rejected
✓ Unactivated user deleted after 7 days

---

#### MYAPP-2: User Profile

...more tickets...
```

---

## Integration with Other Skills & Agents

| Skill/Agent | Integration | Usage |
|-------------|-------------|-------|
| **code_documentation_skill** | Reference generated spec when writing code docs | Code examples match spec requirements |
| **test_skill** | Generate tests from acceptance criteria | Each AC becomes test case |
| **architect:design** | Use spec as system requirements | Design based on functional + non-func reqs |
| **implementer:build** | Reference chapters during implementation | Build features in dependency order |
| **quality:review** | Validate PRs against spec ACs | Ensure code meets spec |

---

## Key Parameters & Defaults

| Parameter | Default | Range | Impact |
|-----------|---------|-------|--------|
| `jira_prefix` | (required) | Any text | Which tickets to fetch |
| `start_number` | 1 | 1-10000 | Where to start incrementing |
| `max_consecutive_misses` | 10 | 1-50 | When to stop searching |
| `output_format` | "markdown" | md, html, pdf | File format & structure |
| `include_ac` | true | bool | Include acceptance criteria |
| `include_deps` | true | bool | Map dependencies & order |

---

## Advanced Features

### Feature 1: Batch Mode
```bash
orchestrator:jira-spec-generator \
  jira_prefixes=["PROJ", "AUTH", "ORDER"] \
  output_mode="separate"  # One doc per prefix
```

**Output:**
```
proj-specification.md (48 pages)
auth-specification.md (32 pages)
order-specification.md (56 pages)
combined-specification.md (200 pages, all three)
```

### Feature 2: Delta Generation
```bash
orchestrator:jira-spec-generator \
  jira_prefix="PROJ" \
  since_last_run=true  # Only new/changed tickets
```

**Output:**
```
What's New in v1.2 (vs v1.1):
- 4 new requirements added
- 2 requirements updated
- 1 requirement completed
- Changed implementation order for 3 items
```

### Feature 3: Metrics & Analytics
```
📊 Specification Metrics

Total Requirements: 30
- Functional: 12 (40%)
- Technical: 8 (27%)
- Bugs: 4 (13%)
- Non-Functional: 6 (20%)

Complexity: Medium
- Story Points: 145
- Estimated Duration: 16 weeks
- Team Size Required: 4-6 engineers

Quality Score: 92%
- All acceptance criteria clearly defined: ✓
- No circular dependencies: ✓
- All requirements have owners: ✓
- Documentation complete: ✓
```

---

## Error Handling

### Scenarios & Recovery

**Scenario 1: JIRA Connection Fails**
```
Error: Cannot connect to JIRA API
Action: Retry with exponential backoff (1s, 2s, 4s, 8s, 16s)
If all retries fail: Use cached data if available
Notify: "Using cached data from 2 hours ago"
```

**Scenario 2: Ticket Not Found**
```
PROJ-5 not found → consecutive_misses = 1
Continue searching...
```

**Scenario 3: Malformed Ticket Data**
```
PROJ-8: Title is missing
Action: Use description as fallback, add warning note
Output: "⚠️ PROJ-8: Title missing (used description instead)"
```

**Scenario 4: Circular Dependency Detected**
```
PROJ-1 → PROJ-2 → PROJ-3 → PROJ-1 (circular!)
Action: Flag error, highlight in document, recommend fix
Output: "🚨 Circular dependency detected: PROJ-1 → PROJ-2 → PROJ-3 → PROJ-1"
```

---

## Success Criteria

✅ Document is comprehensive (all tickets included)
✅ Structure is professional (book-like with TOC, index)
✅ Dependencies are accurate (topological sort)
✅ Acceptance criteria are clearly stated
✅ Implementation order is logical
✅ No circular dependencies
✅ All cross-references work
✅ Document is readable and navigable

---

## Example Configurations

### Configuration 1: Small Project (< 20 tickets)
```yaml
jira_prefix: "PROJ"
start_number: 1
max_consecutive_misses: 5  # Stop faster
output_format: "html"      # Single file
include_acceptance_criteria: true
include_dependencies: true
```

### Configuration 2: Large Project (100+ tickets)
```yaml
jira_prefix: "BIGAPP"
start_number: 1
max_consecutive_misses: 20  # Allow more gaps
output_format: "markdown"   # GitHub friendly
batch_by_type: true        # Separate chapters per type
generate_metrics: true      # Include analytics
generate_timeline: true     # Gantt chart
```

### Configuration 3: Multi-Team Project
```yaml
jira_prefixes: ["BACKEND", "FRONTEND", "DEVOPS", "QA"]
output_mode: "combined"     # One master doc
per_team_docs: true         # Plus individual docs
cross_team_dependencies: true
include_swimlanes: true     # Show team ownership
```

---

## Notes & Limitations

- **JIRA Connection Required:** Must have MCP access to JIRA API
- **Missing Tickets:** Gaps in numbering are OK, 10 consecutive misses = stop
- **Large Projects:** May take 5-10 minutes to fetch 200+ tickets
- **Memory:** Caches all ticket data during run (500 MB for 1000 tickets)
- **Circular Dependencies:** Detected and flagged, but document is still generated

---

## Related Skills & Resources

- [[code_documentation_skill]] — Generate code docs from spec
- [[test_skill]] — Generate tests from acceptance criteria
- [[architect:design]] — Design from functional requirements
- [[SPECIALIST_AGENT_MODES.md]] — Specialist modes for different workflows
- [[FUNCTION_EXAMPLES.md]] — Real-world examples of agent usage

