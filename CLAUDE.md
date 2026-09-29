# CLAUDE.md

Guidance for Claude Code working **on** this repository. Every path and command
here is checked by `tests/test_claude_md.py`; keep it true and keep it short.

## What this repo is

A rulebook, 5 role-based agents with 43 callable functions (`agent:function`),
reusable skills (44 skills, one file each), prompt templates, and an exporter that
turns them into instruction files for 8 AI coding assistants. Overview:
[README.md](README.md) · docs: [docs/README.md](docs/README.md) · workflows for
15 use cases: [docs/01-workflows/README.md](docs/01-workflows/README.md).

## Where things live

| Source | What |
|---|---|
| `instructions/master_instruction_set.md` | The rules every agent follows (RULES 0–12) |
| `agents/` | `<role>_agent.md`, with `agents/<role>/functions/*.md` and `agents/<role>/modules/*.md` |
| `skills/` | `<name>_skill.md`, each opening with a Quick Card; index in `skills/README.md` |
| `prompts/` | Prompt templates by category |
| `hooks/` | Hook scripts exported to platforms |
| `tools/` | Python: `tools/exporter.py`, `tools/skill_validator.py`, `tools/prompt_preflight/`, … |
| `archify/` | Diagram-as-code (TypeScript), with its own tests |
| `tests/` | pytest suite, run in CI |

**Generated — do not edit by hand:** `.claude/` (committed) and `.cursor/`,
`.windsurf/`, `.gemini/`, `.continue/`, `.github/instructions/` (gitignored).
Edit the sources, then re-run the exporter.

## Commands

```bash
pip install -e ".[dev]"                 # Python 3.11+
python3 -m pytest -q                    # full suite — CI requires it green
python3 tools/skill_validator.py        # frontmatter and structure of every skill
python3 tools/exporter.py               # regenerate all platform exports
python3 tools/exporter.py --list        # what would be exported
cd archify && npm ci && npm test && npm run lint
```

## Rules for changes here

- **Principles:** think before coding, simplicity first, surgical changes,
  goal-driven execution — `instructions/master_instruction_set.md`.
- **RULE 11:** no feature code without approved requirements → design → tasks
  (`skills/spec_driven_development_skill.md`). **11a:** a contract, data-shape,
  dependency, or failure-mode change needs an Accepted ADR (`skills/adr_skill.md`).
  **RULE 12:** label claims FACT, INFERENCE, PROPOSAL, or DECISION.
- **Adding a skill or function** changes counts that
  `tests/nemesis/test_nemesis_registration.py` checks across the docs — update them.
- **New skill:** follow `skills/agent_skill_design_skill.md`.
- **Claims must be checkable:** no count, badge, or "verified" statement without
  the test or output that shows it. Close an issue only when its acceptance
  criteria are ticked and CI is green on the merge commit.
- Conventional commit subjects (`feat:`, `fix:`, `docs:`, `chore:`).

## Current work

Content review tracking issue:
[#68](https://github.com/sharmapuneet1510/awesome-prompts/issues/68).
Specs and plans for larger items: `docs/superpowers/specs/`, `docs/superpowers/plans/`.
