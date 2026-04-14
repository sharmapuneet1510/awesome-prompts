# Unified Agent & Skill Exporter — Design Spec

**Date:** 2026-04-14
**Status:** Approved
**Replaces:** `tools/skill_exporter.py`
**Output:** `tools/exporter.py`

---

## Problem

`tools/skill_exporter.py` exports skills only, merges all content into one file per platform, and supports only 5 platforms. Agents in `agents/` are ignored entirely.

## Goal

A single unified exporter that:
- Handles both `skills/` and `agents/` as first-class items
- Writes **one file per skill and one file per agent** — no merging
- Supports **8 platforms** with platform-native file locations and frontmatter
- Replaces `skill_exporter.py` entirely

---

## Data Models

### `BaseFile`
Shared parser for YAML frontmatter (`--- ... ---`) extraction.
- `_extract_scalar(text, key)` — single-line and block scalar values
- `_extract_list(text, key)` — inline `[a, b]` and block `- item` lists
- `slug` — derived from filename stem (e.g. `java_advanced_skill`)

### `SkillFile(BaseFile)`
Parsed from `skills/*.md`.

| Frontmatter field | Type | Description |
|---|---|---|
| `name` | str | Human-readable name |
| `version` | str | Version string |
| `description` | str | One-line summary |
| `applies_to` | list[str] | Technology areas |
| `tags` | list[str] | Topic tags |
| `content` | str | Markdown body (frontmatter stripped) |

### `AgentFile(BaseFile)`
Parsed from `agents/**/*.md` (excluding `README.md`).

| Frontmatter field | Type | Description |
|---|---|---|
| `name` | str | Agent name (e.g. "Java Senior Engineering Agent") |
| `version` | str | Version string |
| `description` | str | One-line summary |
| `skills` | list[str] | Skill slugs this agent uses |
| `instruction_set` | str | Path to master instruction set |
| `intake_form` | str | Path to intake form |
| `role` | str | Derived from subdirectory: `developer`, `reviewer`, `writer`, `integration` |
| `content` | str | Markdown body (frontmatter stripped) |

---

## Exporters

### Abstract Base: `PlatformExporter`

```
PlatformExporter
  ├── target_name: str (property)
  ├── skill_output_dir(repo_root) → Path
  ├── agent_output_dir(repo_root) → Path
  ├── format_skill(skill) → str
  ├── format_agent(agent) → str
  └── export(skills, agents, repo_root, dry_run) → ExportResult
```

`export()` iterates skills and agents, calls the appropriate format method, ensures output dirs exist, and writes one file per item.

### `ExportResult`

```python
@dataclass
class ExportResult:
    target: str
    skill_files: list[Path]
    agent_files: list[Path]
    dry_run: bool
```

### Platform Exporters

#### `CopilotExporter` — GitHub Copilot

| Item | Output path | Format |
|---|---|---|
| Skill | `.github/instructions/<slug>.instructions.md` | YAML frontmatter: `applyTo: '**'` + markdown body |
| Agent | `.github/copilot/agents/<slug>.md` | YAML frontmatter: `name`, `description` + markdown body |

Copilot reads `.github/instructions/*.instructions.md` automatically in agent mode.

#### `ClaudeExporter` — Claude Code

| Item | Output path | Format |
|---|---|---|
| Skill | `.claude/skills/<slug>.md` | Clean markdown with generated-by comment header |
| Agent | `.claude/agents/<slug>.md` | Clean markdown with generated-by comment header |

#### `CursorExporter` — Cursor IDE

| Item | Output path | Format |
|---|---|---|
| Skill | `.cursor/rules/<slug>.mdc` | YAML frontmatter: `description`, `globs: '**'`, `alwaysApply: false` + markdown |
| Agent | `.cursor/rules/agents/<slug>.mdc` | Same frontmatter pattern |

Cursor `.mdc` files require their own frontmatter block — must not be omitted.

#### `WindsurfExporter` — Windsurf IDE

| Item | Output path | Format |
|---|---|---|
| Skill | `.windsurf/rules/<slug>.md` | Clean markdown |
| Agent | `.windsurf/rules/agents/<slug>.md` | Clean markdown |

#### `GeminiExporter` — Gemini CLI

| Item | Output path | Format |
|---|---|---|
| Skill | `.gemini/skills/<slug>.md` | Clean markdown |
| Agent | `.gemini/agents/<slug>.md` | Clean markdown |

#### `ContinueExporter` — Continue.dev

| Item | Output path | Format |
|---|---|---|
| Skill | `.continue/prompts/<slug>.prompt` | YAML frontmatter: `name`, `description` + markdown |
| Agent | `.continue/prompts/agents/<slug>.prompt` | YAML frontmatter: `name`, `description` + markdown |

Continue.dev `.prompt` files require `name` and `description` in frontmatter.

#### `OpenAIExporter` — OpenAI API

| Item | Output path | Format |
|---|---|---|
| Skill | `tools/output/openai/skills/<slug>.txt` | Plain text (no markdown) |
| Agent | `tools/output/openai/agents/<slug>.txt` | Plain text (no markdown) |

Plain text is more portable for API system prompts and custom GPTs.

#### `AiderExporter` — Aider

| Item | Output path | Format |
|---|---|---|
| Skill | `.aider/skills/<slug>.md` | Clean markdown |
| Agent | `.aider/agents/<slug>.md` | Clean markdown |

---

## Orchestrator: `ExportOrchestrator`

```
ExportOrchestrator
  ├── discover_skills() → list[SkillFile]        # scans skills/*.md
  ├── discover_agents() → list[AgentFile]         # scans agents/**/*.md, skips README
  ├── filter_skills(skills, requested) → list     # match on slug/name/tags/applies_to
  ├── filter_agents(agents, requested) → list     # match on slug/name/role
  ├── run(targets, skill_filter, agent_filter, dry_run) → list[ExportResult]
  └── _print_summary(results, dry_run)
```

Pipeline:
1. Discover all skills, filter by `--skills`
2. Discover all agents, filter by `--agents`
3. Resolve target exporters from `--target` (default: all)
4. For each exporter: call `export(skills, agents, repo_root, dry_run)`
5. Print per-platform summary

---

## CLI

```
python tools/exporter.py [OPTIONS]

Options:
  --target, -t TARGET [TARGET ...]
      Platforms to export to.
      Choices: copilot, claude, cursor, windsurf, gemini, continue, openai, aider, all
      Default: all

  --skills, -s SKILL[,SKILL...]
      Comma-separated skill slugs/tags/applies_to to include.
      Default: all skills

  --agents, -a AGENT[,AGENT...]
      Comma-separated agent slugs/names/roles to include.
      Default: all agents

  --list, -l
      List all discovered skills and agents, then exit.

  --dry-run, -n
      Generate content and print paths, but do not write files.

  --clean
      Delete all previously exported files (all platform output dirs) and exit.

  --repo-root PATH
      Repository root. Auto-detected from script location if omitted.
```

### Example usage

```bash
# Export everything to all platforms
python tools/exporter.py

# Export only Java-related skills to Copilot and Claude
python tools/exporter.py --target copilot claude --skills java,spring

# Export only developer agents to Cursor
python tools/exporter.py --target cursor --agents developer

# Dry run — preview all output paths without writing
python tools/exporter.py --dry-run

# List all available skills and agents
python tools/exporter.py --list

# Clean all exported files
python tools/exporter.py --clean
```

---

## File Changes

| Action | File |
|---|---|
| Create | `tools/exporter.py` |
| Delete | `tools/skill_exporter.py` |
| Update | `tools/README.md` — replace skill_exporter docs with exporter docs |
| Update | `CLAUDE.md` — update tool reference |

---

## Out of Scope

- Watching for file changes and auto-re-exporting (not needed)
- Validating skill content quality (handled by `skill_validator.py`)
- Two-way sync (reading platform files back into source format)
- Per-agent skill inlining (agents reference skills by slug, skills export separately)
