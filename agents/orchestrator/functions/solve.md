# Function: orchestrator:solve

**Prefix:** `orchestrator:solve`

**Purpose:** Solve specific design bottlenecks with multi-dimensional, prescriptive solutions.

## Input Specification

```yaml
# Required
problem: string              # Problem statement (e.g., "queries slow, need 10M scale")

# Optional
current_design: string?      # Current architecture description
constraints:
  performance_target: string # e.g., "p99 < 100ms"
  budget: string?            # e.g., "$50k infrastructure"
  team_skills: string[]?     # e.g., ["Java", "PostgreSQL", "AWS"]
  timeline: string?          # e.g., "4 weeks"

dimensions: string[]         # Which to address: db, api, structure, caching, deployment
include_expert_review: bool? # Request expert challenges (default: true)
```

## Process

1. **Diagnosis** (design_solver)
   - Analyze problem statement → identify root causes
   - Map constraints (performance, budget, team, timeline)
   - Classify solution dimensions

2. **Solution Generation** (design_solver)
   - For each dimension, generate 2-3 approaches
   - Each approach includes: architecture, complexity, performance, cost, scalability, effort

3. **Trade-Off Analysis** (design_solver)
   - Compare approaches in matrix (complexity vs. cost vs. performance)
   - Rank by best fit for constraints

4. **Expert Review** (expert_panel_generator, optional)
   - Create virtual architects
   - Each expert challenges the proposed solutions
   - Feedback incorporated into recommendation

5. **Recommendation**
   - Select best-fit approach per dimension
   - Create phased adoption roadmap
   - Estimate total effort and cost

## Output

```
solutions.md
├─ Problem diagnosis
├─ Solution breakdown (per dimension)
│  ├─ Approach A (architecture, pros/cons, metrics)
│  ├─ Approach B (architecture, pros/cons, metrics)
│  └─ Approach C (architecture, pros/cons, metrics)

recommendation.md
├─ Best-fit solution (across dimensions)
├─ Justification (why this approach)
├─ Phased adoption roadmap
├─ Effort estimate (weeks)
└─ Risk mitigation

comparison-table.csv
├─ Complexity, Cost, Performance, Scalability (per approach)
└─ Exportable to spreadsheets

implementation-roadmap.json
├─ Phase 1: [tasks, timeline, skills needed]
├─ Phase 2: [tasks, timeline, skills needed]
└─ Phase 3: [tasks, timeline, skills needed]
```

## Usage Example

```
orchestrator:solve
problem="Database queries are slow, p99=5s. Need to scale to 10M users."
current_design="Monolithic PostgreSQL, single master, 3 read replicas"
constraints={
  performance_target: "p99 < 100ms",
  budget: "$50k infrastructure",
  team_skills: ["Java", "PostgreSQL", "AWS"],
  timeline: "4 weeks"
}
dimensions=["db", "api", "structure"]
include_expert_review=true
```

## Success Criteria

- ✓ Solutions are concrete and implementable
- ✓ Trade-offs are explicitly stated with metrics (performance, cost, complexity)
- ✓ Recommendation is justified with measurable data
- ✓ Phased roadmap is realistic (no phase > 4 weeks)
- ✓ User can compare approaches and make informed decision

## Invokes

- `design_solver` (phases 1-3)
- `expert_panel_generator` (phase 4, optional)
