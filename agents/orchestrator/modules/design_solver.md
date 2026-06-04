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
      architecture: "Separate read/write models. Writes → Kafka → Event processors → Read store (Elasticsearch). Reads hit Elasticsearch. Strong consistency via versioning."
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
