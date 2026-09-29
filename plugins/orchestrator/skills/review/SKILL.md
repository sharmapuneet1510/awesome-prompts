---
name: review
description: Architecture review + design validation + gap analysis
disable-model-invocation: true
---

Role and rules: read ${CLAUDE_PLUGIN_ROOT}/reference/agent.md and ${CLAUDE_PLUGIN_ROOT}/reference/rules.md for the sections this function needs.

# orchestrator:review

**Input:** Architecture plan + design decisions

**Output:**
- Architecture review document
- Gap analysis
- Assumptions validated/challenged
- Recommendation (proceed or revise)

**Steps:**
1. Understand problem definition
2. Validate scope + constraints
3. Challenge technology choices
4. Challenge architectural patterns
5. Challenge optimization assumptions
6. Identify gaps (security, monitoring, scalability)
7. Flag risks for Phase 5 (risk assessment)
8. Output review document
