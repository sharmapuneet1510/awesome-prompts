# Examples

**Worked scenarios**, organised by the agent doing the work.

For *what to run*, see [../01-workflows/](../01-workflows/). These show a full
run in detail, including the output.

| File | Scenarios |
|---|---|
| [orchestrator.md](orchestrator.md) | E-Commerce MVP (greenfield, requirements → launch) · Legacy system modernisation (monolith → microservices) |
| [architect.md](architect.md) | Real-Time Chat (C4 topology, OpenAPI, PostgreSQL DDL, React hierarchy, WCAG audit) · Monolith → microservices with strangler pattern and zero-downtime migration |
| [implementer.md](implementer.md) | Auth service: build → test → doc, then pipeline → Docker → Kubernetes |
| [quality.md](quality.md) | PR review · Codebase audit · Security audit · Performance analysis · Bug RCA · Batch review |
| [general.md](general.md) | Assorted shorter examples across the system |

---

## By workflow

| Workflow | Example |
|---|---|
| [01 New project](../01-workflows/01-start-new-project.md) | [orchestrator.md](orchestrator.md) — E-Commerce MVP; [architect.md](architect.md) — Chat design |
| [03 From a requirement](../01-workflows/03-feature-from-requirement.md) | [implementer.md](implementer.md) — Auth service |
| [04 Understand a codebase](../01-workflows/04-understand-a-codebase.md) | [quality.md](quality.md) — Codebase audit |
| [06 Review a PR](../01-workflows/06-review-a-pull-request.md) | [quality.md](quality.md) — PR review |
| [07 Production incident](../01-workflows/07-fix-production-incident.md) | [quality.md](quality.md) — Bug RCA |
| [08 Audit security](../01-workflows/08-audit-security.md) | [quality.md](quality.md) — Security audit |
| [09 Optimise performance](../01-workflows/09-optimise-performance.md) | [quality.md](quality.md) — Performance analysis |
| [10 Modernise legacy](../01-workflows/10-modernise-legacy-system.md) | [orchestrator.md](orchestrator.md) · [architect.md](architect.md) — brownfield |
| [11 Set up CI/CD](../01-workflows/11-set-up-cicd.md) | [implementer.md](implementer.md) — pipeline, Docker, K8s |

---

## Gaps

**No examples exist yet for the companion functions** added in v5.0.0 —
`ba:discover`, `ba:clarify`, `ba:brd`, `ba:trace`, `architect:analyse`,
`architect:adr`, `architect:spec`, `quality:observe`, `quality:qa`.

That means [workflow 02](../01-workflows/02-feature-from-conversation.md) and
[workflow 05](../01-workflows/05-record-a-decision.md) have no worked example.
Until they do, the function files are the closest thing:
`agents/business_analyst/functions/`, `agents/architect/functions/`, and
`agents/quality/functions/`.

Listed here rather than left as a dead link.

---

## Age

These files date from June 2026 and describe the system as it was at 28–31
functions. The command chains they show still work; they simply do not cover the
newer functions. Counts inside them are stale — the verified numbers are in
[../02-reference/README.md](../02-reference/README.md).
