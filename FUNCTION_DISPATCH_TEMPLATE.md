# Function Dispatch Template (v2.0)

This document shows how to add Function Dispatch sections to each agent file.

## Where to Insert Function Dispatch Section

Insert the **Function Dispatch** section into each agent file **immediately after the Identity section**, before the first workflow/protocol section.

Example location:
```
# Agent Name — vX.0

## Identity
...your identity text...

## Function Dispatch  ← INSERT HERE
...function table...

## Operating Protocol  ← Then continue with your existing sections
```

---

## Template: Copy-Paste Pattern

Replace `PREFIX` with the agent's short prefix (documentation, ba, architecture, etc.)

Replace `FUNCTION_NAME` with the actual function name (context, code, report, etc.)

### Part 1: Function Dispatch Section (Insert after Identity)

```markdown
## Function Dispatch

**Prefix:** `PREFIX`

Invoke a specific function using `PREFIX:function`. When triggered this way, skip all other workflows and run only the steps for that function.

| Function | What it does |
|----------|--------------|
| `PREFIX:function1` | One-line description of what function1 does |
| `PREFIX:function2` | One-line description of what function2 does |
| `PREFIX:function3` | One-line description of what function3 does |

### Dispatch Rules
- **With function:** `PREFIX:function` → run only that function's steps (skip intro questions)
- **Without function:** Full agent workflow with scope selection
- **With path:** `PREFIX:function path=./directory` → pass path directly, skip file prompts
```

---

### Part 2: Add Annotation to Each Step

Inside each STEP/PHASE section header, add one line at the top:

**Before:**
```markdown
### STEP N — Gather Requirements

**Goal:** Parse and...
```

**After:**
```markdown
### STEP N — Gather Requirements
> **Function:** `PREFIX:function_name` — One-line trigger description

**Goal:** Parse and...
```

---

## Agent-Specific Function Maps

Use the tables below to create each agent's Function Dispatch section.

### documentation (Prefix: documentation)

| Function | What it does |
|----------|--------------|
| `documentation:code` | Scan codebase, generate Javadoc/docstrings/JSDoc (100% coverage) |
| `documentation:context` | Build context.json, architecture.md, tech-stack.md (context_builder_skill) |
| `documentation:diagrams` | Generate Mermaid diagrams (C4, sequence, dependency) |
| `documentation:api` | Generate OpenAPI 3.0 spec from routes/controllers |
| `documentation:readme` | Write README + quick-start guide |
| `documentation:html` | Build interactive, searchable, self-contained HTML doc site |

### architecture (Prefix: architecture)

| Function | What it does |
|----------|--------------|
| `architecture:design` | Greenfield system design (topology, API contract, DB schema, caching, stubs) |
| `architecture:refactor` | Brownfield refactoring roadmap (assess → diagnose → phase plan → migration guide + rollbacks) |
| `architecture:schema` | Database schema + DDL + migration scripts only |
| `architecture:api` | API contract design (OpenAPI spec + examples) only |

### business_analyst (Prefix: ba)

| Function | What it does |
|----------|--------------|
| `ba:report` | Parse JIRA JSON/CSV → full filterable/sortable HTML backlog report |
| `ba:parse` | Parse JIRA file → normalized JSON only (no HTML) |

### implementation (Prefix: implementation)

| Function | What it does |
|----------|--------------|
| `implementation:build` | Generate code from requirements (detect stack → apply skill → write code) |
| `implementation:test` | Generate tests only (skip code, skip docs) |
| `implementation:doc` | Auto-document existing code (skip code, skip tests) |
| `implementation:full` | Full lifecycle: build + test + doc + PR |

### code_review (Prefix: review)

| Function | What it does |
|----------|--------------|
| `review:full` | Full PR review (all 6 phases + HTML report + PR comment) |
| `review:quality` | Code quality only (SOLID, patterns, naming — no JIRA lookup) |
| `review:report` | Generate HTML report from prior review analysis |
| `review:comment` | Post formatted PR/MR comment summary |

### security_auditor (Prefix: security)

| Function | What it does |
|----------|--------------|
| `security:audit` | Full OWASP security audit (all 8 phases + ranked report) |
| `security:authn` | Authentication + authorization audit only |
| `security:injection` | Injection risk scan only (SQL/NoSQL/command/template/XXE) |
| `security:report` | Severity-ranked vulnerability report with secure code fixes |

### codebase_auditor (Prefix: audit)

| Function | What it does |
|----------|--------------|
| `audit:scan` | Full codebase audit (all 8 phases) |
| `audit:quality` | SOLID violations + design pattern audit only |
| `audit:perf` | Performance bottleneck scan only (N+1, algorithms, memory) |
| `audit:roadmap` | Generate prioritized refactoring roadmap from existing analysis |

### test_case_generator (Prefix: test)

| Function | What it does |
|----------|--------------|
| `test:generate` | Generate test suite from source code files |
| `test:jira` | Generate tests from JIRA ticket (pull acceptance criteria) |
| `test:validate` | Validate existing tests cover all requirements/ACs |
| `test:coverage` | Coverage gap report (what's missing, what needs more cases) |

### performance_optimizer (Prefix: perf)

| Function | What it does |
|----------|--------------|
| `perf:profile` | Profile code, map hot paths, identify expensive operations |
| `perf:optimize` | Apply optimizations with before/after code comparisons |
| `perf:benchmark` | Generate benchmark test suite (baseline + regression) |
| `perf:monitor` | Design performance monitoring strategy + alerting rules |

### production_debugger (Prefix: debug)

| Function | What it does |
|----------|--------------|
| `debug:rca` | Root cause analysis from stack trace/error description |
| `debug:trace` | Trace execution path through code to find failure point |
| `debug:fix` | Design + implement bug fix with regression tests |
| `debug:edge` | Find similar edge cases around a known bug |

### integration (Prefix: integration)

| Function | What it does |
|----------|--------------|
| `integration:pipeline` | Generate CI/CD pipeline (GitHub Actions / GitLab CI / Jenkins) |
| `integration:docker` | Generate Dockerfile + Docker Compose config |
| `integration:iac` | Generate IaC (Terraform / CloudFormation / K8s manifests) |
| `integration:monitor` | Set up observability (logging, metrics, tracing, alerting) |

### technical_lead (Prefix: lead)

| Function | What it does |
|----------|--------------|
| `lead:review` | Strategic architecture/decision review with challenge questions |
| `lead:tradeoff` | Generate 3-option tradeoff analysis with ranked recommendation |
| `lead:risk` | Risk assessment for proposed solution (5-year maintainability lens) |
| `lead:plan` | Phased execution plan for approved strategy |

### senior_frontend_engineer (Prefix: frontend)

| Function | What it does |
|----------|--------------|
| `frontend:component` | Generate React component(s) with TypeScript, a11y, and tests |
| `frontend:design` | Component architecture + composition strategy |
| `frontend:a11y` | Accessibility audit (WCAG 2.1 AA) + remediation code |
| `frontend:test` | Component test suite (RTL + axe-core + edge cases) |
| `frontend:story` | Storybook stories + prop docs for existing components |

### autonomous_dev (Prefix: autonomous)

| Function | What it does |
|----------|--------------|
| `autonomous:build` | Full-stack generation from requirements.txt (all phases) |
| `autonomous:context` | Build project context only (context.json, architecture.md, knowledge graph) |
| `autonomous:pr` | Package deliverables and open GitHub PR |

---

## Step-by-Step Instructions

### For Each Agent File:

1. **Open the agent file** (e.g., `agents/documentation_agent.md`)

2. **Find the Identity section** (headed `## Identity`)

3. **After the Identity section**, insert a new `## Function Dispatch` section using the template above, replacing:
   - `PREFIX` with the agent's short prefix
   - The function table with functions from the appropriate agent in the maps above

4. **For each STEP/PHASE section** in the Operating Protocol:
   - Add a line below the section header:
   ```markdown
   > **Function:** `PREFIX:function_name` — Brief trigger description
   ```
   - Example:
   ```markdown
   ### STEP 1 — Gather Requirements
   > **Function:** `documentation:code` — Generate code-level documentation

   **Goal:** Scan codebase for...
   ```

5. **Save the file**

6. **Verify:** Check that each STEP/PHASE has its corresponding Function annotation

---

## Validation Checklist

For each agent file:
- [ ] `## Function Dispatch` section added after Identity
- [ ] Function table created with all functions for that agent
- [ ] Dispatch rules section included
- [ ] Each STEP/PHASE has `> **Function:**` annotation
- [ ] Function names match the table in Function Dispatch section
- [ ] No syntax errors in markdown

---

## Example: Complete Documentation Agent Section

Here's what the documentation agent should look like after updates:

```markdown
# Documentation Agent — v2.0

## Identity

You are a **Documentation Engineer**...
[rest of identity section]

## Function Dispatch

**Prefix:** `documentation`

Invoke a specific function using `documentation:function`. When triggered this way, skip all other workflows and run only the steps for that function.

| Function | What it does |
|----------|--------------|
| `documentation:code` | Scan codebase, generate Javadoc/docstrings/JSDoc (100% coverage) |
| `documentation:context` | Build context.json, architecture.md, tech-stack.md (context_builder_skill) |
| `documentation:diagrams` | Generate Mermaid diagrams (C4, sequence, dependency) |
| `documentation:api` | Generate OpenAPI 3.0 spec from routes/controllers |
| `documentation:readme` | Write README + quick-start guide |
| `documentation:html` | Build interactive, searchable, self-contained HTML doc site |

### Dispatch Rules
- **With function:** `documentation:function` → run only that function's steps (skip intro questions)
- **Without function:** Full agent workflow with scope selection
- **With path:** `documentation:function path=./directory` → pass path directly, skip file prompts

## Workflow Overview

...existing content...

### STEP 1 — Clarify Documentation Scope
> **Function:** `documentation:clarify` — Scope documentation type selection

Ask user: "What documentation do you need?"
...rest of step...

### STEP 2 — Code-Level Documentation
> **Function:** `documentation:code` — Generate inline code documentation

**Goal:** 100% method/function documentation...
...rest of step...

### STEP 3 — Technical Architecture Documentation
> **Function:** `documentation:context` — Build codebase visualization snapshot

**Goal:** Build discoverable project context...
...rest of step...
```

---

## Summary

- Each agent file needs: 1 `Function Dispatch` section + annotations in each STEP
- Total changes: 13 agent files × ~10 lines per file = ~130 lines total
- Master reference: [AGENTS_FUNCTIONS.md](../AGENTS_FUNCTIONS.md) has all 54 functions documented
- This enables users to call `agent:function` for targeted workflows without reading the full agent spec

---

**Template Version:** 2.0  
**Date:** June 3, 2026
