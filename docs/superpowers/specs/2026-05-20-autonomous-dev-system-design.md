# Autonomous Developer System - Complete Specification

**Date:** 2026-05-20  
**Status:** Approved  
**Version:** 1.0  

## Executive Summary

The Autonomous Developer System is an end-to-end code generation and testing pipeline that transforms plain-text requirements into production-ready, fully tested code. The system intelligently detects project state (new vs. existing), builds architectural context, generates structured task specifications, executes tasks using specialized skills, and automatically synchronizes results to GitHub and Claude Code platforms.

**Key outcomes:**
- Plain text → Structured requirement.md
- Auto-generated architecture design + knowledge graph
- Task-based code generation (DB → Backend → Frontend → Tests → Deployment)
- JSON-tracked task completion with 100% autonomous execution
- Zero-touch GitHub/Claude Code integration

---

## 1. System Architecture

### 1.1 High-Level Pipeline

```
requirement.txt (user input)
    ↓
[Autonomous Developer Agent]
    ├── Parse & Normalize
    ├── Detect Project State
    ├── Build Context (architecture.md + context.json)
    ├── Generate Knowledge Graph (graphify)
    ├── Create Task Specifications
    ├── Execute Tasks (serial: DB → Backend → Frontend → Tests → Deploy)
    ├── Track Completion (task-completion.json)
    └── Sync Results (GitHub PR + Claude Code)
    ↓
Production-ready code with full test coverage
```

### 1.2 Component Breakdown

| Component | Role | Responsibility |
|-----------|------|-----------------|
| **Autonomous Dev Agent** | Orchestrator | Coordinates all phases; maintains context; invokes skills |
| **Developer Skill (Backend)** | Code Generator | Generates API routes, models, services (Python/Java) |
| **Developer Skill (Frontend)** | Code Generator | Generates React/TS components, pages, styling |
| **Test Skill** | Validator | Generates & runs tests (Playwright, pytest, JUnit); reports coverage |
| **Architecture Skill** | Documentation | Updates architecture.md, context.json, regenerates graphs |
| **Graphify Integration** | Knowledge Store | Builds knowledge graphs; caches embeddings for token reuse |

---

## 2. Input & Output Specifications

### 2.1 Input: `requirement.txt`

**Format:** Plain text, free-form. No structure required.

**Example:**
```
We need a user management system with login, registration, and profile updates.
Use React for frontend, Python FastAPI for backend, PostgreSQL for database.
Support JWT auth. Must be ready in 2 weeks.
Should track user activity in logs.
```

**Agent responsibility:** Parse intent, extract key concepts, infer missing details.

### 2.2 Generated: `requirement.md`

**Location:** `docs/requirement.md`  
**Format:** Structured markdown with clear sections.

**Template:**
```markdown
---
name: project_name
version: 1.0
generated_at: 2026-05-20T10:00:00Z
---

# Project: [Extracted Name]

## Vision
[2-3 sentence summary extracted from requirement.txt]

## Tech Stack
- **Frontend:** React 18+ / TypeScript / Vite
- **Backend:** Python 3.11 / FastAPI / SQLAlchemy 2.x
- **Database:** PostgreSQL 14+
- **Auth:** JWT (Bearer tokens)

## Features (User Stories)
1. **User Registration**
   - Given: Unregistered user
   - When: Completes signup form
   - Then: Account created, JWT issued

2. **User Login**
   - Given: Registered user
   - When: Provides credentials
   - Then: JWT issued, stored in localStorage

3. **Profile Management**
   - Given: Authenticated user
   - When: Updates profile fields
   - Then: Changes persisted, logs recorded

## Success Criteria
- [ ] All API endpoints tested (≥95% coverage)
- [ ] UI responsive on mobile + desktop
- [ ] Zero SQL injection / XSS vulnerabilities
- [ ] All user actions logged

## Constraints
- Timeline: 2 weeks
- Team: 1 agent (autonomous)
- Deployment: Docker + cloud-ready

## Architecture Overview
[Auto-generated after codebase scan]
```

### 2.3 Output: `architecture.md`

**Location:** `docs/architecture.md`  
**Updated:** After context scan + after each major task  

**Sections:**
- System overview diagram (graphify-generated)
- Component responsibilities
- Tech stack rationale
- Data flow diagrams
- API contract (evolves as backend executes)
- Database schema (from migrations)
- Deployment topology

### 2.4 Output: `context.json`

**Location:** `._context/context.json`  
**Updated:** Every task completion  

**Schema:**
```json
{
  "project": "string",
  "created_at": "ISO8601",
  "last_updated": "ISO8601",
  "tech_stack": {
    "frontend": "React 18+ / TypeScript",
    "backend": "Python 3.11 / FastAPI",
    "database": "PostgreSQL 14+"
  },
  "file_structure": {
    "backend": ["src/routes/", "src/models/", "src/services/"],
    "frontend": ["src/components/", "src/pages/", "src/hooks/"],
    "tests": ["tests/unit/", "tests/e2e/"]
  },
  "api_endpoints": [
    {
      "method": "POST",
      "path": "/api/auth/register",
      "description": "User registration",
      "schema": "UserRegisterRequest"
    }
  ],
  "database": {
    "tables": ["users", "activity_logs"],
    "primary_keys": {"users": "id"},
    "foreign_keys": [{"table": "activity_logs", "references": "users.id"}]
  },
  "dependencies": {
    "python": ["fastapi==0.100.0", "sqlalchemy==2.0.0"],
    "node": ["react==18.2.0", "typescript==5.1.0"]
  },
  "test_coverage": {
    "backend": 95,
    "frontend": 88,
    "overall": 92
  }
}
```

### 2.5 Output: `task-completion.json`

**Location:** Root directory + committed to git  
**Format:** JSON tracking all task executions  

**Schema:**
```json
{
  "project": "user_management_system",
  "generated_at": "2026-05-20T10:00:00Z",
  "requirement_version": "1.0",
  "architecture_version": "1.0",
  "execution_mode": "autonomous",
  "tasks": [
    {
      "id": "01-database-schema",
      "title": "Database Schema & Migrations",
      "status": "completed",
      "started_at": "2026-05-20T10:05:00Z",
      "completed_at": "2026-05-20T10:15:00Z",
      "duration_seconds": 600,
      "skill_used": "database_skill",
      "files_generated": [
        "src/migrations/001_init_users_table.sql",
        "src/migrations/002_init_activity_logs_table.sql"
      ],
      "test_coverage": 100,
      "status_details": {
        "success": true,
        "errors": [],
        "warnings": ["Consider adding indexes on foreign keys"]
      }
    },
    {
      "id": "02-backend-api",
      "title": "Backend API (Routes, Models, Services)",
      "status": "completed",
      "started_at": "2026-05-20T10:20:00Z",
      "completed_at": "2026-05-20T10:45:00Z",
      "duration_seconds": 1500,
      "skill_used": "backend_skill",
      "files_generated": [
        "src/routes/auth.py",
        "src/models/user.py",
        "src/services/user_service.py"
      ],
      "test_coverage": 94,
      "status_details": {
        "success": true,
        "errors": [],
        "warnings": []
      }
    }
  ],
  "integration": {
    "github": {
      "repository": "https://github.com/user/project",
      "branch": "feature/auto-generated",
      "pr_url": "https://github.com/user/project/pull/1",
      "pr_status": "open",
      "commit_messages": [
        "feat: initialize database schema with users and activity_logs tables",
        "feat: implement auth API routes and user service"
      ]
    },
    "claude_code": {
      "artifacts_synced": true,
      "skills_exported": ["backend_skill", "frontend_skill", "test_skill"],
      "agents_exported": ["autonomous_dev_agent"]
    }
  },
  "summary": {
    "total_tasks": 5,
    "completed": 3,
    "in_progress": 1,
    "pending": 1,
    "overall_progress": 60,
    "estimated_completion": "2026-05-20T14:30:00Z"
  }
}
```

---

## 3. Task Folder Structure

Each task is a self-contained unit with specification, generated code, and execution metadata.

```
tasks/
├── README.md                          # Task guide
│
├── 01-database-schema/
│   ├── spec.md                        # Detailed requirements + acceptance criteria
│   ├── generated/
│   │   ├── schema.sql                 # Generated DDL
│   │   ├── migrations/
│   │   │   ├── 001_init_users.sql
│   │   │   └── 002_init_activity_logs.sql
│   │   └── indexes.sql
│   └── status.json                    # Execution metadata for this task
│
├── 02-backend-api/
│   ├── spec.md
│   ├── generated/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   └── user.py
│   │   ├── models/
│   │   │   └── user.py
│   │   ├── services/
│   │   │   └── user_service.py
│   │   └── tests/
│   │       ├── test_auth_routes.py
│   │       └── test_user_service.py
│   └── status.json
│
├── 03-frontend-ui/
│   ├── spec.md
│   ├── generated/
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── ProfilePage.tsx
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   └── Dashboard.tsx
│   │   ├── hooks/
│   │   │   └── useAuth.ts
│   │   ├── styles/
│   │   │   └── auth.module.css
│   │   └── tests/
│   │       ├── LoginForm.test.tsx
│   │       └── useAuth.test.ts
│   └── status.json
│
├── 04-integration-tests/
│   ├── spec.md
│   ├── generated/
│   │   ├── e2e/
│   │   │   ├── auth.e2e.ts
│   │   │   └── user_flow.e2e.ts
│   │   ├── api_integration/
│   │   │   └── api.integration.test.py
│   │   └── coverage/
│   │       ├── coverage.html
│   │       └── coverage.json
│   └── status.json
│
└── 05-deployment/
    ├── spec.md
    ├── generated/
    │   ├── docker-compose.yml
    │   ├── Dockerfile
    │   ├── .github/workflows/
    │   │   └── ci-cd.yml
    │   └── k8s/                       # Optional
    │       ├── deployment.yaml
    │       └── service.yaml
    └── status.json
```

**Per-task `status.json`:**
```json
{
  "task_id": "01-database-schema",
  "status": "completed",
  "started_at": "2026-05-20T10:05:00Z",
  "completed_at": "2026-05-20T10:15:00Z",
  "skill_used": "database_skill",
  "files_generated": 3,
  "test_coverage": 100,
  "errors": [],
  "warnings": [],
  "context_hash": "abc123def456"  # For tracking graphify updates
}
```

---

## 4. Project Detection & Context Building

### 4.1 Detection Algorithm

```
Agent reads requirement.txt
    ↓
Does .git/ exist AND code files present?
    ├─ YES: Existing project
    │       • List directory structure
    │       • Read existing docs (README.md, ARCHITECTURE.md, etc.)
    │       • Analyze git history (recent commits, authors, branches)
    │       • Detect tech stack from package.json, requirements.txt, pom.xml
    │       • Ask user: "Project purpose? Deployment target? Any constraints?"
    │       ↓
    │       Build context from existing code
    │
    └─ NO: New project
            Ask user:
            • "Tech stack preference?"
              - Option A: React + Python + PostgreSQL (default)
              - Option B: React + Java + SQL Server
              - Option C: Other (specify)
            • "Any external integrations or APIs?"
            • "Deployment target?" (local, Docker, cloud)
            ↓
            Create folder structure from template
```

### 4.2 Context Building Steps

**For Existing Projects:**
1. Scan directory structure → identify source folders, tests, configs
2. Read existing documentation → extract architectural knowledge
3. Analyze git log → understand project history, recent changes
4. Parse dependencies → detect tech stack and versions
5. Ask clarifying questions → fill gaps in understanding
6. Generate `context.json` from findings
7. Generate `architecture.md` from existing code patterns

**For New Projects:**
1. Ask user for tech stack preference
2. Create default folder structure
3. Initialize `context.json` with defaults
4. Create skeleton `architecture.md`
5. Prepare for first task execution

### 4.3 Graphify Integration

**Trigger:** After context scan + after each major task completion

**Input:**
- Parsed codebase files
- Generated code from tasks
- `architecture.md`

**Output:**
- `._context/graph.json` (knowledge graph structure)
- Token embeddings (cached for reuse in next execution)

**Purpose:**
- Detect component dependencies and architecture violations
- Identify cross-task impacts (e.g., if backend changes API, what frontend tasks need update?)
- Reuse cached embeddings for faster subsequent executions (token efficiency)
- Generate dependency diagrams for `architecture.md`

---

## 5. Task Generation & Specifications

### 5.1 Task Decomposition Strategy

Feature-driven → Deliverable-based tasks.

**Feature:** "User authentication with JWT"  
**Decomposes to:**
1. **Task 01:** Database Schema (users table, password hashing strategy)
2. **Task 02:** Backend API (POST /register, POST /login, GET /me endpoints)
3. **Task 03:** Frontend UI (LoginForm, RegisterForm, AuthContext)
4. **Task 04:** Integration Tests (E2E auth flow, coverage metrics)
5. **Task 05:** Deployment (Docker, CI/CD pipeline)

### 5.2 Task Specification Format

**File:** `tasks/{ID}-{name}/spec.md`

**Template:**
```markdown
---
task_id: 01-database-schema
title: Database Schema & Migrations
feature: User Authentication
skill_to_use: database_skill
estimated_duration_minutes: 30
acceptance_criteria_count: 4
---

## Overview
Create the PostgreSQL schema for user management with proper indexing, constraints, and migration strategy.

## Requirements
- [ ] Create `users` table with: id (UUID, PK), email (unique), password_hash, created_at, updated_at
- [ ] Create `activity_logs` table with: id (UUID, PK), user_id (FK), action (string), timestamp
- [ ] Add appropriate indexes on email (users), user_id (activity_logs)
- [ ] Implement migration numbering (001_init.sql, 002_add_indexes.sql)

## Acceptance Criteria
1. **Schema validity:** All DDL is valid PostgreSQL; no syntax errors
2. **Constraints:** Primary keys, foreign keys, unique constraints enforced
3. **Indexing:** Indexes exist on all foreign keys and unique columns
4. **Migrations:** Each migration is idempotent and can be rolled back

## Data Model
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE activity_logs (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  action VARCHAR(255),
  timestamp TIMESTAMP DEFAULT NOW()
);
```

## Skill Configuration
- **Skill:** database_skill
- **Language:** SQL (PostgreSQL)
- **Validation:** Test migrations with migration runner

## Success Metrics
- All migrations execute without errors
- Schema can be created and destroyed cleanly
- Indexes exist and improve query performance
```

---

## 6. Task Execution & Orchestration

### 6.1 Execution Flow (Per-Task Cycle)

```
1. Agent reads task/{ID}/spec.md
   ↓
2. Agent invokes appropriate skill
   - Database → database_skill
   - Backend API → backend_skill + python/java_advanced_skill
   - Frontend → frontend_skill + react_advanced_skill
   - Tests → test_skill
   ↓
3. Skill generates code in tasks/{ID}/generated/
   ↓
4. Agent runs validation
   - Syntax checks
   - Linting
   - Type checking (if applicable)
   ↓
5. Agent updates task-completion.json
   ↓
6. Agent updates context.json with new files/endpoints/tables
   ↓
7. Agent regenerates architecture.md
   ↓
8. Agent runs graphify to update knowledge graph
   ↓
9. Move to next task (loop)
```

### 6.2 Skill Invocation Details

**Backend Skill Invocation:**
```
Agent → Backend Skill
├── Input:
│   ├── task/{02}/spec.md (API endpoints, data models)
│   ├── context.json (existing database schema, auth rules)
│   └── architecture.md (API design patterns)
│
├── Calls: python_advanced_skill or java_advanced_skill
│
└── Output:
    ├── src/routes/auth.py
    ├── src/models/user.py
    ├── src/services/user_service.py
    ├── src/tests/test_auth_routes.py
    └── Generated code follows:
        - Language-specific conventions
        - Input validation & security patterns
        - Comprehensive docstrings
        - Type hints (Python) or type annotations (Java)
```

**Frontend Skill Invocation:**
```
Agent → Frontend Skill
├── Input:
│   ├── task/{03}/spec.md (UI requirements, user flows)
│   ├── context.json (API endpoints from completed backend task)
│   └── architecture.md (design system, component hierarchy)
│
├── Calls: frontend-design skill + react_advanced_skill
│
└── Output:
    ├── src/components/LoginForm.tsx
    ├── src/pages/Login.tsx
    ├── src/hooks/useAuth.ts
    ├── src/styles/auth.module.css
    ├── src/tests/LoginForm.test.tsx
    └── Generated code follows:
        - React 18+ best practices
        - TypeScript strict mode
        - Accessible HTML (a11y)
        - Responsive design (Tailwind CSS)
```

**Test Skill Invocation:**
```
Agent → Test Skill
├── Input:
│   ├── All completed task code (backend + frontend)
│   ├── task/{04}/spec.md (test scenarios, coverage targets)
│   └── context.json (endpoints, data models)
│
├── Calls:
│   ├── pytest (for Python backend tests)
│   ├── Jest/Playwright (for React frontend tests)
│   ├── Coverage tools
│
└── Output:
    ├── tests/unit/*.test.py (pytest)
    ├── tests/e2e/*.e2e.ts (Playwright)
    ├── tests/integration/*.integration.py
    ├── coverage/coverage.html
    ├── coverage/coverage.json
    └── Reports:
        - Coverage: 95%+ target
        - Test results: All passing
        - Performance: API response times
```

---

## 7. Autonomous Execution & Failure Handling

### 7.1 Serial Execution with Dependency Awareness

Tasks execute in sequence with dependency tracking:

```
Task 01 (Database)
    ↓
    └─→ context.json updated with schema
        ↓
        Task 02 (Backend API)
            ↓
            └─→ context.json updated with endpoints
                ↓
                Task 03 (Frontend UI)
                    ↓
                    └─→ context.json updated with components
                        ↓
                        Task 04 (Integration Tests)
                            ↓
                            └─→ Coverage reports generated
                                ↓
                                Task 05 (Deployment)
```

### 7.2 Error Handling Strategy

| Error Type | Detection | Recovery |
|-----------|-----------|----------|
| **Syntax Error** | Linting fails | Log error, skip task, continue to next |
| **Validation Failure** | Type check fails | Log error, suggest fix in comments, continue |
| **Skill Timeout** | Execution >5 min | Interrupt, log, continue to next task |
| **Dependency Missing** | Task references non-existent context | Backtrack, re-run dependent task |
| **Critical Error** | Database schema invalid | Stop all, report to user, await input |

**Logging:** All errors logged to `task-completion.json` with detailed messages.

---

## 8. Platform Integration

### 8.1 GitHub Integration

After all tasks complete:

1. Create feature branch: `feature/auto-generated-YYYY-MM-DD`
2. Commit all generated code with meaningful messages
3. Open PR with:
   - Summary from `requirement.md`
   - Task breakdown and status
   - Link to `task-completion.json`
   - Code review checklist
4. Update PR status in `task-completion.json`

**Example PR description:**
```markdown
## Auto-Generated Development by Autonomous Developer Agent

### Summary
Generated complete implementation from requirement.txt for user authentication system.

### Task Breakdown
- ✅ Task 01: Database schema (100% complete)
- ✅ Task 02: Backend API (100% complete)
- ✅ Task 03: Frontend UI (100% complete)
- ✅ Task 04: Integration tests (100% complete)
- ✅ Task 05: Deployment (100% complete)

### Code Quality
- Overall test coverage: 95%
- Backend coverage: 97%
- Frontend coverage: 93%

### Artifacts
- [Task Completion Report](./task-completion.json)
- [Architecture Document](./docs/architecture.md)
- [Requirement Specification](./docs/requirement.md)

Generated: 2026-05-20T14:30:00Z
```

### 8.2 Claude Code / Copilot Integration

1. Export all generated skills to `.claude/skills/` and `.copilot/skills/`
2. Export agent to `.claude/agents/autonomous_dev_agent.md`
3. Sync `task-completion.json` to `.claude/` folder
4. Update `AGENTS.md` with agent description
5. Create summary artifact in `.claude/projects/` subfolder

---

## 9. Knowledge Graph & Token Caching

### 9.1 Graphify Output

**Input:** Full codebase snapshot  
**Output:** `._context/graph.json`

**Structure:**
```json
{
  "nodes": [
    {"id": "User", "type": "model", "properties": ["id", "email", "password_hash"]},
    {"id": "ActivityLog", "type": "model", "properties": ["id", "user_id", "action"]},
    {"id": "AuthService", "type": "service", "methods": ["register", "login", "verify"]},
    {"id": "LoginPage", "type": "component", "dependencies": ["useAuth", "LoginForm"]}
  ],
  "edges": [
    {"source": "ActivityLog", "target": "User", "type": "references"},
    {"source": "LoginPage", "target": "AuthService", "type": "calls"},
    {"source": "AuthService", "target": "User", "type": "queries"}
  ],
  "clusters": [
    {"id": "auth", "nodes": ["AuthService", "User", "LoginPage"], "cohesion": 0.95}
  ]
}
```

### 9.2 Token Caching Strategy

- **Cache Key:** Hash of codebase + `architecture.md` + `requirement.md`
- **Store:** `._context/graph_embeddings.json`
- **Reuse:** In next execution, load cached embeddings instead of re-computing
- **Invalidation:** When code changes or requirements evolve

---

## 10. Success Criteria & Acceptance Tests

### 10.1 System-Level Acceptance Criteria

- [ ] Agent reads plain-text `requirement.txt` without errors
- [ ] Agent generates valid `requirement.md` matching standard format
- [ ] Agent correctly detects new vs. existing projects
- [ ] Agent generates `architecture.md` with component diagrams
- [ ] Agent creates task folder structure with all `spec.md` files
- [ ] All 5 tasks execute sequentially without blocking
- [ ] Each task generates valid, tested code
- [ ] `task-completion.json` accurately tracks all task status
- [ ] Graphify integration produces valid `graph.json`
- [ ] GitHub PR created with complete summary
- [ ] Claude Code artifacts synced without errors

### 10.2 Code Quality Gates

- Test coverage ≥ 95% across all generated code
- Zero linting errors (ESLint, pylint, Checkstyle)
- Type checking passes (TypeScript strict, mypy strict)
- No hardcoded secrets or credentials
- SQL injection / XSS vulnerabilities: 0
- All generated components have docstrings/JSDoc

---

## 11. Skill Specifications

### 11.1 New Skills to Create

#### **A. Database Skill** (derivative of existing)
- Generates DDL for PostgreSQL / MySQL / SQL Server
- Creates migrations with rollback support
- Validates schema integrity
- Tests: SQL validation, migration reversibility

#### **B. Backend Skill** (wraps existing python/java skills)
- Generates API routes (FastAPI / Spring Boot)
- Creates models and services
- Implements authentication (JWT)
- Tests: Route testing, service mocking

#### **C. Frontend Skill** (wraps existing react skill)
- Generates React components with TypeScript
- Creates pages and layouts
- Implements hooks and state management
- Tests: Component testing, integration testing

#### **D. Test Skill** (new)
- Invokes pytest for Python tests
- Invokes Jest/Playwright for React tests
- Generates coverage reports
- Validates test coverage thresholds

#### **E. Architecture Skill** (new)
- Parses generated code
- Updates `architecture.md`
- Updates `context.json`
- Invokes graphify and stores results

### 11.2 Autonomous Developer Agent

**Role:** Master orchestrator

**Responsibilities:**
- Parse `requirement.txt` → generate `requirement.md`
- Detect project state and build context
- Generate task specifications
- Invoke skills in sequence
- Track completion in JSON
- Sync to GitHub + Claude Code

---

## 12. Implementation Roadmap (Phases)

### Phase 1: Core Agent + Basic Skills (Weeks 1-2)
- [ ] Create autonomous_dev_agent.md
- [ ] Implement requirement.txt parser → requirement.md generator
- [ ] Create database_skill.md
- [ ] Create backend_skill.md (wrapper)
- [ ] Implement project detection logic
- [ ] Implement context.json generator

### Phase 2: Frontend + Testing (Weeks 3-4)
- [ ] Create frontend_skill.md (wrapper)
- [ ] Create test_skill.md
- [ ] Implement task folder structure generator
- [ ] Implement graphify integration
- [ ] Implement task-completion.json tracker

### Phase 3: Integration (Week 5)
- [ ] Implement GitHub PR creation
- [ ] Implement Claude Code sync
- [ ] End-to-end testing
- [ ] Documentation and examples

### Phase 4: Polish & Deployment (Week 6)
- [ ] Error handling refinement
- [ ] Performance optimization (token caching)
- [ ] User guide and troubleshooting
- [ ] Release and distribution

---

## 13. File Locations & Naming

**Agent File:**
- Location: `agents/autonomous_dev_agent.md`
- Slug: `autonomous_dev_agent`

**Skills Files:**
- Location: `skills/{skill_name}_skill.md`
- Examples:
  - `skills/database_skill.md`
  - `skills/backend_skill.md`
  - `skills/frontend_skill.md`
  - `skills/test_skill.md`
  - `skills/architecture_skill.md`

**Generated Outputs:**
- Requirement: `docs/requirement.md`
- Architecture: `docs/architecture.md`
- Context: `._context/context.json`
- Graph: `._context/graph.json`
- Tasks: `tasks/{ID}-{name}/`
- Completion: `task-completion.json`

---

## 14. Assumptions & Constraints

**Assumptions:**
- User provides `requirement.txt` with enough detail to infer tech stack
- Existing projects have some documentation (README, git history)
- Generated code follows repo's existing patterns (if updating existing project)
- All generated code is reviewed before merge

**Constraints:**
- Agent cannot push to protected branches (PR only)
- Agent cannot delete existing code (append-only, migrations only)
- Agent cannot modify CI/CD without explicit permission
- Test coverage target: ≥95%
- Maximum serial task duration: 5 minutes (soft limit)

---

## 15. Future Enhancements (Post-MVP)

- Parallel task execution (where dependencies allow)
- Multi-language support (Go, Rust, etc.)
- Cloud-native deployment templates (Kubernetes, Terraform)
- AI-powered test case generation
- Performance profiling and optimization
- Security scanning (OWASP, SCA)
- API documentation generation (OpenAPI/Swagger)

---

**Document Version:** 1.0  
**Last Updated:** 2026-05-20  
**Status:** Ready for Implementation
