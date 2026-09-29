---
name: risk
description: Risk assessment + failure modes + mitigation strategies
disable-model-invocation: true
---

Role and rules: read ${CLAUDE_PLUGIN_ROOT}/reference/agent.md and ${CLAUDE_PLUGIN_ROOT}/reference/rules.md for the sections this function needs.

# orchestrator:risk

**Input:** Proposed architecture + deployment plan

**Output:**
- Risk assessment matrix
- Risk categories (operational, data, scaling, team, integration)
- Mitigations per risk
- Monitoring + observability plan

**Steps:**
1. Identify operational risks (component failures, rollback)
2. Identify data risks (loss, corruption, recovery)
3. Identify scaling risks (bottlenecks at 10x, 100x)
4. Identify team risks (knowledge concentration, hiring)
5. Identify integration risks (tight coupling, versioning)
6. For each risk:
   - Estimate probability (low/medium/high)
   - Estimate impact (low/medium/high/critical)
   - Define mitigations (2-3 per risk)
   - Assign owner
7. Create risk matrix (priority ranking)
8. Define monitoring/observability for each risk
9. Create contingency plans (detection + immediate response + mitigation + postmortem)
