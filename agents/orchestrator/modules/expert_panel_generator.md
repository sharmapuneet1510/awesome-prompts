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
