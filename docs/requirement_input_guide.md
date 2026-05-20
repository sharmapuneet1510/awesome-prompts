# Developer Agent: Requirement Input Guide

## Overview

The updated **Developer Agent** (v3.1) now includes a **STEP 0: Gather Requirements** that intelligently accepts requirements from multiple sources:

1. **Free Text** — Describe what you want to build
2. **JIRA Ticket** — Link or reference to JIRA (requires MCP)
3. **Requirement File** — Text, Markdown, or YAML file with requirements
4. **Auto-Detect** — Automatically finds requirements.md in project root

---

## Usage Methods

### Method 1: Free Text Input

**Fastest for small features:**

```
Developer Agent: "How would you like to provide requirements?"

User: "a) Free text"

Agent: "Describe what you want to build. Include:
  ✓ Main purpose
  ✓ Key features/functionality
  ✓ Constraints or dependencies"

User: "Build a FastAPI backend with PostgreSQL for user authentication.
       Features: JWT login, token refresh, password reset via email.
       Must support 10K concurrent users.
       Tech: Python 3.11+, SQLAlchemy 2.0, Alembic migrations."

Agent: (Parses requirements)
       Creates requirement_object:
       {
         "source": "free_text",
         "title": "FastAPI Backend",
         "description": "Build a FastAPI backend with PostgreSQL...",
         "features": ["JWT login", "token refresh", "password reset"],
         "constraints": ["10K concurrent users"],
         "acceptance_criteria": ["Support 10K concurrent users"]
       }
       
       Proceeds to STEP 1 (Context Loading)
```

---

### Method 2: JIRA Ticket

**Best for tracked work:**

```
User: "Use requirement from PROJ-123"

Agent: "Provide JIRA ticket link or key (e.g., PROJ-123 or https://...)"

User: "PROJ-123"

Agent: (Uses MCP to fetch JIRA)
       Extracts:
         - Summary: "Implement user authentication API"
         - Description: Full JIRA description
         - Acceptance Criteria: Listed in JIRA
         - Assignee: dev@company.com
         - Status: In Progress
       
       Creates requirement_object with jira_key: "PROJ-123"
       
       Proceeds to STEP 1
```

**Without MCP:** Copy-paste JIRA description into free text instead.

---

### Method 3: Requirement File

**Best for detailed specs:**

**Example: requirements.md**

```markdown
---
name: user_auth_system
version: 1.0
---

# User Authentication System

## Vision
Secure JWT-based authentication API for microservices.

## Tech Stack
- **Backend:** Python FastAPI 0.95+
- **Database:** PostgreSQL 13+
- **Auth:** JWT tokens with refresh

## Features

### 1. User Registration
POST /api/auth/register
- Input: email, password
- Validation: email format, min 8 char password
- Response: user_id, access_token, refresh_token

### 2. Login
POST /api/auth/login
- Input: email, password
- Validation: credentials check
- Response: access_token (15 min), refresh_token (7 days)

### 3. Token Refresh
POST /api/auth/refresh
- Input: refresh_token
- Response: new access_token

### 4. Password Reset
POST /api/auth/reset-password
- Input: email
- Action: Send reset link via email
- Endpoint: POST /api/auth/reset (token)

## Acceptance Criteria

- [ ] All endpoints return proper HTTP status codes
- [ ] Password hashing uses bcrypt
- [ ] JWT signed with RS256
- [ ] Rate limiting: 5 requests/min per IP
- [ ] Logging: all auth events logged
- [ ] Test coverage: ≥ 95%
- [ ] Database: migrations managed with Alembic
- [ ] API docs: OpenAPI/Swagger auto-generated

## Constraints

- Timeline: 2 weeks
- Team: 2 developers
- No external OAuth (native JWT only)
- Production-ready code required
```

**Usage:**

```
Developer Agent: "How would you like to provide requirements?"

User: "c) Requirement file"

Agent: "Provide absolute path to requirement file"

User: "/path/to/requirements.md"

Agent: (Reads and parses file)
       Creates requirement_object from structured content
       
       Proceeds to STEP 1
```

---

### Method 4: Auto-Detect from Project

**Fastest for ongoing projects:**

```
Developer Agent: "How would you like to provide requirements?"

User: "d) Auto-detect from project"

Agent: (Searches project root)
       Found: docs/requirements.md
       
       Loads and parses automatically
       Creates requirement_object
       
       Proceeds to STEP 1
```

**Auto-detection searches for:**
- `requirements.md`
- `requirements.txt`
- `REQUIREMENTS.md`
- `spec.md`
- `.requirements`

---

## Requirement Object Structure

All input methods produce a consistent `requirement_object`:

```json
{
  "source": "free_text|jira|file|project_file",
  "title": "Feature or project name",
  "description": "2-3 sentence vision or summary",
  "features": [
    "Feature 1",
    "Feature 2",
    "Feature 3"
  ],
  "constraints": [
    "10K concurrent users",
    "2-week timeline",
    "Team of 2 developers"
  ],
  "acceptance_criteria": [
    "All endpoints return proper HTTP status codes",
    "Password hashing uses bcrypt",
    "Test coverage ≥ 95%"
  ],
  "priority": "high|medium|low",
  "parsed_at": "2026-05-20T16:41:23.123826",
  "raw_text": "Original input (first 500 chars)"
}
```

---

## Developer Workflow After Requirement Input

Once requirement is gathered (STEP 0), the agent:

1. **STEP 1:** Loads context (checks docs/context/context.json or auto-detects tech stack)
2. **STEP 2:** Confirms requirements with user
3. **STEP 3:** Creates implementation plan
4. **STEP 4:** Applies appropriate skill (database_skill, backend_skill, frontend_skill, etc.)
5. **STEP 5:** Implements with standards (tests, documentation, security)
6. **STEP 6:** Tests everything (pytest, Jest, Playwright)
7. **STEP 7:** Documents & commits

---

## Tips & Best Practices

### Tip 1: Include Context in Free Text

More details = better results. Include:

```
"Build a FastAPI REST API for a multi-tenant SaaS platform.

Features:
- User authentication with JWT
- Tenant isolation at DB level
- Audit logging for all operations
- Webhooks for event notifications

Stack: Python 3.11+, FastAPI, PostgreSQL, Redis for caching

Constraints:
- Team: 2 backend engineers
- Timeline: 4 weeks
- Must support 5K concurrent users
- No breaking API changes after v1.0 release

Success Criteria:
- 99.9% uptime SLA
- API response time < 200ms (p95)
- All operations audit-logged
- Test coverage ≥ 95%"
```

### Tip 2: Use Requirement Files for Complex Projects

Keep requirements versioned in your repo:

```
project-root/
├── requirements.md          ← Version controlled
├── docs/requirements.txt    ← Can be multiple files
└── src/
```

### Tip 3: Link JIRA for Team Collaboration

If using JIRA in your org, provide the ticket key:

```
"Use JIRA PROJ-456 for this work"
```

Agent will fetch details automatically (with MCP integration).

### Tip 4: Update Requirements As You Go

After implementation, update requirements.md:

```markdown
## Status
- ✅ Phase 1: User registration (completed)
- ✅ Phase 2: Login/refresh (completed)
- ⏳ Phase 3: Password reset (in progress)
- ⏳ Phase 4: Email notifications (scheduled)
```

---

## Integration with Tools

### Requirement Parser CLI

Standalone usage:

```bash
# Free text
python tools/requirement_parser.py "Your requirement description"

# From file
python tools/requirement_parser.py /path/to/requirements.md

# Interactive mode
python tools/requirement_parser.py
# Opens interactive prompt for all input methods
```

---

## MCP Integration (JIRA Support)

To enable automatic JIRA parsing:

1. Install MCP server with JIRA support
2. Configure JIRA credentials in `.env`
3. Developer Agent will automatically use MCP to fetch JIRA details

Example `.env`:

```env
JIRA_BASE_URL=https://jira.company.com
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-api-token
```

---

## FAQ

**Q: Can I change the requirement after providing it?**
A: Yes. In STEP 2, you can refine or correct the parsed requirements.

**Q: What if my requirement file format is different?**
A: The parser is flexible with markdown, YAML, and plain text. As long as it contains feature/criteria keywords, it will extract them.

**Q: Can I provide multiple requirements?**
A: Currently, one requirement per agent run. For multiple features, use autonomous_dev_agent which handles sequencing.

**Q: Does the agent modify my requirement file?**
A: No. It reads the file but doesn't modify it. All parsed data is stored in requirement_object in memory.

**Q: Can I skip STEP 0 and go straight to coding?**
A: No. Requirements are mandatory — even for bug fixes or small features.
