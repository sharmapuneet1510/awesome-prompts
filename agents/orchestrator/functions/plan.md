---
name: orchestrator:plan Function
version: 1.0
description: "Requirement parsing + task breakdown + strategic planning"
prefix: orchestrator:plan
---

# orchestrator:plan

**Input:** requirement.txt + project context

**Output:** 
- requirement.md (structured spec)
- tasks/01-05/spec.md (task specifications)
- strategic plan document

**Steps:**
1. Parse requirement.txt into structured requirement.md
2. Ask clarifying questions if ambiguous
3. Detect project type (new/existing) — a new project without approved
   `docs/project-setup/` runs `skills/project_setup_skill.md` first
4. Break into 5-7 concrete tasks
5. Define acceptance criteria per task
6. Map tasks to skills
7. Estimate scope + dependencies
8. Output strategic plan
