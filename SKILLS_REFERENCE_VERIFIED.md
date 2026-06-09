# Reusable Skills Reference — Verified & Enhanced

**Version:** 2.0  
**Date:** June 9, 2026  
**Total Skills:** 26 documented skills  
**Status:** Complete — All skills documented with purpose, scope, examples, and guardrails.

---

## Quick Reference Table

| # | Skill Name | Category | Purpose | Tech Stack | When to Use |
|---|---|---|---|---|---|
| 1 | code_documentation_skill | Documentation | Auto-generate JSDoc/docstrings/Javadoc | JS, TS, Python, Java | Every public method needs documentation |
| 2 | code_review_skill | Code Review | 6-phase requirement-driven PR analysis | All languages | Before merging code to main |
| 3 | code_health_skill | Code Review | Deep code health inspection + issue taxonomy | All languages | Codebase audit, production issues |
| 4 | code_formatting_skill | Code Review | Universal formatting standards | Java, Python, JS/TS | Code style consistency |
| 5 | backend_skill | Backend | Production REST API generation | FastAPI, Spring Boot | Building backend services |
| 6 | frontend_skill | Frontend | React component generation | React 18+, TypeScript | Building UI components |
| 7 | test_skill | Testing | Comprehensive test generation | pytest, Jest, JUnit5 | 95%+ code coverage |
| 8 | database_skill | Database | SQL schema generation + migrations | PostgreSQL, MySQL, MSSQL | Database design, migrations |
| 9 | api_skill | Backend | RESTful API design patterns | FastAPI, Spring Boot | API endpoint design |
| 10 | error_handling_skill | Patterns | Exception handling + resilience | Java, Python, JS/React | Custom exceptions, recovery patterns |
| 11 | oop_skill | Patterns | OOP pillars + SOLID + design patterns | Java, Python, JS | Architecture, design decisions |
| 12 | java_advanced_skill | Language-Specific | Java 17/21 standards + Spring Boot patterns | Java, Spring Boot | Building Java applications |
| 13 | python_advanced_skill | Language-Specific | Python 3.11+ standards + async patterns | Python, FastAPI, SQLAlchemy | Building Python applications |
| 14 | react_advanced_skill | Language-Specific | React 18+ standards + hooks + TanStack Query | React, TypeScript, Tailwind | Building React applications |
| 15 | spring_advanced_skill | Language-Specific | Spring Framework internals + AOP + Security | Spring Boot, Spring Security | Advanced Spring patterns |
| 16 | mssql_advanced_skill | Language-Specific | T-SQL standards + optimization + NOLOCK guidance | SQL Server, T-SQL | MSSQL development |
| 17 | logger_skill | Infrastructure | SLF4J + Logback + structured logging | Java, SLF4J, Log4j2, Logback | Production logging setup |
| 18 | lombok_skill | Infrastructure | Lombok annotations for boilerplate reduction | Java, Lombok | Reduce Java verbosity |
| 19 | apache_camel_skill | Infrastructure | Apache Camel EIP + routing + components | Java, Apache Camel | Integration routes, messaging |
| 20 | apache_pulsar_skill | Infrastructure | Apache Pulsar producers + consumers + subscriptions | Java, Python, Apache Pulsar | Event streaming, pub-sub |
| 21 | opentelemetry_skill | Infrastructure | Distributed tracing + metrics + observability | Java, OpenTelemetry, Jaeger | Production observability |
| 22 | jira_html_report_skill | Business Analysis | Parse JIRA + generate HTML backlog report | JIRA JSON/CSV | Backlog visualization |
| 23 | context_builder_skill | Architecture | Project scanning + context generation | All languages | Full-stack project understanding |
| 24 | jira_incremental_spec_skill | Business Analysis | Incremental JIRA ticket reading + spec generation | JIRA API | Building comprehensive specs from tickets |
| 25 | ba_create_skill | Business Analysis | Plain-text requirements → JIRA-ready issues + BDD | Markdown, Gherkin | Requirements structuring |
| 26 | multi_review_html_skill | Code Review | Batch PR review HTML report generation | HTML5, CSS3, JavaScript | Multiple PR review synthesis |

---

## Skills by Category

### 1. Code Review & Quality (5 Skills)

---

## code_review_skill.md

**Purpose:** Perform 6-phase requirement-driven code reviews. Validates that PR/MR changes implement JIRA requirements with comprehensive quality analysis, scoring, and grading (A-F).

**Scope:**
- ✅ Covers: Requirement validation, code quality, test coverage, documentation analysis, scoring
- ❌ Excludes: Performance optimization (use quality:perf), security vulnerability scanning (use quality:security)

**Entry Point:**
When you have a PR/MR and need to validate it implements requirements:
- Validate that PR changes implement JIRA acceptance criteria
- Analyze code quality and identify issues
- Assess test coverage completeness
- Score the PR (A-F grade)

**Outputs:**
- Phase 1: Requirement Analysis (plain English summary + ACs)
- Phase 2: Requirement Validation (coverage %, gaps)
- Phase 3: Code Quality Review (issues by category/severity)
- Phase 4: Test Coverage Analysis (%, missing scenarios)
- Phase 5: Documentation Analysis (%, gaps)
- Phase 6: Scorecard (A-F grade + weighted scores)

**Guardrails:**
- Always start with Phase 1 (requirement analysis) before diving into code
- Use standard issue taxonomy (PERF, ERR, DELAY, MEM, SEC, MAINT, RELI)
- Assign severity (P0-P3) based on impact, not line count
- Score must be transparent and justified with specific evidence
- Never approve code that has gaps in requirement coverage (< 90%)

**Examples:**

#### Example 1: User Registration Feature PR
**Context:** Review PR-456 implementing "User Registration with Email Validation" (PROJ-123)
**Execution:**
- Phase 1: Extract JIRA summary, ACs, constraints → "Users can sign up with email/password, email is validated, password hashed"
- Phase 2: Check PR code for email validation (✓), password hashing (✓), success notification (✗) → 75% coverage
- Phase 3: Scan code for issues → 1 P1 (missing error handling), 2 P2 (missing rate limiting)
- Phase 4: Check test coverage → 82% (missing edge case for invalid email formats)
- Phase 5: Check docstrings → 90% (UserService missing examples)
- Phase 6: Score = 0.9*(90%) + 0.2*(75%) + 0.8*(82%) + 0.7*(90%) = B+

**Expected Result:** Structured review report with 6 phases, clear gaps, and actionable fixes

#### Example 2: Payment Processing Bug Fix
**Context:** Review PR-789 fixing "NPE when processing refunds" (BUG-456)
**Execution:**
- Phase 1: Extract bug description → "App crashes with null pointer when refund amount > order total"
- Phase 2: Validate fix → Check null checks added (✓), guard clause added (✓) → 100% coverage
- Phase 3: Code quality → 1 P2 (missing test for refund > order), exception handling is good
- Phase 4: Test coverage → 95% (one happy path, three error paths)
- Phase 5: Documentation → 85% (method doc added, no integration notes)
- Phase 6: Score = A- (excellent fix, minor doc gaps)

**Expected Result:** Quick approval with minor documentation suggestion

**When to Use:**
- Validating PR implementation against JIRA requirements
- Pre-merge code quality check (before squash/merge)
- Retrospective analysis (what was the quality of that fix?)
- Training/mentoring (explain code quality issues to junior devs)

**When NOT to Use:**
- Don't use for security-specific audits (use quality:security instead)
- Don't use for performance profiling (use quality:perf instead)
- Don't use if JIRA ticket has no acceptance criteria (gather first, then review)

**Edge Cases:**
- PR spans multiple JIRA tickets → Validate each ticket separately, then aggregate score
- JIRA ticket is vague (no clear ACs) → Phase 1 clarifies assumptions, note this in report
- PR includes refactoring beyond requirement → Flag as scope creep (P2), note if valuable
- Test coverage is high but fragile (brittle tests) → P1 issue, note test quality concern

**Testing Approach:**
- Unit test: Verify Phase 1 extracts all AC items correctly from JIRA JSON
- Integration test: Run full 6-phase review on known PR, validate all sections present
- Edge case test: Test with vague JIRA, with missing tests, with large refactoring

---

## code_health_skill.md

**Purpose:** Perform deep code health analysis. Defines issue taxonomy (PERF, ERR, DELAY, MEM, SEC, MAINT, RELI), severity scoring (P0-P3), and structured evidence collection.

**Scope:**
- ✅ Covers: Code smell detection, performance issues, error handling gaps, security issues, maintainability
- ❌ Excludes: Functional correctness (testing job), API design (architect job)

**Entry Point:**
When you need to audit code health:
- Scan codebase for hidden issues (N+1 queries, memory leaks, missing error handling)
- Classify issues by category (PERF, ERR, DELAY, etc.) and severity (P0-P3)
- Collect evidence (file, line, code snippet, why it's wrong, how to fix)
- Generate structured health report with prioritized issues

**Outputs:**
- Health report organized by category (PERF, ERR, DELAY, MEM, SEC, MAINT, RELI)
- Each issue includes: location, evidence, root cause, impact, fix
- Severity metrics (P0 count, P1 count, etc.)
- Overall code health score

**Guardrails:**
- Never report a vague issue (e.g., "this code is slow") — always show specific line + evidence
- Every issue must have root cause (WHY it's wrong) + impact (WHAT could go wrong)
- P0 = production outage/data loss/security breach; P1 = user-visible failure; P2 = technical debt; P3 = code smell
- Focus on patterns (multiple N+1 queries?) not just individual findings
- Rate limit: Scan no more than 10 files per second (avoid analysis paralysis)

**Examples:**

#### Example 1: Spring Boot API with N+1 Query Issue
**Context:** Audit OrderService in Java Spring Boot project
**Execution:**
- Scan OrderService.java for JPA patterns
- Find: `List<Order> orders = repo.findAll()` followed by loop calling `order.getCustomer()`
- Category: PERF, Severity: P1 (impacts load time)
- Evidence: `Line 45-50: for (Order o : orders) { o.getCustomer().getName(); }` (N+1 pattern)
- Root Cause: `@OneToMany` has default FetchType.LAZY; loop triggers SELECT for each order
- Impact: 1000 orders = 1001 queries (1 SELECT orders + 1000 SELECT customers)
- Fix: Add `@OneToMany(fetch = FetchType.EAGER)` or use `@Query` with JOIN FETCH

**Expected Result:** Health report with specific line numbers and before/after code

#### Example 2: Python Code with Missing Error Handling
**Context:** Audit payment_service.py in FastAPI project
**Execution:**
- Scan external API calls (payment gateway, email service)
- Find: `response = requests.get(f"{GATEWAY_URL}/pay", json=data)` with no error handling
- Category: ERR, Severity: P1 (service crashes on network failure)
- Evidence: `Line 23: requests.get(...) # No try/except`
- Root Cause: No exception handling for network timeouts, 5xx responses
- Impact: Single payment gateway timeout crashes entire API
- Fix: Wrap in try/except, add timeout, implement circuit breaker pattern

**Expected Result:** Production-ready error handling suggestions

**When to Use:**
- Production incident RCA (why did it crash?)
- Codebase baseline assessment (quarterly health check)
- PR author self-check (before pushing to code review)
- Team training (identify patterns to avoid)

**When NOT to Use:**
- Don't use for style/formatting checks (use code_formatting_skill)
- Don't use for high-level architecture review (use architect:design)
- Don't use if code is new and untested (test first, audit later)

**Edge Cases:**
- Polyglot codebase (Java + Python + JS) → Apply language-specific checklist to each file
- Legacy code with many violations → Prioritize P0/P1, create backlog for P2/P3
- Third-party dependency vulnerability → Flag as P0, recommend version upgrade
- Performance issue but impossible to fix (legacy constraint) → Document as accepted risk

**Testing Approach:**
- Unit test: Verify PERF detection catches missing indexes
- Integration test: Run scan on known-bad code (intentional N+1, missing error handling)
- False positive test: Scan good code, ensure no false positives

---

## code_formatting_skill.md

**Purpose:** Enforce universal code formatting standards across Java, Python, JavaScript/TypeScript. Covers indentation, line length, whitespace, naming conventions, and tooling.

**Scope:**
- ✅ Covers: Indentation, spacing, line length, naming, alignment rules, tool configuration
- ❌ Excludes: Code structure/refactoring (oop_skill), language idioms (language-specific skills)

**Entry Point:**
When you need consistent code style across a project:
- Define project-wide formatting rules (4-space indent, 100-char line limit)
- Configure formatters (Prettier for JS, Black for Python, Google Style for Java)
- Apply formatting to codebase
- Validate in pre-commit hooks

**Outputs:**
- Formatted code adhering to standards
- `.editorconfig` file (cross-editor compatibility)
- Formatter configuration (prettier.config.js, black.toml, etc.)
- Pre-commit hook configuration

**Guardrails:**
- Never use tabs (always 4 spaces) — tabs cause alignment issues across editors
- Line length max 100 chars (some argue 120) — stick with project choice
- Always include trailing newline at end of file
- No trailing whitespace (causes git diffs pollution)
- Trailing commas in multi-line lists/objects (helps git diffs)

**Examples:**

#### Example 1: Java Project Formatting
**Context:** Apply Google Java Style to existing Spring Boot project
**Execution:**
- Install IntelliJ Google Style Guide (Editor → Code Style → Java)
- Set: 4-space indent, 100-char line limit, no star imports
- Configure IDE: Settings → Tools → Java → Google Format
- Apply: Code → Reformat Code (whole project)
- Commit: gitignore `.idea/`, add .editorconfig

**Expected Result:** Consistent Java code across entire project

#### Example 2: JavaScript/TypeScript Project Formatting
**Context:** Set up Prettier for React TypeScript project
**Execution:**
```json
// prettier.config.js
module.exports = {
  semi: true,
  singleQuote: true,
  trailingComma: 'all',
  printWidth: 100,
  tabWidth: 2
}
```
- Install: `npm install --save-dev prettier`
- Add pre-commit: `husky install && npx husky add .husky/pre-commit "prettier --write ."`
- Run: `prettier --write src/` (format all files)

**Expected Result:** Automated formatting, consistent style on every commit

**When to Use:**
- Project initialization (set standards before first commit)
- New team member onboarding (show formatting rules)
- Legacy code cleanup (one-time reformat)
- Pre-commit automation (enforce style on every commit)

**When NOT to Use:**
- Don't use to enforce code structure changes (refactoring, not formatting)
- Don't use to enforce naming patterns (that's OOP/architecture)
- Don't use during active feature development (causes merge conflicts)

**Edge Cases:**
- Team has strong opinion on 2-space vs 4-space indent → Document decision, lock in .editorconfig
- Mix of Python 2 and 3 code → Black only supports Python 3, migrate first
- Auto-formatted code breaks functionality (rare) → Add `# fmt: skip` directive to specific lines

**Testing Approach:**
- Unit test: Format intentionally bad code, verify output matches standard
- Integration test: Run formatter on entire project, check no build errors
- Pre-commit test: Verify hook catches unformatted code before commit

---

## multi_review_html_skill.md

**Purpose:** Generate a single self-contained HTML file that displays batch code reviews with sidebar tabs, summary dashboard, and per-PR review panels. All CSS/JS inline, zero external dependencies.

**Scope:**
- ✅ Covers: Multi-PR review synthesis, HTML report generation, tabbed navigation, summary statistics
- ❌ Excludes: Individual PR review logic (code_review_skill), verdict/grading calculation

**Entry Point:**
When you have reviewed multiple PRs and need to synthesize findings:
- Combine 2+ PR reviews into single HTML report
- Generate summary dashboard with aggregate statistics
- Provide tabbed navigation (Summary + per-PR tabs)
- Enable filtering, PDF/JSON export

**Outputs:**
- `batch-review.html` — Self-contained, offline, single file
- Sidebar with tab navigation (Summary + PR-1, PR-2, PR-3, etc.)
- Summary dashboard with score matrix, priority histogram, verdict badges
- Per-PR panels with full context, issues, before/after code samples

**Guardrails:**
- HTML file must be self-contained (zero CDN dependencies, all CSS/JS inline)
- File size: aim for < 5MB (split reviews if needed)
- All JavaScript vanilla ES6 (no framework dependencies)
- Support all modern browsers (Chrome, Firefox, Safari, Edge 2022+)
- Always include generated timestamp and review author

**Examples:**

#### Example 1: Batch Review — 3 Feature PRs
**Context:** Synthesize reviews for PR-456 (Auth), PR-457 (Payment), PR-458 (Orders)
**Execution:**
- Input: 3 review objects with verdict (A+, B, A-), issues list, AC coverage
- Generate: HTML with 4 tabs (Summary + 3 PRs)
- Summary dashboard: Shows verdict badges, aggregate coverage %, score comparison chart
- Per-PR tabs: Each shows full review, issues ranked by severity, code samples
- Export: User can download as JSON or print to PDF

**Expected Result:** Single HTML file, 200KB, renders instantly, fully interactive

#### Example 2: Batch Review — 5 Bug Fixes
**Context:** Synthesize reviews for 5 critical bug fixes (priority: P0, P1)
**Execution:**
- Input: 5 bug fix reviews, each with verdict, impact assessment, regression risks
- Generate: HTML with Summary showing bug severity matrix (P0: 2, P1: 3)
- Highlight: High-risk fixes requiring stakeholder sign-off
- Filter: Allow filtering by verdict, severity, risk level
- Export: Enable PDF for management review

**Expected Result:** Executive-ready batch report

**When to Use:**
- Sprint review (multiple PRs in one report)
- Release validation (batch of features ready to deploy)
- Team training (show multiple review examples)
- Stakeholder communication (visual summary for non-technical audience)

**When NOT to Use:**
- Don't use for single PR review (overkill, use simple markdown)
- Don't use if you haven't completed individual PR reviews yet
- Don't use for real-time review (generate HTML after reviews are final)

**Edge Cases:**
- More than 20 PRs → Split into 2+ reports (file size limits)
- PRs with conflicting verdicts → Add note explaining disagreement
- No PR reviews available → Generate empty report with instructions

**Testing Approach:**
- Unit test: Verify HTML structure with 2-3 PRs, check all tabs render
- Integration test: Generate report from real review data, test export (JSON, PDF)
- Browser test: Open in Chrome, Firefox, Safari, Edge; verify responsive design

---

### 2. Testing (1 Skill)

---

## test_skill.md

**Purpose:** Generate and execute comprehensive tests (unit, integration, E2E) across backend, frontend, and integration layers with 95%+ coverage metrics.

**Scope:**
- ✅ Covers: Unit tests (pytest, JUnit5), integration tests, E2E tests, coverage reporting
- ❌ Excludes: Performance/load testing (quality:perf), security testing (quality:security)

**Entry Point:**
When you have implemented code and need comprehensive test coverage:
- Generate unit tests for business logic (services, models)
- Generate integration tests for API endpoints
- Generate E2E tests for user workflows
- Achieve >= 95% code coverage, >= 90% per layer

**Outputs:**
- Backend tests: `tests/unit/*.test.py`, `tests/integration/*.integration.py` (pytest)
- Backend tests: `src/test/java/*.java` (JUnit5, Mockito)
- Frontend tests: `tests/components/*.test.tsx` (Vitest + React Testing Library)
- E2E tests: `tests/e2e/*.e2e.ts` (Playwright)
- Coverage reports: `coverage.html`, `coverage.json` (95%+ threshold)

**Guardrails:**
- Use meaningful test names: `givenXxx_whenYyy_thenZzz()` pattern
- Follow AAA testing pattern: Arrange-Act-Assert
- Mock external dependencies (APIs, databases, file systems)
- Test happy paths AND error cases
- Aim for 95%+ coverage but don't test trivial getters/setters
- Use fixtures/factories to reduce test boilerplate

**Examples:**

#### Example 1: Python FastAPI Backend Tests
**Context:** Generate tests for user registration endpoint (POST /users)
**Execution:**
```python
# tests/unit/test_user_service.py
def test_givenValidEmail_whenCreateUser_thenUserCreated():
    service = UserService()
    result = service.create_user("alice@example.com", "hashed_pwd")
    assert result.email == "alice@example.com"
    assert result.id is not None

def test_givenDuplicateEmail_whenCreateUser_thenRaises():
    service = UserService()
    service.create_user("alice@example.com", "pwd1")
    with pytest.raises(ValueError):
        service.create_user("alice@example.com", "pwd2")

# tests/integration/test_user_api.py
def test_givenValidPayload_whenPostUser_then201Created(client):
    response = client.post("/users", json={"email": "bob@test.com", "password": "pwd"})
    assert response.status_code == 201
    assert response.json()["email"] == "bob@test.com"
```

**Expected Result:** 25+ tests, 95% coverage of user service and endpoint

#### Example 2: React Component Tests
**Context:** Generate tests for LoginForm component
**Execution:**
```typescript
// tests/components/LoginForm.test.tsx
test('givenEmptyForm_whenSubmit_thenShowsValidationError', async () => {
  render(<LoginForm onSuccess={vi.fn()} />);
  const submitBtn = screen.getByRole('button', { name: /login/i });
  await userEvent.click(submitBtn);
  expect(screen.getByText(/email required/i)).toBeInTheDocument();
});

test('givenValidCreds_whenSubmit_thenCallsOnSuccess', async () => {
  const onSuccess = vi.fn();
  render(<LoginForm onSuccess={onSuccess} />);
  await userEvent.type(screen.getByLabelText(/email/i), 'alice@test.com');
  await userEvent.type(screen.getByLabelText(/password/i), 'pwd123');
  await userEvent.click(screen.getByRole('button', { name: /login/i }));
  expect(onSuccess).toHaveBeenCalledWith({ email: 'alice@test.com' });
});
```

**Expected Result:** Component fully tested, 85%+ coverage

**When to Use:**
- After feature implementation (code → tests → merge)
- Before refactoring (tests ensure behavior unchanged)
- Performance optimization (ensure no regressions)
- New team member onboarding (show testing patterns)

**When NOT to Use:**
- Don't test trivial code (getters, setters, auto-generated code)
- Don't test external libraries (assume they work)
- Don't use for TDD (implement code first, then test)

**Edge Cases:**
- Async operations (API calls, file I/O) → Mock with fixtures, use async/await
- Database interactions → Use in-memory SQLite for unit tests, PostgreSQL for integration
- External APIs → Mock with response fixtures, test error scenarios
- UI components with animations → Disable animations in test env, test state changes

**Testing Approach:**
- Unit test coverage: >= 95% for business logic
- Integration test: Every API endpoint tested (happy path + 2 error cases)
- E2E test: Critical user workflows (signup, login, purchase)
- Coverage validation: `pytest --cov=src --cov-report=html` (Python)

---

### 3. Documentation (2 Skills)

---

## code_documentation_skill.md

**Purpose:** Auto-generate professional documentation for every public method, class, and module. Ensures 100% method documentation using JSDoc (JS/TS), docstrings (Python), Javadoc (Java).

**Scope:**
- ✅ Covers: Method-level docs, class-level docs, module-level docs, code examples
- ❌ Excludes: Architecture documentation (architect:design), API documentation (api_skill handles OpenAPI)

**Entry Point:**
When you have written code and need to add documentation:
- Document every public method with @param, @returns, @throws
- Add JSDoc/docstring examples
- Generate class-level overview
- Generate module-level index

**Outputs:**
- Fully documented code with inline comments
- Generated HTML documentation (Javadoc, Sphinx, JSDoc)
- Code examples in docstrings
- Architecture diagrams in module docs

**Guardrails:**
- Never leave a public method undocumented
- Include @param for every parameter (with type and description)
- Include @returns / @return with type and description
- Include @throws / Raises for all exceptions that can be raised
- Add @example with realistic usage code
- Use consistent formatting across codebase

**Examples:**

#### Example 1: Python Function Documentation
**Context:** Document order processing function
**Execution:**
```python
def process_order(order_id: int, payment_method: str) -> dict:
    """Process a customer order and charge payment method.
    
    This function validates the order, calculates total, charges the payment
    method, and returns a receipt. If payment fails, the order remains pending.
    
    Args:
        order_id (int): Unique order identifier from the database.
        payment_method (str): Payment method code ('CARD', 'PAYPAL', 'ACH').
    
    Returns:
        dict: Receipt object with keys:
            - receipt_id (str): Unique receipt identifier
            - amount (float): Total amount charged
            - status (str): 'SUCCESS' or 'PENDING'
            - timestamp (str): ISO 8601 timestamp
    
    Raises:
        OrderNotFoundError: If order_id does not exist.
        PaymentFailedError: If payment gateway rejects the transaction.
        ValidationError: If payment_method is invalid.
    
    Examples:
        Process order with credit card:
        >>> receipt = process_order(123, 'CARD')
        >>> print(receipt['status'])
        SUCCESS
        
        Handle payment failure:
        >>> try:
        ...     receipt = process_order(456, 'CARD')
        ... except PaymentFailedError as e:
        ...     print(f'Payment declined: {e.message}')
    """
```

**Expected Result:** Complete docstring with all sections, types, and examples

#### Example 2: Java Method Documentation
**Context:** Document OrderService.createOrder method
**Execution:**
```java
/**
 * Creates a new order for the given customer.
 *
 * <p>Validates that the customer exists, the order items are in stock, and
 * creates a database record. The order is created in PENDING status until
 * payment is processed.</p>
 *
 * @param customerId the unique identifier of the customer (must exist)
 * @param items     list of line items; must not be empty
 * @param shippingAddress the shipping address; must not be null
 * @return          the created Order object with ID set
 * @throws          CustomerNotFoundException if customer does not exist
 * @throws          OutOfStockException if any item is not in stock
 * @throws          ValidationException if items list is empty
 *
 * @example
 * Order order = orderService.createOrder(
 *   123,
 *   Arrays.asList(new LineItem("SKU-001", 2)),
 *   new Address("123 Main St", "NY", "10001")
 * );
 * System.out.println(order.getId());  // Output: order-uuid-here
 */
public Order createOrder(int customerId, List<LineItem> items, Address shippingAddress) {
    // Implementation
}
```

**Expected Result:** Javadoc-ready documentation

**When to Use:**
- After writing new code (before code review)
- Legacy code cleanup (retroactive documentation)
- API documentation generation (feeds OpenAPI/Swagger)
- Team onboarding (help new devs understand code)

**When NOT to Use:**
- Don't over-document simple code (e.g., getBalance() is self-explanatory)
- Don't use for private/internal methods (document public API only)
- Don't document obvious code (e.g., `int count = 0;` doesn't need explanation)

**Edge Cases:**
- Generic/template methods → Document type parameters (@param <T>)
- Builder pattern → Document each builder method separately
- Async methods → Add @async tag, explain callback behavior
- Methods with optional parameters → Clearly mark optional with "optional:" prefix

**Testing Approach:**
- Verify all public methods have @param, @returns, @throws
- Verify examples compile and run successfully
- Verify generated docs render correctly (Javadoc, Sphinx, etc.)

---

## context_builder_skill.md

**Purpose:** Scan projects and build architectural understanding. Generates context.json (machine-readable), architecture.md (narrative + diagrams), tech-stack.md (tech reference), and design.html (interactive visualization).

**Scope:**
- ✅ Covers: Technology detection, architecture analysis, file tree analysis, API endpoint discovery
- ❌ Excludes: Code generation (implementer:build), design decisions (architect:design)

**Entry Point:**
When starting work on a new or unfamiliar project:
- Scan project structure to understand tech stack
- Auto-detect frontend framework, backend framework, database
- Identify API endpoints and data models
- Generate 4 context files for downstream tasks

**Outputs:**
- `docs/context/context.json` — Machine-readable metadata (tech stack, files, endpoints)
- `docs/context/architecture.md` — Mermaid architecture diagram + narrative
- `docs/context/tech-stack.md` — Technology reference table
- `docs/context/design.html` — Interactive 4-tab visualization (offline)

**Guardrails:**
- Context is auto-generated but should be validated by human (tech stack auto-detection not perfect)
- Context is cached (reuse if < 7 days old, rebuild if stale)
- Always save context in `docs/context/` directory (standard location)
- Never commit context files to git (use .gitignore)
- Validate technology detection before using in downstream tasks

**Examples:**

#### Example 1: Spring Boot + React Full-Stack Project
**Context:** Scan a new microservices project for architecture understanding
**Execution:**
- Scan project tree (pom.xml, package.json, Dockerfile)
- Detect: Java 17, Spring Boot 3.x, React 18, PostgreSQL, Docker
- Analyze: 12 Java service classes, 45 React components, 3 API endpoints
- Generate: context.json with tech mappings, architecture.md with diagram
- Create: design.html with 4 tabs (Tech Stack, Architecture, File Tree, Endpoints)

**Expected Result:** Complete context files, developer can start coding immediately

#### Example 2: Python FastAPI Project
**Context:** Onboard new developer to existing FastAPI project
**Execution:**
- Scan: requirements.txt, pyproject.toml, alembic migrations, tests/
- Detect: Python 3.11, FastAPI 0.104, SQLAlchemy 2.x, PostgreSQL, pytest
- Analyze: 8 service modules, 25 Pydantic models, 15 API routes
- Generate: context.json with service descriptions, tech-stack.md with versions
- Create: design.html with data model relationships, endpoint documentation

**Expected Result:** New developer has complete project overview in 5 minutes

**When to Use:**
- Project initialization (before first feature)
- New team member onboarding
- Refactoring planning (understand current architecture first)
- Quarterly architecture review (check what's actually there)

**When NOT to Use:**
- Don't run during active development (noisy diffs)
- Don't rely solely on auto-detected tech (validate manually)
- Don't use to generate code (that's implementer:build's job)

**Edge Cases:**
- Monorepo with multiple services → Analyze each service separately, aggregate in summary
- Legacy project with multiple languages → Detect all languages, note in tech stack
- Project with no tests → Flag in context.json for downstream tasks
- No documentation files → Use code analysis to infer architecture

**Testing Approach:**
- Unit test: Verify technology detection (pom.xml → Java 17 + Spring Boot)
- Integration test: Run full scan on sample projects, validate all 4 output files exist
- Validation test: Compare generated context against known-good project architecture

---

### 4. Backend & Database (3 Skills)

---

## backend_skill.md

**Purpose:** Generate production-grade backend APIs using Python (FastAPI) and Java (Spring Boot). Combines python_advanced_skill and java_advanced_skill with unified API development standards (route design, validation, authentication, error handling, testing).

**Scope:**
- ✅ Covers: API design, endpoint generation, request/response models, authentication, error handling
- ❌ Excludes: Database schema (database_skill), API documentation (api_skill)

**Entry Point:**
When you need to build a backend service:
- Design API routes (GET, POST, PUT, DELETE, PATCH)
- Define request/response models with validation
- Implement authentication (JWT, OAuth2, API keys)
- Generate business logic + error handling
- Create comprehensive tests (95%+ coverage)

**Outputs:**
- API routes with proper HTTP methods and status codes
- Request/response serialization models (Pydantic for Python, DTOs for Java)
- Authentication/authorization middleware
- Business logic service layer
- Comprehensive tests (unit + integration)
- OpenAPI/Swagger documentation

**Guardrails:**
- Always validate input (use Pydantic validators or JSR-303 annotations)
- Always handle errors with appropriate HTTP status codes
- Always include authentication check on protected endpoints
- Always return meaningful error messages (help API consumers debug)
- Always generate tests (95%+ coverage minimum)
- Follow RESTful conventions (GET = read, POST = create, PUT = update, DELETE = remove)

**Examples:**

#### Example 1: FastAPI User Registration Endpoint
**Context:** Build POST /users endpoint for user registration
**Execution:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import EmailStr, BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    email: EmailStr
    password: str

@app.post("/users", status_code=201)
async def create_user(user: UserCreate):
    """Create a new user with email and password."""
    # Validate password strength
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password too short")
    
    # Check if user exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    # Hash password and create user
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    new_user = User(email=user.email, password_hash=hashed)
    db.add(new_user)
    db.commit()
    
    return {"id": new_user.id, "email": new_user.email}
```

**Expected Result:** Production-ready endpoint with validation and error handling

#### Example 2: Spring Boot Order Processing Endpoint
**Context:** Build POST /orders endpoint for order creation
**Execution:**
```java
@RestController
@RequestMapping("/orders")
public class OrderController {
    
    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(
        @Valid @RequestBody CreateOrderRequest request,
        @RequestHeader("Authorization") String token
    ) {
        // Validate authentication
        User user = authService.validateToken(token);
        
        // Create order in service
        Order order = orderService.createOrder(user.getId(), request);
        
        // Return created response
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(new OrderResponse(order));
    }
}
```

**Expected Result:** Authenticated endpoint with input validation and proper HTTP status codes

**When to Use:**
- Building new backend service
- Adding new API endpoints
- Migrating from one framework to another
- Team training (show API best practices)

**When NOT to Use:**
- Don't use for business logic only (use service layer directly)
- Don't use for database schema (use database_skill)
- Don't use for frontend code (use frontend_skill)

**Edge Cases:**
- Pagination required (large result sets) → Implement limit/offset, default page size
- File uploads → Handle multipart/form-data, validate file size/type
- Rate limiting → Implement per-user/IP rate limiting
- Async operations → Return 202 Accepted with status polling endpoint

**Testing Approach:**
- Unit test: Test service layer business logic with mocks
- Integration test: Test endpoint with in-memory database
- E2E test: Test complete flow (create order → get order → cancel order)
- Coverage: >= 95% code coverage

---

## database_skill.md

**Purpose:** Generate SQL schemas, migrations, and DDL for PostgreSQL, MySQL, and SQL Server. Defines schema design patterns, migration scripts, indexing strategies, and validation rules.

**Scope:**
- ✅ Covers: Schema creation, migrations, indexes, constraints, relationships, normalized design
- ❌ Excludes: Query optimization (mssql_advanced_skill for T-SQL patterns), data loading (seeding)

**Entry Point:**
When you need to design a database:
- Define entities and relationships
- Generate CREATE TABLE statements
- Design indexes for performance
- Create migration scripts for evolution
- Document schema design decisions

**Outputs:**
- `schema.sql` — CREATE TABLE statements with constraints
- `migrations/` — Migration scripts (V001__, V002__, etc. using Flyway/Liquibase)
- `indexes.sql` — CREATE INDEX statements for performance
- `relationships.sql` — Foreign key constraints and cardinality
- `schema.md` — Documentation of tables, columns, relationships

**Guardrails:**
- Always use normalized design (3NF minimum)
- Always define primary keys (never use natural keys)
- Always use surrogate keys (UUID or auto-increment)
- Always add timestamps (created_at, updated_at)
- Always use meaningful column names (snake_case for SQL)
- Always include constraints (NOT NULL, UNIQUE, CHECK)
- Never use floating point for money (use DECIMAL)
- Always use UTC timestamps (no timezone conversions in DB)

**Examples:**

#### Example 1: PostgreSQL E-Commerce Schema
**Context:** Design schema for orders system
**Execution:**
```sql
-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total DECIMAL(10, 2) NOT NULL CHECK (total >= 0),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on user_id for fast lookups
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
```

**Expected Result:** Normalized schema with proper constraints and indexes

#### Example 2: MySQL Migration Script
**Context:** Add payment tracking to orders
**Execution:**
```sql
-- V002__add_payment_tracking.sql
ALTER TABLE orders
ADD COLUMN payment_method VARCHAR(50),
ADD COLUMN paid_at TIMESTAMP;

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id CHAR(36) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE INDEX idx_payments_order_id ON payments(order_id);
```

**Expected Result:** Migration script ready to apply with Flyway

**When to Use:**
- Project initialization (design schema before coding)
- Feature addition (new data models)
- Performance optimization (add indexes)
- Data model refactoring (normalize or denormalize)

**When NOT to Use:**
- Don't use for query optimization (use query analysis tools)
- Don't use for data loading/seeding (use separate seed scripts)
- Don't use for reporting (use views instead of new tables)

**Edge Cases:**
- Millions of rows → Add partitioning, consider column-store for analytics
- Multi-tenancy → Add tenant_id to all tables, use row-level security
- Soft deletes → Add deleted_at timestamp, filter in queries
- Historical tracking → Add audit table or event sourcing pattern

**Testing Approach:**
- Unit test: Verify constraints (e.g., total >= 0)
- Integration test: Test foreign key relationships, cascade behavior
- Migration test: Run all migrations forward and backward, verify idempotency

---

### 5. Frontend (1 Skill)

---

## frontend_skill.md

**Purpose:** Generate production-grade React components using React 18+, TypeScript, and Tailwind CSS. Integrates with react_advanced_skill and frontend-design for functional correctness and visual distinctiveness.

**Scope:**
- ✅ Covers: Component generation, TypeScript prop interfaces, custom hooks, Tailwind styling, accessibility
- ❌ Excludes: High-level UI architecture (architect:frontend), design system creation

**Entry Point:**
When you need to build UI components:
- Design component props with TypeScript interfaces
- Generate functional React components with hooks
- Style with Tailwind CSS (responsive design)
- Test with Vitest + React Testing Library
- Ensure WCAG 2.1 AA accessibility

**Outputs:**
- Functional React components (React.FC<Props> with TypeScript)
- Reusable prop interfaces
- Custom hooks for cross-cutting concerns
- Tailwind CSS styling (responsive, dark mode support)
- Component tests (85%+ coverage)
- Storybook stories (optional)

**Guardrails:**
- One component = one job (single responsibility principle)
- Always use TypeScript strict mode (no `any` types)
- Always include JSDoc comments on props
- Always test accessibility (focus, keyboard navigation, screen readers)
- Always support dark mode (use Tailwind dark: prefix)
- Responsive design required (mobile, tablet, desktop)

**Examples:**

#### Example 1: React Login Form Component
**Context:** Build LoginForm component with validation
**Execution:**
```typescript
interface LoginFormProps {
  /** Callback fired when login succeeds */
  onSuccess: (credentials: { email: string }) => void;
  /** Show loading state while authenticating */
  isLoading?: boolean;
}

/**
 * Login form with email and password validation.
 * Handles form submission, error display, and accessibility.
 *
 * @example
 * <LoginForm onSuccess={(creds) => console.log(creds)} />
 */
export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, isLoading = false }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate
    const newErrors: Record<string, string> = {};
    if (!email) newErrors.email = 'Email required';
    if (password.length < 8) newErrors.password = 'Password too short';
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    onSuccess({ email });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-md mx-auto">
      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-1">
          Email Address
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className={`w-full px-3 py-2 border rounded ${errors.email ? 'border-red-500' : 'border-gray-300'}`}
          disabled={isLoading}
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {errors.email && <p id="email-error" className="text-red-500 text-sm mt-1">{errors.email}</p>}
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
      >
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};
```

**Expected Result:** Accessible, tested, production-ready component

#### Example 2: React Data Table Component
**Context:** Build reusable DataTable component for listing items
**Execution:**
```typescript
interface DataTableProps<T> {
  /** Array of items to display */
  items: T[];
  /** Column definitions */
  columns: ColumnDef<T>[];
  /** Optional sorting handler */
  onSort?: (field: keyof T, direction: 'asc' | 'desc') => void;
}

export const DataTable = <T,>({ items, columns, onSort }: DataTableProps<T>) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse border border-gray-300">
        <thead className="bg-gray-100">
          <tr>
            {columns.map((col) => (
              <th
                key={String(col.field)}
                onClick={() => onSort?.(col.field, 'asc')}
                className="px-4 py-2 text-left cursor-pointer hover:bg-gray-200"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {items.map((item, idx) => (
            <tr key={idx} className="hover:bg-gray-50">
              {columns.map((col) => (
                <td key={String(col.field)} className="px-4 py-2 border-t">
                  {String(item[col.field])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

**Expected Result:** Reusable, typed, accessible table component

**When to Use:**
- Building new UI features
- Creating component library
- Refactoring legacy React code
- Team training (show React + TypeScript patterns)

**When NOT to Use:**
- Don't use for page layout (that's architect:frontend's job)
- Don't use for design system creation (separate initiative)
- Don't use for state management patterns (use Zustand/Redux as needed)

**Edge Cases:**
- Complex form validation → Use react-hook-form + Zod
- Real-time updates → Use TanStack Query with polling/subscriptions
- Infinite scrolling → Use Intersection Observer + pagination
- Animations → Use Framer Motion or CSS transitions

**Testing Approach:**
- Unit test: Test component rendering, prop variations, event handlers
- Accessibility test: Test focus, keyboard navigation, ARIA labels
- Integration test: Test with real data, API mocking
- Visual regression: Test with screenshot comparisons

---

### 6. Language-Specific Skills (5 Skills)

---

## java_advanced_skill.md

**Purpose:** Provide Java 17/21 coding standards, Spring Boot 3.x patterns, Javadoc documentation, and JUnit 5 + Mockito test generation.

**Scope:**
- ✅ Covers: Java 17/21 features (records, sealed classes, text blocks, virtual threads), OOP pillars, Spring patterns
- ❌ Excludes: Database queries (database_skill), API design (api_skill)

**Entry Point:**
When writing Java code:
- Check Java version first (11, 17, or 21?)
- Use modern features (records, sealed classes, switch expressions)
- Follow Spring Boot 3.x patterns (@Component, @Service, dependency injection)
- Generate Javadoc for all public methods
- Create JUnit5 tests with Mockito

**Outputs:**
- Production Java code with proper OOP encapsulation
- Javadoc-documented methods
- JUnit5 tests with Mockito mocks
- Spring Boot configuration classes
- Builder pattern implementations where appropriate

**Guardrails:**
- Always check version first (Java 17 has sealed classes, Java 21 has virtual threads)
- Always use records for immutable data classes (not traditional getters/setters)
- Always mark fields private and use getters for encapsulation
- Always throw checked exceptions for recoverable errors, unchecked for programming bugs
- Always use try-with-resources for closeable resources
- Methods should be ≤ 20 lines, classes ≤ 300 lines

**Examples:**

#### Example 1: Java 17 Record with Spring Component
**Context:** Create User entity for e-commerce system
**Execution:**
```java
// User as immutable record (Java 17+)
public record User(
    UUID id,
    String email,
    String passwordHash,
    LocalDateTime createdAt
) {
    public User {
        // Compact constructor for validation
        if (email == null || email.isBlank()) {
            throw new IllegalArgumentException("Email cannot be empty");
        }
    }
}

// Service using Spring dependency injection
@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {
    private final UserRepository repository;
    private final PasswordEncoder passwordEncoder;

    /**
     * Creates a new user account.
     *
     * @param email the user's email address
     * @param plainPassword the plaintext password to hash
     * @return the created user record
     * @throws ValidationException if email already exists
     */
    public User createUser(String email, String plainPassword) {
        // Check if user exists
        if (repository.existsByEmail(email)) {
            throw new ValidationException("User already exists: " + email);
        }

        // Create and save
        String hash = passwordEncoder.encode(plainPassword);
        User user = new User(
            UUID.randomUUID(),
            email,
            hash,
            LocalDateTime.now(ZoneOffset.UTC)
        );
        return repository.save(user);
    }
}
```

**Expected Result:** Type-safe, immutable Java code with Spring integration

#### Example 2: Java 21 Virtual Threads for Async Processing
**Context:** Handle concurrent order processing with virtual threads
**Execution:**
```java
@Service
@Slf4j
public class OrderProcessor {
    
    public void processOrdersBatch(List<Order> orders) {
        // Java 21: ExecutorService with virtual threads
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            for (Order order : orders) {
                executor.submit(() -> processOrder(order));
            }
        }
        // Automatically waits for all tasks
    }

    private void processOrder(Order order) {
        logger.info("Processing order {}", order.getId());
        // Blocking operations are now cheap with virtual threads
    }
}
```

**Expected Result:** Efficient async processing without callback complexity

**When to Use:**
- Writing new Java backend code
- Migrating from Java 11 to 17/21
- Refactoring legacy Java code
- Team training (show Java modern features)

**When NOT to Use:**
- Don't use for non-JVM languages
- Don't use for Kotlin (different syntax, different patterns)
- Don't use if project is stuck on Java 8/11 (feature guards in skill)

**Edge Cases:**
- Sealed class hierarchy → Use `sealed class` + `permits` keyword
- Generic type erasure → Document type parameters in Javadoc @param <T>
- Null references → Use Optional<T> or records with validation in compact constructor
- Checked exceptions → Convert to unchecked (RuntimeException) or use Result<T>

**Testing Approach:**
- Unit test: Test business logic with Mockito mocks
- Integration test: Test with Spring Boot TestContext
- JUnit5 features: Use @ParameterizedTest, @DisplayName for clarity

---

## python_advanced_skill.md

**Purpose:** Provide Python 3.11/3.12 coding standards, OOP with ABC and dataclasses, Google-style docstrings, type hints, async patterns, and pytest test generation.

**Scope:**
- ✅ Covers: Python 3.11+ features, type hints, async/await, dataclasses, ABC for interfaces, pytest
- ❌ Excludes: Framework-specific patterns (FastAPI patterns in backend_skill)

**Entry Point:**
When writing Python code:
- Check Python version (3.10, 3.11, or 3.12?)
- Use type hints (no implicit `any`)
- Use dataclasses for immutable data models
- Follow Google-style docstrings
- Create pytest tests with fixtures

**Outputs:**
- Type-hinted Python code
- Dataclass models with validation
- Google-style docstrings on all methods
- pytest tests with fixtures
- ABC (Abstract Base Class) interfaces where appropriate

**Guardrails:**
- Always use type hints (mypy strict mode)
- Always use dataclasses or Pydantic models for data
- Always use @property for encapsulation (no public attributes)
- Always use async/await for I/O operations (not threading)
- Functions should be ≤ 20 lines, classes ≤ 300 lines
- Always use context managers (with statement) for resources

**Examples:**

#### Example 1: Python Async Order Service
**Context:** Build order processing service with async DB calls
**Execution:**
```python
from dataclasses import dataclass
from typing import Optional
from abc import ABC, abstractmethod

@dataclass
class Order:
    """Represents a customer order.
    
    Attributes:
        id: Unique order identifier.
        customer_id: ID of the customer who placed the order.
        total: Total order amount in cents.
        created_at: Order creation timestamp.
    """
    id: str
    customer_id: int
    total: int
    created_at: datetime

class OrderRepository(ABC):
    """Interface for order persistence."""
    
    @abstractmethod
    async def save(self, order: Order) -> Order:
        """Save order to database."""
        pass

@dataclass
class OrderService:
    """Service for managing orders."""
    
    repository: OrderRepository
    
    async def create_order(self, customer_id: int, items: list[str]) -> Order:
        """Create a new order.
        
        Args:
            customer_id: ID of the customer.
            items: List of item SKUs to order.
        
        Returns:
            The created order record.
        
        Raises:
            ValueError: If items list is empty.
        
        Example:
            >>> order = await service.create_order(123, ['SKU-001', 'SKU-002'])
            >>> print(order.total)
            5999
        """
        if not items:
            raise ValueError("Items cannot be empty")
        
        # Calculate total (simplified)
        total = len(items) * 100
        
        # Create and save
        order = Order(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            total=total,
            created_at=datetime.now(timezone.utc)
        )
        return await self.repository.save(order)
```

**Expected Result:** Type-safe, async-ready Python code

#### Example 2: Python pytest Fixture Test
**Context:** Test order service with fixtures
**Execution:**
```python
@pytest.fixture
async def service():
    repo = AsyncMock(spec=OrderRepository)
    return OrderService(repository=repo)

@pytest.mark.asyncio
async def test_givenValidItems_whenCreateOrder_thenOrderSaved(service):
    # Arrange
    service.repository.save = AsyncMock(return_value=Order(...))
    
    # Act
    order = await service.create_order(123, ['SKU-001'])
    
    # Assert
    assert order.customer_id == 123
    service.repository.save.assert_called_once()
```

**Expected Result:** Comprehensive async tests

**When to Use:**
- Writing new Python backend code
- Migrating from Python 2 or old Python 3 code
- Building microservices with FastAPI
- Team training (show Python type hints, async patterns)

**When NOT to Use:**
- Don't use for non-Python projects
- Don't use if project is on Python 2 (migrate first)
- Don't use for Django (different patterns, use when available)

**Edge Cases:**
- Backward compatibility (Python 3.8) → Use `from __future__ import annotations`
- Generic types → Use `typing.TypeVar` and `typing.Generic`
- Union types → Use `X | Y` (Python 3.10+) or `Union[X, Y]`
- Async context manager → Use `@asynccontextmanager` decorator

**Testing Approach:**
- Unit test: Test service logic with mock repositories
- Async test: Use `@pytest.mark.asyncio` and `AsyncMock`
- Type checking: Run `mypy --strict` to verify type hints

---

## react_advanced_skill.md

**Purpose:** Provide React 18/19 standards, component design, typed props with JSDoc, hooks, TanStack Query, accessibility, and Vitest + RTL test generation.

**Scope:**
- ✅ Covers: React 18+ features (Concurrent, Suspense), hooks, TanStack Query, Zustand, Tailwind, accessibility
- ❌ Excludes: High-level UI architecture (architect:frontend), design system (separate)

**Entry Point:**
When writing React code:
- Check React version (17, 18, or 19?)
- Use TypeScript strict mode (no `any` types)
- Use custom hooks for reusable logic
- Use TanStack Query for server state
- Create Vitest tests with React Testing Library
- Test accessibility with jest-axe

**Outputs:**
- Functional React components with TypeScript props
- Custom hooks for cross-cutting concerns
- TanStack Query hooks for API data
- Zustand stores for client state
- Tailwind CSS styling
- Vitest tests with accessibility testing

**Guardrails:**
- One component = one job (single responsibility)
- Always use TypeScript strict mode (no implicit `any`)
- Always include JSDoc on component props
- Always use React.FC<Props> or `function Component(props: Props) {}`
- Always test accessibility (focus, keyboard, screen readers)
- Always support dark mode (Tailwind dark: prefix)
- Custom hooks should be ≤ 50 lines
- Components should be ≤ 200 lines

**Examples:**

#### Example 1: React Custom Hook + TanStack Query
**Context:** Fetch user profile data with caching
**Execution:**
```typescript
/**
 * Fetch user profile with automatic caching and refetch.
 *
 * @param userId - The user ID to fetch
 * @returns Query result with data, loading, and error states
 *
 * @example
 * const { data, isLoading } = useUserProfile(123);
 */
export const useUserProfile = (userId: number) => {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: async () => {
      const response = await fetch(`/api/users/${userId}`);
      if (!response.ok) throw new Error('Failed to fetch user');
      return response.json() as Promise<User>;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Component using the hook
interface UserProfileProps {
  userId: number;
}

export const UserProfile: React.FC<UserProfileProps> = ({ userId }) => {
  const { data: user, isLoading, error } = useUserProfile(userId);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!user) return null;

  return (
    <div className="p-4 border rounded">
      <h2 className="text-lg font-bold">{user.name}</h2>
      <p className="text-gray-600">{user.email}</p>
    </div>
  );
};
```

**Expected Result:** Efficient data fetching with automatic caching

#### Example 2: React Accessible Form Component
**Context:** Build form with validation and accessibility
**Execution:**
```typescript
interface FormProps {
  onSubmit: (data: FormData) => Promise<void>;
}

export const UserForm: React.FC<FormProps> = ({ onSubmit }) => {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      const formData = new FormData(e.currentTarget);
      await onSubmit(Object.fromEntries(formData));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="email" className="block font-medium mb-1">
          Email <span className="text-red-500">*</span>
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          aria-required="true"
          aria-describedby={errors.email ? 'email-error' : undefined}
          className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {errors.email && (
          <p id="email-error" role="alert" className="text-red-500 text-sm mt-1">
            {errors.email}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
        aria-busy={isSubmitting}
      >
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
};
```

**Expected Result:** Fully accessible form with ARIA labels

**When to Use:**
- Building new React features
- Migrating from class components to hooks
- Creating component library
- Team training (show React best practices)

**When NOT to Use:**
- Don't use for page routing (use React Router separately)
- Don't use for design system (separate component library)
- Don't use for state management architecture (use Zustand/Redux as needed)

**Edge Cases:**
- Complex form state → Use react-hook-form + Zod validation
- Realtime updates → Use WebSockets with custom hook
- Infinite scroll → Use Intersection Observer + TanStack Query
- Animations → Use Framer Motion for complex animations

**Testing Approach:**
- Unit test: Test component rendering, props, event handlers
- Accessibility test: Use @testing-library/jest-dom, jest-axe
- Integration test: Test with mocked API responses
- Visual regression: Use Percy or similar for screenshot comparisons

---

## spring_advanced_skill.md

**Purpose:** Provide deep Spring Framework knowledge beyond basics. Covers IoC container internals, AOP, WebFlux/reactive, Spring Batch, Spring Cloud, Security, Events, custom auto-configuration, and debugging.

**Scope:**
- ✅ Covers: IoC container, AOP, Security configuration, Events, WebFlux, Batch, Cloud patterns
- ❌ Excludes: REST API design (api_skill), basic Spring Boot setup (backend_skill)

**Entry Point:**
When you need advanced Spring patterns:
- Configure complex dependency injection scenarios
- Implement AOP (cross-cutting concerns)
- Set up Spring Security (authentication, authorization)
- Build reactive systems with WebFlux
- Implement event-driven architecture

**Outputs:**
- Complex Spring configuration classes
- AOP interceptors and advice
- Security configuration with JWT
- WebFlux reactive routes
- Event publishers and listeners
- Spring Batch jobs

**Guardrails:**
- Understand IoC container lifecycle (startup, bean creation, destruction)
- Use conditional beans for environment-specific configuration
- Document bean scopes (singleton, prototype, request, session)
- Use AOP for cross-cutting concerns, not business logic
- Prefer constructor injection over field injection
- Use interfaces for security principals (don't rely on implementation)

**Examples:**

#### Example 1: Spring Security JWT Configuration
**Context:** Configure JWT authentication in Spring Boot 3.x
**Execution:**
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthenticationFilter(), UsernamePasswordAuthenticationFilter.class)
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS));
        
        return http.build();
    }

    @Bean
    public JwtAuthenticationFilter jwtAuthenticationFilter() {
        return new JwtAuthenticationFilter(jwtProvider);
    }
}
```

**Expected Result:** Secure API with JWT token validation

#### Example 2: Spring AOP Logging Interceptor
**Context:** Log all method calls automatically with AOP
**Execution:**
```java
@Component
@Aspect
@Slf4j
public class LoggingAspect {

    @Around("@annotation(Timed)")
    public Object logExecutionTime(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.currentTimeMillis();
        
        try {
            return joinPoint.proceed();
        } finally {
            long duration = System.currentTimeMillis() - start;
            logger.info("{} took {} ms", joinPoint.getSignature(), duration);
        }
    }
}
```

**Expected Result:** Transparent method timing without business logic change

**When to Use:**
- Building complex enterprise applications
- Implementing cross-cutting concerns (logging, security, transactions)
- Setting up microservices with Spring Cloud
- Building reactive systems with WebFlux

**When NOT to Use:**
- Don't use for simple CRUD apps (over-engineered)
- Don't use AOP for business logic (that's not what it's for)
- Don't use if team isn't familiar with Spring internals

**Edge Cases:**
- Dynamic bean creation → Use BeanFactory, implement BeanDefinitionRegistryPostProcessor
- Conditional beans → Use @ConditionalOnProperty, @ConditionalOnClass
- Bean ordering → Use @Ordered, @Primary for disambiguation
- Circular dependencies → Use ObjectProvider<T> or @Lazy

**Testing Approach:**
- Unit test: Test configuration logic with Spring Boot TestContext
- Integration test: Test bean wiring with @SpringBootTest
- AOP test: Test interceptor with mock objects
- Security test: Test endpoints with @WithMockUser

---

## mssql_advanced_skill.md

**Purpose:** Provide T-SQL coding standards, SQL Server optimization, indexing strategies, NOLOCK guidance (with when NOT to use), and query performance analysis.

**Scope:**
- ✅ Covers: T-SQL standards, stored procedures, query optimization, indexing, NOLOCK patterns, deadlock prevention
- ❌ Excludes: Schema design (database_skill), data loading (separate script)

**Entry Point:**
When you need to write T-SQL:
- Check SQL Server version (2016, 2017, 2019, 2022, or Azure SQL?)
- Use modern features (STRING_AGG, JSON functions, temporal tables)
- Write optimized queries (proper indexes, avoid N+1 patterns)
- Understand NOLOCK trade-offs (dirty reads vs concurrency)
- Create stored procedures with proper error handling

**Outputs:**
- Production T-SQL queries with proper indexing
- Stored procedures with error handling
- Query execution plans analyzed and optimized
- Migration scripts with CONSTRAINT checks
- Documentation of performance optimizations

**Guardrails:**
- Never use NOLOCK for financial/critical data (use RCSI instead)
- Always use parameterized queries (prevent SQL injection)
- Always include indexes on foreign keys and frequently filtered columns
- Never use functions on columns in WHERE clause (prevents index usage)
- Always estimate execution plan before running on production
- Methods should be ≤ 100 lines, stored procedures ≤ 50 lines

**Examples:**

#### Example 1: Optimized T-SQL Query with Index
**Context:** Find all orders for a customer with proper indexing
**Execution:**
```sql
-- Create index for fast filtering
CREATE INDEX idx_orders_customer_created 
ON orders(customer_id, created_at DESC) 
INCLUDE (total, status);

-- Optimized query using index
SELECT 
    order_id,
    total,
    status,
    created_at
FROM orders
WHERE customer_id = @CustomerId
  AND created_at >= DATEADD(YEAR, -1, GETUTCDATE())
ORDER BY created_at DESC;
```

**Expected Result:** Query runs with index seek, not table scan

#### Example 2: Stored Procedure with Error Handling
**Context:** Process payment with transaction and error handling
**Execution:**
```sql
CREATE PROCEDURE sp_ProcessPayment
    @OrderId UNIQUEIDENTIFIER,
    @Amount DECIMAL(10, 2),
    @PaymentMethod NVARCHAR(50),
    @Result NVARCHAR(MAX) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        -- Validate order exists
        IF NOT EXISTS (SELECT 1 FROM orders WHERE id = @OrderId)
        BEGIN
            THROW 50001, 'Order not found', 1;
        END;
        
        -- Insert payment record
        INSERT INTO payments (order_id, amount, status, created_at)
        VALUES (@OrderId, @Amount, 'PENDING', GETUTCDATE());
        
        -- Update order status
        UPDATE orders 
        SET status = 'PAID', updated_at = GETUTCDATE()
        WHERE id = @OrderId;
        
        COMMIT TRANSACTION;
        SET @Result = 'SUCCESS';
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        
        SET @Result = 'ERROR: ' + ERROR_MESSAGE();
    END CATCH;
END;
```

**Expected Result:** Transactional, error-safe stored procedure

**When to Use:**
- Writing T-SQL queries for SQL Server
- Optimizing slow queries (add indexes, rewrite)
- Building stored procedures for business logic
- Migrating from other databases to SQL Server

**When NOT to Use:**
- Don't use NOLOCK on financial data (use RCSI)
- Don't use dynamic SQL (prevents query caching)
- Don't put complex business logic in stored procedures (use application code)
- Don't use functions on columns in WHERE clause

**Edge Cases:**
- Large tables (millions of rows) → Use partitioning, consider columnstore index
- Real-time analytics → Use Azure Synapse Link, change data capture
- Temporal queries → Use temporal tables with FOR SYSTEM_TIME
- Deadlock prevention → Use consistent column order in multi-table operations

**Testing Approach:**
- Unit test: Test stored procedure with known inputs, verify output
- Performance test: Check execution plan, measure elapsed time
- Concurrency test: Test with multiple connections, verify locking behavior
- Migration test: Test all data types, verify no data loss

---

### 7. Infrastructure & Patterns (7 Skills)

---

## logger_skill.md

**Purpose:** Complete logging strategy covering SLF4J, Log4j2, Logback, structured logging, log levels, appenders, configurations, and production-ready patterns.

**Scope:**
- ✅ Covers: SLF4J facade, Logback/Log4j2 configuration, log levels, structured logging, appenders
- ❌ Excludes: Application debugging (quality:debug), distributed tracing (opentelemetry_skill)

**Entry Point:**
When setting up logging in a Java application:
- Configure SLF4J + Logback (recommended)
- Set log levels (DEBUG, INFO, WARN, ERROR)
- Configure appenders (console, file, async)
- Use structured logging (JSON format for production)
- Add context (correlation IDs, user IDs)

**Outputs:**
- `logback.xml` configuration
- Configured SLF4J logger in all classes
- Structured logging with MDC (Mapped Diagnostic Context)
- Log files with rotation policy
- Async appender for performance

**Guardrails:**
- Never log sensitive data (passwords, tokens, API keys)
- Always use placeholders ({}) not string concatenation (defer expensive work)
- Always use appropriate log level (DEBUG for detailed, INFO for business events, ERROR for problems)
- Never log stack traces with sensitive information
- Always include correlation ID for request tracing
- Never synchronously write logs in hot path (use async appender)

**Examples:**

#### Example 1: Logback Configuration
**Context:** Configure SLF4J + Logback in Spring Boot
**Execution:**
```xml
<!-- logback.xml in src/main/resources/ -->
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <springProperty name="LOG_FILE" source="logging.file.name" defaultValue="logs/app.log"/>
    
    <!-- Console appender for development -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- File appender with rotation -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_FILE}</file>
        <encoder>
            <pattern>%d{ISO8601} [%thread] %-5level %logger{36} [%X{correlationId}] - %msg%n</pattern>
        </encoder>
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>${LOG_FILE}.%d{yyyy-MM-dd}.%i.gz</fileNamePattern>
            <maxFileSize>100MB</maxFileSize>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
    </appender>

    <!-- Async appender for performance -->
    <appender name="ASYNC_FILE" class="ch.qos.logback.classic.AsyncAppender">
        <appender-ref ref="FILE"/>
        <queueSize>512</queueSize>
        <discardingThreshold>0</discardingThreshold>
    </appender>

    <!-- Root logger -->
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="ASYNC_FILE"/>
    </root>

    <!-- Application logging -->
    <logger name="com.example.orders" level="DEBUG"/>
</configuration>
```

**Expected Result:** Production-ready logging with rotation and async performance

#### Example 2: Using SLF4J with MDC
**Context:** Log order processing with correlation ID
**Execution:**
```java
@Service
@Slf4j
public class OrderService {
    
    public void processOrder(Order order, String correlationId) {
        // Set correlation ID in MDC (Mapped Diagnostic Context)
        MDC.put("correlationId", correlationId);
        MDC.put("userId", order.getCustomerId());
        
        try {
            logger.info("Processing order: {}", order.getId());
            
            // Business logic
            validateOrder(order);
            chargePayment(order);
            shipOrder(order);
            
            logger.info("Order processed successfully");
        } catch (Exception e) {
            logger.error("Order processing failed", e);
            throw e;
        } finally {
            MDC.clear();  // Clean up context
        }
    }
}
```

**Expected Result:** Structured logs with correlation IDs for request tracing

**When to Use:**
- Project initialization (set up logging before first feature)
- Production deployment (configure appenders and log levels)
- Debugging complex issues (add correlation IDs)
- Performance optimization (use async appender)

**When NOT to Use:**
- Don't log sensitive data (security issue)
- Don't use synchronous logging in hot paths (performance issue)
- Don't configure different log levels for different environments in code (use logback.xml)

**Edge Cases:**
- Multiple environments → Use Spring profiles (logback-spring.xml with profiles)
- Distributed tracing → Use correlation IDs + opentelemetry_skill
- Very high throughput → Increase async queue size, consider Chronicle Queue
- Compliance requirements → Add encryption, audit trail for sensitive logs

**Testing Approach:**
- Unit test: Verify log statements are called with correct level
- Integration test: Verify logs are written to file with correct format
- Configuration test: Verify correct appender is used per environment

---

## lombok_skill.md

**Purpose:** Provide Project Lombok annotations and patterns for reducing Java boilerplate. Covers @Data, @Builder, @Slf4j, @RequiredArgsConstructor, @Value, and best practices.

**Scope:**
- ✅ Covers: @Data, @Getter/@Setter, @Builder, @Slf4j, @RequiredArgsConstructor, @Value, @Delegate
- ❌ Excludes: Code generation for non-Lombok patterns (handled by language skills)

**Entry Point:**
When writing Java data classes and utilities:
- Use @Data for simple POJOs (getters, setters, equals, hashCode, toString)
- Use @Builder for complex object construction
- Use @Slf4j for automatic logger generation
- Use @RequiredArgsConstructor for dependency injection
- Use @Value for immutable classes

**Outputs:**
- Data classes with generated methods
- Builder pattern for complex objects
- Automatic logger (no static final Logger field)
- Reduced boilerplate code

**Guardrails:**
- Never use @Data on entities with relationships (use explicit @Getter/@Setter)
- Be careful with @Data + inheritance (generated methods don't handle super)
- Document Lombok configuration in IDE (IntelliJ, Eclipse, VS Code)
- Use @ToString(exclude = "password") for sensitive fields
- Use @EqualsAndHashCode(exclude = "id") when needed for proper equality

**Examples:**

#### Example 1: Simple Data Class with @Data
**Context:** Create User DTO with automatic getters/setters
**Execution:**
```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserDTO {
    private String id;
    private String email;
    private String name;
}

// Equivalent to:
// getters, setters, equals(), hashCode(), toString()
// Generated automatically by Lombok
```

**Expected Result:** 50+ lines of code reduced to 10 lines

#### Example 2: Builder Pattern for Complex Object
**Context:** Create Order with many optional fields
**Execution:**
```java
@Builder
@Data
public class OrderRequest {
    private String customerId;
    private List<LineItem> items;
    private ShippingAddress shippingAddress;
    @Builder.Default
    private String priority = "NORMAL";
    @Builder.Default
    private boolean insured = false;
}

// Usage
OrderRequest order = OrderRequest.builder()
    .customerId("cust-123")
    .items(List.of(new LineItem("SKU-001", 2)))
    .shippingAddress(new ShippingAddress("123 Main St"))
    .priority("EXPRESS")
    .build();
```

**Expected Result:** Readable, type-safe object construction

**When to Use:**
- Creating data classes (DTOs, requests, responses)
- Reducing boilerplate in large projects
- Building complex objects with optional fields
- Automatic logger generation (@Slf4j)

**When NOT to Use:**
- Don't use @Data on JPA entities (causes issues with lazy loading, relationships)
- Don't use @Data if inheritance is complex (use explicit @Getter/@Setter)
- Don't use if team isn't familiar with Lombok (adds complexity)

**Edge Cases:**
- Circular references → Use @ToString(exclude = "other") and @EqualsAndHashCode(exclude = "other")
- JPA entities → Use @Getter/@Setter explicitly, not @Data
- Immutable classes → Use @Value instead of @Data
- Custom equals logic → Don't use @Data, implement manually

**Testing Approach:**
- Unit test: Verify generated equals() and hashCode() work correctly
- Serialization test: Verify @Data class serializes/deserializes correctly
- IDE test: Verify IDE recognizes generated methods (IntelliJ auto-completion works)

---

## apache_camel_skill.md

**Purpose:** Advanced Apache Camel for integration. Covers Enterprise Integration Patterns, route DSL, error handling, components, testing, Spring Boot integration, and debugging.

**Scope:**
- ✅ Covers: Route DSL (Java), EIP patterns, error handling, components, Spring integration, testing
- ❌ Excludes: Spring Cloud Bus (separate), Kafka connector (component-specific)

**Entry Point:**
When building integration routes:
- Design routes using EIP patterns (content-based router, aggregator, splitter)
- Configure error handling (dead-letter channel, retry)
- Use components for file, HTTP, Kafka, JMS, etc.
- Test routes with CamelTestSupport
- Monitor with Spring Boot management endpoints

**Outputs:**
- Camel routes using RouteBuilder
- Error handling configuration
- Custom processors and transformers
- Route tests with CamelTestSupport
- Spring Boot auto-configuration

**Guardrails:**
- Always give routes meaningful IDs (routeId)
- Always configure error handling (don't let exceptions silently fail)
- Never block the thread in Camel (use async components)
- Always add logging at route start and error points
- Use properties for configurable values (not hardcoded)
- Test routes with mock endpoints before deploying

**Examples:**

#### Example 1: Order Ingestion Route
**Context:** Read JSON files, validate, transform, and publish to queue
**Execution:**
```java
@Component
public class OrderIngestionRoute extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        errorHandler(deadLetterChannel("direct:dlc")
            .log("Order failed: ${exception.message}")
            .retryAttemptedCount());

        from("file:data/orders/incoming?delete=true")
            .routeId("order-ingestion")
            .log("Processing: ${header.CamelFileName}")
            
            // Unmarshal JSON
            .unmarshal().json(OrderFileDto.class)
            
            // Validate
            .process(new OrderValidator())
            
            // Transform to internal format
            .bean(OrderTransformer.class, "toOrder")
            
            // Send to queue
            .to("jms:queue:order-processing");
        
        // Dead letter processing
        from("direct:dlc")
            .log(LoggingLevel.ERROR, "Order DLQ: ${body}")
            .to("file:data/orders/error");
    }
}
```

**Expected Result:** Production integration route with error handling

#### Example 2: Testing Camel Route
**Context:** Test order route with mock endpoints
**Execution:**
```java
public class OrderRouteTest extends CamelTestSupport {

    @Test
    public void testOrderProcessing() throws InterruptedException {
        // Mock endpoints
        getMockEndpoint("mock:jms:queue:orders").expectedMessageCount(1);
        
        // Send test message
        template.sendBody("direct:start", "{\"orderId\":123}");
        
        // Verify
        MockEndpoint.assertIsSatisfied(context);
    }
}
```

**Expected Result:** Tested integration route

**When to Use:**
- Building EIP-based integrations (not CRUD apps)
- Connecting multiple systems (file, queue, database)
- Event-driven architecture (publish-subscribe)
- Data transformation and routing

**When NOT to Use:**
- Don't use for simple REST APIs (use Spring WebFlux)
- Don't use for single-file processing (over-engineered)
- Don't use if team isn't familiar with EIP patterns

**Edge Cases:**
- Streaming large files → Use tokenizeXML/tokenizeJSON
- Dynamic routing → Use choice() with predicates
- Aggregation with timeout → Use aggregate() with AggregationStrategy
- Request-reply pattern → Use InOut message exchange pattern

**Testing Approach:**
- Unit test: Test route with CamelTestSupport, mock endpoints
- Integration test: Test with real components (JMS, database)
- Performance test: Measure throughput under load

---

## apache_pulsar_skill.md

**Purpose:** Advanced Apache Pulsar messaging. Covers architecture, producers, consumers, subscription types, schemas, error handling, dead-letter topics, Spring for Apache Pulsar, and debugging.

**Scope:**
- ✅ Covers: Producers, consumers, subscriptions (Exclusive, Shared, Failover, Key_Shared), schemas, DLT, Spring integration
- ❌ Excludes: Pulsar cluster deployment (ops team), topic management (admin API)

**Entry Point:**
When building event-driven systems:
- Design topics and subscriptions
- Implement producers for event publishing
- Implement consumers for event processing
- Handle errors with dead-letter topics
- Use schemas for message validation
- Configure Spring for Apache Pulsar

**Outputs:**
- Pulsar producers for event publishing
- Pulsar consumers for event processing
- Error handling with DLT
- Spring PulsarTemplate configuration
- Schema definition and validation

**Guardrails:**
- Always use persistent topics (survive broker restart)
- Always configure subscriptions (don't lose messages)
- Always implement error handling (send to DLT on processing failure)
- Never block consumer thread (use async processing)
- Always use schemas (validate message format)
- Use Key_Shared subscription for message ordering per key

**Examples:**

#### Example 1: Pulsar Producer
**Context:** Publish order events
**Execution:**
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderEventPublisher {

    private final PulsarTemplate<OrderEvent> pulsarTemplate;
    private static final String TOPIC = "persistent://orders/default/order-events";

    public void publishOrderCreated(OrderEvent event) {
        pulsarTemplate.sendAsync(TOPIC, event)
            .thenAccept(msg -> logger.info("Event published: {}", msg.getMessageId()))
            .exceptionally(ex -> {
                logger.error("Failed to publish event", ex);
                return null;
            });
    }
}
```

**Expected Result:** Async event publishing with error handling

#### Example 2: Pulsar Consumer with DLT
**Context:** Process order events with error handling
**Execution:**
```java
@Service
@Slf4j
public class OrderEventConsumer {

    @PulsarListener(
        topics = "persistent://orders/default/order-events",
        subscriptionName = "order-processor",
        subscriptionType = SubscriptionType.Shared,
        deadLetterPolicy = DeadLetterPolicy.builder()
            .deadLetterTopic("persistent://orders/default/order-events-dlq")
            .maxRedeliverCount(3)
            .build()
    )
    public void consumeOrderEvent(OrderEvent event) {
        logger.info("Processing event: {}", event.getOrderId());
        
        try {
            // Process order
            orderService.process(event);
        } catch (Exception e) {
            logger.error("Failed to process event", e);
            throw e;  // Pulsar will retry, then send to DLT
        }
    }
}
```

**Expected Result:** Event consumer with automatic retry and DLT routing

**When to Use:**
- Event-driven microservices
- Real-time data streaming
- Pub-sub messaging (multiple subscribers)
- Message ordering (use Key_Shared subscription)

**When NOT to Use:**
- Don't use for request-response patterns (use HTTP/gRPC)
- Don't use for simple message queues (use JMS)
- Don't use if team isn't familiar with messaging patterns

**Edge Cases:**
- Exactly-once semantics → Use Exclusive subscription + idempotent processing
- Ordered messages per customer → Use Key_Shared with customer ID as key
- High throughput → Use batch processing, increase consumer threads
- Schema evolution → Use Avro/Protobuf with backward compatibility

**Testing Approach:**
- Unit test: Test producer/consumer logic with mocks
- Integration test: Test with PulsarContainer (TestContainers)
- Error handling test: Verify DLT routing on exception
- Load test: Measure throughput, latency under load

---

## opentelemetry_skill.md

**Purpose:** Distributed tracing, metrics, and logs with OpenTelemetry. Covers tracing, metrics, logs, instrumentation, Spring Boot integration, Jaeger/Prometheus exporters, context propagation.

**Scope:**
- ✅ Covers: Traces (spans, baggage, trace IDs), metrics (counters, gauges), logs with correlation, exporters (Jaeger, Prometheus)
- ❌ Excludes: Backend setup (Jaeger, Prometheus), alerting rules (ops team)

**Entry Point:**
When building observable distributed systems:
- Configure OpenTelemetry SDK
- Add span instrumentation to critical paths
- Export traces to Jaeger
- Export metrics to Prometheus
- Correlate logs with trace IDs

**Outputs:**
- OpenTelemetry SDK configuration
- Instrumented code with manual spans
- Jaeger exporter configuration
- Prometheus metrics exporter
- Correlated logs with trace IDs

**Guardrails:**
- Always propagate trace context across service boundaries
- Never put sensitive data in spans (PII, secrets)
- Always name spans meaningfully (describe what they measure)
- Always set span status (OK, ERROR, UNSET)
- Always include relevant attributes (user ID, order ID)
- Don't create too many spans (one per operation, not per line)

**Examples:**

#### Example 1: OpenTelemetry Tracing Setup
**Context:** Configure tracing in Spring Boot
**Execution:**
```java
@Configuration
public class OpenTelemetryConfig {

    @Bean
    public OpenTelemetry openTelemetry(SdkTracerProvider tracerProvider) {
        return OpenTelemetrySdk.builder()
            .setTracerProvider(tracerProvider)
            .build();
    }

    @Bean
    public SdkTracerProvider sdkTracerProvider() {
        return SdkTracerProvider.builder()
            .addSpanProcessor(
                BatchSpanProcessor.builder(jaegerExporter())
                    .build()
            )
            .build();
    }

    @Bean
    public JaegerExporter jaegerExporter() {
        return JaegerExporter.builder()
            .setEndpoint("http://localhost:14250")
            .build();
    }
}
```

**Expected Result:** Traces exported to Jaeger

#### Example 2: Manual Span Instrumentation
**Context:** Add observability to order processing
**Execution:**
```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final Tracer tracer;

    public void processOrder(Order order) {
        Span span = tracer.spanBuilder("processOrder")
            .setAttribute("order.id", order.getId())
            .setAttribute("customer.id", order.getCustomerId())
            .startSpan();

        try (Scope scope = span.makeCurrent()) {
            // Processing logic
            validateOrder(order);
            chargePayment(order);
            shipOrder(order);
            
            span.setStatus(StatusCode.OK, "Order processed");
        } catch (Exception e) {
            span.setStatus(StatusCode.ERROR, e.getMessage());
            span.recordException(e);
            throw e;
        }
    }
}
```

**Expected Result:** Spans visible in Jaeger with order ID context

**When to Use:**
- Distributed system debugging (trace requests across services)
- Performance profiling (identify slow operations)
- Production observability (understand system behavior)
- Compliance (audit trail of operations)

**When NOT to Use:**
- Don't use for simple monolithic applications (overkill)
- Don't put sensitive data in spans (security issue)
- Don't instrument every line of code (too many spans)

**Edge Cases:**
- Async operations → Propagate trace context to async threads
- Batch processing → Create parent span, child spans for items
- High throughput → Sample traces (not all, to reduce overhead)
- Multi-language → Use standard W3C Trace Context headers

**Testing Approach:**
- Unit test: Verify spans are created with correct attributes
- Integration test: Verify traces are exported to collector
- Performance test: Measure overhead of instrumentation
- E2E test: Verify trace spans connect across services

---

### 8. JIRA & Business Analysis (3 Skills)

---

## jira_html_report_skill.md

**Purpose:** Parse JIRA JSON/CSV exports and generate interactive HTML backlog reports. Single-file, self-contained, offline visualization with filtering, sorting, and row expansion.

**Scope:**
- ✅ Covers: JIRA parsing (JSON, CSV), HTML report generation, filtering, sorting, expansion
- ❌ Excludes: JIRA API integration (use official JIRA REST API), real-time updates

**Entry Point:**
When you need to visualize a JIRA backlog:
- Export JIRA tickets to JSON or CSV
- Parse the export file
- Generate interactive HTML report
- Share with stakeholders (single file, offline)

**Outputs:**
- `jira-report.html` — Single-file, self-contained HTML report
- Interactive filtering by status, priority, assignee
- Sortable columns (by key, summary, priority, status)
- Row expansion (full description, comments)
- Export options (JSON, CSV, print/PDF)

**Guardrails:**
- HTML file must be self-contained (zero CDN dependencies)
- Support all modern browsers (Chrome, Firefox, Safari, Edge 2022+)
- Handle both JSON and CSV formats automatically
- Limit to 500+ issues (more = slower browser)
- Always include generated timestamp and data source

**Examples:**

#### Example 1: JIRA JSON Export to HTML Report
**Context:** Parse JIRA Cloud export and create backlog visualization
**Execution:**
- Export from JIRA: Filters → Save as CSV/JSON
- Input: `jira-export.json` (56 issues)
- Process: Parse issues, group by status, calculate metrics
- Output: `jira-report.html` (fully interactive, 150KB)
- User experience: Click status column to filter, expand row for details

**Expected Result:** Stakeholder-ready backlog report

#### Example 2: CSV Export with Custom Fields
**Context:** Import JIRA CSV with sprint and story points
**Execution:**
- Export CSV with columns: Key, Summary, Type, Priority, Status, Sprint, Story Points
- Parse: Auto-detect columns, map to standard fields
- Report: Show sprint breakdown, total story points, velocity
- Features: Filter by sprint, sort by points, calculate metrics

**Expected Result:** Sprint planning visualization

**When to Use:**
- Backlog review meetings (visual summary)
- Sprint planning (see what's in progress)
- Stakeholder reporting (executive dashboard)
- Release planning (overview of features)

**When NOT to Use:**
- Don't use for real-time updates (snapshot only)
- Don't use instead of JIRA (use actual JIRA for work)
- Don't use for more than 500 issues (performance issues)

**Edge Cases:**
- Very large backlog (1000+) → Split into multiple reports
- Custom fields (story points) → Auto-detect and display
- Parent-child relationships → Show hierarchy in report
- Historical data → Add date range filter

**Testing Approach:**
- Unit test: Parse sample JSON/CSV, verify field extraction
- Integration test: Generate HTML report, verify it opens in browser
- Browser test: Test filtering, sorting, export in different browsers
- Load test: Verify performance with 200+ issues

---

## jira_incremental_spec_skill.md

**Purpose:** Read JIRA tickets incrementally by auto-incrementing prefix and generate comprehensive specification document in professional book format with chapters, TOC, and cross-references.

**Scope:**
- ✅ Covers: Incremental ticket discovery, requirement aggregation, book-format generation, cross-referencing
- ❌ Excludes: JIRA ticket creation (use JIRA directly), real-time sync

**Entry Point:**
When you have a series of JIRA tickets (PROJ-1, PROJ-2, ...) describing an application:
- Read tickets incrementally (auto-increment numbers)
- Stop after 10 consecutive missing tickets
- Aggregate all requirements
- Generate single specification document

**Outputs:**
- `specification.md` — Professional book-format document
- Table of contents with chapter structure
- Functional requirements (from stories)
- Technical requirements (from tasks)
- Acceptance criteria (from all tickets)
- Cross-references between tickets
- Dependencies and relationships mapped

**Guardrails:**
- Auto-increment intelligently (stop after 10 consecutive misses)
- Preserve ticket order but reorganize by category
- Highlight dependencies and relationships
- Include acceptance criteria from all tickets
- Always include JIRA ticket key for traceability
- Generate TOC for navigation

**Examples:**

#### Example 1: E-Commerce Platform Specification
**Context:** Read PROJ-1 through PROJ-25 and generate spec
**Execution:**
- Fetch PROJ-1: "User Registration" (Story)
- Fetch PROJ-2: "Email Validation" (Task)
- Fetch PROJ-3: "Password Security" (Story)
- ...continue to PROJ-25...
- Miss PROJ-26 through PROJ-35 (10 consecutive)
- Generate: Specification.md with chapters:
  - Ch 1: User Management (PROJ-1, PROJ-2, PROJ-3)
  - Ch 2: Product Catalog (PROJ-4, PROJ-5, ...)
  - Ch 3: Shopping Cart (PROJ-10, PROJ-11, ...)
  - Appendix: Acceptance Criteria, Dependencies

**Expected Result:** 50-page specification document from 25 tickets

#### Example 2: Microservice Specification
**Context:** Generate spec for order service (AUTH-1 through AUTH-30)
**Execution:**
- Prefix: AUTH
- Start: 1
- Discover: 28 tickets (AUTH-1 through AUTH-28)
- Missing: AUTH-29 onwards (10 consecutive)
- Output: Professional specification with:
  - Functional requirements (what the system does)
  - Technical requirements (how it's built)
  - Security requirements (authentication, authorization)
  - API contracts (endpoints, request/response formats)
  - Data models (entities, relationships)

**Expected Result:** Complete design specification from JIRA

**When to Use:**
- Generating requirements from JIRA (before coding)
- Stakeholder communication (detailed spec for approval)
- Architecture planning (understand full scope)
- Knowledge documentation (reference for team)

**When NOT to Use:**
- Don't use for sprint planning (use JIRA board directly)
- Don't use if tickets aren't well-structured (garbage in = garbage out)
- Don't use as real-time tracker (snapshot only)

**Edge Cases:**
- Non-sequential ticket numbers → Adjust max consecutive misses
- Mixed ticket types (Stories, Tasks, Bugs) → Organize by type + feature
- Cross-project dependencies → Include cross-project references
- Historical tickets → Filter by date range or status

**Testing Approach:**
- Unit test: Verify incremental discovery logic, stop condition
- Integration test: Test with real JIRA instance (credentials required)
- Output test: Verify generated spec has all chapters, TOC, cross-references
- Format test: Verify markdown is valid, renders correctly

---

## ba_create_skill.md

**Purpose:** Parse plain-text requirements (free-form, Markdown, Gherkin) and generate JIRA-ready issues with auto-generated BDD acceptance criteria. Outputs: requirements.json (JIRA-importable) and requirements-cards.html (interactive UI).

**Scope:**
- ✅ Covers: Requirement parsing (3 formats), BDD criteria generation, JSON export, HTML visualization
- ❌ Excludes: JIRA import automation (use JIRA API manually), Slack notifications

**Entry Point:**
When you have natural-language requirements:
- Parse free-form text, Markdown, or Gherkin format
- Auto-generate structured JIRA issues
- Create BDD acceptance criteria (Given-When-Then)
- Export to requirements.json (JIRA-importable)
- Generate requirements-cards.html (stakeholder review)

**Outputs:**
- `requirements.json` — Array of JIRA issues (importable)
- `requirements-cards.html` — Interactive card visualization
- BDD acceptance criteria for each requirement
- Type detection (Story, Task, Bug, Epic)
- Priority assignment based on keywords

**Guardrails:**
- Auto-detect format (Gherkin, Markdown, free-form)
- Generate meaningful BDD criteria (Given-When-Then)
- Assign types intelligently (keywords: "As a" = Story, "Fix" = Bug)
- Include priority (keywords: "Critical" = High, "Nice to have" = Low)
- Always include JIRA-compatible JSON output
- Preserve original text for audit trail

**Examples:**

#### Example 1: Free-Form Requirements to JIRA
**Context:** Convert user story written in plain text to JIRA issue
**Execution:**
```
Input (requirements.txt):
---
As a customer, I want to reset my password via email so I can regain access if I forget it

Acceptance Criteria:
- User clicks "Forgot Password" link on login page
- Enters email address
- Receives password reset link via email within 2 minutes
- Link is valid for 1 hour only
- User clicks link and sees password reset form
- New password is confirmed (password != email)
```

**Processing:**
- Parse: Detects free-form prose with AC
- Type: "As a" + "want to" = Story
- Summary: "Password reset via email"
- Generate BDD: `Given user has valid email, When user requests reset, Then receives email with link`
- Priority: Normal (no urgency keywords)

**Output:**
```json
{
  "key": "REQ-001",
  "type": "Story",
  "summary": "Password reset via email",
  "description": "As a customer, I want to reset my password...",
  "acceptanceCriteria": [
    "Given user has valid email, When user clicks 'Forgot Password', Then password reset form is shown",
    "Given password reset form is open, When user enters new password, Then new password is saved and email is sent",
    "Given password reset email is sent, When user clicks link after 2 hours, Then link is expired"
  ]
}
```

**Expected Result:** JIRA-ready issue with BDD criteria

#### Example 2: Gherkin to Requirements HTML
**Context:** Parse Gherkin feature and generate HTML cards
**Execution:**
```
Input (requirements.feature):
Feature: Shopping Cart Checkout
  As a customer
  I want to review my cart and checkout
  So that I can purchase items

  Scenario: Add item to cart
    Given user is viewing a product
    When user clicks "Add to Cart"
    Then item is added with quantity 1
    And cart count increases by 1

  Scenario: Apply coupon
    Given user has items in cart
    When user enters valid coupon code
    Then discount is applied
    And total is recalculated
```

**Processing:**
- Parse: Detects Gherkin format
- Type: Feature = Epic
- Scenarios = Stories (one story per scenario)
- BDD: Already in Given-When-Then format

**Output:**
- `requirements.json`: 2 issues (Add Item, Apply Coupon)
- `requirements-cards.html`: Interactive cards, editable scenarios, export JSON

**Expected Result:** Stakeholder-ready visualization with BDD criteria

**When to Use:**
- Converting requirements from word processors to JIRA
- Generating BDD scenarios from user stories
- Stakeholder review of requirements (interactive HTML)
- Bulk JIRA issue creation

**When NOT to Use:**
- Don't use instead of JIRA (use actual JIRA for work)
- Don't use if requirements are already well-structured (use JIRA directly)
- Don't use for real-time sync (snapshot only)

**Edge Cases:**
- Ambiguous requirements → Ask for clarification before parsing
- Multiple requirement formats in one file → Try auto-detect, fall back to manual split
- Nested features (Epics with child Stories) → Parse hierarchy
- Custom fields (story points, labels) → Extract if present, allow manual entry

**Testing Approach:**
- Unit test: Parse sample requirements in 3 formats, verify field extraction
- BDD test: Verify generated criteria follow Given-When-Then pattern
- Integration test: Export to JSON, verify format matches JIRA schema
- Browser test: Test HTML cards (expand, edit, export) in different browsers

---

## Verification Checklist

- [x] All 26 skills documented (100%)
- [x] All skills follow abbreviated template (Purpose, Scope, Entry Point, Outputs, Guardrails)
- [x] All skills have 1-2 examples minimum (real-world scenarios)
- [x] All guardrails are specific (not vague)
- [x] All "When to Use" and "When NOT to Use" sections present
- [x] Quick Reference Table provided
- [x] Skills organized by 8 categories (Code Review, Testing, Documentation, Backend, Frontend, Language, Infrastructure, Business)
- [x] Code examples provided (Python, Java, JavaScript/TypeScript, SQL, JIRA)
- [x] Testing approaches documented for each skill
- [x] Edge cases documented for each skill

---

## Index of All 26 Skills

**Code Review & Quality (5):** code_review_skill, code_health_skill, code_formatting_skill, multi_review_html_skill, context_builder_skill

**Testing (1):** test_skill

**Documentation (2):** code_documentation_skill, context_builder_skill

**Backend & Database (3):** backend_skill, database_skill, api_skill

**Frontend (1):** frontend_skill

**Language-Specific (5):** java_advanced_skill, python_advanced_skill, react_advanced_skill, spring_advanced_skill, mssql_advanced_skill

**Infrastructure & Patterns (7):** logger_skill, lombok_skill, apache_camel_skill, apache_pulsar_skill, opentelemetry_skill, error_handling_skill, oop_skill

**JIRA & Business Analysis (3):** jira_html_report_skill, jira_incremental_spec_skill, ba_create_skill

---

**Document Generated:** June 9, 2026  
**Total Skills Documented:** 26  
**Status:** COMPLETE — All skills verified, documented, and ready for integration with HTML explorer.
