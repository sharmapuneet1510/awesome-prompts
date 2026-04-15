# Tools — Exporter

Exports skills and agent definitions to platform-native instruction files. One file per skill, one file per agent — no merging.

## exporter.py

### Supported Platforms

| Target | Skills | Agents | Format |
|--------|--------|--------|--------|
| `copilot` | `.github/instructions/<slug>.instructions.md` | `.github/copilot/agents/<slug>.md` | `applyTo: '**'` frontmatter |
| `claude` | `.claude/skills/<slug>.md` | `.claude/agents/<slug>.md` | Clean markdown |
| `cursor` | `.cursor/rules/<slug>.mdc` | `.cursor/rules/agents/<slug>.mdc` | `description/globs/alwaysApply` frontmatter |
| `windsurf` | `.windsurf/rules/<slug>.md` | `.windsurf/rules/agents/<slug>.md` | Clean markdown |
| `gemini` | `.gemini/skills/<slug>.md` | `.gemini/agents/<slug>.md` | Clean markdown |
| `continue` | `.continue/prompts/<slug>.prompt` | `.continue/prompts/agents/<slug>.prompt` | `name/description` frontmatter |
| `openai` | `tools/output/openai/skills/<slug>.txt` | `tools/output/openai/agents/<slug>.txt` | Plain text |
| `aider` | `.aider/skills/<slug>.md` | `.aider/agents/<slug>.md` | Clean markdown |

### Usage

```bash
# Export everything to all platforms
python tools/exporter.py

# Specific platforms
python tools/exporter.py --target copilot claude

# Filter skills and agents
python tools/exporter.py --skills java,spring --agents developer

# Dry run
python tools/exporter.py --dry-run

# List all discovered skills and agents
python tools/exporter.py --list

# Remove all exported files
python tools/exporter.py --clean
```

### Arguments

```
--target, -t   Platforms: copilot claude cursor windsurf gemini continue openai aider all
--skills, -s   Comma-separated skill slugs/tags (default: all)
--agents, -a   Comma-separated agent slugs/roles (default: all)
--list, -l     List all skills and agents then exit
--dry-run, -n  Preview without writing
--clean        Remove all exported platform directories
--repo-root    Repository root (auto-detected if omitted)
```

### Skill file format (`skills/*.md`)

```yaml
---
name: My Skill
version: 1.0
description: One-line summary
applies_to: [java, spring-boot]
tags: [java, patterns]
---
```

### Agent file format (`agents/<role>/*.md`)

```yaml
---
name: My Agent
version: 1.0
description: One-line summary
skills: [my_skill]
instruction_set: instructions/master_instruction_set.md
intake_form: instructions/my_intake.md
---
```

The `role` is derived from the agent's parent directory (`developer`, `reviewer`, `writer`, `integration`).

### Tests

```bash
python3 -m pytest tests/tools/test_exporter.py -v
```
