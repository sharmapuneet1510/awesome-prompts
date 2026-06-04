# Design: Orchestrator Expansion — `ideate` and `solve` Functions

**Date:** June 4, 2026  
**Status:** Design Approved  
**Version:** 1.0  
**Scope:** Add two new functions to orchestrator agent + three reusable prompt modules  

---

## Executive Summary

The orchestrator agent gains two new strategic functions by composing reusable prompt modules:

1. **`orchestrator:ideate`** — Transform vague ideas into validated project plans with expert feedback (inspired by Carter Leffen's ideation.prompt)
2. **`orchestrator:solve`** — Solve design bottlenecks with multi-dimensional solutions (DB design, throttling, structure, etc.)

Both functions leverage a modular architecture (ideation_engine, design_solver, expert_panel_generator) that avoids duplication and enables future extensions.

---

## Context & Motivation

**Problem:** 
- Users often arrive with half-formed ideas that need structured refinement before planning
- Mid-design, teams need help solving specific bottlenecks (scalability, performance, architecture) across multiple dimensions

**Solution:**
- Add `orchestrator:ideate` for idea refinement + expert panel feedback
- Add `orchestrator:solve` for prescriptive design problem-solving
- Use modular prompt engines to avoid duplication and maintain the skill-based architecture philosophy

**Why Modular?**
- Aligns with awesome-prompts' existing skill-based architecture (22 reusable skills)
- Both functions share expert_panel_generator; keeping it modular avoids code duplication
- Enables future functions (e.g., `orchestrator:validate`, `architect:critique`) to reuse modules
- Easier to test, maintain, and export across 8 platforms

---

## Architecture

### File Structure

```
orchestrator/
├── functions/
│   ├── ideate.md               ← NEW: orchestrator:ideate
│   ├── solve.md                ← NEW: orchestrator:solve
│   ├── plan.md                 ← existing
│   ├── build.md                ← existing
│   ├── context.md              ← existing
│   ├── pr.md                   ← existing
│   ├── review.md               ← existing
│   ├── tradeoff.md             ← existing
│   └── risk.md                 ← existing
│
└── modules/
    ├── ideation_engine.md           ← NEW: Idea refinement → project plan
    ├── design_solver.md             ← NEW: Bottleneck analysis → solutions
    └── expert_panel_generator.md    ← NEW: Virtual expert creation & feedback
```

### Execution Model

**Functions call modules; modules don't call each other.**

```
orchestrator:ideate
  ├─ calls ideation_engine (phases 1-3)
  └─ calls expert_panel_generator (phase 2)

orchestrator:solve
  ├─ calls design_solver (phases 1-2)
  └─ calls expert_panel_generator (phase 3, optional)

expert_panel_generator
  └─ standalone module (used by both functions)
```

---

## Function Specifications

### `orchestrator:ideate`

**Purpose:** Systematically refine raw ideas into detailed, validated project specifications.

**Input:**
```yaml
idea:
  concept: string              # Raw idea/concept
  constraints:
    timeline: string?          # e.g., "3 months"
    budget: string?            # e.g., "$50k"
    team_size: int?            # e.g., 5 people
    tech_stack: string?        # e.g., "Python, React, PostgreSQL"
  mode: enum?                  # "quick" (1 round) or "comprehensive" (3 rounds, default)
```

**Process:**

**Phase 1: Clarification** (5-7 questions)
- ideation_engine asks targeted questions to solidify the concept
- User answers each question
- Engine synthesizes into a refined concept statement

**Phase 2: Expert Panel** (domain-specific feedback)
- expert_panel_generator creates 3-5 domain experts
- Each expert asks targeted challenges
- User addresses feedback
- Feedback is incorporated into the plan

**Phase 3: Planning** (detailed breakdown)
- ideation_engine generates:
  - Milestones (phases with duration + deliverables)
  - Tasks (granular work items, 2-week estimates)
  - Resource allocation (skills needed, team composition)
  - RAID analysis (Risks, Assumptions, Issues, Dependencies)
  - Timeline (Gantt-style breakdown)

**Output:**

```
idea-spec.md
├─ Original concept
├─ Refined concept statement
├─ Assumptions (from expert panel feedback)
├─ Success criteria
└─ Constraints

project-plan.json
├─ milestones[]
│  ├─ name, duration, deliverables, dependencies
├─ tasks[]
│  ├─ id, title, milestone, estimate (days), assignee_skills
├─ resources[]
│  ├─ skill, quantity, seniority, notes
└─ timeline (start → end)

raid-analysis.md
├─ Risks (technical, staffing, timeline)
├─ Assumptions (external, technical, business)
├─ Issues (current blockers)
└─ Dependencies (internal, external)

project-plan.csv
└─ Exportable to Jira, Asana, Monday.com
```

**Success Criteria:**
- ✓ Idea is concrete enough for implementer to work with
- ✓ Expert feedback is captured and addressed
- ✓ Project plan is realistic (tasks are 2-week estimate max, dependencies are clear)
- ✓ RAID analysis identifies risks early

**Example Usage:**
```
orchestrator:ideate
idea="Build a multi-tenant SaaS analytics platform"
constraints="Timeline: 6 months, Budget: $200k, Team: 4 engineers"
```

---

### `orchestrator:solve`

**Purpose:** Solve specific design bottlenecks with prescriptive, multi-dimensional solutions.

**Input:**
```yaml
problem:
  statement: string            # e.g., "Database queries are slow, need to scale to 10M users"
  current_design: string?      # Optional: current architecture description
  constraints:
    performance_target: string # e.g., "< 100ms p99 latency"
    budget: string?
    team_skills: string[]      # e.g., ["Java", "PostgreSQL", "AWS"]
    tech_stack: string?
  dimensions: string[]         # Which to address: db, api, structure, caching, deployment, etc.
```

**Process:**

**Phase 1: Diagnosis** (constraint analysis)
- design_solver analyzes the problem statement
- Identifies root causes and constraints
- Maps problem to solution dimensions

**Phase 2: Solution Generation** (2-3 approaches per dimension)
For each dimension (DB, API throttling, project structure, etc.):
- Approach A: (e.g., "Sharding + read replicas")
- Approach B: (e.g., "NoSQL with eventual consistency")
- Approach C: (e.g., "CQRS pattern")

Each approach includes:
- Architecture diagram (ASCII or description)
- Implementation complexity (low/medium/high)
- Performance impact (before/after metrics)
- Cost implications
- Team effort (weeks to implement)
- Scalability ceiling

**Phase 3: Pro/Con Analysis**
- design_solver compares approaches across dimensions
- Trade-off matrix (complexity vs. cost vs. performance)
- Ranked recommendation with justification

**Phase 4: Expert Review** (optional)
- expert_panel_generator creates virtual architects
- They challenge the proposals: "What about X?", "Have you considered Y?"
- Feedback is incorporated into recommendations

**Output:**

```
solutions.md
├─ Problem diagnosis
├─ Constraint analysis
└─ Solution breakdown (per dimension)
   ├─ Database Design
   │  ├─ Approach A: [architecture + pros/cons]
   │  ├─ Approach B: [architecture + pros/cons]
   │  └─ Approach C: [architecture + pros/cons]
   ├─ API Throttling
   │  └─ [similar structure]
   ├─ Project Structure
   │  └─ [similar structure]
   └─ [other dimensions]

recommendation.md
├─ Best-fit solution (across dimensions)
├─ Justification (why this approach)
├─ Phased adoption roadmap
├─ Effort estimate
└─ Risk mitigation

comparison-table.csv
├─ Complexity, Cost, Performance, Scalability (per approach)
└─ Exportable to spreadsheets for stakeholder review

implementation-roadmap.json
├─ Phase 1: [tasks, timeline, skills needed]
├─ Phase 2: [tasks, timeline, skills needed]
└─ Phase 3: [tasks, timeline, skills needed]
```

**Success Criteria:**
- ✓ Solutions are concrete and implementable
- ✓ Trade-offs are explicitly stated with metrics
- ✓ Recommendation is justified with performance/cost/complexity data
- ✓ Phased roadmap is realistic (no phase > 4 weeks)

**Example Usage:**
```
orchestrator:solve
problem="Database queries are slow, need to scale to 10M users"
current_design="Monolithic PostgreSQL, single write master, read replicas"
constraints="Performance target: < 100ms p99, Budget: $50k infrastructure"
dimensions=["db", "api", "structure"]
```

---

## Reusable Modules

### `ideation_engine.md`

**Purpose:** Structured prompt for idea refinement → project planning

**Inputs:**
- Raw concept + constraints
- User answers to clarification questions
- Expert panel feedback (if using)

**Outputs:**
- Refined concept statement
- Assumptions list
- Project plan (milestones, tasks, resources)
- RAID analysis

**Key Phases:**
1. Clarification questions (5-7 targeted Qs)
2. Synthesis (refine concept)
3. Planning (breakdown milestones → tasks)
4. RAID analysis (identify risks early)

**Reusable by:** `orchestrator:ideate`, future planning functions

---

### `design_solver.md`

**Purpose:** Structured prompt for bottleneck analysis → multi-solution generation

**Inputs:**
- Problem statement + constraints
- Current design (if provided)
- Solution dimensions to address

**Outputs:**
- Problem diagnosis (root cause analysis)
- 2-3 approaches per dimension
- Pro/con comparison
- Ranked recommendation

**Key Phases:**
1. Diagnosis (constraint mapping)
2. Solution generation (2-3 per dimension)
3. Trade-off analysis (metrics-based comparison)
4. Recommendation (justified ranking)

**Reusable by:** `orchestrator:solve`, future optimization functions

---

### `expert_panel_generator.md`

**Purpose:** Create virtual domain experts for feedback/challenges

**Inputs:**
- Topic/domain (e.g., "scalable database architecture")
- Context (current problem or proposed solution)

**Outputs:**
- 3-5 virtual experts with profiles
- Expert questions/challenges
- Feedback synthesis

**Expert Types:**
- Technical architect
- DevOps/infrastructure specialist
- Performance engineer
- Security specialist
- Product/business lead

**Reusable by:** `orchestrator:ideate` (phase 2), `orchestrator:solve` (phase 4), future review functions

---

## Integration with Existing Pipeline

### Linear Execution Pipeline

```
User Requirement
    ↓
orchestrator:ideate (OPTIONAL—for vague ideas)
    ├─ Refine concept
    ├─ Expert feedback
    └─ Output: detailed spec + project plan
    ↓
orchestrator:plan (Parse requirements → tasks)
    ↓
architect:design (System topology, API, schema)
    ↓
orchestrator:solve (OPTIONAL—for bottleneck solving)
    ├─ Analyze constraints
    ├─ Multi-dimensional solutions
    └─ Output: recommendations + roadmap
    ↓
implementer:full (Build + test + doc)
    ↓
quality:review
    ↓
orchestrator:pr
```

**Key Points:**
- Both `ideate` and `solve` are **optional insertion points**
- They don't disrupt existing pipeline
- `ideate` sits before planning (for vague ideas)
- `solve` sits after architecture (for bottleneck solving)

### When to Use Each Function

| Function | When | Input | Output |
|----------|------|-------|--------|
| `orchestrator:ideate` | Raw idea + constraints | Concept | Spec + project plan + RAID |
| `orchestrator:plan` | Clear requirements | Req doc | Task breakdown + execution order |
| `architect:design` | Tasks defined | Tasks | System topology + API + schema |
| `orchestrator:solve` | Mid-design bottlenecks | Problem + constraints | Solutions + recommendation + roadmap |
| `implementer:full` | Architecture approved | Architecture | Code + tests + docs |

---

## Data Flow & Context Management

### Context Preservation

Both functions preserve context between phases:
- User inputs are accumulated
- Expert feedback is indexed
- Outputs are self-contained (can be passed to next function)

**Example:** 
```
orchestrator:ideate output (idea-spec.md + project-plan.json)
  ↓
orchestrator:plan (takes project-plan.json as starting point)
  ↓
architect:design (uses milestones + tasks as scope)
```

---

## Testing Strategy

### Unit Tests (per module)
- **ideation_engine:** 
  - Generates well-formed questions ✓
  - Synthesizes feedback correctly ✓
  - Produces valid JSON/CSV output ✓
  
- **design_solver:**
  - Diagnoses constraints correctly ✓
  - Generates 2-3 approaches per dimension ✓
  - Comparison table is complete ✓
  
- **expert_panel_generator:**
  - Creates diverse expert profiles ✓
  - Questions are relevant to domain ✓
  - Feedback is synthesized correctly ✓

### Integration Tests (function level)
- `orchestrator:ideate` end-to-end: idea → spec → plan → RAID ✓
- `orchestrator:solve` end-to-end: problem → diagnosis → solutions → recommendation ✓
- Both functions produce valid, exportable outputs ✓

### Acceptance Tests (user workflow)
- User can invoke `orchestrator:ideate` with raw idea and get project plan ✓
- User can invoke `orchestrator:solve` with bottleneck and get solutions with pros/cons ✓
- Outputs are usable by downstream functions (plan, architecture) ✓

---

## Exportability & Platform Support

Both functions will be exported via `tools/exporter.py` to:

- **Claude Code** — native markdown instructions
- **GitHub** — markdown format with platform-agnostic prompts
- **Copilot/Cursor/Windsurf** — platform instruction files
- **OpenAI/Gemini** — system prompt format
- **Continue/Aider** — LLM-agnostic markdown

**Export structure:**
```
exports/
├── claude/
│   └── orchestrator-ideate.md
│   └── orchestrator-solve.md
├── copilot/
│   └── orchestrator_ideate.md
│   └── orchestrator_solve.md
└── [other platforms...]
```

---

## Open Questions & Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Should `ideate` and `solve` be mandatory or optional in pipeline? | Optional insertion points | Different users have different starting points (vague idea vs. clear requirements) |
| Should expert panel be inline or optional? | Optional (default: on, can be skipped) | Quick mode for experienced teams, comprehensive mode for new projects |
| Should outputs be JSON/CSV or markdown? | Both | CSV for project management tools, markdown for documentation |
| Should modules be versioned separately? | No, they follow orchestrator version | Simpler maintenance, all functions updated together |

---

## Success Metrics

- ✓ Both functions produce outputs that downstream functions can consume
- ✓ Expert feedback is actionable and synthesized
- ✓ Project plans are realistic (no task > 2 weeks, dependencies are clear)
- ✓ Design solutions have measurable trade-offs (performance, cost, complexity)
- ✓ Functions are exportable to all 8 platforms without modification

---

## Timeline & Dependencies

- **Modules:** ideation_engine, design_solver, expert_panel_generator (3 weeks parallel)
- **Functions:** orchestrator:ideate, orchestrator:solve (2 weeks sequential after modules)
- **Testing:** 1 week
- **Export & Documentation:** 1 week
- **Total:** ~6-7 weeks

---

## Appendix: Examples

### Example 1: `orchestrator:ideate` Output

**Input:**
```
idea="Build a multi-tenant SaaS analytics platform"
constraints="Timeline: 6 months, Budget: $200k, Team: 4 engineers"
```

**Output (idea-spec.md):**
```markdown
# Idea Specification: Multi-Tenant SaaS Analytics Platform

## Original Concept
Build a multi-tenant SaaS analytics platform for SMBs to track and visualize business metrics.

## Refined Concept Statement
A web-based, multi-tenant analytics platform that enables SMBs to:
- Ingest data from 10+ sources (Google Analytics, Stripe, Slack, etc.)
- Create custom dashboards with drag-and-drop widgets
- Set alerts on KPI thresholds
- Export reports (CSV, PDF, email)
- Manage team permissions with role-based access control

## Assumptions
- SMB definition: 10-500 employees
- Primary use case: monthly reporting
- Integration via APIs (not webhooks initially)
- ~100 customers in year 1

## Success Criteria
- 50+ integrations by launch
- < 5 second dashboard load time
- 99.5% uptime
- < 2% monthly churn
```

**Output (project-plan.json):**
```json
{
  "milestones": [
    {
      "name": "Foundation & Integrations",
      "duration": "8 weeks",
      "deliverables": ["Data ingestion API", "3 source integrations", "User auth"]
    },
    {
      "name": "Dashboard Builder",
      "duration": "6 weeks",
      "deliverables": ["Widget library", "Drag-drop builder", "Sharing controls"]
    }
  ],
  "tasks": [...],
  "resources": [...]
}
```

---

### Example 2: `orchestrator:solve` Output

**Input:**
```
problem="Database queries are slow, p99 latency 5s. Need to scale to 10M users."
dimensions=["db", "api", "structure"]
```

**Output (solutions.md - excerpt):**
```markdown
## Database Design Solutions

### Approach A: Sharding + Read Replicas
- Shard users by account_id
- 8 shards, cross-region replication
- Performance: p99 < 100ms
- Complexity: HIGH (schema changes, data migration)
- Effort: 6 weeks

### Approach B: NoSQL (MongoDB) + Caching
- Migrate analytics writes to MongoDB
- Redis for hot reads
- Performance: p99 < 50ms
- Complexity: MEDIUM (new tech stack)
- Effort: 4 weeks

### Approach C: CQRS Pattern + Event Streaming
- Separate read/write models
- Kafka for event streaming
- Read model in Elasticsearch
- Performance: p99 < 80ms
- Complexity: HIGH (architectural shift)
- Effort: 8 weeks
```

---

## Approval Checklist

- [x] Architecture is clear (functions → modules, no duplication)
- [x] Data flow is well-defined (inputs/outputs for each phase)
- [x] Integration with existing pipeline is non-disruptive
- [x] Success criteria are measurable
- [x] Testing strategy is comprehensive
- [x] Exportability is addressed
- [x] Timeline and dependencies are realistic

---

**Document Status:** Ready for user review and implementation planning.
