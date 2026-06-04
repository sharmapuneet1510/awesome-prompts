# Orchestrator Agent

The orchestrator agent handles **strategic planning and execution coordination** across the development lifecycle.

## Functions (9 Total)

### Idea Refinement & Problem-Solving

- **[orchestrator:ideate](./functions/ideate.md)** — Transform vague ideas into validated project plans
  - Uses: ideation_engine, expert_panel_generator
  - Input: Raw concept + constraints
  - Output: idea-spec.md, project-plan.json, raid-analysis.md, CSV export
  - Use when: "I have an idea but need to flesh it out into a project plan"
  
- **[orchestrator:solve](./functions/solve.md)** — Solve design bottlenecks with multi-dimensional solutions
  - Uses: design_solver, expert_panel_generator
  - Input: Problem statement + constraints + dimensions
  - Output: solutions.md, recommendation.md, comparison-table.csv, roadmap.json
  - Use when: "Our database is slow and we need options for scaling"

### Planning & Execution

- **[orchestrator:plan](./functions/plan.md)** — Parse requirements, break into tasks
  - Input: Requirements document (free text, JIRA, GitHub, etc.)
  - Output: requirements.md, task-breakdown.json, execution-order.txt
  - Use when: "I have clear requirements and need to break them into tasks"

- **[orchestrator:build](./functions/build.md)** — Full-stack generation (end-to-end)
  - Input: Requirements
  - Output: Complete system (architecture → code → tests → docs)
  - Use when: "Build everything from requirements in one go"

- **[orchestrator:context](./functions/context.md)** — Build project context (architecture, tech stack)
  - Input: Existing codebase
  - Output: architecture.md, tech-stack.md, context.json, design.html visualization
  - Use when: "I need to understand project structure and technology stack"

- **[orchestrator:pr](./functions/pr.md)** — Package deliverables, create GitHub PR
  - Input: Generated code + tests + docs
  - Output: GitHub PR with comprehensive description
  - Use when: "I have code ready to propose as a pull request"

### Review & Risk Analysis

- **[orchestrator:review](./functions/review.md)** — Strategic architecture review with challenges
  - Input: Architecture design
  - Output: Review report with challenge questions and 5-year assessment
  - Use when: "I want expert-level feedback on system design"

- **[orchestrator:tradeoff](./functions/tradeoff.md)** — Generate 3-option complexity analysis
  - Input: Problem statement + constraints
  - Output: 3 approaches with trade-off analysis and ranked recommendation
  - Use when: "I need to compare architectural approaches"

- **[orchestrator:risk](./functions/risk.md)** — Risk assessment with mitigation strategies
  - Input: Project plan + constraints
  - Output: Risk assessment covering operational, data, scaling, team, integration risks
  - Use when: "I need to identify and mitigate risks in my project"

## Reusable Modules (3 Total)

Modules are composed by functions to avoid duplication and enable future extensions.

- **[expert_panel_generator](./modules/expert_panel_generator.md)** — Create virtual domain experts for feedback
  - Used by: orchestrator:ideate (phase 2), orchestrator:solve (phase 4)
  - Creates: 3-5 diverse experts (architect, DevOps, performance, security, product)
  - Generates: Targeted challenges, feedback synthesis, recommendations
  - When to use: When you need expert perspective on ideas or designs

- **[ideation_engine](./modules/ideation_engine.md)** — Systematically refine ideas → project plans
  - Used by: orchestrator:ideate
  - Creates: Clarification questions, concept refinement, project breakdown
  - Generates: Milestones, tasks, resources, RAID analysis, timeline
  - When to use: When you have a vague idea and need structured planning

- **[design_solver](./modules/design_solver.md)** — Solve bottlenecks with multi-dimensional solutions
  - Used by: orchestrator:solve
  - Analyzes: Problem diagnosis, constraint mapping
  - Generates: 2-3 approaches per dimension (DB, API, structure, etc.)
  - Outputs: Trade-off analysis, ranked recommendations, phased roadmaps
  - When to use: When you have a design problem and need solution options

## Usage Patterns

### Pattern 1: Idea Refinement (Green-field)

```
User: "I want to build X"
    ↓
orchestrator:ideate (idea + constraints)
    ├─ Clarify concept
    ├─ Expert feedback
    └─ Generate project plan
    ↓
orchestrator:plan (parse ideation output)
    ↓
architect:design
    ↓
implementer:full
```

**Best for:** New projects starting from vague ideas

---

### Pattern 2: Bottleneck Solving (Brown-field)

```
System has problem (slow queries, scaling issues, etc.)
    ↓
orchestrator:solve (problem + constraints)
    ├─ Analyze root cause
    ├─ Generate solution options
    ├─ Compare trade-offs
    └─ Recommend best fit
    ↓
implementer:full (implement recommendation)
```

**Best for:** Existing systems with specific bottlenecks

---

### Pattern 3: Full-Stack from Requirement

```
orchestrator:plan (requirement)
    ↓
architect:design
    ↓
orchestrator:solve (if mid-design bottlenecks emerge)
    ↓
implementer:full
```

**Best for:** Clear requirements that may need design consultation

---

## When to Use Each Function

| Scenario | Function | Input | Output |
|----------|----------|-------|--------|
| "I have a vague idea" | `orchestrator:ideate` | Concept | Validated spec + project plan |
| "I have requirements" | `orchestrator:plan` | Requirement doc | Task breakdown |
| "Our database is slow" | `orchestrator:solve` | Problem + constraints | Solution options + recommendation |
| "Design the system" | `architect:design` | Tasks | System topology + API + schema |
| "Build everything" | `orchestrator:build` | None | Full-stack implementation |
| "Understand current system" | `orchestrator:context` | Codebase | Architecture + tech stack + visualization |
| "Review architecture" | `orchestrator:review` | Architecture | Review report + challenges |
| "Compare options" | `orchestrator:tradeoff` | Problem + constraints | 3 approaches with trade-offs |
| "Identify risks" | `orchestrator:risk` | Project plan | Risk assessment + mitigation |
| "Create PR" | `orchestrator:pr` | Code + tests + docs | GitHub PR |

## Module Dependencies

```
orchestrator:ideate
    ├─ ideation_engine (clarification, planning, RAID)
    └─ expert_panel_generator (expert feedback)

orchestrator:solve
    ├─ design_solver (diagnosis, solutions, trade-offs)
    └─ expert_panel_generator (expert review)

expert_panel_generator (reusable)
    ↑ used by ideate, solve, and future review functions
```

## File Structure

```
agents/orchestrator/
├── README.md                 ← You are here
├── functions/
│   ├── ideate.md            ← NEW (Transform ideas → plans)
│   ├── solve.md             ← NEW (Solve bottlenecks)
│   ├── plan.md              (Parse requirements → tasks)
│   ├── build.md             (Full-stack generation)
│   ├── context.md           (Build project context)
│   ├── pr.md                (Package and create PR)
│   ├── review.md            (Architecture review)
│   ├── tradeoff.md          (Compare 3 options)
│   └── risk.md              (Risk assessment)
└── modules/
    ├── expert_panel_generator.md    ← NEW (Virtual experts)
    ├── ideation_engine.md           ← NEW (Idea refinement)
    └── design_solver.md             ← NEW (Solve bottlenecks)
```

## Testing

### Run Module Tests
```bash
python tests/test_orchestrator_modules.py
```

Expected:
```
✓ expert_panel_generator module structure test passed
✓ ideation_engine module structure test passed
✓ design_solver module structure test passed
✓ All module structure tests passed
```

### Run Function Tests
```bash
python tests/test_orchestrator_functions.py
```

Expected:
```
✓ orchestrator:ideate function structure test passed
✓ orchestrator:solve function structure test passed
✓ All orchestrator functions passed structure tests
```

## Version History

- **v3.1** (2026-06-04) — Add `orchestrator:ideate` and `orchestrator:solve` functions + 3 reusable modules
  - New: orchestrator:ideate (transform ideas → validated plans)
  - New: orchestrator:solve (solve bottlenecks with options)
  - New: expert_panel_generator module (virtual experts)
  - New: ideation_engine module (idea refinement)
  - New: design_solver module (multi-dimensional solutions)

- **v3.0** — Initial 5-agent architecture
  - 5 agents: orchestrator, architect, implementer, quality, business_analyst
  - Lean, role-based model with skill composition
  - Linear pipeline: plan → design → implement → review → pr

## Integration with Other Agents

```
orchestrator (strategic planning)
    ↓ provides plan to
architect (system design)
    ↓ provides architecture to
implementer (code generation)
    ↓ provides artifacts to
quality (review & validation)
    ↓ final review, then
orchestrator (package & PR)
```

The orchestrator acts as the "conductor" — it initiates workflows, handles mid-design bottlenecks via solve(), and packages final deliverables.
