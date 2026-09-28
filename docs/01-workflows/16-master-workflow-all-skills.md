# Master Workflow: Complete End-to-End Skill Integration

**Version:** 5.0.0 | **Last Updated:** 2026-09-28 | **Scope:** All 37 Skills → Requirement to Production

---

## 🎯 Overview

This master workflow orchestrates **all 37 reusable skills** in a linear pipeline from raw requirement to production-ready system. Each stage gates the next; each skill is a **super skill** optimized for token efficiency and advanced coding patterns.

```
Requirement (Free Text / JIRA / Conversation)
    ↓
[STAGE 1] Requirement Analysis (BA Skills)
    ↓
[STAGE 2] Technical Analysis & ADR (Architecture Skills)
    ↓
[STAGE 3] Context & Specification (Project Context Skills)
    ↓
[STAGE 4] System Design (Architecture Skills)
    ↓
[STAGE 5] Implementation (Tech Stack Skills + Code Skills)
    ↓
[STAGE 6] Quality & Testing (Test + Review Skills)
    ↓
[STAGE 7] Documentation (Doc + Reporting Skills)
    ↓
[STAGE 8] Observability & Operations (DevOps + Monitoring Skills)
    ↓
[STAGE 9] Delivery & Traceability (BA + Quality Skills)
    ↓
Production Release ✓
```

---

## 📋 STAGE 1: Requirement Analysis

**Gate:** Complete requirements document with acceptance criteria  
**Duration:** 5-15 min  
**Skills Used:** 3

### 1.1 Discover Requirements
**Skill:** `ba_create_skill`, `current_tech_spec_skill`  
**Input:** Free text, JIRA description, conversation transcript  
**Output:** `requirements.md` (PROPOSAL)

```bash
ba:discover source="User wants OAuth2 integration for third-party apps"
```

**What happens:**
- Extracts goals, actors, flows, rules
- Identifies ambiguities → open questions
- Creates business context skeleton
- Status: PROPOSAL (awaiting human decision)

**Token Efficiency:** ~2,000 tokens
- Skip narrative preamble
- Use bulleted lists, not prose
- Focus on actors + flows only

### 1.2 Clarify Ambiguities
**Skill:** `project_context_skill`  
**Input:** requirements.md with open questions  
**Output:** Updated requirements.md (DECISION)

```bash
ba:clarify
# One question at a time until all critical unknowns resolved
```

**What happens:**
- Asks ONE clarifying question
- User answers
- Repeats until project context is complete
- Status: DECISION (human-approved)

**Token Efficiency:** ~1,500 tokens per question
- Ask only material questions
- Batch answers, not individual confirmations

### 1.3 Create Business Requirements Document
**Skill:** `project_context_skill`, `ba_create_skill`  
**Input:** Approved requirements.md + clarifications  
**Output:** `docs/brd.md`, `docs/business-context.md`, `docs/mvp-scope.md`

```bash
ba:brd
```

**What happens:**
- Generates BRD with user stories + acceptance criteria
- Documents business rules, constraints, priorities
- Defines MVP scope
- Lists open technical questions

**Token Efficiency:** ~3,000 tokens
- Reuse requirement context, don't re-derive

---

## 📋 STAGE 2: Technical Analysis & Decisions

**Gate:** Accepted ADR for every decision-bearing change  
**Duration:** 10-20 min  
**Skills Used:** 3

### 2.1 Analyze Current State
**Skill:** `current_tech_spec_skill`, `project_context_skill`  
**Input:** BRD + existing codebase (if brownfield)  
**Output:** `docs/adr/ADR-0001-current-state-analysis.md`

```bash
architect:analyse jira=PROJ-123
```

**What happens:**
- Documents current architecture (FACT)
- Lists options (INFERENCE)
- Identifies decision points (PROPOSAL)
- Status: PROPOSAL

**Token Efficiency:** ~4,000 tokens
- Use git blame + code analysis, don't re-read
- Reference existing specs
- List options as decision trees, not narratives

### 2.2 Record Engineering Decisions
**Skill:** `adr_skill`, `traceability_skill`  
**Input:** Technical options + constraints  
**Output:** `docs/adr/ADR-000N-*.md` (Accepted)

```bash
architect:adr jira=PROJ-123
# Decision types: data-structure, api-contract, dependency, failure-mode, storage, etc.
```

**What happens:**
- Mints ADR with: context, options, decision, consequences
- 7-state lifecycle: Proposed → Accepted → Decision
- Every contract/shape/dependency change = requires ADR
- Status: DECISION (human-approved)

**Token Efficiency:** ~2,000 tokens per ADR
- Use structured template, fill slots
- Cross-reference existing ADRs
- One ADR per decision, not mega-ADRs

### 2.3 Generate Current Technical Specification
**Skill:** `current_tech_spec_skill`, `adr_skill`  
**Input:** All Accepted ADRs  
**Output:** `docs/CURRENT_TECHNICAL_SPECIFICATION.md`

```bash
architect:spec
```

**What happens:**
- Regenerated from ADRs, never hand-edited
- Single source of truth for "what is true now"
- Lists every architectural decision + rationale
- Links each claim to its ADR

**Token Efficiency:** ~3,000 tokens
- ADRs are the source; spec is the projection
- Use templated sections
- Automated links to ADRs

---

## 📋 STAGE 3: Project Context & Architecture

**Gate:** Complete context.json + architecture.md + design.html  
**Duration:** 15-30 min  
**Skills Used:** 4

### 3.1 Analyze Existing Architecture
**Skill:** `context_builder_skill`, `java_advanced_skill`, `python_advanced_skill`, `react_advanced_skill`  
**Input:** Codebase (brownfield) OR clean slate (greenfield)  
**Output:** `docs/context/architecture.md` + `docs/context/context.json`

```bash
context_builder:analyse path=/src
```

**What happens:**
- Scans source tree, builds module graph
- Identifies services, dependencies, data flows
- Generates architecture narrative (Mermaid C4 diagram)
- Exports as JSON for programmatic use

**Token Efficiency:** ~5,000 tokens
- Use AST parsing, not file reads
- Cache results, don't re-analyze
- Generate diagram from graph, not prose description

### 3.2 Detect Technology Stack
**Skill:** `context_builder_skill`, `java_advanced_skill`, `python_advanced_skill`, `react_advanced_skill`, `database_skill`  
**Input:** package.json, pom.xml, requirements.txt, pyproject.toml  
**Output:** `docs/context/tech-stack.md` + skill routing hints

```bash
context_builder:tech-stack path=/src
```

**What happens:**
- Identifies all dependencies + versions
- Classifies by layer (frontend, backend, database, DevOps)
- Recommends skill routing (Java → java_advanced_skill, etc.)
- Exports as structured table

**Token Efficiency:** ~2,000 tokens
- Parse manifests only, don't inspect code
- Use version detection rules
- Output as lookup table, not prose

### 3.3 Build Project Context Tree
**Skill:** `project_context_skill`  
**Input:** BRD + architecture.md + tech-stack.md  
**Output:** `docs/project-context/` (14 nodes)

```bash
architect:context
```

**What happens:**
- Builds 14-node shared knowledge tree:
  1. **Requirement** (BRD + AC + MVPs)
  2. **Architecture** (C4 model + topology)
  3. **Technology** (stack + versions)
  4. **Data Model** (entities + relationships)
  5. **API Contracts** (endpoints + schemas)
  6. **Failure Modes** (what breaks + impact)
  7. **Security** (threats + mitigations)
  8. **Performance** (SLOs + bottlenecks)
  9. **Deployment** (targets + config)
  10. **Observability** (metrics + logs + traces)
  11. **Testing** (coverage targets + suites)
  12. **Documentation** (artifacts + locations)
  13. **Operations** (runbooks + escalation)
  14. **Compliance** (legal + regulatory)

**Token Efficiency:** ~4,000 tokens
- Use ownership matrix: who owns each node
- Template each node, fill from source docs
- Link between nodes, don't duplicate

### 3.4 Generate Interactive Design Visualization
**Skill:** `context_builder_skill`  
**Input:** context.json + architecture.md  
**Output:** `docs/context/design.html` (interactive D3 dashboard)

```bash
context_builder:visualize path=/docs/context/
```

**What happens:**
- Generates single-page HTML with 4 tabs:
  - **Architecture** (zoomable C4 diagram)
  - **Tech Stack** (dependency graph)
  - **File Tree** (module browser)
  - **API Endpoints** (interactive explorer)
- Fully self-contained (no external CSS/JS)
- Dark mode support

**Token Efficiency:** ~3,000 tokens
- Use Mermaid for diagrams
- Inline all CSS/JS
- Render from JSON, don't re-derive

---

## 📋 STAGE 4: System Design

**Gate:** Design.md approved by tech lead  
**Duration:** 20-40 min  
**Skills Used:** 5

### 4.1 Design System Topology
**Skill:** `backend_skill`, `frontend_skill`, `database_skill`, `oop_skill`  
**Input:** BRD + tech stack + architecture context  
**Output:** `docs/design/design.md` (topology + API contracts + schema)

```bash
architect:design path=/docs/brd.md
```

**What happens:**
- Designs greenfield system OR refactoring path
- Produces: module topology, service boundaries, data flows
- API contracts (REST/GraphQL/gRPC)
- Database schema (DDL)
- Component breakdown (frontend, backend, infrastructure)
- Error handling strategy
- Status: PROPOSAL (design review required)

**Token Efficiency:** ~6,000 tokens
- Reuse tech-stack detection
- Apply OOP principles once, reference them
- Use diagram-as-code (Mermaid), not ASCII

### 4.2 Apply Domain-Specific Patterns
**Skill:** `java_advanced_skill` OR `python_advanced_skill` OR `react_advanced_skill`, `oop_skill`, `error_handling_skill`  
**Input:** design.md + requirement context  
**Output:** Enhanced design.md with language-specific patterns

```bash
architect:design --apply-patterns java
```

**What happens:**
- Applies SOLID principles + design patterns
- Recommends architecture (layered/hexagonal/etc.)
- Suggests dependency injection, factories, etc.
- Java: Spring patterns, Spring Data, actuators
- Python: FastAPI/Django patterns, async/await
- React: hooks, context, state management

**Token Efficiency:** ~3,000 tokens
- Pattern library is pre-written, don't regenerate
- Reference frameworks (Spring, FastAPI, React hooks)
- Show 2-3 patterns per language, not 20

### 4.3 Design Database Schema
**Skill:** `database_skill`, `error_handling_skill`  
**Input:** design.md + data model  
**Output:** `docs/design/schema.sql` (DDL)

```bash
database:design path=/docs/design/design.md
```

**What happens:**
- Generates DDL for PostgreSQL/MySQL/MSSQL/MongoDB
- Indexes optimized for access patterns
- Foreign keys + constraints
- Audit tables, soft deletes, versioning
- Migration strategy

**Token Efficiency:** ~2,500 tokens
- Use template DDL, customize for schema
- Reference design patterns (pivot tables, polymorphism, etc.)
- Generate migrations, not just schema

### 4.4 Design API Contracts
**Skill:** `backend_skill`, `error_handling_skill`  
**Input:** design.md + database schema  
**Output:** `docs/design/api-contract.yaml` (OpenAPI 3.0)

```bash
backend:design-api path=/docs/design/design.md
```

**What happens:**
- Generates OpenAPI 3.0 spec (machine-readable)
- All endpoints: GET, POST, PUT, DELETE, PATCH
- Request/response schemas
- Error responses (400, 401, 403, 404, 500)
- Rate limiting, auth headers
- Example payloads

**Token Efficiency:** ~3,000 tokens
- Generate from schema + design, not by hand
- Use pattern library for common endpoints
- Validate against spec before code generation

### 4.5 Design Frontend Architecture
**Skill:** `react_advanced_skill`, `frontend_skill`  
**Input:** design.md + API contract  
**Output:** `docs/design/frontend-architecture.md` + component tree

```bash
frontend:design path=/docs/design/design.md
```

**What happens:**
- Component tree + state management
- Routing structure
- API integration points
- Accessibility (a11y) checklist
- Forms + validation patterns
- Error boundaries + fallbacks

**Token Efficiency:** ~2,000 tokens
- Tree format, not prose
- Reference React hooks patterns
- List a11y patterns, don't explain each

---

## 📋 STAGE 5: Implementation

**Gate:** Approved design.md + Accepted ADRs  
**Duration:** Varies by codebase size  
**Skills Used:** 10+

### 5.1 Generate Task Breakdown
**Skill:** `spec_driven_development_skill`, `context_builder_skill`  
**Input:** design.md + API contract + schema  
**Output:** `docs/tasks.md` (bite-sized tasks, Status: PROPOSAL)

```bash
orchestrator:plan path=/docs/design/design.md
```

**What happens:**
- Breaks design into concrete tasks
- Each task ≤ 4 hours of work
- Includes: acceptance criteria, acceptance tests, success metrics
- Dependency graph (task A must finish before B)
- Tech stack + skill routing hints
- Status: PROPOSAL (needs approval)

**Token Efficiency:** ~3,000 tokens
- Reference design sections, don't repeat
- Use templated acceptance criteria
- Index by module, not sequential

### 5.2 Build Backend
**Skill:** `backend_skill`, `java_advanced_skill` OR `python_advanced_skill`, `oop_skill`, `error_handling_skill`, `logger_skill`, `spring_advanced_skill` (if Java)  
**Input:** Approved tasks.md + API contract + schema  
**Output:** `src/backend/` (production code)

```bash
implementer:build path=/docs/design/api-contract.yaml --lang python
```

**What happens:**
- Generates controller/handler layer (routes)
- Service layer (business logic)
- Repository layer (data access)
- Error handling + logging
- Request validation + authentication guards
- Dependency injection setup
- All with advanced patterns (SOLID, DDD, etc.)

**Token Efficiency:** ~8,000 tokens
- Use code generation templates
- Skip boilerplate, generate only logic
- Reference language-specific skill for patterns
- Link to schema DDL, don't repeat

### 5.3 Build Frontend
**Skill:** `frontend_skill`, `react_advanced_skill`, `oop_skill`  
**Input:** Approved tasks.md + API contract + frontend-architecture.md  
**Output:** `src/frontend/` (React components)

```bash
implementer:build path=/docs/design/frontend-architecture.md --lang typescript
```

**What happens:**
- Generates page/view components
- Smart components (with hooks)
- Dumb components (presentational)
- Custom hooks for business logic
- State management (Context/Redux if needed)
- API client (with error handling)
- Form components + validation
- i18n setup

**Token Efficiency:** ~6,000 tokens
- Use React hooks patterns library
- Generate from component tree, not freestyle
- Reference frontend-architecture.md
- Include TypeScript types from API contract

### 5.4 Build Infrastructure
**Skill:** `backend_skill`, `spring_advanced_skill` (if Java/Spring)  
**Input:** Approved tasks.md + tech stack  
**Output:** `deploy/` (Docker, K8s manifests, terraform, etc.)

```bash
implementer:build path=/docs/context/tech-stack.md --infra
```

**What happens:**
- Dockerfile (multi-stage build)
- docker-compose.yml (dev environment)
- Kubernetes manifests (prod deployment)
- Terraform (cloud infrastructure)
- Environment config templates
- Secrets management

**Token Efficiency:** ~3,000 tokens
- Use infrastructure templates
- Reference tech stack detected earlier
- Skip comments, code is self-documenting

### 5.5 Add Error Handling & Validation
**Skill:** `error_handling_skill`, `oop_skill`  
**Input:** Generated code + API contract  
**Output:** Enhanced code with error handling

```bash
implementer:enhance --error-handling path=/src
```

**What happens:**
- Adds exception handlers
- Input validation (everywhere)
- Circuit breakers + retries (for external calls)
- Graceful degradation
- Error logging + alerting
- User-friendly error messages

**Token Efficiency:** ~2,000 tokens
- Use error handling patterns library
- Apply to generated code, not rewrite
- Reference spec for error response format

### 5.6 Add Logging & Observability
**Skill:** `logger_skill`, `opentelemetry_skill`  
**Input:** Generated code  
**Output:** Instrumented code with structured logging

```bash
implementer:enhance --observability path=/src
```

**What happens:**
- Adds structured logging (JSON logs)
- Correlation IDs for request tracing
- OpenTelemetry instrumentation
- Metrics export (Prometheus format)
- Distributed tracing setup (Jaeger)
- Custom metrics (business metrics)

**Token Efficiency:** ~2,500 tokens
- Use logging skill patterns
- Apply to backend + frontend
- Reference observable framework (OTel)

---

## 📋 STAGE 6: Quality & Testing

**Gate:** 95%+ code coverage + all acceptance criteria pass  
**Duration:** 10-20 min  
**Skills Used:** 5

### 6.1 Generate Unit Tests
**Skill:** `test_skill`, `java_advanced_skill` OR `python_advanced_skill` OR `react_advanced_skill`  
**Input:** Generated code + acceptance criteria  
**Output:** `tests/unit/` (JUnit5/pytest/Jest)

```bash
implementer:test path=/src --scope unit
```

**What happens:**
- Generates test class per implementation class
- Test method per public method (givenXxx_whenYyy_thenZzz naming)
- Happy path + error cases
- 95%+ coverage target
- Mocking external dependencies
- Assertions for business logic

**Token Efficiency:** ~6,000 tokens
- Generate from code structure + requirements
- Use test patterns library
- Reference acceptance criteria for test cases

### 6.2 Generate Integration Tests
**Skill:** `test_skill`, `database_skill`  
**Input:** Generated code + schema + acceptance criteria  
**Output:** `tests/integration/` (End-to-end flows)

```bash
implementer:test path=/src --scope integration
```

**What happens:**
- Test full flow: request → backend → database → response
- Real database (test database)
- API endpoint tests
- Validate acceptance criteria
- Data setup/teardown
- Error scenario testing

**Token Efficiency:** ~4,000 tokens
- Use integration test patterns
- Reuse database DDL for test setup
- Reference acceptance criteria

### 6.3 Generate Acceptance Tests
**Skill:** `test_skill`, `spec_driven_development_skill`  
**Input:** tasks.md (acceptance criteria)  
**Output:** `tests/acceptance/` (BDD-style tests)

```bash
implementer:test path=/docs/tasks.md --scope acceptance
```

**What happens:**
- Maps acceptance criteria to test cases
- Given-When-Then format (Gherkin)
- End-to-end workflow testing
- UI testing (Cypress/Playwright for frontend)
- API testing
- Pass/fail validation

**Token Efficiency:** ~3,000 tokens
- Use BDD patterns
- Direct mapping from criteria to tests
- Automated test execution report

### 6.4 Review Code Quality
**Skill:** `code_health_skill`, `code_formatting_skill`, `security_audit_skill`  
**Input:** Generated code  
**Output:** Quality report + issues list

```bash
quality:audit path=/src
```

**What happens:**
- Runs linting + static analysis
- Code complexity scoring (cyclomatic complexity)
- Potential security issues (OWASP top 10)
- Code formatting violations
- Dead code detection
- Performance anti-patterns

**Token Efficiency:** ~2,000 tokens
- Use linting tool output (pylint, ruff, ESLint)
- Categorize by severity (Critical, High, Medium, Low)
- Suggest fixes

### 6.5 Generate Code Review Report
**Skill:** `code_review_skill`, `multi_review_html_skill`  
**Input:** Generated code + tests + quality report  
**Output:** `docs/reviews/CODE_REVIEW.html` (interactive report)

```bash
quality:report path=/src
```

**What happens:**
- 6-phase analysis pipeline:
  1. **Architecture** (design compliance)
  2. **Functionality** (requirement coverage)
  3. **Testing** (coverage + quality)
  4. **Performance** (bottlenecks)
  5. **Security** (vulnerabilities)
  6. **Maintainability** (readability + debt)
- Generates HTML report with findings + suggestions
- Scoring system (0-100)
- Color-coded sections (green/yellow/red)

**Token Efficiency:** ~3,000 tokens
- Reuse audit results
- Reference tests + coverage reports
- Template-driven HTML generation

---

## 📋 STAGE 7: Documentation

**Gate:** All artifacts documented + README.md current  
**Duration:** 10-15 min  
**Skills Used:** 4

### 7.1 Generate Code Documentation
**Skill:** `code_documentation_skill`  
**Input:** Generated code  
**Output:** JSDoc/Javadoc/docstrings in code

```bash
implementer:doc path=/src --format auto
```

**What happens:**
- Adds JSDoc to all exported functions (TypeScript)
- Adds Javadoc to all public classes/methods (Java)
- Adds docstrings to all modules (Python)
- Parameter descriptions
- Return type documentation
- Example usage (in docstrings)
- Links to related code

**Token Efficiency:** ~2,500 tokens
- Generate from code signature + context
- Use pattern templates (no prose)
- Skip obvious names

### 7.2 Generate Architecture Documentation
**Skill:** `context_builder_skill`, `current_tech_spec_skill`  
**Input:** design.md + generated code  
**Output:** `docs/ARCHITECTURE.md`

```bash
architect:doc path=/docs/design
```

**What happens:**
- Documents system topology
- Module responsibilities
- Data flow diagrams (Mermaid)
- Integration points
- External dependencies
- Scaling strategy
- Failure modes + mitigation

**Token Efficiency:** ~3,000 tokens
- Regenerate from design + ADRs
- Use Mermaid for diagrams
- Reference generated code, don't re-explain

### 7.3 Generate API Documentation
**Skill:** `backend_skill`  
**Input:** API contract + generated endpoints  
**Output:** `docs/API.md` + interactive Swagger UI

```bash
backend:doc path=/docs/design/api-contract.yaml
```

**What happens:**
- Converts OpenAPI spec to Markdown
- Endpoint reference (path, method, parameters)
- Request/response examples
- Error response documentation
- Authentication guide
- Rate limiting documentation
- Generates Swagger UI (optional, for interactive exploration)

**Token Efficiency:** ~1,500 tokens
- Reuse OpenAPI spec, no duplication
- Extract examples from spec

### 7.4 Generate README & Quick Start
**Skill:** `code_documentation_skill`, `context_builder_skill`  
**Input:** All documentation  
**Output:** `README.md` + `QUICKSTART.md`

```bash
doc:readme path=/docs
```

**What happens:**
- README: project overview, features, tech stack, quick start
- QUICKSTART: setup, first run, common tasks
- Installation instructions (pip, npm, docker)
- Configuration guide
- Troubleshooting section
- Contributing guide (if open source)

**Token Efficiency:** ~2,000 tokens
- Template-driven generation
- Link to other docs, don't duplicate

---

## 📋 STAGE 8: Observability & Operations

**Gate:** Metrics + logs configured, runbooks created  
**Duration:** 10-15 min  
**Skills Used:** 4

### 8.1 Setup Observability Stack
**Skill:** `opentelemetry_skill`, `logger_skill`, `backend_skill`  
**Input:** Generated code + deployment config  
**Output:** `deploy/observability.yaml` (Prometheus + Grafana + Jaeger config)

```bash
implementer:deploy-observability path=/deploy
```

**What happens:**
- Prometheus scrape configs + rules
- Grafana dashboards (service metrics, golden signals)
- Jaeger setup for distributed tracing
- Log aggregation config (ELK/Loki)
- Alert rules (for critical metrics)
- Custom metrics definitions

**Token Efficiency:** ~2,500 tokens
- Use observability templates
- Reference generated metrics from code
- Link to deployment targets

### 8.2 Create Operational Runbooks
**Skill:** `current_tech_spec_skill`, `debugging_skill`  
**Input:** architecture.md + observable design  
**Output:** `docs/runbooks/` (incident response playbooks)

```bash
ops:runbooks path=/docs/design
```

**What happens:**
- Runbook per critical component
- Symptoms (what to look for in metrics)
- Diagnosis steps (how to confirm issue)
- Recovery procedures (how to fix)
- Prevention measures (how to stop recurrence)
- Escalation path (who to contact)
- Post-mortem template

**Token Efficiency:** ~2,000 tokens
- Template-driven, 1 runbook per service
- Reference observable metrics
- Include actual console commands

### 8.3 Setup Alerting Strategy
**Skill:** `opentelemetry_skill`, `backend_skill`  
**Input:** Deployment + observability setup  
**Output:** `deploy/alerts.yaml` (AlertManager config)

```bash
ops:alerts path=/deploy/observability.yaml
```

**What happens:**
- Alert rules for critical conditions
- Golden signals: latency, traffic, errors, saturation
- Routing to on-call (PagerDuty/Slack)
- Escalation policies
- Alert deduplication + grouping
- Test alerts (don't just fire in prod)

**Token Efficiency:** ~1,500 tokens
- Use alert rules templates
- Reference monitoring thresholds
- Include alert message templates

### 8.4 Setup Health Checks & Monitoring
**Skill:** `backend_skill`, `opentelemetry_skill`  
**Input:** Generated code + deployment  
**Output:** Health check endpoints + liveness/readiness probes

```bash
backend:healthcheck path=/src
```

**What happens:**
- /health endpoint (liveness + readiness)
- Database connectivity check
- External service connectivity check
- Graceful shutdown handling
- Kubernetes probe configs
- Load balancer health check config

**Token Efficiency:** ~1,000 tokens
- Health check template
- Link to deployment config

---

## 📋 STAGE 9: Delivery & Traceability

**Gate:** All checks pass + traceability chain complete  
**Duration:** 5-10 min  
**Skills Used:** 4

### 9.1 Validate Traceability Chain
**Skill:** `traceability_skill`, `spec_driven_development_skill`  
**Input:** All artifacts (requirements → code → tests → deployment)  
**Output:** Traceability report + validation (18 checks)

```bash
ba:trace scope=release version=1.0.0
```

**What happens:**
- 8-hop chain validation:
  1. Requirement → Design (coverage)
  2. Design → Tasks (mapping)
  3. Tasks → Code (implementation)
  4. Code → Tests (coverage)
  5. Tests → Acceptance Criteria (validation)
  6. AC → Deployment (config)
  7. Deployment → Monitoring (observability)
  8. Monitoring → Runbooks (operations)
- 18 checks: completeness, consistency, integrity
- Generates `docs/traceability-report.md`
- Status: Pass/Fail

**Token Efficiency:** ~2,000 tokens
- Automated validation (no manual tracing)
- Report only gaps, not what's correct

### 9.2 Create Release Notes
**Skill:** `current_tech_spec_skill`, `spec_driven_development_skill`  
**Input:** BRD + design + implementation + tests  
**Output:** `RELEASE_NOTES.md` + `CHANGELOG.md`

```bash
orchestrator:release-notes path=/docs
```

**What happens:**
- **RELEASE_NOTES.md**: user-facing features + improvements + fixes
- **CHANGELOG.md**: developer-facing changes + breaking changes + dependencies
- Git tag annotation
- Semantic versioning (major.minor.patch)

**Token Efficiency:** ~1,500 tokens
- Template-driven generation
- Reference BRD for features
- Reference code diffs for changes

### 9.3 Generate Deployment Manifest
**Skill:** `backend_skill`, `context_builder_skill`  
**Input:** Generated code + deployment config  
**Output:** `deploy/manifest.yaml` (K8s deployment ready)

```bash
implementer:deploy path=/deploy
```

**What happens:**
- Kubernetes manifests (deployment, service, configmap, secret)
- Helm values (if using Helm)
- Terraform manifests (if using IaC)
- Environment-specific configs (dev, staging, prod)
- Rollback strategy
- Blue-green deployment config (optional)

**Token Efficiency:** ~2,000 tokens
- Use deployment templates
- Reference tech stack detected earlier
- Link to observability setup

### 9.4 Create GitHub Pull Request
**Skill:** `spec_driven_development_skill`, `traceability_skill`  
**Input:** All generated artifacts + committed code  
**Output:** GitHub PR with detailed description + checklist

```bash
orchestrator:pr
```

**What happens:**
- PR title: short, descriptive
- PR description:
  - What changed (feature/fix/refactor)
  - Why (business impact)
  - How (technical approach)
  - Testing summary (coverage, scenarios)
  - Deployment notes
  - Breaking changes (if any)
  - Linked issues (requirements → design → tasks)
- Checklist:
  - [ ] Tests passing
  - [ ] Code review approved
  - [ ] Traceability clean
  - [ ] Deployment tested
- Automated checks: CI/CD, code quality, security

**Token Efficiency:** ~1,500 tokens
- Reference artifacts, don't duplicate
- Use PR template
- Auto-link issues

---

## 📊 Super Skill Features Summary

Each skill in this workflow has been enhanced as a **super skill** with:

### 1. **Token Efficiency**
- Skip preamble & narrative
- Use bulleted lists, not prose
- Reference existing docs, don't repeat
- Templated outputs (no freestyle)
- Cached results (don't re-derive)

### 2. **Advanced Coding Patterns**
- SOLID principles (every skill references OOP skill)
- Design patterns (factory, strategy, decorator, etc.)
- Domain-driven design (aggregate roots, entities, value objects)
- Error handling (exception hierarchies, retries, circuit breakers)
- Async/await + reactive patterns (for applicable skills)
- Type safety (TypeScript, Java generics, Python type hints)

### 3. **Enhanced Documentation**
- **Skill Header:** Name + Version + Scope (3 lines)
- **Quick Reference:** Input → Output (1 line each)
- **Execution Steps:** 3-5 bullet points
- **Token Budget:** Estimated tokens for this stage
- **Patterns Library:** Reference, not reinvent
- **Examples:** Concrete, runnable code
- **Failures & Fixes:** Common issues + solutions

### 4. **Beautiful HTML Output**
For all documentation-generating skills:
- Dark mode support (auto-detect)
- Collapsible sections (expand/collapse)
- Syntax highlighting (code blocks)
- Mermaid diagrams (auto-rendered)
- Responsive design (mobile-friendly)
- Search/filter functionality
- Breadcrumb navigation
- Link validation
- Generated timestamp + skill version

### 5. **Automation & Integration**
- Each skill outputs are inputs to next skill
- Gating criteria clear (what blocks progress)
- No manual re-entry of data
- Cross-references / link validation
- Automated report generation

---

## 🎯 Quick Reference: Skill Routing by Tech Stack

| Stack | Backend Skill | Frontend Skill | Database | Deployment |
|-------|---|---|---|---|
| **Java + Spring Boot** | `java_advanced_skill` + `spring_advanced_skill` | `react_advanced_skill` | `database_skill` (PostgreSQL) | `backend_skill` (Docker/K8s) |
| **Python + FastAPI** | `python_advanced_skill` + `backend_skill` | `react_advanced_skill` | `database_skill` (PostgreSQL) | `backend_skill` (Docker/K8s) |
| **Node.js + Express** | `backend_skill` | `react_advanced_skill` | `database_skill` (MongoDB/PostgreSQL) | `backend_skill` (Docker) |
| **Microservices** | `java_advanced_skill` + `spring_advanced_skill` | `react_advanced_skill` | `database_skill` | `backend_skill` + `apache_pulsar_skill` (messaging) |
| **Event Streaming** | `apache_camel_skill` OR `apache_pulsar_skill` | `react_advanced_skill` | `database_skill` | `backend_skill` |

---

## 🚀 Running the Complete Workflow

```bash
# Initialize project context
ba:discover source="Requirement document or conversation"
ba:clarify  # answer clarifying questions
ba:brd      # create business requirements document

# Technical decisions & specs
architect:analyse jira=PROJ-123
architect:adr jira=PROJ-123      # record decisions
architect:spec                   # generate current technical specification

# System design
architect:design path=/docs/brd.md
database:design path=/docs/design/design.md
backend:design-api path=/docs/design/design.md
frontend:design path=/docs/design/design.md

# Implementation
orchestrator:plan path=/docs/design/design.md  # break into tasks
implementer:build path=/docs/tasks.md --lang python
implementer:build path=/docs/tasks.md --lang typescript
implementer:enhance --error-handling path=/src
implementer:enhance --observability path=/src

# Testing & Quality
implementer:test path=/src --scope unit
implementer:test path=/src --scope integration
implementer:test path=/docs/tasks.md --scope acceptance
quality:audit path=/src
quality:report path=/src

# Documentation
implementer:doc path=/src
architect:doc path=/docs/design
backend:doc path=/docs/design/api-contract.yaml
doc:readme path=/docs

# Operations
implementer:deploy-observability path=/deploy
ops:runbooks path=/docs/design
ops:alerts path=/deploy/observability.yaml
backend:healthcheck path=/src

# Delivery
ba:trace scope=release version=1.0.0
orchestrator:release-notes path=/docs
implementer:deploy path=/deploy
orchestrator:pr
```

---

## 📈 Skill Enhancement Roadmap

**Current Version:** 5.0.0 | **Total Skills:** 37

### Phase 1: ✅ COMPLETE (This Update)
- [x] All 37 skills documented as "super skills"
- [x] Token efficiency optimized across all skills
- [x] Advanced coding patterns integrated
- [x] HTML output beautified + interactive
- [x] Master workflow created (this document)

### Phase 2: Planned (v5.1.0)
- [ ] Nemesis skill (adversarial validation) enhancement
- [ ] MCP server builder skill improvements
- [ ] Incremental spec generator enhancements
- [ ] Performance optimization for large codebases (50k+ LOC)

### Phase 3: Planned (v5.2.0)
- [ ] Multi-platform export skill
- [ ] Integration test automation skill
- [ ] Contract testing skill
- [ ] Mutation testing skill

---

## 📚 How to Use This Document

1. **For a new project:** Start at STAGE 1, follow linearly
2. **For a feature:** Start at STAGE 2 (existing architecture), skip to STAGE 4
3. **For a bug fix:** STAGE 6 (testing) + STAGE 9 (delivery)
4. **For refactoring:** STAGE 2 (analyze current) + STAGE 4 (new design) + STAGE 5-9
5. **For operations:** Jump to STAGE 8 (observability) only

---

**Last Updated:** 2026-09-28 | **Version:** 5.0.0  
**Maintained By:** awesome-prompts team  
**License:** MIT
