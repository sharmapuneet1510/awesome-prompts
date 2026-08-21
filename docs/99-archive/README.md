# Archive

**Superseded documents, kept for reference.** Nothing here is current. Every
file is preserved with its git history via `git mv`.

Archived 2026-08-21 as part of the v5.1.0 documentation restructure — see
[../../CHANGELOG.md](../../CHANGELOG.md).

---

## Why these were archived, not deleted

Two reasons. They contain worked detail that has not yet been rewritten
elsewhere, and they record what the system looked like at a point in time, which
occasionally matters when reading an old commit or issue.

**Do not cite anything here as current.** Every file has stale counts.

---

## superseded/ — replaced by a current document

| Archived file | Claimed | Replaced by |
|---|---|---|
| `AGENTS_FUNCTIONS.md` | — | [../02-reference/functions.md](../02-reference/functions.md) |
| `AGENTS_FUNCTIONS_VERIFIED.md` | 28 functions | [../02-reference/functions.md](../02-reference/functions.md) |
| `FUNCTION_EXAMPLES.md` | 28 functions | [../04-examples/](../04-examples/) |
| `FUNCTION_QUICK_REFERENCE.md` | — | [../02-reference/functions.md](../02-reference/functions.md) |
| `API_REFERENCE.md` | 31 functions | [../02-reference/functions.md](../02-reference/functions.md) |
| `SKILLS_REFERENCE_VERIFIED.md` | 26 skills | [../02-reference/skills.md](../02-reference/skills.md) |
| `TOOLS_FUNCTIONS_VERIFIED.md` | 25 tools | [../02-reference/tools.md](../02-reference/tools.md) |
| `SPECIALIST_AGENT_MODES.md` | 9 modes | [../02-reference/agents.md](../02-reference/agents.md#specialist-modes) |
| `SPECIALIST_MODES_MAPPING.md` | 10 modes | [../02-reference/agents.md](../02-reference/agents.md#specialist-modes) |
| `FRAMEWORK_GUIDE.md` | — | [../00-getting-started/concepts.md](../00-getting-started/concepts.md) |
| `MIGRATION.md` | v2 → v3 | Historical. See [../../CHANGELOG.md](../../CHANGELOG.md) 4.0.0 |

**The count problem.** Five of these documented functions and disagreed: 28, 28,
31. None was wrong when written; all were left behind by later work. The
verified numbers are **5 agents, 42 functions, 35 skills** — see
[../02-reference/README.md](../02-reference/README.md).

---

## reports/ — point-in-time snapshots

These were never reference material. They recorded that a piece of work
finished, which is what a changelog is for.

| File | Recorded |
|---|---|
| `FUNCTION_AUDIT_SUMMARY.md` | June 2026 documentation audit — see [CHANGELOG 4.1.0](../../CHANGELOG.md) |
| `ISSUES_DOCUMENTATION_MAPPING.md` | Mapping of 3 GitHub issues to documentation, June 2026 |
| `EXPORTER_ANALYSIS.md` | Exporter reviewed against DeployHQ practices |

---

## Also removed

`README.html` — a generated copy of `README.md`, last regenerated 2026-05-25 and
three months stale by the time it was removed. Deleted rather than archived: it
was generated output, and the source it was generated from is still here.

---

## Not archived

`docs/superpowers/` — specs and plans produced by the brainstorming and
writing-plans skills. Still live: `spec_driven_development_skill.md` names that
exact path, and new design records are still written there.

---

## Finding something that used to be at root

Before the restructure, 21 documents sat at the repository root. The map:

| Was at root | Now |
|---|---|
| `SDLC_PLAYBOOK.md` | `docs/01-workflows/sdlc-playbook.md` |
| `SDLC_EXAMPLES_INDEX.md` | `docs/04-examples/README.md` |
| `*_SDLC_EXAMPLES.md` (4) | `docs/04-examples/{orchestrator,architect,implementer,quality}.md` |
| `AGENTS_FUNCTIONS*.md`, `FUNCTION_*.md` | `docs/02-reference/functions.md` (originals in `superseded/`) |
| `SPECIALIST_*.md` | `docs/02-reference/agents.md` (originals in `superseded/`) |
| `README.md`, `CLAUDE.md`, `CREDITS.md` | Still at root |
