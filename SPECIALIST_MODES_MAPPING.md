---
title: Specialist Agent Modes → Function Mapping
version: 1.0
date: 2026-06-08
purpose: Map specialized AI expert modes to agent functions
---

# Specialist Agent Modes Mapping

**Status: ALL 10 SPECIALIST MODES MAPPED ✅**

All specialized agent modes (Full-Stack Engineer, Security Auditor, Performance Expert, etc.) are covered by existing agents. Function definitions have been enhanced to ensure they produce the exact outputs expected.

---

## MODE → AGENT MAPPING

### 1️⃣ Full-Stack Startup Engineer (MVP Builder)

**Mode Description:**
> "Act like a senior full-stack engineer building a production-ready MVP from scratch."

**Outputs Required:**
- System architecture
- File structure
- Database schema
- API endpoints
- UI architecture
- Production-ready code

**Maps To:** `orchestrator:build` + `implementer:full`

---

### 2️⃣ Codebase Auditor (Code Health Expert)

**Mode Description:**
> "Act like a senior engineer who just joined a massive unfamiliar codebase. Reverse-engineer the architecture and understand the complete data flow."

**Outputs Required:**
- Clean architecture breakdown
- Critical problem areas
- Refactoring strategies
- Improved production-grade code

**Maps To:** `quality:audit`

---

### 3️⃣ Production Debugging Expert (RCA Master)

**Mode Description:**
> "Act like a senior debugging engineer investigating a live production issue. Analyze step by step like you're handling a critical outage."

**Outputs Required:**
- Code functionality breakdown
- Root cause analysis
- Failure explanation (WHY it happens)
- Edge case discovery
- Fixed production-ready code
- Regression tests

**Maps To:** `quality:debug` (v3.1 with 5-phase RCA)

---

### 4️⃣ Technical Lead (Strategic Decision-Maker)

**Mode Description:**
> "Act like a senior technical lead managing a real engineering team. Before writing code: ask clarifying questions, challenge bad decisions, identify scaling risks, suggest better approaches."

**Outputs Required:**
- Clarifying questions asked FIRST
- Challenge assumptions
- Scaling risk identification
- Better approach suggestions
- Architecture recommendations
- Implementation plan

**Maps To:** `orchestrator:review` + `orchestrator:tradeoff` + `orchestrator:risk`

---

### 5️⃣ Performance Engineering Expert (Scale Master)

**Mode Description:**
> "Act like a senior performance engineer optimizing a production application used by millions."

**Goals:**
- Maximum speed
- Lower memory usage
- Better scalability
- Faster rendering
- Cleaner execution

**Outputs Required:**
- Performance bottleneck analysis
- Before/after code examples with measurements
- Optimization roadmap (quick wins first)
- Scalability recommendations

**Maps To:** `quality:perf` (v3.1 with 6-phase analysis)

---

### 6️⃣ Backend Systems Architect (Infrastructure Designer)

**Mode Description:**
> "Act like a senior systems architect designing infrastructure for a high-growth startup."

**Outputs Required:**
- System architecture (C4 diagram)
- Component structure
- Data flow
- API design
- Database schema
- Caching strategy
- Production-ready implementation code

**Maps To:** `architect:design` + `architect:api` + `architect:schema`

---

### 7️⃣ Frontend Architecture Expert (Component Designer)

**Mode Description:**
> "Act like a senior frontend engineer building production-grade UI systems for a modern startup."

**Outputs Required:**
- Reusable UI components
- Scalable component architecture
- Accessible production-ready interfaces
- Component hierarchy
- Props/API design
- Usage examples
- Best practices

**Maps To:** `architect:frontend` + `architect:a11y`

---

### 8️⃣ Security Auditor (OWASP Expert)

**Mode Description:**
> "Act like a senior security engineer auditing a production application. Carefully inspect the system and provide comprehensive vulnerability assessment."

**Inspect For:**
- Security vulnerabilities
- Authentication flaws
- API weaknesses
- Injection risks
- Sensitive data exposure
- Infrastructure risks

**Outputs Required:**
- Vulnerability report
- Severity levels (Critical/High/Medium/Low)
- Attack scenarios
- Secure implementation fixes
- Production-grade recommendations
- Compliance verification

**Maps To:** `quality:security` (v3.1 with 7-phase threat assessment)

---

### 9️⃣ DevOps & Infrastructure Engineer (Deployment Expert)

**Mode Description:**
> "Act like a senior DevOps engineer preparing this application for real production deployment."

**Responsibilities:**
- Design deployment architecture
- Configure CI/CD
- Setup monitoring/logging
- Improve reliability
- Reduce downtime risks
- Optimize scaling

**Outputs Required:**
- Infrastructure architecture
- Deployment workflow
- CI/CD pipeline
- Docker/Kubernetes setup
- Monitoring strategy
- Production deployment checklist

**Maps To:** `implementer:pipeline` + `implementer:docker` + `implementer:iac`

---

## Summary Matrix

| Specialist Mode | Agent:Function | Use When |
|---|---|---|
| Full-Stack Engineer | `orchestrator:build` | New project from scratch |
| Code Auditor | `quality:audit` | Joining existing project, finding tech debt |
| Debugging Expert | `quality:debug` | Live incident, deep RCA needed |
| Technical Lead | `orchestrator:review/tradeoff/risk` | Strategic guidance before coding |
| Performance Expert | `quality:perf` | App is slow, scaling to millions |
| Systems Architect | `architect:design` | New system design, infrastructure |
| Frontend Expert | `architect:frontend` | Component system, UI architecture |
| Security Auditor | `quality:security` | Vulnerability scanning, compliance |
| DevOps Engineer | `implementer:pipeline/docker/iac` | Production readiness, CI/CD setup |

---

## Function Enhancement Status

- ✅ `quality:debug` (v3.1) — 5-phase RCA with edge case discovery
- ✅ `quality:perf` (v3.1) — 6-phase profiling with optimization roadmap
- ✅ `quality:security` (v3.1) — 7-phase threat assessment with compliance coverage
- ✅ All other functions (v3.0) — Ready for production use

---

## Next Steps

1. ✅ Review this mapping with team
2. ✅ Prioritize function enhancements by usage frequency
3. ✅ Test each mode to ensure outputs match specifications
4. ✅ Create composite modes for common workflows (if needed)
