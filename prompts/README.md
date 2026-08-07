# 📋 Prompts Directory

> Reusable, copy-paste-ready prompt templates organized by category. 11 categories, 19 prompts.

Prompts complement `skills/` and `agents/`: a skill defines *how* to do something (reusable methodology), an agent *dispatches* work, a prompt is a ready-to-use template for a specific task.

## Quick Navigation

| Category | Purpose | Files | Skills Referenced |
|---|---|---|---|
| [Email](email/) | Email composition, review, professional communication | 3 | — |
| [Code Review](code-review/) | Conversational and MCP-enabled code review sessions | 1 | `code_review_skill.md` |
| [Testing](testing/) | Unit/integration/E2E test generation | 1 | `test_skill.md` |
| [Codebase Analysis](codebase-analysis/) | Architecture mapping, field tracing, regulatory auditing | 3 | `context_builder_skill.md` |
| [Project Management](project-management/) | User stories, workflow mapping, JIRA reading | 3 | — |
| [Incident Management](incident-management/) | Production issue investigation protocol | 1 | `error_handling_skill.md`, `logger_skill.md` |
| [Reporting](reporting/) | HTML report and dashboard generation | 1 | — |
| [Implementation Guides](implementation-guides/) | Full-stack, step-by-step build guides | 1 | Multiple (see guide) |
| [Spec-Driven Development](spec-driven-development/) | Requirements drafting for the RULE 11 gate | 1 | `spec_driven_development_skill.md` |
| [DevOps & SRE](devops-sre/) | Incident runbooks, release/platform engineering | 1 | `error_handling_skill.md`, `opentelemetry_skill.md` |
| [Meta-Prompt Engineering](meta-prompt-engineering/) | Prompt self-critique and authoring guidance | 1 | `agent_skill_design_skill.md` |
| [Technical Writing](technical-writing/) | Plain-language technical documentation rewriting | 1 | `code_documentation_skill.md` |

## How to Use Prompts

### Step 1: Export Skills and Agents
```bash
python tools/exporter.py
```
This generates platform-native instruction files for Claude Code, Copilot, Cursor, Windsurf, Gemini, Continue, OpenAI, and Aider — including `prompts/` as of this version.

### Step 2: Pick a Prompt
Match the task to a category above, then open the specific file for the template.

### Step 3: Reference the Linked Skills
Each prompt lists the skills it depends on under "Skills Referenced" — mention those skill files explicitly when dispatching to an agent so it has full pattern context.

### Step 4: Follow the Template
Every prompt follows the same shape: Context → Requirements → Approach → Skills Referenced → Expected Output → Success Criteria.

## Adding a New Prompt

1. Create the file at `prompts/<category>/<PromptName>.md` (new category: create the directory and add a row to the table above).
2. Follow the standard template shape (see Step 4 above).
3. Reference concrete skills from `skills/`, not vague "best practices."
4. State success criteria that are checkable from the output alone.

## History

Categories `email/`, `code-review/`, `testing/`, `codebase-analysis/`, `project-management/`, `incident-management/`, `reporting/`, and `implementation-guides/` were restored from `.deprecated/old-prompts/` — an earlier repository reorganization moved them there while `CLAUDE.md` continued documenting `prompts/` as a live top-level directory. That drift is now resolved; `prompts/` is live again.

Categories `spec-driven-development/`, `devops-sre/`, `meta-prompt-engineering/`, and `technical-writing/` were added new, with content inspired by (not copied from) [ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts) — see `../CREDITS.md`.

## References

- **Main Repo**: [README.md](../README.md)
- **Skills**: [skills/](../skills/)
- **Instructions**: [instructions/](../instructions/)
- **Agents**: [agents/](../agents/)
- **Credits**: [CREDITS.md](../CREDITS.md)
