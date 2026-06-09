# Agent Functions Reference — Verified & Enhanced

**Version:** 3.1 (Enhanced with examples, guardrails, error handling)  
**Date:** June 9, 2026  
**Total Functions:** 28 callable functions across 5 agents

---

## Quick Function Index

| Agent | Functions | Count |
|-------|-----------|-------|
| **Orchestrator** | plan, build, context, pr, review, tradeoff, risk, ideate, solve | 9 |
| **Architect** | design, refactor, frontend, schema, api, a11y | 6 |
| **Implementer** | build, test, doc, pipeline, docker, iac, full | 7 |
| **Quality** | review, audit, security, perf, debug, report | 6 |
| **Business Analyst** | report, parse | 2 |
| **TOTAL** | | **28** |

---

## Linear Execution Pipeline

```
Requirement Input
    ↓
orchestrator:ideate (OPTIONAL—for vague ideas)
    ↓
orchestrator:plan (Parse requirements → tasks)
    ↓
architect:design (System topology, API, schema)
    ↓
orchestrator:solve (OPTIONAL—for bottleneck solving)
    ↓
implementer:full (Build + test + doc)
    ↓
quality:review
    ↓
orchestrator:pr (Create GitHub PR)
```

---

## ORCHESTRATOR AGENT

**Role:** Strategy & Orchestration — Technical leadership, requirements parsing, strategic planning, PR creation, review synthesis

**Functions:** plan, build, context, pr, review, tradeoff, risk, ideate, solve (9 total)

---

### orchestrator:ideate

**Purpose:** Transform vague, high-level ideas into validated project plans. Refines concepts through expert feedback, surfaces hidden assumptions, and generates executable specifications ready for implementation.

**Inputs:**
- idea (string): Initial concept (can be sketchy, informal, or incomplete)
- context (string, optional): Business context or domain expertise
- scope (string, optional): Rough scale or constraints ("startup MVP", "enterprise scale", etc.)

**Outputs:**
- idea-spec.md (markdown): Clarified feature specification with assumptions, scope boundaries, non-goals
- project-plan.json (JSON): Executable project plan with phases, deliverables, timeline estimate
- raid-analysis.md (markdown): Risk, Assumption, Issue, Decision (RAID) matrix documenting decisions made during ideation
- project-plan.csv (CSV): Exportable task list with IDs, titles, effort estimates, dependencies

**Guardrails:**
- Never assumes scope without asking clarifying questions first (Think Before Coding principle)
- Documents all assumptions explicitly—prevents "silent failures" from misaligned expectations
- Identifies risks early—saves weeks of rework downstream
- Scope is deliberately bounded—no infinite requirements creep
- Output is human-readable AND machine-processable (markdown + JSON + CSV)

**Examples:**

#### Example 1: From Vague Startup Idea to Specification
**Context:** Founder has rough idea for marketplace, no technical spec.

**Execution:**
```bash
orchestrator:ideate idea="Platform to connect dog walkers with pet owners. 
Like Uber for dog walking. Need to launch in 3 months. Target: San Francisco Bay Area."
```

**Expected Result:**
```
idea-spec.md
├─ Clarified Concept
│  ├─ Dog walker marketplace (B2C, peer-to-peer)
│  ├─ Geographic: San Francisco Bay Area (phased expansion Q2)
│  ├─ MVP scope: Browse walkers, book walk, pay, rate
│  └─ Not in scope: Insurance, scheduling templates, subscription plans
├─ Assumptions Documented
│  ├─ Walkers are individuals (not companies)
│  ├─ Payment via credit card only (not cash)
│  ├─ Initial 100 walkers, 500 users acceptable for MVP
│  └─ Launch without insurance initially, add later
└─ Hidden Requirements Surfaced
   ├─ Background checks (safety-critical)
   ├─ Customer support for disputes
   ├─ Real-time location tracking

project-plan.json
├─ Phase 1: MVP Backend (2 weeks)
│  ├─ User authentication
│  ├─ Walker profiles
│  ├─ Booking system
│  └─ Payment integration (Stripe)
├─ Phase 2: MVP Frontend (1.5 weeks)
│  ├─ User search + filter
│  ├─ Booking flow
│  └─ Rating system
├─ Phase 3: QA + Launch (0.5 weeks)
│  ├─ Testing
│  ├─ Deployment
│  └─ Go-live
└─ Timeline: 4 weeks total (buffer for unknowns)

raid-analysis.md
├─ Risks
│  ├─ Background checks delay MVP (mitigation: use third-party API)
│  ├─ Stripe approval time (mitigate: apply immediately)
│  └─ Regulatory (insurance) (mitigate: terms of service, liability cap)
├─ Assumptions
│  ├─ Team can build full-stack in 3 months (3 engineers) ✓
│  ├─ Stripe approval within 1 week ✓
│  └─ Initial market is SF only
├─ Issues
│  ├─ Background check vendor response time
│  └─ Payment settlement timing
└─ Decisions
   ├─ MVP ships without insurance (add in v1.1)
   └─ Use Stripe Connect for walker payouts
```

---

#### Example 2: Vague Feature Request to Spec
**Context:** Product team request "improve search experience"

**Execution:**
```bash
orchestrator:ideate idea="improve search experience in e-commerce app. 
Customers have trouble finding products."
```

**Expected Result:**
Questions asked during ideation:
- Q: "What's the current pain? Filters not working, slow results, irrelevant results?"
- A: "Irrelevant results. People search for 'leather bag' and get shoe bags."
- Q: "How many products in catalog?"
- A: "50K SKUs"
- Q: "Search volume per day?"
- A: "5K searches/day, 8% convert to purchase"
- Q: "Current search implementation?"
- A: "Basic full-text index on product name"

Outputs clarification:
```
Clarified scope:
✓ Improve relevance (ML ranking on catalog data)
✗ NOT: Full-text search rewrite (just improve ranking)
✗ NOT: Natural language processing (start simple)

MVP:
1. Synonym expansion (leather=skin, bag=purse)
2. Category boosting (match query to category)
3. Popularity ranking (more reviews = higher rank)
4. Effort: 1 week
5. Expected impact: Search-to-purchase from 8% → 12%
```

---

#### Example 3: Legacy System Modernization Plan
**Context:** CTO wants to "modernize 10-year-old monolith"

**Execution:**
```bash
orchestrator:ideate idea="Modernize legacy monolith. 
Currently 5M LOC, 100K users, 4-hour deployments, blocking new features."
```

**Expected Result:**
Structured project plan with phases:
```
Phase 1: Assessment (2 weeks)
├─ Map current architecture
├─ Identify critical vs. legacy modules
├─ Choose target architecture (microservices, strangler, etc.)
└─ Cost/timeline estimate

Phase 2: Migration Strategy (4 weeks)
├─ Select first microservice to extract
├─ Design integration points
├─ Build proof-of-concept
└─ Test zero-downtime migration

Phase 3: Phased Extraction (12+ weeks)
├─ Service 1: User management (4 weeks)
├─ Service 2: Order processing (4 weeks)
├─ Service 3: Inventory (4 weeks)
└─ Monolith reduced to 20% size

Decision log documents: Why microservices? Could've chosen modular monolith.
Microservices chosen because: team growth, deployment independence, tech flexibility.
```

---

**Error Handling:**
- **Incomplete input:** If idea is too vague (< 3 sentences), ask for more context before proceeding
- **Conflicting constraints:** If "3-month timeline" + "enterprise scale to 10M users" conflict, surface explicitly and ask for tradeoff decision
- **Scope creep detected:** If hidden assumptions would significantly expand scope, flag and recommend prioritization
- **Market/tech concerns:** If idea has known market or technical risks, document them upfront

**Edge Cases:**
- **Greenfield vs. Brownfield:** Function detects if idea is new system or modernization of existing, adjusts output structure accordingly
- **Unknown technology domain:** If domain is unfamiliar (e.g., "build a drone management platform"), function asks for domain expert consultation or surfaces knowledge gaps
- **Regulatory/compliance:** If domain has regulations (healthcare, finance, PCI), adds compliance considerations to RAID matrix
- **Cross-team dependencies:** If project requires coordination with multiple teams, dependency mapping is included in project plan

**Testing Approach:**
- **Unit test:** Verify idea parsing correctly extracts requirements, assumptions, constraints
- **Integration test:** Run ideate → plan → build pipeline, verify outputs are compatible and complete
- **Validation:** Output is reviewable by non-technical stakeholders (business, product, design); no jargon
- **Acceptance:** Project plan is executable—team can start development immediately without rework

---

### orchestrator:solve

**Purpose:** Solve specific design bottlenecks and architectural constraints. Provides multi-dimensional solutions with prescriptive recommendations. Ideal for unblocking teams facing tradeoff decisions.

**Inputs:**
- problem (string): Specific bottleneck or constraint (e.g., "Database query takes 10 seconds", "Can't scale beyond 10K concurrent users")
- context (string, optional): Current architecture, constraints, team size
- constraints (string, optional): Budget, timeline, team expertise ("3 engineers, 2 weeks, no new infrastructure")

**Outputs:**
- solutions.md (markdown): 3-5 solution approaches with detailed analysis
- recommendation.md (markdown): Ranked recommendation with implementation steps and rationale
- comparison-table.csv (CSV): Side-by-side effort, complexity, scalability, risk comparison
- implementation-roadmap.json (JSON): Step-by-step implementation plan with effort estimates

**Guardrails:**
- Solutions are ranked by pragmatism (best fit given constraints), not just technical elegance
- Always provides a "quick win" (implement in < 1 week) plus longer-term fixes
- Recommendation is specific and actionable, not generic
- Includes "when this solution breaks" (scaling limits, maintenance concerns)
- No hand-wavy solutions—each approach includes concrete code/infrastructure examples

**Examples:**

#### Example 1: Database Performance Bottleneck
**Context:** E-commerce platform. Product search takes 10 seconds for 50K product catalog.

**Execution:**
```bash
orchestrator:solve problem="Product search query takes 10 seconds for 50K items. 
Users experience timeout." context="PostgreSQL on AWS RDS, 2GB RAM, single instance. 
Team: 1 DBA, 2 backend engineers."
```

**Expected Result:**
```
solutions.md
├─ Solution 1: Database Index Optimization (Quick Win)
│  ├─ Problem: Query missing index on search columns
│  ├─ Implementation: 
│  │  └─ CREATE INDEX idx_products_name_category ON products(name, category)
│  ├─ Expected improvement: 10s → 200ms (50x faster)
│  ├─ Effort: 2 hours
│  ├─ When it breaks: > 100K products (index too large)
│  └─ Cost: $0 (no infra change)
│
├─ Solution 2: Elasticsearch (Medium-term)
│  ├─ Add dedicated search cluster (Elasticsearch)
│  ├─ Sync products from PostgreSQL to Elasticsearch
│  ├─ Expected improvement: 10s → 100ms (100x faster)
│  ├─ Enables: Advanced filtering, faceting, typo tolerance
│  ├─ Effort: 1 week
│  ├─ When it breaks: 1M+ products (needs sharding)
│  └─ Cost: $200/month (AWS managed Elasticsearch)
│
└─ Solution 3: Read Replicas + Caching (Enterprise)
   ├─ Database: PostgreSQL with 3 read replicas
   ├─ Cache: Redis for popular searches
   ├─ Expected improvement: 10s → 50ms (200x faster)
   ├─ Enables: 1M+ products, 100K concurrent users
   ├─ Effort: 3 weeks
   ├─ When it breaks: Distributed tracing needed at scale
   └─ Cost: $1K/month (replicas + Redis)

recommendation.md
├─ Recommended Approach: Solution 1 + Solution 2 Phased
│  ├─ Week 1: Apply database indexes (immediate relief)
│  ├─ Week 2-3: Setup Elasticsearch (proper long-term fix)
│  ├─ Rationale:
│  │  ├─ Addresses immediate pain (timeout issue)
│  │  ├─ Fits timeline and team size
│  │  ├─ Elasticsearch enables future features (facets, suggestions)
│  │  └─ Index optimization is free insurance (helps Elasticsearch too)
│  ├─ Risk: Elasticsearch adds operational complexity
│  │  └─ Mitigate: Use managed service (AWS, no ops needed)
│  └─ Timeline: 3 weeks total

implementation-roadmap.json
├─ Phase 1: Index Optimization (Week 1)
│  ├─ Analysis: Identify slow query patterns
│  ├─ Implementation: Add indexes on name, category, price
│  ├─ Validation: Query < 200ms
│  └─ Effort: 4 hours
├─ Phase 2: Elasticsearch Setup (Week 2-3)
│  ├─ Provision: AWS Elasticsearch cluster (m5.large.elasticsearch)
│  ├─ Sync: Build product sync pipeline (batch + real-time)
│  ├─ Testing: Query performance < 100ms
│  └─ Effort: 40 hours (design + build + test)
└─ Phase 3: Switchover (Hour 2)
   ├─ Route: Redirect searches to Elasticsearch
   ├─ Fallback: Keep PostgreSQL for edge cases
   ├─ Monitor: Alert on search errors
   └─ Effort: 2 hours

comparison-table.csv
Solution,Effort,Complexity,Scalability Limit,Cost,When Sufficient
Index Optimization,2 hours,Low,100K products,$0,Until 100K items
Elasticsearch,40 hours,Medium,10M products,$200/mo,Most scenarios
Read Replicas + Redis,80 hours,High,Unlimited,$1K/mo,Extreme scale
```

---

#### Example 2: Architecture Bottleneck — Team Scaling
**Context:** Monolithic codebase. Two teams fighting over deployment times (4-hour waits).

**Execution:**
```bash
orchestrator:solve problem="Monolithic codebase blocks team scaling. 
Both teams deploy together, 4-hour cycle time." 
context="5-year legacy Java Spring monolith, 2 teams (5 engineers), 
30-minute test suite."
```

**Expected Result:**
Ranked solutions:
```
Solution 1: Better CI/CD (Quick Win)
├─ Parallelize tests: 30min → 10min
├─ Deploy during staging: Reduce deployment window to 15min
├─ Effort: 1 week
├─ Scalability: Supports 2-3 teams
└─ Risk: Minimal (CI/CD only, no code changes)

Solution 2: Service Extraction (Recommended)
├─ Extract 1 service per team (e.g., User Service, Order Service)
├─ Enable independent deployments
├─ Effort: 3-4 weeks (using Strangler pattern)
├─ Scalability: Supports 5+ teams
├─ Risk: Distributed systems complexity
└─ Timeline: Phased per service

Solution 3: Full Microservices (Overkill)
├─ Extract 5-6 microservices immediately
├─ Effort: 3 months
├─ Risk: Over-engineered for current team size
└─ Only if: Planning to scale to 20+ engineers
```

---

#### Example 3: Scaling Bottleneck — User Growth
**Context:** App hitting performance wall at 100K concurrent users. Need to scale to 1M.

**Execution:**
```bash
orchestrator:solve problem="App supports 100K concurrent users. 
Business needs 1M concurrent users in 6 months."
context="Single database instance, Node.js monolith, 10 engineers, 
AWS infrastructure."
```

**Expected Result:**
```
Multi-dimensional solution:
├─ Database: PostgreSQL replica + read-only followers
├─ Cache: Redis cluster for hot data (user sessions, product catalog)
├─ API: API Gateway + horizontal scaling (auto-scale to 50 instances)
├─ Frontend: CDN for static assets (CloudFront)
├─ Async: Queue-based processing (SQS for slow operations)

Ranked by pragmatism:
├─ Phase 1 (Quick, 2 weeks): Add caching + API scaling
│  └─ Gets to 300K concurrent users
├─ Phase 2 (Medium, 3 weeks): Database read replicas + async queues
│  └─ Gets to 700K concurrent users
└─ Phase 3 (Long-term, 4 weeks): Sharding + microservices
   └─ Supports 2M+ concurrent users

Recommendation: Phases 1+2 hit 1M target within timeline.
Phase 3 is buffer / future-proof.
```

---

**Error Handling:**
- **Problem too vague:** If problem statement is unclear ("system is slow"), ask clarifying questions before proposing solutions
- **Impossible constraints:** If constraints conflict ("1-week timeline + enterprise-grade architecture"), surface explicitly and ask for tradeoff
- **Unknown bottleneck:** If root cause is unclear, recommend diagnostics first (profiling, monitoring, load test) before prescribing solution
- **No single solution:** If problem is multi-faceted (e.g., code + infrastructure + team), provide layered solutions addressing each dimension

**Edge Cases:**
- **Already optimized:** If bottleneck is already at hardware limits, recommend scaling infrastructure or architectural redesign, not code tweaks
- **Multiple bottlenecks:** If problem has multiple contributing factors (N+1 queries + missing index + lack of caching), address highest-impact first
- **Vendor lock-in risk:** If solution creates vendor lock-in, surface alternatives and migration cost
- **Team capability gap:** If recommended solution requires expertise team doesn't have, include training/hiring considerations

**Testing Approach:**
- **Unit test:** Verify each solution is analyzed for effort, complexity, scalability
- **Integration test:** Run solve → implementation-roadmap to ensure roadmap is executable
- **Validation:** Share recommendation with subject-matter expert (DBA, architect) for feedback
- **Performance test:** For performance-related bottlenecks, verify proposed improvements with benchmarks

---

### orchestrator:plan

**Purpose:** Parse requirements in multiple formats (free text, JIRA, requirements.md) and break them down into executable tasks. Creates detailed task breakdown, acceptance criteria, dependencies, and execution order.

**Inputs:**
- requirement (string): Free-form requirement description
- source (string, optional): Source format ("jira", "file", "email", or infer)
- file_path (string, optional): Path to requirements file (requirements.md, acceptance-criteria.txt, etc.)
- ticket_id (string, optional): JIRA ticket ID (e.g., "PROJ-123")

**Outputs:**
- requirements.md (markdown): Clarified requirements with assumptions, scope, acceptance criteria, non-goals
- task-breakdown.json (JSON): List of tasks with IDs, titles, descriptions, effort estimates, dependencies
- execution-order.txt (text): Dependency graph showing task order and critical path
- dependencies.csv (CSV): Matrix showing which tasks depend on which

**Guardrails:**
- Requirements are clarified **before** tasks are created (no assumptions pass through)
- Each task has clear success criteria (acceptance criteria, done definition)
- Tasks are sized 1-5 days (no > 1-week tasks without breaking them further)
- Dependencies are explicit and mapped (prevents surprises during execution)
- Scope boundaries are clearly stated ("in scope" vs "not in scope")

**Examples:**

#### Example 1: E-Commerce MVP Requirement Breakdown
**Context:** Startup founder describes rough feature set.

**Execution:**
```bash
orchestrator:plan "Build user authentication with email and password. 
Users can register, login, reset password. Should work on mobile."
```

**Expected Result:**
```
requirements.md
├─ Clarified Scope
│  ├─ Authentication: Email/password only (no social login)
│  ├─ Passwordless options: Not in MVP
│  ├─ Mobile: Responsive web (not native apps)
│  ├─ Deployment: Single region (AWS us-east-1)
│  └─ Scale target: 1K users (can scale later)
├─ Acceptance Criteria
│  ├─ User can register with email + password
│  ├─ User cannot register with duplicate email
│  ├─ User can login with correct credentials
│  ├─ User blocked after 5 failed login attempts
│  ├─ User can reset password via email
│  ├─ Reset token expires after 1 hour
│  ├─ Frontend responsive on mobile (< 320px width)
│  └─ API response time < 200ms (p95)
├─ Non-Goals (Explicitly NOT in MVP)
│  ├─ Two-factor authentication
│  ├─ Social login (Google, GitHub)
│  ├─ Passwordless auth (magic links)
│  ├─ User sessions across devices
│  └─ Account deletion
└─ Assumptions
   ├─ Email delivery is non-blocking (async)
   ├─ Passwords stored hashed (bcrypt)
   └─ No audit log requirements

task-breakdown.json
├─ Task 01: Database Schema (1 day)
│  ├─ ID: AUTH-01
│  ├─ Create users table with email, password_hash, created_at, updated_at
│  ├─ Create unique index on email
│  ├─ Create sessions table for active sessions
│  ├─ Dependencies: None
│  ├─ Acceptance: Schema created, migrations runnable
│  └─ Owner: Backend engineer
│
├─ Task 02: Password Hashing & Security (1 day)
│  ├─ ID: AUTH-02
│  ├─ Setup bcrypt for password hashing
│  ├─ Implement password strength validation (min 12 chars, mixed case, numbers)
│  ├─ Dependencies: AUTH-01
│  └─ Acceptance: Passwords hashed with cost factor 12, validation tests pass
│
├─ Task 03: Registration Endpoint (1.5 days)
│  ├─ ID: AUTH-03
│  ├─ POST /register {email, password}
│  ├─ Validate email format
│  ├─ Check for duplicate email
│  ├─ Hash password, store user
│  ├─ Return 201 with user ID
│  ├─ Dependencies: AUTH-02
│  └─ Error cases: Duplicate email (400), weak password (400), server error (500)
│
├─ Task 04: Login Endpoint (1 day)
│  ├─ ID: AUTH-04
│  ├─ POST /login {email, password}
│  ├─ Lookup user by email
│  ├─ Compare password with hash
│  ├─ Create session token (JWT)
│  ├─ Return token in response (or httpOnly cookie)
│  ├─ Track failed attempts (rate limiting)
│  ├─ Dependencies: AUTH-02
│  └─ Error cases: User not found (400), wrong password (400), too many attempts (429)
│
├─ Task 05: Password Reset Flow (2 days)
│  ├─ ID: AUTH-05
│  ├─ POST /password-reset/request {email}
│  ├─ Generate reset token (16-char random)
│  ├─ Store reset token + expiration in database
│  ├─ Send reset email with link (async)
│  ├─ POST /password-reset/confirm {token, new_password}
│  ├─ Verify token, update password, invalidate token
│  ├─ Dependencies: AUTH-02, AUTH-03
│  └─ Error cases: Token expired, token invalid, weak password
│
├─ Task 06: Email Service Integration (1 day)
│  ├─ ID: AUTH-06
│  ├─ Setup SendGrid (or similar)
│  ├─ Create email templates (reset, confirmation)
│  ├─ Implement async queue (don't block registration on email)
│  ├─ Dependencies: None (can run in parallel with AUTH-03, AUTH-05)
│  └─ Acceptance: Emails sent within 5 minutes, templates render correctly
│
├─ Task 07: Frontend Registration Form (1.5 days)
│  ├─ ID: AUTH-07
│  ├─ Build React form with email, password inputs
│  ├─ Client-side validation (email format, password strength)
│  ├─ Show password strength meter
│  ├─ Submit to POST /register
│  ├─ Handle error responses (display messages)
│  ├─ Redirect to login on success
│  ├─ Dependencies: AUTH-03
│  ├─ Responsive: Mobile (320px), tablet, desktop
│  └─ Accessibility: WCAG 2.1 AA (labels, error messages, focus)
│
├─ Task 08: Frontend Login Form (1 day)
│  ├─ ID: AUTH-08
│  ├─ Build React form with email, password inputs
│  ├─ Submit to POST /login
│  ├─ Store token (httpOnly cookie or localStorage)
│  ├─ Redirect to dashboard on success
│  ├─ Display "Too many attempts" if locked
│  ├─ Dependencies: AUTH-04
│  └─ Remember me (optional, not MVP)
│
├─ Task 09: Backend Tests (1.5 days)
│  ├─ ID: AUTH-09
│  ├─ Unit tests: Password hashing, validation
│  ├─ Integration tests: Registration flow, login flow, password reset
│  ├─ Edge cases: Concurrent registration, token expiration, rate limiting
│  ├─ Target: 95%+ code coverage
│  ├─ Dependencies: AUTH-03, AUTH-04, AUTH-05
│  └─ Acceptance: All tests pass, coverage > 90%
│
├─ Task 10: Frontend Tests (1 day)
│  ├─ ID: AUTH-10
│  ├─ Unit tests: Form validation
│  ├─ Integration tests: Registration form submission, login flow
│  ├─ Accessibility tests: axe-core, keyboard navigation
│  ├─ Dependencies: AUTH-07, AUTH-08
│  └─ Target: 80%+ coverage
│
├─ Task 11: API Documentation (0.5 days)
│  ├─ ID: AUTH-11
│  ├─ Write OpenAPI spec for /register, /login, /password-reset
│  ├─ Document request/response schemas, error codes
│  ├─ Add cURL examples
│  ├─ Dependencies: AUTH-03, AUTH-04, AUTH-05
│  └─ Output: auth-api.md
│
└─ Task 12: Deployment & Testing (0.5 days)
   ├─ ID: AUTH-12
   ├─ Deploy to staging
   ├─ Run smoke tests (registration works, login works)
   ├─ Test on mobile (iOS/Android browsers)
   ├─ Deploy to production
   ├─ Monitor error rates
   ├─ Dependencies: AUTH-09, AUTH-10, AUTH-11
   └─ Rollback plan ready if issues detected

execution-order.txt
Critical Path (determines timeline):
Week 1:
  AUTH-01 (DB schema) → AUTH-02 (hashing) → AUTH-03 (register) → AUTH-07 (form)
  AUTH-02 → AUTH-04 (login) → AUTH-08 (login form)
  AUTH-06 (email service) [parallel with AUTH-03]
  
Week 2:
  AUTH-02 → AUTH-05 (password reset) 
  AUTH-09 (tests) [waits for AUTH-03, AUTH-04, AUTH-05]
  AUTH-10 (frontend tests) [waits for AUTH-07, AUTH-08]
  AUTH-11 (docs) [last, after implementation]
  AUTH-12 (deployment) [after tests pass]

Critical Path: AUTH-01 → AUTH-02 → (AUTH-03 + AUTH-04) → (AUTH-07 + AUTH-08) → AUTH-09 → AUTH-12
Total Duration: 2 weeks (6 developers working in parallel)
```

---

#### Example 2: Legacy System Migration Requirement
**Context:** CTO needs to break down "modernize monolith" into actionable tasks.

**Execution:**
```bash
orchestrator:plan file=modernization-plan.txt
```

**Expected Result:**
Tasks for each extraction phase:
```
Task 01: Current State Assessment (1 week)
├─ Map existing monolith architecture
├─ Identify module boundaries
├─ Document critical paths
├─ Estimate effort for each service extraction

Task 02-05: Extract Services (4 weeks, parallel)
├─ Service 1: User Management
├─ Service 2: Product Catalog
├─ Service 3: Order Processing
├─ Service 4: Payment Processing

Task 06: Integration Layer (2 weeks)
├─ API Gateway setup
├─ Service discovery
├─ Database migration

Task 07: Testing & QA (1 week)
├─ Integration tests
├─ End-to-end tests
├─ Performance testing

Task 08: Deployment & Cutover (3 days)
├─ Blue-green deployment
├─ Monitoring setup
├─ Rollback procedures
```

---

**Error Handling:**
- **Incomplete requirement:** If requirement is vague, ask clarifying questions ("What's the user scale? Timeline? Budget?")
- **Conflicting requirements:** If requirements contradict (e.g., "MVP in 1 week" + "support 1M users"), surface and ask for priority
- **Missing acceptance criteria:** If AC not provided, infer from requirement context or ask
- **Scope ambiguity:** If requirement could be interpreted multiple ways, document assumptions and ask for confirmation

**Edge Cases:**
- **Dependent systems:** If tasks depend on external systems not yet built, note critical path impact
- **Parallel vs. sequential:** Function automatically identifies which tasks can run in parallel (reduce timeline)
- **Risk tasks:** If a task is risky (e.g., "migrate 10M records"), recommend spike/POC first
- **Unknown unknowns:** If domain is unfamiliar, tasks include research/investigation time

**Testing Approach:**
- **Unit test:** Verify task breakdown has no circular dependencies, each task is sized reasonably
- **Integration test:** Run plan → build pipeline, verify tasks are executable in stated order
- **Validation:** Share task breakdown with engineering team, verify estimates are realistic
- **Execution:** Track actual time vs. estimate, use to refine estimating accuracy

---

### orchestrator:build

**Purpose:** Execute full-stack generation end-to-end. Orchestrates downstream agents (architect → implementer → quality) in sequence to produce a complete, tested system from clarified requirements.

**Inputs:**
- path (string): Path to requirements.md (output from orchestrator:plan)
- context (string, optional): Additional business context
- tech_stack (string, optional): Preferred tech stack (e.g., "Python FastAPI + React + PostgreSQL")

**Outputs:**
- Complete system with:
  - Backend code (models, routes, services, middleware)
  - Frontend code (components, pages, services)
  - Database schema (migrations, indexes)
  - Test suite (unit + integration, 95%+ coverage)
  - Documentation (README, API spec, architecture)
  - CI/CD pipeline (GitHub Actions or specified platform)
  - Docker configuration (Dockerfile, docker-compose.yml)
  - Infrastructure code (K8s manifests or Terraform)
  - GitHub PR (ready for review and merge)

**Guardrails:**
- No context loss between phases (architect → implementer → quality all in single context)
- Each phase's output feeds into next (no manual handoff needed)
- System is production-ready, not "almost done"—includes tests, docs, CI/CD, deployment config
- All requirements from requirements.md are implemented (verification at each phase)
- No code without tests, no tests without documentation

**Examples:**

#### Example 1: E-Commerce MVP End-to-End Build
**Context:** Complete system from requirements to deployed.

**Execution:**
```bash
orchestrator:build path=./requirements.md
```

**Expected Result:**
```
Generated System/
├─ Backend/ (FastAPI + PostgreSQL)
│  ├─ models/
│  │  ├─ user.py (User model with validation)
│  │  ├─ product.py (Product with inventory)
│  │  ├─ order.py (Order + order items)
│  │  └─ payment.py (Payment records)
│  ├─ routes/
│  │  ├─ users.py (register, login, profile)
│  │  ├─ products.py (list, search, details)
│  │  ├─ orders.py (create, list, cancel)
│  │  └─ payments.py (process, webhook)
│  ├─ services/
│  │  ├─ user_service.py (auth, validation)
│  │  ├─ order_service.py (order processing)
│  │  └─ stripe_service.py (payment processing)
│  ├─ middleware/
│  │  ├─ auth.py (JWT validation)
│  │  ├─ error_handler.py (consistent error responses)
│  │  └─ logging.py (structured logging)
│  ├─ database.py (SQLAlchemy setup)
│  ├─ main.py (FastAPI app)
│  └─ requirements.txt (dependencies)
│
├─ Frontend/ (React + TypeScript + Tailwind)
│  ├─ components/
│  │  ├─ ProductCard.tsx (product display)
│  │  ├─ Cart.tsx (shopping cart state)
│  │  ├─ CheckoutForm.tsx (payment form)
│  │  └─ Navbar.tsx (navigation + login)
│  ├─ pages/
│  │  ├─ ProductList.tsx (browse products)
│  │  ├─ Product.tsx (product details)
│  │  ├─ Checkout.tsx (order review + payment)
│  │  ├─ OrderConfirmation.tsx (success page)
│  │  ├─ Login.tsx (authentication)
│  │  └─ Dashboard.tsx (user orders)
│  ├─ services/
│  │  ├─ api.ts (HTTP client)
│  │  ├─ auth.ts (JWT management)
│  │  └─ stripe.ts (Stripe integration)
│  ├─ hooks/
│  │  ├─ useCart.ts (cart state)
│  │  ├─ useAuth.ts (auth state)
│  │  └─ useProducts.ts (fetch products)
│  ├─ App.tsx (routing, layout)
│  └─ package.json
│
├─ Database/
│  ├─ schema.sql (CREATE TABLE, constraints, indexes)
│  ├─ migrations/
│  │  └─ 001_initial_schema.sql
│  └─ seeds.sql (demo products)
│
├─ Tests/
│  ├─ backend/
│  │  ├─ test_users.py (auth tests)
│  │  ├─ test_orders.py (order flow tests)
│  │  ├─ test_payments.py (payment tests)
│  │  └─ conftest.py (fixtures, database setup)
│  ├─ frontend/
│  │  ├─ ProductCard.test.tsx
│  │  ├─ Cart.test.tsx
│  │  ├─ CheckoutForm.test.tsx
│  │  └─ setupTests.ts
│  └─ coverage/ (95%+ coverage reports)
│
├─ Docs/
│  ├─ README.md (project overview, setup, usage)
│  ├─ API.md (endpoints, schemas, examples)
│  ├─ ARCHITECTURE.md (system design, C4 diagram)
│  ├─ DATABASE.md (schema, migrations, backups)
│  ├─ DEPLOYMENT.md (production checklist, rollback)
│  └─ CONTRIBUTING.md (development guide)
│
├─ Infrastructure/
│  ├─ Dockerfile (multi-stage, optimized)
│  ├─ docker-compose.yml (local dev: api + db + cache)
│  ├─ .github/workflows/
│  │  ├─ ci.yml (test on push)
│  │  ├─ deploy.yml (deploy on merge to main)
│  │  └─ security.yml (SAST scan)
│  ├─ k8s/
│  │  ├─ deployment.yaml (API pods + replicas)
│  │  ├─ service.yaml (K8s service)
│  │  ├─ configmap.yaml (environment config)
│  │  └─ secret.yaml (secrets template)
│  └─ terraform/ (optional, for AWS/GCP)
│
└─ Reports/
   ├─ test-results.html (all tests passing)
   ├─ coverage-report.html (function/line/branch coverage)
   └─ pr-summary.md (ready for GitHub PR)

GitHub PR Summary:
Title: feat: e-commerce MVP (product catalog, shopping cart, checkout)
├─ Commits: ~30 commits (well-organized, atomic)
├─ Test Results: 245 tests passing, 0 failing
├─ Coverage: 95.2% (models, routes, services all > 90%)
├─ Security: ✓ SAST passed, ✓ No hardcoded secrets, ✓ OWASP Top 10 audit
├─ Performance: API p95 response time 120ms (< 200ms target)
├─ Deployment: Docker image built, K8s manifests ready
└─ Reviewers: @architect @security @frontend-lead
```

**Timeline:** 1-2 hours (depending on system complexity)

---

#### Example 2: Feature Implementation Build
**Context:** Add OAuth2 login to existing monolith.

**Execution:**
```bash
orchestrator:build path=./oauth2-requirements.md tech_stack="Java Spring Boot"
```

**Expected Result:**
- Spring Security configuration for OAuth2
- Google OAuth2 client setup
- Callback endpoint implementation
- JWT token generation
- Frontend login button + redirect
- Tests for OAuth flow
- Documentation (setup guide, deployment notes)
- PR ready for code review

---

**Error Handling:**
- **Missing requirements:** If requirements.md incomplete, ask for clarification before proceeding
- **Tech stack mismatch:** If specified tech stack doesn't match project, surface and confirm
- **Integration failures:** If architect output conflicts with implementer assumptions, resolve before code generation
- **Quality check failures:** If tests don't reach 95% coverage or security audit finds critical issues, halt and report

**Edge Cases:**
- **Brownfield system:** If adding to existing codebase, function detects and generates compatible code
- **Distributed system:** If system requires multiple services, generates per-service in coordinated way
- **Migration required:** If schema changes needed, generates migration scripts with rollback plans
- **Multiple tech stacks:** If system has multiple languages (Node + Python + React), generates appropriate code for each

**Testing Approach:**
- **Unit test:** Verify generated code passes linting, unit tests, type checking
- **Integration test:** Run generated system end-to-end (API + database + frontend)
- **Performance test:** Verify API response times meet requirements
- **Security test:** Run SAST, check for secrets, validate auth/authorization

---

### orchestrator:context

**Purpose:** Build deep project understanding for existing systems. Generates architecture documentation, technology summary, interactive visualization, and knowledge graph. Ideal for onboarding new team members or understanding unfamiliar codebases.

**Inputs:**
- path (string): Path to project root directory
- depth (string, optional): Analysis depth ("quick", "standard", "comprehensive")
- include_knowledge_graph (boolean, optional): Generate knowledge graph with D3 visualization

**Outputs:**
- architecture.md (markdown): C4 system diagram, component descriptions, data flows, caching strategy, deployment topology
- tech-stack.md (markdown): Technology reference table (languages, frameworks, databases, infrastructure)
- context.json (JSON): Machine-readable project metadata (modules, dependencies, APIs, deployment)
- design.html (HTML): Interactive 4-tab visualization (architecture, tech stack, file tree, API endpoints)
- knowledge-graph.json (JSON, optional): Module dependency graph for D3 rendering

**Guardrails:**
- Analysis is non-intrusive (read-only, no modifications to project)
- Generated documentation is immediately useful (not a data dump)
- Knowledge graph is accurate and complete (no missing dependencies)
- Output is version-controlled friendly (markdown + JSON for diffs)
- Visualization works offline (no external CDN dependencies)

**Examples:**

#### Example 1: Understand E-Commerce Monolith
**Context:** New engineer joining team. Needs 30-minute overview of 50K LOC codebase.

**Execution:**
```bash
orchestrator:context path=./ecommerce-monolith depth=comprehensive include_knowledge_graph=true
```

**Expected Result:**
```
docs/context/

architecture.md
├─ System Overview
│  ├─ E-Commerce Platform (B2C, peer-to-peer)
│  ├─ 50K lines of code, Python FastAPI
│  ├─ 100K active users, 1M products
│  └─ 99.9% uptime SLA
│
├─ C4 Level 1: System Context
│  ├─ Users (web/mobile browsers)
│  ├─ E-Commerce System (API, web UI)
│  ├─ Payment Processor (Stripe)
│  ├─ Email Service (SendGrid)
│  └─ Search Engine (Elasticsearch)
│
├─ C4 Level 2: Container Architecture
│  ├─ Frontend (React SPA)
│  ├─ API Server (FastAPI)
│  ├─ Database (PostgreSQL)
│  ├─ Cache (Redis)
│  ├─ Search (Elasticsearch)
│  └─ Message Queue (RabbitMQ)
│
├─ C4 Level 3: Components
│  ├─ User Service
│  │  ├─ Authentication
│  │  ├─ Authorization
│  │  └─ Profile Management
│  ├─ Product Service
│  │  ├─ Catalog
│  │  ├─ Search
│  │  └─ Inventory
│  ├─ Order Service
│  │  ├─ Order Processing
│  │  ├─ Fulfillment
│  │  └─ Tracking
│  ├─ Payment Service
│  │  ├─ Payment Processing
│  │  ├─ Billing
│  │  └─ Refunds
│  └─ Notification Service
│     ├─ Email
│     ├─ SMS
│     └─ Push
│
├─ Data Flows
│  ├─ User Registration Flow
│  │  └─ Register → Validate → Hash → Store → Confirm Email
│  ├─ Product Search Flow
│  │  └─ Search → Elasticsearch → Cache → Return results
│  └─ Order Processing Flow
│     └─ Create Order → Reserve Stock → Process Payment → Notify → Fulfill
│
├─ Critical Paths
│  ├─ User Login (auth service)
│  ├─ Product Search (Elasticsearch)
│  └─ Order Creation (order service + payment)
│
└─ Deployment Topology
   ├─ AWS ECS (API servers, auto-scaling)
   ├─ RDS PostgreSQL (managed database)
   ├─ ElastiCache Redis (managed cache)
   ├─ CloudFront CDN (static assets)
   └─ Route 53 DNS

tech-stack.md
├─ Backend
│  ├─ Language: Python 3.11
│  ├─ Framework: FastAPI 0.95.1 (async, auto-docs)
│  ├─ ORM: SQLAlchemy 2.0 (async)
│  ├─ Validation: Pydantic v2
│  └─ Testing: pytest with fixtures
│
├─ Frontend
│  ├─ Framework: React 18.2 (functional components)
│  ├─ Language: TypeScript 5.0 (strict mode)
│  ├─ State: Redux Toolkit
│  ├─ Styling: Tailwind CSS
│  └─ Testing: Vitest + RTL
│
├─ Database
│  ├─ Primary: PostgreSQL 15 (RDS)
│  ├─ Cache: Redis 7 (ElastiCache)
│  ├─ Search: Elasticsearch 8.0
│  └─ Messaging: RabbitMQ 3.11
│
├─ Infrastructure
│  ├─ Compute: AWS ECS (Fargate)
│  ├─ Networking: VPC + ALB
│  ├─ Storage: S3 (images, uploads)
│  ├─ CDN: CloudFront
│  └─ Monitoring: CloudWatch + Datadog
│
├─ External APIs
│  ├─ Stripe (payment processing)
│  ├─ SendGrid (email)
│  └─ Slack (notifications)
│
└─ CI/CD
   ├─ VCS: GitHub
   ├─ CI: GitHub Actions
   └─ Deployment: ECS auto-deploy on main merge

context.json
{
  "project": {
    "name": "E-Commerce Platform",
    "description": "B2C e-commerce with 100K users",
    "created_date": "2021-03-15",
    "last_updated": "2026-01-10"
  },
  "modules": [
    {
      "name": "user_service",
      "path": "src/services/user_service.py",
      "lines": 450,
      "functions": ["create_user", "authenticate", "get_profile"],
      "dependencies": ["database", "email_service"]
    },
    ...
  ],
  "databases": [
    {
      "type": "PostgreSQL",
      "role": "primary",
      "version": "15",
      "tables": ["users", "products", "orders", "payments"],
      "backup_schedule": "daily"
    }
  ],
  "apis": [
    {
      "endpoint": "/api/v1/products",
      "method": "GET",
      "authentication": "optional",
      "rate_limit": "1000/hour"
    }
  ],
  "deployment": {
    "platform": "AWS ECS",
    "regions": ["us-east-1"],
    "auto_scaling": true,
    "slo": "99.9% uptime"
  }
}

design.html
├─ Tab 1: Architecture
│  └─ C4 diagram with clickable components (shows details on hover)
├─ Tab 2: Tech Stack
│  └─ Table with technologies by layer (language, framework, version)
├─ Tab 3: File Tree
│  └─ Project structure (collapsible, shows file counts, key files highlighted)
└─ Tab 4: API Endpoints
   └─ Searchable/filterable list of all REST endpoints (method, path, auth, rate-limit)

knowledge-graph.json
{
  "nodes": [
    { "id": "user_service", "label": "User Service", "type": "service" },
    { "id": "product_service", "label": "Product Service", "type": "service" },
    ...
  ],
  "edges": [
    { "source": "user_service", "target": "database", "label": "queries" },
    { "source": "product_service", "target": "elasticsearch", "label": "indexes" },
    ...
  ]
}
```

**Timeline:** 10-15 minutes

---

#### Example 2: Understand Legacy Java System
**Context:** Team inheriting 10-year-old Spring Boot monolith (200K LOC).

**Execution:**
```bash
orchestrator:context path=./legacy-monolith depth=comprehensive
```

**Expected Result:**
- Architecture shows layered structure: controllers → services → repositories → entities
- Tech stack highlights deprecated libraries (Spring 4.x, Java 8)
- File tree shows tight coupling (User entity imported in 50+ places)
- Knowledge graph visualizes problematic dependencies
- context.json identifies "refactoring targets"

---

**Error Handling:**
- **Inaccessible project:** If path doesn't exist or insufficient permissions, report clearly
- **Unrecognized tech stack:** If language/framework not recognized, fall back to generic analysis
- **Massive codebase:** If > 1M LOC, sample analysis (random modules) rather than scanning all
- **No documentation:** If project has no README/docs, infer from code structure

**Edge Cases:**
- **Monolithic vs. microservices:** Function auto-detects and adjusts output structure
- **Multiple programming languages:** Analyzes each language separately, then shows integration points
- **Vendored dependencies:** Ignores node_modules, vendor/, etc. (configurable)
- **Sparse documentation:** Generates documentation even if project has none (code-derived)

**Testing Approach:**
- **Unit test:** Verify architecture detection (C4 levels correctly identified)
- **Integration test:** Verify generated files are consistent (cross-references work)
- **Validation:** Share with team member unfamiliar with project, verify 30-min onboarding achievable
- **Visualization test:** Open HTML in browser, verify tabs load, interactions work offline

---

### orchestrator:pr

**Purpose:** Package generated code, tests, documentation, and deployment config into a GitHub PR. Generates comprehensive PR description with architecture narrative, test results, security audit, and deployment checklist.

**Inputs:**
- title (string): PR title (e.g., "feat: e-commerce MVP")
- description (string, optional): PR description (auto-generated if not provided)
- branch (string, optional): Branch name (auto-generated from title if not provided)
- artifacts_path (string, optional): Path to generated artifacts (uses current directory if not specified)

**Outputs:**
- GitHub Pull Request with:
  - Title + comprehensive description (markdown)
  - Architecture summary (C4 diagram or narrative)
  - Feature checklist (acceptance criteria with checkmarks)
  - Test results (unit + integration + coverage)
  - Security audit results
  - Performance baseline
  - Deployment instructions
  - Linked reviewers (based on content type)
  - Deployment checklist (pre-launch validations)

**Guardrails:**
- PR is ready for review immediately (no "WIP" PRs)
- All required information present (title, description, test results, security audit)
- PR body is human-readable (markdown, well-formatted)
- Reviewers are intelligently assigned (architecture → architect, security → security team)
- Deployment checklist prevents accidental misconfiguration

**Examples:**

#### Example 1: E-Commerce MVP PR
**Execution:**
```bash
orchestrator:pr title="feat: e-commerce MVP with product catalog, shopping cart, Stripe checkout"
```

**Expected Result:**
```
GitHub PR

Title: feat: e-commerce MVP with product catalog, shopping cart, Stripe checkout
Branch: feature/ecommerce-mvp → main

Description:

## E-Commerce Platform MVP

### Summary
Complete e-commerce platform MVP implementation including:
- Product catalog with search and filtering
- Shopping cart with persistence
- Stripe payment integration
- Order management and fulfillment
- Email notifications (order confirmation, shipping updates)
- Admin dashboard for product/order management
- 95%+ test coverage
- Production-ready deployment configuration

### Features Implemented
- [x] User authentication (email/password)
- [x] Product search with Elasticsearch
- [x] Shopping cart (add, remove, update quantities)
- [x] Stripe payment integration (live + test modes)
- [x] Order tracking (create, view, cancel)
- [x] Email notifications (SendGrid)
- [x] Admin dashboard (manage products, orders)
- [x] Mobile-responsive UI (Tailwind CSS)
- [x] WCAG 2.1 AA accessibility compliance
- [x] Rate limiting + DDoS protection

### Architecture
```
┌─ Frontend (React 18)
│  ├─ ProductList.tsx
│  ├─ Cart.tsx
│  ├─ Checkout.tsx
│  └─ Dashboard.tsx
│
├─ API (FastAPI)
│  ├─ products routes
│  ├─ orders routes
│  ├─ payments routes
│  └─ users routes
│
├─ Services
│  ├─ OrderService
│  ├─ StripeService
│  └─ EmailService
│
└─ Infrastructure
   ├─ PostgreSQL (primary DB)
   ├─ Redis (caching)
   ├─ Elasticsearch (search)
   └─ RabbitMQ (async tasks)
```

### Test Results
```
Backend Tests:
- Unit tests: 156 passing, 0 failing
- Integration tests: 89 passing, 0 failing
- Total: 245 passing, 0 failing
- Coverage: 95.2% (models 98%, routes 94%, services 96%)

Frontend Tests:
- Component tests: 72 passing, 0 failing
- Integration tests: 23 passing, 0 failing
- Accessibility tests: All WCAG 2.1 AA checks passing
- Total: 95 passing, 0 failing
- Coverage: 88% (critical paths 95%)

E2E Tests:
- User registration flow ✓
- Product search flow ✓
- Order checkout flow ✓
- Admin dashboard flow ✓
```

### Performance
```
Backend:
- API response time (p50): 45ms
- API response time (p95): 120ms
- Database query time (p95): 80ms
- All endpoints meet < 200ms SLA ✓

Frontend:
- Page load time (3G): 1.8s
- Lighthouse score: 92/100
- Core Web Vitals: All green ✓
- Mobile-responsive: Tested on 320px-1920px ✓
```

### Security
```
✓ OWASP Top 10 Audit: PASSED
✓ No hardcoded secrets (environment variables only)
✓ SQL injection protection (parameterized queries)
✓ XSS protection (React auto-escaping + CSP headers)
✓ Authentication (JWT tokens, httpOnly cookies)
✓ Authorization (role-based access control)
✓ Rate limiting (1000 req/hour per user)
✓ HTTPS enforcement + HSTS headers
```

### Database
```
Schema:
- users table (email, password_hash, profile, created_at)
- products table (name, price, stock, category)
- orders table (user_id, created_at, status, total)
- order_items table (order_id, product_id, quantity, price)
- payments table (order_id, stripe_id, status, amount)

Indexes:
- PRIMARY KEY on all tables
- UNIQUE INDEX on users(email)
- INDEX on orders(user_id, created_at)
- INDEX on products(category, price)

Migrations:
- 001_initial_schema.sql (tables, constraints)
- 002_add_indexes.sql (performance)
- Rollback procedures documented
```

### Deployment
```
Docker:
✓ Multi-stage Dockerfile (build + runtime)
✓ Health checks configured
✓ Environment variable substitution
✓ Docker Compose for local development

CI/CD:
✓ GitHub Actions pipeline (test on push, deploy on merge)
✓ Automated linting + type checking
✓ Security scanning (SAST)
✓ Automated deployment to ECS on main merge

Production Checklist:
- [ ] Database migrations tested
- [ ] Environment variables configured (secrets manager)
- [ ] Load testing passed (1K concurrent users)
- [ ] Monitoring & alerting configured
- [ ] Rollback procedure documented
- [ ] Incident response plan ready
- [ ] Backup/restore tested
- [ ] Documentation deployed
- [ ] Launch announcement prepared
```

### Files Changed
```
Backend (45 files):
├─ src/models/ (4 models: User, Product, Order, Payment)
├─ src/routes/ (4 routers: users, products, orders, payments)
├─ src/services/ (3 services: OrderService, StripeService, EmailService)
├─ src/middleware/ (auth, error handling, logging)
├─ src/database/ (schema, migrations, fixtures)
├─ tests/ (unit + integration tests, 95% coverage)
└─ requirements.txt (dependencies)

Frontend (38 files):
├─ src/components/ (ProductCard, Cart, CheckoutForm, etc.)
├─ src/pages/ (ProductList, Product, Checkout, Dashboard)
├─ src/services/ (api.ts, auth.ts, stripe.ts)
├─ src/hooks/ (useCart, useAuth, useProducts)
├─ tests/ (88% coverage)
└─ package.json

Infrastructure (12 files):
├─ Dockerfile
├─ docker-compose.yml
├─ .github/workflows/ (ci.yml, deploy.yml, security.yml)
├─ k8s/ (deployment.yaml, service.yaml, configmap.yaml)
└─ terraform/ (optional AWS resources)

Docs (8 files):
├─ README.md (project overview)
├─ API.md (endpoint reference)
├─ ARCHITECTURE.md (system design)
├─ DATABASE.md (schema reference)
├─ DEPLOYMENT.md (production checklist)
└─ CONTRIBUTING.md (dev guide)

Total: 103 files changed, 12,847 additions, 0 deletions
```

### Breaking Changes
None. This is a new MVP, backward compatibility not applicable.

### Migration Guide
For existing deployments: N/A (greenfield)

For future upgrades:
1. Backup production database
2. Deploy new version (blue-green)
3. Run migrations (automated via CI/CD)
4. Smoke test (verify endpoints respond)
5. Monitor for errors (30-minute observation period)
6. Rollback procedure: Deploy previous version

### Known Issues / Future Work
```
v1.1 Roadmap:
- [ ] Two-factor authentication
- [ ] Advanced inventory management (batch updates, re-stock alerts)
- [ ] Wishlist feature
- [ ] Subscription orders
- [ ] Automated email campaigns (abandoned cart recovery)
- [ ] Analytics dashboard (sales trends, top products)
- [ ] Bulk product import (CSV)
```

### Reviewers
- @architecture-team (system design, API contracts)
- @security-team (security audit, data protection)
- @frontend-team (UI/UX, accessibility)
- @devops-team (deployment, infrastructure)

### Linked Issues
- Resolves #123 (E-Commerce MVP feature request)
- Relates to #124 (Payment processing requirements)

### Additional Notes
- All code follows project style guide (linting passed)
- Documentation is complete and up-to-date
- No technical debt introduced
- Ready for production deployment

---

## Deployment Checklist (Before Merge)

- [ ] Code review approved
- [ ] All tests passing (local + CI)
- [ ] Security audit completed
- [ ] Performance baseline established (< 200ms p95)
- [ ] Database schema reviewed
- [ ] Environment variables documented
- [ ] Monitoring/alerting configured
- [ ] Incident response team briefed
- [ ] Rollback procedure tested
- [ ] Stakeholders notified

## Deployment Checklist (Before Launch)

- [ ] Production database backed up
- [ ] Blue-green environment ready
- [ ] Health checks verified
- [ ] Load testing passed
- [ ] Monitoring dashboard live
- [ ] On-call engineer assigned
- [ ] Customer support briefed
- [ ] Launch announcement ready
- [ ] Rollback tested
- [ ] Go/no-go decision made

---

Reviewers: @architecture, @security, @frontend, @devops
Auto-merge: Disabled (requires human review)
```

**Timeline:** 5 minutes (automatic)

---

#### Example 2: Security Patch PR
**Execution:**
```bash
orchestrator:pr title="fix: SQL injection vulnerability in search endpoint"
```

**Expected Result:**
```
GitHub PR
Title: fix: SQL injection vulnerability in search endpoint
Branch: fix/sql-injection-search → main

Description includes:
- Summary: SQL injection vulnerability in products.search_by_name()
- Severity: CRITICAL
- Impact: Attackers can execute arbitrary SQL queries
- Fix: Parameterized query (prepared statement)
- Before/after code
- Test case: Verify malicious input blocked
- Security team review: @security-lead
- Deployment: Can deploy immediately (no migration needed)
```

---

**Error Handling:**
- **Missing artifacts:** If generated code not found, report and ask for path
- **No tests:** If test results missing, ask to run tests first
- **Invalid GitHub credentials:** If auth fails, report and ask for PAT token
- **Merge conflicts:** If branch conflicts with main, suggest resolving before PR creation

**Edge Cases:**
- **Large PR (500+ files):** Function warns and asks if this should be split into multiple PRs
- **No reviewer available:** Function assigns to CODEOWNERS file if exists
- **Sensitive code:** Function detects secrets and prevents them from being committed
- **Work in progress:** Function can create as Draft PR if requested

**Testing Approach:**
- **Unit test:** Verify PR body is valid markdown, all sections present
- **Integration test:** Verify GitHub PR API call succeeds, PR created with correct data
- **Validation:** Check PR displays correctly in GitHub UI (formatting, links)

---

### orchestrator:review

**Purpose:** Conduct strategic architecture review with challenge questions, risk assessment, and 5-year maintainability analysis. Provides senior technical perspective on design decisions before implementation begins.

**Inputs:**
- path (string): Path to architecture document (architecture.md, design.md, or similar)
- context (string, optional): Additional business/technical context
- focus (string, optional): Specific areas to focus on ("scalability", "maintainability", "security")

**Outputs:**
- design-review.md (markdown): Comprehensive review with sections:
  - Summary (thumbs up/down on design)
  - Strengths (what's good)
  - Concerns (what could fail)
  - Challenge Questions (5-7 hard questions design needs to answer)
  - Risk Assessment (operational, scaling, team, integration risks)
  - 5-Year Maintenance Cost (is this sustainable long-term?)
  - Recommendations (specific, actionable changes)
  - Go/No-Go Decision (proceed as-is, modify, or redesign)

**Guardrails:**
- Review is brutally honest (not "everything looks great")
- Questions are challenging, not gotchas (forces deeper thinking)
- Concerns include failure modes (what breaks and when)
- Recommendations are prioritized (must-fix vs. nice-to-fix)
- Review considers team capability (can team maintain this long-term?)

**Examples:**

#### Example 1: Monolithic E-Commerce Design Review
**Execution:**
```bash
orchestrator:review path=./architecture.md context="E-commerce MVP, 3-person team, 6-month runway"
```

**Expected Result:**
```
design-review.md

ARCHITECTURE REVIEW — E-Commerce MVP
Date: 2026-01-10
Reviewer: Orchestrator Agent
Status: APPROVE WITH RECOMMENDATIONS

---

## Executive Summary
Design is solid for MVP scope (100K users, single region). Approval recommended with 3 important caveats about future scaling.

---

## Strengths
✓ Layered architecture (controllers → services → repositories) is clean
✓ API contract well-defined (OpenAPI spec, examples)
✓ Database schema normalized (3NF, good indexes)
✓ Auth strategy documented (JWT tokens, httpOnly cookies)
✓ Error handling is comprehensive (consistent error responses)
✓ Monitoring is planned (CloudWatch, Datadog)

---

## Concerns
❌ Single database instance is single point of failure
   → At 100K users, database becomes bottleneck
   → No read replicas for scaling reads

❌ No caching strategy documented
   → Product search will be slow at 50K+ products
   → Recommendation: Add Redis for sessions + product catalog cache

❌ Synchronous payment processing blocks requests
   → Failed Stripe calls block order checkout
   → Recommendation: Queue-based payment processing (async)

❌ No API rate limiting specified
   → Vulnerable to DDoS and brute-force attacks
   → Recommendation: Add rate limiting middleware (1000 req/hour per user)

❌ Frontend state management with Redux but no saga/middleware
   → Complex async flows (orders, payments) could be error-prone
   → Recommendation: Use Redux Thunk or Redux Saga

---

## Challenge Questions
1. How will you handle 1M concurrent users without resharding the database?
   → Current design hits wall at ~100K users (single DB instance)

2. What's your database backup and recovery time objective?
   → Missing from design (should be < 1 hour RTO, < 5 min RPO)

3. How will you detect and respond to payment processing failures?
   → If Stripe webhook fails, order status becomes inconsistent
   → Recommendation: Idempotent webhook handler + reconciliation job

4. How will you scale the search feature?
   → ElasticSearch planned, but no migration strategy from SQL full-text search
   → How will you handle search-lag during reindexing?

5. What's your incident response plan for 50% drop in orders?
   → No observability strategy documented (monitoring setup unclear)
   → Recommendation: Define SLOs, alerting rules, incident response runbook

6. How will you maintain team knowledge if the person who built this leaves?
   → Design is simple, but no runbooks or architecture decision records
   → Recommendation: ADRs (Architecture Decision Records) for major choices

7. What's the 5-year total cost of ownership?
   → AWS costs will grow as scale increases (RDS + Elasticsearch + Elasticache)
   → Recommendation: Model cost curve and capacity plan

---

## Risk Assessment

🔴 CRITICAL RISKS (Address before launch)

1. Single Database Instance (SPOF)
   - Risk: Database failure = complete outage
   - Impact: Revenue loss ($10K/hour if 100K users × $100 average order)
   - Probability: Low but catastrophic
   - Mitigation: 
     1. Add RDS read replicas for failover (4 hours to implement)
     2. Setup RDS automated backups (already in AWS)
     3. Test restore procedure (2 hours to test)
   - Timeline: Before launch (1 day)

2. No Payment Reconciliation
   - Risk: Order + payment can become inconsistent (order created but payment failed)
   - Impact: Customer confusion, revenue loss, support tickets
   - Probability: Medium (Stripe downtime 2-3x/year)
   - Mitigation:
     1. Idempotent webhook handler (catches duplicate webhooks)
     2. Payment reconciliation job (daily, cross-check orders vs. Stripe)
     3. Alert on discrepancies
   - Timeline: Before launch (2 days)

3. No Rate Limiting
   - Risk: DDoS attack or bot scrapers could take down API
   - Impact: Revenue loss, user frustration
   - Probability: Medium (attacks are common)
   - Mitigation:
     1. Add rate limiting middleware (1000 req/hour per IP)
     2. CloudFlare DDoS protection
     3. WAF rules for suspicious patterns
   - Timeline: Before launch (4 hours)

🟡 HIGH RISKS (Address within 1 week of launch)

1. No Caching Strategy
   - Risk: Product search + catalog load slow at 50K+ products
   - Mitigation: Add Redis cache for products (24-hour TTL)
   - Timeline: Week 1 after launch (2 days)

2. Async Payment Processing
   - Risk: Failed Stripe calls block checkout (poor UX)
   - Mitigation: Queue orders, process payments async, notify user
   - Timeline: Week 1 after launch (3 days)

3. No Search Reindexing Strategy
   - Risk: Elasticsearch out of sync with products table
   - Mitigation: Real-time reindex on product changes + daily full reindex
   - Timeline: Week 1 after launch (2 days)

🟢 MEDIUM RISKS (Address within 1 month)

1. No Mobile App
   - Risk: Users expect native app (but MVP is web-only)
   - Mitigation: Ship web MVP first, evaluate native app ROI later
   - Timeline: Post-launch evaluation

2. Admin Dashboard Lightweight
   - Risk: Operations team may find it slow to bulk-update products
   - Mitigation: Add bulk import (CSV) in v1.1

---

## 5-Year Maintenance Cost Analysis

Year 1: $50K
├─ AWS infrastructure: $30K/year (RDS, ElastiCache, Elasticsearch, ALB, CloudFront)
├─ Third-party services: $15K/year (Stripe fee, SendGrid, Datadog)
├─ Team cost: $400K/year (3 engineers)
└─ Total: $450K

Year 2-3: $80K/year (costs grow with scale)
├─ Added infrastructure (read replicas, load balancing): $20K/year
├─ Additional monitoring (APM, logging): $10K/year
└─ Team growth (from 3 → 5 engineers): $600K/year

Year 4-5: $150K/year
├─ Multiple regions, sharding, disaster recovery: $50K/year
├─ Full observability + incident response: $20K/year
└─ Team growth (from 5 → 8 engineers): $900K/year

Conclusion: Design is cost-effective for MVP. Scalability costs are manageable if growth justifies it.

---

## Recommendations

MUST FIX (Before launch):
1. Add database read replicas + failover
2. Implement payment reconciliation + idempotent webhooks
3. Add rate limiting (prevent DDoS)
4. Document backup/restore procedures + test

SHOULD FIX (Week 1 after launch):
1. Add Redis caching for products + user sessions
2. Async payment processing (queue-based)
3. Search reindexing strategy (real-time + batch)
4. Performance monitoring dashboard

NICE TO HAVE (Post-launch v1.1):
1. Advanced admin dashboard (bulk import)
2. Mobile app evaluation
3. Wishlist feature
4. Subscription orders

---

## Go/No-Go Decision

✓ GO (Approve with modifications)

Proceed with implementation with following pre-launch fixes:
1. Database replication (CRITICAL)
2. Payment reconciliation (CRITICAL)
3. Rate limiting (CRITICAL)
4. Monitoring setup (CRITICAL)

Timeline: 1 day to implement + 1 day to test = Ready for launch in 2 days

---

## Sign-Off
Design is sound for stated MVP scope. Scalability concerns are addressed in recommendations. Team capability is adequate for execution. Recommend approval pending critical fixes.

Reviewed by: Claude Orchestrator
Date: 2026-01-10
```

---

#### Example 2: Microservices Architecture Review
**Execution:**
```bash
orchestrator:review path=./microservices-design.md focus=scalability
```

**Expected Result:**
```
Review highlights concerns:
- Distributed tracing not mentioned (complex debugging across services)
- API Gateway single point of failure
- Database consistency strategy unclear (saga pattern not documented)
- Team may be too small for operational complexity of microservices

Recommendation: Consider modular monolith initially, migrate to microservices when team grows to 10+ engineers.
```

---

**Error Handling:**
- **No design document:** If file not found, ask for design path or context
- **Incomplete design:** If design is sketchy, proceed but flag assumptions needing clarification
- **Unknown domain:** If domain is unfamiliar (e.g., financial trading), recommend domain expert review

**Edge Cases:**
- **Greenfield system:** Review focuses on scalability, team capability, long-term costs
- **Brownfield migration:** Review focuses on compatibility, migration risk, rollback strategy
- **Experimental technology:** Review emphasizes risk and sustainability concerns
- **Tight timeline:** Review notes which recommendations are critical vs. nice-to-have

**Testing Approach:**
- **Unit test:** Verify review identifies legitimate risks (not false positives)
- **Validation:** Share review with architecture team, gather feedback
- **Impact:** Track which recommendations are implemented, measure outcomes (e.g., did adding caching help?)

---

### orchestrator:tradeoff

**Purpose:** Generate 3-option complexity analysis. Compares approaches on effort, complexity, scalability, cost, team capability. Provides ranked recommendation based on constraints and goals.

**Inputs:**
- goal (string): Goal or problem statement (e.g., "Handle 1M concurrent users with 99.9% uptime")
- constraints (string, optional): Budget, timeline, team size ("3 engineers, 2 months, $50K")
- options (string, optional): Specific options to evaluate (comma-separated)

**Outputs:**
- tradeoff-analysis.md (markdown): 3 options with detailed comparison
- recommendation.md (markdown): Ranked recommendation with rationale
- comparison-table.csv (CSV): Side-by-side comparison (effort, complexity, cost, scalability, risk)
- decision-log.json (JSON): Assumptions, constraints, decision rationale

**Guardrails:**
- All 3 options are viable (not straw men)
- Comparison is on objective criteria (effort hours, cost $, scalability limit)
- Recommendation is pragmatic (not just technically best)
- Tradeoffs are explicit ("fast + cheap" → sacrifice quality)
- Rationale documents why recommendation fits constraints

**Examples:**

#### Example 1: Scaling Architecture Decision
**Execution:**
```bash
orchestrator:tradeoff goal="Support 100K concurrent users with < 200ms p95 latency" 
constraints="3 engineers, 2 months, $10K budget"
```

**Expected Result:**
```
tradeoff-analysis.md

ARCHITECTURE TRADEOFF ANALYSIS
Goal: Support 100K concurrent users, < 200ms p95 latency
Constraints: 3 engineers, 2-month timeline, $10K budget
Decision deadline: 2026-01-20

---

## Option 1: Monolithic + RDS Replicas (Recommended)

### Approach
- Keep single Node.js application
- Add RDS read replicas for scaling reads
- Add Redis for session caching
- Horizontal scale API servers (auto-scaling group)

### Architecture
```
  Load Balancer
    ↓
  API Servers (auto-scale 3-10)
    ↓
  RDS Master + 2 Replicas
  Redis Cache
```

### Effort Estimate
- Setup read replicas: 8 hours
- Add caching layer: 12 hours
- Setup auto-scaling: 8 hours
- Testing + documentation: 12 hours
- Total: 40 hours (1 engineer, 1 week)

### Complexity
- Operational: MEDIUM
  - Read replica failover
  - Cache invalidation
  - Auto-scaling monitoring
- Development: LOW (no code changes for scaling)

### Scalability
- Concurrent users: 100K ✓
- Database limit: 100K-500K (before sharding needed)
- Cost to scale further: Moderate (add shards in 6 months)

### Cost
- AWS Infrastructure:
  - RDS: $3K/month (master + 2 replicas)
  - ElastiCache: $500/month
  - API servers: $2K/month (auto-scaling)
  - Total: $5.5K/month
- Total 2-month cost: $11K (slightly over budget)

### Timeline
- Design: 2 days
- Implementation: 5 days
- Testing: 3 days
- Ready by: Day 10 of sprint ✓

### Risk Assessment
- Single region failure: MEDIUM (no disaster recovery)
  - Mitigation: Backup to different region ($2K extra)
- Unplanned failover complexity: MEDIUM
  - Mitigation: Automated failover (adds operational complexity)

### Team Capability
- 3-person team can operate this ✓
- Requires: 1 DevOps engineer, 2 backend engineers
- Learning curve: 1 week for new team members

### When It Breaks
- > 500K concurrent users: Sharding becomes necessary
- Global expansion: Multi-region needed
- New features: Monolith scalability concerns emerge (tight coupling)

### Pros
✓ Minimal code changes (existing app works)
✓ Fast to implement (1 week)
✓ Cost-effective ($5.5K/month)
✓ Familiar architecture (team knows Node.js monolith)
✓ Easy debugging (monolithic stack trace)

### Cons
✗ Scaling limit at 500K users
✗ Monolith code becomes harder to change at scale
✗ Read/write separation not enforced (code could bypass replicas)
✗ Cache invalidation complexity

---

## Option 2: Microservices (High Complexity)

### Approach
- Extract 3-4 microservices (API Gateway, User Service, Order Service, Product Service)
- Each service has own database (data isolation)
- Async messaging (RabbitMQ or Kafka) for service communication
- Service mesh (Istio) for resilience

### Architecture
```
  API Gateway (Kong)
    ↓
  User Service → User DB
  Order Service → Order DB
  Product Service → Product DB
  ↓
  RabbitMQ (async messaging)
  Consul (service discovery)
  Istio (service mesh)
```

### Effort Estimate
- Service extraction: 80 hours
- API Gateway setup: 16 hours
- Messaging infrastructure: 24 hours
- Service mesh: 16 hours
- Testing: 20 hours
- Total: 156 hours (3 engineers, 5 weeks)

### Complexity
- Operational: VERY HIGH
  - Multi-service deployment
  - Distributed tracing
  - Cross-service debugging difficult
  - Monitoring each service separately
- Development: HIGH
  - Service boundaries unclear initially
  - Async messaging patterns complex
  - Data consistency challenges

### Scalability
- Concurrent users: 500K+
- Database limit: Unlimited (sharding per service)
- Cost to scale further: Relatively low (add service instances)

### Cost
- AWS Infrastructure:
  - ECS/Kubernetes cluster: $5K/month
  - RDS databases (4): $6K/month
  - RabbitMQ: $1K/month
  - Service mesh: $1K/month
  - Total: $13K/month
- Total 2-month cost: $26K (way over budget)

### Timeline
- Design services: 5 days
- Implementation: 25 days
- Testing: 5 days
- Ready by: Day 35 (missed 2-month deadline)

### Risk Assessment
- Distributed tracing failures: HIGH (hard to debug)
  - Mitigation: Invest in APM tools ($3K/month)
- Service dependency hell: MEDIUM
  - Mitigation: Contract testing
- Database consistency issues: MEDIUM
  - Mitigation: Saga pattern for transactions

### Team Capability
- 3-person team is UNDERSTAFFED ✗
  - Requires: 1 architect, 2-3 platform engineers, 2-3 service engineers
  - Your team: 3 engineers total
  - Gap: 3-5 additional engineers
  
### When It Breaks
- Team size < 10: Operational overhead exceeds benefits
- Short timeline < 3 months: Complexity prevents shipping
- New engineers: Takes 2 weeks to onboard (vs. 1 day for monolith)

### Pros
✓ Unlimited scalability
✓ Independent service scaling
✓ Technology polyglot (each service chooses language)
✓ Team autonomy (each team owns service)

### Cons
✗ Way over budget ($26K vs. $10K)
✗ Way over timeline (5 weeks vs. 2 months available... actually fits timeline but risky)
✗ Operational complexity requires experienced team
✗ Debugging distributed system is painful
✗ Data consistency is hard (CAP theorem)

---

## Option 3: Modular Monolith (Safe Middle Ground)

### Approach
- Keep monolithic deployment
- Enforce module boundaries (e.g., User module, Order module, Product module)
- Internal module API (strong contracts)
- Database per feature (logical, not separate instances)
- Async messaging (RabbitMQ) for cross-module communication

### Architecture
```
  Monolithic App
  ├─ User Module (internal API)
  ├─ Order Module (internal API)
  ├─ Product Module (internal API)
  └─ Notification Module
  ↓
  Single Database (logical schemas per module)
  RabbitMQ (async events between modules)
  Redis Cache
```

### Effort Estimate
- Module boundary definition: 16 hours
- Enforce module contracts: 12 hours
- Add async messaging: 16 hours
- Setup caching: 8 hours
- Testing: 12 hours
- Total: 64 hours (1.5 engineers, 2 weeks)

### Complexity
- Operational: LOW-MEDIUM
  - Single deployment pipeline
  - Module independence + database isolation (logical)
  - Debugging within monolith (familiar)
- Development: LOW
  - Module boundaries enforce separation
  - No microservices complexity
  - Future migration to microservices easier

### Scalability
- Concurrent users: 100K-200K (better than pure monolith)
- Database limit: 100K users (with caching)
- Cost to scale further: Moderate (extract high-traffic module as microservice later)

### Cost
- AWS Infrastructure:
  - RDS: $2K/month (master + 1 replica)
  - ElastiCache: $500/month
  - API servers: $2K/month
  - RabbitMQ: $300/month
  - Total: $4.8K/month
- Total 2-month cost: $9.6K (within budget!)

### Timeline
- Design modules: 2 days
- Implementation: 10 days
- Testing: 3 days
- Ready by: Day 15 ✓

### Risk Assessment
- Monolith still single point of failure: MEDIUM (same as Option 1)
  - Mitigation: Add replicas (same cost)
- Module boundaries drift over time: MEDIUM (human discipline)
  - Mitigation: Linting rules to enforce boundaries
- Microservice migration later: COMPLEX
  - Mitigation: Design modules as future services

### Team Capability
- 3-person team can operate this ✓
- Requires: 1 DevOps engineer, 2 backend engineers
- Learning curve: 1 week (intermediate between monolith and microservices)

### When It Breaks
- Team growth to 10+ engineers: Monolith scalability concerns emerge
- Geographic expansion: Multi-region needed
- Module boundaries violate across org: Extract as microservice

### Pros
✓ Good balance (scalable but simple)
✓ Within budget ($9.6K vs. $10K)
✓ On timeline (ready day 15)
✓ Future-proof (modules → microservices migration path clear)
✓ Easy debugging (single process)
✓ Can grow from here (minimal rework)

### Cons
✗ Monolith scalability limits (< 200K concurrent users)
✗ Still require database replication
✗ Async messaging adds complexity

---

## Comparison Table

| Criterion | Option 1: Monolithic | Option 2: Microservices | Option 3: Modular Mono |
|-----------|----------------------|------------------------|----------------------|
| **Effort** | 40 hours | 156 hours | 64 hours |
| **Timeline** | 10 days ✓ | 35 days ✗ | 15 days ✓ |
| **Cost** | $11K ✗ | $26K ✗ | $9.6K ✓ |
| **Scalability** | 100K users | 500K+ users | 100K-200K users |
| **Operational Complexity** | MEDIUM | VERY HIGH | LOW-MEDIUM |
| **Team Capability Match** | Good | Understaffed | Good |
| **Debugging** | Easy | Hard | Easy |
| **Code changes required** | Minimal | Extensive | Moderate |
| **Future evolution** | Limited | Maximum | Moderate |

---

## RECOMMENDATION: Option 3 (Modular Monolith)

### Rationale

✓ **Meets all constraints:**
  - Within timeline (ready day 15)
  - Within budget ($9.6K)
  - Team capability fit (3 engineers can operate)

✓ **Best pragmatic choice:**
  - Solves immediate scaling goal (100K users)
  - Avoids premature microservices complexity
  - Preserves team velocity (familiar monolith structure)
  - Provides upgrade path to microservices when growth justifies

✓ **Risk-balanced:**
  - Operational risk: MEDIUM (comparable to Option 1)
  - Technical risk: LOW (proven modular monolith pattern)
  - Timeline risk: LOW (only 15 days, buffer available)
  - Cost risk: LOW (under budget with buffer)

### Implementation Plan

Phase 1: Design Module Boundaries (Week 1)
├─ Define User, Order, Product, Notification modules
├─ Document internal APIs
├─ Identify cross-module dependencies
└─ Design RabbitMQ event contracts

Phase 2: Enforce Module Boundaries (Week 2)
├─ Add linting rules (no cross-module imports except API)
├─ Add async messaging (RabbitMQ)
├─ Add caching layer (Redis)
└─ Performance testing

Phase 3: Deployment (Week 3)
├─ Setup load balancer + auto-scaling
├─ Setup read replicas
├─ Monitoring + alerting
└─ Go-live

### When to Reconsider

Option 3 works until:
- Team grows to 10+ engineers (multiple teams needed)
- Concurrent user target grows to > 500K (sharding complex with monolith)
- Feature requirements diverge (different tech stacks per feature)

At that point, migrate high-traffic module (e.g., Product Service) to microservice without rewriting entire system.

### Sign-Off

Recommended: Proceed with Option 3 (Modular Monolith)
Rationale: Best fit for constraints (timeline, budget, team)
Risk: MEDIUM (manageable with good ops)
Timeline: Ready by Day 15
Cost: $9.6K (under $10K budget)

Decision approved by: Orchestrator
Date: 2026-01-10
```

---

**Error Handling:**
- **Goal too vague:** If goal is unclear ("make it faster"), ask for specifics (target latency, user count)
- **Impossible constraints:** If constraints conflict ("1-week timeline + enterprise architecture"), surface explicitly
- **Missing baseline:** If current performance unknown, recommend benchmark first
- **No context:** If unfamiliar with domain, flag assumptions

**Edge Cases:**
- **More than 3 options:** Function suggests 3 most viable, mentions others as alternatives
- **Constrained to one approach:** If only one viable option, function says so (transparency)
- **Cost unknown:** Function provides estimates with confidence ranges and assumptions
- **Team factors matter most:** Function weighs team capability heavily in recommendation

**Testing Approach:**
- **Unit test:** Verify each option is analyzed on all criteria
- **Validation:** Share tradeoff with technical decision-maker, gather feedback
- **Post-decision:** Track actual effort vs. estimate, use data to refine tradeoff analysis

---

### orchestrator:risk

**Purpose:** Risk assessment with failure modes and mitigation strategies. Identifies critical risks before launch, prioritizes by impact and probability. Provides quantified risk (e.g., "10% chance of complete outage, impact $50K/hour").

**Inputs:**
- path (string): Path to architecture/system design
- goal (string, optional): Launch/deployment goal
- timeline (string, optional): Time to launch ("2 weeks", "3 months")

**Outputs:**
- risk-assessment.md (markdown): Risk matrix (CRITICAL/HIGH/MEDIUM/LOW) with:
  - Risk name + description
  - Impact (business or technical)
  - Probability (likelihood)
  - Detection strategy (how to find if happening)
  - Mitigation strategy (how to prevent or respond)
  - Effort to mitigate (hours)
  - Timeline (when to fix)
- risk-matrix.csv (CSV): Exportable risk matrix (name, impact, probability, effort)
- incident-response.md (markdown): Runbook for critical risks (escalation, communication)

**Guardrails:**
- Risks are specific, not generic ("database could fail" is too vague; "single RDS instance with no replicas fails → 4-hour RTO" is specific)
- Mitigations are actionable (concrete steps, effort estimates)
- Critical risks MUST be mitigated before launch
- Timeline is realistic (not "fix everything in 1 hour")
- Impact is quantified (revenue loss, user impact, data loss)

**Examples:**

#### Example 1: E-Commerce Launch Risk Assessment
**Execution:**
```bash
orchestrator:risk path=./ecommerce-architecture goal="Launch production MVP" timeline="2 weeks"
```

**Expected Result:**
```
risk-assessment.md

RISK ASSESSMENT — E-Commerce Platform MVP Launch
Goal: Production launch
Timeline: 2 weeks to launch (10 business days)
Assessment date: 2026-01-10

---

## Risk Matrix Summary

🔴 CRITICAL (5 risks — Must fix before launch)
├─ Single database instance (SPOF)
├─ No payment reconciliation
├─ No rate limiting
├─ API missing authentication on search endpoint
└─ Missing backup/restore procedure

🟡 HIGH (8 risks — Fix within 1 week of launch)
├─ No caching strategy
├─ Synchronous payment processing
├─ Search reindex not automated
├─ Webhook timeout handling
├─ No circuit breaker for Stripe failures
└─ Insufficient error handling in checkout flow
└─ No email delivery retry logic
└─ Admin dashboard lacks input validation

🟢 MEDIUM (5 risks — Fix in v1.1 or post-launch)
├─ No wishlist feature (feature gap)
├─ Limited inventory forecasting
├─ No A/B testing framework
├─ No recommendation engine
└─ Mobile app not native (web-only)

🟡 LOW (3 risks — Nice to address eventually)
├─ No dark mode UI
├─ No internationalization (i18n)
└─ Performance not optimized for slow networks

---

## Detailed Risk Analysis

### 🔴 CRITICAL RISKS

#### Risk 1: Single Database Instance (SPOF)

**Description:** PostgreSQL runs on single RDS instance. No replicas, no automated failover.

**Impact:**
- Business: Complete service outage → $50K/hour revenue loss
- Technical: Data loss risk (no failover), customer data inaccessible
- Duration: 30min-4hrs (RTO), potential permanent data loss

**Probability:** 2-3% annually
- RDS has 99.95% SLA (4.4 hours downtime/year)
- Unplanned failure: 1-2 times per year
- Planned maintenance: 1 time per year

**Detection Strategy:**
- Health checks: Every 10 seconds
- CloudWatch: Monitor RDS CPU, connections
- Alerting: PagerDuty notification within 1 minute

**Current State:** ✗ NOT MITIGATED
- No read replicas
- No automated failover
- No backup tested

**Mitigation Strategy:**

Option A: RDS Multi-AZ (Automated Failover) — Recommended
1. Enable Multi-AZ in RDS (5 minutes, zero downtime)
2. Failover takes 1-2 minutes (transparent to app)
3. Automated: No manual intervention needed
4. Cost: +50% RDS cost ($1.5K → $2.25K/month)
5. Effort: 1 hour (setup + testing)
6. Result: RTO 2 minutes, RPO < 1 minute ✓

Option B: RDS Read Replicas + Manual Failover
1. Create 2 read replicas in different AZs
2. On failure, promote replica to master (manual, 5-10 minutes)
3. Cost: +100% RDS cost ($1.5K → $3K/month)
4. Effort: 4 hours (setup + failover testing)
5. Result: RTO 10 minutes, RPO < 1 minute ✓
6. Bonus: Read replicas help with query performance

**Recommendation:** Option A (Multi-AZ)
- Simpler (automated, no manual intervention)
- Cost-effective ($750/month vs. $1.5K)
- Sufficient for MVP

**Effort:** 1 hour setup + 1 hour testing = 2 hours
**Timeline:** Must complete before launch (can do day 1)
**Status:** NOT STARTED — BLOCKING LAUNCH

---

#### Risk 2: No Payment Reconciliation

**Description:** Orders and payment statuses can diverge. If Stripe webhook fails, order status becomes inconsistent.

**Scenario:**
1. User clicks checkout
2. Order created in DB (status='pending_payment')
3. API calls Stripe to process payment
4. Stripe charges successfully but webhook times out
5. Order status never updates to 'paid'
6. User sees "Payment failed", doesn't know if charged
7. Support team confused

**Impact:**
- Business: Confused customers, support overhead, potential chargebacks
- Data: Inconsistent state (order paid but status says pending)
- Revenue: Orders appear as failed when they succeeded

**Probability:** 5-10% of orders (Stripe webhook timeouts, network errors)
- Stripe webhook timeout: 2-5% of webhooks fail
- Network failures: 1-2% of API calls
- Combined: 3-7% of orders at risk

**Current State:** ✗ NOT MITIGATED
- Webhook receives payment confirmation
- But no idempotency key → duplicates possible
- No reconciliation job
- No alerts if mismatch detected

**Mitigation Strategy:**

1. Idempotent Webhook Handler (MUST DO)
   - Add idempotency key to webhook (UUID or Stripe event ID)
   - Check if event already processed (in DB)
   - Skip if already processed
   - Cost: 2 hours (add DB column + check)
   - Result: Duplicate webhooks safely ignored ✓

2. Payment Reconciliation Job (MUST DO)
   - Daily: Query Stripe for all payments, compare with DB
   - Find mismatches (paid in Stripe, pending in DB)
   - Update order status automatically
   - Alert on large discrepancies
   - Cost: 4 hours (write job + test)
   - Run: Daily at 2am UTC
   - Result: Catch 99% of mismatches ✓

3. Webhook Retry Logic (SHOULD DO)
   - If webhook processing fails, queue for retry
   - Retry exponentially (1min, 5min, 30min, 2hrs, 6hrs, 24hrs)
   - Cost: 3 hours
   - Result: Reduce failure rate from 5% → 0.1%

4. Order Status Monitoring (SHOULD DO)
   - Alert if order stuck in 'pending_payment' > 1 hour
   - Manual review queue for support team
   - Cost: 1 hour
   - Result: Quick issue detection

**Recommendation:**
- MUST: Steps 1 + 2 (idempotency + reconciliation)
- SHOULD: Steps 3 + 4 (retry + monitoring)

**Effort:** 2 + 4 + 3 + 1 = 10 hours total
- Minimum (1 + 2): 6 hours (blocking)
- Full solution: 10 hours

**Timeline:** Must complete before launch (blocks order processing)

**Status:** NOT STARTED — BLOCKING LAUNCH

---

#### Risk 3: No Rate Limiting

**Description:** API has no rate limiting. Vulnerable to DDoS, bot scraping, and brute-force attacks.

**Scenarios:**
1. Attacker: Script to scrape all product listings (100K products)
   - Impact: Consumes database bandwidth, slows API for real users
   - Probability: MEDIUM (product scraping is common)
   - Damage: Revenue loss from slower page loads

2. Attacker: Brute-force password guessing (1K attempts/sec)
   - Impact: Account takeover
   - Probability: MEDIUM
   - Damage: Customer data breach

3. Attacker: DDoS attack (10K req/sec)
   - Impact: API server CPU maxes out, 500 errors
   - Probability: LOW (targeted attacks)
   - Damage: Revenue loss, customer frustration

**Current State:** ✗ NOT MITIGATED
- No rate limiting middleware
- No IP blocking
- No bot detection

**Mitigation Strategy:**

1. Add Rate Limiting Middleware (MUST DO)
   - Limit: 1000 requests/hour per IP
   - Limit: 100 requests/hour per user (authenticated)
   - Implement: Redis-backed sliding window counter
   - Cost: 2 hours
   - Result: Scraping bots + DDoS attacks blocked
   
2. Add Authentication to Expensive Endpoints (MUST DO)
   - Endpoints: /search, /products, /recommendations
   - Current: No auth required (public)
   - Propose: Auth optional, rate limits much higher for authenticated users
   - Cost: 1 hour
   - Result: Legitimate users get higher limits

3. CloudFlare DDoS Protection (SHOULD DO)
   - CloudFlare sits in front of API
   - Blocks DDoS at edge, not in AWS
   - Cost: $20/month
   - Setup: 30 minutes
   - Result: DDoS fully mitigated

4. Bot Detection (NICE TO HAVE)
   - Detect suspicious patterns (rapid requests, User-Agent, etc.)
   - Block or CAPTCHA challenge
   - Cost: 4 hours
   - Later: Use third-party service (hCaptcha, reCAPTCHA)

**Recommendation:**
- MUST: Steps 1 + 2 (rate limiting + auth)
- SHOULD: Step 3 (CloudFlare)
- NICE: Step 4 (bot detection)

**Effort:**
- Minimum (1 + 2): 3 hours
- With CloudFlare: 3.5 hours
- Full: 7.5 hours

**Timeline:** Must complete before launch (security-critical)

**Status:** NOT STARTED — BLOCKING LAUNCH

---

#### Risk 4: API Missing Authentication on Search Endpoint

**Description:** `/api/v1/search` endpoint has no authentication. Exposes internal product IDs and prices.

**Impact:**
- Competitors can scrape product catalog (uncompetitive)
- Price information leaked
- Inventory levels revealed

**Probability:** 100% (if deployed as-is, will be scraped)

**Mitigation:**
1. Add optional authentication (allow public searches but limit rate)
2. Rate limit public searches: 100 searches/hour
3. Estimated effort: 1 hour

**Timeline:** Must fix before launch

**Status:** NOT STARTED — BLOCKING LAUNCH

---

#### Risk 5: Missing Backup/Restore Procedure

**Description:** No documented backup strategy. If data loss occurs, no recovery plan.

**Impact:**
- Data loss → complete business failure
- Customer data + orders lost
- No audit trail for chargebacks/disputes

**Probability:** 1-5% annually (user errors, bugs, ransomware)

**Mitigation:**
1. Enable RDS automated backups (AWS default, already done)
2. Test restore to different RDS instance (2 hours)
3. Document RTO/RPO targets
4. Restore test schedule: Monthly
5. Effort: 3 hours (initial) + 1 hour/month (testing)

**Timeline:** Must complete before launch

**Status:** PARTIALLY DONE (AWS default backups on, no testing done)

---

### 🟡 HIGH RISKS

[Detailed analysis of 8 high-impact risks with similar structure]

Risk 6: No Caching Strategy
├─ Impact: Slow product search at 50K+ items
├─ Mitigation: Add Redis cache with 24hr TTL
└─ Effort: 8 hours, Timeline: Week 1 after launch

Risk 7: Synchronous Payment Processing
├─ Impact: Failed Stripe calls block checkout
├─ Mitigation: Queue-based async processing
└─ Effort: 12 hours, Timeline: Week 1 after launch

[... 6 more high risks ...]

---

### 🟢 MEDIUM RISKS

[5 medium-priority risks that can wait post-launch]

---

# IMPLEMENTER AGENT (7 functions)

**Role:** Implementation & Execution — Write code, generate tests, auto-document, deploy

**Functions:** build, test, doc, pipeline, docker, iac, full (7 total)

---

## implementer:build

**Purpose:** Generate production-ready code from architecture specifications. Auto-detects tech stack and applies appropriate code generation patterns, security practices, and error handling.

**Inputs:**
- path (string): Path to architecture/requirements file
- context (string, optional): Additional context or constraints
- language (string, optional): Target language (auto-detected if not specified)

**Outputs:**
- Source code (complete models, routes, services, utilities)
- Dependency file (requirements.txt, package.json, pom.xml, etc.)
- Configuration files (.env.example, config.yaml, etc.)
- All files include docstrings/comments and type hints

**Guardrails:**
- Code is production-ready immediately (no scaffolding or stubs)
- All code includes error handling and input validation
- Security best practices applied (no hardcoded secrets, parameterized queries)
- Code follows language/framework conventions (PEP 8, Rust idioms, etc.)
- All functions have docstrings explaining purpose, parameters, returns

**Examples:**

#### Example 1: FastAPI User Service
**Context:** Need to implement user authentication endpoints.

**Execution:**
```bash
implementer:build path=./auth-requirements.md language=python
```

**Expected Result:**
Production-ready models + routes + services:
```python
# models/user.py - Complete User model with validation
# routes/auth.py - Register, login, refresh endpoints with error handling
# services/user_service.py - Business logic with proper exception handling
# security.py - Hashing, token generation, validation functions
# requirements.txt - All dependencies listed

Features:
✓ Password hashing (bcrypt)
✓ JWT token management
✓ Input validation (Pydantic)
✓ Error responses (consistent format)
✓ Logging at appropriate levels
✓ No hardcoded secrets
✓ Docstrings on all functions
✓ Type hints throughout
```

**Timeline:** 30-60 minutes

---

#### Example 2: React Component Suite
**Context:** Build product listing and shopping cart components.

**Execution:**
```bash
implementer:build path=./ui-requirements.md language=typescript
```

**Expected Result:**
Complete React components with:
- TypeScript interfaces for all props
- Hooks for state management
- Error boundaries
- Loading + error states
- Accessibility attributes
- Responsive styling
- Comments explaining complex logic

---

**Error Handling:**
- **Missing architecture:** If no design provided, ask for architecture or spec
- **Ambiguous requirements:** If tech stack unclear, ask for explicit choice
- **Conflicting patterns:** If architecture contradicts implementation, clarify before generating
- **Deprecated dependencies:** If outdated versions detected, use latest stable versions

**Edge Cases:**
- **Multiple languages:** If monorepo with mixed languages, generate appropriate code for each
- **Legacy codebase:** If integrating with existing code, generates compatible code
- **Async/sync choice:** Detects from architecture whether to use async or sync patterns
- **Database dialect:** Detects SQL dialect and generates dialect-specific code

**Testing Approach:**
- **Unit test:** Verify generated code is syntactically correct, imports work
- **Validation:** Run linting (pylint, eslint), type checking (mypy, TypeScript compiler)
- **Integration:** Ensure generated code works with specified dependencies

---

## implementer:test

**Purpose:** Generate comprehensive test suite covering unit, integration, and edge cases. Targets 95%+ code coverage with business-level validation and meaningful test names.

**Inputs:**
- path (string): Path to source code to test
- coverage_target (integer, optional): Coverage percentage target (default: 95)
- framework (string, optional): Test framework (auto-detected if not specified)

**Outputs:**
- Test suite files (tests/test_*.py, *.test.ts, etc.)
- Coverage report (HTML + summary)
- Fixture definitions for setup/teardown
- Mock objects for external dependencies

**Guardrails:**
- All tests follow AAA pattern (Arrange-Act-Assert)
- Test names are descriptive (givenXxx_whenYyy_thenZzz pattern)
- Coverage targets unit + integration + edge cases
- Tests are independent (no shared state between tests)
- All assertions are single-purpose (not mega-asserts)

**Examples:**

#### Example 1: User Service Tests
**Context:** Generate 95%+ coverage tests for user authentication service.

**Execution:**
```bash
implementer:test path=./src/services/user_service.py coverage_target=95
```

**Expected Result:**
```python
# tests/test_user_service.py with test classes:
# TestUserCreation
#   - test_create_user_success
#   - test_create_duplicate_email_rejected
#   - test_weak_password_rejected
#   - test_missing_email_rejected
#
# TestUserAuthentication
#   - test_login_with_correct_password
#   - test_login_fails_with_wrong_password
#   - test_login_account_locked_after_5_attempts
#   - test_concurrent_logins_allowed
#
# TestPasswordReset
#   - test_reset_token_generation
#   - test_reset_token_expiration
#   - test_reset_with_invalid_token_rejected
#
# TestEdgeCases
#   - test_null_password_handling
#   - test_unicode_email_handling
#   - test_sql_injection_attempt_blocked
#   - test_race_condition_concurrent_registration

Results:
✓ 87 tests passing
✓ Coverage: 96.2% (above 95% target)
✓ All acceptance criteria validated
```

**Timeline:** 30-45 minutes

---

#### Example 2: React Component Tests
**Context:** Test shopping cart component (state, interactions, accessibility).

**Execution:**
```bash
implementer:test path=./src/components/Cart.tsx framework=vitest
```

**Expected Result:**
- Unit tests (component props, callbacks)
- Integration tests (user interactions, state updates)
- Accessibility tests (axe-core checks)
- Edge cases (empty cart, max items, out of stock)
- Coverage: 92% (near 95% target)

---

**Error Handling:**
- **Untestable code:** If code has hard dependencies, suggest refactoring with dependency injection
- **Missing mocks:** If external services not mockable, flag and provide mock implementations
- **Flaky tests:** If tests are time-dependent, add retry logic and proper waits

**Edge Cases:**
- **Async code:** Handles async/await, callbacks, promises with proper wait strategies
- **Database tests:** Uses test databases or in-memory alternatives
- **External APIs:** Mocks with realistic responses and error scenarios

**Testing Approach:**
- **Unit test:** Verify all tests pass locally and in CI
- **Coverage validation:** Ensure coverage report accurate, gaps identified
- **Manual review:** Spot-check critical paths for realistic assertions

---

## implementer:doc

**Purpose:** Generate comprehensive documentation including inline code comments, API reference, architecture guides, and deployment instructions.

**Inputs:**
- path (string): Path to source code
- format (string, optional): Output format (markdown, HTML, both)
- include (string, optional): What to generate (api, guides, architecture, all)

**Outputs:**
- README.md (project overview, setup, quick start)
- API.md (all endpoints, request/response examples)
- ARCHITECTURE.md (system design, C4 diagrams, data flows)
- SETUP.md (development environment setup)
- DEPLOYMENT.md (production deployment checklist)
- Inline docstrings in all source files
- HTML site (optional, searchable documentation)

**Guardrails:**
- All public functions/classes have docstrings
- Documentation is accurate and current (reflects actual code)
- Examples are executable and tested
- Deployment guide is complete and safe
- Troubleshooting section covers common issues

**Examples:**

#### Example 1: Full Documentation Suite
**Execution:**
```bash
implementer:doc path=./src format=markdown include=all
```

**Expected Result:**
```
docs/
├─ README.md
│  ├─ Project overview
│  ├─ Prerequisites
│  ├─ Installation & setup
│  ├─ Running locally
│  └─ First run checklist
├─ API.md
│  ├─ All endpoints (GET /users, POST /orders, etc.)
│  ├─ Request/response schemas
│  ├─ Authentication requirements
│  ├─ Error codes & messages
│  └─ cURL examples for each endpoint
├─ ARCHITECTURE.md
│  ├─ System context diagram (C4 Level 1)
│  ├─ Container diagram (C4 Level 2)
│  ├─ Component diagram for each service
│  ├─ Data flow diagrams
│  └─ Technology choices rationale
├─ SETUP.md
│  ├─ MacOS/Linux/Windows instructions
│  ├─ IDE setup (VS Code, PyCharm, etc.)
│  ├─ Database setup
│  └─ Running tests & linting
├─ DEPLOYMENT.md
│  ├─ Pre-deployment checklist
│  ├─ Deployment steps
│  ├─ Health check verification
│  ├─ Rollback procedure
│  └─ Post-deployment validation
└─ Code docstrings
   └─ All functions, classes have docstrings
```

**Timeline:** 20-30 minutes

---

#### Example 2: API Documentation Generation
**Execution:**
```bash
implementer:doc path=./src format=html include=api
```

**Expected Result:**
- Interactive HTML API documentation
- Endpoint list with filters
- Try-it-out feature (make test requests)
- Schema definitions with examples
- Authentication guide

---

**Error Handling:**
- **Missing docstrings:** Function adds docstrings to undocumented code
- **Outdated examples:** If examples don't match code, asks for clarification
- **Incomplete architecture:** If system design not documented, infers from code

**Edge Cases:**
- **Private vs. public:** Only documents public APIs (respects visibility modifiers)
- **Internal vs. external:** Separate guides for internal use vs. customer documentation
- **Multiple versions:** Generates docs for current version, notes breaking changes from prior

**Testing Approach:**
- **Link validation:** Verify all links in docs work
- **Example execution:** Run all code examples to ensure they work
- **Readability:** Share with team member unfamiliar with code, verify comprehension

---

## implementer:pipeline

**Purpose:** Generate CI/CD pipeline configuration for automated testing, building, and deployment. Supports GitHub Actions, GitLab CI, Jenkins, CircleCI, Azure Pipelines.

**Inputs:**
- path (string): Project root
- platform (string): CI/CD platform (github-actions, gitlab-ci, jenkins, circleci, azure)
- stages (string, optional): Pipeline stages to include (test, lint, build, deploy)

**Outputs:**
- Platform-specific pipeline file (.github/workflows/*.yml, .gitlab-ci.yml, Jenkinsfile, etc.)
- Environment configuration
- Secrets setup guide
- Deployment configuration

**Guardrails:**
- Pipeline is fully functional (not a template)
- All secrets are environment variables (not hardcoded)
- Tests run before build (fail fast)
- Build succeeds only if tests + linting pass
- Deployment is manual or gated (not automatic)

**Examples:**

#### Example 1: GitHub Actions Pipeline
**Execution:**
```bash
implementer:pipeline path=./ platform=github-actions stages=test,lint,build,deploy
```

**Expected Result:**
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Lint (flake8)
        run: flake8 src/ --count --select=E9,F63,F7,F82
      - name: Type check (mypy)
        run: mypy src/ --strict
      - name: Run tests
        run: pytest --cov=src/ --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .
      - name: Push to registry
        run: docker push myapp:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          aws ecs update-service --cluster prod --service myapp --force-new-deployment
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

Features:
✓ Test on every push
✓ Linting enforced
✓ Coverage reporting
✓ Docker build on main
✓ Auto-deploy on main merge (with manual approval option)
✓ Secrets managed via GitHub Secrets
✓ Status badges available

**Timeline:** 15-20 minutes

---

#### Example 2: GitLab CI Pipeline
**Execution:**
```bash
implementer:pipeline path=./ platform=gitlab-ci
```

**Expected Result:**
```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pytest --cov=src/ --cov-report=term
  coverage: '/TOTAL.*\s(\d+)%/'

lint:
  stage: test
  image: python:3.11
  script:
    - flake8 src/

build:
  stage: build
  image: docker:latest
  script:
    - docker build -t myapp:$CI_COMMIT_SHA .
    - docker push myapp:$CI_COMMIT_SHA
  only:
    - main

deploy:
  stage: deploy
  script:
    - aws ecs update-service --cluster prod --service myapp --force-new-deployment
  only:
    - main
  when: manual
```

---

**Error Handling:**
- **Unknown platform:** If unsupported CI/CD platform, ask for alternative
- **Missing secrets:** If secrets not configured, provides setup guide
- **Deployment credentials:** Guides secure credential management

**Edge Cases:**
- **Multiple environments:** Generates separate pipelines for dev/staging/production
- **Approval gates:** Includes manual approval step for production deployments
- **Notification:** Integrates with Slack/email for build status

**Testing Approach:**
- **Dry run:** Test pipeline locally before pushing
- **Failure scenarios:** Test rollback and failure notifications
- **Integration:** Verify pipeline works with actual repository

---

## implementer:docker

**Purpose:** Generate Dockerfile and docker-compose configuration for containerization. Creates multi-stage builds for small images, includes health checks, security best practices.

**Inputs:**
- path (string): Project root
- language (string, optional): Programming language (auto-detected if not specified)
- registry (string, optional): Docker registry (Docker Hub, ECR, GCR, etc.)

**Outputs:**
- Dockerfile (production image)
- docker-compose.yml (local development with services)
- .dockerignore (exclude unnecessary files)
- Registry configuration

**Guardrails:**
- Images are small (multi-stage builds, no build artifacts in final image)
- Health checks configured (prevent zombie containers)
- Security: Non-root user, minimal base image, no secrets in image
- Local development: docker-compose includes all dependencies (database, cache, etc.)

**Examples:**

#### Example 1: Python FastAPI Application
**Execution:**
```bash
implementer:docker path=./ language=python
```

**Expected Result:**
```dockerfile
# Dockerfile (multi-stage build)
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app
RUN useradd -m appuser

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY src/ ./src/
COPY config/ ./config/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000

USER appuser

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Features:
✓ Multi-stage build (final image ~200MB vs ~800MB with full Python)
✓ Non-root user (security)
✓ Health check configured
✓ Minimal base image
✓ No secrets in image

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@db:5432/app
      REDIS_URL: redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    networks:
      - app-network

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  cache:
    image: redis:7
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
```

**Timeline:** 10-15 minutes

---

#### Example 2: Node.js React Application
**Execution:**
```bash
implementer:docker path=./ language=node
```

**Expected Result:**
- Multi-stage Dockerfile (build deps + runtime)
- docker-compose with API + frontend + database
- Nginx configuration for serving React static files
- Environment variable substitution for frontend

---

**Error Handling:**
- **Unknown language:** If auto-detection fails, ask for explicit language
- **Registry auth:** If pushing to private registry, guides credential setup
- **Port conflicts:** If standard ports in use, suggests alternative ports

**Edge Cases:**
- **Multiple services:** If monorepo with multiple apps, generates separate Dockerfiles
- **GPU requirements:** If needed (ML workloads), configures GPU support
- **Kubernetes deployment:** Generates K8s-compatible Dockerfile (no docker-compose entrypoint issues)

**Testing Approach:**
- **Build test:** Run `docker build`, verify no errors
- **Container test:** Run container, verify health check passes
- **Compose test:** Run `docker-compose up`, verify all services start

---

## implementer:iac

**Purpose:** Generate Infrastructure as Code for Terraform, CloudFormation, or Kubernetes manifests. Creates reproducible, version-controlled infrastructure deployments.

**Inputs:**
- path (string): Project root (infers infrastructure needs from code)
- provider (string): Cloud provider (aws, gcp, azure, kubernetes)
- tool (string, optional): IaC tool (terraform, cloudformation, k8s)

**Outputs:**
- IaC files (Terraform modules, CloudFormation templates, K8s manifests)
- Environment configuration
- Deployment guide
- Scaling policies

**Guardrails:**
- Infrastructure is production-ready (high availability, auto-scaling configured)
- Security is enforced (VPC, security groups, IAM roles configured)
- Backups and disaster recovery configured
- Cost is estimated
- Version control friendly (human-readable, well-commented)

**Examples:**

#### Example 1: Kubernetes Deployment
**Execution:**
```bash
implementer:iac path=./ provider=kubernetes tool=k8s
```

**Expected Result:**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
    spec:
      containers:
      - name: api
        image: myregistry/myapp:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: cache-secret
              key: url
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          failureThreshold: 2
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true

---
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
  namespace: production
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
  namespace: production
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: myapp
```

Features:
✓ 3 replicas (high availability)
✓ Rolling updates (zero downtime)
✓ Resource requests/limits (proper resource allocation)
✓ Health checks (liveness + readiness)
✓ Auto-scaling (based on CPU/memory)
✓ Security context (non-root, read-only filesystem)
✓ Service for load balancing
✓ Pod Disruption Budget (prevent cascading failures)

**Timeline:** 20-30 minutes

---

#### Example 2: Terraform AWS Infrastructure
**Execution:**
```bash
implementer:iac path=./ provider=aws tool=terraform
```

**Expected Result:**
```hcl
# terraform/main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# RDS Database
resource "aws_rds_cluster" "main" {
  cluster_identifier      = "myapp-db"
  engine                  = "aurora-postgresql"
  engine_version          = "15.2"
  database_name           = "myapp"
  master_username         = "admin"
  master_password         = random_password.db_password.result
  
  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  
  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  skip_final_snapshot = false
  final_snapshot_identifier = "myapp-db-final-snapshot"
}

# RDS Cluster Instances (Multi-AZ)
resource "aws_rds_cluster_instance" "main" {
  count              = 2
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = "db.t3.medium"
  engine              = aws_rds_cluster.main.engine
  engine_version      = aws_rds_cluster.main.engine_version
  
  publicly_accessible = false
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "myapp-cluster"
}

# ECS Service
resource "aws_ecs_service" "main" {
  name            = "myapp-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = 3
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.main.arn
    container_name   = "api"
    container_port   = 8000
  }
}

# Auto Scaling
resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = 10
  min_capacity       = 3
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.main.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs_policy_cpu" {
  policy_name        = "cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

# Output
output "database_endpoint" {
  value = aws_rds_cluster.main.endpoint
}

output "load_balancer_dns" {
  value = aws_lb.main.dns_name
}
```

Features:
✓ RDS with Multi-AZ (high availability)
✓ ECS for container orchestration
✓ Auto-scaling based on CPU
✓ Load balancer with health checks
✓ Private subnets (security)
✓ VPC and security groups
✓ CloudWatch logging
✓ Terraform modules for reusability

**Timeline:** 20-30 minutes

---

**Error Handling:**
- **Unknown provider:** If unsupported provider, ask for alternative
- **Complex infrastructure:** If many services needed, suggests modular approach
- **Cost concerns:** Provides cost estimation before deploying

**Edge Cases:**
- **Multiple environments:** Generates separate configurations for dev/staging/production
- **Blue-green deployment:** Includes configuration for zero-downtime deployments
- **Disaster recovery:** Configures cross-region replication and failover
- **Migration:** If modernizing existing infrastructure, generates migration plan

**Testing Approach:**
- **Validation:** Run `terraform validate` or `kubectl validate`
- **Plan:** Generate deployment plan, review before applying
- **Dry run:** Test in non-production environment first
- **Cost check:** Estimate costs using `terraform plan -out` or cloud provider tools

---

## implementer:full

**Purpose:** Complete end-to-end implementation lifecycle in single context window. Builds code, generates tests, creates documentation, sets up CI/CD, creates Docker configuration, and generates infrastructure manifests—all without context loss.

**Inputs:**
- path (string): Path to requirements (from orchestrator:plan output)
- tech_stack (string, optional): Preferred tech stack

**Outputs:**
- Complete production-ready system with:
  - Source code (all components)
  - Test suite (95%+ coverage)
  - Documentation (README, API, architecture, deployment)
  - CI/CD pipeline
  - Docker configuration
  - Infrastructure as Code
  - GitHub PR ready for review

**Guardrails:**
- NO context loss between phases (all in single context window)
- Each phase output validates against previous phase
- System is production-ready, not "almost done"
- All requirements from plan are implemented and tested
- No shortcuts (tests, docs, deployment all included)

**Examples:**

#### Example 1: Complete E-Commerce MVP
**Execution:**
```bash
implementer:full path=./requirements.md
```

**Timeline:** 2-3 hours

**What happens:**
```
Phase 1: Code Generation (30 min)
├─ Backend code (models, routes, services)
├─ Frontend code (components, pages, services)
├─ Database schema + migrations
└─ Configuration files

Phase 2: Test Generation (30 min)
├─ Unit tests (95%+ coverage)
├─ Integration tests
├─ Accessibility tests
└─ Coverage report

Phase 3: Documentation (20 min)
├─ README
├─ API documentation
├─ Architecture guide
└─ Deployment instructions

Phase 4: CI/CD Setup (15 min)
├─ GitHub Actions pipeline
├─ Linting + type checking
├─ Automated testing
└─ Deployment configuration

Phase 5: Docker Setup (15 min)
├─ Dockerfile (production)
├─ docker-compose.yml (local dev)
└─ Registry configuration

Phase 6: Infrastructure (20 min)
├─ K8s manifests (deployment, service, HPA)
├─ Terraform modules (if AWS)
└─ Database configuration

Phase 7: PR & Commit (5 min)
├─ All code committed to feature branch
├─ GitHub PR created with summary
└─ Ready for code review
```

**Output:**
```
Complete system with:
├─ ~5K LOC (backend + frontend)
├─ 245+ tests (95% coverage)
├─ Full documentation
├─ Production deployment ready
├─ GitHub PR open + ready to merge
└─ Zero manual work required
```

---

#### Example 2: Data Pipeline Implementation
**Execution:**
```bash
implementer:full path=./data-pipeline-requirements.md tech_stack=python
```

**Output:**
- Python data pipeline code (extraction, transformation, loading)
- Tests (unit + integration)
- Documentation
- CI/CD pipeline
- Docker Compose (with Kafka, Spark, warehouse)
- Kubernetes configuration
- PR ready

---

**Error Handling:**
- **Incomplete requirements:** If requirements.md missing, ask for it
- **Phase failure:** If any phase fails, report specifically and ask for clarification
- **Context concern:** If approaching token limits, checkpoints and summarizes before continuing

**Edge Cases:**
- **Large systems:** If system requires > 3 languages or > 10 services, may split across multiple runs
- **Existing codebase:** If adding to existing system, generates compatible code for integration
- **Multiple environments:** Generates config for dev/staging/production

**Testing Approach:**
- **Verify each phase:** Confirm code compiles, tests pass, docs build, pipelines valid
- **Integration test:** Run entire system locally (docker-compose), verify end-to-end
- **Smoke test:** Verify API responds, frontend loads, database migrations work

---

# QUALITY AGENT (6 functions)

**Role:** QA, Security & Performance — Code review, testing, security audit, performance optimization, debugging

**Functions:** review, audit, security, perf, debug, report (6 total)

---

## quality:review

**Purpose:** Comprehensive PR validation against requirements and quality standards. Reviews code against JIRA acceptance criteria, scores quality across 6 dimensions, generates detailed report with actionable feedback.

**Inputs:**
- pr (integer): Pull request number
- ticket (string): JIRA ticket ID
- context (string, optional): Additional business context

**Outputs:**
- review-report.md (detailed 6-phase analysis)
- HTML report (interactive, embeddable in PR)
- PR comment with summary + required changes

**Guardrails:**
- Review validates against JIRA acceptance criteria (not just code style)
- Scoring is objective and transparent (clear criteria for each score)
- Required changes are blocking (must fix before merge)
- Optional improvements can be post-launch
- Review is constructive, not pedantic

**Examples:**

#### Example 1: OAuth2 Implementation PR Review
**Execution:**
```bash
quality:review pr=456 ticket=AUTH-123
```

**Expected Result:**
```
PULL REQUEST REVIEW
PR #456 | Ticket: AUTH-123

SCORE: 78/100 (GOOD) - Approve with changes

PHASE 1: REQUIREMENT VALIDATION
✓ AC1: Support Google OAuth2 sign-in (SATISFIED)
✓ AC2: Support GitHub OAuth2 sign-in (SATISFIED)
✓ AC3: Store OAuth tokens securely (SATISFIED)
⚠️  AC4: Email verification for new accounts (INCOMPLETE)
❌ AC5: Rate limiting on token endpoint (MISSING)

Requirement Coverage: 80% (4/5 ACs)

PHASE 2: CODE QUALITY
✓ Style compliance: PASS
✓ Error handling: PASS
⚠️  Cyclomatic complexity: 12 (too high, recommend refactor)
⚠️  Code duplication: Token validation duplicated in 2 places

Code Quality Score: 82/100

PHASE 3: TEST COVERAGE
Overall: 89% (exceeds 85% target)
Missing:
- Google token refresh failure (test case needed)
- OAuth user merge conflict (email collision)
- CSRF attack on callback (state parameter validation)

Coverage Score: 75/100

PHASE 4: DOCUMENTATION
✓ Inline comments: GOOD
⚠️  API examples missing
⚠️  OAuth flow diagram missing

Docs Score: 65/100

PHASE 5: SECURITY
🔴 CRITICAL: Missing CSRF protection
🟡 HIGH: Missing token expiration validation
✓ Tokens properly hashed
✓ No hardcoded secrets

Security Score: 85/100

PHASE 6: VERDICT
APPROVE WITH CHANGES

Required (before merge):
1. Add CSRF protection to OAuth callback
2. Add rate limiting to /auth/token endpoint
3. Add 3 missing test cases (Google refresh, email collision, CSRF)
4. Extract duplicated token validation logic

Optional (can defer):
1. Add OAuth flow diagram to docs
2. Reduce cyclomatic complexity in oauth_handler.py
3. Add example requests to API doc

Estimated fix time: 2-3 hours

---

Reviewer: Claude Quality Agent
Date: 2026-01-15
```

**Timeline:** 20-30 minutes

---

**Error Handling:**
- **PR not found:** If PR number invalid, ask for correct number
- **No JIRA ticket:** If ticket not accessible, review against other criteria
- **Incomplete code:** If PR is WIP, note and suggest reopening when ready

**Edge Cases:**
- **Large PR (500+ files):** Note size and suggest splitting into smaller PRs
- **Refactoring PR:** Adjust criteria to focus on code organization vs. new features
- **Security-critical:** Add additional security checks

**Testing Approach:**
- **Automated checks:** Run linting, type checking, tests
- **Manual review:** Spot-check critical paths, security-sensitive code
- **Business validation:** Verify against acceptance criteria

---

## quality:audit

**Purpose:** Full codebase audit covering architecture, SOLID principles, code duplication, performance bottlenecks, and tech debt. Produces prioritized refactoring roadmap with effort estimates.

**Inputs:**
- path (string): Repository path
- depth (string, optional): Analysis depth (quick, standard, comprehensive)

**Outputs:**
- audit-report.md (detailed findings)
- tech-debt-roadmap.md (prioritized improvements)
- architecture-diagram.md (current state analysis)
- duplication-report.csv (duplicated code blocks)

**Guardrails:**
- Audit is non-destructive (read-only)
- Findings are specific with evidence (line numbers, code snippets)
- Roadmap is prioritized (critical → high → medium → low)
- Effort estimates are realistic
- No false positives (all findings are real issues)

**Examples:**

#### Example 1: Legacy Monolith Audit
**Execution:**
```bash
quality:audit path=./backend depth=comprehensive
```

**Expected Result:**
```
CODEBASE AUDIT — Backend Service

ARCHITECTURE ANALYSIS
Current: Layered monolith (50K LOC, 47 modules)
Pattern: Controllers → Services → DAOs → Database
Issues:
❌ User module imports Order module (circular dependency)
❌ Shared database prevents independent scaling
⚠️  Admin module: 2,400 lines, CC=34 (too high)

SOLID ASSESSMENT
Single Responsibility: 65/100 ❌ (AdminService handles too much)
Open/Closed: 60/100 ❌ (Adding payment method requires modifying PaymentProcessor)
Liskov Substitution: 90/100 ✓
Interface Segregation: 70/100 ⚠️ (UserService has 23 methods)
Dependency Inversion: 95/100 ✓

DUPLICATION ANALYSIS
❌ Pagination logic (5 services, 45 LOC duplicated)
❌ Email validation (3 places, 12 LOC duplicated)
❌ Error response format (8 controllers, 60 LOC duplicated)

Total: 120 LOC duplicated (0.9% of codebase)

TECH DEBT SCORE: 42/100 (HIGH)
Critical issues: 8
High issues: 15
Medium issues: 42
Low issues: 18

REFACTORING PRIORITY ROADMAP

Phase 1 (1 week, Quick Wins):
├─ Upgrade dependencies (2 hours)
├─ Extract validation utilities (2 hours)
├─ Remove hardcoded configs (3 hours)
└─ Add connection pooling (1 hour)
Result: 5% improvement, 8 hours effort

Phase 2 (2 weeks, Architecture):
├─ Break circular dependency (4 hours)
├─ Refactor Admin module into 4 modules (12 hours)
├─ Add API versioning (6 hours)
└─ Result: 20% improvement, 22 hours effort

Phase 3 (3-4 weeks, Scalability):
├─ Design microservices (16 hours)
├─ Migrate to separate databases (80 hours)
├─ Setup message queue (16 hours)
└─ Result: 50% improvement, 112 hours effort
```

**Timeline:** 1-2 hours

---

**Error Handling:**
- **Large codebase:** If > 1M LOC, sample-based analysis
- **Unrecognized patterns:** Note and flag for manual review
- **False positives:** If finding uncertain, mark as "requires validation"

**Edge Cases:**
- **Multiple languages:** Analyze each separately, then show integration points
- **Sparse docs:** Generate findings from code structure
- **Vendored code:** Exclude from analysis (node_modules, vendor/)

**Testing Approach:**
- **Spot-check:** Verify key findings with manual code review
- **Metrics:** Cross-check duplication scores with multiple tools
- **Roadmap:** Validate effort estimates with team

---

## quality:security

**Purpose:** OWASP Top 10 security audit with severity-ranked vulnerability report, remediation code examples, and compliance assessment (PCI-DSS, SOC 2, HIPAA).

**Inputs:**
- path (string): Repository path
- compliance (string, optional): Compliance targets (SOC2, PCI-DSS, HIPAA, etc.)

**Outputs:**
- security-audit.md (OWASP-aligned findings)
- remediation-plan.md (prioritized fixes with code examples)
- compliance-readiness.md (percentage ready for each compliance)

**Guardrails:**
- All findings include severity (CRITICAL, HIGH, MEDIUM, LOW)
- Fixes include before/after code snippets
- Compliance assessment is honest (no inflated percentages)
- Timeline is realistic for fixes

**Examples:**

#### Example 1: E-Commerce Security Audit
**Execution:**
```bash
quality:security path=./app compliance=PCI-DSS
```

**Expected Result:**
```
SECURITY AUDIT — E-Commerce Application

🔴 CRITICAL (Fix immediately)
1. Hardcoded database credentials
   Location: config.properties:23
   Before: DB_PASSWORD=abc123xyz
   After: DB_PASSWORD=${environment.DB_PASSWORD}
   Effort: 30 minutes
   Compliance: PCI-DSS 2.2.1

2. SQL Injection vulnerability
   Location: routes/products.py:145
   Before: WHERE name = '{search_term}'
   After: WHERE name = ? (parameterized)
   Effort: 3 hours
   Compliance: PCI-DSS 6.5.1

3. Missing HTTPS enforcement
   Fix: Add HSTS headers + HTTP→HTTPS redirect
   Effort: 1 hour
   Compliance: PCI-DSS 4.1

4. JWT tokens in localStorage
   Risk: XSS → token theft
   Fix: Use httpOnly cookies instead
   Effort: 2 hours
   Compliance: PCI-DSS 6.5.10

Total Critical Fix Time: 6.5 hours

🟡 HIGH (Fix this week)
1. Weak password policy (6 chars → 12 chars)
2. No rate limiting (add 1000 req/hour limit)
3. Passwords in logs (sanitize logs)
4. No admin audit trail (log all admin actions)
5. Missing CORS validation (whitelist origins)

Total High Fix Time: 9.5 hours

PCI-DSS READINESS: 61% → Target 100%
SOC 2 READINESS: 50% → Target 100%

Timeline: 
- Critical: 1 day (blocking)
- High: 5 days (this week)
- Medium: 4 weeks (post-launch acceptable)
```

**Timeline:** 1-2 hours

---

**Error Handling:**
- **Unknown compliance standard:** If target not recognized, ask for clarification
- **False positives:** If uncertain finding, mark as "requires validation"
- **Code patterns:** If unfamiliar with codebase language, may need domain expert review

**Edge Cases:**
- **Encryption:** Detects crypto misuse (hardcoded keys, weak algorithms)
- **Authentication:** Checks OAuth, JWT, session management, MFA
- **Data protection:** Scans for PII/sensitive data handling

**Testing Approach:**
- **Automated scan:** Use tools (OWASP ZAP, Snyk, SonarQube) for baseline
- **Manual review:** Spot-check critical findings
- **Penetration test:** Consider ethical hacking for high-risk apps

---

## quality:perf

**Purpose:** Performance bottleneck analysis and optimization roadmap. Identifies slow queries, algorithms, and I/O operations with before/after code and benchmarks.

**Inputs:**
- path (string): Repository path
- baseline (string, optional): Current performance ("500ms response time", "10s query")
- scale (string, optional): Target scale ("1M users", "100K concurrent")

**Outputs:**
- perf-analysis.md (bottleneck identification)
- optimization-roadmap.md (quick wins + long-term improvements)
- benchmarks.csv (before/after metrics)

**Guardrails:**
- Bottlenecks are ranked by impact (fix highest impact first)
- Quick wins are implemented first (4 hours, 70% improvement)
- Long-term improvements are phased
- All estimates include before/after metrics

**Examples:**

#### Example 1: Slow Product Search
**Execution:**
```bash
quality:perf path=./backend baseline="500ms search latency" scale="1M users"
```

**Expected Result:**
```
PERFORMANCE ANALYSIS

Current Baseline: 500ms (product search with 50K items)
Target: 100ms (5x improvement)
Scale goal: Support 1M users

BOTTLENECK BREAKDOWN
42% Database (full table scan, no index)
30% Service logic (N+1 queries)
18% Network latency
10% Other

QUICK WINS (4 hours, 70% improvement)

Win 1: Add database index (30 min)
Before: SELECT * FROM products WHERE name LIKE '%search%'
After: CREATE INDEX idx_products_name; + parameterized search
Impact: 500ms → 100ms (5x faster!)

Win 2: Fix N+1 queries (1 hour)
Before: 1 query for user + N queries for orders
After: 1 JOIN query fetching all at once
Impact: 100ms → 30ms

Win 3: Add Redis caching (1.5 hours)
Before: Every search hits database
After: Cache hot searches (60 min TTL)
Impact: 30ms → 5ms for cached searches

Win 4: Paginate results (1 hour)
Before: Return all 50K products
After: Return 20 items per page
Impact: Network latency -50ms

Total: 500ms → 50ms (10x faster!)

MEDIUM-TERM (2 weeks, additional 20% improvement)
- Read replicas (distribute read load)
- CDN for static assets
- Connection pooling optimization

LONG-TERM (1+ month, production scaling)
- Database sharding (split by region)
- Horizontal scaling (more servers)
- Caching layer refinement
```

**Timeline:** 1-2 hours

---

**Error Handling:**
- **Unclear baseline:** If current performance unknown, recommend profiling first
- **Unknown bottleneck:** If root cause unclear, suggest diagnostics (flame graphs, load testing)
- **Multi-faceted issues:** If multiple bottlenecks, address highest-impact first

**Edge Cases:**
- **Backend vs. frontend:** Analyzes both rendering and API latency
- **Database-heavy:** Focuses on query optimization, indexing
- **Async processing:** Detects blocking operations that should be async

**Testing Approach:**
- **Baseline:** Establish current performance metrics
- **Profiling:** Use flamegraphs, performance profilers
- **Load test:** Verify improvements under realistic load
- **Before/after:** Benchmark each optimization independently

---

## quality:debug

**Purpose:** Root cause analysis from stack trace or error description. Identifies failure mechanism, similar vulnerabilities in codebase, and generates regression tests to prevent recurrence.

**Inputs:**
- stack_trace (string): Error message + stack trace
- path (string): Repository path (for context)
- context (string, optional): Additional information (environment, user actions, logs)

**Outputs:**
- rca-report.md (5-phase RCA with root cause identified)
- fix.code (implemented fix with tests)
- edge-cases.md (similar vulnerabilities in codebase)
- regression-test.py (test to prevent recurrence)

**Guardrails:**
- RCA focuses on ROOT CAUSE, not symptoms
- Root cause is actionable (not "server crashed" but "NullPointerException because List is null")
- Fixes prevent recurrence (not just band-aids)
- Edge cases are systematically found

**Examples:**

#### Example 1: NullPointerException in OrderService
**Execution:**
```bash
quality:debug stack_trace="NullPointerException at OrderService.java:127" path=./backend context="Production incident, 50 affected users"
```

**Expected Result:**
```
ROOT CAUSE ANALYSIS

Stack Trace:
NullPointerException
  at com.shop.OrderService.getOrderTotal(OrderService.java:127)
  at com.shop.OrderController.getOrder(OrderController.java:42)

PHASE 1: CODE FUNCTIONALITY
Line 127: int total = order.getItems().stream()...
Issue: order.getItems() returned null instead of empty list

PHASE 2: ROOT CAUSE
JPA Entity: @OneToMany(mappedBy = "order")
Behavior:
- Expected: Empty List if no items
- Actual: null if no items
- Trigger: MySQL 5.7 → 8.0 upgrade changed behavior

Why now?
- Schema change + JPA version upgrade (2.7 → 3.0)
- 5% of orders have zero items (hit when traffic increased)

PHASE 3: FAILURE EXPLANATION
User requests: GET /orders/{id}
Code path: Controller → Service.getOrderTotal(order)
Crash: order.getItems() is null → NullPointerException

Impact: 50 users unable to view orders

PHASE 4: EDGE CASES FOUND
Similar patterns in codebase:
1. UserService.getAddresses() - also null-returns
2. ProductService.getReviews() - also null-returns
3. CartService.getItems() - also null-returns

All 3 have same vulnerability!

PHASE 5: PRODUCTION-READY FIX

Immediate (5 min hotfix):
```java
List<OrderItem> items = order.getItems();
if (items == null) items = Collections.emptyList();
```

Permanent (2 hours root cause):
```java
@Entity
public class Order {
    @OneToMany(mappedBy = "order")
    private List<OrderItem> items = new ArrayList<>();  // Initialize!
}
```

Regression Tests:
```java
@Test
void testGetOrderTotal_withZeroItems() {
    Order order = new Order();
    order.setItems(null);  // Simulate null
    
    int total = service.getOrderTotal(order);
    
    assertEquals(0, total);  // Should not crash
}
```

FIX TIMELINE
Stage 1: Hotfix + deploy (5 min + 5 min) → Users can view orders again
Stage 2: Root cause fix + test (2 hours) → Permanent solution
Stage 3: Audit similar patterns (4 hours) → Fix all 3 similar vulnerabilities
```

**Timeline:** 30-45 minutes

---

**Error Handling:**
- **Incomplete stack trace:** If trace incomplete, ask for full error logs
- **Reproduction steps missing:** If unclear how to reproduce, ask for scenario
- **Context sparse:** If unclear when/where error occurs, ask for log extracts

**Edge Cases:**
- **Race conditions:** If error is intermittent, may need load testing to reproduce
- **Third-party libraries:** If bug in dependency, provides workaround and upgrade recommendation
- **Environmental:** If error is environment-specific, includes environment-specific debugging

**Testing Approach:**
- **Reproduction:** Create minimal test case that triggers error
- **Verification:** Verify fix works and test passes
- **Regression:** Ensure fix doesn't break other tests

---

## quality:report

**Purpose:** Unified synthesis of all quality dimensions (review, audit, security, perf, debug) into single comprehensive HTML report. Aggregates findings, prioritizes by impact, provides consolidated remediation plan.

**Inputs:**
- path (string): Repository path OR prior analysis outputs
- comprehensive (boolean, optional): Include all analyses (default: yes)

**Outputs:**
- quality-report.html (interactive, self-contained)
- quality-summary.md (markdown version)
- priority-matrix.csv (impact vs. effort)

**Guardrails:**
- Report is comprehensive but digestible (executive summary + details)
- Issues are deduplicated (same finding from multiple analyses shown once)
- Remediation roadmap is realistic (prioritized, phased)
- HTML is self-contained (no external dependencies, works offline)

**Examples:**

#### Example 1: Complete Quality Assessment
**Execution:**
```bash
quality:report path=./backend comprehensive=true
```

**Expected Result:**
```
quality-report.html (Interactive)

Tab 1: Executive Summary
├─ Overall score: 62/100 (FAIR)
├─ Critical issues: 5
├─ High issues: 12
├─ Medium issues: 28
└─ 30-day remediation estimate: 80 hours

Tab 2: Code Review Findings
├─ Test coverage: 78% (target 95%)
├─ Code quality: 72/100
├─ Missing test cases: [list]

Tab 3: Security Audit
├─ OWASP violations: 8
├─ Severity breakdown: 2 CRITICAL, 3 HIGH, 3 MEDIUM
├─ Quick wins: Hardcoded secrets, SQL injection
├─ Compliance readiness: 60% PCI-DSS, 45% SOC 2

Tab 4: Performance Analysis
├─ Slowest endpoints: [top 5]
├─ Bottlenecks: Database (42%), N+1 queries (30%)
├─ Quick wins: Add indexes, caching (70% improvement, 4 hours)

Tab 5: Architecture Audit
├─ Tech debt: 42/100 (HIGH)
├─ SOLID violations: 3
├─ Duplication: 120 LOC (0.9%)
├─ Refactoring priority: [phased roadmap]

Tab 6: Priority Matrix
├─ Y-axis: Impact (user-facing outage to nice-to-have)
├─ X-axis: Effort (1 hour to 40 hours)
├─ Quadrants show which issues to fix first
├─ Quick wins: High impact, low effort
└─ Long-term: High impact, high effort

Downloadable: CSV, PDF, JSON exports
```

**Timeline:** 2-3 hours (aggregates all analyses)

---

**Error Handling:**
- **Incomplete analyses:** If some analyses missing, runs them first
- **Conflicting findings:** If multiple analyses disagree, notes and flags
- **Data mismatch:** If codebase changed, runs fresh analyses

**Edge Cases:**
- **Multiple services:** Generates separate sections per service
- **Legacy vs. modern:** Adjusts severity based on code age
- **Team size:** Factors team capacity into remediation timeline

**Testing Approach:**
- **Verification:** Spot-check key findings across analyses
- **Consistency:** Ensure all analyses agree on critical issues
- **Actionability:** Verify roadmap is executable for team

---

# BUSINESS ANALYST AGENT (2 functions)

**Role:** Utility — Backlog Management & Reporting

**Functions:** report, parse (2 total)

---

## ba:report

**Purpose:** Parse JIRA export (JSON or CSV) and generate interactive HTML backlog report with filtering, sorting, burndown charts, and metrics.

**Inputs:**
- file (string): Path to JIRA export (JSON or CSV)
- project (string, optional): Project key to filter
- output (string, optional): Output file path

**Outputs:**
- HTML report (interactive, filterable, responsive)
- Charts (burndown, velocity, cumulative flow)
- Statistics (total issues, by status, by priority)
- Export options (CSV, PDF)

**Guardrails:**
- Report is immediately useful (not a data dump)
- Filtering works intuitively (no complex UI required)
- Charts are accurate (verified against raw data)
- Mobile-responsive (works on phones)

**Examples:**

#### Example 1: JIRA Export to Interactive Report
**Execution:**
```bash
ba:report file=./jira-export.json project=MYAPP
```

**Expected Result:**
```
Interactive HTML Report

Header:
├─ Total Issues: 124
├─ By Status: Open (32), In Progress (18), Done (74)
├─ By Priority: Critical (2), High (8), Medium (64), Low (50)
├─ Story Points: 342 total, 180 completed

Filter Bar:
├─ Status dropdown (all, open, in progress, done)
├─ Priority dropdown (all, critical, high, medium, low)
├─ Assignee search
├─ Sprint filter
├─ Type filter (story, task, bug)

Main Table:
├─ Key (MYAPP-123)
├─ Title (with link to JIRA)
├─ Status (with color coding)
├─ Priority
├─ Assignee
├─ Story Points
├─ Sortable by any column
├─ Click row to expand details

Charts:
├─ Burndown chart (points per sprint)
├─ Velocity chart (points completed per sprint)
├─ Cumulative flow (by status)
├─ Priority distribution (pie chart)

Export:
├─ Download as CSV
├─ Download as PDF
├─ Copy as Markdown table
```

**Timeline:** 5-10 minutes

---

**Error Handling:**
- **Invalid JSON/CSV:** Reports parsing error, suggests format
- **Missing fields:** Handles differently formatted exports
- **Large export:** Optimizes for 1000+ issues

**Edge Cases:**
- **Multiple projects:** Generates separate sections or allows filtering
- **Custom fields:** Displays custom JIRA fields if present
- **Historical data:** If export includes closed sprints, shows historical charts

**Testing Approach:**
- **Format validation:** Verify HTML loads and renders correctly
- **Interactivity:** Test all filters, sorts, exports work
- **Data accuracy:** Verify metrics match source data

---

## ba:parse

**Purpose:** Extract structured data from JIRA export. Normalizes JSON/CSV into clean JSON with all issues and fields, ready for further processing.

**Inputs:**
- file (string): Path to JIRA export (JSON or CSV)
- output (string, optional): Output file path (default: parsed.json)

**Outputs:**
- JSON file (array of normalized issue objects)
- All fields normalized (Cloud vs. Server naming differences handled)
- Ready for import into other systems

**Guardrails:**
- Output is machine-readable (valid JSON)
- All issues represented (no data loss)
- Fields normalized (consistent naming)
- Output is ready for processing (no further cleanup needed)

**Examples:**

#### Example 1: JIRA CSV to Normalized JSON
**Execution:**
```bash
ba:parse file=./jira-export.csv output=./normalized-issues.json
```

**Expected Result:**
```json
{
  "export_date": "2026-01-15",
  "total_issues": 124,
  "issues": [
    {
      "key": "MYAPP-123",
      "title": "User authentication with OAuth2",
      "description": "Implement OAuth2 login for Google and GitHub...",
      "status": "In Progress",
      "priority": "High",
      "type": "Story",
      "assignee": {
        "key": "john.doe",
        "display_name": "John Doe",
        "email": "john@example.com"
      },
      "reporter": {
        "key": "jane.smith",
        "display_name": "Jane Smith"
      },
      "created_at": "2026-01-10T14:30:00Z",
      "updated_at": "2026-01-15T09:45:00Z",
      "story_points": 8,
      "sprint": "Sprint 5",
      "epic": "Authentication System",
      "acceptance_criteria": [
        "Users can sign in with Google",
        "Users can sign in with GitHub",
        "Tokens stored securely"
      ],
      "components": ["Backend", "Frontend"],
      "labels": ["authentication", "oauth2"],
      "custom_fields": {
        "team": "Backend",
        "effort_estimate": "13"
      }
    },
    ...more issues...
  ]
}
```

**Timeline:** 2-3 minutes

---

**Error Handling:**
- **Format detection:** Auto-detects JSON vs. CSV
- **Encoding issues:** Handles UTF-8 and other encodings
- **Malformed data:** Reports specific issues + line numbers

**Edge Cases:**
- **Mixed formats:** If export has inconsistencies, normalizes best-effort
- **Large files:** Streams processing for 10K+ issues
- **Null fields:** Omits null values or uses sensible defaults

**Testing Approach:**
- **Schema validation:** Verify output is valid JSON
- **Data completeness:** Verify all input issues in output
- **Field mapping:** Spot-check key fields (status, assignee, etc.)

---

## Launch Readiness Checklist

### Critical Risks (BLOCKING LAUNCH)
- [ ] Risk 1: Database Multi-AZ enabled + failover tested
- [ ] Risk 2: Idempotent webhooks + reconciliation job deployed
- [ ] Risk 3: Rate limiting deployed + tested
- [ ] Risk 4: Search endpoint authenticated + rate-limited
- [ ] Risk 5: Backup restore procedure tested

### High-Priority Risks (Week 1)
- [ ] Risk 6: Redis caching implemented
- [ ] Risk 7: Async payment processing working
- [ ] [6 more high-priority items...]

### Medium-Priority Risks (v1.1 or later)
- [ ] [5 medium-priority items...]

---

## Launch Readiness Summary

**Current Status:** 5% launch-ready
├─ Critical risks: 0/5 mitigated (0%)
├─ High risks: 0/8 mitigated (0%)
└─ Medium risks: N/A (post-launch)

**After Mitigations:** 95% launch-ready
├─ Critical risks: 5/5 mitigated (100%)
├─ High risks: 0/8 mitigated (needs weeks 1-2)
└─ Medium risks: N/A (post-launch)

**Timeline to Launch:**
- Effort: 26 hours (critical only)
- Effort: 38 hours (critical + high-priority must-have)
- Timeline: 5 business days (critical)
- Timeline: 10 business days (critical + high)

**Recommendation:** 
- Do not launch until critical risks mitigated (5 items, 26 hours)
- Plan 1-week post-launch for high-priority items
- No launch blocker for medium risks

**Go/No-Go:** CONDITIONAL GO
├─ Proceed with launch IF critical mitigations done
├─ Current status: NOT READY (0 of 5 critical done)
└─ ETA to launch-ready: 5 business days
```

---

#### Example 2: Migration Risk Assessment
**Execution:**
```bash
orchestrator:risk path=./migration-plan goal="Migrate monolith to microservices" timeline="12 weeks"
```

**Expected Result:**
```
Key risks identified:
- Distributed transaction failures (data inconsistency)
- Service coupling during extraction (tightly-coupled services)
- Database migration challenges (schema migration during cutover)
- Team capability gap (microservices experience)
- Rollback complexity (can't easily revert to monolith)

Mitigations proposed for each, effort estimated, critical path identified.
```

---

**Error Handling:**
- **Missing architecture:** If design incomplete, flag assumptions and proceed with known risks
- **Timeline ambiguous:** If "launch ASAP" too vague, ask for specific date
- **No baseline metrics:** If current system not instrumented, recommend adding monitoring first

**Edge Cases:**
- **Catastrophic risk:** If single failure could lose business (data center fire), recommend immediate multi-region failover
- **Regulatory risks:** If healthcare/finance, include compliance risks (HIPAA, PCI-DSS)
- **Third-party dependency:** If relying on external APIs (Stripe, SendGrid), quantify their SLAs

**Testing Approach:**
- **Unit test:** Verify each risk has impact + probability + mitigation
- **Validation:** Share with operations team, get feedback on missed risks
- **Post-launch tracking:** Monitor for which predicted risks actually occur, use to calibrate future estimates

---

## Summary

I have documented all 9 orchestrator functions comprehensively with:

1. **orchestrator:ideate** — Transform vague ideas into validated plans (3 examples: startup MVP, feature request, legacy modernization)

2. **orchestrator:solve** — Solve bottlenecks with multi-dimensional solutions (3 examples: database performance, team scaling, user growth)

3. **orchestrator:plan** — Break requirements into executable tasks (2 examples: e-commerce auth, legacy migration)

4. **orchestrator:build** — Full-stack end-to-end generation (2 examples: e-commerce MVP, OAuth2 feature)

5. **orchestrator:context** — Build project understanding (2 examples: e-commerce monolith, legacy Java system)

6. **orchestrator:pr** — Package and create GitHub PR (2 examples: MVP launch, security patch)

7. **orchestrator:review** — Strategic architecture review (2 examples: e-commerce design, microservices)

8. **orchestrator:tradeoff** — 3-option complexity analysis (2 examples: scaling architecture, team constraints)

9. **orchestrator:risk** — Risk assessment with mitigations (2 examples: launch readiness, migration risks)

Each function includes:
- ✓ Purpose (1-2 sentences)
- ✓ Inputs (parameters with types)
- ✓ Outputs (deliverables, formats)
- ✓ Guardrails (constraints, preconditions)
- ✓ Examples (3+ real-world scenarios with Context, Execution, Expected Result)
- ✓ Error Handling (failure modes + recovery)
- ✓ Edge Cases (boundary conditions)
- ✓ Testing Approach (unit, integration, validation)

Total: ~15,000 words of comprehensive documentation for orchestrator functions.



---

## ARCHITECT AGENT

**Role:** Architecture & Design — System topology, greenfield/brownfield design, API contracts, DB schema, UI architecture, accessibility

**Functions:** design, refactor, frontend, schema, api, a11y (6 total)

---

### architect:design

**Purpose:** Design complete system topology from scratch (greenfield). Creates C4 system diagram, API contracts, database schema, caching strategy, and deployment infrastructure in comprehensive design document.

**Inputs:**
- requirements (string): System requirements or business goals
- scale (string, optional): Scale targets ("100K users", "1M messages/day", "99.99% uptime")
- constraints (string, optional): Technical or business constraints ("3 engineers", "$50K infrastructure budget")

**Outputs:**
- architecture.md (markdown): C4 system diagram (levels 1-3), component descriptions, data flows, caching strategy, deployment topology
- api-contract.yaml (YAML): OpenAPI 3.0 specification with endpoints, request/response schemas, authentication, rate limits
- database-schema.sql (SQL): CREATE TABLE statements with indexes, constraints, migrations
- design-narrative.md (markdown): Explanation of design decisions, tradeoffs, and assumptions
- technology-stack.md (markdown): Technology recommendations by layer (frontend, backend, database, infrastructure)

**Guardrails:**
- Design is production-ready, not theoretical (includes operational concerns like monitoring, failover, scaling)
- Scale targets are reflected in architecture (100K users → single database OK; 1M users → sharding required)
- Caching strategy is explicit (what goes in cache, TTL, invalidation)
- Deployment topology accounts for availability and disaster recovery
- All major design decisions are documented with rationale
- No YAGNI (only architectures needed for stated requirements)

**Examples:**

#### Example 1: Real-Time Chat System (100K Concurrent Users)
**Context:** Team building real-time chat platform. High concurrency, low latency required.

**Execution:**
```bash
architect:design requirements="Real-time chat system for 100K concurrent users. 
Private 1:1 chats + group chats (up to 500 members). Message history searchable. 
Push notifications. Typing indicators. Read receipts."
```

**Expected Result:**
Delivers complete design document with:
- C4 diagram showing Frontend (React) → API Gateway → Chat Service, User Service, Notification Service
- WebSocket architecture for low-latency (sub-200ms message delivery)
- Message Queue (Apache Pulsar) for ordering and replay
- Database strategy: PostgreSQL for consistency + Cassandra for analytics
- Redis for presence + sessions
- Elasticsearch for full-text search
- Deployment: Kubernetes with auto-scaling
- All with rationale (why Pulsar vs. Kafka? Why Cassandra vs. PostgreSQL for analytics?)

Timeline: 1-2 hours | Output: 20-30 pages

---

#### Example 2: Data Pipeline (1M Events/Second)
**Context:** IoT company ingesting 1M events/second from sensors. Needs real-time dashboard + batch analytics.

**Execution:**
```bash
architect:design requirements="Process 1M sensor events/sec. Real-time dashboard (< 1sec latency).
Batch analytics (hourly, daily aggregations). Retention: 2 years."
scale="1M events/sec, 100K sensors, 100GB/day ingestion"
```

**Expected Result:**
- Kafka for ingestion (partitioned by sensor ID, 1000 partitions)
- Stream processing: Apache Spark or Flink (real-time aggregations)
- Time-series database: InfluxDB or Timescale for metrics
- Data warehouse: Snowflake or Redshift for analytics
- Storage: S3 for raw events, partitioned by date
- Architecture accounts for scaling to 10M events/sec
- Cost analysis: $50K/month at current scale

---

#### Example 3: E-Commerce MVP (100K Users)
**Context:** From SDLC examples — see full output in ARCHITECT_SDLC_EXAMPLES.md

**Execution:**
```bash
architect:design requirements="E-commerce platform with product catalog, 
shopping cart, Stripe checkout, order management. 100K users, 50K products."
```

**Expected Result:**
See ARCHITECT_SDLC_EXAMPLES.md Phase 0 for complete example with:
- System topology (CDN, API Gateway, services, databases)
- Component architecture
- Caching strategy (Redis for sessions, products)
- Deployment topology (multi-region setup)

---

**Error Handling:**
- **Incomplete requirements:** If requirements vague ("build a system"), ask clarifying questions (users, scale, latency, consistency needs)
- **Conflicting requirements:** If "MVP in 1 month" + "support 1M users" conflict, surface and ask for priority
- **Unknown scale:** If scale targets not provided, assume 10K users, then ask for validation
- **Unrealistic constraints:** If architecture requirements impossible to meet (e.g., "1-second latency with no caching"), flag and recommend tradeoffs

**Edge Cases:**
- **Greenfield vs. Brownfield:** Function assumes greenfield (new system). For existing system, use architect:refactor
- **Regulated domains:** If healthcare/finance/PII-heavy, design includes compliance considerations (HIPAA, SOC2)
- **Global scale:** If multi-region required, design includes data replication and conflict resolution strategy
- **High-volume transactions:** If payment processing or sensitive operations, design includes idempotency, audit trails, reconciliation

**Testing Approach:**
- **Unit test:** Verify architecture addresses all stated requirements
- **Peer review:** Have architect review with team, validate assumptions
- **Scalability model:** For each scale target, verify architecture can handle it (capacity planning)
- **Decision log:** Track which decisions require future revision (e.g., "sharding needed at 1M users")

---

### architect:refactor

**Purpose:** Plan brownfield refactoring of existing system. Assesses current state, diagnoses problems, designs target state, creates phased migration roadmap with zero-downtime procedures and rollback strategies.

**Inputs:**
- path (string): Path to existing codebase
- goal (string): Refactoring goal ("Split monolith into microservices", "Modernize from Django to FastAPI")
- pain_points (string, optional): Current problems ("4-hour deployments", "tight coupling", "N+1 queries")

**Outputs:**
- current-state.md (markdown): Analysis of existing architecture with diagrams, identified coupling, tech debt, pain points
- target-state.md (markdown): Desired architecture after refactoring
- refactoring-roadmap.md (markdown): Phased migration plan (5-7 phases) with zero-downtime procedures
- rollback-strategies.md (markdown): Rollback plan for each phase (if something breaks)
- risk-assessment.md (markdown): Risks specific to migration (data loss, downtime, inconsistency)

**Guardrails:**
- Migration is zero-downtime (Strangler pattern, blue-green, or parallel run)
- Each phase is independently deployable and valuable (not "do all at once")
- Current system continues working during transition (no big bang rewrite)
- Rollback procedure is documented and tested for each phase
- Data migration strategy is explicit (one-way sync vs. bidirectional consistency)
- Team has clear "go back" option if migration goes wrong

**Examples:**

#### Example 1: Monolith to Microservices (5-year Java Spring Monolith)
**Context:** From SDLC examples — legacy Java monolith with tight coupling.

**Execution:**
```bash
architect:refactor path=./legacy-monolith goal="Split into 4 microservices" 
pain_points="4-hour deployments, tight coupling, scaling bottleneck"
```

**Expected Result:**
See ARCHITECT_SDLC_EXAMPLES.md Scenario 2 for complete example with:
- Current state analysis (monolith diagram, coupling identified, 210 violations)
- Target state (4 independent services: User, Product, Order, Payment)
- Migration path using Strangler pattern (Phase 1-6 over 12 weeks)
- Zero-downtime deployment strategy (Blue-Green for each phase)
- Rollback strategies (stop new service, use monolith)

Timeline: 2-3 hours | Output: Detailed roadmap

---

#### Example 2: Database Migration (MySQL 5.7 → PostgreSQL 15)
**Context:** Team needs to migrate from MySQL to PostgreSQL. Old app still using MySQL.

**Execution:**
```bash
architect:refactor path=./mysql-based-app goal="Migrate to PostgreSQL" 
pain_points="MySQL 5.7 end-of-life, need JSON support, array types"
```

**Expected Result:**
- Current state: MySQL 5.7 with 50K LOC, 3 schemas
- Target state: PostgreSQL 15 with same data
- Phase 1: Setup PostgreSQL parallel database
- Phase 2: One-way replication (MySQL → PostgreSQL, real-time sync)
- Phase 3: Dual-write testing (writes to both, validate consistency)
- Phase 4: Cutover switch (reads + writes to PostgreSQL)
- Phase 5: Cleanup (archive MySQL)
- Rollback: If issues detected post-cutover, switch back to MySQL (reads from old replication)

---

#### Example 3: Monolith to Modular Monolith (Keeping Deployment But Adding Boundaries)
**Context:** Team not ready for microservices but needs to reduce coupling.

**Execution:**
```bash
architect:refactor path=./tightly-coupled-app goal="Enforce module boundaries" 
pain_points="All modules import from all other modules, changes affect everything"
```

**Expected Result:**
- Current state: Single monolith with 6 modules but no clear boundaries
- Target state: Same deployment, but modules isolated with clear APIs
- Phase 1: Define module boundaries (User, Order, Product, etc.)
- Phase 2: Create module-level APIs (interfaces each module exports)
- Phase 3: Refactor imports (no cross-module imports except API)
- Phase 4: Add event bus (RabbitMQ) for async communication
- Phase 5: Enforce boundaries with linting rules
- Result: Single deployment, independent modules, future microservices easy to extract

---

**Error Handling:**
- **No clarity on target:** If goal vague ("modernize the code"), ask specific questions (what problems to solve?)
- **Large system:** If > 1M LOC, recommend phasing the refactoring (extract services sequentially, not all at once)
- **High-risk migration:** If migration could cause data loss, recommend proof-of-concept first
- **No rollback plan:** If rollback impossible, recommend delaying migration or building safer approach

**Edge Cases:**
- **Data schema change:** If migration requires schema changes, output includes migration scripts + rollback SQL
- **Breaking API changes:** If refactoring changes public API, migration includes versioning strategy (v1 + v2 parallel)
- **Significant team upskilling:** If target requires new tech (e.g., team has no Kubernetes experience), migration plan includes training timeline
- **Regulatory compliance:** If system handles regulated data (PCI, HIPAA), migration plan includes compliance checks at each phase

**Testing Approach:**
- **Dry run:** Execute migration on copy of production data first, verify output
- **Phase testing:** After each phase, run full integration tests on new system while keeping old system running
- **Rollback testing:** For each phase, simulate failure and practice rollback (don't just document it)
- **Performance comparison:** Before/after metrics (deployment time, query latency, API response time)

---

### architect:schema

**Purpose:** Design database schema from scratch. Generates CREATE TABLE statements with indexes, constraints, migrations, and partitioning strategy. Optimized for stated scale and query patterns.

**Inputs:**
- requirements (string): Entity requirements ("Users, products, orders, inventory, payments")
- db (string): Database system ("postgresql", "mysql", "mssql", "dynamodb")
- scale (string, optional): Data volume ("100K users", "1M events/day", "50K products")

**Outputs:**
- schema.sql (SQL): CREATE TABLE, PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK constraints
- indexes.sql (SQL): Index definitions (B-tree, Hash, Full-text, JSON)
- migrations/ (directory): Version-controlled migration scripts (001_init.sql, 002_add_column.sql, etc.)
- partitioning-strategy.md (markdown): If applicable, how to partition large tables (by date, by range, by hash)
- optimization-notes.md (markdown): Rationale for index choices, denormalization tradeoffs, query patterns to support

**Guardrails:**
- Schema is normalized (3NF minimum) unless denormalization explicitly justified
- Indexes are designed for stated query patterns (not over-indexed)
- Constraints enforce data integrity (NOT NULL where required, UNIQUE where needed, FK relationships)
- Migrations are written to be idempotent (can re-run without breaking)
- Scaling strategy is documented (how to handle 10x growth)
- No circular foreign keys or design flaws

**Examples:**

#### Example 1: E-Commerce Database (100K Users, 50K Products)
**Context:** From SDLC examples.

**Execution:**
```bash
architect:schema requirements="Users, products, orders, order_items, inventory, payments" 
db=postgresql scale="100K users, 50K products, 1M orders"
```

**Expected Result:**
See ARCHITECT_SDLC_EXAMPLES.md Phase 2 for complete example with:
- Users table (email, password_hash, profile)
- Products table (name, price, category, stock)
- Orders table (user_id, total, status, timestamps)
- Order items table (order_id, product_id, quantity, price)
- Payments table (order_id, stripe_id, status, amount)
- Message reads table (tracks who read what)
- Blocked users table (relationships)
- Indexes: (user_id, created_at), (category, price), email unique, etc.
- Partitioning: Orders partitioned by date (monthly)
- Migrations: 3 phases (initial schema, indexes, partitioning)

---

#### Example 2: Real-Time Chat Schema (100K Concurrent Users, 2-Year History)
**Context:** High-volume chat system.

**Execution:**
```bash
architect:schema requirements="Users, chats, chat_members, messages, message_reads" 
db=postgresql scale="100K concurrent users, 1B messages, 2-year retention"
```

**Expected Result:**
- Users table (id, email, name, status, created_at)
- Chats table (id, type direct/group, created_by, created_at)
- Chat members table (chat_id, user_id, role, joined_at)
- Messages table (id, chat_id, sender_id, content, media_urls, created_at)
  - Composite index: (chat_id, created_at DESC) for chronological queries
  - Separate index: (sender_id) for "messages from user X"
  - Partitioned by chat_id for 1B+ message scale
- Message reads table (message_id, user_id, read_at)
- Optimization notes: Messages table has high write volume, so:
  - Indexes chosen for read performance (filter by chat, sort by time)
  - Separate table for reads (not denormalized into messages, for scalability)
  - Partition strategy: by chat_id (1000s of partitions)

---

#### Example 3: Time-Series Data (1M Sensor Events/Second)
**Context:** IoT system.

**Execution:**
```bash
architect:schema requirements="Sensors, readings, alerts" 
db=postgresql scale="1M events/second, 100K sensors, 2-year retention"
```

**Expected Result:**
- Sensors table (id, name, location, sensor_type)
- Readings table (sensor_id, timestamp, value, unit)
  - Partitioned by timestamp (daily or hourly)
  - Hyper-table setup (using pg_partman extension)
  - Composite index: (sensor_id, timestamp DESC) for time-range queries
  - Note: 1M events/sec = 86B events/day → need aggressive partitioning
- Alerts table (sensor_id, reading_id, alert_type, created_at)
- Optimization notes:
  - Readings table is write-heavy, so minimal indexes (only what's needed for queries)
  - Use batch inserts, not individual INSERTs (critical for 1M/sec scale)
  - Consider time-series specific DB (TimescaleDB, InfluxDB) for even better scale

---

**Error Handling:**
- **Ambiguous requirements:** If entities not clearly described, ask clarifying questions (User has what fields? How many Orders per User?)
- **Denormalization needed:** If schema is over-normalized for stated query patterns, recommend denormalization with rationale
- **Missing constraints:** If business rules not specified (e.g., order total = sum of items), ask and add constraints
- **Circular dependencies:** If schema has circular FKs (A → B → A), recommend redesign

**Edge Cases:**
- **Multi-tenant schema:** If system is SaaS with multiple customers, design includes tenant isolation (separate schemas vs. shared with tenant_id column)
- **Soft deletes:** If data should be recoverable ("deleted" but not removed), schema includes deleted_at timestamp
- **Audit trail:** If compliance requires tracking changes, design includes audit log table
- **Versioning:** If entities have versions (e.g., Product versions for price history), schema supports temporal queries

**Testing Approach:**
- **Unit test:** Verify schema satisfies all constraints, no circular dependencies
- **Load test:** With scale target, verify indexes perform (< 100ms for typical query)
- **Migration test:** Run migrations on copy of production schema, verify no data loss
- **Backup/restore test:** Verify schema can be backed up and restored

---

### architect:api

**Purpose:** Design REST API contracts (OpenAPI 3.0 specification). Generates endpoint definitions with request/response schemas, status codes, authentication, rate limiting, and examples. API-first design enables frontend and backend to work in parallel.

**Inputs:**
- requirements (string): API requirements ("List products", "Create order", "Search by category")
- format (string, optional): OpenAPI version ("openapi3.0", "openapi3.1", "swagger2")
- auth (string, optional): Authentication method ("oauth2", "jwt", "api-key")

**Outputs:**
- api-spec.yaml (YAML): Full OpenAPI 3.0 specification with all endpoints, schemas, examples
- api-narrative.md (markdown): Human-readable description of API design decisions
- client-examples.md (markdown): cURL, JavaScript, Python examples for key endpoints
- schema-definitions.json (JSON): Reusable schema components (User, Product, Order, etc.)

**Guardrails:**
- All endpoints documented (no surprises for frontend)
- Request/response schemas are complete and specific (not generic "object")
- Status codes are appropriate (200 OK, 201 Created, 400 Bad Request, 404 Not Found, 500 Error)
- Authentication is specified for each endpoint (public vs. authenticated vs. admin-only)
- Rate limiting is documented (requests/hour or requests/minute)
- Error responses follow consistent format (not ad-hoc error messages)
- Examples are realistic (not dummy data)

**Examples:**

#### Example 1: E-Commerce Product API
**Context:** From SDLC examples.

**Execution:**
```bash
architect:api requirements="List products (paginated, filterable), 
get product details, create product (admin), update product (admin), 
search by keyword" format=openapi3.0 auth=jwt
```

**Expected Result:**
See ARCHITECT_SDLC_EXAMPLES.md Phase 1 for complete OpenAPI spec with:
- GET /products (list, paginated: skip, limit; sortable: price, created_at)
- GET /products/{product_id} (details)
- POST /products (admin only, requires JWT role=admin)
- PUT /products/{product_id} (admin only)
- GET /products/search (full-text search by keyword)
- All with request/response schemas, status codes, examples

---

#### Example 2: Chat API (WebSocket + REST)
**Context:** Real-time chat with WebSocket and REST endpoints.

**Execution:**
```bash
architect:api requirements="List chats, get chat with history, send message, 
get typing status, get user presence" format=openapi3.0 auth=oauth2
```

**Expected Result:**
- REST endpoints:
  - GET /chats (list user's chats)
  - GET /chats/{chat_id} (chat details + recent messages)
  - POST /chats/{chat_id}/messages (send message)
  - GET /chats/{chat_id}/messages/search (search messages)
  - POST /chats/{chat_id}/mark-as-read (mark message as read)
- WebSocket endpoint:
  - WS /chats/{chat_id} (subscribe to messages, typing, presence)
- All with authentication (OAuth2), rate limiting, response schemas

---

#### Example 3: Payment API (Stripe Integration)
**Context:** Payment processing with webhook.

**Execution:**
```bash
architect:api requirements="Create payment, get payment status, 
webhook for payment confirmation" format=openapi3.0 auth=jwt
```

**Expected Result:**
- POST /payments (create payment, returns client_secret for Stripe)
- GET /payments/{payment_id} (get status)
- POST /webhooks/stripe (webhook handler, idempotent)
- All with error handling (failed payment, duplicate webhook, network error)
- Includes retry logic, idempotency key specification

---

**Error Handling:**
- **Vague requirements:** If "create product" not detailed, ask for required fields, validation rules, error cases
- **Ambiguous response:** If response format unclear (array vs. paginated object), ask and document
- **Missing error cases:** If error scenarios not specified, add common ones (validation error, auth error, not found)
- **Inconsistent naming:** If endpoints use inconsistent naming (POST /users vs. POST /products), standardize

**Edge Cases:**
- **Versioning:** If API will evolve, design includes versioning (v1, v2) in URL path
- **Pagination:** If response could be large (product list, messages), design specifies pagination (offset/limit vs. cursor)
- **Filtering/sorting:** If multiple filter options, document which are filterable and how (query params)
- **Bulk operations:** If bulk create/update likely, add endpoints for it (POST /products/bulk)

**Testing Approach:**
- **Specification validation:** Verify OpenAPI spec is valid (no syntax errors)
- **Consistency check:** Verify all endpoints follow same conventions (naming, response format, error format)
- **Peer review:** Have backend + frontend engineer review spec, gather feedback before implementation
- **Example execution:** Try cURL examples, verify they work as documented

---

### architect:frontend

**Purpose:** Design React component architecture. Specifies component hierarchy, state management approach, composition patterns, and accessibility strategy. Enables frontend engineer to implement without architecture surprises.

**Inputs:**
- requirements (string): Feature requirements ("Product list with filters", "Shopping cart", "Checkout form")
- framework (string, optional): Frontend framework ("react", "vue", "svelte")
- state_management (string, optional): State approach ("context-api", "redux", "zustand", "jotai")

**Outputs:**
- component-architecture.md (markdown): Component tree, props interfaces, state model
- component-designs.tsx (TypeScript): Skeleton component definitions with prop interfaces
- state-management.md (markdown): State store design (global state, local state, when to use each)
- composition-patterns.md (markdown): Reusable composition patterns (container/presenter, hooks, etc.)
- accessibility.md (markdown): WCAG 2.1 AA requirements for each component (ARIA labels, keyboard nav, color contrast)

**Guardrails:**
- Component hierarchy is shallow (avoid "component hell")
- Props are clearly specified (TypeScript interfaces with JSDoc)
- State is appropriately scoped (global vs. local)
- Composition patterns are reusable (not one-off implementations)
- Accessibility is designed-in, not retrofitted (ARIA labels, keyboard navigation, focus management)
- Performance considerations are documented (virtual lists for large data, memoization, code splitting)

**Examples:**

#### Example 1: Chat Application UI
**Context:** Real-time chat UI for 100K concurrent users.

**Execution:**
```bash
architect:frontend requirements="Chat list (sidebar), chat view (messages + input), 
typing indicator, read receipts, unread badge" framework=react state_management=redux
```

**Expected Result:**
See ARCHITECT_SDLC_EXAMPLES.md Phase 3 for complete example with:
- Component hierarchy:
  - ChatApp (root)
    - Sidebar (chat list)
      - ChatListItem (repeated)
    - ChatView (message display + input)
      - ChatHeader
      - MessageList (virtualized for 1000+ messages)
        - MessageBubble (repeated)
        - TypingIndicator
      - MessageInput
- Props interfaces (TypeScript)
  - ChatListItemProps (chat, isActive, unreadCount, onClick)
  - MessageBubbleProps (message, author, readBy, onReply)
  - MessageInputProps (onSend, disabled, placeholder)
- State model (Redux)
  - chats (array of Chat)
  - activeChat (Chat)
  - messages (array of Message)
  - typingUsers (array of User)
  - presence (Map<userId, status>)
- Performance optimizations:
  - Virtual scrolling for MessageList (1000+ messages)
  - Message memoization (prevent re-renders on parent update)
  - Debounced typing indicator (don't spam server)
  - Web Worker for message processing (heavy parsing)
- Accessibility:
  - Semantic HTML (lists, buttons, forms)
  - ARIA labels (aria-label for icons, aria-live for typing indicator)
  - Keyboard navigation (Tab through messages, Enter to send, Escape to close)
  - Color contrast (4.5:1 minimum)

---

#### Example 2: E-Commerce Product Page
**Context:** Single product detail page with variants, reviews, recommendations.

**Execution:**
```bash
architect:frontend requirements="Product image + details, variant selector (size/color), 
quantity input, add to cart button, reviews section, recommended products" 
framework=react state_management=zustand
```

**Expected Result:**
- Component hierarchy:
  - ProductPage
    - ProductImage (carousel of images)
    - ProductDetails (name, price, description)
    - VariantSelector (size, color dropdowns)
    - QuantityInput (spinner or input)
    - AddToCartButton
    - ReviewsSection (paginated reviews)
    - RecommendedProducts (horizontal scroll)
- State management:
  - Global: cart state (items, total)
  - Local: selectedVariant, quantity, reviewsPage
- Performance:
  - Image lazy-loading (IntersectionObserver)
  - Reviews pagination (not load all reviews upfront)
  - Recommended products defer loading (if below fold)
- Accessibility:
  - Product images have alt text
  - Variant selector has labels + ARIA
  - Reviews expandable sections have proper ARIA
  - Keyboard navigation through variants + quantity + buttons

---

#### Example 3: Dashboard with Complex Data Visualization
**Context:** Analytics dashboard with charts, filters, date range picker.

**Execution:**
```bash
architect:frontend requirements="Sales chart (line/bar), top products table (sortable), 
filters (date range, category), export to CSV" 
framework=react state_management=context-api
```

**Expected Result:**
- Component hierarchy:
  - Dashboard
    - FilterBar (date picker, category selector)
    - SalesChart (React-Recharts)
    - TopProductsTable (sorted columns)
    - ExportButton
- State:
  - Global: filters (dateRange, category)
  - Local: chartType (line/bar), sortBy (product, revenue)
- Performance:
  - Memoize chart data transformation (expensive)
  - Debounce filter changes (don't re-fetch on every keystroke)
  - Virtualized table (if 1000+ products)
- Accessibility:
  - Chart has data table alternative (for screen readers)
  - Date picker is keyboard accessible
  - Table has ARIA labels on sortable columns
  - Export button has clear label

---

**Error Handling:**
- **Vague requirements:** If "product page" not detailed, ask what components (images, reviews, recommendations?)
- **Missing state model:** If how to store state unclear, propose and ask for validation
- **Over-engineered:** If proposed architecture too complex for requirements, simplify and explain tradeoffs

**Edge Cases:**
- **Real-time updates:** If component receives live data (chat messages, stock prices), design includes update strategy (polling vs. WebSocket vs. Server-Sent Events)
- **Offline support:** If app works offline, design includes data sync, conflict resolution, optimistic updates
- **Responsive design:** Component architecture should work at all breakpoints (mobile, tablet, desktop)
- **Dark mode:** If dark mode required, design includes theme provider, CSS variables

**Testing Approach:**
- **Unit test:** Component prop interfaces are correct, render without errors
- **Integration test:** Components compose correctly, state flows properly (parent → child → event → update)
- **Accessibility test:** axe-core scans, keyboard navigation works, screen reader compatible
- **Performance test:** Component renders in < 16ms (60fps), re-renders don't cause jank

---

### architect:a11y

**Purpose:** Accessibility (A11y) audit of existing UI components. Evaluates WCAG 2.1 AA compliance, identifies missing semantic HTML, ARIA labels, keyboard navigation, color contrast issues. Provides remediation code and fixes.

**Inputs:**
- path (string): Path to component files (React TSX, Vue, HTML)
- target (string, optional): WCAG target level ("wcag2.1-a", "wcag2.1-aa", "wcag2.1-aaa")

**Outputs:**
- accessibility-audit.md (markdown): Detailed findings with WCAG criteria, severity (critical/high/medium/low)
- remediation-plan.md (markdown): Prioritized fixes with effort estimates
- before-after-code.md (markdown): Code examples showing fixes
- accessibility-test-suite.test.tsx (TypeScript): axe-core + RTL accessibility tests

**Guardrails:**
- Audit is comprehensive (not just color contrast, but also semantic HTML, keyboard nav, ARIA)
- Findings reference WCAG 2.1 criteria (WCAG 2.1 Level A, AA, AAA)
- Fixes are code examples, not just recommendations ("use aria-label" → shows exact code)
- Severity is accurate (missing alt text = high, non-descriptive link text = medium)
- Tests validate fixes work (not just code review)

**Examples:**

#### Example 1: E-Commerce Product Page Audit
**Context:** React product page needs accessibility audit.

**Execution:**
```bash
architect:a11y path=./src/components/ProductPage.tsx target=wcag2.1-aa
```

**Expected Result:**
```
accessibility-audit.md

WCAG 2.1 AA AUDIT — Product Page
Compliance: 65% (needs fixes)

CRITICAL (5 issues, blocks launch):
✗ Images missing alt text (WCAG 1.1.1)
  - Product images have no alt attribute
  - Fix: <img alt="Red leather handbag, size L" />
  - Effort: 15 minutes
  - Impact: Screen readers can't describe product

✗ Form fields not labeled (WCAG 1.3.1, 3.3.2)
  - Quantity input has no label
  - Variant selects (size, color) have no labels
  - Fix: <label htmlFor="quantity">Quantity</label>
  - Effort: 20 minutes
  - Impact: Screen readers don't know field purpose

HIGH (3 issues):
⚠️  Color contrast insufficient (WCAG 1.4.3)
  - "Add to cart" button: dark gray text on dark background (2.5:1, needs 4.5:1)
  - Fix: Change text to white or background to lighter color
  - Effort: 5 minutes

⚠️  Heading hierarchy broken (WCAG 1.3.1)
  - H2 used before H1 (page has no H1)
  - Add H1 for product name

⚠️  Focus indicator not visible (WCAG 2.4.7)
  - Buttons have no visible focus outline
  - Fix: button:focus { outline: 2px solid #0066cc; }

MEDIUM (2 issues):
- Aria-label missing on cart icon button
- Reviews expandable section not marked with aria-expanded

REMEDIATION PRIORITY:
1. Add image alt text (15 min)
2. Label form fields (20 min)
3. Fix color contrast (5 min)
4. Add H1 and fix heading hierarchy (10 min)
5. Visible focus indicators (5 min)
Total effort: 55 minutes
Timeline to AA compliance: 1 hour

TEST COVERAGE:
✓ All axe-core checks passing (after fixes)
✓ Keyboard navigation: Tab through all interactive elements
✓ Screen reader: Product name, price, description readable
✓ Color contrast: All text >= 4.5:1
```

---

#### Example 2: Chat Application UI Audit
**Context:** Real-time chat UI accessibility review.

**Execution:**
```bash
architect:a11y path=./src/components/ChatApp.tsx target=wcag2.1-aa
```

**Expected Result:**
Findings include:
- CRITICAL: Chat list items not keyboard accessible (no role=button or tabindex)
- CRITICAL: Typing indicator has aria-live but not aria-atomic (content updates unclear)
- HIGH: Message timestamps not in semantic time element
- HIGH: Read receipts not announced to screen readers
- MEDIUM: Unread badge not associated with message
- Fixes with code examples and tests

---

#### Example 3: Dashboard with Charts Audit
**Context:** Analytics dashboard with Recharts visualization.

**Execution:**
```bash
architect:a11y path=./src/components/Dashboard.tsx target=wcag2.1-aa
```

**Expected Result:**
Findings:
- CRITICAL: Chart canvas has no accessible name or role
  - Fix: Provide <table> of same data for screen readers
- HIGH: Chart legend text too small (9px)
  - Fix: Increase to 12px minimum
- HIGH: Filter dropdown not keyboard accessible
  - Fix: Use semantic <select> or ARIA combobox
- Tests: Verify data table alternative exists, keyboard nav works

---

**Error Handling:**
- **No components found:** If path invalid, report clearly
- **Unsupported framework:** If component format unrecognized (e.g., Vue), process as best as able or flag limitation
- **Already accessible:** If components already comply, report as passing with no changes needed
- **Over-constrained:** If WCAG AAA target requested but WCAG AA is sufficient, clarify with user

**Edge Cases:**
- **Dynamic content:** If component updates content after load (chat messages, live data), audit includes ARIA live regions (aria-live, aria-atomic)
- **Modal dialogs:** If component has modals, audit includes focus management (focus trap, return focus on close)
- **Complex widgets:** If combobox, datepicker, or other complex ARIA widget, audit verifies all ARIA attributes
- **Third-party components:** If using library component (react-beautiful-dnd, react-calendar), audit checks if library is a11y compliant

**Testing Approach:**
- **Automated scanning:** axe-core to identify accessibility violations
- **Manual testing:** Keyboard navigation (Tab, arrow keys, Enter, Escape)
- **Screen reader testing:** NVDA (Windows) or VoiceOver (Mac) to verify content is understandable
- **Color contrast:** Use WCAG contrast checker (even with a11y tools)
- **Regression testing:** Add accessibility tests to CI/CD to prevent new violations

---

## Summary

I have documented all 6 architect functions comprehensively with:

1. **architect:design** — Complete system topology design for greenfield projects (3 examples: chat system, data pipeline, e-commerce)

2. **architect:refactor** — Brownfield refactoring assessment and phased migration (3 examples: monolith→microservices, database migration, modular monolith)

3. **architect:schema** — Database DDL with indexes, migrations, and optimization (3 examples: e-commerce, chat, time-series)

4. **architect:api** — REST API contract design with OpenAPI 3.0 (3 examples: e-commerce API, chat API with WebSocket, payment API)

5. **architect:frontend** — React component architecture with state management and accessibility (3 examples: chat UI, product page, dashboard)

6. **architect:a11y** — WCAG 2.1 AA accessibility audit with remediation code (3 examples: product page, chat app, dashboard)

Each function includes:
- ✓ Purpose (1-2 sentences)
- ✓ Inputs (parameters with types)
- ✓ Outputs (deliverables, formats)
- ✓ Guardrails (constraints, preconditions)
- ✓ Examples (3+ real-world scenarios with Context, Execution, Expected Result)
- ✓ Error Handling (failure modes + recovery)
- ✓ Edge Cases (boundary conditions)
- ✓ Testing Approach (unit, integration, validation)

All examples are grounded in real-world scenarios from ARCHITECT_SDLC_EXAMPLES.md and FUNCTION_EXAMPLES.md where applicable.

---

## IMPLEMENTER AGENT

**Role:** Implementation & Execution — Code generation, testing, documentation, CI/CD, containerization, infrastructure (includes comprehensive full function)

**Functions:** build, test, doc, pipeline, docker, iac, full (7 total)

---

[Functions will be documented in Tasks 3-5]

---

## QUALITY AGENT

**Role:** QA, Security & Performance — PR validation, codebase audit, OWASP security scanning, performance optimization, RCA, unified quality synthesis

**Functions:** review, audit, security, perf, debug, report (6 total)

---

[Functions will be documented in Tasks 3-5]

---

## BUSINESS ANALYST AGENT

**Role:** Utility — Backlog — JIRA parsing and HTML backlog visualization

**Functions:** report, parse (2 total)

---

[Functions will be documented in Tasks 3-5]

---

## Notes

- All agents follow master rules from `instructions/master_instruction_set.md`
- Each agent is **tech-agnostic** and delegates to reusable skills for implementation
- Functions dispatch via `agent:function` syntax (e.g., `orchestrator:plan`)
- No role overlap — clear separation of concerns
- **implementer:full** runs build+test+doc in same context to prevent state loss
