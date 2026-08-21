# 14 — Export to Platforms

**Use these agents, skills, and prompts outside Claude Code.** One command
writes platform-native instruction files for eight tools.

Covers [SDLC](sdlc-playbook.md) — none. This is repository tooling, not a
lifecycle stage.

---

## When to use this

- Your team uses Cursor, Copilot, Windsurf, or another assistant.
- You want the same agents and skills available in a different project.
- After adding or changing a skill, agent, or prompt in this repository.

## Prerequisites

- Python 3. See [../00-getting-started/installation.md](../00-getting-started/installation.md).

---

## The commands

```bash
# Everything, to every platform
python3 tools/exporter.py

# See what exists before exporting
python3 tools/exporter.py --list

# Preview without writing
python3 tools/exporter.py --dry-run

# Narrow by platform and content
python3 tools/exporter.py --target cursor copilot --skills java,spring --agents architect

# Only prompts
python3 tools/exporter.py --prompts

# Remove everything previously exported
python3 tools/exporter.py --clean
```

**Run `--dry-run` first when exporting into an existing project.** It reports
per-platform counts without touching the filesystem.

---

## Platforms

Claude · Copilot · Cursor · Windsurf · Gemini · Continue · OpenAI · Aider

Each gets its own directory convention and file format. Nothing is merged — one
file per skill, one per agent, so you can delete what you do not want without
unpicking a bundle.

---

## What gets exported

| Category | Count | Source |
|---|---|---|
| Skills | 35 | `skills/*.md` |
| Agents | 5 | `agents/*_agent.md` |
| Functions | 34 | `agents/*/functions/*.md` |
| Modules | 3 | `agents/orchestrator/modules/` |
| Instructions | 1 | `instructions/master_instruction_set.md` |
| Hooks | varies | `hooks/` |
| Prompts | 18 | `prompts/*/` |

Function *files* number 34 while the dispatch tables declare 42 callable
functions — several functions are documented inside their parent agent file
rather than as standalone files. See
[../02-reference/functions.md](../02-reference/functions.md).

---

## Export manifests

The exporter tracks what it wrote. On re-export it cleans up superseded files
rather than leaving orphans from a previous version — which matters once you
have renamed or removed a skill.

`--clean` removes everything it has ever written, using the same manifests.

---

## After changing this repository

Re-export. A skill edited here does not reach Cursor until the exporter runs.

```bash
python3 tools/exporter.py --dry-run    # confirm the change is picked up
python3 tools/exporter.py              # write it
```

---

## Artifacts

Written into the target project or this repository, depending on platform
conventions: `.claude/`, `.cursor/`, `.github/`, `.windsurf/`, `.gemini/`,
`.continue/`, `.aider/`, and OpenAI-format files.

---

## Reference

- [../03-guides/exporting-to-platforms.md](../03-guides/exporting-to-platforms.md) — full guide with per-platform detail
- `tools/README.md` — all CLI flags
