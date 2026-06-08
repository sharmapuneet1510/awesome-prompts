---
title: Function Quick Reference Cards
description: One-page cheat sheets for all 28 agent functions - quick syntax, inputs, outputs, use cases
---

# 🎯 Function Quick Reference Cards

**One-page guide for every function. Copy-paste commands directly.**

---

## 🎯 Orchestrator Agent (7 Functions)

### 1. orchestrator:plan
```bash
orchestrator:plan "Build user authentication system"
```
| Aspect | Details |
|--------|---------|
| **Input** | Free-text requirement |
| **Output** | Task breakdown, execution plan |
| **Key Step** | PHASE 0: Asks clarifying questions FIRST |
| **Use When** | Starting new project, need strategic plan |
| **Time** | 5-10 minutes |

---

### 2. orchestrator:build
```bash
orchestrator:build path=./requirements.md
```
| Aspect | Details |
|--------|---------|
| **Input** | Clarified requirements (or path to design) |
| **Output** | Complete system (code + tests + docs + CI/CD) |
| **Orchestrates** | architect:design → implementer:full → quality:review |
| **Use When** | Need full-stack MVP, end-to-end generation |
| **Time** | 1-2 hours |

---

### 3. orchestrator:context
```bash
orchestrator:context path=./existing-project
```
| Aspect | Details |
|--------|---------|
| **Input** | Path to existing project |
| **Output** | architecture.md, tech-stack.md, context.json, design.html |
| **Purpose** | Build comprehensive project understanding |
| **Use When** | Joining team, need quick project overview |
| **Time** | 10-15 minutes |

---

### 4. orchestrator:review
```bash
orchestrator:review path=./system-design.md
```
| Aspect | Details |
|--------|---------|
| **Input** | Design document or architecture |
| **Output** | Review with challenge questions, risks, assessment |
| **Validates** | Assumptions, complexity, production readiness |
| **Use When** | Before implementation, need senior perspective |
| **Time** | 15-20 minutes |

---

### 5. orchestrator:tradeoff
```bash
orchestrator:tradeoff goal="Handle 1M users, 99.99% uptime"
```
| Aspect | Details |
|--------|---------|
| **Input** | Goal or constraint |
| **Output** | 3 approaches with effort/complexity/tradeoffs |
| **Compares** | Monolithic vs Microservices vs Hybrid |
| **Use When** | Need to choose between architecture patterns |
| **Time** | 10-15 minutes |

---

### 6. orchestrator:risk
```bash
orchestrator:risk path=./architecture
```
| Aspect | Details |
|--------|---------|
| **Input** | Design or architecture |
| **Output** | Risk assessment with mitigation strategies |
| **Identifies** | Critical risks, failure modes, dependencies |
| **Use When** | Pre-production readiness check |
| **Time** | 15-20 minutes |

---

### 7. orchestrator:pr
```bash
orchestrator:pr title="feat: user auth MVP" description="Implements registration, login, sessions"
```
| Aspect | Details |
|--------|---------|
| **Input** | Generated code + tests + docs |
| **Output** | GitHub PR with complete description |
| **Includes** | Code diff, architecture narrative, test report |
| **Use When** | Ready to submit for review |
| **Time** | 5 minutes |

---

## 🏗️ Architect Agent (6 Functions)

### 8. architect:design
```bash
architect:design requirements="Real-time chat for 100K users"
```
| Aspect | Details |
|--------|---------|
| **Input** | System requirements (scope, scale, constraints) |
| **Output** | C4 diagram, API spec, DB schema, deployment plan |
| **Covers** | Architecture, components, data flow, caching, scaling |
| **Use When** | Designing system from scratch |
| **Time** | 1-2 hours |

**Example outputs:**
- System topology (Mermaid C4)
- OpenAPI 3.0 spec
- PostgreSQL DDL + migrations
- Redis caching strategy
- K8s deployment manifests

---

### 9. architect:refactor
```bash
architect:refactor path=./monolith goal="Split into microservices"
```
| Aspect | Details |
|--------|---------|
| **Input** | Existing codebase + refactoring goal |
| **Output** | Current-state analysis, target design, phased roadmap |
| **Produces** | Migration guide, rollback strategies, zero-downtime plan |
| **Use When** | Modernizing legacy system |
| **Time** | 2-3 hours |

---

### 10. architect:schema
```bash
architect:schema requirements="Users, products, orders" db=postgresql
```
| Aspect | Details |
|--------|---------|
| **Input** | Data model requirements, database type |
| **Output** | SQL DDL, indexes, migrations, optimization |
| **Includes** | Primary keys, foreign keys, constraints, partitioning |
| **Use When** | Designing database from scratch |
| **Time** | 30-45 minutes |

---

### 11. architect:api
```bash
architect:api requirements="List products, create order, get user"
```
| Aspect | Details |
|--------|---------|
| **Input** | API endpoint requirements |
| **Output** | OpenAPI 3.0 spec, request/response schemas, examples |
| **Includes** | Auth, rate limiting, error codes, documentation |
| **Use When** | Designing REST API contract |
| **Time** | 30-45 minutes |

---

### 12. architect:frontend
```bash
architect:frontend requirements="Product card with image, price, rating, buy button"
```
| Aspect | Details |
|--------|---------|
| **Input** | Component requirements |
| **Output** | Component architecture, TypeScript interfaces, examples |
| **Covers** | State management, accessibility (WCAG 2.1 AA), responsive design |
| **Use When** | Designing reusable UI components |
| **Time** | 1-2 hours |

---

### 13. architect:a11y
```bash
architect:a11y path=./product-page.tsx
```
| Aspect | Details |
|--------|---------|
| **Input** | React/HTML file |
| **Output** | Accessibility audit, recommendations, fixes |
| **Checks** | WCAG 2.1 AA compliance, keyboard navigation, ARIA |
| **Use When** | Auditing UI for accessibility |
| **Time** | 15-30 minutes |

---

## 💻 Implementer Agent (7 Functions)

### 14. implementer:build
```bash
implementer:build path=./api-spec.md
```
| Aspect | Details |
|--------|---------|
| **Input** | Architecture/API spec |
| **Output** | Production-ready code (auto-detects tech stack) |
| **Generates** | Models, routes, services, middleware |
| **Use When** | Need to write code from spec |
| **Time** | 30-60 minutes |

**Tech stack auto-detection:**
- Python → FastAPI
- Java → Spring Boot
- TypeScript → React

---

### 15. implementer:test
```bash
implementer:test path=./services/user_service.py
```
| Aspect | Details |
|--------|---------|
| **Input** | Source code |
| **Output** | Test suite with 95%+ coverage |
| **Follows** | AAA pattern (Arrange-Act-Assert) |
| **Use When** | Need comprehensive tests |
| **Time** | 30-45 minutes |

**Covers:**
- Unit tests (individual functions)
- Integration tests (function interactions)
- Edge cases (boundary conditions, errors)

---

### 16. implementer:doc
```bash
implementer:doc path=./src
```
| Aspect | Details |
|--------|---------|
| **Input** | Source code directory |
| **Output** | JSDoc, docstrings, Javadoc + README + API guide |
| **Generates** | Inline docs, architecture guide, setup instructions |
| **Use When** | Need auto-generated documentation |
| **Time** | 20-30 minutes |

---

### 17. implementer:pipeline
```bash
implementer:pipeline path=./ platform=github-actions
```
| Aspect | Details |
|--------|---------|
| **Input** | Project path, target platform |
| **Output** | .github/workflows/ci.yml (or equivalent) |
| **Includes** | Tests, linting, coverage, deployment steps |
| **Supports** | GitHub Actions, GitLab CI, Jenkins, CircleCI, Azure |
| **Use When** | Setting up CI/CD |
| **Time** | 15-20 minutes |

---

### 18. implementer:docker
```bash
implementer:docker path=./src
```
| Aspect | Details |
|--------|---------|
| **Input** | Project path |
| **Output** | Dockerfile + docker-compose.yml |
| **Includes** | Multi-stage build, health checks, security best practices |
| **Use When** | Containerizing application |
| **Time** | 10-15 minutes |

---

### 19. implementer:iac
```bash
implementer:iac path=./app type=kubernetes
```
| Aspect | Details |
|--------|---------|
| **Input** | App path, infrastructure type |
| **Output** | deployment.yaml, service.yaml, configmap.yaml |
| **Supports** | Kubernetes, Terraform, CloudFormation, ARM templates |
| **Use When** | Deploying to cloud infrastructure |
| **Time** | 20-30 minutes |

---

### 20. implementer:full
```bash
implementer:full path=./requirements.md
```
| Aspect | Details |
|--------|---------|
| **Input** | Requirements (detects tech stack automatically) |
| **Output** | Code + Tests + Docs + CI/CD + Docker + K8s (all in one pass!) |
| **Key Benefit** | NO context loss between phases (all in same context window) |
| **Use When** | Need complete end-to-end implementation |
| **Time** | 2-3 hours |

**Runs in sequence (no context transfer):**
1. Build code
2. Generate tests
3. Create documentation
4. Setup CI/CD pipeline
5. Create Docker setup
6. Generate K8s manifests

---

## ✅ Quality Agent (8 Functions)

### 21. quality:review
```bash
quality:review pr=456 ticket=PROJ-123 context="OAuth2 implementation"
```
| Aspect | Details |
|--------|---------|
| **Input** | PR #, JIRA ticket, context |
| **Output** | 6-phase review report with score (A-F) |
| **Analyzes** | Requirements, code quality, tests, documentation |
| **Use When** | Reviewing pull requests |
| **Time** | 20-30 minutes |

**Phases:**
1. Requirement validation (vs JIRA ACs)
2. Code quality assessment
3. Test coverage analysis
4. Documentation audit
5. Security check
6. Scoring & verdict

---

### 22. quality:audit
```bash
quality:audit path=./backend
```
| Aspect | Details |
|--------|---------|
| **Input** | Codebase path |
| **Output** | Architecture analysis, SOLID violations, tech debt roadmap |
| **Identifies** | Duplication, complexity, maintainability issues |
| **Use When** | Auditing existing codebase |
| **Time** | 1-2 hours |

---

### 23. quality:security
```bash
quality:security path=./app compliance=SOC2
```
| Aspect | Details |
|--------|---------|
| **Input** | App path, compliance standard |
| **Output** | Vulnerability report with severity levels & fixes |
| **Covers** | OWASP Top 10, authentication, data protection |
| **Compliance** | SOC2, PCI-DSS, HIPAA, GDPR checks |
| **Use When** | Security audit or compliance verification |
| **Time** | 1-2 hours |

---

### 24. quality:perf
```bash
quality:perf path=./src baseline="500ms" scale="1M users"
```
| Aspect | Details |
|--------|---------|
| **Input** | Code path, current metrics, target scale |
| **Output** | Bottleneck analysis, before/after code, optimization roadmap |
| **Analyzes** | Database, memory, CPU, rendering, I/O bottlenecks |
| **Use When** | Optimizing slow application |
| **Time** | 1-2 hours |

**Roadmap includes:**
- Quick wins (4 hours, 70% improvement)
- Medium-term (2 weeks, 20% more)
- Long-term (1+ month, 10x scaling)

---

### 25. quality:debug
```bash
quality:debug stack_trace="NullPointerException at line 42" path=./src
```
| Aspect | Details |
|--------|---------|
| **Input** | Stack trace or error message, code path |
| **Output** | 5-phase RCA with fixed code + tests |
| **Phases** | Functionality → Root cause → Explanation → Edge cases → Fix |
| **Use When** | Fixing production bugs |
| **Time** | 30-45 minutes |

---

### 26. quality:report
```bash
quality:report path=./src comprehensive=true
```
| Aspect | Details |
|--------|---------|
| **Input** | Code path |
| **Output** | Unified report (review + audit + security + perf + debug) |
| **Synthesizes** | All quality dimensions into single document |
| **Use When** | Need complete quality assessment |
| **Time** | 2-3 hours |

---

### 27. quality:batch-review
```bash
quality:batch-review from=./reviews.json output=./report.html
```
| Aspect | Details |
|--------|---------|
| **Input** | JSON file with multiple PR configs |
| **Output** | Single HTML report with tabs + summary |
| **Includes** | Score comparison, merged issues, export options |
| **Use When** | Reviewing multiple PRs at once |
| **Time** | 5 minutes per PR |

---

### 28. quality:diagnose
```bash
quality:diagnose problem="Orders endpoint taking 10 seconds"
```
| Aspect | Details |
|--------|---------|
| **Input** | Problem description (conversational) |
| **Output** | RCA + proposed solutions with code examples |
| **Asks** | Clarifying questions to narrow scope |
| **Use When** | Need conversational debugging |
| **Time** | 15-20 minutes |

---

## 📊 Business Analyst Agent (2 Functions)

### 29. ba:report
```bash
ba:report path=./jira-export.json project=MYAPP
```
| Aspect | Details |
|--------|---------|
| **Input** | JIRA export JSON |
| **Output** | Interactive HTML backlog report |
| **Includes** | Filterable, charts, burndown, velocity trends |
| **Use When** | Analyzing JIRA backlog |
| **Time** | 5-10 minutes |

---

### 30. ba:parse
```bash
ba:parse path=./jira-export.json format=json
```
| Aspect | Details |
|--------|---------|
| **Input** | JIRA export file |
| **Output** | Structured JSON with stories, story points, status |
| **Extracts** | Key info, assignee, estimates, acceptance criteria |
| **Use When** | Need machine-readable JIRA data |
| **Time** | 2-3 minutes |

---

## 🔥 Quick Command Reference

**New Project:**
```bash
orchestrator:plan "requirement"
orchestrator:build path=./design
```

**Existing Project:**
```bash
orchestrator:context path=./project
quality:audit path=./src
quality:security path=./src
```

**Code Review:**
```bash
quality:review pr=123
quality:batch-review from=./reviews.json
```

**Fix Bug:**
```bash
quality:debug stack_trace="error" path=./src
quality:perf path=./src baseline="metric"
```

**System Design:**
```bash
architect:design requirements="..."
architect:schema requirements="..."
architect:api requirements="..."
```

**Implementation:**
```bash
implementer:full path=./design
# Or step-by-step:
implementer:build path=./design
implementer:test path=./src
implementer:doc path=./src
implementer:pipeline path=./
```

---

## 📌 Index by Use Case

### By Task Type

**Starting a project:**
- orchestrator:plan
- architect:design
- orchestrator:build

**Code generation:**
- implementer:build
- implementer:test
- implementer:doc
- implementer:full

**Review & Analysis:**
- quality:review
- quality:audit
- quality:security
- quality:perf

**Debugging:**
- quality:debug
- quality:diagnose

**Infrastructure:**
- implementer:pipeline
- implementer:docker
- implementer:iac

**Architecture:**
- architect:design
- architect:refactor
- architect:schema
- architect:api
- architect:frontend
- architect:a11y

**Backlog Management:**
- ba:report
- ba:parse

---

## 🎯 By Specialist Mode

| Mode | Functions |
|------|-----------|
| **Full-Stack Engineer** | orchestrator:build, implementer:full |
| **Code Auditor** | quality:audit, quality:report |
| **Debugging Expert** | quality:debug, quality:diagnose |
| **Technical Lead** | orchestrator:review, orchestrator:tradeoff, orchestrator:risk |
| **Performance Expert** | quality:perf |
| **Systems Architect** | architect:design, architect:refactor |
| **Frontend Expert** | architect:frontend, architect:a11y |
| **Security Auditor** | quality:security |
| **DevOps Engineer** | implementer:pipeline, implementer:docker, implementer:iac |

---

## ✨ Pro Tips

1. **Always start with PHASE 0** — orchestrator:plan asks clarifying questions first
2. **Use implementer:full** — Builds code + tests + docs with no context loss
3. **Review against requirements** — quality:review validates vs JIRA ACs
4. **Chain functions** — orchestrator:build → quality:review → orchestrator:pr
5. **Copy commands** — Each card has ready-to-use commands above the table

