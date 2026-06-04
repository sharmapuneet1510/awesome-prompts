# Function: orchestrator:ideate

**Prefix:** `orchestrator:ideate`

**Purpose:** Transform vague ideas into validated project plans with expert feedback.

## Input Specification

```yaml
# Required
idea: string               # Raw concept or idea

# Optional
constraints:
  timeline: string?        # e.g., "6 months", "asap"
  budget: string?          # e.g., "$200k", "bootstrap"
  team_size: int?          # e.g., 5
  tech_stack: string[]?    # e.g., ["Python", "React", "PostgreSQL"]

mode: enum?               # "quick" (1 iteration) or "comprehensive" (3 iterations, default)
```

## Process

1. **Clarification** (ideation_engine)
   - Ask 5-7 targeted questions
   - Collect user answers
   - Synthesize into refined concept

2. **Expert Feedback** (expert_panel_generator)
   - Create 3-5 domain experts
   - Each expert asks 2-3 challenges
   - Synthesize feedback

3. **Project Planning** (ideation_engine)
   - Generate milestones (with deliverables, dependencies)
   - Generate tasks (granular, 2-week max estimates)
   - Allocate resources (skills, seniority, duration)
   - Create RAID analysis (risks, assumptions, issues, dependencies)
   - Create timeline (start date, end date, critical path)

4. **Validation** (user review)
   - User reviews plan
   - Adjustments if needed
   - Final approval

## Output

```
idea-spec.md
├─ Original concept
├─ Refined concept statement
├─ Target users
├─ Success criteria
├─ Assumptions
└─ Constraints

project-plan.json
├─ milestones[] (with deliverables, dependencies)
├─ tasks[] (with estimates, skills, dependencies)
├─ resources[] (with quantity, seniority, duration)
└─ timeline (start, end, critical path)

raid-analysis.md
├─ Risks (with severity, mitigation)
├─ Assumptions
├─ Issues (open questions)
└─ Dependencies (external, internal)

project-plan.csv
└─ Exportable to Jira, Asana, Monday.com
```

## Usage Example

```
orchestrator:ideate
idea="Build a multi-tenant SaaS analytics platform"
constraints={
  timeline: "6 months",
  budget: "$200k",
  team_size: 4,
  tech_stack: ["Python", "React", "PostgreSQL"]
}
mode="comprehensive"
```

## Success Criteria

- ✓ Idea is concrete enough for implementer:build to work with
- ✓ Project plan is realistic (no task > 2 weeks, dependencies are clear)
- ✓ RAID analysis identifies key risks early
- ✓ User can export plan to project management tool (CSV)
- ✓ Expert feedback is incorporated into assumptions

## Invokes

- `ideation_engine` (phases 1, 3)
- `expert_panel_generator` (phase 2)
