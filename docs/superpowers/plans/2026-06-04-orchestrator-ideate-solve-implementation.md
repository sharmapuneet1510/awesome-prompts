# Orchestrator `ideate` and `solve` Functions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two new strategic functions (`orchestrator:ideate` and `orchestrator:solve`) to the orchestrator agent, backed by three reusable prompt modules, enabling idea refinement and design problem-solving workflows.

**Architecture:** The orchestrator agent is extended with two new callable functions that compose three reusable prompt modules (ideation_engine, design_solver, expert_panel_generator). This modular design avoids duplication, aligns with the skill-based architecture, and enables future functions to reuse components. Both functions are optional insertion points in the existing linear pipeline.

**Tech Stack:** Markdown (prompt definitions), Python (test infrastructure), JSON (configuration/output formats)

---

## Phase 1: Create Reusable Modules (Parallel Tasks 1-3)

### Task 1: Create `expert_panel_generator` Module

**Files:**
- Create: `agents/orchestrator/modules/expert_panel_generator.md`
- Test: `tests/test_orchestrator_modules.py` (Step 5)

- [ ] **Step 1: Create orchestrator modules directory**

```bash
mkdir -p /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/agents/orchestrator/modules
mkdir -p /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/agents/orchestrator/functions
```

- [ ] **Step 2: Write expert_panel_generator.md**

```markdown
# Expert Panel Generator Module

## Purpose
Create virtual domain experts for targeted feedback, challenges, and perspective-sharing. Used by orchestrator:ideate (phase 2) and orchestrator:solve (phase 4).

## Invocation
When you need expert feedback on a topic/problem:
1. Specify domain/topic (e.g., "scalable database architecture")
2. Provide context (current problem or proposed solution)
3. Module generates 3-5 diverse experts
4. Experts ask challenges and provide feedback

## Expert Types Generated
- **Technical Architect** — System design, trade-offs, scalability
- **DevOps/Infrastructure Specialist** — Deployment, monitoring, reliability
- **Performance Engineer** — Optimization, benchmarking, bottleneck analysis
- **Security Specialist** — Auth, data protection, compliance, threat modeling
- **Product/Business Lead** — User impact, cost, time-to-market, ROI

## Process

### Phase 1: Expert Panel Creation
For the given domain/topic, create 3-5 experts with:
- Name and title
- Relevant background (2-3 key accomplishments)
- Perspective/bias (e.g., "prioritizes performance over simplicity")
- Key concern for this domain

### Phase 2: Expert Challenges
Each expert asks 2-3 targeted questions:
- Technical Architect: "How will this scale to 10M users?"
- Security Specialist: "What are the data protection implications?"
- etc.

### Phase 3: Feedback Synthesis
Aggregate feedback into:
- Common concerns (by frequency)
- Unique perspectives (by expert)
- Recommendations (by consensus)

## Output Format

```yaml
experts:
  - name: "Dr. Sarah Chen"
    title: "Principal Architect"
    background: "Led architecture for 50M+ user platform at Uber; scaled PostgreSQL from 100K to 10M TPS"
    perspective: "Pragmatist—prioritizes shipping over perfect design"
    key_concern: "Operational complexity"
    
    challenges:
      - "How will your team operationalize this? Is it in your skillset?"
      - "What's the migration path from your current system?"
    
  - name: "Marcus Williams"
    title: "DevOps/SRE Lead"
    background: "Managed infrastructure for multi-region SaaS; expert in Kubernetes, observability"
    perspective: "Reliability-first—designs for graceful degradation"
    key_concern: "Operational burden and observability"
    
    challenges:
      - "How do you observe this in production?"
      - "What's your backup/disaster recovery plan?"

feedback_synthesis:
  common_concerns:
    - "Operational complexity for team of 4"
    - "Need observability/monitoring from day 1"
  unique_perspectives:
    - "Security: consider compliance implications"
    - "Performance: benchmark before/after"
  recommendations:
    - "Phase the rollout—don't migrate everything at once"
    - "Start with one shard, measure before expanding"
```

## Usage Example

**Input to module:**
```
domain: "multi-tenant SaaS architecture"
context: "Proposed: microservices with 10+ services, event-driven messaging, PostgreSQL sharding"
challenge_areas: ["scalability", "operational complexity", "data consistency"]
```

**Output from module:**
- 5 expert profiles (see above)
- 10-15 targeted challenges
- Synthesis of common concerns + unique perspectives

## Notes
- Experts should be diverse in background and perspective
- Challenges should be specific to the domain and proposed solution (not generic)
- Synthesis should highlight areas of consensus and disagreement
- Module is stateless—can be called multiple times for different domains
```

- [ ] **Step 3: Verify expert_panel_generator.md is complete**

Check:
- ✓ Purpose is clear (virtual domain experts)
- ✓ Invocation pattern is explicit
- ✓ All 5 expert types are defined
- ✓ 3-phase process is documented
- ✓ Output format is concrete (YAML with example)
- ✓ Usage example shows input/output clearly

- [ ] **Step 4: Commit expert_panel_generator module**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
git add agents/orchestrator/modules/expert_panel_generator.md
git commit -m "feat: add expert_panel_generator reusable module"
```

- [ ] **Step 5: Write failing test for expert_panel_generator**

Create `tests/test_orchestrator_modules.py`:

```python
import json
import sys
sys.path.insert(0, '/Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts')

def test_expert_panel_generator_structure():
    """Test that expert_panel_generator module can be imported and has required sections."""
    with open('agents/orchestrator/modules/expert_panel_generator.md', 'r') as f:
        content = f.read()
    
    # Verify required sections
    required_sections = [
        "# Expert Panel Generator Module",
        "## Purpose",
        "## Invocation",
        "## Expert Types Generated",
        "## Process",
        "## Output Format",
        "## Usage Example"
    ]
    
    for section in required_sections:
        assert section in content, f"Missing section: {section}"
    
    # Verify all 5 expert types are documented
    expert_types = [
        "Technical Architect",
        "DevOps/Infrastructure Specialist",
        "Performance Engineer",
        "Security Specialist",
        "Product/Business Lead"
    ]
    
    for expert in expert_types:
        assert expert in content, f"Missing expert type: {expert}"

if __name__ == '__main__':
    test_expert_panel_generator_structure()
    print("✓ expert_panel_generator module structure test passed")
```

Run test:
```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
python tests/test_orchestrator_modules.py
```

Expected output: `✓ expert_panel_generator module structure test passed`

---

### Task 2: Create `ideation_engine` Module

**Files:**
- Create: `agents/orchestrator/modules/ideation_engine.md`

- [ ] **Step 1: Write ideation_engine.md**

```markdown
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
```

- [ ] **Step 2: Verify ideation_engine.md is complete**

Check:
- ✓ 3 phases are documented (Clarification, Refinement, Planning)
- ✓ 7 clarification questions are provided
- ✓ Output format is YAML with concrete examples
- ✓ RAID sections are detailed (R001, R002, etc.)
- ✓ Task estimates are reasonable (all ≤ 10 days)
- ✓ Timeline includes 10-20% buffer

- [ ] **Step 3: Commit ideation_engine module**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
git add agents/orchestrator/modules/ideation_engine.md
git commit -m "feat: add ideation_engine reusable module"
```

- [ ] **Step 4: Add test for ideation_engine to test_orchestrator_modules.py**

Add to existing `tests/test_orchestrator_modules.py`:

```python
def test_ideation_engine_structure():
    """Test ideation_engine module has all required process phases and outputs."""
    with open('agents/orchestrator/modules/ideation_engine.md', 'r') as f:
        content = f.read()
    
    # Verify required phases
    phases = [
        "### Phase 1: Clarification",
        "### Phase 2: Concept Refinement",
        "### Phase 3: Project Planning"
    ]
    
    for phase in phases:
        assert phase in content, f"Missing phase: {phase}"
    
    # Verify 7 clarification questions
    questions = [
        "Core Purpose",
        "Target Users",
        "Success Definition",
        "Constraints",
        "Differentiation",
        "MVP Scope",
        "Key Risks"
    ]
    
    for question in questions:
        assert question in content, f"Missing question: {question}"
    
    # Verify output sections
    outputs = [
        "idea_specification",
        "project_plan",
        "raid_analysis",
        "timeline"
    ]
    
    for output in outputs:
        assert output in content, f"Missing output section: {output}"

if __name__ == '__main__':
    test_expert_panel_generator_structure()
    test_ideation_engine_structure()
    print("✓ All module structure tests passed")
```

Run test:
```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
python tests/test_orchestrator_modules.py
```

Expected output: `✓ All module structure tests passed`

- [ ] **Step 5: Commit updated tests**

```bash
git add tests/test_orchestrator_modules.py
git commit -m "test: add ideation_engine structure validation tests"
```

---

### Task 3: Create `design_solver` Module

**Files:**
- Create: `agents/orchestrator/modules/design_solver.md`

- [ ] **Step 1: Write design_solver.md**

```markdown
# Design Solver Module

## Purpose
Solve specific design bottlenecks with multi-dimensional, prescriptive solutions. Used by orchestrator:solve.

## Process Phases

### Phase 1: Diagnosis
Analyze the problem statement to:
1. Identify root causes (not symptoms)
2. Map constraints (performance, budget, team skills, timeline)
3. Classify solution dimensions (DB, API throttling, project structure, caching, deployment)
4. Set success metrics (performance targets, cost limits, complexity tolerance)

### Phase 2: Solution Generation
For each dimension, generate 2-3 approaches:
- **Approach A:** [Name + architecture]
- **Approach B:** [Name + architecture]
- **Approach C:** [Name + architecture]

Each approach includes:
- Architecture diagram (ASCII or narrative)
- Implementation steps
- Complexity rating (Low/Medium/High)
- Performance impact (before/after metrics)
- Cost implications (infrastructure, team effort)
- Scalability ceiling (max scale achievable)
- Team effort (weeks to implement)

### Phase 3: Trade-Off Analysis
Compare approaches in a matrix:
- Complexity (implementation, operational)
- Performance (latency, throughput)
- Cost (infrastructure, engineering)
- Scalability (max users/data)

Rank by best fit for stated constraints.

### Phase 4: Recommendation (Optional Expert Review)
- Select best-fit approach per dimension
- Create phased adoption roadmap
- Identify risks and mitigation
- Estimate total effort and timeline

## Output Format

```yaml
problem_diagnosis:
  statement: "Database queries are slow, p99 latency 5s. Need to scale to 10M users."
  root_cause: "Single PostgreSQL master without read scaling; all queries hit write master"
  current_design: "Monolithic PostgreSQL; single write master, 3 read replicas (not used effectively)"
  constraints:
    performance_target: "p99 latency < 100ms"
    budget: "$50k infrastructure"
    team_skills: ["Java", "PostgreSQL", "AWS"]
    timeline: "4 weeks implementation"
  success_metrics:
    - "p99 latency reduced to < 100ms"
    - "Support 10M users"
    - "Infrastructure cost < $50k/month"

solution_dimensions:
  database_design:
    - name: "Sharding + Read Replicas"
      architecture: "Shard users by account_id into 8 shards; each shard has 1 write master + 3 read replicas. Route writes to master, reads to replicas."
      pros:
        - "Proven approach at scale (Uber, Stripe, Airbnb)"
        - "Excellent performance (p99 < 50ms)"
        - "High scalability (10M+ users)"
      cons:
        - "Complex to operate (shard rebalancing, hotspot management)"
        - "Schema changes are expensive (must run across all shards)"
        - "Distributed transactions harder"
      complexity: "HIGH"
      performance_impact:
        - "Query latency: 5s → 50ms (100x improvement)"
        - "Throughput: 1K qps → 100K qps"
      cost:
        - "Infrastructure: $20k/month (8 x m5.2xlarge instances)"
        - "Engineering: 6 weeks (2 backend engineers)"
      scalability_ceiling: "100M+ users"
      team_effort_weeks: 6
    
    - name: "NoSQL (MongoDB) + Redis Caching"
      architecture: "Migrate analytics writes to MongoDB; cache hot reads in Redis (TTL 15 min). Writes go directly to Mongo; reads hit Redis first, fallback to Mongo."
      pros:
        - "Simple to scale (MongoDB auto-sharding)"
        - "Fast reads (Redis < 5ms)"
        - "Good for analytics workload (flexible schema)"
      cons:
        - "New technology (team learning curve)"
        - "Eventual consistency (may see stale data)"
        - "Loss of ACID guarantees"
      complexity: "MEDIUM"
      performance_impact:
        - "Hot read latency: 5s → 5ms (1000x)"
        - "Cold read latency: 5s → 50ms (100x)"
      cost:
        - "Infrastructure: $15k/month (Mongo Atlas m30 + Redis enterprise)"
        - "Engineering: 4 weeks (2 backend engineers)"
      scalability_ceiling: "50M+ users"
      team_effort_weeks: 4
    
    - name: "CQRS + Event Streaming (Kafka)"
      architecture: "Separate read/write models. Writes → Kafka → Event processors → Read store (Elasticsearch). Reads hit Elasticsearch. Strongconsistency via versioning."
      pros:
        - "Extremely scalable (event streaming handles unlimited volume)"
        - "Auditable (all events stored)"
        - "Decoupled systems (read/write scale independently)"
      cons:
        - "Complex architecture (steep learning curve)"
        - "Operational burden (manage Kafka cluster)"
        - "Eventual consistency (slight read lag)"
      complexity: "HIGH"
      performance_impact:
        - "Write latency: 5s → 50ms (100x)"
        - "Read latency: 5s → 100ms (50x)"
      cost:
        - "Infrastructure: $25k/month (Kafka cluster + Elasticsearch)"
        - "Engineering: 8 weeks (2-3 backend engineers)"
      scalability_ceiling: "1B+ users"
      team_effort_weeks: 8
  
  api_throttling:
    - name: "Token Bucket (Redis-backed)"
      architecture: "Token bucket per user/account; refill at configured rate (e.g., 1000 req/min). Check token availability before serving request."
      complexity: "LOW"
      performance_impact: "< 1ms overhead per request"
      cost: "Minimal (Redis cluster already needed)"
      team_effort_weeks: 1
    
    - name: "Leaky Bucket (Database-backed)"
      architecture: "Track request count per window in PostgreSQL; reject if count > limit."
      complexity: "MEDIUM"
      performance_impact: "5-10ms overhead per request"
      cost: "Minimal"
      team_effort_weeks: 2
    
    - name: "Sliding Window Log (Kafka)"
      architecture: "Log all requests to Kafka; count requests in sliding window; enforce limit."
      complexity: "HIGH"
      performance_impact: "< 1ms overhead"
      cost: "Kafka cluster"
      team_effort_weeks: 3

  project_structure:
    - name: "Monolithic (status quo)"
      description: "Single codebase, single deployment"
      pros: ["Simple", "Easy testing", "Single deployment"]
      cons: ["Scalability bottleneck", "Hard to parallelize team"]
      complexity: "LOW"
      team_effort_weeks: 0
    
    - name: "Microservices (API, Analytics, Auth)"
      description: "3 independent services; API Gateway routes requests"
      pros: ["Scale independently", "Team can parallelize", "Easier to replace components"]
      cons: ["Distributed system complexity", "Operational burden", "Data consistency challenges"]
      complexity: "MEDIUM"
      team_effort_weeks: 4
    
    - name: "Modular Monolith"
      description: "Single codebase, internal module boundaries, ready for future extraction"
      pros: ["Scalable architecture", "Team parallelization", "Easy to migrate to microservices later"]
      cons: ["Requires discipline (module boundaries)", "Testing more complex"]
      complexity: "MEDIUM"
      team_effort_weeks: 2

trade_off_analysis:
  comparison_matrix:
    - dimension: "Database Design"
      approaches:
        - name: "Sharding + Replicas"
          complexity: 9
          performance: 9
          cost: 7
          scalability: 9
          feasibility: 7
          rank: 1
        
        - name: "NoSQL + Redis"
          complexity: 6
          performance: 8
          cost: 8
          scalability: 7
          feasibility: 8
          rank: 2
        
        - name: "CQRS + Kafka"
          complexity: 9
          performance: 8
          cost: 6
          scalability: 10
          feasibility: 4
          rank: 3
    
    - dimension: "API Throttling"
      approaches:
        - name: "Token Bucket"
          complexity: 2
          performance: 10
          cost: 9
          scalability: 9
          feasibility: 10
          rank: 1
        
        - name: "Leaky Bucket"
          complexity: 4
          performance: 7
          cost: 9
          scalability: 7
          feasibility: 9
          rank: 2
        
        - name: "Sliding Window Log"
          complexity: 7
          performance: 10
          cost: 6
          scalability: 10
          feasibility: 6
          rank: 3
    
    - dimension: "Project Structure"
      approaches:
        - name: "Monolithic"
          complexity: 1
          performance: 5
          cost: 10
          scalability: 2
          feasibility: 10
          rank: 3
        
        - name: "Microservices"
          complexity: 9
          performance: 8
          cost: 6
          scalability: 10
          feasibility: 4
          rank: 2
        
        - name: "Modular Monolith"
          complexity: 5
          performance: 7
          cost: 8
          scalability: 8
          feasibility: 8
          rank: 1

recommendation:
  best_fit: "Sharding + Read Replicas (DB) + Token Bucket (Throttling) + Modular Monolith (Structure)"
  rationale:
    - "Sharding is proven at scale and meets performance targets"
    - "Token Bucket is simple, high-performance, low-cost"
    - "Modular Monolith allows team parallelization without operational burden"
  
  phased_adoption:
    - phase: "Phase 1: Analysis & Design (Week 1)"
      tasks:
        - "Define shard key and number of shards"
        - "Design read replica topology"
        - "Create migration plan"
      effort: "1 week"
    
    - phase: "Phase 2: Sharding Implementation (Weeks 2-4)"
      tasks:
        - "Implement shard routing layer"
        - "Create sharded schema"
        - "Migrate data to shards"
      effort: "3 weeks"
    
    - phase: "Phase 3: Throttling & Testing (Week 5)"
      tasks:
        - "Implement token bucket throttling"
        - "Load testing (verify p99 < 100ms at 10M scale)"
        - "Rollout to production (canary, then full)"
      effort: "1 week"
  
  total_effort: "5 weeks"
  total_cost: "$20k (infrastructure) + $40k (engineering at $100k/yr for 2 engineers)"
  risks:
    - "Data migration window may impact availability—use log-based CDC"
    - "Shard rebalancing is complex—build dedicated tooling"
    - "Hot spot management required (monitor per-shard latencies)"
```

## Usage Example

**Input to module:**
```
problem: "Database queries slow, p99=5s. Need 10M users."
current_design: "Monolithic PostgreSQL, single master, 3 read replicas"
constraints:
  performance: "p99 < 100ms"
  budget: "$50k infra"
  team_skills: ["Java", "PostgreSQL", "AWS"]
  timeline: "4 weeks"
dimensions: ["database_design", "api_throttling", "project_structure"]
```

**Output from module:**
- solutions.md (detailed approaches per dimension)
- recommendation.md (best-fit + phased roadmap)
- comparison-table.csv (trade-off matrix, exportable)
- implementation-roadmap.json (tasks, timeline, effort)

## Notes
- Approaches should be concrete (not theoretical)
- Performance metrics should be before/after
- Cost should include both infrastructure and engineering
- Scalability ceiling should be realistic for team
- Phased roadmap should not exceed 4 weeks per phase
```

- [ ] **Step 2: Verify design_solver.md is complete**

Check:
- ✓ 4 phases documented (Diagnosis, Solution Generation, Trade-Off, Recommendation)
- ✓ Multiple solution dimensions covered (DB, API, structure)
- ✓ Each approach has: complexity, performance, cost, scalability, effort
- ✓ Trade-off matrix is concrete with numeric rankings
- ✓ Recommendation includes phased roadmap
- ✓ Example input/output shows realistic scenario

- [ ] **Step 3: Commit design_solver module**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
git add agents/orchestrator/modules/design_solver.md
git commit -m "feat: add design_solver reusable module"
```

- [ ] **Step 4: Add test for design_solver to test_orchestrator_modules.py**

Add to `tests/test_orchestrator_modules.py`:

```python
def test_design_solver_structure():
    """Test design_solver module has all required phases and dimensions."""
    with open('agents/orchestrator/modules/design_solver.md', 'r') as f:
        content = f.read()
    
    # Verify required phases
    phases = [
        "### Phase 1: Diagnosis",
        "### Phase 2: Solution Generation",
        "### Phase 3: Trade-Off Analysis",
        "### Phase 4: Recommendation"
    ]
    
    for phase in phases:
        assert phase in content, f"Missing phase: {phase}"
    
    # Verify solution dimensions
    dimensions = [
        "database_design",
        "api_throttling",
        "project_structure"
    ]
    
    for dimension in dimensions:
        assert dimension in content, f"Missing dimension: {dimension}"

if __name__ == '__main__':
    test_expert_panel_generator_structure()
    test_ideation_engine_structure()
    test_design_solver_structure()
    print("✓ All module structure tests passed")
```

Run test:
```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
python tests/test_orchestrator_modules.py
```

Expected output: `✓ All module structure tests passed`

- [ ] **Step 5: Commit all updated tests**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
git add tests/test_orchestrator_modules.py
git commit -m "test: add design_solver structure validation tests"
```

---

## Phase 2: Create Orchestrator Functions (Sequential Tasks 4-5)

### Task 4: Create `orchestrator:ideate` Function

**Files:**
- Create: `agents/orchestrator/functions/ideate.md`

- [ ] **Step 1: Write orchestrator:ideate function**

```markdown
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
```

- [ ] **Step 2: Verify ideate.md is complete**

Check:
- ✓ Purpose is clear
- ✓ Input spec matches design (idea, constraints, mode)
- ✓ Process references ideation_engine and expert_panel_generator
- ✓ Output is specific (idea-spec.md, project-plan.json, raid-analysis.md, CSV)
- ✓ Success criteria are measurable
- ✓ Example shows realistic usage

- [ ] **Step 3: Commit ideate function**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
git add agents/orchestrator/functions/ideate.md
git commit -m "feat: add orchestrator:ideate function"
```

- [ ] **Step 4: Write failing test for orchestrator:ideate**

Add to `tests/test_orchestrator_functions.py` (create new file):

```python
import json
import sys
sys.path.insert(0, '/Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts')

def test_ideate_function_invokes_modules():
    """Test orchestrator:ideate references required modules."""
    with open('agents/orchestrator/functions/ideate.md', 'r') as f:
        content = f.read()
    
    # Verify function signature
    assert "# Function: orchestrator:ideate" in content
    assert "**Prefix:** `orchestrator:ideate`" in content
    
    # Verify it invokes required modules
    assert "ideation_engine" in content
    assert "expert_panel_generator" in content
    
    # Verify input spec is present
    assert "## Input Specification" in content
    assert "idea: string" in content
    
    # Verify output spec is present
    assert "## Output" in content
    assert "idea-spec.md" in content
    assert "project-plan.json" in content
    assert "raid-analysis.md" in content
    assert "project-plan.csv" in content

if __name__ == '__main__':
    test_ideate_function_invokes_modules()
    print("✓ orchestrator:ideate function structure test passed")
```

Run test:
```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
python tests/test_orchestrator_functions.py
```

Expected output: `✓ orchestrator:ideate function structure test passed`

- [ ] **Step 5: Commit test**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
git add tests/test_orchestrator_functions.py
git commit -m "test: add orchestrator:ideate function validation tests"
```

---

### Task 5: Create `orchestrator:solve` Function

**Files:**
- Create: `agents/orchestrator/functions/solve.md`

- [ ] **Step 1: Write orchestrator:solve function**

```markdown
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
```

- [ ] **Step 2: Verify solve.md is complete**

Check:
- ✓ Purpose is clear (solve design bottlenecks)
- ✓ Input spec matches design (problem, constraints, dimensions)
- ✓ Process references design_solver and expert_panel_generator
- ✓ Output is specific (solutions.md, recommendation.md, comparison-table.csv, roadmap.json)
- ✓ Success criteria are measurable
- ✓ Example shows realistic usage with all inputs

- [ ] **Step 3: Commit solve function**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
git add agents/orchestrator/functions/solve.md
git commit -m "feat: add orchestrator:solve function"
```

- [ ] **Step 4: Add test for orchestrator:solve to test_orchestrator_functions.py**

Add to `tests/test_orchestrator_functions.py`:

```python
def test_solve_function_invokes_modules():
    """Test orchestrator:solve references required modules."""
    with open('agents/orchestrator/functions/solve.md', 'r') as f:
        content = f.read()
    
    # Verify function signature
    assert "# Function: orchestrator:solve" in content
    assert "**Prefix:** `orchestrator:solve`" in content
    
    # Verify it invokes required modules
    assert "design_solver" in content
    assert "expert_panel_generator" in content
    
    # Verify input spec is present
    assert "## Input Specification" in content
    assert "problem: string" in content
    assert "dimensions: string[]" in content
    
    # Verify output spec is present
    assert "## Output" in content
    assert "solutions.md" in content
    assert "recommendation.md" in content
    assert "comparison-table.csv" in content
    assert "implementation-roadmap.json" in content

if __name__ == '__main__':
    test_ideate_function_invokes_modules()
    test_solve_function_invokes_modules()
    print("✓ All orchestrator functions passed structure tests")
```

Run test:
```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
python tests/test_orchestrator_functions.py
```

Expected output: `✓ All orchestrator functions passed structure tests`

- [ ] **Step 5: Commit test**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
git add tests/test_orchestrator_functions.py
git commit -m "test: add orchestrator:solve function validation tests"
```

---

## Phase 3: Update Documentation (Task 6)

### Task 6: Update AGENTS_FUNCTIONS.md

**Files:**
- Modify: `AGENTS_FUNCTIONS.md`

- [ ] **Step 1: Read current AGENTS_FUNCTIONS.md**

Note current structure (should have orchestrator section with functions: plan, build, context, pr, review, tradeoff, risk).

- [ ] **Step 2: Update ORCHESTRATOR AGENT section**

Find the section `# ORCHESTRATOR AGENT (7 functions)` and update to:

```markdown
# ORCHESTRATOR AGENT (9 functions)

**Prefix:** `orchestrator`

### orchestrator:ideate
Transform vague ideas into validated project plans with expert feedback. Uses ideation_engine module for systematic refinement, expert_panel_generator for domain-specific challenges. Outputs: idea-spec.md, project-plan.json, raid-analysis.md, project-plan.csv.

### orchestrator:solve
Solve design bottlenecks with multi-dimensional, prescriptive solutions. Uses design_solver module for diagnosis and trade-off analysis, expert_panel_generator for architecture challenges. Generates: solutions.md, recommendation.md, comparison-table.csv, implementation-roadmap.json.

### orchestrator:plan
Parse requirements in 5 formats, break into tasks. Outputs: requirements.md, task-breakdown.json, execution-order.txt

### orchestrator:build
Full-stack generation (architect → implementer → quality end-to-end). Outputs: complete system artifacts.

### orchestrator:context
Build project context (architecture.md, tech-stack.md, context.json, design.html visualization).

### orchestrator:pr
Package deliverables and create GitHub PR with comprehensive description.

### orchestrator:review
Strategic architecture review with challenge questions and 5-year assessment.

### orchestrator:tradeoff
Generate 3-option complexity analysis with ranked recommendation.

### orchestrator:risk
Risk assessment (operational, data, scaling, team, integration) with mitigation strategies.
```

- [ ] **Step 3: Update Quick Function Index table**

Update the table row for Orchestrator:

```markdown
| **Orchestrator** | `orchestrator` | ideate, solve, plan, build, review, tradeoff, risk, context, pr | Start new project, refine vague ideas, solve bottlenecks, or generate full-stack system |
```

- [ ] **Step 4: Update Linear Execution Pipeline**

Update the pipeline to show ideate and solve as optional insertion points:

```
Requirement
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

- [ ] **Step 5: Verify changes**

Check:
- ✓ Orchestrator function count updated to 9
- ✓ Both ideate and solve are documented with clear input/output
- ✓ Quick index table is updated
- ✓ Pipeline shows ideate and solve as optional
- ✓ No other sections altered

- [ ] **Step 6: Commit AGENTS_FUNCTIONS.md**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
git add AGENTS_FUNCTIONS.md
git commit -m "docs: add orchestrator:ideate and orchestrator:solve to function reference"
```

---

## Phase 4: Testing & Validation (Task 7)

### Task 7: Run All Tests

**Files:**
- Test: `tests/test_orchestrator_modules.py`
- Test: `tests/test_orchestrator_functions.py`

- [ ] **Step 1: Run all module tests**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
python tests/test_orchestrator_modules.py -v
```

Expected output:
```
✓ expert_panel_generator module structure test passed
✓ ideation_engine module structure test passed
✓ design_solver module structure test passed
✓ All module structure tests passed
```

- [ ] **Step 2: Run all function tests**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
python tests/test_orchestrator_functions.py -v
```

Expected output:
```
✓ orchestrator:ideate function structure test passed
✓ orchestrator:solve function structure test passed
✓ All orchestrator functions passed structure tests
```

- [ ] **Step 3: Verify file structure**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
find agents/orchestrator -type f -name "*.md" | sort
```

Expected output:
```
agents/orchestrator/functions/ideate.md
agents/orchestrator/functions/solve.md
agents/orchestrator/modules/design_solver.md
agents/orchestrator/modules/expert_panel_generator.md
agents/orchestrator/modules/ideation_engine.md
```

- [ ] **Step 4: Verify git history**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
git log --oneline | head -10
```

Expected output (should see all commits from this plan):
```
[commit hash] docs: add orchestrator:ideate and orchestrator:solve to function reference
[commit hash] test: add orchestrator:solve function validation tests
[commit hash] test: add orchestrator:ideate function validation tests
[commit hash] feat: add orchestrator:solve function
[commit hash] feat: add orchestrator:ideate function
[commit hash] test: add design_solver structure validation tests
[commit hash] feat: add design_solver reusable module
[commit hash] test: add ideation_engine structure validation tests
[commit hash] feat: add ideation_engine reusable module
[commit hash] feat: add expert_panel_generator reusable module
```

- [ ] **Step 5: Create test summary document**

Create `tests/ORCHESTRATOR_TESTS_SUMMARY.md`:

```markdown
# Orchestrator Module & Function Tests Summary

**Date:** 2026-06-04  
**Status:** All tests passing ✓

## Module Tests

| Module | Tests | Status |
|--------|-------|--------|
| expert_panel_generator | Structure validation | ✓ PASS |
| ideation_engine | Structure validation | ✓ PASS |
| design_solver | Structure validation | ✓ PASS |

## Function Tests

| Function | Tests | Status |
|----------|-------|--------|
| orchestrator:ideate | Module invocation + input/output spec | ✓ PASS |
| orchestrator:solve | Module invocation + input/output spec | ✓ PASS |

## Coverage

- ✓ All 3 modules have structure validation
- ✓ Both functions verify module invocation
- ✓ Input/output specs verified for both functions
- ✓ File creation verified

## Test Execution

```bash
python tests/test_orchestrator_modules.py
python tests/test_orchestrator_functions.py
```

Both return "✓ All tests passed"

## Next Steps

- Integration testing (invoke functions with sample inputs)
- Export testing (verify 8-platform exportability)
- User acceptance testing (validate outputs are useful)
```

- [ ] **Step 6: Commit test summary**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
git add tests/ORCHESTRATOR_TESTS_SUMMARY.md
git commit -m "test: add orchestrator module and function test summary"
```

---

## Phase 5: Export & Documentation (Task 8)

### Task 8: Update Exporter for New Modules

**Files:**
- Modify: `tools/exporter.py` (add orchestrator modules to export list)

- [ ] **Step 1: Read current exporter.py**

Check the file structure and identify where modules are registered.

- [ ] **Step 2: Add orchestrator modules to exporter**

Find the section where skills/modules are registered and add:

```python
# In the orchestrator modules section (create if doesn't exist):
orchestrator_modules = [
    {
        "name": "expert_panel_generator",
        "path": "agents/orchestrator/modules/expert_panel_generator.md",
        "type": "module",
        "agent": "orchestrator"
    },
    {
        "name": "ideation_engine",
        "path": "agents/orchestrator/modules/ideation_engine.md",
        "type": "module",
        "agent": "orchestrator"
    },
    {
        "name": "design_solver",
        "path": "agents/orchestrator/modules/design_solver.md",
        "type": "module",
        "agent": "orchestrator"
    }
]

# In the orchestrator functions section (update existing):
orchestrator_functions = [
    {
        "name": "ideate",
        "path": "agents/orchestrator/functions/ideate.md",
        "type": "function",
        "agent": "orchestrator"
    },
    {
        "name": "solve",
        "path": "agents/orchestrator/functions/solve.md",
        "type": "function",
        "agent": "orchestrator"
    },
    # ... existing functions (plan, build, etc.)
]
```

- [ ] **Step 3: Test exporter list command**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
python tools/exporter.py --list | grep orchestrator
```

Expected output (should show ideate, solve, and 3 modules):
```
orchestrator:ideate
orchestrator:solve
orchestrator:expert_panel_generator
orchestrator:ideation_engine
orchestrator:design_solver
... (existing functions)
```

- [ ] **Step 4: Test dry-run export**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
python tools/exporter.py --target claude --dry-run 2>&1 | grep orchestrator | head -10
```

Expected: Files that would be exported (no actual export)

- [ ] **Step 5: Commit exporter updates**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
git add tools/exporter.py
git commit -m "feat: add orchestrator modules and functions to exporter"
```

---

## Phase 6: Documentation & Final Review (Task 9)

### Task 9: Create README for New Functions

**Files:**
- Create: `agents/orchestrator/README.md`

- [ ] **Step 1: Write README for orchestrator functions and modules**

```markdown
# Orchestrator Agent

The orchestrator agent handles **strategic planning and execution coordination** across the development lifecycle.

## Functions (9 Total)

### Idea Refinement & Problem-Solving

- **[orchestrator:ideate](./functions/ideate.md)** — Transform vague ideas into validated project plans
  - Uses: ideation_engine, expert_panel_generator
  - Input: Raw concept + constraints
  - Output: idea-spec.md, project-plan.json, raid-analysis.md, CSV export
  
- **[orchestrator:solve](./functions/solve.md)** — Solve design bottlenecks with multi-dimensional solutions
  - Uses: design_solver, expert_panel_generator
  - Input: Problem statement + constraints + dimensions
  - Output: solutions.md, recommendation.md, comparison-table.csv, roadmap.json

### Planning & Execution

- **[orchestrator:plan](./functions/plan.md)** — Parse requirements, break into tasks
- **[orchestrator:build](./functions/build.md)** — Full-stack generation (end-to-end)
- **[orchestrator:context](./functions/context.md)** — Build project context (architecture, tech stack)
- **[orchestrator:pr](./functions/pr.md)** — Package deliverables, create GitHub PR

### Review & Risk Analysis

- **[orchestrator:review](./functions/review.md)** — Strategic architecture review with challenges
- **[orchestrator:tradeoff](./functions/tradeoff.md)** — Generate 3-option complexity analysis
- **[orchestrator:risk](./functions/risk.md)** — Risk assessment with mitigation strategies

## Reusable Modules (3 Total)

Modules are composed by functions to avoid duplication and enable future extensions.

- **[expert_panel_generator](./modules/expert_panel_generator.md)** — Create virtual domain experts for feedback
  - Used by: orchestrator:ideate (phase 2), orchestrator:solve (phase 4)
  - Generates: 3-5 diverse experts, targeted challenges, feedback synthesis

- **[ideation_engine](./modules/ideation_engine.md)** — Systematically refine ideas → project plans
  - Used by: orchestrator:ideate
  - Generates: clarification questions, concept refinement, milestones, tasks, RAID analysis

- **[design_solver](./modules/design_solver.md)** — Solve bottlenecks with multi-dimensional solutions
  - Used by: orchestrator:solve
  - Generates: diagnosis, solution approaches, trade-off analysis, recommendations

## Usage Patterns

### Pattern 1: Idea Refinement (Green-field)

```
orchestrator:ideate (idea + constraints)
    ↓
orchestrator:plan (parse ideation output)
    ↓
architect:design
    ↓
implementer:full
```

### Pattern 2: Bottleneck Solving (Brown-field)

```
architect:design (current system)
    ↓
orchestrator:solve (problem + constraints)
    ↓
implementer:full (implement best-fit solution)
```

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

## When to Use Each Function

| Scenario | Function | Input | Output |
|----------|----------|-------|--------|
| "I have a vague idea" | `orchestrator:ideate` | Concept | Validated spec + project plan |
| "I have requirements" | `orchestrator:plan` | Requirement doc | Task breakdown |
| "Database is slow" | `orchestrator:solve` | Problem + constraints | Solution options + recommendation |
| "Design the system" | `architect:design` | Tasks | System topology + API + schema |
| "Build everything" | `orchestrator:build` | None | Full-stack implementation |

## Module Dependencies

```
orchestrator:ideate
    └─ ideation_engine
    └─ expert_panel_generator

orchestrator:solve
    └─ design_solver
    └─ expert_panel_generator

expert_panel_generator (reusable)
    ↑ used by ideate, solve, and future review functions
```

## File Structure

```
agents/orchestrator/
├── README.md                 ← You are here
├── functions/
│   ├── ideate.md            ← NEW
│   ├── solve.md             ← NEW
│   ├── plan.md
│   ├── build.md
│   ├── context.md
│   ├── pr.md
│   ├── review.md
│   ├── tradeoff.md
│   └── risk.md
└── modules/
    ├── expert_panel_generator.md    ← NEW
    ├── ideation_engine.md           ← NEW
    └── design_solver.md             ← NEW
```

## Testing

Run tests:
```bash
python tests/test_orchestrator_modules.py
python tests/test_orchestrator_functions.py
```

All tests should pass ✓

## Version History

- **v3.1** (2026-06-04) — Add `orchestrator:ideate` and `orchestrator:solve` functions + 3 reusable modules
- **v3.0** — Initial 5-agent architecture (orchestrator, architect, implementer, quality, business_analyst)
```

- [ ] **Step 2: Verify README is complete**

Check:
- ✓ All 9 functions documented
- ✓ All 3 modules documented
- ✓ Usage patterns shown
- ✓ Module dependencies clear
- ✓ File structure matches actual files
- ✓ When-to-use table is helpful

- [ ] **Step 3: Commit README**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
git add agents/orchestrator/README.md
git commit -m "docs: add orchestrator agent README with function and module index"
```

- [ ] **Step 4: Verify all files exist**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
ls -la agents/orchestrator/functions/
ls -la agents/orchestrator/modules/
```

Expected: All files from plan exist

- [ ] **Step 5: Final commit verification**

```bash
cd /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts
git log --oneline --grep="orchestrator\|ideate\|solve" | wc -l
```

Expected: At least 12 commits related to orchestrator changes

---

## Self-Review Against Spec

**Spec Coverage Checklist:**

- ✓ **`orchestrator:ideate` function** — Created with ideation_engine + expert_panel_generator (Task 4)
- ✓ **`orchestrator:solve` function** — Created with design_solver + expert_panel_generator (Task 5)
- ✓ **`ideation_engine` module** — Created with 3 phases (Task 2)
- ✓ **`design_solver` module** — Created with 4 phases (Task 3)
- ✓ **`expert_panel_generator` module** — Created with 3 phases (Task 1)
- ✓ **AGENTS_FUNCTIONS.md updated** — Both functions documented (Task 6)
- ✓ **Tests written** — Modules + functions validated (Task 7)
- ✓ **Exporter updated** — New modules exported to 8 platforms (Task 8)
- ✓ **Documentation** — README created (Task 9)

**Placeholder Check:**
- ✓ No "TBD", "TODO", or "implement later" in any module or function
- ✓ All code examples are concrete
- ✓ All input/output specs are specific

**Type Consistency:**
- ✓ Modules referenced consistently across functions
- ✓ Output formats (YAML, JSON, CSV, markdown) consistent
- ✓ Phase naming consistent (Phase 1, 2, 3, etc.)

**Spec Requirements Not Yet Covered:**
- Full integration testing (invoking with sample data) — defer to execution phase
- Platform export verification (actual exports to 8 platforms) — defer to execution phase
- User acceptance testing (validate output usefulness) — defer to execution phase

---

## Summary

**Deliverables Completed:**
1. ✓ 3 reusable prompt modules (expert_panel_generator, ideation_engine, design_solver)
2. ✓ 2 orchestrator functions (ideate, solve)
3. ✓ AGENTS_FUNCTIONS.md updated
4. ✓ Exporter updated for new modules
5. ✓ Unit tests for all modules and functions
6. ✓ README with comprehensive documentation

**Total Commits:** 12+

**Total Tasks:** 9 (sequential, no parallelization needed—modules → functions → tests → docs)

**Estimated Timeline:** 5 working days

**Next Phase:** Integration testing + user acceptance testing + platform export verification
