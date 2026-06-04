# Ideation Engine Module

## Purpose
Systematically refine vague ideas into detailed project specifications with expert feedback integration. Used by orchestrator:ideate.

## Process Phases

### Phase 1: Clarification (Questions)
Ask 5-7 targeted questions to solidify the concept:
1. **Core Purpose** — "What problem does this solve? Who has it?"
2. **Target Users** — "Who are the primary users? What's their scale?"
3. **Success Definition** — "How do you measure success?"
4. **Constraints** — "What are hard constraints (time, budget, team)?"
5. **Differentiation** — "What makes this different from existing solutions?"
6. **MVP Scope** — "What's the minimum viable product?"
7. **Key Risks** — "What could cause this to fail?"

### Phase 2: Concept Refinement
Synthesize clarification answers into:
- **Refined Concept Statement** (2-3 sentences)
- **Target Users** (personas, scale)
- **Success Criteria** (measurable)
- **Core Assumptions** (what must be true)

### Phase 3: Project Planning
Generate detailed breakdown:
- **Milestones** (phases with duration, deliverables, dependencies)
- **Tasks** (granular work items, 2-week max estimates)
- **Resource Allocation** (skills needed, team composition)
- **RAID Analysis** (Risks, Assumptions, Issues, Dependencies)
- **Timeline** (start → end, critical path)

## Output Format

```yaml
idea_specification:
  original_concept: "Build a multi-tenant SaaS analytics platform"
  
  refined_concept: "A web-based analytics platform enabling SMBs to ingest data from 10+ sources, create custom dashboards, set KPI alerts, and export reports with role-based access control."
  
  target_users:
    - segment: "SMB founders/operators"
      scale: "100-500 employees"
      pain_point: "Manual reporting taking 20+ hours/month"
  
  success_criteria:
    - "50+ integrations by launch"
    - "< 5s dashboard load time"
    - "99.5% uptime"
    - "< 2% monthly churn"
  
  assumptions:
    - "SMB market is underserved"
    - "Integration via APIs is sufficient (not webhooks initially)"
    - "~100 customers in year 1"
    - "Team can handle 24/7 operations"
  
project_plan:
  milestones:
    - name: "Foundation & Integrations"
      duration: "8 weeks"
      deliverables:
        - "Data ingestion API"
        - "3 source integrations (Google Analytics, Stripe, Slack)"
        - "User authentication & multi-tenancy"
      dependencies: []
    
    - name: "Dashboard Builder"
      duration: "6 weeks"
      deliverables:
        - "Widget library (20+ widgets)"
        - "Drag-drop dashboard builder"
        - "Sharing & permission controls"
      dependencies: ["Foundation & Integrations"]
  
  tasks:
    - id: "T001"
      title: "Design data ingestion API"
      milestone: "Foundation & Integrations"
      estimate_days: 5
      required_skills: ["Backend", "Database", "API Design"]
      dependencies: []
    
    - id: "T002"
      title: "Implement Google Analytics integration"
      milestone: "Foundation & Integrations"
      estimate_days: 10
      required_skills: ["Backend", "HTTP Client"]
      dependencies: ["T001"]
  
  resources:
    - skill: "Backend Engineer (Python/Node)"
      quantity: 2
      seniority: "mid"
      duration_weeks: 14
    
    - skill: "Frontend Engineer (React)"
      quantity: 1
      seniority: "senior"
      duration_weeks: 6
    
    - skill: "Database Engineer"
      quantity: 1
      seniority: "mid"
      duration_weeks: 8
    
    - skill: "DevOps/Infra"
      quantity: 0.5
      seniority: "mid"
      duration_weeks: 14

raid_analysis:
  risks:
    - id: "R001"
      description: "Integration complexity—each source has different API patterns"
      severity: "HIGH"
      mitigation: "Use adapter pattern; hire contractor with integration experience"
    
    - id: "R002"
      description: "Competitive response—larger platforms may add free tier"
      severity: "MEDIUM"
      mitigation: "Focus on SMB-specific features (simplicity, no data science needed)"
  
  assumptions:
    - "Team can ship MVP in 14 weeks"
    - "Integrations API becomes stable (not breaking frequently)"
    - "No major competitors emerge in 6 months"
  
  issues:
    - "Decision: PostgreSQL or MongoDB for analytics data?"
    - "Decision: Self-hosted or managed infrastructure?"
  
  dependencies:
    - "External: Google Analytics API stability"
    - "Internal: Database team available by week 3"
    - "Internal: Hiring: Need 2 senior backend engineers"

timeline:
  start_date: "2026-07-01"
  end_date: "2026-09-15"
  total_weeks: 11
  critical_path: ["T001", "T002", "T003", "Dashboard UI", "Testing & Launch"]
  risks: "Aggressive timeline—only 1 week buffer before target launch"
```

## Usage Example

**Input to module:**
```
idea: "Build a multi-tenant SaaS analytics platform"
constraints:
  timeline: "6 months"
  budget: "$200k"
  team_size: 4
  tech_stack: "Python/FastAPI, React, PostgreSQL"
mode: "comprehensive"  # or "quick"
```

**Output from module:**
- idea-spec.md (refined concept, assumptions, success criteria)
- project-plan.json (milestones, tasks, resources)
- raid-analysis.md (risks, assumptions, issues, dependencies)
- project-plan.csv (exportable to Jira, Asana, Monday.com)

## Notes
- Questions should be open-ended to encourage discovery
- Concept refinement should incorporate expert feedback (from expert_panel_generator)
- Project tasks should never exceed 2 weeks (break larger items into sub-tasks)
- Timeline should include 10-20% buffer for unknowns
