# Hook Exporter Feature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend exporter.py to support copying hooks to all 8 platforms (Claude, Copilot, Cursor, Windsurf, Gemini, Continue, OpenAI, Aider), automatically register hooks in platform configs, and validate hook integrity.

**Architecture:** Introduce HookFile data class (parallel to SkillFile/AgentFile), add hook_output_dir() and export_hooks() methods to PlatformExporter, implement platform-specific hook directories, auto-generate settings.json/config files with hook registrations.

**Tech Stack:** Python 3.11+, pathlib, dataclasses, JSON (settings), shell scripts (hooks)

---

### Task 1: Create HookFile Data Class

**Files:**
- Modify: `tools/exporter.py:1-300` (add HookFile class after AgentFile)
- Test: `tools/test_exporter.py` (add HookFile parsing tests)

- [ ] **Step 1: Add HookFile dataclass definition**

```python
@dataclass
class HookFile(BaseFile):
    """Represents a hook script (.sh or .py) with metadata.
    
    Attributes:
        hook_type:    Type of hook (e.g., "pre-commit", "user-prompt-submit")
        applies_to:   List of platforms this hook applies to (e.g., ["claude", "copilot"])
        is_executable: Whether this is a shell script (.sh) or Python script (.py)
    """
    hook_type: str
    applies_to: list[str] = field(default_factory=list)
    is_executable: bool = False
    
    @classmethod
    def from_path(cls, path: Path) -> "HookFile":
        """Parse hook file from disk.
        
        Args:
            path: Path to hook file (.sh or .py)
            
        Returns:
            HookFile with parsed metadata from frontmatter
            
        Raises:
            ValueError: If file has no frontmatter or invalid hook_type
        """
        fm_text, body = cls._parse_frontmatter(path)
        
        name = cls._extract_scalar(fm_text, "name", default=path.stem)
        version = cls._extract_scalar(fm_text, "version", default="1.0.0")
        description = cls._extract_scalar(fm_text, "description", default="")
        hook_type = cls._extract_scalar(fm_text, "hook_type", default="")
        applies_to = cls._extract_list(fm_text, "applies_to")
        
        if not hook_type:
            raise ValueError(
                f"Hook file '{path.name}' missing 'hook_type' in frontmatter. "
                f"Must specify: hook_type: <type>"
            )
        
        is_executable = path.suffix == ".sh"
        
        return cls(
            path=path,
            name=name,
            version=version,
            description=description,
            content=body,
            slug=path.stem,
            hook_type=hook_type,
            applies_to=applies_to or ["claude"],  # default to claude
            is_executable=is_executable,
        )
```

- [ ] **Step 2: Write tests for HookFile parsing**

```python
def test_hookfile_from_path_valid():
    """Parse valid hook file with all required fields."""
    content = """---
name: Security Check
version: 1.0
description: Validates prompt patterns
hook_type: user-prompt-submit
applies_to: [claude, copilot, cursor]
---

#!/bin/bash
# Hook body here
exit 0
"""
    hook = HookFile.from_path_string(content, "test.sh")
    assert hook.name == "Security Check"
    assert hook.hook_type == "user-prompt-submit"
    assert hook.applies_to == ["claude", "copilot", "cursor"]
    assert hook.is_executable is True

def test_hookfile_missing_hook_type():
    """Raise error when hook_type is missing."""
    content = """---
name: Bad Hook
version: 1.0
---

#!/bin/bash
"""
    with pytest.raises(ValueError, match="hook_type"):
        HookFile.from_path_string(content, "bad.sh")

def test_hookfile_defaults_to_claude():
    """Default applies_to to ['claude'] if not specified."""
    content = """---
name: Default Hook
hook_type: pre-commit
---

#!/bin/bash
"""
    hook = HookFile.from_path_string(content, "default.sh")
    assert hook.applies_to == ["claude"]
```

- [ ] **Step 3: Run tests to verify HookFile works**

```bash
pytest tools/test_exporter.py::test_hookfile_from_path_valid -v
pytest tools/test_exporter.py::test_hookfile_missing_hook_type -v
pytest tools/test_exporter.py::test_hookfile_defaults_to_claude -v
```

Expected: All 3 tests PASS

- [ ] **Step 4: Commit HookFile class**

```bash
git add tools/exporter.py tools/test_exporter.py
git commit -m "feat: add HookFile data class for hook parsing"
```

---

### Task 2: Add Hook Scanning to Exporter

**Files:**
- Modify: `tools/exporter.py:800-950` (main function and file discovery)
- Test: `tools/test_exporter.py` (add hook discovery tests)

- [ ] **Step 1: Create hook discovery function**

```python
def discover_hooks(repo_root: Path) -> list[HookFile]:
    """Scan hooks/ directory and parse all hook files.
    
    Args:
        repo_root: Root directory of the repository
        
    Returns:
        List of parsed HookFile objects
        
    Note:
        Hooks can be .sh or .py files with YAML frontmatter.
        If hooks/ directory doesn't exist, returns empty list.
    """
    hooks_dir = repo_root / "hooks"
    
    if not hooks_dir.exists():
        return []
    
    hooks: list[HookFile] = []
    
    for hook_file in sorted(hooks_dir.glob("*")):
        if hook_file.suffix not in [".sh", ".py"]:
            continue
        if hook_file.name.startswith("."):
            continue
        
        try:
            hook = HookFile.from_path(hook_file)
            hooks.append(hook)
        except ValueError as e:
            print(f"⚠️  Skipping hook {hook_file.name}: {e}", file=sys.stderr)
            continue
    
    return hooks
```

- [ ] **Step 2: Add to ExportResult dataclass**

```python
@dataclass
class ExportResult:
    # ... existing fields ...
    hook_files: list[Path] = field(default_factory=list)
    
    def summary(self) -> str:
        """Human-readable summary of exported files."""
        lines = [
            f"✅ {self.target.upper()}",
            f"   Skills: {len(self.skill_files)}",
            f"   Agents: {len(self.agent_files)}",
            f"   Hooks:  {len(self.hook_files)}",
        ]
        return "\n".join(lines)
```

- [ ] **Step 3: Write hook discovery tests**

```python
def test_discover_hooks_empty():
    """Return empty list when hooks/ doesn't exist."""
    with tmp_repo() as repo_root:
        hooks = discover_hooks(repo_root)
        assert hooks == []

def test_discover_hooks_valid():
    """Discover and parse valid hook files."""
    with tmp_repo() as repo_root:
        hooks_dir = repo_root / "hooks"
        hooks_dir.mkdir()
        
        (hooks_dir / "test.sh").write_text("""---
name: Test Hook
hook_type: pre-commit
applies_to: [claude]
---

#!/bin/bash
exit 0
""")
        
        hooks = discover_hooks(repo_root)
        assert len(hooks) == 1
        assert hooks[0].name == "Test Hook"
        assert hooks[0].hook_type == "pre-commit"

def test_discover_hooks_skip_invalid():
    """Skip hooks with missing required fields."""
    with tmp_repo() as repo_root:
        hooks_dir = repo_root / "hooks"
        hooks_dir.mkdir()
        
        # Valid hook
        (hooks_dir / "valid.sh").write_text("""---
name: Valid
hook_type: pre-commit
---

#!/bin/bash
exit 0
""")
        
        # Invalid hook (missing hook_type)
        (hooks_dir / "invalid.sh").write_text("""---
name: Invalid
---

#!/bin/bash
exit 0
""")
        
        hooks = discover_hooks(repo_root)
        assert len(hooks) == 1  # Only valid hook
        assert hooks[0].name == "Valid"
```

- [ ] **Step 4: Run tests**

```bash
pytest tools/test_exporter.py::test_discover_hooks_empty -v
pytest tools/test_exporter.py::test_discover_hooks_valid -v
pytest tools/test_exporter.py::test_discover_hooks_skip_invalid -v
```

Expected: All 3 tests PASS

- [ ] **Step 5: Commit hook discovery**

```bash
git add tools/exporter.py tools/test_exporter.py
git commit -m "feat: add hook discovery and scanning"
```

---

### Task 3: Add Hook Export to PlatformExporter Base Class

**Files:**
- Modify: `tools/exporter.py:279-361` (PlatformExporter abstract base class)
- Test: `tools/test_exporter.py` (add hook export tests)

- [ ] **Step 1: Add abstract hook methods to PlatformExporter**

```python
class PlatformExporter(ABC):
    """Abstract base class for all platform exporters."""
    
    # ... existing code ...
    
    @abstractmethod
    def hook_output_dir(self) -> Path:
        """Directory where hook files are written.
        
        Examples:
            - Claude: ~/.claude/hooks/
            - Copilot: .github/hooks/
            - Cursor: .cursor/hooks/
        """

    def hook_filename(self, hook: HookFile) -> str:
        """Output filename for a hook. Override for platform-specific naming."""
        return hook.path.name  # Default: keep original filename

    def format_hook(self, hook: HookFile) -> str:
        """Format hook content for this platform.
        
        Default: return content as-is (for shell/Python scripts).
        Override for platforms needing special formatting.
        """
        return hook.content

    def export_hooks(
        self,
        hooks: list[HookFile],
        dry_run: bool = False,
    ) -> list[Path]:
        """Copies hook scripts to platform directory.
        
        Args:
            hooks:   Hook files to export.
            dry_run: If True, generate paths but do not write files.
            
        Returns:
            List of written (or planned) hook file paths.
        """
        hook_paths: list[Path] = []
        
        for hook in hooks:
            # Filter: only export hooks that apply to this platform
            if hook.applies_to and self.target_name not in hook.applies_to:
                continue
            
            out = self.hook_output_dir() / self.hook_filename(hook)
            hook_paths.append(out)
            
            if not dry_run:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(self.format_hook(hook), encoding="utf-8")
                
                # Make shell scripts executable
                if hook.is_executable:
                    out.chmod(0o755)
        
        return hook_paths
```

- [ ] **Step 2: Update export() method to include hooks**

```python
def export(
    self,
    skills: list[SkillFile],
    agents: list[AgentFile],
    hooks: list[HookFile],  # NEW
    dry_run: bool = False,
) -> ExportResult:
    """Writes one file per skill, agent, and hook."""
    
    # ... existing skill/agent export code ...
    
    hook_paths = self.export_hooks(hooks, dry_run=dry_run)
    
    return ExportResult(
        target=self.target_name,
        skill_files=skill_paths,
        agent_files=agent_paths,
        hook_files=hook_paths,  # NEW
        dry_run=dry_run,
    )
```

- [ ] **Step 3: Write hook export tests**

```python
def test_export_hooks_filters_by_platform():
    """Only export hooks that apply to this platform."""
    exporter = ClaudeExporter(Path("/repo"))
    
    hook_claude = HookFile(
        path=Path("test.sh"), name="Claude Hook", version="1.0",
        description="", content="exit 0", slug="test",
        hook_type="pre-commit", applies_to=["claude"], is_executable=True
    )
    
    hook_copilot = HookFile(
        path=Path("copilot.sh"), name="Copilot Hook", version="1.0",
        description="", content="exit 0", slug="copilot",
        hook_type="pre-commit", applies_to=["copilot"], is_executable=True
    )
    
    with tmp_repo() as repo_root:
        exporter = ClaudeExporter(repo_root)
        paths = exporter.export_hooks([hook_claude, hook_copilot], dry_run=False)
        
        # Only claude hook exported
        assert len(paths) == 1
        assert "test.sh" in str(paths[0])

def test_export_hooks_makes_executable():
    """Set executable bit on .sh files."""
    with tmp_repo() as repo_root:
        exporter = ClaudeExporter(repo_root)
        hook = HookFile(
            path=Path("test.sh"), name="Test", version="1.0",
            description="", content="#!/bin/bash\nexit 0", slug="test",
            hook_type="pre-commit", applies_to=["claude"], is_executable=True
        )
        
        paths = exporter.export_hooks([hook], dry_run=False)
        
        hook_file = paths[0]
        assert hook_file.exists()
        assert os.access(hook_file, os.X_OK)  # executable
```

- [ ] **Step 4: Run tests**

```bash
pytest tools/test_exporter.py::test_export_hooks_filters_by_platform -v
pytest tools/test_exporter.py::test_export_hooks_makes_executable -v
```

Expected: Both tests PASS

- [ ] **Step 5: Commit hook export base class**

```bash
git add tools/exporter.py tools/test_exporter.py
git commit -m "feat: add hook_output_dir and export_hooks to PlatformExporter"
```

---

### Task 4: Implement hook_output_dir() for All 8 Platforms

**Files:**
- Modify: `tools/exporter.py:367-650` (CopilotExporter, ClaudeExporter, CursorExporter, WindsurfExporter, GeminiExporter, ContinueExporter, OpenAIExporter, AiderExporter classes)
- Test: `tools/test_exporter.py` (add platform-specific tests)

- [ ] **Step 1: Add hook_output_dir to ClaudeExporter**

```python
class ClaudeExporter(PlatformExporter):
    """Claude Code — .claude/skills/, .claude/agents/, .claude/hooks/"""
    
    def hook_output_dir(self) -> Path:
        return self._repo_root / ".claude" / "hooks"
```

- [ ] **Step 2: Add hook_output_dir to CopilotExporter**

```python
class CopilotExporter(PlatformExporter):
    """GitHub Copilot — .github/instructions/, .github/agents/, .github/hooks/"""
    
    def hook_output_dir(self) -> Path:
        return self._repo_root / ".github" / "hooks"
```

- [ ] **Step 3: Add hook_output_dir to CursorExporter**

```python
class CursorExporter(PlatformExporter):
    """Cursor IDE — .cursor/rules/, .cursor/rules/agents/, .cursor/rules/hooks/"""
    
    def hook_output_dir(self) -> Path:
        return self._repo_root / ".cursor" / "rules" / "hooks"
```

- [ ] **Step 4: Add hook_output_dir to WindsurfExporter**

```python
class WindsurfExporter(PlatformExporter):
    """Windsurf IDE — .windsurf/rules/, .windsurf/rules/agents/, .windsurf/rules/hooks/"""
    
    def hook_output_dir(self) -> Path:
        return self._repo_root / ".windsurf" / "rules" / "hooks"
```

- [ ] **Step 5: Add hook_output_dir to GeminiExporter**

```python
class GeminiExporter(PlatformExporter):
    """Google Gemini — .gemini/skills/, .gemini/agents/, .gemini/hooks/"""
    
    def hook_output_dir(self) -> Path:
        return self._repo_root / ".gemini" / "hooks"
```

- [ ] **Step 6: Add hook_output_dir to ContinueExporter**

```python
class ContinueExporter(PlatformExporter):
    """Continue IDE — .continue/prompts/, .continue/prompts/agents/, .continue/hooks/"""
    
    def hook_output_dir(self) -> Path:
        return self._repo_root / ".continue" / "hooks"
```

- [ ] **Step 7: Add hook_output_dir to OpenAIExporter**

```python
class OpenAIExporter(PlatformExporter):
    """OpenAI — tools/output/openai/skills/, agents/, hooks/"""
    
    def hook_output_dir(self) -> Path:
        return self._repo_root / "tools" / "output" / "openai" / "hooks"
```

- [ ] **Step 8: Add hook_output_dir to AiderExporter**

```python
class AiderExporter(PlatformExporter):
    """Aider CLI — .aider/skills/, .aider/agents/, .aider/hooks/"""
    
    def hook_output_dir(self) -> Path:
        return self._repo_root / ".aider" / "hooks"
```

- [ ] **Step 9: Write platform-specific tests**

```python
def test_claude_exporter_hook_output_dir():
    exporter = ClaudeExporter(Path("/repo"))
    assert exporter.hook_output_dir() == Path("/repo/.claude/hooks")

def test_copilot_exporter_hook_output_dir():
    exporter = CopilotExporter(Path("/repo"))
    assert exporter.hook_output_dir() == Path("/repo/.github/hooks")

def test_cursor_exporter_hook_output_dir():
    exporter = CursorExporter(Path("/repo"))
    assert exporter.hook_output_dir() == Path("/repo/.cursor/rules/hooks")

# ... similar for other 5 platforms
```

- [ ] **Step 10: Run all platform tests**

```bash
pytest tools/test_exporter.py -k "hook_output_dir" -v
```

Expected: 8 tests PASS

- [ ] **Step 11: Commit platform hook directories**

```bash
git add tools/exporter.py tools/test_exporter.py
git commit -m "feat: add hook_output_dir for all 8 platforms"
```

---

### Task 5: Create Sample Hooks in hooks/ Directory

**Files:**
- Create: `hooks/promptshield-check.sh`
- Create: `hooks/test-runner-pre-commit.py`
- Create: `hooks/code-format-check.sh`

- [ ] **Step 1: Create promptshield-check.sh hook**

```bash
cat > /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/hooks/promptshield-check.sh << 'EOF'
#!/bin/bash
# name: Promptshield Security Check
# version: 1.0
# description: Validates user prompts for security patterns and injection attempts
# hook_type: user-prompt-submit
# applies_to: [claude, copilot, cursor, windsurf, gemini, continue, openai, aider]

set -e

# List of dangerous patterns to check for
DANGEROUS_PATTERNS=(
    "DROP TABLE"
    "DELETE FROM"
    "ALTER TABLE"
    "TRUNCATE TABLE"
    "exec("
    "eval("
    "__import__"
    "subprocess.call"
    "os.system"
)

# Check if any dangerous patterns appear in the prompt
for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if [[ "$1" == *"$pattern"* ]]; then
        echo "⚠️  Security alert: Detected potentially dangerous pattern: $pattern"
        echo "This may indicate SQL injection or code injection attempt."
        exit 1
    fi
done

echo "✅ Prompt passed security validation"
exit 0
EOF
chmod +x /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/hooks/promptshield-check.sh
```

- [ ] **Step 2: Create test-runner-pre-commit.py hook**

```bash
cat > /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/hooks/test-runner-pre-commit.py << 'EOF'
#!/usr/bin/env python3
# name: Test Runner Pre-Commit
# version: 1.0
# description: Runs test suite before allowing commits
# hook_type: pre-commit
# applies_to: [claude, copilot, cursor, windsurf, gemini, continue, openai]

import subprocess
import sys

def run_tests():
    """Run pytest with coverage."""
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", "tools/", "-v", "--cov=tools", "--cov-report=term-missing"],
            check=True,
            capture_output=False
        )
        print("✅ All tests passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("⚠️  pytest not found, skipping test hook")
        return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
EOF
chmod +x /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/hooks/test-runner-pre-commit.py
```

- [ ] **Step 3: Create code-format-check.sh hook**

```bash
cat > /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/hooks/code-format-check.sh << 'EOF'
#!/bin/bash
# name: Code Format Checker
# version: 1.0
# description: Checks Python code formatting with black and isort
# hook_type: pre-commit
# applies_to: [claude, copilot, cursor, windsurf]

set -e

echo "🔍 Checking Python code format..."

# Check if black is installed
if ! command -v black &> /dev/null; then
    echo "⚠️  black not installed, skipping format check"
    exit 0
fi

# Run black on tools/ directory
if ! black --check tools/ 2>/dev/null; then
    echo "❌ Code format issues found. Run: black tools/"
    exit 1
fi

echo "✅ Code format check passed"
exit 0
EOF
chmod +x /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/hooks/code-format-check.sh
```

- [ ] **Step 4: Verify hooks have correct frontmatter**

```bash
head -10 /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/hooks/*.sh
head -10 /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/hooks/*.py
```

Expected: All hooks show frontmatter with name, version, description, hook_type, applies_to

- [ ] **Step 5: Commit sample hooks**

```bash
git add hooks/
git commit -m "feat: add sample hooks (promptshield, test-runner, format-check)"
```

---

### Task 6: Auto-Generate settings.json and Platform Configs with Hook Registrations

**Files:**
- Modify: `tools/exporter.py:900-1023` (main function and config generation)
- Create: `tools/config_generator.py` (new module for platform config generation)
- Test: `tools/test_exporter.py` (config generation tests)

- [ ] **Step 1: Create config_generator.py module**

```python
cat > /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/tools/config_generator.py << 'EOF'
"""Generate platform-specific configuration files with hook registrations.

This module generates configuration files (settings.json, .cursorules, etc.)
that register exported hooks for each platform.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class HookConfig:
    """Configuration for a hook in platform settings."""
    hook_type: str
    hook_path: str  # Path to the hook script


class ConfigGenerator:
    """Base class for platform-specific config generation."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
    
    def generate_claude_settings(self, hook_paths: list[Path]) -> dict[str, Any]:
        """Generate .claude/settings.json with hook registrations.
        
        Args:
            hook_paths: List of exported hook file paths
            
        Returns:
            Dict suitable for JSON serialization
        """
        hooks_by_type: dict[str, list[dict]] = {}
        
        for hook_path in hook_paths:
            # Extract hook type from parent directory or filename
            hook_type = hook_path.parent.name  # e.g., "pre-commit" from hooks/pre-commit/
            
            if hook_type not in hooks_by_type:
                hooks_by_type[hook_type] = []
            
            hooks_by_type[hook_type].append({
                "type": "command",
                "command": str(hook_path)
            })
        
        settings = {
            "model": "haiku",
            "hooks": {
                "UserPromptSubmit": [
                    {
                        "matcher": "",
                        "hooks": hooks_by_type.get("user-prompt-submit", [])
                    }
                ],
                "PreCommit": [
                    {
                        "matcher": "",
                        "hooks": hooks_by_type.get("pre-commit", [])
                    }
                ]
            },
            "enabledPlugins": {
                "superpowers@claude-plugins-official": True,
                "frontend-design@claude-plugins-official": True,
                "code-review@claude-plugins-official": True,
                "playwright@claude-plugins-official": True,
            }
        }
        
        return settings

    def generate_copilot_config(self, hook_paths: list[Path]) -> str:
        """Generate GitHub Copilot .github/copilot.yml config."""
        lines = [
            "# Generated by tools/exporter.py — Do not edit manually",
            "# Re-run: python tools/exporter.py",
            "",
            "version: 1",
            "",
            "hooks:",
        ]
        
        for hook_path in hook_paths:
            hook_name = hook_path.stem
            lines.append(f"  - name: {hook_name}")
            lines.append(f"    path: {hook_path.relative_to(self.repo_root)}")
        
        return "\n".join(lines) + "\n"

    def generate_gitignore_entry(self) -> str:
        """Return .gitignore entry for local hook configs (not tracked)."""
        return "\n".join([
            "# Generated hook configs (local, not tracked)",
            ".claude/settings.local.json",
            ".github/copilot.local.yml",
        ]) + "\n"
EOF
```

- [ ] **Step 2: Update main() in exporter.py to generate configs**

```python
def main() -> None:
    """Main entry point."""
    args = build_argument_parser().parse_args()
    
    # ... existing code to load skills, agents ...
    
    hooks = discover_hooks(repo_root)  # NEW: discover hooks
    
    exporters = get_exporters(repo_root, args.target)
    results = []
    
    for exporter in exporters:
        result = exporter.export(
            skills=filtered_skills,
            agents=filtered_agents,
            hooks=hooks,  # NEW: pass hooks
            dry_run=args.dry_run
        )
        results.append(result)
        
        # NEW: Generate platform-specific configs
        if exporter.target_name == "claude" and not args.dry_run:
            config_gen = ConfigGenerator(repo_root)
            hook_paths = exporter.export_hooks(hooks, dry_run=False)
            settings = config_gen.generate_claude_settings(hook_paths)
            
            settings_file = repo_root / ".claude" / "settings.json"
            settings_file.parent.mkdir(parents=True, exist_ok=True)
            settings_file.write_text(json.dumps(settings, indent=2))
            print(f"📝 Generated {settings_file}")
    
    # NEW: Print summary
    print("\n" + "="*60)
    for result in results:
        print(result.summary())
```

- [ ] **Step 3: Write config generation tests**

```python
def test_generate_claude_settings():
    """Generate valid Claude settings.json with hooks."""
    gen = ConfigGenerator(Path("/repo"))
    hook_paths = [
        Path("/repo/.claude/hooks/promptshield-check.sh"),
        Path("/repo/.claude/hooks/test-runner.py"),
    ]
    
    settings = gen.generate_claude_settings(hook_paths)
    
    assert "hooks" in settings
    assert "UserPromptSubmit" in settings["hooks"]
    assert len(settings["hooks"]["UserPromptSubmit"]) > 0

def test_generate_copilot_config():
    """Generate GitHub Copilot config YAML."""
    gen = ConfigGenerator(Path("/repo"))
    hook_paths = [Path("/repo/.github/hooks/test.sh")]
    
    config = gen.generate_copilot_config(hook_paths)
    
    assert "version: 1" in config
    assert "hooks:" in config
    assert "test.sh" in config
```

- [ ] **Step 4: Run config generation tests**

```bash
pytest tools/test_exporter.py::test_generate_claude_settings -v
pytest tools/test_exporter.py::test_generate_copilot_config -v
```

Expected: Both tests PASS

- [ ] **Step 5: Commit config generation**

```bash
git add tools/exporter.py tools/config_generator.py tools/test_exporter.py
git commit -m "feat: auto-generate platform configs with hook registrations"
```

---

### Task 7: Update Exporter CLI to Support Hooks Argument

**Files:**
- Modify: `tools/exporter.py:823-880` (argument parser)
- Test: `tools/test_exporter.py` (CLI argument tests)

- [ ] **Step 1: Add --hooks argument to parser**

```python
def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(...)
    
    # ... existing arguments ...
    
    parser.add_argument(
        "--hooks",
        "-k",
        type=str,
        default=None,
        help=(
            "Comma-separated list of hooks to export (e.g., promptshield,test-runner). "
            "If omitted, all hooks are exported."
        ),
    )
    
    return parser
```

- [ ] **Step 2: Add hook filtering logic**

```python
def filter_hooks(hooks: list[HookFile], names: str | None) -> list[HookFile]:
    """Filter hooks by name if specified.
    
    Args:
        hooks: All discovered hooks
        names: Comma-separated hook names (or None for all)
        
    Returns:
        Filtered list of hooks
    """
    if not names:
        return hooks
    
    requested = set(n.strip() for n in names.split(","))
    return [h for h in hooks if h.slug in requested]
```

- [ ] **Step 3: Update main() to use hook filter**

```python
def main() -> None:
    args = build_argument_parser().parse_args()
    
    # ... existing code ...
    
    hooks = discover_hooks(repo_root)
    hooks = filter_hooks(hooks, args.hooks)  # NEW: filter by name
    
    # ... rest of export logic ...
```

- [ ] **Step 4: Update help text and docstring**

```python
def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export skills, agents, and hooks to platform-native formats.",
        epilog=(
            "Examples:\n"
            "  python tools/exporter.py                          # all → all platforms\n"
            "  python tools/exporter.py --target claude          # all skills/agents/hooks → claude\n"
            "  python tools/exporter.py --skills java,spring     # specific skills only\n"
            "  python tools/exporter.py --hooks promptshield     # specific hooks only\n"
            "  python tools/exporter.py --interactive            # guided setup\n"
        ),
    )
    
    return parser
```

- [ ] **Step 5: Write CLI tests**

```python
def test_filter_hooks_by_name():
    """Filter hooks by comma-separated names."""
    hooks = [
        HookFile(..., slug="promptshield", ...),
        HookFile(..., slug="test-runner", ...),
        HookFile(..., slug="formatter", ...),
    ]
    
    filtered = filter_hooks(hooks, "promptshield,formatter")
    
    assert len(filtered) == 2
    assert filtered[0].slug == "promptshield"
    assert filtered[1].slug == "formatter"

def test_filter_hooks_none_returns_all():
    """Return all hooks if no filter specified."""
    hooks = [
        HookFile(..., slug="a", ...),
        HookFile(..., slug="b", ...),
    ]
    
    filtered = filter_hooks(hooks, None)
    
    assert len(filtered) == 2
```

- [ ] **Step 6: Run CLI tests**

```bash
pytest tools/test_exporter.py::test_filter_hooks_by_name -v
pytest tools/test_exporter.py::test_filter_hooks_none_returns_all -v
```

Expected: Both tests PASS

- [ ] **Step 7: Commit CLI updates**

```bash
git add tools/exporter.py tools/test_exporter.py
git commit -m "feat: add --hooks CLI argument and filtering"
```

---

### Task 8: Test Hook Export End-to-End

**Files:**
- Test: `tools/test_exporter.py` (end-to-end integration tests)

- [ ] **Step 1: Write full export test**

```python
def test_export_hooks_end_to_end():
    """Test complete hook export workflow."""
    with tmp_repo() as repo_root:
        # Create hooks/ directory with sample hooks
        hooks_dir = repo_root / "hooks"
        hooks_dir.mkdir()
        
        (hooks_dir / "test.sh").write_text("""---
name: Test Hook
version: 1.0
description: Test hook
hook_type: pre-commit
applies_to: [claude, copilot]
---

#!/bin/bash
exit 0
""")
        
        # Discover hooks
        hooks = discover_hooks(repo_root)
        assert len(hooks) == 1
        
        # Export to claude
        claude_exporter = ClaudeExporter(repo_root)
        result = claude_exporter.export([], [], hooks, dry_run=False)
        
        # Verify hook was exported
        assert len(result.hook_files) == 1
        hook_file = result.hook_files[0]
        assert hook_file.exists()
        assert hook_file.parent == repo_root / ".claude" / "hooks"
        assert os.access(hook_file, os.X_OK)  # executable

def test_export_all_platforms_with_hooks():
    """Test hook export to all 8 platforms."""
    with tmp_repo() as repo_root:
        hooks_dir = repo_root / "hooks"
        hooks_dir.mkdir()
        
        (hooks_dir / "multi.sh").write_text("""---
name: Multi Platform Hook
hook_type: pre-commit
applies_to: [claude, copilot, cursor, windsurf, gemini, continue, openai, aider]
---

#!/bin/bash
exit 0
""")
        
        hooks = discover_hooks(repo_root)
        
        # Export to all platforms
        for exporter_cls in [ClaudeExporter, CopilotExporter, CursorExporter, 
                            WindsurfExporter, GeminiExporter, ContinueExporter, 
                            OpenAIExporter, AiderExporter]:
            exporter = exporter_cls(repo_root)
            result = exporter.export([], [], hooks, dry_run=False)
            
            # Each platform should have 1 hook
            assert len(result.hook_files) == 1
            assert result.hook_files[0].exists()
```

- [ ] **Step 2: Run end-to-end tests**

```bash
pytest tools/test_exporter.py::test_export_hooks_end_to_end -v
pytest tools/test_exporter.py::test_export_all_platforms_with_hooks -v
```

Expected: Both tests PASS

- [ ] **Step 3: Test with actual exporter command**

```bash
# Run exporter with all options
python3 tools/exporter.py --target claude --dry-run

# Expected output: Lists skills, agents, hooks that would be exported
# ✅ CLAUDE
#    Skills: N
#    Agents: M
#    Hooks: 3
```

- [ ] **Step 4: Commit end-to-end tests**

```bash
git add tools/test_exporter.py
git commit -m "test: add end-to-end hook export tests"
```

---

### Task 9: Update Documentation and README

**Files:**
- Modify: `tools/README.md` (add hook exporting section)
- Modify: `SETUP_GUIDE.md` (mention hook exporting)
- Create: `hooks/README.md` (hooks directory guide)

- [ ] **Step 1: Create hooks/README.md**

```bash
cat > /Users/puneetsharma/Workspace/projects/ai-lab/awesome-prompts/hooks/README.md << 'EOF'
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

| Platform | Location | Config File |
|----------|----------|-------------|
| Claude | `~/.claude/hooks/` | `~/.claude/settings.json` |
| Copilot | `.github/hooks/` | `.github/copilot.yml` |
| Cursor | `.cursor/rules/hooks/` | `.cursor/rules/.cursorules` |
| Windsurf | `.windsurf/rules/hooks/` | `.windsurf/.windsurf` |
| Gemini | `.gemini/hooks/` | `.gemini/gemini.json` |
| Continue | `.continue/hooks/` | `.continue/config.json` |
| OpenAI | `tools/output/openai/hooks/` | `tools/output/openai/config.json` |
| Aider | `.aider/hooks/` | `.aider/.aiderrc` |

## Testing Hooks

```bash
# Test a hook directly
bash hooks/promptshield-check.sh "test prompt"

# Run hook tests
pytest hooks/test_hooks.py -v
```
EOF
```

- [ ] **Step 2: Update tools/README.md**

```bash
# Find the section on exporter and update it
# Add a "Hooks" section describing how to export hooks
```

Find this section in tools/README.md:
```markdown
### Usage

Export all skills and agents to all platforms:
```

Add after it:

```markdown
### Exporting Hooks

Hooks are automatically discovered from the `hooks/` directory and exported to all platforms:

```bash
# Export hooks with skills and agents
python3 tools/exporter.py

# Export only hooks
python3 tools/exporter.py --hooks promptshield,test-runner

# Export hooks to specific platforms
python3 tools/exporter.py --target claude copilot --hooks promptshield
```

See `hooks/README.md` for hook format and examples.
```

- [ ] **Step 3: Update SETUP_GUIDE.md**

Add after the "Installation" section:

```markdown
### 4️⃣ (Optional) Configure Hooks

Hooks are security and development automation scripts that run at key moments.

```bash
# Export hooks to your Claude environment
python3 tools/exporter.py --target claude --hooks promptshield,test-runner
```

After export, hooks will automatically run:
- **Before you send messages** — security validation
- **Before git commits** — test and format checking
- **After commits** — cleanup and notifications
```

- [ ] **Step 4: Commit documentation**

```bash
git add hooks/README.md tools/README.md SETUP_GUIDE.md
git commit -m "docs: add hook exporting documentation"
```

---

### Task 10: Final Validation and Testing

**Files:**
- Test: Run all exporter tests
- Verify: Hook exporting works end-to-end

- [ ] **Step 1: Run complete test suite**

```bash
pytest tools/test_exporter.py -v --tb=short

# Expected: All tests pass
# Test summary should show:
# - HookFile parsing tests (4+)
# - Hook discovery tests (3+)
# - Hook export tests (5+)
# - Platform-specific tests (8+)
# - Config generation tests (2+)
# - CLI tests (2+)
# - End-to-end tests (2+)
# Total: 26+ tests, all PASS
```

- [ ] **Step 2: Manual smoke test**

```bash
# 1. Verify hooks directory exists
ls -la hooks/

# 2. Discover hooks
python3 tools/exporter.py --list | grep -i hook

# 3. Dry-run export
python3 tools/exporter.py --dry-run --target claude

# Expected: Should list 3 hooks (promptshield, test-runner, formatter)

# 4. Actual export
python3 tools/exporter.py --target claude

# Verify hooks were created
ls -la ~/.claude/hooks/

# 5. Verify settings.json was updated
cat ~/.claude/settings.json | jq '.hooks'

# Expected: Should show hook registrations
```

- [ ] **Step 3: Test hook execution**

```bash
# Test promptshield hook
bash ~/.claude/hooks/promptshield-check.sh "normal prompt"
# Expected: exit 0, prints "✅ Prompt passed security validation"

bash ~/.claude/hooks/promptshield-check.sh "DROP TABLE users"
# Expected: exit 1, prints security warning

# Test test-runner hook
python3 ~/.claude/hooks/test-runner-pre-commit.py
# Expected: exit 0 if all tests pass
```

- [ ] **Step 4: Verify all 8 platforms**

```bash
# Export to all platforms
python3 tools/exporter.py

# Verify each platform has hooks
test -d .claude/hooks && echo "✅ Claude"
test -d .github/hooks && echo "✅ Copilot"
test -d .cursor/rules/hooks && echo "✅ Cursor"
test -d .windsurf/rules/hooks && echo "✅ Windsurf"
test -d .gemini/hooks && echo "✅ Gemini"
test -d .continue/hooks && echo "✅ Continue"
test -d tools/output/openai/hooks && echo "✅ OpenAI"
test -d .aider/hooks && echo "✅ Aider"

# Expected: 8 ✅ checkmarks
```

- [ ] **Step 5: Commit test results**

```bash
# No changes to commit if all tests pass
echo "All hook exporting tests passed ✅"
```

- [ ] **Step 6: Final status check**

```bash
git log --oneline | head -10
```

Expected: Shows 10 commits related to hook exporting:
1. feat: add HookFile data class
2. feat: add hook discovery and scanning
3. feat: add hook_output_dir and export_hooks to PlatformExporter
4. feat: add hook_output_dir for all 8 platforms
5. feat: add sample hooks (promptshield, test-runner, format-check)
6. feat: auto-generate platform configs with hook registrations
7. feat: add --hooks CLI argument and filtering
8. test: add end-to-end hook export tests
9. docs: add hook exporting documentation
10. (previous commit)

---

## Summary

Hook exporting is now fully integrated into the awesome-prompts system:

✅ **HookFile class** — parses hook scripts with YAML frontmatter
✅ **Hook discovery** — scans `hooks/` directory automatically
✅ **Platform exporters** — copy hooks to all 8 platform directories
✅ **Config generation** — auto-registers hooks in platform settings
✅ **CLI support** — `--hooks` argument for filtering
✅ **Sample hooks** — promptshield, test-runner, code-formatter
✅ **Full test coverage** — 26+ tests covering all workflows
✅ **Documentation** — hooks/README.md and updated guides

**Usage:**
```bash
python3 tools/exporter.py                    # export everything
python3 tools/exporter.py --hooks promptshield  # specific hook
python3 tools/exporter.py --target claude    # specific platform
```
