# Prompts — AI-Powered Development Templates

Reusable prompt templates organized by category for code generation, review, testing, and system design.

## Categories

### 📧 Email
Email writing, review, and communication templates.
- Email composition prompts
- Email review and feedback
- Professional communication templates

**Use Case:** Generate and review email communications

---

### 🔍 Code Review
Code review agent prompts and checklists.
- Conversational code review
- MCP-enabled review sessions
- Pattern and design analysis
- Security review prompts

**Use Case:** Systematically review code for quality, patterns, and security

---

### 🧪 Testing
Test case generation and testing strategy prompts.
- Unit test generation (JUnit5, pytest, Jest)
- Integration test templates
- E2E test scenarios
- Test coverage analysis

**Use Case:** Generate comprehensive test suites for new code

---

### 📊 Codebase Analysis
Deep code analysis, tracing, and auditing prompts.
- Codebase cartography (architecture mapping)
- Field tracing analysis (data flow tracking)
- Regulatory compliance auditing
- Module dependency analysis

**Use Case:** Understand complex codebases and data flows

---

### 📋 Project Management
User story generation, workflow mapping, and Jira integration prompts.
- User story generation (from requirements)
- Workflow state mapping
- Task breakdown and estimation
- Jira issue reader

**Use Case:** Structure and track development work

---

### 🚨 Incident Management
Production issue investigation and debugging prompts.
- Production issue investigation protocol
- Error log analysis
- Root cause analysis
- Impact assessment

**Use Case:** Systematically investigate and resolve production issues

---

### 📈 Reporting
HTML report generation and presentation prompts.
- Performance report generation
- Code quality dashboards
- Security assessment reports
- Executive summaries

**Use Case:** Generate professional reports from analysis data

---

### 🚀 Implementation Guides
Complete, step-by-step guides for building production applications.
- Full-stack application architecture
- Integration patterns
- Deployment strategies
- Best practices across the stack

**Skills Referenced:** Multiple skills from `skills/` directory

**Available Guides:**
- **react-sso-fullstack.md** — React 18+ with OAuth2/OIDC SSO
  - Spring Boot or FastAPI backend
  - TanStack Query + Zustand frontend
  - JWT token management
  - Distributed tracing with OpenTelemetry
  - Full testing and security checklist

**Use Case:** Build complete applications following all best practices

---

## How to Use Prompts

### Step 1: Export Skills
First, export the awesome-prompts skills to your AI tool:

```bash
cd awesome-prompts
python3 tools/skill_exporter.py
```

This generates instruction files for:
- GitHub Copilot (`.github/copilot-instructions.md`)
- Claude Code (`.claude/skills_context.md`)
- Cursor IDE (`.cursorrules`)
- Continue.dev (`.continue/config.json`)
- OpenAI API (`.openai/system_prompt.txt`)

### Step 2: Choose a Prompt
Select a prompt file that matches your task:

```
Task: Generate unit tests
→ prompts/testing/test_generation.md

Task: Review code architecture
→ prompts/code-review/architectural_review.md

Task: Investigate production error
→ prompts/incident-management/investigation_protocol.md

Task: Build React app with SSO
→ prompts/implementation-guides/react-sso-fullstack.md
```

### Step 3: Reference Skills
When using prompts, reference the corresponding skills from `skills/`:

```markdown
Using skills from awesome-prompts repo (react_advanced_skill,
rest_api_java_skill, error_handling_skill), implement...
```

The exported instructions include all skill details, so your AI tool will have
full context for the implementation.

### Step 4: Follow Implementation Steps
Each prompt includes:
- Context and requirements
- Tech stack recommendations
- Project structure
- Implementation phases
- Success criteria
- Code examples and patterns

---

## Quick Reference

| Task | Prompt | Skills |
|------|--------|--------|
| Generate unit tests | `testing/test_generation.md` | testing_junit5_skill, testing_pytest_skill |
| Review code quality | `code-review/quality_review.md` | code_health_skill, sonarqube_vulnerability_skill |
| Investigate bug | `incident-management/investigation.md` | error_handling_skill, logger_skill |
| Design REST API | `project-management/api_design.md` | rest_api_java_skill, documentation_skill |
| Build full-stack app | `implementation-guides/react-sso-fullstack.md` | 8 skills (see guide) |

---

## Tips

1. **Export skills first** — Skills contain all patterns and examples
2. **Reference specific skills** — Mention skill files in your prompt
3. **Follow recommended tech stack** — Ensure compatibility across skills
4. **Use success criteria** — Validate your implementation matches requirements
5. **Check examples** — Each skill has 200+ code examples
6. **Team alignment** — All skills follow master_instruction_set rules

---

## Adding New Prompts

To add a new prompt:

1. Create file in appropriate category:
   ```
   prompts/[category]/[prompt-name].md
   ```

2. Use standard template:
   ```markdown
   # Prompt Title

   ## Context
   Explain the scenario

   ## Requirements
   List key requirements

   ## Approach
   Outline the strategy

   ## Skills Referenced
   - skill_name.md (description)

   ## Expected Output
   What the AI should produce

   ## Success Criteria
   How to validate results
   ```

3. Reference awesome-prompts skills
4. Include code examples
5. Test the prompt with Claude/Copilot

---

## References

- **Main Repo**: [README.md](../README.md)
- **Skills**: [skills/](../skills/)
- **Instructions**: [instructions/](../instructions/)
- **Agents**: [agents/](../agents/)

---

**Status:** Production Ready | **Last Updated:** 2026-04-03 | **Total Prompts:** 15+
