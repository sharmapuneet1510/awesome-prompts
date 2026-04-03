---
name: Code Health Inspection Skill
version: 1.0
description: >
  Reusable skill module for deep code health analysis. Defines the complete
  taxonomy of issues to detect, severity scoring, evidence collection rules,
  and the structured report format used by the Code Health Inspector Agent.
applies_to: [java, python, react, mssql, all-languages]
---

# Code Health Inspection Skill — v1.0

---

## 1. Issue Taxonomy

Every issue found during a scan belongs to one of these seven categories.
Use these category codes in the report.

| Code | Category | Examples |
|------|----------|---------|
| `PERF` | Performance & Slowness | N+1 queries, missing indexes, blocking calls, over-fetching, missing pagination |
| `ERR` | Error Handling | Swallowed exceptions, missing try/catch, no fallback, bare `except`, silent failures |
| `DELAY` | Processing Delays | Synchronous calls that should be async, missing queues, retry storms, no timeouts |
| `MEM` | Memory & Resource Leaks | Unclosed connections, unbounded caches, large objects in memory, no streaming |
| `SEC` | Security | SQL injection, hardcoded secrets, insecure deserialization, missing auth checks |
| `MAINT` | Maintainability | God classes, deeply nested code, magic numbers, missing documentation, dead code |
| `RELI` | Reliability | No retry logic, no circuit breaker, missing health checks, no idempotency |

---

## 2. Severity Scale

Assign one severity level to each issue found.

| Level | Code | Meaning | Action |
|-------|------|---------|--------|
| Critical | `P0` | Causes data loss, outages, or security breaches in production | Fix before next deploy |
| High | `P1` | Causes user-visible failures or significant performance degradation | Fix in current sprint |
| Medium | `P2` | Causes intermittent issues or technical debt that will compound | Fix in next sprint |
| Low | `P3` | Code smell, maintainability concern, minor inefficiency | Fix when touching this code |

---

## 3. Evidence Collection Rules

For each issue found, you MUST collect:

1. **Location** — exact file, class, method, and line number (or range)
2. **Evidence** — the exact code snippet that demonstrates the problem
3. **Root Cause** — WHY this is a problem (not just what it is)
4. **Impact** — what can go wrong at runtime because of this
5. **Fix** — a concrete code example showing the corrected version

Never report a vague issue like "this code is slow." Always show the specific line and explain why.

---

## 4. Scan Checklist by Language

### Java / Spring Boot

**Performance (PERF)**
- [ ] JPA: are entities fetched with `findAll()` on large tables without pagination?
- [ ] JPA: are there `@OneToMany` / `@ManyToMany` without `FetchType.LAZY`?
- [ ] JPA: are there loops that call a repository method (N+1 pattern)?
- [ ] Spring: are there `@Transactional` methods making external HTTP calls?
- [ ] Caching: are expensive repeated reads missing `@Cacheable`?
- [ ] Collections: are streams collecting to a `List` when only a count is needed?

**Error Handling (ERR)**
- [ ] Are exceptions caught but only logged, with execution continuing incorrectly?
- [ ] Are checked exceptions converted to unchecked without preserving the cause?
- [ ] Is there a global `@RestControllerAdvice`? Does it cover all exception types?
- [ ] Are `CompletableFuture.get()` calls missing timeout + exception handling?
- [ ] Are Optional values accessed with `.get()` without `.isPresent()` guard?

**Processing Delays (DELAY)**
- [ ] Are outbound HTTP calls synchronous inside a request thread?
- [ ] Are file I/O operations on the main application thread?
- [ ] Are there long DB transactions holding locks while doing external work?
- [ ] Are batch jobs processing records one-by-one instead of in bulk?

**Memory / Resources (MEM)**
- [ ] Are JDBC `Connection`, `Statement`, or `ResultSet` objects opened outside try-with-resources?
- [ ] Are `InputStream` / `OutputStream` objects closed in finally blocks (not try-with-resources)?
- [ ] Is there a cache with no eviction policy (`ConcurrentHashMap` used as a cache)?

**Security (SEC)**
- [ ] Is there any SQL built by string concatenation?
- [ ] Are secrets or API keys hardcoded in source files?
- [ ] Are user inputs passed to `Runtime.exec()` or `ProcessBuilder`?

---

### Python / FastAPI

**Performance (PERF)**
- [ ] Are there SQLAlchemy queries loading full ORM objects when only a count or single column is needed?
- [ ] Are there N+1 patterns: a query inside a `for` loop over a collection?
- [ ] Are there `selectall()` / `fetchall()` calls on large tables without `.limit()`?
- [ ] Are there missing `async` on I/O-bound functions (network, DB, file)?

**Error Handling (ERR)**
- [ ] Are there bare `except:` blocks that catch everything silently?
- [ ] Are there `except Exception as e: pass` patterns?
- [ ] Does FastAPI have a global exception handler for domain errors?
- [ ] Are Pydantic validation errors caught and returned with meaningful messages?

**Processing Delays (DELAY)**
- [ ] Are blocking library calls (`requests`, `time.sleep`, `open()`) inside `async` functions?
- [ ] Are CPU-heavy operations running on the async event loop instead of `ProcessPoolExecutor`?
- [ ] Are there long-running tasks being processed synchronously in an HTTP handler?

**Memory / Resources (MEM)**
- [ ] Are database sessions opened without `async with` / context manager?
- [ ] Are files opened without `with open(...)` statements?
- [ ] Are there large lists loaded entirely into memory when generators would work?

---

### React / TypeScript

**Performance (PERF)**
- [ ] Are there components re-rendering on every parent render due to missing `React.memo`?
- [ ] Are there inline object/function props created on every render (`onClick={() => ...}` in list items)?
- [ ] Are there large lists rendered without virtualisation (`@tanstack/react-virtual`)?
- [ ] Are there data fetches triggered inside `useEffect` instead of TanStack Query?

**Error Handling (ERR)**
- [ ] Are there fetch calls without `.catch()` or error state handling?
- [ ] Are there components that render `undefined` data without a guard?
- [ ] Is there a top-level `<ErrorBoundary>` wrapping the app?
- [ ] Are form submissions missing error feedback to the user?

**Processing Delays (DELAY)**
- [ ] Are there blocking synchronous operations in the render path?
- [ ] Are there heavy computations in render without `useMemo`?
- [ ] Is user input triggering expensive operations without debouncing?

---

### MSSQL / T-SQL

**Performance (PERF)**
- [ ] Are there queries with table scans on large tables (`sys.dm_exec_query_stats`)?
- [ ] Are there key lookups in execution plans (suggests missing INCLUDE columns)?
- [ ] Are there cursor-based row-by-row operations that could be set-based?
- [ ] Are there missing statistics on frequently queried columns?

**Error Handling (ERR)**
- [ ] Are there transactional stored procedures without `TRY/CATCH`?
- [ ] Are there `COMMIT` statements without corresponding error rollback logic?
- [ ] Are there procedures that silently return 0 rows on error instead of raising?

**Processing Delays (DELAY)**
- [ ] Are there long-running transactions holding locks during email sends or file writes?
- [ ] Are there procedures doing row-by-row inserts instead of bulk `INSERT ... SELECT`?
- [ ] Are there missing indexes causing full scans on heavily queried lookup columns?

**Security (SEC)**
- [ ] Is there any dynamic SQL built with string concatenation (SQL injection)?
- [ ] Are application logins using `sysadmin` or `db_owner` roles?
- [ ] Are there tables with direct `SELECT`/`INSERT` grants instead of `EXECUTE` on procedures?

---

## 5. Report Format

The final report must follow this exact structure. Every section is mandatory.

```plaintext
╔══════════════════════════════════════════════════════════════════════╗
║              CODE HEALTH INSPECTION REPORT                           ║
╠══════════════════════════════════════════════════════════════════════╣
║  Scope      : [files / modules / feature scanned]                    ║
║  Language   : [Java / Python / React / MSSQL]                        ║
║  Scan Date  : [date]                                                 ║
║  Issues Found: [total]  P0:[n]  P1:[n]  P2:[n]  P3:[n]              ║
╚══════════════════════════════════════════════════════════════════════╝

## EXECUTIVE SUMMARY
[2–4 sentences. What is the overall health? What is the most critical concern?
What will happen if nothing is fixed?]

## ISSUE REGISTRY
| # | Severity | Category | Location | Title |
|---|----------|----------|----------|-------|
| 1 | P0 🔴    | PERF     | OrderService:42 | N+1 query in order list |
| 2 | P1 🟠    | ERR      | PaymentController:88 | Exception swallowed silently |
...

## DETAILED FINDINGS

### Issue #1 — [Title]
- **Severity**: P0 🔴 Critical
- **Category**: PERF — Performance & Slowness
- **Location**: `src/service/OrderService.java`, method `getOrdersForCustomer()`, line 42

**Evidence (the problem)**
[exact code snippet showing the issue]

**Root Cause**
[Plain English explanation of WHY this is a problem]

**Impact**
[What happens at runtime because of this — user sees slowness, DB melts, data lost, etc.]

**Recommended Fix**
[Corrected code snippet with explanation]

---
[Repeat for each issue]

## PRIORITY RECOMMENDATIONS
[Ordered action list — what to fix first and why]
1. [P0 fixes — must do immediately]
2. [P1 fixes — do this sprint]
3. [P2/P3 fixes — backlog]

## HEALTH SCORE
[Optional: a simple A/B/C/D/F grade with justification]
```plaintext
