# Skill Exporter — Quick Start Guide

## What It Does

The skill exporter converts advanced coding knowledge files into instruction formats that your AI assistant understands. It bridges the gap between your codebase and GitHub Copilot, Claude, Cursor, and other AI tools.

## Installation

No dependencies needed. The exporter is pure Python 3.

```bash
# After cloning the repository, generate IDE rules
python tools/exporter.py

# Verify installation
python tools/exporter.py --list
```

This exports agents and skills to all platforms (Claude Code, Copilot, Cursor, Windsurf, etc).

## Common Tasks

### 1. Update All AI Platforms (Recommended)

Run this after adding or updating skills:

```bash
python tools/skill_exporter.py
```

**What it does:**
- Exports all skills and agents to 8 platforms
- Updates `.github/instructions/`, `.github/agents/`, `plugins/` (Claude Code), etc.
- Creates files in `tools/output/openai/` for API use

### 2. Export for GitHub Copilot Only

```bash
python tools/exporter.py --target copilot
```

**Output:** `.github/instructions/` and `.github/agents/`

Use this when Copilot in VSCode or GitHub Web needs the latest skills and agents.

### 3. Export for Claude Code

```bash
python tools/exporter.py --target claude
```

**Output:** `plugins/` and `.claude-plugin/marketplace.json` — a plugin marketplace.

Install it in Claude Code with `/plugin marketplace add sharmapuneet1510/awesome-prompts`, then `/plugin install <plugin>@awesome-prompts`.

### 4. Export for Cursor IDE

```bash
python tools/exporter.py --target cursor
```

**Output:** `.cursor/rules/`

Cursor automatically loads rules from this folder.

### 5. Export for OpenAI API / ChatGPT

```bash
python tools/exporter.py --target openai
```

**Output:**
- `tools/output/openai/skills/` (skill files)
- `tools/output/openai/agents/` (agent files)

### 6. Export Only Certain Skills

Export just Java and Spring knowledge for Cursor:

```bash
python tools/skill_exporter.py --skills java,spring --target cursor
```

Available skill slugs:
- `java_advanced` — Java 17+, OOP, Spring Boot
- `python_advanced` — Python 3.11+, FastAPI, async
- `react_advanced` — React 18+, TypeScript, hooks
- `mssql_advanced` — T-SQL, indexing, debugging
- `code_health` — Code inspection taxonomy and reporting
- `apache_camel` — Integration patterns, EIP
- `spring_advanced` — IoC, AOP, WebFlux, Batch, Cloud
- `apache_pulsar` — Messaging, consumers, schemas

### 7. See What Would Be Generated (Dry Run)

```bash
python tools/skill_exporter.py --dry-run
```

**Output:** Shows what files would be created and their size, without writing.

Use this before committing to preview changes.

### 8. List All Available Skills

```bash
python tools/skill_exporter.py --list
```

**Shows:**
- Skill names
- File slugs (used with `--skills`)
- What technologies each skill covers

## Platform Integration

After running the exporter, each platform automatically uses the output:

### GitHub Copilot

✅ Automatic — Copilot reads `.github/instructions/` and `.github/agents/` on every suggestion.

No additional setup needed. Just run the exporter and Copilot will start applying the skills and agents.

### Claude Code (Claude.ai + Extensions)

✅ Plugins — installed once from the marketplace.

Install the plugins (see above). Commands such as `/architect:adr` then appear in the `/` menu, and Claude loads the reference skills when relevant.

### Cursor IDE

✅ Automatic — Cursor reads `.cursor/rules/` on startup.

Just run the exporter and restart Cursor.

### Continue.dev

✅ Automatic — Continue reads `.continue/prompts/` for skills and agents.

Just run the exporter and restart Continue.

### OpenAI API / Custom GPTs

❌ Manual — You copy the generated text.

**For API calls:**
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "system",
            "content": open("tools/output/openai/skills/<skill>.txt").read()
        },
        {
            "role": "user",
            "content": "Help me optimize this query"
        }
    ]
)
```

**For Custom GPTs:**
1. Run: `python tools/exporter.py --target openai`
2. Copy the contents of skill/agent files from `tools/output/openai/`
3. Paste into your Custom GPT's "Instructions" field

## Troubleshooting

### "Python: command not found"

Use `python3` instead:
```bash
python3 tools/exporter.py
```

### "No such file or directory: skills/"

Run from the repository root:
```bash
cd /path/to/awesome-prompts
python tools/exporter.py
```

### "No skills matched the filter"

Check the correct slug name:
```bash
python tools/skill_exporter.py --list
```

Then use the exact slug shown. Example:
```bash
python tools/skill_exporter.py --skills apache_camel_skill
```

### "Files are too large"

Export fewer skills to keep file sizes manageable:
```bash
python tools/exporter.py --skills java,spring --target cursor
```

### Files not being read by my platform

**Copilot:** Verify `.github/instructions/` and `.github/agents/` exist and are committed to Git.

**Claude Code:** run `/plugin` and check the awesome-prompts plugins are installed and enabled.

**Cursor:** The files go in `.cursor/rules/` — verify this folder exists.

**Continue.dev:** Restart Continue after running the exporter.

## Advanced Usage

### Combine Multiple Targets in One Run

```bash
python tools/skill_exporter.py --target copilot claude cursor
```

### Export to All Targets, But Only Java and Spring Skills

```bash
python tools/skill_exporter.py --skills java_advanced,spring_advanced
```

### Specify a Different Repo Root

```bash
python tools/skill_exporter.py --repo-root /path/to/another/repo
```

### Run From Anywhere

```bash
cd ~ && python /full/path/to/awesome-prompts/tools/exporter.py
```

## Tips

1. **Commit the exporter output** — `.github/instructions/`, `.github/agents/`, `.cursor/rules/`, etc. should be committed to Git. This ensures all team members and CI/CD get the same skills and agents.

2. **Re-export after updates** — Whenever you modify a skill or agent `.md` file, run the exporter again to update all platforms.

3. **Keep skills in sync** — The exporter is the single source of truth. Don't manually edit platform-specific files — always change the source skill/agent file and re-export.

4. **Use dry-run before committing** — Run with `--dry-run` to preview changes:
   ```bash
   python tools/exporter.py --dry-run > /tmp/export_preview.txt
   cat /tmp/export_preview.txt
   ```

5. **Version your skills** — Update the `version:` field in skill frontmatter when you make breaking changes:
   ```yaml
   ---
   name: Java Advanced Skill
   version: 1.1          # bump this
   description: ...
   ```

## Full Command Reference

```bash
# Export everything to everywhere
python tools/exporter.py

# Export specific skills/agents to specific targets
python tools/exporter.py \
  --skills java,spring,camel \
  --target copilot claude cursor

# Dry run with fewer skills
python tools/exporter.py --skills java --dry-run

# List all skills and agents
python tools/exporter.py --list

# Export from outside the repo
python tools/exporter.py --repo-root /path/to/awesome-prompts

# All at once
python tools/exporter.py -s java,spring -t copilot -n
```

## Support

For issues or questions, refer to:
- `tools/README.md` — Full technical documentation
- `skills/*.md` — Source skill files with YAML frontmatter format
- `agents/` — Source agent files
- `CLAUDE.md` — Project structure and agent definitions

