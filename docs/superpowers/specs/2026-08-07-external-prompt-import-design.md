# Import Engineering Prompts from ai-boost/awesome-prompts — Design Specification

**Date:** August 7, 2026
**Status:** Approved Design
**Version:** 1.0

---

## Executive Summary

Add 9 new engineering-focused content files to this repo — 5 new `skills/`, 4 new `prompts/` categories — inspired by a curated shortlist from `github.com/ai-boost/awesome-prompts` (GPL-3.0, 300+ persona-style prompts across many domains). Content is **rewritten in this repo's own voice and format**, not copied — each file carries a one-line "inspired by" credit, and a repo-level `CREDITS.md` links the source. Update `tools/exporter.py` to discover and export `prompts/` (currently not exported at all — only `skills/`, `agents/`, `hooks/` are), so the new and existing prompt categories reach all 8 export platforms. Generate a cleaned `prompts/README.md` index documenting the full prompt catalog (existing + new).

---

## Problem Statement

- This repo's `prompts/` directory (email, code-review, testing, codebase-analysis, project-management, incident-management, reporting) has real gaps: no debugging methodology, no refactoring guidance, no dedicated security-audit skill, no MCP/tool-design guidance, no spec-driven-development prompt, no DevOps/SRE category, no meta-prompt-engineering category, no technical-writing category.
- `ai-boost/awesome-prompts` has strong material covering these exact gaps, but it's GPL-3.0 and copying verbatim would obligate this repo to GPL-compatible licensing and raises "did we just copy someone's work" concerns the user explicitly wants to avoid.
- `tools/exporter.py` does not currently discover or export `prompts/` at all — it only handles `skills/`, `agents/` (+ modules/functions/instructions), and `hooks/`. Any new prompt content added won't reach the 8 export platforms without this fixed.

---

## Solution

### Content (rewritten, not copied)

**New `skills/` (5 files, coding-standard/pattern modules, matching existing skill frontmatter/structure):**
1. `skills/debugging_skill.md` — systematic root-cause methodology (hypothesis → isolate → verify → fix → regression-test)
2. `skills/refactoring_skill.md` — safe refactoring patterns (characterize behavior first, small reversible steps, no drive-by rewrites)
3. `skills/security_audit_skill.md` — OWASP Top 10 audit checklist + severity grading, complements existing `code_review_skill.md`
4. `skills/mcp_server_skill.md` — MCP server/tool-schema design guidance (tool minimization, least-privilege, schema clarity)
5. `skills/agent_skill_design_skill.md` — meta-guidance for authoring new skills in *this* repo's own architecture (dogfoods the skill-based system)

**New `prompts/` categories (4 dirs, one README + 1-3 template files each, matching existing `prompts/<category>/` structure):**
6. `prompts/spec-driven-development/` — complements the RULE 11 gate shipped earlier this session
7. `prompts/devops-sre/` — SRE runbook / release-engineering / IaC platform prompts
8. `prompts/meta-prompt-engineering/` — prompt-authoring and prompt-optimization guidance
9. `prompts/technical-writing/` — technical writer + plain-language (STE-style) rewriting prompts

Every new file gets a one-line footer: `> Inspired by ideas from [ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts) (GPL-3.0) — content rewritten, not copied.`

### Attribution

Add `CREDITS.md` at repo root listing each new file, which source-repo persona inspired it, and the GPL-3.0 notice. No changes to this repo's own licensing — since content is rewritten rather than copied, no GPL obligation is inherited. (If the user later wants to copy source text verbatim instead, that decision needs revisiting — out of scope here per the user's explicit instruction to rewrite, not copy.)

### `tools/exporter.py` changes

- Add a `PromptFile` class (mirrors `SkillFile`'s shape — frontmatter optional since existing `prompts/*.md` files may not have it; category = parent directory name).
- Add `ExportOrchestrator._discover_prompts()`: `for path in sorted(self._prompts_dir.rglob("*.md"))`, skip `README.md` index files.
- Wire prompts into each of the 8 `PlatformExporter` subclasses' output-path logic, following the same per-platform directory convention already used for skills (e.g., Claude → `.claude/prompts/`, Copilot → `.github/prompts/`, etc.) — extend `copy_to_target_project`'s per-platform tuple similarly.
- Add prompts to `--list` output and `--dry-run` preview.
- No changes to existing skill/agent/hook export logic.

### Documentation

Generate `prompts/README.md` — a cleaned index of the full prompt catalog (all existing categories + the 4 new ones), matching the style of `skills/README.md` (quick-navigation table: category, file, one-line purpose). Update root `CLAUDE.md`'s directory tree and Key Tools table only if the exporter's CLI surface changes (new `--prompts` flag, if added).

---

## Out of Scope

- No verbatim copying of source repo text.
- No import of non-engineering categories (healthcare, legal, game dev, roleplay, creative writing, translation, legacy 2023 personas).
- No relicensing of this repo.
- No changes to the 5-agent architecture or RULE 11.
