---
name: Agent Skill Design Skill
version: 1.0
description: >
  Meta-guidance for authoring new skills in this repo's own skill-based
  architecture — when a skill is warranted, how to scope it, and how to keep
  it independently useful.
applies_to: [meta, skill-authoring, agents]
tags: [meta, skill-design, agent-architecture]
---

# Agent Skill Design Skill — v1.0

## 1. When a New Skill Is Warranted

Add a skill when there's a recurring pattern an agent needs to apply consistently across many tasks — not for a one-off. Ask:
- Will this guidance be reused across multiple, unrelated features/projects? (If it's specific to one feature, it belongs in that feature's plan/spec, not a skill.)
- Does it define *how* to do something (patterns, checklists, conventions), not *what* to build? Skills are reusable methodology; specs are per-feature requirements.
- Is there already a skill that covers this? Check `skills/README.md`'s index before creating a near-duplicate.

## 2. Scoping a Skill

- **One skill, one responsibility.** `error_handling_skill.md` covers error handling; it doesn't also cover logging conventions (that's `logger_skill.md`). If a skill's checklist starts covering two unrelated concerns, split it.
- **Language-agnostic where possible.** Prefer skills that state the principle once and show multiple language examples, over language-specific skills, unless the guidance is genuinely language-specific (e.g., `lombok_skill.md` only makes sense for Java).
- **Match this repo's existing frontmatter shape** (`name`, `version`, `description`, `applies_to`, `tags`) — the exporter and other tooling depend on this structure being consistent.

## 3. Structure of a Good Skill

- Numbered sections building from principle → pattern → anti-pattern → checklist.
- Concrete code examples over abstract prose — an agent applying the skill should be able to copy a pattern, not have to infer one from a description.
- A checklist at the end (✅ bullet list) — this is what an agent actually re-checks against before considering a task complete.
- Keep it self-contained: a reader should understand what the skill does, when to use it, and what it doesn't cover without reading other skills first.

## 4. Independent Testability

Before adding a skill, check: could someone verify an agent followed this skill correctly just by reading its output, without also reading every other skill in the repo? If understanding compliance requires cross-referencing five other files, the skill's boundary is probably wrong — narrow it.

## 5. Checklist

✅ Confirmed no existing skill already covers this (checked skills/README.md)
✅ Skill has one clear responsibility
✅ Frontmatter matches the repo's existing convention
✅ Content moves from principle to concrete pattern to checklist
✅ Skill is understandable and verifiable on its own, without requiring other skills as prerequisites
✅ Registered in skills/README.md's index after creation

---
> Inspired by ideas from [ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts) (GPL-3.0) — content rewritten, not copied. See `CREDITS.md`.
