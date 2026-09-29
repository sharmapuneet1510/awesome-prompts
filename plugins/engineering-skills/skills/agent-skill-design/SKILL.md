---
name: agent-skill-design
description: Authoring a new skill, or restructuring an existing one
---

# Agent Skill Design Skill — v1.1

## Quick Card

> Read this card first. Load a numbered section only when the task needs it.

| | |
|---|---|
| **Use when** | Authoring a new skill, or restructuring an existing one |
| **Skip when** | The guidance is specific to one feature — that belongs in its spec, not a skill |
| **Inputs** | The recurring pattern, the agents that will load it, `skills/README.md` index |
| **Produces** | `skills/<name>_skill.md` with frontmatter + Quick Card + numbered body + checklist |
| **Steps** | 1. Check the index for overlap → 2. Scope to one responsibility → 3. Write the Quick Card → 4. Body: principle → pattern → anti-pattern → checklist → 5. Register in the index |
| **Done when** | §5 checklist passes and the skill count matches everywhere the tests check |
| **Load on demand** | §1 warrant · §2 scope · §3 structure · §3a Quick Card spec · §4 testability |
| **Run report** | `html_report_skill` — adds: Overlap check · Registration |
| **Pairs with** | `html_report_skill` |

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

## 3a. The Quick Card

Every skill opens, directly under its H1, with a `## Quick Card` table. It is
the part an agent reads on every load; the numbered body is loaded only when a
step needs it. That is the token saving — progressive disclosure, not shorter
prose.

| Row | Required | Rule |
|---|---|---|
| **Use when** | yes | The trigger, in one clause |
| **Skip when** | yes | The nearest case where another skill, or nothing, fits better |
| **Inputs** | yes | What the skill reads |
| **Produces** | yes | Artifacts, with paths where they are fixed |
| **Steps** | yes | 3–6 numbered verbs, joined by → |
| **Done when** | yes | A checkable condition, not "complete" |
| **Senior defaults** | coding skills | 4–6 advanced rules that matter most; each must agree with the body |
| **Load on demand** | yes | Section numbers → topic, so an agent can load one section |
| **Run report** | yes | `html_report_skill` plus the sections this skill adds, or "own HTML" |
| **Pairs with** | yes | Skills commonly loaded alongside |

Keep every cell under about 30 words. The card must not contradict the body; if
it does, the body wins and the card is the bug.

## 4. Independent Testability

Before adding a skill, check: could someone verify an agent followed this skill correctly just by reading its output, without also reading every other skill in the repo? If understanding compliance requires cross-referencing five other files, the skill's boundary is probably wrong — narrow it.

## 5. Checklist

✅ Confirmed no existing skill already covers this (checked skills/README.md)
✅ Skill has one clear responsibility
✅ Frontmatter matches the repo's existing convention
✅ Quick Card present under the H1, every required row filled, consistent with the body
✅ Content moves from principle to concrete pattern to checklist
✅ Skill is understandable and verifiable on its own, without requiring other skills as prerequisites
✅ Registered in skills/README.md's index after creation

---
> Inspired by ideas from [ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts) (GPL-3.0) — content rewritten, not copied. See `docs/reference/credits.md`.
