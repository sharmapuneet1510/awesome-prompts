# Hooks Directory

This directory contains hook scripts that are automatically copied to all platforms by `tools/exporter.py`.

## What Are Hooks?

Hooks are shell or Python scripts that run automatically at key moments:
- **user-prompt-submit**: Runs before your message is sent to the AI
- **pre-commit**: Runs before git commits
- **post-commit**: Runs after successful commits

## Adding a New Hook

1. Create a `.sh` or `.py` file in this directory
2. Add YAML frontmatter with metadata:

```bash
#!/bin/bash
# name: My Hook
# version: 1.0
# description: What this hook does
# hook_type: pre-commit
# applies_to: [claude, copilot, cursor]

# Hook logic here
exit 0
```

3. Run exporter:

```bash
python3 tools/exporter.py --target claude
```

## Available Hooks

| Hook | Type | Platforms | Purpose |
|------|------|-----------|---------|
| `promptshield-check.sh` | user-prompt-submit | All | Security validation |
| `test-runner-pre-commit.py` | pre-commit | Most | Run tests before commit |
| `code-format-check.sh` | pre-commit | Most | Check Python code formatting |

## Hook Metadata

Each hook must have YAML frontmatter:

- **name**: Human-readable name
- **version**: Version string (e.g., "1.0")
- **description**: One-line description
- **hook_type**: Type of hook (pre-commit, user-prompt-submit, post-commit)
- **applies_to**: List of platforms (optional, defaults to "claude")

## Exporting Hooks

```bash
# Export all hooks to all platforms
python3 tools/exporter.py

# Export specific hooks to specific platforms
python3 tools/exporter.py --target claude --hooks promptshield

# Dry run (preview without writing)
python3 tools/exporter.py --dry-run
```

## Platform Hook Locations

| Platform | Location |
|----------|----------|
| Claude | `~/.claude/hooks/` |
| Copilot | `.github/hooks/` |
| Cursor | `.cursor/rules/hooks/` |
| Windsurf | `.windsurf/rules/hooks/` |
| Gemini | `.gemini/hooks/` |
| Continue | `.continue/hooks/` |
| OpenAI | `tools/output/openai/hooks/` |
| Aider | `.aider/hooks/` |

## Hook Format Examples

### Shell Hook (bash)

```bash
#!/bin/bash
# name: Code Format Check
# version: 1.0
# description: Validate Python code formatting before commit
# hook_type: pre-commit
# applies_to: [claude, copilot, cursor, windsurf]

set -e

# Check if black is installed
if ! command -v black &> /dev/null; then
    echo "black not installed. Install with: pip install black"
    exit 1
fi

# Format check
python_files=$(find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*")

for file in $python_files; do
    black --check "$file" || exit 1
done

echo "✓ All Python files are properly formatted"
exit 0
```

### Python Hook

```python
#!/usr/bin/env python3
# name: Test Runner
# version: 1.0
# description: Run tests before commit
# hook_type: pre-commit
# applies_to: [claude, copilot, cursor]

import subprocess
import sys

def run_tests():
    """Run test suite"""
    result = subprocess.run(
        ["python", "-m", "pytest", "-v"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Tests failed:")
        print(result.stdout)
        print(result.stderr)
        return False
    
    print("✓ All tests passed")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
```

## Hook Lifecycle

### 1. Creation
- Add `.sh` or `.py` file to `hooks/` directory
- Include YAML frontmatter with metadata

### 2. Discovery
- Run `exporter.py --list` to see hooks
- Run `exporter.py --dry-run` to preview export

### 3. Export
- Run `exporter.py --target [platform]`
- Hooks are copied to platform-specific locations

### 4. Installation
- Platform installs hooks in its native location
- Claude → `~/.claude/hooks/`
- Copilot → `.github/hooks/`
- Cursor → `.cursor/rules/hooks/`

### 5. Execution
- Platform runs hooks at configured moments
- Pre-commit hook runs before git commit
- User-prompt-submit runs before sending messages

## Best Practices

### Performance
- Keep hooks fast (< 2 seconds)
- Avoid network calls when possible
- Use caching for expensive operations

### Reliability
- Always set `set -e` in bash scripts
- Use `sys.exit(0)` for success, `sys.exit(1)` for failure
- Log meaningful error messages

### Compatibility
- Test on multiple platforms
- Use portable shell syntax (bash, not zsh-specific)
- Handle missing dependencies gracefully

### Security
- Don't hardcode credentials
- Validate all inputs
- Use environment variables for sensitive data

## Troubleshooting

### Hook Not Running

1. Check if hook was exported:
   ```bash
   ls ~/.claude/hooks/
   ```

2. Check hook permissions:
   ```bash
   chmod +x ~/.claude/hooks/my-hook.sh
   ```

3. Check hook syntax:
   ```bash
   bash -n ~/.claude/hooks/my-hook.sh
   ```

### Hook Failing

1. Test locally:
   ```bash
   ./hooks/my-hook.sh
   ```

2. Check logs:
   ```bash
   tail -f ~/.claude/logs/hooks.log
   ```

3. Debug with verbose output:
   ```bash
   bash -x hooks/my-hook.sh
   ```

## Links

- **[Exporter Tool](../tools/README.md)** — Main exporter documentation
- **[Tools Directory](../tools/)** — All utilities
- **[Setup Guide](../SETUP_GUIDE.md)** — Installation instructions
- **[Main README](../README.md)** — Project overview
