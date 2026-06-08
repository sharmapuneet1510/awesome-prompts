---
title: SDLC Examples Index
description: Complete guide to software development lifecycle examples organized by agent and phase
version: 1.0
---

# SDLC Examples Index

Complete real-world examples showing how each agent works across the full Software Development Lifecycle (SDLC).

---

## 📚 By Agent

### 🎯 Orchestrator Agent — Strategic Leadership
**File:** [ORCHESTRATOR_SDLC_EXAMPLES.md](ORCHESTRATOR_SDLC_EXAMPLES.md)

**Scenarios:**
1. **E-Commerce MVP (Greenfield)** — From requirements to production
   - Phase 0: Requirements gathering with clarifying questions
   - Phase 1: Planning & orchestration
   - Phase 2: Design review & tradeoffs
   - Phase 3: Risk assessment
   - Phase 4: Context building
   - Phase 5: PR management & launch

2. **Legacy System Modernization** — From monolith to microservices
   - Requirements analysis for modernization
   - Planning migration strategy
   - Design review of new architecture
   - Risk assessment of strangler pattern

**Key Takeaways:**
- Always start with `orchestrator:plan` (clarify assumptions)
- Use `orchestrator:tradeoff` to compare approaches
- Use `orchestrator:risk` before launch
- Chain orchestrator functions → downstream agents

---

### 🏗️ Architect Agent — System Design
**File:** [ARCHITECT_SDLC_EXAMPLES.md](ARCHITECT_SDLC_EXAMPLES.md)

**Scenarios:**
1. **Real-Time Chat System (Greenfield)**
   - Phase 0: System topology design (C4 architecture)
   - Phase 1: API contract design (OpenAPI 3.0)
   - Phase 2: Database schema design (PostgreSQL DDL)
   - Phase 3: Frontend component architecture (React)
   - Phase 4: Accessibility audit (WCAG 2.1 AA)

2. **Monolith → Microservices Refactoring (Brownfield)**
   - Current state assessment
   - Target state design
   - Phased migration roadmap
   - Zero-downtime deployment strategy
   - Database migration strategy

**Key Takeaways:**
- Design before coding (prevents expensive rewrites)
- API contract first (parallel frontend/backend work)
- Schema optimization upfront (hard to migrate later)
- A11y from day 1 (retrofitting is 3x more expensive)

---

### 💻 Implementer Agent — Code Generation & Execution
**File:** [IMPLEMENTER_SDLC_EXAMPLES.md](IMPLEMENTER_SDLC_EXAMPLES.md)

**Scenarios:**
1. **User Authentication Service (New Feature)**
   - Phase 0: Code generation (production-ready models + routes)
   - Phase 1: Comprehensive testing (95%+ coverage)
   - Phase 2: Documentation (API + architecture + setup)
   - Phase 3: CI/CD pipeline (GitHub Actions)
   - Phase 4: Containerization (Docker + docker-compose)
   - Phase 5: Infrastructure as Code (Kubernetes)
   - Phase 6: Complete lifecycle (implementer:full)

**Key Takeaways:**
- Code generation first (from solid design)
- Test as you go (95%+ coverage required)
- Automate pipeline early (saves hours per week)
- Use `implementer:full` for zero context loss

---

### ✅ Quality Agent — Validation & Optimization
**File:** [QUALITY_SDLC_EXAMPLES.md](QUALITY_SDLC_EXAMPLES.md)

**Scenarios:**
1. **Pull Request Code Review**
   - 6-phase review: requirements → code → tests → docs → security → scoring
   - Weighted scorecard (A-F grading)
   - Requirement validation against JIRA ACs
   - Code quality + test coverage assessment
   - Security audit
   - Actionable feedback

2. **Codebase Audit** — Architecture & tech debt
   - SOLID principles assessment
   - Duplication analysis
   - Tech debt scoring
   - Refactoring priority roadmap
   - Maintainability index

3. **Security Audit** — Compliance focused
   - OWASP Top 10 assessment
   - Secrets scanning
   - Dependency vulnerability scan
   - SOC 2 / PCI-DSS compliance
   - Remediation roadmap

4. **Performance Analysis** — Optimization focused
   - Bottleneck identification
   - Quick wins (4 hours, 70% improvement)
   - Medium-term optimizations (2 weeks, 20% more)
   - Scalability projections (1M users)
   - Implementation plan

5. **Production Bug Debugging**
   - 5-phase RCA (root cause analysis)
   - Edge case identification
   - Permanent fixes + preventive measures
   - Incident summary + lessons learned

**Key Takeaways:**
- Review before building (catch issues early)
- Quality is everyone's job (not just QA)
- Debug systematically (root cause first)
- Document lessons learned (prevent repeats)

---

## 📋 By SDLC Phase

### Phase 0: Requirements → Planning
```
orchestrator:plan           → Clarify requirements
architect:design            → System topology
orchestrator:tradeoff       → Compare approaches
```
**Files:**
- [ORCHESTRATOR_SDLC_EXAMPLES.md](ORCHESTRATOR_SDLC_EXAMPLES.md) — E-Commerce MVP Phase 0-1
- [ARCHITECT_SDLC_EXAMPLES.md](ARCHITECT_SDLC_EXAMPLES.md) — Chat System Phase 0

---

### Phase 1: Design & Architecture
```
architect:design            → System topology
architect:schema            → Database schema
architect:api               → API contracts
architect:frontend          → Component architecture
orchestrator:review         → Design review
```
**Files:**
- [ARCHITECT_SDLC_EXAMPLES.md](ARCHITECT_SDLC_EXAMPLES.md) — Complete design lifecycle

---

### Phase 2: Implementation & Coding
```
implementer:build           → Code generation
implementer:test            → Test generation
implementer:doc             → Documentation
```
**Files:**
- [IMPLEMENTER_SDLC_EXAMPLES.md](IMPLEMENTER_SDLC_EXAMPLES.md) — Auth service build phase

---

### Phase 3: CI/CD & Infrastructure
```
implementer:pipeline        → CI/CD setup
implementer:docker          → Containerization
implementer:iac             → Kubernetes manifests
```
**Files:**
- [IMPLEMENTER_SDLC_EXAMPLES.md](IMPLEMENTER_SDLC_EXAMPLES.md) — Pipeline + Docker + K8s

---

### Phase 4: Code Review & Validation
```
quality:review              → PR validation
quality:audit               → Architecture audit
quality:security            → Security audit
quality:perf                → Performance audit
```
**Files:**
- [QUALITY_SDLC_EXAMPLES.md](QUALITY_SDLC_EXAMPLES.md) — All quality phases

---

### Phase 5: Debugging & Optimization
```
quality:debug               → Root cause analysis
quality:diagnose            → Conversational debugging
quality:report              → Comprehensive synthesis
quality:batch-review        → Multiple PR reviews
```
**Files:**
- [QUALITY_SDLC_EXAMPLES.md](QUALITY_SDLC_EXAMPLES.md) — Debug + perf + batch review

---

## 🚀 Common Workflows

### Workflow 1: MVP Launch (2-3 days)
```
Day 1:  orchestrator:plan → architect:design → orchestrator:review
Day 2:  implementer:full → quality:review
Day 3:  orchestrator:pr → [merge + deploy]
```
**See:**
- [ORCHESTRATOR_SDLC_EXAMPLES.md](ORCHESTRATOR_SDLC_EXAMPLES.md) — E-Commerce MVP
- [ARCHITECT_SDLC_EXAMPLES.md](ARCHITECT_SDLC_EXAMPLES.md) — Chat System Design
- [IMPLEMENTER_SDLC_EXAMPLES.md](IMPLEMENTER_SDLC_EXAMPLES.md) — Auth Service

---

### Workflow 2: Code Review Sprint
```
quality:review pr=123 → quality:review pr=124 → quality:batch-review
```
**See:** [QUALITY_SDLC_EXAMPLES.md](QUALITY_SDLC_EXAMPLES.md) — PR review scenario

---

### Workflow 3: Legacy System Modernization
```
orchestrator:context → quality:audit → architect:refactor → [phased migration]
```
**See:**
- [ORCHESTRATOR_SDLC_EXAMPLES.md](ORCHESTRATOR_SDLC_EXAMPLES.md) — Modernization phase
- [ARCHITECT_SDLC_EXAMPLES.md](ARCHITECT_SDLC_EXAMPLES.md) — Brownfield refactoring
- [QUALITY_SDLC_EXAMPLES.md](QUALITY_SDLC_EXAMPLES.md) — Audit scenario

---

### Workflow 4: Production Incident Response
```
quality:diagnose → quality:debug → implementer:build → quality:review → [deploy]
```
**See:** [QUALITY_SDLC_EXAMPLES.md](QUALITY_SDLC_EXAMPLES.md) — Bug debugging scenario

---

## 📊 Real-World Scenarios

| Scenario | File | Duration | Functions Used |
|----------|------|----------|-----------------|
| E-Commerce MVP | ORCHESTRATOR | 2-3 days | plan → build → review → pr |
| Real-Time Chat | ARCHITECT | 1-2 days | design → api → schema → frontend → a11y |
| Auth Service | IMPLEMENTER | 2-3 hours | build → test → doc → pipeline → docker → iac → full |
| PR Code Review | QUALITY | 20-30 min | review |
| Codebase Audit | QUALITY | 1-2 hours | audit |
| Security Audit | QUALITY | 1-2 hours | security |
| Performance Opt | QUALITY | 1-2 hours | perf |
| Bug RCA | QUALITY | 30-45 min | debug |
| Monolith Migration | ARCHITECT + ORCHESTRATOR | 3-4 weeks | refactor + plan + risk |

---

## 🎯 How to Use This Index

**I want to build a new feature:**
→ Start with [ORCHESTRATOR_SDLC_EXAMPLES.md](ORCHESTRATOR_SDLC_EXAMPLES.md) (E-Commerce MVP scenario)
→ Then [ARCHITECT_SDLC_EXAMPLES.md](ARCHITECT_SDLC_EXAMPLES.md) (Chat System design)
→ Then [IMPLEMENTER_SDLC_EXAMPLES.md](IMPLEMENTER_SDLC_EXAMPLES.md) (Auth service implementation)

**I need to review code:**
→ See [QUALITY_SDLC_EXAMPLES.md](QUALITY_SDLC_EXAMPLES.md) (PR review scenario)

**I need to audit existing codebase:**
→ See [QUALITY_SDLC_EXAMPLES.md](QUALITY_SDLC_EXAMPLES.md) (codebase audit scenario)

**I have a production bug:**
→ See [QUALITY_SDLC_EXAMPLES.md](QUALITY_SDLC_EXAMPLES.md) (debug scenario)

**I need to modernize legacy system:**
→ See [ORCHESTRATOR_SDLC_EXAMPLES.md](ORCHESTRATOR_SDLC_EXAMPLES.md) (modernization scenario)
→ Then [ARCHITECT_SDLC_EXAMPLES.md](ARCHITECT_SDLC_EXAMPLES.md) (brownfield refactoring)

**I need to optimize performance:**
→ See [QUALITY_SDLC_EXAMPLES.md](QUALITY_SDLC_EXAMPLES.md) (performance analysis scenario)

---

## 🔗 Related Documentation

- **[FUNCTION_EXAMPLES.md](FUNCTION_EXAMPLES.md)** — Detailed examples for all 30 functions
- **[FUNCTION_QUICK_REFERENCE.md](FUNCTION_QUICK_REFERENCE.md)** — One-page cheat sheets
- **[agents/README.md](agents/README.md)** — Agent descriptions
- **[skills/README.md](skills/README.md)** — Reusable implementation skills
- **[SPECIALIST_AGENT_MODES.md](SPECIALIST_AGENT_MODES.md)** — 9 specialist role modes

---

## 📈 SDLC Maturity Model

Use these examples to understand how agents support different maturity levels:

**Level 1: Ad-hoc**
- Manual review process
- No consistent architecture
- Documentation after coding
- **Agent help:** quality:review catches issues

**Level 2: Repeatable**
- Design before coding
- Consistent CI/CD
- Basic testing
- **Agent help:** architect:design → implementer:build → quality:review

**Level 3: Defined**
- Formal architecture reviews
- Security audits
- Performance optimization
- **Agent help:** quality:audit → quality:security → quality:perf

**Level 4: Managed**
- Continuous monitoring
- Metrics-driven decisions
- Proactive optimization
- **Agent help:** quality:report (synthesizes all dimensions)

**Level 5: Optimized**
- Automated quality gates
- Self-healing systems
- Zero-downtime deployments
- **Agent help:** All agents in coordinated workflow

---

**Last Updated:** June 8, 2026 | **Version:** 1.0
