---
name: orchestrator:context Function
version: 1.0
description: "Build project context + architecture + knowledge graph"
prefix: orchestrator:context
---

# orchestrator:context

**Input:** requirement.md + project codebase (if existing)

**Output:**
- architecture.md (Mermaid diagrams + narrative)
- context.json (machine-readable metadata)
- design.html (interactive visualization)
- graph.json (knowledge graph via graphify)

**Steps:**
1. Scan project structure (if existing)
2. Identify tech stack
3. Map modules + components
4. Generate Mermaid diagrams (architecture, data flow)
5. Create context.json with all metadata
6. Generate design.html with D3 visualization
7. Run graphify for knowledge graph + embeddings
8. Cache embeddings for intelligent retrieval
