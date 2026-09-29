---
name: orchestrator:tradeoff Function
version: 1.0
description: "Complexity vs. simplicity analysis + 3-option comparison"
prefix: orchestrator:tradeoff
---

# orchestrator:tradeoff

**Input:** Proposed architecture + constraints

**Output:**
- 3-option analysis (simple/moderate/advanced)
- Explicit tradeoff dimensions
- Recommendation with rationale

**Steps:**
1. Identify key decision (DB choice, pattern, tech stack)
2. Define Option A (simple approach)
   - ✓ Benefits, ✗ limitations
   - Effort estimate
   - Team skill required
   - Scalability ceiling
3. Define Option B (moderate approach)
   - ✓ Benefits, ✗ limitations
   - Effort estimate
   - Team skill required
   - Scalability ceiling
4. Define Option C (advanced approach)
   - ✓ Benefits, ✗ limitations
   - Effort estimate
   - Team skill required
   - Scalability ceiling
5. Analyze tradeoff dimensions for each
6. Recommend pragmatically
7. Provide contingency (when to move to next option)
