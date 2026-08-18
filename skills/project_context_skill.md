---
name: Project Context Skill
version: 1.0
description: >
  Reusable skill for the Central Project Context — the shared, persistent
  knowledge base all companions read before acting and write after deciding.
  Defines the 14-node tree, a template per node, and the ownership matrix
  saying which agent writes what and when.
---

# Project Context Skill — v1.0

## Purpose

Give every companion one shared memory. Without it each agent re-derives the
same facts from the codebase on every invocation, drifts from the others, and
loses everything the moment its context window closes.

The Project Context holds **durable knowledge** — things that stay true across
features. Feature-scoped artifacts belong in `specs/<feature-name>/`; decision
reasoning belongs in `docs/adr/`.

This skill is **internal** — called by agents, not invoked directly by users.

---

## Artifact Location

Lives in the **downstream project**, one file per node:

```
<project-root>/docs/project-context/
├── README.md                  ← index; links every node below
├── project-overview.md
├── business-context.md
├── technical-context.md
├── architecture-context.md
├── known-behaviours.md
├── technical-debt.md
├── mvp-scope.md
├── quality/
│   ├── sanity.md
│   ├── regression.md
│   ├── integration.md
│   ├── performance.md
│   └── security.md
├── dependencies.md
├── risks.md
├── release-history.md
├── open-questions.md
└── ai-memory.md
```

---

## Ownership Matrix

The requirement does not say who maintains which node. Without an answer,
every node is either everyone's job or nobody's. This is the answer.

| Node | Owner | Written when |
|---|---|---|
| `project-overview.md` | `orchestrator` | Project init; on scope change |
| `business-context.md` | `business_analyst` | After `ba:brd` |
| `technical-context.md` | `architect` | After `architect:spec` |
| `architecture-context.md` | `architect` | After `architect:spec` |
| `known-behaviours.md` | `architect` | After `architect:analyse` finds a quirk |
| `technical-debt.md` | `architect` | On any ADR with non-empty Technical Debt |
| `mvp-scope.md` | `business_analyst` | After `ba:brd`; on scope change |
| `quality/*.md` (5) | `quality` | After `quality:qa` |
| `dependencies.md` | `implementer` | On dependency add, remove, or major bump |
| `risks.md` | `orchestrator` | At `orchestrator:plan` and `orchestrator:risk` |
| `release-history.md` | `orchestrator` | On release |
| `open-questions.md` | any | On encountering an unresolved question |
| `ai-memory.md` | any | Append-only, timestamped |

**Read-before-act:** every companion reads `README.md` plus the nodes relevant
to its function before doing anything else. **Write-after-decide:** an owner
updates its node only after a decision is approved, never on speculation.

Non-owners never edit a node directly. They raise the gap in
`open-questions.md` and let the owner resolve it.

---

## Node Templates

### `project-overview.md`

```markdown
# Project Overview
**Last updated:** <YYYY-MM-DD> by <agent>

## What this system does
<three sentences, no jargon — a new joiner must understand it>

## Who uses it
<user types and their primary job>

## Current phase
<discovery | MVP | growth | maintenance | sunset>

## Repository map
| Path | Contains |
|---|---|
```

### `business-context.md`

Sections, in this order, from requirement §4: **Goals**, **Stakeholders**,
**Business flows**, **Business rules**, **Domain glossary**, **Regulatory
constraints**, **Assumptions**.

```markdown
# Business Context
**Last updated:** <YYYY-MM-DD> by business_analyst

## Goals
- G-1: <measurable outcome, with its metric>

## Stakeholders
| Role | Name/Team | Cares about | Approves |
|---|---|---|---|

## Business Flows
### BF-1: <flow name>
<trigger → steps → outcome>

## Business Rules
| ID | Rule | Source | Enforced in |
|---|---|---|---|
| BR-1 | <rule as a testable statement> | <ticket/policy> | <component> |

## Domain Glossary
| Term | Means | Does not mean |
|---|---|---|

## Regulatory Constraints
| Constraint | Applies to | Evidence required |
|---|---|---|

## Assumptions
| ID | Assumption | If wrong, then | Validated? |
|---|---|---|---|
```

Business rules get stable `BR-n` IDs because acceptance criteria, ADRs, and
tests all cite them.

### `technical-context.md`

Sections from requirement §4: **Architecture**, **Services**, **APIs**,
**Database**, **Messaging**, **External systems**, **Deployment**,
**Observability**. Each entry names the ADR that established it where one
exists.

```markdown
# Technical Context
**Last updated:** <YYYY-MM-DD> by architect

## Architecture
<style, and the ADR that chose it>

## Services
| Service | Responsibility | Owns data | Language/Runtime |
|---|---|---|---|

## APIs
| API | Consumers | Auth | Spec | ADR |
|---|---|---|---|---|

## Database
| Store | Engine | Holds | Migration tool | ADR |
|---|---|---|---|---|

## Messaging
| Topic/Queue | Producer | Consumers | Delivery guarantee | ADR |
|---|---|---|---|---|

## External Systems
| System | Used for | Failure mode | Fallback |
|---|---|---|---|

## Deployment
<environments, pipeline, rollback mechanism>

## Observability
<metrics, traces, logs, dashboards, alert thresholds>
```

### `architecture-context.md`

The shape and the reasons: component diagram, boundaries and why they sit
where they do, cross-cutting concerns, and the constraints no future change
may violate.

````markdown
# Architecture Context
**Last updated:** <YYYY-MM-DD> by architect

## Component Diagram
```mermaid
graph TD
```

## Boundaries
| Boundary | Separates | Why here | ADR |
|---|---|---|---|

## Cross-Cutting Concerns
| Concern | Handled by | Applies to |
|---|---|---|

## Invariants
<constraints no change may violate, each with the ADR that set it>
````

### `known-behaviours.md`

From requirement §4: expected behaviour, intentional limitations, known quirks.
The distinction matters — a quirk recorded here is a decision, not a bug, and
stops the team from "fixing" it repeatedly.

```markdown
# Known Behaviours
**Last updated:** <YYYY-MM-DD> by architect

## Expected Behaviour
| ID | Behaviour | Surprising because | Correct because |
|---|---|---|---|

## Intentional Limitations
| ID | Limitation | Chosen in | Revisit when |
|---|---|---|---|

## Known Quirks
| ID | Quirk | Impact | Why not fixed |
|---|---|---|---|
```

### `technical-debt.md`

Fields from requirement §4: issue, impact, workaround, recommendation, priority.

```markdown
# Technical Debt
**Last updated:** <YYYY-MM-DD> by architect

| ID | Issue | Impact | Workaround | Recommendation | Priority | Source ADR |
|---|---|---|---|---|---|---|
| TD-1 | <what is wrong> | <what it costs, concretely> | <what we do today> | <what to do> | P1/P2/P3 | ADR-000X |
```

Every ADR with non-empty `Consequences → Technical Debt` adds a row here. Debt
recorded in an ADR but absent from this table is a traceability violation.

### `mvp-scope.md`

```markdown
# MVP / Scope
**Last updated:** <YYYY-MM-DD> by business_analyst

## In Scope
| ID | Capability | Satisfies goal | Jira |
|---|---|---|---|

## Explicitly Out of Scope
| Capability | Why excluded | Revisit when |
|---|---|---|

## Definition of Done for MVP
- [ ] <criterion>
```

The out-of-scope table matters as much as the in-scope one — it is what stops
scope creep from being re-litigated every sprint.

### `quality/*.md`

Five files, one per suite from requirement §4. Each holds **reusable
scenarios**, not one-off test cases, so they accumulate across features.

```markdown
# <Sanity | Regression | Integration | Performance | Security> Scenarios
**Last updated:** <YYYY-MM-DD> by quality

| ID | Scenario | Covers | Automated | Location | Last run |
|---|---|---|---|---|---|
| SAN-1 | <given/when/then> | BR-1, REQ-2 | yes/no | <path> | <date> |
```

Suite-specific extras:

- **sanity** — must be runnable in under five minutes; note the budget.
- **regression** — each row cites the incident or bug that created it.
- **integration** — name the external systems touched and their test doubles.
- **performance** — every row carries a numeric threshold and the load profile.
- **security** — map rows to the OWASP category they cover.

### `dependencies.md`

```markdown
# Dependencies
**Last updated:** <YYYY-MM-DD> by implementer

## Runtime
| Package | Version | Used for | Risk if unmaintained | ADR |
|---|---|---|---|---|

## Build & Dev
| Package | Version | Used for |
|---|---|---|

## External Services
| Service | SLA | Cost driver | Exit plan |
|---|---|---|---|
```

### `risks.md`

```markdown
# Risks
**Last updated:** <YYYY-MM-DD> by orchestrator

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| R-1 | <what could go wrong> | H/M/L | H/M/L | <action> | <role> | open/closed |
```

### `release-history.md`

```markdown
# Release History
**Last updated:** <YYYY-MM-DD> by orchestrator

| Version | Date | Jira | ADRs applied | PRs | Notes |
|---|---|---|---|---|---|
```

This is the last hop of the traceability chain — a release row must name the
ADRs it shipped.

### `open-questions.md`

```markdown
# Open Questions
**Last updated:** <YYYY-MM-DD>

| ID | Question | Raised by | Blocks | Owner | Answer |
|---|---|---|---|---|---|
| Q-1 | <question> | <agent> | <what is blocked> | <role> | <or "open"> |
```

Any companion may append. Only the owner writes the answer. An answered
question that changed a decision must also produce an ADR.

### `ai-memory.md`

Append-only. Never edit or delete an entry — supersede it with a newer one.

```markdown
# AI Memory
Append-only. Newest last.

## <YYYY-MM-DD HH:MM> — <agent>
**Learned:** <what was discovered that is not derivable from the code>
**Why it matters:** <what it changes next time>
**Supersedes:** <earlier entry timestamp | none>
```

Record what the codebase cannot tell you: dead ends already explored, why an
obvious approach fails here, tribal knowledge from a conversation. Do **not**
record what a file read would reveal.

---

## Bootstrapping

When `docs/project-context/` does not exist, create the tree with every node
stubbed and `README.md` linking all of them. Populate `project-overview.md`
and `technical-context.md` from `context_builder_skill` output if
`docs/context/` is present. Leave the rest as templates with `Status: not yet
populated` rather than inventing content — an empty node is honest, a
hallucinated one is worse than nothing.

---

## Staleness

Every node carries a `Last updated` line. Any node untouched for more than 90
days while its owning area has changed is reported by `quality:observe` as a
staleness finding — an observation, never an automatic edit.

---

## Related

- `skills/adr_skill.md` — decisions that feed technical debt and context
- `skills/current_tech_spec_skill.md` — the current-state projection
- `skills/traceability_skill.md` — validates context links
- `skills/context_builder_skill.md` — bootstraps overview and technical context
