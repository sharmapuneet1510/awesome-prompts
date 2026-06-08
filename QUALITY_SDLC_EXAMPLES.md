---
title: Quality Agent — SDLC Examples
description: Complete software development lifecycle examples showing quality functions in real-world scenarios
version: 1.0
---

# Quality Agent — SDLC Examples

**Role:** QA, Security & Performance | **Functions:** review, audit, security, perf, debug, report, batch-review, diagnose

Complete lifecycle examples showing how quality functions work together in validation and debugging phases.

---

## 📋 SDLC Lifecycle Overview

```
Phase 0: Code Review              → quality:review
Phase 1: Architecture Audit       → quality:audit
Phase 2: Security Assessment      → quality:security
Phase 3: Performance Analysis     → quality:perf
Phase 4: Debugging (if needed)    → quality:debug
Phase 5: Comprehensive Report     → quality:report
Phase 6: Batch Reviews            → quality:batch-review
Phase 7: Conversational Diagnosis → quality:diagnose
```

---

## 🎯 Scenario 1: Pull Request Code Review

### Phase 0: PR Validation

**Situation:** Team submits PR for OAuth2 authentication feature. Need comprehensive code review before merge.

**Command:**
```bash
quality:review pr=456 ticket=PROJ-123 context="OAuth2 implementation with Google + GitHub providers"
```

**Quality Output: 6-Phase Review Report**

```
PULL REQUEST CODE REVIEW — PR #456

┌─────────────────────────────────────────────────────┐
│ SCORE: 78/100 (GOOD)                               │
│ Verdict: APPROVE WITH MINOR CHANGES               │
└─────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════

PHASE 1: REQUIREMENT VALIDATION (vs JIRA AC)

✓ AC1: Support Google OAuth2 sign-in
  Status: SATISFIED
  Evidence: routes/oauth.py → @router.get("/auth/google")

✓ AC2: Support GitHub OAuth2 sign-in
  Status: SATISFIED
  Evidence: routes/oauth.py → @router.get("/auth/github")

✓ AC3: Store OAuth tokens securely
  Status: SATISFIED
  Evidence: models/oauth_token.py with encryption

❌ AC4: Email verification for new accounts
  Status: PARTIALLY MISSING
  Evidence: Not found in PR
  Impact: Users can bypass email verification via OAuth

⚠️  AC5: Rate limiting on token endpoint
  Status: INCOMPLETE
  Evidence: No rate limiter middleware
  Impact: Vulnerable to token stuffing attacks

Requirement Coverage: 80% (4/5 ACs fully satisfied)

═══════════════════════════════════════════════════════

PHASE 2: CODE QUALITY ASSESSMENT

Style & Convention Compliance: ✓ PASS
├─ PEP 8 followed (line length, naming)
├─ Docstrings present on all public methods
├─ Type hints throughout
└─ Imports properly organized

Complexity Analysis: ⚠️  WARNING
├─ oauth_handler.py cyclomatic complexity: 12 (too high)
│  Recommendation: Split into smaller functions
└─ Token refresh logic: Consider extracting to separate module

Code Duplication: ❌ ISSUE FOUND
├─ Token validation logic duplicated in 2 places
│  Line 42 (validate_google_token)
│  Line 89 (validate_github_token)
│  Recommendation: Extract to shared utility function

Error Handling: ✓ PASS
├─ All exception paths handled
├─ User-friendly error messages
└─ Logging at appropriate levels

Security Patterns: ⚠️  CAUTION
├─ ✓ Tokens hashed in database
├─ ✓ Sensitive data not logged
├─ ❌ MISSING: CSRF protection on OAuth callback
├─ ❌ MISSING: Token expiration validation
└─ ❌ MISSING: Redirect URI validation

Code Quality Score: 82/100

═══════════════════════════════════════════════════════

PHASE 3: TEST COVERAGE ANALYSIS

Coverage Metrics
├─ Line coverage: 89% (good)
├─ Branch coverage: 76% (acceptable)
├─ Function coverage: 100% (excellent)
└─ Overall: 88%

Missing Coverage: ⚠️  3 Critical Gaps

Gap 1: Google token refresh failure
├─ Scenario: Google returns 401 during refresh
├─ Current coverage: NOT TESTED
├─ Risk: Silent failure, user gets 500 error
├─ Test needed: test_google_token_refresh_failure

Gap 2: OAuth user merge (existing email)
├─ Scenario: User already has account with same email
├─ Current coverage: NOT TESTED
├─ Risk: Account conflict, duplicate users
├─ Test needed: test_oauth_email_collision_handling

Gap 3: CSRF attack on callback
├─ Scenario: State parameter tampered with
├─ Current coverage: NOT TESTED
├─ Risk: CSRF vulnerability
├─ Test needed: test_invalid_state_parameter_rejected

Test Quality Assessment
├─ Test naming: ✓ GOOD (descriptive, givenXxx_whenYyy)
├─ Assertions per test: ✓ GOOD (single responsibility)
├─ Mocking strategy: ✓ GOOD (OAuth provider mocked)
├─ Setup/teardown: ✓ GOOD (fixtures used)
└─ Integration tests: ⚠️  MISSING (only unit tests)

Test Coverage Score: 75/100

═══════════════════════════════════════════════════════

PHASE 4: DOCUMENTATION AUDIT

Inline Documentation: ✓ GOOD
├─ All public functions have docstrings
├─ Complex algorithms explained
└─ Parameter types documented

API Documentation: ⚠️  INCOMPLETE
├─ Missing: Example requests for OAuth endpoints
├─ Missing: Error response codes documented
├─ Missing: Token format explanation
└─ Action: Add examples to API.md

README: ⚠️  INCOMPLETE
├─ Missing: OAuth setup instructions
├─ Missing: Environment variables list
├─ Missing: Troubleshooting section
└─ Action: Add OAuth section to README

Architecture Documentation: ❌ MISSING
├─ No diagram showing OAuth flow
├─ No sequence diagram for token refresh
└─ Action: Add architecture.md with OAuth sequence

Documentation Score: 65/100

═══════════════════════════════════════════════════════

PHASE 5: SECURITY CHECK

OWASP Top 10 Assessment:

🔴 CRITICAL
├─ A03: Injection
│  Status: ✓ PASS (parameterized queries used)
├─ A05: Broken Authentication
│  Status: ⚠️  CAUTION (CSRF not protected)
└─ A06: Vulnerable & Outdated Components
   Status: ✓ PASS (dependencies updated)

🟡 HIGH
├─ A01: Broken Access Control
│  Status: ✓ PASS (OAuth scope validation)
├─ A07: Cross-Site Scripting (XSS)
│  Status: ✓ PASS (output encoded)
└─ A08: Software & Data Integrity Failures
   Status: ✓ PASS (dependencies verified)

🟢 MEDIUM
├─ A04: Insecure Design
│  Status: ⚠️  INCOMPLETE (no rate limiting)
└─ A02: Cryptographic Failures
   Status: ✓ PASS (tokens encrypted)

Secrets Scanning: ✓ PASS
├─ No hardcoded API keys
├─ No credentials in comments
└─ Environment variables used correctly

Dependency Scan: ✓ PASS
├─ No known vulnerabilities
├─ Latest versions of auth libraries
└─ Security patches applied

Security Score: 85/100

═══════════════════════════════════════════════════════

PHASE 6: SCORING & VERDICT

Weighted Scorecard:
├─ Requirements compliance:  80/100 × 40% =  32/40
├─ Code quality:            82/100 × 25% =  20/25
├─ Test coverage:           75/100 × 20% =  15/20
├─ Documentation:           65/100 × 10% =   6/10
└─ Security:                85/100 × 5%  =   4/5
                                          ────────
                           TOTAL SCORE: 77/100 (B+)

Verdict: ✅ APPROVE WITH MINOR CHANGES

Required Changes (Must fix before merge):
1. Add CSRF protection to OAuth callback
2. Add rate limiting to token endpoint
3. Add missing test coverage (3 critical gaps)
4. Fix code duplication in token validation
5. Add redirect URI validation

Optional Improvements (Can merge, fix in v1.1):
1. Reduce cyclomatic complexity in oauth_handler.py
2. Add architecture diagram to documentation
3. Add example requests to API documentation
4. Add troubleshooting to README

Estimated Fix Time: 2-3 hours

═══════════════════════════════════════════════════════

REVIEW SUMMARY

Strengths:
✓ Good requirement coverage (80%)
✓ Solid code quality overall
✓ Comprehensive error handling
✓ Security-conscious implementation
✓ Good test naming conventions

Areas for Improvement:
• CSRF protection gap (critical)
• Rate limiting missing (high)
• Code duplication in token logic
• Documentation incomplete
• Missing integration tests

Recommendations:
1. Fix critical security gaps first
2. Add missing tests for edge cases
3. Refactor duplicated token logic
4. Improve documentation before launch
5. Consider adding OAuth flow diagram

Next Steps:
→ Request changes in GitHub PR
→ Schedule follow-up review after fixes
→ Approve for merge once requirements met
```

**Timeline:** 20-30 minutes | **Output:** Detailed 6-phase report with actionable feedback

---

## 🎯 Scenario 2: Codebase Audit (Architecture & Tech Debt)

### Phase 1: Architecture Audit

**Situation:** 3-year-old codebase. Team feels slow, wants to understand what's holding them back.

**Command:**
```bash
quality:audit path=./backend
```

**Quality Output: Comprehensive Audit Report**

```
CODEBASE AUDIT — BACKEND

═══════════════════════════════════════════════════════

ARCHITECTURE ANALYSIS

Current Pattern: Layered Monolith
├─ Controllers (routes) → Services → DAOs → Database
├─ Total modules: 47
├─ Code lines: 12,500
├─ Test lines: 8,900
└─ Code-to-test ratio: 1.4:1 (good)

Strengths:
✓ Clear separation of concerns
✓ Dependency injection used properly
✓ Data access abstraction
✓ Good test coverage overall

Issues Identified:

❌ CRITICAL: User service tightly coupled to Order service
├─ User.java imports OrderService (line 42)
├─ OrderService imports UserService (line 15)
├─ Result: Circular dependency
├─ Impact: Hard to test independently
├─ Fix effort: 4 hours (extract shared interfaces)

❌ CRITICAL: Shared database prevents independent scaling
├─ All services read/write to same PostgreSQL instance
├─ Impossible to scale User service separately from Orders
├─ Impact: Cannot meet 10x growth requirement
├─ Fix effort: Microservices migration (3-4 weeks)

⚠️  HIGH: Admin module violates single responsibility
├─ AdminService handles: users, orders, products, reports
├─ Lines of code: 2,400
├─ Cyclomatic complexity: 34 (very high)
├─ Fix effort: Split into 4 separate modules

═══════════════════════════════════════════════════════

SOLID PRINCIPLES ASSESSMENT

Single Responsibility Principle: ❌ VIOLATED
├─ UserController handles: auth, profile, preferences, notifications
├─ ProductService handles: catalog, inventory, recommendations
└─ Fix effort: 6-8 hours (1-2 engineer days)

Open/Closed Principle: ⚠️  PARTIAL
├─ Adding new payment method requires modifying PaymentProcessor (not extensible)
├─ Adding new report type requires modifying ReportService
└─ Fix effort: 4-5 hours (introduce strategy pattern)

Liskov Substitution Principle: ✓ PASS
├─ Inheritance hierarchy is sound
└─ No violations detected

Interface Segregation Principle: ⚠️  PARTIAL
├─ UserService interface has 23 methods (too many)
├─ Clients only need 3-4 methods on average
├─ Fix effort: 2-3 hours (break into smaller interfaces)

Dependency Inversion Principle: ✓ PASS
├─ Dependencies injected, not hardcoded
└─ Using Spring DI properly

SOLID Score: 65/100

═══════════════════════════════════════════════════════

DUPLICATION ANALYSIS

Code Duplication: ⚠️  MODERATE

Duplication 1: Database query logic
├─ Same pagination logic in 5 services
├─ Pattern: skip + limit + order by
├─ Lines duplicated: 45 total
├─ Recommendation: Extract to QueryBuilder utility

Duplication 2: Validation rules
├─ Email validation in 3 places
├─ Password validation in 2 places
├─ Fix effort: 2 hours (extract to validators)

Duplication 3: Error responses
├─ Same error response format in 8 controllers
├─ Fix effort: 1 hour (create ErrorResponseDTO)

Total duplicated lines: 120 (0.9% of codebase)
Recommendation: Extract utilities (5-6 hours)

═══════════════════════════════════════════════════════

TECH DEBT SCORING

Issue Severity Breakdown:
├─ 🔴 Critical (must fix):     8 issues
├─ 🟡 High (should fix):       15 issues
├─ 🟢 Medium (nice to fix):    42 issues
└─ 🔵 Low (informational):     18 issues

Critical Issues:
1. Circular dependency (User ↔ Order)
2. Single database instance (scalability blocker)
3. Admin module complexity (38 CC)
4. Hardcoded configurations (11 instances)
5. No API versioning strategy
6. Missing database connection pooling
7. No distributed caching setup
8. Outdated dependencies (8 packages)

Tech Debt Score: 42/100 (HIGH)

═══════════════════════════════════════════════════════

REFACTORING PRIORITY ROADMAP

Phase 1 (1 week) — Quick Wins
├─ Upgrade dependencies (8 packages) — 2 hours
├─ Extract shared validation utilities — 2 hours
├─ Move hardcoded configs to properties — 3 hours
├─ Add database connection pooling — 1 hour
└─ Result: ~5% improvement, 8 hours effort

Phase 2 (2 weeks) — Architecture Improvements
├─ Break up circular dependency (User ↔ Order) — 4 hours
├─ Refactor Admin module into 4 modules — 12 hours
├─ Add API versioning — 6 hours
└─ Result: ~20% improvement, 22 hours effort

Phase 3 (3-4 weeks) — Scalability Overhaul
├─ Design microservices architecture — 16 hours
├─ Migrate to separate databases (strangler pattern) — 80 hours
├─ Setup message queue (Pulsar) — 16 hours
└─ Result: ~50% improvement, 112 hours effort

Phase 4 (Ongoing) — Continuous Improvement
├─ Maintain test coverage > 85%
├─ Keep cyclomatic complexity < 10
├─ Code reviews for adherence to principles
└─ Monthly refactoring sprints

═══════════════════════════════════════════════════════

MAINTAINABILITY INDEX: 68/100 (FAIR)

Readability:   ✓ GOOD (75/100)
Testability:   ✓ GOOD (80/100)
Complexity:    ⚠️  FAIR (55/100)
Consistency:   ✓ GOOD (70/100)
Duplication:   ✓ GOOD (85/100)

Recommendation: Schedule Phase 1 refactoring in next sprint
```

**Timeline:** 1-2 hours | **Output:** Detailed audit with roadmap

---

## 🎯 Scenario 3: Security Audit

### Phase 2: Security Assessment

**Command:**
```bash
quality:security path=./app compliance=SOC2,PCI-DSS
```

**Quality Output: Security Audit Report**

```
SECURITY AUDIT — APPLICATION

Compliance Targets: SOC 2, PCI-DSS

═══════════════════════════════════════════════════════

🔴 CRITICAL VULNERABILITIES (Fix immediately)

1. Hardcoded Database Credentials
├─ Location: config.properties line 23
├─ Issue: DB password hardcoded in source code
├─ Risk: Anyone with repo access = DB access
├─ Fix: Use environment variables or secrets manager
├─ Effort: 30 minutes
├─ Compliance impact: FAILS PCI-DSS 2.2.1

2. SQL Injection Vulnerability
├─ Location: routes/products.py line 145
├─ Issue: User input directly in SQL query
│  Current: query = f"SELECT * FROM products WHERE name = '{name}'"
│  Should: query = "SELECT * FROM products WHERE name = ?" with parameters
├─ Risk: Database compromise
├─ Fix: Use parameterized queries everywhere
├─ Effort: 3 hours
├─ Compliance impact: FAILS PCI-DSS 6.5.1

3. Missing HTTPS Enforcement
├─ Issue: Application serves over HTTP in production
├─ Risk: Man-in-the-middle attacks, credential theft
├─ Fix: Add HSTS headers, redirect HTTP → HTTPS
├─ Effort: 1 hour
├─ Compliance impact: FAILS PCI-DSS 4.1

4. Session Tokens in LocalStorage
├─ Issue: JWT tokens stored in browser localStorage
├─ Risk: XSS attack = token theft
├─ Fix: Use httpOnly, secure cookies instead
├─ Effort: 2 hours
├─ Compliance impact: FAILS PCI-DSS 6.5.10

🔴 SUBTOTAL: 4 critical issues = 6.5 hours to fix

═══════════════════════════════════════════════════════

🟡 HIGH VULNERABILITIES (Fix this week)

1. Weak Password Policy
├─ Current: Minimum 6 characters
├─ Risk: Easy to brute force
├─ Fix: Minimum 12 characters, complexity requirements
├─ Effort: 1 hour
├─ Compliance impact: FAILS SOC 2 (CC6.1)

2. No Rate Limiting on Login
├─ Issue: Unlimited login attempts
├─ Risk: Brute force attacks
├─ Fix: Add rate limiter (5 attempts/5 minutes)
├─ Effort: 2 hours
├─ Compliance impact: FAILS SOC 2 (CC7.2)

3. Passwords Visible in Logs
├─ Issue: Error logs contain user passwords
├─ Risk: Sensitive data exposure
├─ Fix: Sanitize logs, never log passwords
├─ Effort: 2 hours
├─ Compliance impact: FAILS PCI-DSS 3.4

4. No Audit Trail for Admin Actions
├─ Issue: Can't track who did what in admin panel
├─ Risk: Insider threats undetected
├─ Fix: Log all admin actions with user/timestamp
├─ Effort: 4 hours
├─ Compliance impact: FAILS SOC 2 (CC7.1)

5. Missing CORS Validation
├─ Issue: Accepts requests from any origin
├─ Risk: CSRF attacks possible
├─ Fix: Whitelist allowed origins
├─ Effort: 30 minutes
├─ Compliance impact: FAILS PCI-DSS 6.5.9

🟡 SUBTOTAL: 5 high issues = 9.5 hours to fix

═══════════════════════════════════════════════════════

🟢 MEDIUM VULNERABILITIES (Fix next month)

1. No API Key Rotation Policy — 1 hour
2. Missing CSP Headers — 30 minutes
3. No backup encryption — 2 hours
4. Database backups stored unencrypted — 1 hour
5. No secrets rotation schedule — 30 minutes

🟢 SUBTOTAL: 5 medium issues = 5 hours

═══════════════════════════════════════════════════════

REMEDIATION PLAN

Immediate (Before any deployment):
├─ Remove hardcoded secrets → Env vars — 30 min
├─ Fix SQL injection → Parameterized queries — 3 hours
├─ Enable HTTPS → HSTS headers — 1 hour
├─ Move tokens → httpOnly cookies — 2 hours
└─ Total: 6.5 hours

Week 1:
├─ Add password complexity — 1 hour
├─ Implement rate limiting — 2 hours
├─ Sanitize logs — 2 hours
├─ Add audit trail — 4 hours
├─ Fix CORS — 30 min
└─ Total: 9.5 hours

Month 1:
├─ Medium vulnerabilities (5 items) — 5 hours

═══════════════════════════════════════════════════════

COMPLIANCE STATUS

SOC 2 Readiness:
├─ CC1: Control Environment — 60% (need audit trail)
├─ CC6: Logical Access — 40% (need stronger auth)
├─ CC7: User Access — 30% (need logging)
├─ CC9: System Monitoring — 70% (good)
└─ Overall: 50% ready (need 15+ hours work)

PCI-DSS Readiness:
├─ Requirement 1: Network segmentation — 100%
├─ Requirement 2: Remove defaults — 80% (hardcoded secrets)
├─ Requirement 3: Data protection — 40% (encryption gaps)
├─ Requirement 4: Encryption in transit — 50% (HTTPS issue)
├─ Requirement 5: Anti-malware — 90%
├─ Requirement 6: Code review — 60%
├─ Requirement 7: Access control — 50%
├─ Requirement 8: Authentication — 40%
└─ Overall: 61% ready (need 20+ hours work)

═══════════════════════════════════════════════════════

NEXT STEPS

1. Fix critical vulnerabilities immediately (6.5 hours)
2. Schedule week-long security sprint (9.5 hours)
3. Plan monthly security reviews
4. Set up automated security scanning (SAST tool)
5. Schedule SOC 2 / PCI-DSS audit in 2 months
```

**Timeline:** 1-2 hours | **Output:** Detailed security findings + remediation roadmap

---

## 🎯 Scenario 4: Performance Analysis & Optimization

### Phase 3: Performance Optimization

**Command:**
```bash
quality:perf path=./backend baseline="500ms p95 response time" scale="1M users"
```

**Quality Output: Performance Analysis**

```
PERFORMANCE ANALYSIS & OPTIMIZATION

Current Baseline: 500ms p95 response time (product list endpoint)
Scale Target: 1M concurrent users
Current users: 100K

═══════════════════════════════════════════════════════

BOTTLENECK ANALYSIS

Where Is Time Spent?
├─ Database queries: 42% (210ms)
├─ Service logic: 30% (150ms)
├─ Network latency: 18% (90ms)
└─ Other: 10% (50ms)

Top Bottleneck: Database Queries (42%)

Query 1: GetProducts (145ms)
├─ Current: SELECT * FROM products (no index, no limit)
├─ Issue: Full table scan, fetches 50K products
├─ Optimization: Add index, pagination, caching
├─ Expected gain: 145ms → 5ms (29x faster!)

Query 2: GetUserOrders (40ms)
├─ Issue: N+1 pattern (1 query for user, 1 per order)
├─ Optimization: Use JOIN to fetch in single query
├─ Expected gain: 40ms → 3ms (13x faster)

Query 3: CheckInventory (25ms)
├─ Issue: No index on inventory.product_id
├─ Optimization: Add composite index
├─ Expected gain: 25ms → 2ms (12x faster)

═══════════════════════════════════════════════════════

OPTIMIZATION ROADMAP

Quick Wins (4 hours, 70% improvement)

Win 1: Add Database Index on products table
├─ Effort: 30 minutes
├─ Query: CreateIndex idx_products_category on products(category_id)
├─ Expected gain: 145ms → 5ms
└─ Savings: 140ms per request

Win 2: Implement JOIN to fix N+1 pattern
├─ Effort: 1 hour
├─ Query: SELECT * FROM orders JOIN order_items ON ... (single query)
├─ Expected gain: 40ms → 3ms
└─ Savings: 37ms per request

Win 3: Add Redis Caching for Products
├─ Effort: 1.5 hours
├─ Cache product list (60-minute TTL)
├─ Expected gain: 5ms → 0.5ms (database skip)
└─ Savings: 4.5ms per request

Win 4: Paginate Results (default 20 items)
├─ Effort: 30 minutes
├─ Limit to 20 items instead of 50K
├─ Expected gain: Data transfer 500KB → 10KB
└─ Savings: Network latency -50ms

Total expected gain: 500ms → 100ms (5x faster!) ✓

═══════════════════════════════════════════════════════

Medium-Term (2 weeks, additional 20% improvement)

Optimization 5: Implement Read Replicas
├─ Effort: 3 days infrastructure
├─ Benefit: Distribute read traffic
├─ Expected gain: 3ms → 1.5ms per query
└─ Result: 100ms → 85ms (additional 15% gain)

Optimization 6: Add CDN for Static Assets
├─ Effort: 2 hours setup
├─ Benefit: Serve images from edge locations
├─ Expected gain: Network latency -20ms globally
└─ Result: 85ms → 65ms (additional 20% gain)

═══════════════════════════════════════════════════════

Scalability Projection

Current System:
├─ Response time at 100K users: 500ms
├─ Response time at 1M users: 2000ms ❌ EXCEEDS TARGET
└─ Bottleneck: Single database instance

After Quick Wins:
├─ Response time at 100K users: 100ms ✓
├─ Response time at 1M users: 400ms ✓
└─ Headroom: 25% before hitting limits again

After Medium-Term:
├─ Response time at 1M users: 65ms ✓
└─ Headroom: 60% before hitting limits

Long-Term (1+ month): Database Sharding
├─ Split by region: EU, US, Asia
├─ Expected response: 20-30ms globally
└─ Scales to 10M+ users

═══════════════════════════════════════════════════════

IMPLEMENTATION PLAN

Day 1 (Indexes):
$ CREATE INDEX idx_products_category ON products(category_id);
$ CREATE INDEX idx_orders_user_id ON orders(user_id);
→ Result: 500ms → 300ms (40% improvement)

Day 2 (N+1 Fix):
// Before: 40 queries (1 user + 39 orders)
// After: 1 query with JOIN
→ Result: 300ms → 220ms (25% improvement)

Day 3 (Caching):
// Add Redis caching for products
redis.get("products:1") || db.query(...).then(redis.set)
→ Result: 220ms → 100ms (55% improvement)

Day 4 (Pagination):
// Limit to 20 items
SELECT * FROM products LIMIT 20 OFFSET ? 
→ Result: 100ms → 60ms (40% improvement)

═══════════════════════════════════════════════════════

DEPLOYMENT STRATEGY

Phase 1: Deploy indexes (no downtime)
└─ Verify with load test

Phase 2: Deploy N+1 fix
└─ Monitor for 24 hours

Phase 3: Enable Redis cache
└─ Gradual rollout (10% → 50% → 100%)

Phase 4: Pagination defaults
└─ Update frontend, monitor

Rollback: Instant if metrics degrade
```

**Timeline:** 1-2 hours | **Output:** Detailed performance analysis + optimization roadmap

---

## 🎯 Scenario 5: Production Bug Debugging

### Phase 4: Root Cause Analysis

**Situation:** Production incident: OrderService returning NullPointerException.

**Command:**
```bash
quality:debug stack_trace="NullPointerException at OrderService.java:127 in getOrderTotal()" \
  path=./backend context="Production incident, 50 affected users"
```

**Quality Output: 5-Phase RCA**

```
PRODUCTION BUG DEBUG REPORT

Stack Trace:
Exception in thread "main": java.lang.NullPointerException
  at com.shop.OrderService.getOrderTotal(OrderService.java:127)
  at com.shop.OrderController.getOrder(OrderController.java:42)
  at java.lang.Thread.run(Thread.java:832)

═══════════════════════════════════════════════════════

PHASE 1: CODE FUNCTIONALITY ANALYSIS

OrderService.java:127
└─ Code: int total = order.getItems().stream()...

What should happen:
1. order variable is loaded from database
2. order.getItems() returns list of items
3. stream() iterates items
4. Calculate total price

What actually happened:
→ order.getItems() returned null
→ stream() called on null
→ NullPointerException

═══════════════════════════════════════════════════════

PHASE 2: ROOT CAUSE IDENTIFICATION

Root Cause: order.getItems() returns null instead of empty list

Why?
├─ Order.java has @OneToMany(mappedBy = "order")
│  └─ JPA defaults to null for empty collections (not empty list)
│
└─ When order has zero items:
   ├─ Expected: items = [] (empty list)
   ├─ Actual: items = null
   └─ Result: NullPointerException

Why didn't we catch this before?
├─ Test coverage gap: No test for "order with zero items"
├─ No defensive null check: order.getItems() assumed non-null
└─ Previous behavior: Older JPA version defaulted to empty list

Why now (not before)?
├─ MySQL 5.7 → 8.0 upgrade
├─ New JPA version (2.7 → 3.0)
├─ Changed default behavior for collections
├─ 5% of orders have zero items (hit today at scale)

═══════════════════════════════════════════════════════

PHASE 3: FAILURE EXPLANATION

Trigger Path:
User calls: GET /orders/{orderId}
  → OrderController.getOrder(orderId)
  → OrderService.getOrderTotal(order)
  → order.getItems().stream() ← CRASH HERE

Why it affects 50 users:
├─ Only affects orders with zero items
├─ Large morning sales → 5% of orders = 50 affected users
└─ Users can't view their order history

Impact:
├─ Severity: CRITICAL (users can't access orders)
├─ Blast radius: 50 users (but could grow as traffic increases)
├─ Duration: 2 hours until fix deployed
└─ Revenue impact: ~$500 (lost repeat orders from affected users)

═══════════════════════════════════════════════════════

PHASE 4: EDGE CASE IDENTIFICATION

Related Edge Cases:

Case 1: Order with zero items (current issue)
├─ Trigger: order.getItems() == null
├─ Impact: CRITICAL
└─ Fix: Defensive null check

Case 2: Order with null total
├─ Trigger: order.total == null in database
├─ Impact: HIGH
└─ Fix: Add NOT NULL constraint

Case 3: Concurrent order modification
├─ Trigger: Order deleted between getOrder() and getOrderTotal()
├─ Impact: MEDIUM
└─ Fix: Transaction isolation level

Case 4: Database timeout during item fetch
├─ Trigger: Database slow, returns null instead of timeout
├─ Impact: MEDIUM
└─ Fix: Add timeout + proper error handling

═══════════════════════════════════════════════════════

PHASE 5: PRODUCTION-READY FIX

Immediate Fix (Deploy now, 5 minutes):

// FIX 1: Defensive null check
@Override
public int getOrderTotal(Order order) {
    if (order == null) {
        throw new OrderNotFoundException("Order not found");
    }
    
    List<OrderItem> items = order.getItems();
    if (items == null) {
        items = Collections.emptyList(); // ← FIX
    }
    
    return items.stream()
        .mapToInt(item -> item.getPrice() * item.getQuantity())
        .sum();
}

Root Cause Fix (Deploy in v1.1, 2 hours):

// FIX 2: Configure JPA to use empty list instead of null
@Entity
public class Order {
    @OneToMany(mappedBy = "order", fetch = FetchType.LAZY)
    private List<OrderItem> items = new ArrayList<>(); // ← Initialize
}

Permanent Prevention:

// FIX 3: Add defensive checks in base class
public abstract class BaseEntity {
    protected <T> List<T> safe(List<T> list) {
        return list == null ? Collections.emptyList() : list;
    }
}

// FIX 4: Add test coverage
@Test
public void test_getOrderTotal_zeroItems() {
    Order order = new Order();
    order.setItems(null); // Simulates null condition
    
    int total = service.getOrderTotal(order);
    
    assertEquals(0, total);
}

═══════════════════════════════════════════════════════

FIX DEPLOYMENT PLAN

Stage 1: Hotfix (Now, 5 minutes)
├─ Deploy defensive null check
├─ Monitor error logs (should drop to 0)
└─ Affected users can now access orders

Stage 2: Root Cause Fix (Today, 2 hours)
├─ Update JPA configuration
├─ Redeploy with permanent fix
└─ Remove hotfix code

Stage 3: Test Coverage (Today, 1 hour)
├─ Add test for "order with null items"
├─ Add test for "concurrent order access"
└─ CI/CD prevents future regression

Stage 4: Root Cause Prevention (Week 1)
├─ Audit similar null-checks across codebase
├─ Update database constraints (NOT NULL)
├─ Add defensive checks in base classes

═══════════════════════════════════════════════════════

INCIDENT SUMMARY

Problem: NullPointerException in OrderService
Root Cause: JPA returning null for empty collections (version upgrade)
Impact: 50 users unable to view orders
Fix Time: 5 minutes (hotfix) + 2 hours (permanent)
Prevention: Test coverage + defensive checks

Lessons Learned:
1. Test edge cases (empty collections, null values)
2. Add defensive null checks in service layer
3. Mock dependencies in tests (JPA collections)
4. Document version-specific behavior changes
5. Have hotfix deployment process ready

Follow-up Actions:
✓ Deploy hotfix (5 min)
✓ Deploy permanent fix (2 hours)
✓ Add test coverage (1 hour)
✓ Audit similar patterns (4 hours)
✓ Post-incident review (30 minutes)
```

**Timeline:** 30-45 minutes | **Output:** 5-phase RCA with fix + prevention

---

## ✨ Pro Tips for Quality Functions

1. **Review before building** — Catch issues early
2. **Audit yearly** — Find tech debt accumulation
3. **Security audit quarterly** — Compliance + protection
4. **Perf test before scale** — Avoid surprises at 10x users
5. **Debug systematically** — Root cause first, fix second
6. **Use batch-review** — Faster than individual reviews
7. **Document lessons learned** — Prevent repeat incidents
8. **Quality is everyone's job** — Not just QA team

