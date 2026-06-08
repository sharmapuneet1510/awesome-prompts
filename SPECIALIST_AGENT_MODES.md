---
title: Specialist Agent Modes — Quick Reference
version: 1.0
date: 2026-06-08
purpose: Quick reference guide for invoking specialized AI expert modes
---

# Specialist Agent Modes — Quick Reference

This guide shows how to invoke each specialized agent mode for common engineering tasks.

---

## 🚀 Quick Invoke Guide

```bash
# Full-Stack Startup Engineer - MVP Builder
orchestrator:build path=./spec.md

# Codebase Auditor - Find tech debt & architecture issues
quality:audit path=./src

# Production Debugging Expert - Root cause analysis
quality:debug stack_trace="[your error]"

# Technical Lead - Strategic decisions & risk assessment
orchestrator:review path=./architecture.md
orchestrator:tradeoff path=./architecture.md
orchestrator:risk path=./architecture.md

# Performance Engineering Expert - Optimize for scale
quality:perf path=./src baseline="[current metrics]" scale="1M users"

# Backend Systems Architect - Infrastructure design
architect:design requirements="[your requirements]"

# Frontend Architecture Expert - Component design
architect:frontend requirements="[your requirements]"

# Security Auditor - OWASP vulnerability scanning
quality:security path=./src compliance="SOC2"

# DevOps & Infrastructure Engineer - Deployment setup
implementer:pipeline path=./
implementer:docker path=./
implementer:iac path=./
```

---

## 📋 Specialist Modes by Role

### 1️⃣ Full-Stack Startup Engineer

**Command:**
```bash
orchestrator:build path=./design
```

**Outputs:**
- ✅ System architecture
- ✅ File structure
- ✅ Database schema
- ✅ API endpoints
- ✅ UI architecture
- ✅ Production-ready code

**When to use:** Starting new project from scratch, need complete MVP

---

### 2️⃣ Codebase Auditor

**Command:**
```bash
quality:audit path=./src
```

**Outputs:**
- ✅ Architecture breakdown
- ✅ Critical problem areas
- ✅ Refactoring strategies
- ✅ Improved code examples

**When to use:** Joining existing project, understanding tech debt

---

### 3️⃣ Production Debugging Expert

**Command:**
```bash
quality:debug stack_trace="NullPointerException at OrderService.java:42" path=./src
```

**Outputs:**
- ✅ Code functionality breakdown
- ✅ Root cause analysis
- ✅ Failure mechanism explanation
- ✅ Edge case discovery
- ✅ Fixed code with tests
- ✅ Prevention strategy

**When to use:** Live production incident, need comprehensive RCA

---

### 4️⃣ Technical Lead

**Command:**
```bash
orchestrator:review path=./architecture.md
orchestrator:tradeoff path=./architecture.md
orchestrator:risk path=./architecture.md
```

**Outputs:**
- ✅ Clarifying questions
- ✅ Decision challenges
- ✅ Scaling risk identification
- ✅ Architecture recommendations
- ✅ Implementation plan
- ✅ Tradeoff analysis

**When to use:** Before coding major features, need strategic guidance

---

### 5️⃣ Performance Engineering Expert

**Command:**
```bash
quality:perf path=./src baseline="500ms response time" scale="1M users"
```

**Outputs:**
- ✅ Bottleneck analysis
- ✅ Before/after code examples
- ✅ Optimization roadmap (quick wins first)
- ✅ Scalability projections
- ✅ Monitoring strategy

**When to use:** Application is slow, need to scale to millions of users

---

### 6️⃣ Backend Systems Architect

**Command:**
```bash
architect:design requirements="e-commerce platform for 1M users"
```

**Outputs:**
- ✅ System topology (C4 diagram)
- ✅ Component structure
- ✅ Data flow design
- ✅ API contracts (OpenAPI)
- ✅ Database schema (DDL)
- ✅ Caching strategy
- ✅ Production code stubs

**When to use:** Designing system from scratch, scaling infrastructure

---

### 7️⃣ Frontend Architecture Expert

**Command:**
```bash
architect:frontend requirements="product card component for e-commerce"
```

**Outputs:**
- ✅ Component hierarchy
- ✅ Reusable component architecture
- ✅ Props/API design
- ✅ Accessibility (WCAG 2.1 AA)
- ✅ Production implementation
- ✅ Usage examples
- ✅ Best practices

**When to use:** Building UI systems, component libraries

---

### 8️⃣ Security Auditor

**Command:**
```bash
quality:security path=./src compliance="SOC2"
```

**Outputs:**
- ✅ Vulnerability report
- ✅ Severity levels (Critical/High/Medium/Low)
- ✅ Attack scenarios
- ✅ Secure code fixes
- ✅ Compliance coverage
- ✅ Remediation plan

**When to use:** Security compliance deadline, vulnerability assessment needed

---

### 9️⃣ DevOps & Infrastructure Engineer

**Command:**
```bash
implementer:pipeline path=./
implementer:docker path=./
implementer:iac path=./
```

**Outputs:**
- ✅ Infrastructure architecture
- ✅ Deployment workflow
- ✅ CI/CD pipeline (GitHub Actions, GitLab CI, etc.)
- ✅ Docker/Kubernetes setup
- ✅ Monitoring strategy
- ✅ Deployment checklist

**When to use:** Preparing for production, setting up CI/CD infrastructure

---

## 🎯 Quick Reference Matrix

| Specialist Role | Agent:Function | Use When |
|---|---|---|
| Full-Stack Engineer | `orchestrator:build` | New project from scratch |
| Code Auditor | `quality:audit` | Existing codebase analysis |
| Debugging Expert | `quality:debug` | Production incident RCA |
| Technical Lead | `orchestrator:review/tradeoff/risk` | Strategic decisions needed |
| Performance Expert | `quality:perf` | Performance optimization |
| Backend Architect | `architect:design` | System architecture design |
| Frontend Expert | `architect:frontend` | UI component architecture |
| Security Auditor | `quality:security` | Security vulnerability scan |
| DevOps Engineer | `implementer:pipeline/docker/iac` | Deployment setup |

---

## 💡 Pro Tips

### Combine modes for complete workflows:
```bash
# Full startup workflow
orchestrator:plan path=./requirements.md
architect:design path=./plan-output/
implementer:full path=./architecture/
quality:review
orchestrator:pr
```

### Use conversational debugging:
```bash
quality:diagnose problem="Orders taking 10 seconds to load"
```

### Batch process multiple PRs:
```bash
quality:batch-review from=./reviews.json
```

### Create custom workflows:
- Technical Lead mode: `review` + `tradeoff` + `risk` (all together)
- DevOps Complete mode: `pipeline` + `docker` + `iac` (all together)
- Full Audit mode: `audit` + `security` + `perf` (comprehensive)

---

## 📖 Complete Documentation

See `SPECIALIST_MODES_MAPPING.md` for detailed mode descriptions and architectural mappings.

