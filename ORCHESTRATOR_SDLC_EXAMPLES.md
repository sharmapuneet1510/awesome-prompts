---
title: Orchestrator Agent — SDLC Examples
description: Complete software development lifecycle examples showing orchestrator functions in real-world scenarios
version: 1.0
---

# Orchestrator Agent — SDLC Examples

**Role:** Strategy & Orchestration | **Functions:** plan, build, context, review, tradeoff, risk, pr

Complete lifecycle examples showing how orchestrator functions work together in real SDLC phases.

---

## 📋 SDLC Lifecycle Overview

```
Phase 0: Requirements     → orchestrator:plan
Phase 1: Planning         → orchestrator:build (orchestrates downstream)
Phase 2: Design Review    → orchestrator:review, orchestrator:tradeoff
Phase 3: Risk Assessment  → orchestrator:risk
Phase 4: Context Building → orchestrator:context (for existing projects)
Phase 5: PR Management    → orchestrator:pr
```

---

## 🎯 Scenario 1: E-Commerce MVP (Greenfield)

### Phase 0: Requirements Gathering

**Situation:** New startup wants to build an e-commerce platform. Founder has rough idea but no technical spec.

**Command:**
```bash
orchestrator:plan "We want to build an e-commerce platform like Shopify but for small businesses. 
Features: product catalog, shopping cart, checkout with Stripe, order management, 
customer notifications via email. Target: 100K products, 10K concurrent users in year 1."
```

**What Orchestrator Does (PHASE 0):**

Asks clarifying questions:
- "B2C or B2B? Both?"
- "Multi-vendor or single seller?"
- "Inventory management: real-time stock or batch updates?"
- "Global or single country initially?"
- "Multiple currencies or USD only?"
- "Custom shipping rules or flat rate?"

**Output Artifacts:**
```
requirements.md
├─ Clarified requirements (with assumptions stated)
├─ Key constraints (budget, timeline, tech stack preferences)
└─ Success criteria (metrics, scale targets)

task-breakdown.json
├─ Task 01: Database schema (products, orders, users, inventory)
├─ Task 02: Backend API (FastAPI or Spring Boot)
├─ Task 03: Frontend UI (React SPA)
├─ Task 04: Payment integration (Stripe)
├─ Task 05: Email notifications
├─ Task 06: Order management dashboard
├─ Task 07: Tests (95%+ coverage)
├─ Task 08: CI/CD pipeline
└─ Task 09: Deployment (Docker + K8s)

execution-order.txt
├─ Dependencies mapped
├─ Critical path identified
└─ Risk dependencies flagged
```

**Timeline:** 5-10 minutes

---

### Phase 1: Planning & Orchestration

**Command:**
```bash
orchestrator:build path=./requirements.md
```

**What Orchestrator Does:**

1. Reads clarified requirements
2. Orchestrates downstream agents:
   ```
   architect:design          ← System topology, API contracts, schema, caching strategy
   implementer:full          ← Code generation, testing, documentation
   quality:review            ← Validate against requirements
   orchestrator:pr           ← Package and submit
   ```

**Output Structure:**
```
Generated System/
├─ Backend/
│  ├─ models/ (Product, Order, User, Payment)
│  ├─ routes/ (products, orders, users, payments)
│  ├─ services/ (ProductService, OrderService, StripeService)
│  ├─ middleware/ (auth, logging, error handling)
│  └─ tests/ (95%+ coverage)
│
├─ Frontend/
│  ├─ components/ (ProductCard, Cart, Checkout, Dashboard)
│  ├─ pages/ (ProductList, Order, Checkout, Admin)
│  ├─ services/ (api.ts, stripe.ts)
│  └─ tests/ (95%+ coverage)
│
├─ Database/
│  ├─ schema.sql (migrations)
│  ├─ indexes.sql
│  └─ seed-data.sql
│
├─ Infrastructure/
│  ├─ Dockerfile
│  ├─ docker-compose.yml
│  ├─ k8s/deployment.yaml
│  ├─ .github/workflows/ci.yml
│  └─ .github/workflows/deploy.yml
│
├─ Documentation/
│  ├─ README.md (setup, usage, architecture)
│  ├─ API.md (endpoint reference)
│  ├─ ARCHITECTURE.md (system design)
│  ├─ DEPLOYMENT.md (production checklist)
│  └─ CONTRIBUTING.md (development guide)
│
└─ Test Reports/
   ├─ test-results.html
   ├─ coverage-report.html
   └─ performance-baseline.json
```

**Timeline:** 1-2 hours

---

### Phase 2: Design Review & Tradeoffs

**Command (Design Review):**
```bash
orchestrator:review path=./system-design.md context="E-commerce MVP with Stripe"
```

**Orchestrator Analysis:**
- Are assumptions documented? ✓
- Is design too complex? ❌ Consider simplifying inventory initially
- What could fail? → Single database instance (SPOF), Stripe API downtime
- Production readiness? ⚠️ Missing monitoring and alerting

**Output:**
```
Design Review Report
├─ Strengths
│  ├─ ✓ Clear API contract
│  ├─ ✓ Proper database normalization
│  └─ ✓ Auth strategy documented
├─ Concerns
│  ├─ ❌ No database replication for HA
│  ├─ ❌ Missing caching strategy
│  └─ ❌ No observability setup
└─ Recommendations
   ├─ Add Redis for session caching
   ├─ Setup PostgreSQL replicas
   └─ Add APM (e.g., New Relic)
```

**Command (Tradeoffs):**
```bash
orchestrator:tradeoff goal="Scale to 100K products, 10K concurrent users, 99.9% uptime, 6-month timeline"
```

**Orchestrator Analysis:**

```
APPROACH 1: Monolithic (Simplest, Fastest to MVP)
├─ Timeline: 6 weeks
├─ Team size: 3 engineers
├─ Uptime: 99.5% (limited)
├─ Scale limit: 10K concurrent users
├─ Operational complexity: Low
├─ Cost: $500/month
└─ Risk: Database becomes bottleneck at scale

APPROACH 2: Microservices (Complex, Maximum Scale)
├─ Timeline: 16 weeks
├─ Team size: 8 engineers
├─ Uptime: 99.99% (achievable)
├─ Scale limit: Unlimited
├─ Operational complexity: Very high (K8s, service mesh)
├─ Cost: $5K/month
└─ Risk: Over-engineered for MVP, slow to market

APPROACH 3: Hybrid Modular Monolith (Recommended)
├─ Timeline: 8 weeks
├─ Team size: 4 engineers
├─ Uptime: 99.9% (achievable)
├─ Scale limit: 100K+ concurrent users
├─ Operational complexity: Moderate
├─ Cost: $1.5K/month
└─ Strength: Best balance for your goals
```

**Timeline:** 15-20 minutes per review/tradeoff

---

### Phase 3: Risk Assessment

**Command:**
```bash
orchestrator:risk path=./architecture goal="Launch production MVP"
```

**Orchestrator Output:**

```
RISK ASSESSMENT — E-Commerce MVP

🔴 CRITICAL RISKS (Must fix before launch)
1. Single database instance (SPOF)
   - Impact: Complete outage if DB fails
   - Probability: Low but catastrophic
   - Mitigation: Add PostgreSQL read replicas + failover
   - Effort: 4 hours
   
2. No API rate limiting
   - Impact: DDoS vulnerability, cost spike with Stripe
   - Probability: Medium (attackers will try)
   - Mitigation: Add Redis rate limiter, CloudFlare DDoS protection
   - Effort: 2 hours

3. Hardcoded secrets in config
   - Impact: Credentials exposed in GitHub
   - Probability: High if not automated
   - Mitigation: Use environment variables + secrets manager
   - Effort: 1 hour

🟡 HIGH RISKS (Should fix before launch)
1. No monitoring/alerting
   - Impact: Won't know when system fails
   - Mitigation: Setup CloudWatch + PagerDuty
   - Effort: 3 hours
   
2. No backup strategy
   - Impact: Data loss = business failure
   - Mitigation: Daily automated backups + restore testing
   - Effort: 2 hours

3. Payment processing error handling
   - Impact: Customer confused about order status
   - Mitigation: Implement webhook verification + retry logic
   - Effort: 4 hours

🟢 MEDIUM RISKS (Fix in v1.1)
1. No caching strategy
   - Impact: Database load increases with users
   - Mitigation: Add Redis for product catalog cache
   
2. No CDN for static assets
   - Impact: Slower page loads globally
   - Mitigation: Use CloudFront for images

Remediation Timeline:
├─ CRITICAL: Before launch (8 hours total)
├─ HIGH: Before launch (7 hours total)
└─ MEDIUM: After launch v1.0 (2 weeks)

Launch Readiness: 70% → 95% after critical/high fixes
```

**Timeline:** 15-20 minutes

---

### Phase 4: Context Building (For Existing Projects)

**Command:**
```bash
orchestrator:context path=./ecommerce-repo
```

**Scenario:** Team member joins existing e-commerce project, needs rapid understanding.

**Orchestrator Generates:**

```
docs/context/
├─ architecture.md
│  └─ C4 System Diagram
│     ├─ Level 1: E-Commerce System (Users, Products, Orders)
│     ├─ Level 2: Frontend (React), Backend (FastAPI), Database (PostgreSQL)
│     ├─ Level 3: Services (ProductService, OrderService, StripeService)
│     └─ Level 4: Implementation details (files, classes, functions)
│
├─ tech-stack.md
│  ├─ Backend: FastAPI 0.95.1 (async, OpenAPI)
│  ├─ Frontend: React 18.2, TypeScript 5.0
│  ├─ Database: PostgreSQL 15, Redis 7
│  ├─ Infrastructure: Docker, GitHub Actions, ECS on AWS
│  ├─ Observability: CloudWatch, Sentry
│  └─ External APIs: Stripe, SendGrid
│
├─ context.json
│  ├─ Project metadata (name, description, created date)
│  ├─ Technology breakdown by layer
│  ├─ Module dependency graph
│  ├─ External API integrations
│  ├─ Database schema summary
│  └─ Deployment topology
│
└─ design.html
   └─ Interactive 4-tab visualization
      ├─ Tab 1: Architecture (C4 diagram)
      ├─ Tab 2: Tech Stack (technologies by layer)
      ├─ Tab 3: File Tree (project structure)
      └─ Tab 4: API Endpoints (all REST endpoints)
```

**Timeline:** 10-15 minutes

---

### Phase 5: PR Management & Launch

**Command:**
```bash
orchestrator:pr title="feat: e-commerce MVP" \
  description="Implements complete e-commerce platform with product catalog, 
  shopping cart, Stripe checkout, order management, and email notifications"
```

**Orchestrator Creates:**

```
GitHub Pull Request

Title: feat: e-commerce MVP
Branch: feature/ecommerce-mvp → main

Description:
## E-Commerce MVP Implementation

### What's Included
- ✓ Product catalog with search + filtering
- ✓ Shopping cart with persistence
- ✓ Stripe payment integration
- ✓ Order management (create, view, cancel)
- ✓ Email notifications (order confirmation, shipping)
- ✓ Admin dashboard
- ✓ 95%+ test coverage

### Architecture
[Architecture diagram]

### Deployment
- Docker containerization ✓
- GitHub Actions CI/CD ✓
- ECS deployment ready ✓
- Database migrations ✓

### Test Results
- Unit tests: 245 passing
- Integration tests: 89 passing
- Coverage: 94.3%

### Performance
- API response time: < 200ms (p95)
- Frontend load time: < 2s (3G)

### Security
- OWASP Top 10 audit: PASSED
- Secrets management: PASSED
- SQL injection protection: PASSED

### Reviewers
- @architect-review (architecture, design)
- @security-review (security audit)
- @frontend-review (UI/UX)

### Deployment Checklist
- [ ] Code review approved
- [ ] Security review passed
- [ ] Performance baseline established
- [ ] Database migrations tested
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured
```

**Timeline:** 5 minutes

---

## 🎯 Scenario 2: Legacy System Modernization

### Phase 0: Requirements Analysis

**Situation:** 5-year-old monolithic Java Spring Boot application. New features blocked by architecture. Decision: migrate to microservices.

**Command:**
```bash
orchestrator:plan "Modernize 5-year legacy monolith. Currently handles 100K users but 
architecture prevents scaling. Goal: split into microservices, reduce deployment time from 
4 hours to 15 minutes, enable independent team scaling."
```

**Orchestrator Questions:**
- "How many users currently active?"
- "What's the database size?"
- "Can we have downtime during migration?"
- "What's the business priority: speed or feature parity?"
- "Timeline and budget constraints?"

**Output:** Migration requirements with phased roadmap

---

### Phase 1: Planning Modernization

**Command:**
```bash
orchestrator:build path=./modernization-plan.md
```

Orchestrator chains:
1. **architect:refactor** → Assess current state, design target microservices
2. **implementer:full** → Build first microservice (User Service)
3. **quality:review** → Validate migration approach
4. **quality:audit** → Identify tech debt to address during migration

---

### Phase 2: Design Review

**Command:**
```bash
orchestrator:review path=./migration-design.md context="Monolith → Microservices"
```

**Orchestrator Concerns:**
- ❌ Is event-driven architecture feasible?
- ❌ How to handle distributed transactions?
- ❌ Database strategy (shared vs separate DBs)?
- ❌ Communication between services (sync vs async)?

---

### Phase 3: Tradeoff Analysis

**Command:**
```bash
orchestrator:tradeoff goal="Migrate to microservices within 3 months with zero downtime"
```

**Orchestrator Presents:**

```
APPROACH 1: Big Bang Rewrite (Risky)
├─ Timeline: 8 weeks
├─ Risk: Everything fails together, can't rollback
└─ Not recommended

APPROACH 2: Strangler Pattern (Safe)
├─ Timeline: 12 weeks
├─ Strategy: Wrap monolith, extract services one by one
├─ Rollback: Always possible
└─ Recommended
```

---

### Phase 4: Risk Assessment

**Command:**
```bash
orchestrator:risk path=./strangler-architecture
```

**Key Risks:**
- 🔴 Two codebases to maintain simultaneously
- 🔴 Distributed transaction complexity
- 🟡 Database migration challenges
- 🟡 Operational complexity increase

---

## 📊 SDLC Chaining Examples

### Full Feature Lifecycle (2-3 days)

```
Day 1 Morning:
  orchestrator:plan → Requirements clarified

Day 1 Afternoon:
  architect:design → System design approved
  orchestrator:review → Design reviewed, risks identified

Day 2 Morning:
  orchestrator:build → Code generated
  implementer:full → Tests + docs generated

Day 2 Afternoon:
  quality:review → Validation against requirements
  quality:audit → Code quality checked

Day 3 Morning:
  orchestrator:pr → PR submitted
  [Human review + approval]
  
Day 3 Afternoon:
  [Merge + Deploy]
  orchestrator:context → Document new system state
```

### Incident Response Workflow (1-4 hours)

```
Minute 0: Incident detected
  quality:diagnose problem="Orders endpoint returning 500 errors"

Minute 15: Root cause analysis
  quality:debug stack_trace="NullPointerException at OrderService:42"

Minute 30: Quick fix implemented
  implementer:build path=./fix.md
  implementer:test path=./tests

Minute 45: Deploy fix
  orchestrator:pr title="fix: null order handling"
  
Minute 90: Validation
  quality:perf → Verify fix improves performance
  orchestrator:risk → Assess risk of fix

Minute 120: Monitor
  [Observability + monitoring dashboard]
```

---

## 🔧 Real-World Pattern Examples

### Pattern 1: Assume Nothing (Think Before Coding)

```bash
# ❌ Wrong: Direct to build
orchestrator:build path=./requirements.md

# ✅ Right: Always start with plan
orchestrator:plan "unclear requirements"
# Clarifies scope, constraints, assumptions
# Then orchestrator:build with solid foundation
```

### Pattern 2: Stakeholder Review Loop

```bash
orchestrator:plan
  ↓ [Share task breakdown with stakeholders]
orchestrator:review (design review)
  ↓ [Share architecture with stakeholders]
orchestrator:tradeoff (present options)
  ↓ [Stakeholders choose approach]
orchestrator:risk (present risks)
  ↓ [Stakeholders accept/mitigate]
orchestrator:build (proceed with confidence)
```

### Pattern 3: Migration Safety

```bash
orchestrator:context (understand current system)
  ↓
architect:refactor (design migration)
  ↓
orchestrator:risk (identify risks)
  ↓
orchestrator:tradeoff (compare approaches)
  ↓
architect:refactor (create detailed plan)
  ↓
implementer:full (Phase 1 execution)
  ↓
quality:review (validate phase 1)
  ↓
[Repeat for Phase 2, 3, etc.]
```

---

## ✨ Pro Tips for Orchestrator Functions

1. **Always start with plan** — Even "obvious" requirements have hidden assumptions
2. **Use tradeoff early** — Compare approaches before committing to one
3. **Review before building** — Design feedback is cheaper than code rewrites
4. **Risk assessment is free insurance** — 20 minutes identifying risks saves weeks of firefighting
5. **Context building is onboarding gold** — New team members understand system in 15 minutes vs 3 days
6. **Chain functions for momentum** — plan → design → build → review → pr in sequence
7. **Stakeholder involvement at each phase** — Reduces rework and surprises
8. **Document assumptions explicitly** — Plan output becomes requirements artifact

