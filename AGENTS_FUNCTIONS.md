# Agent Functions Reference — v3.0

**Version:** 3.0  
**Date:** June 3, 2026  
**Total Agents:** 5 (4 role-based + 1 utility)  
**Total Functions:** 28 callable functions

---

## Quick Function Index

| Agent | Prefix | Functions | Use When |
|-------|--------|-----------|----------|
| **Orchestrator** | `orchestrator` | ideate, solve, plan, build, review, tradeoff, risk, context, pr | Start new project, refine vague ideas, solve bottlenecks, or generate full-stack system |
| **Architect** | `architect` | design, refactor, frontend, schema, api, a11y | Design system topology, DB schema, API contracts |
| **Implementer** | `implementer` | build, test, doc, pipeline, docker, iac, full | Write code, generate tests, auto-document, deploy |
| **Quality** | `quality` | review, audit, security, perf, debug, report | Validate PRs, scan codebase, find bugs, optimize |
| **Business Analyst** | `ba` | report, parse | Parse JIRA backlog, generate filterable reports |

---

## Linear Execution Pipeline

```
Requirement
    ↓
orchestrator:ideate (OPTIONAL—for vague ideas)
    ├─ Refine concept
    ├─ Expert feedback
    └─ Output: detailed spec + project plan
    ↓
orchestrator:plan (Parse requirements → tasks)
    ↓
architect:design (System topology, API, schema)
    ↓
orchestrator:solve (OPTIONAL—for bottleneck solving)
    ├─ Analyze constraints
    ├─ Multi-dimensional solutions
    └─ Output: recommendations + roadmap
    ↓
implementer:full (Build + test + doc)
    ↓
quality:review
    ↓
orchestrator:pr
```

---

# ORCHESTRATOR AGENT (9 functions)

**Prefix:** `orchestrator`

### orchestrator:ideate
Transform vague ideas into validated project plans with expert feedback. Uses ideation_engine module for systematic refinement, expert_panel_generator for domain-specific challenges. Outputs: idea-spec.md, project-plan.json, raid-analysis.md, project-plan.csv.

### orchestrator:solve
Solve design bottlenecks with multi-dimensional, prescriptive solutions. Uses design_solver module for diagnosis and trade-off analysis, expert_panel_generator for architecture challenges. Generates: solutions.md, recommendation.md, comparison-table.csv, implementation-roadmap.json.

### orchestrator:plan
Parse requirements in 5 formats, break into tasks. Outputs: requirements.md, task-breakdown.json, execution-order.txt

### orchestrator:build
Full-stack generation (architect → implementer → quality end-to-end). Outputs: complete system artifacts.

### orchestrator:context
Build project context (architecture.md, tech-stack.md, context.json, design.html visualization).

### orchestrator:pr
Package deliverables and create GitHub PR with comprehensive description.

### orchestrator:review
Strategic architecture review with challenge questions and 5-year assessment.

### orchestrator:tradeoff
Generate 3-option complexity analysis with ranked recommendation.

### orchestrator:risk
Risk assessment (operational, data, scaling, team, integration) with mitigation strategies.

---

# ARCHITECT AGENT (6 functions)

**Prefix:** `architect`

### architect:design
Design complete system topology (C4, API contract, DB schema, deployment infrastructure).

### architect:refactor
Brownfield refactoring (assess current state, diagnose, phased migration + rollback procedures).

### architect:frontend
Component architecture design (React, TypeScript, state management, composition patterns).

### architect:schema
Database DDL with indexes, constraints, migrations, partitioning strategy.

### architect:api
REST API contracts (OpenAPI 3.0 spec, request/response schemas, auth, rate limits).

### architect:a11y
Accessibility audit (WCAG 2.1 AA) with semantic HTML, ARIA, keyboard navigation.

---

# IMPLEMENTER AGENT (7 functions)

**Prefix:** `implementer`

### implementer:build
Generate production-ready code from architecture. Auto-detects tech stack, applies skill.

### implementer:test
Generate test suite (unit + integration + E2E, 95%+ coverage with business validation).

### implementer:doc
Code documentation (Javadoc/docstrings/JSDoc) + architecture + API reference + HTML site.

### implementer:pipeline
CI/CD pipeline generation (GitHub Actions, GitLab CI, Jenkins, CircleCI, Azure).

### implementer:docker
Dockerfile + docker-compose (multi-stage, health checks, security best practices).

### implementer:iac
Infrastructure as Code (Terraform, CloudFormation, Kubernetes manifests).

### implementer:full
**Complete lifecycle:** build → test → doc in single context (no context loss).

---

# QUALITY AGENT (6 functions)

**Prefix:** `quality`

### quality:review
PR validation against JIRA ACs, 6-category scoring, HTML report + PR comment.

### quality:audit
Full codebase audit (SOLID violations, duplication, complexity, tech debt roadmap).

### quality:security
OWASP Top 10 security audit (auth, injection, data protection, infrastructure).

### quality:perf
Performance bottleneck analysis with before/after code and benchmark data.

### quality:debug
Root cause analysis from stack trace, failure mechanism explanation, regression tests.

### quality:report
**NEW (v3.0):** Unified synthesis of all 5 quality functions into single HTML report.

### quality:batch-review
**NEW (v3.0):** Batch PR review for multiple PRs in one session.  
**Input:** `reviews.json` array with PR configs (pr, ticket, context, business-justification, review-scope, success-criteria)  
**Output:** `quality-batch-report.html` — single self-contained file with fixed sidebar tabs + summary dashboard  
**Usage:**
```
quality:batch-review from=./reviews.json
quality:batch-review from=./reviews.json output=./reports/batch-report.html
```
**What it does:** Runs quality:review for each PR sequentially, aggregates findings into priority matrix and score comparison, produces tabbed HTML report with Summary tab (aggregate stats, worst issues, merged verdict) and per-PR tabs (full review context, AC coverage, issues with before/after code, scorecard). Supports JSON export and Print/PDF.

### quality:diagnose
**NEW (v3.0):** Conversational problem solver — describe issue → get solutions.  
**Input:** Problem statement (required), code path (optional), verbose mode (optional)  
**Output:** Root cause analysis with proposed solutions, code examples, impact assessment  
**Usage:**
```
quality:diagnose problem="Orders taking 10 seconds to load"
quality:diagnose problem="API returning 500 errors randomly" path=./src verbose=true
quality:diagnose problem="Database queries timing out"
```
**What it does:** Conversational investigation across code, database, configuration, logs. Asks clarifying questions (when, frequency, impact), traces code paths, checks for N+1 queries, missing indexes, configuration bottlenecks, exception handling gaps. Identifies root causes (critical/high/medium/low) and proposes specific fixes with file:line references and implementation examples. Covers: code patterns, database queries/indexes, connection pools/cache, exception handling, resource usage, concurrency issues.

---

## Documentation Agent (`documentation`)

### documentation:readme path=./project include-contributing=true
```
**What it does:** Writes a comprehensive README with project summary, prerequisites, local setup, running tests, project structure, key concepts, and troubleshooting guide. Target: new developers onboard in < 5 minutes.

### documentation:diagrams
**Prefix:** `documentation` | **Function:** `diagrams`  
**Input:** Architecture context (architecture.md or codebase)  
**Output:** Mermaid diagrams (C4, sequence, dependency, dataflow)  
**Usage:**
```
documentation:diagrams path=./src diagram-type=c4
documentation:diagrams path=./src diagram-type=sequence,dependency
```
**What it does:** Generates workflow and architecture diagrams in Mermaid format: system context (C4 level 1), container diagrams, sequence flows for critical paths, and module dependency graphs.

### documentation:html
**Prefix:** `documentation` | **Function:** `html`  
**Input:** All prior artifacts (code-docs, API spec, architecture.md, README)  
**Output:** Single-file, self-contained interactive HTML documentation site  
**Usage:**
```
documentation:html path=./docs output=site.html
```
**What it does:** Assembles a searchable, responsive HTML documentation portal with dark mode, full-text search across all docs, syntax highlighting, and embedded Mermaid diagrams. No external CDN dependencies.

---

## Architecture Agent (`architecture`)

### architecture:design
**Prefix:** `architecture` | **Function:** `design`  
**Input:** Requirements + scale targets  
**Output:** System topology diagram, API contract (OpenAPI), DB schema, caching strategy, deployment plan, code stubs  
**Usage:**
```
architecture:design requirements="e-commerce platform" scale="1M users, 1K req/sec"
architecture:design requirements="real-time notification system" 
```
**What it does:** Greenfield system design from scratch. Creates C4 system topology, designs API contracts, generates database schema with indexes, defines caching layers (Redis/Memcached), plans deployment topology (Docker/K8s), and produces skeleton implementation stubs (models, routes, repositories).

### architecture:refactor
**Prefix:** `architecture` | **Function:** `refactor`  
**Input:** Existing codebase + pain points  
**Output:** Current-state diagram, target-state diagram, phased refactoring roadmap (5-7 phases), before/after code, migration guide, rollback strategies  
**Usage:**
```
architecture:refactor path=./monolith goal="split into microservices"
architecture:refactor path=./legacy pain-points="N+1 queries, tight coupling"
```
**What it does:** Brownfield refactoring. Assesses existing architecture, diagnoses problems, designs desired target state, creates a phased roadmap with zero-downtime migrations, provides step-by-step migration guide for each phase, and documents rollback procedures for safety.

### architecture:schema
**Prefix:** `architecture` | **Function:** `schema`  
**Input:** Data model requirements  
**Output:** SQL DDL (CREATE TABLE, indexes, constraints), migration scripts  
**Usage:**
```
architecture:schema requirements="users, orders, inventory" db=postgres
architecture:schema requirements="events, aggregations" db=mysql
```
**What it does:** Database schema design only. Generates SQL DDL (CREATE TABLE, PRIMARY KEY, FOREIGN KEY, UNIQUE constraints), index recommendations (B-tree, hash, full-text), migration scripts (ALTER TABLE, ADD INDEX), and partitioning strategy for scale.

### architecture:api
**Prefix:** `architecture` | **Function:** `api`  
**Input:** Service requirements (endpoints, operations)  
**Output:** OpenAPI 3.0 spec, request/response schemas, examples  
**Usage:**
```
architecture:api requirements="user CRUD, login, profile" format=json
architecture:api requirements="order creation, payment, tracking"
```
**What it does:** API contract design only. Creates OpenAPI 3.0 specification with all endpoints, request/response schema definitions, status codes, authentication methods, rate limiting definitions, and cURL/JavaScript/Python examples.

---

## Business Analyst Agent (`ba`)

### ba:report
**Prefix:** `ba` | **Function:** `report`  
**Input:** JIRA JSON or CSV export file  
**Output:** Single-file interactive HTML backlog report  
**Usage:**
```
ba:report file=jira-export.json
ba:report file=jira-export.csv output=backlog.html
```
**What it does:** Parses JIRA export (auto-detects JSON vs CSV), normalizes all fields, generates filterable/sortable HTML report with stats header (total issues, by status, by priority, story points), filter bar (status, priority, assignee, sprint, type), sortable table, row expansion, and export-to-CSV option.

### ba:parse
**Prefix:** `ba` | **Function:** `parse`  
**Input:** JIRA JSON or CSV file  
**Output:** Normalized JSON with all issues and fields  
**Usage:**
```
ba:parse file=jira-export.json output=parsed.json
ba:parse file=jira-export.csv output=issues.json
```
**What it does:** Parses JIRA file only (JSON or CSV), auto-detects format, normalizes fields (handles Cloud vs Server naming differences), and outputs a clean JSON array of issue objects ready for further processing (no HTML generation).

---

## Implementation Agent (`implementation`)

### implementation:build
**Prefix:** `implementation` | **Function:** `build`  
**Input:** Requirements (free text / JIRA ticket / file)  
**Output:** Production-ready source code in detected tech stack  
**Usage:**
```
implementation:build requirement="add login with OAuth2"
implementation:build jira=AUTH-123
implementation:build file=requirements.md
```
**What it does:** Builds feature code only. Detects tech stack, applies matching skill (Java/Python/React/SQL), generates complete, tested, production-ready code with proper error handling, logging, and security practices. Skips tests and docs.

### implementation:test
**Prefix:** `implementation` | **Function:** `test`  
**Input:** Source code files + test requirements  
**Output:** Test suite (unit + integration) with >= 95% coverage  
**Usage:**
```
implementation:test files=src/auth.ts requirement="login flow"
implementation:test file=src/payments.py 
```
**What it does:** Generates test suite only. Skips building code, applies `test_skill` with framework-specific patterns (JUnit5, pytest, Jest), generates unit + integration tests, auto-documents with JSDoc/docstrings, targets >= 95% coverage.

### implementation:doc
**Prefix:** `implementation` | **Function:** `doc`  
**Input:** Existing source code  
**Output:** Javadoc/docstrings/JSDoc + API reference  
**Usage:**
```
implementation:doc path=./src
implementation:doc path=./src format=javadoc
```
**What it does:** Generates documentation only. Scans existing code (skips building new code, skips tests), applies `code_documentation_skill` to add 100% method/function documentation in language-appropriate format, generates API reference.

### implementation:full
**Prefix:** `implementation` | **Function:** `full`  
**Input:** Requirements (free text / JIRA / file)  
**Output:** Code + tests (95%+ coverage) + documentation + GitHub PR  
**Usage:**
```
implementation:full requirement="add user profile feature"
implementation:full jira=FEATURE-456
```
**What it does:** Full lifecycle. Gathers requirements, builds code, generates tests, auto-documents everything, creates GitHub PR with summary. This is the default when no function is specified.

---

## Code Review Agent (`review`)

### review:full
**Prefix:** `review` | **Function:** `full`  
**Input:** JIRA ticket number (e.g., PROJ-123)  
**Output:** Interactive HTML report + PR comment  
**Usage:**
```
review:full ticket=PROJ-123 pr=main
review:full jira-key=AUTH-789
```
**What it does:** Full code review. Fetches JIRA acceptance criteria, validates PR against requirements, scores code quality (6 categories), analyzes test coverage, checks documentation, generates composite grade (A-F), produces interactive HTML report and posts MR/PR comment.

### review:quality
**Prefix:** `review` | **Function:** `quality`  
**Input:** Code diff / PR files  
**Output:** Quality scorecard (6 categories)  
**Usage:**
```
review:quality files=src/auth.ts,src/models.ts
review:quality branch=feature/oauth
```
**What it does:** Code quality review only. Skips JIRA lookup, scores code against 6 categories: design patterns, SOLID principles, security, performance, readability, and test organization. Returns scorecard without HTML or PR comment.

### review:report
**Prefix:** `review` | **Function:** `report`  
**Input:** Prior review analysis data  
**Output:** Interactive HTML report (6 sections + metrics)  
**Usage:**
```
review:report analysis=review-data.json
```
**What it does:** Renders HTML report from existing review analysis. Takes structured review data and produces a browsable HTML report with findings, scores, and recommendations.

### review:comment
**Prefix:** `review` | **Function:** `comment`  
**Input:** Prior review analysis + PR context  
**Output:** Formatted PR/MR comment  
**Usage:**
```
review:comment analysis=review-data.json pr=main 
```
**What it does:** Posts formatted code review summary to MR/PR comment via MCP. Takes structured review data and writes a human-readable summary comment suitable for team discussion.

---

## Security Auditor Agent (`security`)

### security:audit
**Prefix:** `security` | **Function:** `audit`  
**Input:** Source code + config + infrastructure  
**Output:** OWASP-aligned severity-ranked vulnerability report with secure code examples  
**Usage:**
```
security:audit path=./src include-infra=true
security:audit path=./backend threat-model="payment processing"
```
**What it does:** Full security audit (8 phases). Audits authentication, authorization, injection risks (SQL/NoSQL/command), API security, data protection, infrastructure/secrets, and builds attack chains showing how vulnerabilities combine. Produces ranked report with remediation code.

### security:authn
**Prefix:** `security` | **Function:** `authn`  
**Input:** Auth-related source code (session, credential, OAuth config)  
**Output:** Authentication + authorization audit report  
**Usage:**
```
security:authn path=./src/auth
security:authn path=./middleware 
```
**What it does:** Authentication & Authorization audit only. Examines identity verification (OAuth, SAML, basic auth), credential storage (hashing, salting, key management), session management (tokens, cookies, CSRF), MFA implementation, and access control enforcement.

### security:injection
**Prefix:** `security` | **Function:** `injection`  
**Input:** Source code (database, templates, shell calls)  
**Output:** Injection vulnerability list (SQL, NoSQL, command, template, LDAP, XXE)  
**Usage:**
```
security:injection path=./src files="*.sql,*.js"
security:injection path=./api 
```
**What it does:** Injection risk scan only. Identifies SQL injection, NoSQL injection, command injection, template injection, LDAP injection, and XXE risks. Provides secure code examples for each finding.

### security:report
**Prefix:** `security` | **Function:** `report`  
**Input:** Security audit data  
**Output:** Severity-ranked vulnerability report with fixes  
**Usage:**
```
security:report audit-data=security-findings.json output=report.md
```
**What it does:** Formats security findings into severity-ranked report (OWASP-mapped). Groups by severity (critical, high, medium, low), provides remediation code examples, deployment notes, and timeline recommendations.

---

## Codebase Auditor Agent (`audit`)

### audit:scan
**Prefix:** `audit` | **Function:** `scan`  
**Input:** Repository or directory path  
**Output:** Full audit report (all 8 phases) + roadmap  
**Usage:**
```
audit:scan path=./src
audit:scan path=./legacy deep-analysis=true
```
**What it does:** Full codebase audit (8 phases). Scans structure, reverse-engineers architecture, audits code quality (SOLID/patterns), finds duplicates, profiles for performance bottlenecks, measures complexity/maintainability, scores technical debt, and generates prioritized refactoring roadmap.

### audit:quality
**Prefix:** `audit` | **Function:** `quality`  
**Input:** Source code files  
**Output:** SOLID violations + design pattern audit  
**Usage:**
```
audit:quality path=./src exclude="test,vendor"
audit:quality path=./backend focus="domain models"
```
**What it does:** Code quality audit only. Scans for SOLID principle violations (single responsibility, open-closed, Liskov substitution, interface segregation, dependency inversion), checks for appropriate design patterns, and identifies missing abstractions.

### audit:perf
**Prefix:** `audit` | **Function:** `perf`  
**Input:** Source code (database queries, algorithms, I/O)  
**Output:** Performance bottleneck list (N+1, algorithms, memory, blocking I/O, rendering)  
**Usage:**
```
audit:perf path=./src focus="database queries"
audit:perf path=./frontend focus="rendering"
```
**What it does:** Performance bottleneck scan only. Identifies N+1 query patterns, inefficient algorithms, memory leaks, blocking I/O operations, and slow rendering patterns without running the code.

### audit:roadmap
**Prefix:** `audit` | **Function:** `roadmap`  
**Input:** Prior audit findings + technical debt scores  
**Output:** Prioritized, phased refactoring roadmap  
**Usage:**
```
audit:roadmap findings=audit-report.json
audit:roadmap findings=audit-report.json phases=5
```
**What it does:** Generates refactoring roadmap from audit findings. Prioritizes work by impact, effort, and risk. Creates 5-7 phases, each deliverable and deployable independently. Includes effort estimates and rollback strategies.

---

## Test Engineer Agent (`test`)

### test:generate
**Prefix:** `test` | **Function:** `generate`  
**Input:** Source code files (specify paths)  
**Output:** Test suite (unit + integration) >= 95% coverage  
**Usage:**
```
test:generate files=src/auth.ts,src/payments.ts
test:generate path=./src framework=jest
```
**What it does:** Generates test suite from source code. Applies framework-specific skill (JUnit5, pytest, Jest/Vitest), creates unit + integration tests, targets >= 95% coverage, includes edge cases and error scenarios, uses meaningful test names (givenXxx_whenYyy_thenZzz).

### test:jira
**Prefix:** `test` | **Function:** `jira`  
**Input:** JIRA ticket key (e.g., AUTH-123)  
**Output:** Test suite validating all acceptance criteria  
**Usage:**
```
test:jira ticket=AUTH-789
test:jira jira-key=FEATURE-456 framework=pytest
```
**What it does:** Generates tests from JIRA. Fetches ticket via MCP, extracts acceptance criteria, links code files, generates test cases covering each AC, validates 100% AC coverage, documents which test covers which AC.

### test:validate
**Prefix:** `test` | **Function:** `validate`  
**Input:** Test suite + requirements/ACs  
**Output:** Validation report (coverage %, missing ACs)  
**Usage:**
```
test:validate files=tests/** requirement=requirements.md
test:validate tests=tests/ jira=FEATURE-789
```
**What it does:** Validates existing tests against requirements. Checks test coverage percentage, verifies all acceptance criteria are tested, identifies gaps, and suggests additional test cases.

### test:coverage
**Prefix:** `test` | **Function:** `coverage`  
**Input:** Test suite + source code  
**Output:** Coverage gap report (missing paths, untested edge cases)  
**Usage:**
```
test:coverage path=./src tests=tests/
test:coverage path=./backend min-coverage=90
```
**What it does:** Analyzes test coverage. Reports code paths with insufficient test coverage, identifies edge cases not tested, suggests additional test scenarios, generates coverage by file/method.

---

## Performance Optimizer Agent (`perf`)

### perf:profile
**Prefix:** `perf` | **Function:** `profile`  
**Input:** Application code + performance baseline  
**Output:** Hot-path map, expensive operations list  
**Usage:**
```
perf:profile path=./src baseline="API latency 500ms"
perf:profile path=./backend focus="database layer"
```
**What it does:** Code profiling analysis. Identifies which functions consume most time/memory/CPU, maps hot paths, categorizes expensive operations (I/O, algorithm, memory), and estimates impact of each bottleneck.

### perf:optimize
**Prefix:** `perf` | **Function:** `optimize`  
**Input:** Bottleneck analysis + source code  
**Output:** Optimized code with before/after comparisons  
**Usage:**
```
perf:optimize bottlenecks=profile.json target-improvement="3x faster"
perf:optimize path=./src optimization="add caching layer"
```
**What it does:** Applies optimizations to code. Provides before/after side-by-side comparisons, implements caching, fixes N+1 queries, optimizes algorithms, reduces memory usage. Maintains functionality while improving performance.

### perf:benchmark
**Prefix:** `perf` | **Function:** `benchmark`  
**Input:** Application code + performance targets  
**Output:** Benchmark test suite (baseline + regression tests)  
**Usage:**
```
perf:benchmark path=./src target="API latency < 100ms"
perf:benchmark path=./backend 
```
**What it does:** Generates benchmark test suite. Creates baseline measurements, performance regression tests (alert if latency degrades), load tests (10x/100x expected load), and memory profiling tests.

### perf:monitor
**Prefix:** `perf` | **Function:** `monitor`  
**Input:** Optimized code + scale targets  
**Output:** Performance monitoring strategy + alerting rules  
**Usage:**
```
perf:monitor path=./src targets="p99 latency < 200ms, memory < 1GB"
perf:monitor application=api slo="99.9% uptime"
```
**What it does:** Designs performance monitoring. Defines SLI/SLO metrics, creates alerting rules (when to alert, escalation), designs dashboards, sets regression guardrails, and provides observability recommendations (logging, tracing, metrics).

---

## Production Debugger Agent (`debug`)

### debug:rca
**Prefix:** `debug` | **Function:** `rca`  
**Input:** Stack trace / error message + context  
**Output:** Root cause analysis report  
**Usage:**
```
debug:rca error="NullPointerException in AuthService line 45" 
debug:rca stacktrace=error.txt environment="production"
```
**What it does:** Root cause analysis. Takes error/stack trace, reads affected code, traces execution path, identifies the exact condition that triggers the failure (distinguishes symptom from root cause), surfaces similar vulnerabilities.

### debug:trace
**Prefix:** `debug` | **Function:** `trace`  
**Input:** Failure scenario + affected code  
**Output:** Execution path map + failure mechanism  
**Usage:**
```
debug:trace scenario="user hits 500 error when uploading file"
debug:trace code=src/upload.ts condition="file > 10MB"
```
**What it does:** Traces execution path through code during failure. Reads code line-by-line, maps execution flow, identifies exact line that causes failure, explains why it occurs under those specific conditions.

### debug:fix
**Prefix:** `debug` | **Function:** `fix`  
**Input:** Root cause + failure mechanism  
**Output:** Implemented fix + regression test suite  
**Usage:**
```
debug:fix root-cause="null check missing in OAuth token validation"
debug:fix issue="N+1 query in user profile loading"
```
**What it does:** Designs and implements bug fix. Proposes production-grade fix addressing root cause (not symptom), generates regression tests preventing recurrence, handles edge cases, provides deployment notes and rollback strategy.

### debug:edge
**Prefix:** `debug` | **Function:** `edge`  
**Input:** Known bug + root cause  
**Output:** List of similar edge cases + vulnerable code patterns  
**Usage:**
```
debug:edge bug="NullPointerException in token validation"
debug:edge root-cause="Missing null check on optional field"
```
**What it does:** Edge case discovery. Finds similar failure patterns in codebase, surfaces related vulnerabilities before they hit production, suggests defensive patterns to prevent recurrence elsewhere.

---

## Integration Agent (`integration`)

### integration:pipeline
**Prefix:** `integration` | **Function:** `pipeline`  
**Input:** Repository config + platform choice  
**Output:** CI/CD pipeline YAML (GitHub Actions / GitLab CI / Jenkins)  
**Usage:**
```
integration:pipeline repo=./  platform=github-actions
integration:pipeline repo=./ platform=gitlab-ci stages="test,build,deploy"
```
**What it does:** Generates CI/CD pipeline. Creates workflows/jobs for testing, building, semantic versioning, artifact publishing, and deployment. Supports GitHub Actions, GitLab CI, and Jenkins. Includes health checks and automated rollback.

### integration:docker
**Prefix:** `integration` | **Function:** `docker`  
**Input:** Application source + dependencies  
**Output:** Dockerfile + Docker Compose configuration  
**Usage:**
```
integration:docker path=./ language=node
integration:docker path=./backend language=java target-registry="gcr.io/myproject"
```
**What it does:** Generates Docker configuration. Creates optimized Dockerfile (multi-stage build for smaller images), Docker Compose for local development with services, and registry configuration for publishing.

### integration:iac
**Prefix:** `integration` | **Function:** `iac`  
**Input:** Deployment requirements + cloud provider  
**Output:** Infrastructure-as-Code manifests (Terraform / CloudFormation / K8s)  
**Usage:**
```
integration:iac provider=aws region=us-east-1 service="API server"
integration:iac provider=gcp services="API,database,cache" iac-tool=terraform
```
**What it does:** Generates IaC. Creates Terraform modules, CloudFormation templates, or Kubernetes YAML for reproducible infrastructure. Includes compute, networking, storage, database, and load balancing configuration.

### integration:monitor
**Prefix:** `integration` | **Function:** `monitor`  
**Input:** Service endpoints + SLO targets  
**Output:** Observability setup (logging, metrics, tracing, alerts)  
**Usage:**
```
integration:monitor service="api.example.com" slo="99.95% uptime, p99 < 100ms"
integration:monitor path=./src targets="memory < 1GB, errors < 0.1%"
```
**What it does:** Sets up observability. Configures logging (structured, centralized), metrics (Prometheus/Datadog), distributed tracing (Jaeger), and alerting rules. Defines SLI/SLO metrics and thresholds.

---

## Technical Lead Agent (`lead`)

### lead:review
**Prefix:** `lead` | **Function:** `review`  
**Input:** Proposed solution / architecture / decision  
**Output:** Strategic review with challenge questions + risk assessment  
**Usage:**
```
lead:review proposal="split monolith into microservices"
lead:review architecture=architecture.md focus="scalability"
```
**What it does:** Strategic review. Challenges assumptions, asks clarifying questions, identifies scaling/maintenance/team risks, assesses 5-year maintainability implications, and provides candid feedback on technical choices.

### lead:tradeoff
**Prefix:** `lead` | **Function:** `tradeoff`  
**Input:** Problem definition + constraints  
**Output:** 3-option tradeoff analysis with ranked recommendation  
**Usage:**
```
lead:tradeoff problem="real-time notifications" constraints="< 2 months, < 3 engineers"
lead:tradeoff requirement="database migration" options="online,offline,parallel"
```
**What it does:** Generates 3 solution options with explicit tradeoffs (simplicity, cost, scalability, team risk, timeline). Ranks options, recommends the pragmatic choice, documents reasoning for future context.

### lead:risk
**Prefix:** `lead` | **Function:** `risk`  
**Input:** Proposed solution  
**Output:** Risk assessment (scaling risk, maintenance risk, team capability gaps)  
**Usage:**
```
lead:risk solution="add real-time events via WebSocket"
lead:risk decision="migrate to serverless" team-experience="low"
```
**What it does:** Risk assessment. Identifies scaling bottlenecks, maintenance burden, team capability gaps, vendor lock-in, technical debt creation, and long-term evolution challenges. Stress-tests decisions against 5-year horizon.

### lead:plan
**Prefix:** `lead` | **Function:** `plan`  
**Input:** Approved strategy / recommendation  
**Output:** Phased execution plan with checkpoints  
**Usage:**
```
lead:plan strategy="refactor monolith into microservices" team-size=5
lead:plan recommendation="migrate to serverless" timeline="Q2-Q3"
```
**What it does:** Breaks strategy into shippable phases. Creates milestones, resource allocation, risk checkpoints, go/no-go decision points, and rollback plans for each phase.

---

## Senior Frontend Engineer Agent (`frontend`)

### frontend:component
**Prefix:** `frontend` | **Function:** `component`  
**Input:** Component spec + design system  
**Output:** React component(s) with TypeScript, accessibility, and tests  
**Usage:**
```
frontend:component spec="Button with loading state" framework=react
frontend:component spec="Form with validation" framework=react,tailwind a11y=wcag-aa
```
**What it does:** Generates production-grade React components. Creates TypeScript prop interfaces, handles loading/error/disabled/empty states, implements keyboard navigation, ARIA labels (WCAG 2.1 AA), responsive design, and RTL + axe-core tests.

### frontend:design
**Prefix:** `frontend` | **Function:** `design`  
**Input:** Feature requirements + design tokens  
**Output:** Component architecture + composition strategy  
**Usage:**
```
frontend:design feature="user profile page" design-system="Material UI"
frontend:design feature="checkout flow" components="FormField,Button,Card"
```
**What it does:** Component architecture design. Maps requirements to components, defines composition hierarchy, identifies reusable patterns, plans state management (props, Context, external store), and documents composition contracts.

### frontend:a11y
**Prefix:** `frontend` | **Function:** `a11y`  
**Input:** Existing component(s) + WCAG target  
**Output:** Accessibility audit + remediation code  
**Usage:**
```
frontend:a11y path=src/components/ target=wcag-2.1-aa
frontend:a11y component="Modal.tsx"
```
**What it does:** Accessibility audit (WCAG 2.1 AA compliance). Checks semantic HTML, ARIA labels, keyboard navigation, focus management, color contrast, heading hierarchy. Provides remediation code for each issue.

### frontend:test
**Prefix:** `frontend` | **Function:** `test`  
**Input:** Implemented component(s)  
**Output:** Jest/Vitest unit tests + RTL integration tests + axe accessibility tests  
**Usage:**
```
frontend:test files=src/components/Button.tsx framework=vitest
frontend:test path=src/components/ coverage-target=95
```
**What it does:** Component test suite. Writes unit tests (props, state, callbacks), integration tests (user interactions), accessibility tests (axe-core), edge cases, error states. Targets >= 95% coverage.

### frontend:story
**Prefix:** `frontend` | **Function:** `story`  
**Input:** Implemented component(s)  
**Output:** Storybook stories + prop tables + usage examples  
**Usage:**
```
frontend:story path=src/components/ 
frontend:story files=Button.tsx,Form.tsx
```
**What it does:** Generates Storybook stories. Creates interactive component previews, documents props with types and defaults, shows usage examples, edge cases, and design system integration.

---

## Autonomous Developer Agent (`autonomous`)

### autonomous:build
**Prefix:** `autonomous` | **Function:** `build`  
**Input:** `requirements.txt` file (plain text requirements)  
**Output:** Complete working system (DB + API + UI + tests + docs) + GitHub PR  
**Usage:**
```
autonomous:build file=requirements.txt
autonomous:build file=requirements.txt target-pr=origin/develop
```
**What it does:** Full-stack generation from scratch. Parses requirements, detects tech, generates database, backend API, frontend UI, tests (95%+ coverage), documentation, architecture context, and opens GitHub PR with summary.

### autonomous:context
**Prefix:** `autonomous` | **Function:** `context`  
**Input:** Project directory  
**Output:** context.json, architecture.md, tech-stack.md, design.html, knowledge graph  
**Usage:**
```
autonomous:context path=./project
autonomous:context path=./project include-knowledge-graph=true
```
**What it does:** Builds project context only. Scans codebase, extracts architecture, generates machine-readable context and knowledge graph, creates visual documentation. Useful for understanding existing projects before making changes.

### autonomous:pr
**Prefix:** `autonomous` | **Function:** `pr`  
**Input:** Generated artifacts (code, tests, docs, tasks)  
**Output:** GitHub PR with formatted summary  
**Usage:**
```
autonomous:pr artifacts=./output
autonomous:pr artifacts=./output target-branch=develop
```
**What it does:** Packages deliverables into GitHub PR. Takes generated code, tests, documentation, and task specs, creates a formatted PR with summary, acceptance criteria checklist, test results, and deployment notes.

---

## Quick Reference Table

| Agent | Functions | Short Prefix |
|-------|-----------|--------------|
| Documentation | code, context, diagrams, api, readme, html | `documentation` |
| Architecture | design, refactor, schema, api | `architecture` |
| Business Analyst | report, parse | `ba` |
| Implementation | build, test, doc, full | `implementation` |
| Code Review | full, quality, report, comment | `review` |
| Security | audit, authn, injection, report | `security` |
| Codebase Auditor | scan, quality, perf, roadmap | `audit` |
| Test Engineer | generate, jira, validate, coverage | `test` |
| Performance | profile, optimize, benchmark, monitor | `perf` |
| Production Debugger | rca, trace, fix, edge | `debug` |
| Integration | pipeline, docker, iac, monitor | `integration` |
| Technical Lead | review, tradeoff, risk, plan | `lead` |
| Senior Frontend | component, design, a11y, test, story | `frontend` |
| Autonomous Dev | build, context, pr | `autonomous` |

**Total:** 54 callable functions across 13 agents

---

## Usage Examples

### Example 1: Generate code + tests without docs
```
implementation:build requirement="add user authentication with OAuth"
implementation:test files=src/auth/** requirement="oauth-flow"
```

### Example 2: Full security audit + performance check
```
security:audit path=./backend
perf:profile path=./backend baseline="API < 200ms"
```

### Example 3: Complete documentation for existing project
```
documentation:context path=./my-project
documentation:code path=./my-project
documentation:api path=./my-project
documentation:html path=./my-project
```

### Example 4: Design new system from scratch
```
architecture:design requirements="e-commerce platform" scale="1M users"
test:generate path=./generated
documentation:diagrams path=./generated
autonomous:pr artifacts=./output
```

### Example 5: Debug production issue
```
debug:rca error="NullPointerException" stacktrace=error.log
debug:edge bug="null reference" 
debug:fix root-cause="missing null check"
```

---

**Last Updated:** June 3, 2026 | **Total Functions:** 54 | **Total Agents:** 13 | **Version:** 2.0
