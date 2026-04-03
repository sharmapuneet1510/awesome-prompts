# Tools — Skill Exporter

This directory contains utility scripts for managing and exporting agent skills to various AI assistant platforms.

## skill_exporter.py

Exports advanced coding skills from `skills/` to instruction files compatible with multiple AI platforms.

### Supported Targets

| Target | Output File | Platform | Use Case |
|--------|-------------|----------|----------|
| `copilot` | `.github/copilot-instructions.md` | GitHub Copilot | VSCode, GitHub Web, CLI |
| `claude` | `.claude/skills_context.md` | Claude Code | Claude.ai, IDE extensions |
| `cursor` | `.cursorrules` | Cursor IDE | Cursor editor |
| `continue` | `.continue/config.json` | Continue.dev | VS Code extension |
| `openai` | `tools/output/openai_system_prompt.txt` | OpenAI / ChatGPT | API calls, custom GPTs |

### Quick Start

```bash
# Export ALL skills to ALL targets
python tools/skill_exporter.py

# Export specific skills to a specific target
python tools/skill_exporter.py --skills java,camel,pulsar --target copilot

# Export to GitHub Copilot only
python tools/skill_exporter.py --target copilot

# Dry run — see what would be generated
python tools/skill_exporter.py --dry-run

# List all available skills
python tools/skill_exporter.py --list
```

### Advanced Usage

```bash
# Export only Java-related skills to Cursor
python tools/skill_exporter.py --skills java --target cursor

# Export Spring and Camel to Claude
python tools/skill_exporter.py --skills spring,camel --target claude

# Export everything except Pulsar to all targets
python tools/skill_exporter.py --skills 'java,spring,camel,react,mssql,python,code_health'

# Specify a custom repo root
python tools/skill_exporter.py --repo-root /path/to/repo
```

### Arguments

```
--target, -t [TARGET ...]
  Which platform to export to. Options:
    copilot, claude, cursor, continue, openai, all
  Default: all

--skills, -s SKILL[,SKILL...]
  Comma-separated list of skill slugs to include. E.g. --skills java,spring,camel
  Default: all skills

--list, -l
  List all available skills and exit.

--dry-run, -n
  Show what would be generated without writing files.

--repo-root PATH
  Path to the repository root. Auto-detected if not provided.
```

### How It Works

1. **Discovery** — Scans `skills/` for all `.md` files with YAML frontmatter
2. **Parsing** — Extracts name, description, tags, applies_to, and content
3. **Filtering** — If `--skills` is provided, filters the list
4. **Formatting** — Each exporter formats the skills for its target platform
5. **Output** — Writes the formatted content to the target file

### Skill File Format

Every skill `.md` file must start with a YAML frontmatter block:

```yaml
---
name: Java Advanced Skill
version: 1.0
description: >
  Brief one-line description of what this skill covers.
applies_to: [java, spring-boot, maven, gradle]
tags: [java, spring, patterns, testing]
---

# Content starts here
Everything after the closing --- is the skill content...
```

### Example Output

**For GitHub Copilot** — generates `.github/copilot-instructions.md`:
- Header with instructions for Copilot
- Table of contents with links to each skill
- Full skill content sections

**For Cursor** — generates `.cursorrules`:
- Concise rules optimised for Cursor's file size limit (~50KB)
- Focuses on code quality rules and standards
- Omits lengthy examples to save space

**For OpenAI** — generates `tools/output/openai_system_prompt.txt`:
- Plain-text system prompt ready to paste into OpenAI API calls
- Also generates `.json` version with metadata and structured data
- Can be used for custom GPTs or fine-tuning

### Troubleshooting

**"No skills found"**
- Check that `.md` files exist in the `skills/` directory
- Verify files have YAML frontmatter (--- ... ---)

**"Unknown target"**
- Valid targets are: `copilot`, `claude`, `cursor`, `continue`, `openai`, `all`

**"No skills matched the filter"**
- Check spelling of skill slugs with `--list`
- Slugs match filename without `.md` extension

**Large file warnings**
- `.cursorrules` warns if > 50KB — use `--skills` to export fewer skills
- GitHub Copilot supports up to 100KB

### Integration

After exporting, the generated files are automatically read by each platform:

- **GitHub Copilot** — automatically reads `.github/copilot-instructions.md`
- **Claude Code** — reference from `CLAUDE.md` or `.claude/` folder
- **Cursor** — automatically reads `.cursorrules` from repo root
- **Continue.dev** — reads from `.continue/config.json`
- **OpenAI API** — manually copy the system prompt to your API call

No additional configuration is needed — the exporter handles everything.

### Maintenance

Run the exporter after:
- Adding new skills to `skills/`
- Modifying skill frontmatter (name, tags, etc.)
- Updating skill content that affects multiple platforms
- Before committing to ensure all platforms have the latest version

```bash
# Update all platforms in one command
python tools/skill_exporter.py
```
