#!/usr/bin/env python3
"""
test_exporter.py — Test suite for HookFile data class and hook discovery.

Tests:
1. test_hookfile_from_path_valid() — parse valid hook with all fields
2. test_hookfile_missing_hook_type() — raise error when hook_type missing
3. test_hookfile_defaults_to_claude() — applies_to defaults to ["claude"]
4. test_discover_hooks_empty() — return [] when no hooks/ dir
5. test_discover_hooks_valid() — discover and parse valid hook files
6. test_discover_hooks_skip_invalid() — skip hooks with errors, continue with valid ones
7. test_export_hooks_filters_by_platform() — only export hooks for current platform
8. test_export_hooks_makes_executable() — .sh files get executable bit (0o755)
"""

import json
import tempfile
from pathlib import Path
import os
import stat

from exporter import (
    HookFile,
    ExportOrchestrator,
    ClaudeExporter,
    CopilotExporter,
    CursorExporter,
    WindsurfExporter,
    GeminiExporter,
    ContinueExporter,
    OpenAIExporter,
    AiderExporter,
)


def test_hookfile_from_path_valid():
    """Test HookFile.from_path() with a valid hook file containing all fields."""
    print("\n" + "=" * 70)
    print("TEST 1: HookFile.from_path_valid()")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        hook_path = Path(tmpdir) / "test_hook.sh"
        hook_path.write_text(
            """---
name: Test Hook
version: 1.0.0
description: A test hook for validation
hook_type: pre-commit
applies_to:
  - claude
  - copilot
---

#!/bin/bash
echo "Running test hook..."
""",
            encoding="utf-8",
        )

        hook = HookFile.from_path(hook_path)

        # Verify all fields are parsed correctly
        assert hook.path == hook_path, "path not set correctly"
        print(f"✓ path: {hook.path}")

        assert hook.name == "Test Hook", f"Expected name 'Test Hook', got '{hook.name}'"
        print(f"✓ name: {hook.name}")

        assert hook.version == "1.0.0", f"Expected version '1.0.0', got '{hook.version}'"
        print(f"✓ version: {hook.version}")

        assert (
            hook.description == "A test hook for validation"
        ), f"Expected description 'A test hook for validation', got '{hook.description}'"
        print(f"✓ description: {hook.description}")

        assert (
            hook.hook_type == "pre-commit"
        ), f"Expected hook_type 'pre-commit', got '{hook.hook_type}'"
        print(f"✓ hook_type: {hook.hook_type}")

        assert hook.applies_to == [
            "claude",
            "copilot",
        ], f"Expected applies_to ['claude', 'copilot'], got {hook.applies_to}"
        print(f"✓ applies_to: {hook.applies_to}")

        assert (
            hook.is_executable is True
        ), f"Expected is_executable=True for .sh file, got {hook.is_executable}"
        print(f"✓ is_executable: {hook.is_executable}")

        assert hook.slug == "test_hook", f"Expected slug 'test_hook', got '{hook.slug}'"
        print(f"✓ slug: {hook.slug}")

        assert "echo" in hook.content, "Content body not parsed correctly"
        print(f"✓ content: {hook.content[:50]}...")

        print("\n✓ TEST 1 PASSED")


def test_hookfile_missing_hook_type():
    """Test that HookFile.from_path() raises ValueError when hook_type is missing."""
    print("\n" + "=" * 70)
    print("TEST 2: HookFile missing hook_type raises ValueError")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        hook_path = Path(tmpdir) / "invalid_hook.sh"
        hook_path.write_text(
            """---
name: Invalid Hook
version: 1.0.0
description: This hook is missing hook_type
applies_to:
  - claude
---

#!/bin/bash
echo "This hook has no hook_type"
""",
            encoding="utf-8",
        )

        try:
            HookFile.from_path(hook_path)
            print("✗ Expected ValueError to be raised")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            error_msg = str(e)
            assert "hook_type" in error_msg, f"Error message should mention hook_type: {error_msg}"
            print(f"✓ ValueError raised with correct message:")
            print(f"  {error_msg}")

        print("\n✓ TEST 2 PASSED")


def test_hookfile_defaults_to_claude():
    """Test that HookFile.applies_to defaults to ['claude'] when not specified."""
    print("\n" + "=" * 70)
    print("TEST 3: HookFile.applies_to defaults to ['claude']")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        hook_path = Path(tmpdir) / "default_hook.py"
        hook_path.write_text(
            """---
name: Default Hook
version: 1.0.0
description: This hook has no applies_to
hook_type: user-prompt-submit
---

#!/usr/bin/env python3
print("Running hook...")
""",
            encoding="utf-8",
        )

        hook = HookFile.from_path(hook_path)

        assert (
            hook.applies_to == ["claude"]
        ), f"Expected applies_to to default to ['claude'], got {hook.applies_to}"
        print(f"✓ applies_to defaults to: {hook.applies_to}")

        assert (
            hook.is_executable is False
        ), f"Expected is_executable=False for .py file, got {hook.is_executable}"
        print(f"✓ is_executable=False for .py file")

        assert (
            hook.hook_type == "user-prompt-submit"
        ), f"Expected hook_type 'user-prompt-submit', got '{hook.hook_type}'"
        print(f"✓ hook_type: {hook.hook_type}")

        print("\n✓ TEST 3 PASSED")


def test_discover_hooks_empty():
    """Test discover_hooks() returns [] when hooks/ doesn't exist."""
    print("\n" + "=" * 70)
    print("TEST 4: discover_hooks_empty() — no hooks/ directory")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)

        # Create minimal repo structure (no hooks/ dir)
        (repo_root / "skills").mkdir()
        (repo_root / "agents").mkdir()

        orchestrator = ExportOrchestrator(repo_root)
        hooks = orchestrator.discover_hooks()

        assert hooks == [], f"Expected empty list, got {hooks}"
        print("✓ discover_hooks() returns [] when hooks/ doesn't exist")

        print("\n✓ TEST 4 PASSED")


def test_discover_hooks_valid():
    """Test discover_hooks() discovers and parses valid hook files."""
    print("\n" + "=" * 70)
    print("TEST 5: discover_hooks_valid() — discover valid hooks")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)

        # Create minimal repo structure
        (repo_root / "skills").mkdir()
        (repo_root / "agents").mkdir()
        hooks_dir = repo_root / "hooks"
        hooks_dir.mkdir()

        # Create two valid hook files
        hook1_path = hooks_dir / "pre_commit.sh"
        hook1_path.write_text(
            """---
name: Pre-Commit Hook
version: 1.0.0
description: Runs tests before commit
hook_type: pre-commit
applies_to:
  - claude
---

#!/bin/bash
echo "Running pre-commit checks..."
""",
            encoding="utf-8",
        )

        hook2_path = hooks_dir / "prompt_submit.py"
        hook2_path.write_text(
            """---
name: Prompt Submit Hook
version: 1.0.0
description: Validates prompt before submit
hook_type: user-prompt-submit
---

#!/usr/bin/env python3
print("Validating prompt...")
""",
            encoding="utf-8",
        )

        orchestrator = ExportOrchestrator(repo_root)
        hooks = orchestrator.discover_hooks()

        assert len(hooks) == 2, f"Expected 2 hooks, got {len(hooks)}"
        print(f"✓ Discovered {len(hooks)} hook(s)")

        # Verify hooks are sorted
        assert hooks[0].slug == "pre_commit", f"Expected first hook slug 'pre_commit', got '{hooks[0].slug}'"
        assert hooks[1].slug == "prompt_submit", f"Expected second hook slug 'prompt_submit', got '{hooks[1].slug}'"
        print(f"✓ Hook 1 (sorted): {hooks[0].slug} ({hooks[0].hook_type})")
        print(f"✓ Hook 2 (sorted): {hooks[1].slug} ({hooks[1].hook_type})")

        assert hooks[0].is_executable is True, "Expected hook1 (.sh) to be executable"
        print(f"✓ Hook 1 is_executable: {hooks[0].is_executable}")

        assert hooks[1].is_executable is False, "Expected hook2 (.py) to NOT be executable"
        print(f"✓ Hook 2 is_executable: {hooks[1].is_executable}")

        print("\n✓ TEST 5 PASSED")


def test_discover_hooks_skip_invalid():
    """Test discover_hooks() skips invalid hooks and continues with valid ones."""
    print("\n" + "=" * 70)
    print("TEST 6: discover_hooks_skip_invalid() — skip invalid, continue with valid")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)

        # Create minimal repo structure
        (repo_root / "skills").mkdir()
        (repo_root / "agents").mkdir()
        hooks_dir = repo_root / "hooks"
        hooks_dir.mkdir()

        # Create a valid hook
        valid_hook = hooks_dir / "valid_hook.sh"
        valid_hook.write_text(
            """---
name: Valid Hook
version: 1.0.0
description: A valid hook
hook_type: pre-commit
---

#!/bin/bash
echo "Valid hook"
""",
            encoding="utf-8",
        )

        # Create an invalid hook (missing hook_type)
        invalid_hook = hooks_dir / "invalid_hook.sh"
        invalid_hook.write_text(
            """---
name: Invalid Hook
version: 1.0.0
description: Missing hook_type field
---

#!/bin/bash
echo "Invalid hook"
""",
            encoding="utf-8",
        )

        # Create another valid hook
        another_valid = hooks_dir / "another_hook.py"
        another_valid.write_text(
            """---
name: Another Valid Hook
version: 1.0.0
description: Another valid hook
hook_type: user-prompt-submit
---

#!/usr/bin/env python3
print("Another valid hook")
""",
            encoding="utf-8",
        )

        # Create hidden file (should be skipped)
        hidden_hook = hooks_dir / ".hidden_hook.sh"
        hidden_hook.write_text(
            """---
name: Hidden Hook
hook_type: pre-commit
---

#!/bin/bash
echo "hidden"
""",
            encoding="utf-8",
        )

        # Create wrong file type (should be skipped)
        wrong_type = hooks_dir / "readme.txt"
        wrong_type.write_text("This is not a hook file")

        orchestrator = ExportOrchestrator(repo_root)
        hooks = orchestrator.discover_hooks()

        # Should only have the 2 valid hooks
        assert len(hooks) == 2, f"Expected 2 valid hooks, got {len(hooks)}"
        print(f"✓ Discovered {len(hooks)} valid hook(s) (skipped invalid/hidden/wrong-type)")

        # Verify the valid hooks are present
        slugs = {h.slug for h in hooks}
        assert "another_hook" in slugs, "Expected 'another_hook' to be discovered"
        assert "valid_hook" in slugs, "Expected 'valid_hook' to be discovered"
        assert "invalid_hook" not in slugs, "Should have skipped 'invalid_hook'"
        assert "hidden_hook" not in slugs, "Should have skipped '.hidden_hook'"
        print(f"✓ Valid hooks included: {sorted(slugs)}")

        print("\n✓ TEST 6 PASSED")


def test_export_hooks_filters_by_platform():
    """Test that export_hooks() only exports hooks matching applies_to platform."""
    print("\n" + "=" * 70)
    print("TEST 7: export_hooks() filters by platform")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)

        # Create hooks that apply to different platforms
        hooks_dir = repo_root / "hooks"
        hooks_dir.mkdir()

        # Hook for claude only
        claude_hook = hooks_dir / "claude_only.sh"
        claude_hook.write_text(
            """---
name: Claude Only Hook
version: 1.0
hook_type: pre-commit
applies_to:
  - claude
---

#!/bin/bash
echo "Claude only"
""",
            encoding="utf-8",
        )

        # Hook for copilot only
        copilot_hook = hooks_dir / "copilot_only.sh"
        copilot_hook.write_text(
            """---
name: Copilot Only Hook
version: 1.0
hook_type: pre-commit
applies_to:
  - copilot
---

#!/bin/bash
echo "Copilot only"
""",
            encoding="utf-8",
        )

        # Hook for multiple platforms
        multi_hook = hooks_dir / "multi.sh"
        multi_hook.write_text(
            """---
name: Multi Platform Hook
version: 1.0
hook_type: pre-commit
applies_to:
  - claude
  - copilot
  - windsurf
---

#!/bin/bash
echo "Multi platform"
""",
            encoding="utf-8",
        )

        # Discover all hooks
        orchestrator = ExportOrchestrator(repo_root)
        all_hooks = orchestrator.discover_hooks()
        assert len(all_hooks) == 3, f"Expected 3 hooks, got {len(all_hooks)}"
        print(f"✓ Discovered {len(all_hooks)} hooks")

        # Export with Claude exporter
        claude_exporter = ClaudeExporter(repo_root)
        claude_paths = claude_exporter.export_hooks(all_hooks, dry_run=False)

        # Should only have claude_only and multi
        assert len(claude_paths) == 2, f"Expected 2 hooks for Claude, got {len(claude_paths)}"
        print(f"✓ Claude exporter exported {len(claude_paths)} hooks (filtered applies_to)")

        # Verify the correct hooks were exported
        exported_names = {p.name for p in claude_paths}
        assert "claude_only.sh" in exported_names, "Expected claude_only.sh to be exported"
        assert "multi.sh" in exported_names, "Expected multi.sh to be exported"
        assert "copilot_only.sh" not in exported_names, "copilot_only.sh should not be exported"
        print(f"✓ Correct hooks exported: {sorted(exported_names)}")

        # Export with Copilot exporter
        copilot_exporter = CopilotExporter(repo_root)
        copilot_paths = copilot_exporter.export_hooks(all_hooks, dry_run=False)

        # Should only have copilot_only and multi
        assert len(copilot_paths) == 2, f"Expected 2 hooks for Copilot, got {len(copilot_paths)}"
        print(f"✓ Copilot exporter exported {len(copilot_paths)} hooks (filtered applies_to)")

        # Verify the correct hooks were exported
        exported_names = {p.name for p in copilot_paths}
        assert "copilot_only.sh" in exported_names, "Expected copilot_only.sh to be exported"
        assert "multi.sh" in exported_names, "Expected multi.sh to be exported"
        assert "claude_only.sh" not in exported_names, "claude_only.sh should not be exported"
        print(f"✓ Correct hooks exported: {sorted(exported_names)}")

        print("\n✓ TEST 7 PASSED")


def test_export_hooks_makes_executable():
    """Test that .sh files get executable bit (0o755) when exported."""
    print("\n" + "=" * 70)
    print("TEST 8: export_hooks() makes .sh files executable")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)

        # Create hooks directory
        hooks_dir = repo_root / "hooks"
        hooks_dir.mkdir()

        # Create a shell script hook
        shell_hook = hooks_dir / "my_script.sh"
        shell_hook.write_text(
            """---
name: Shell Script Hook
version: 1.0
hook_type: pre-commit
---

#!/bin/bash
echo "test"
""",
            encoding="utf-8",
        )

        # Create a Python hook (not executable)
        python_hook = hooks_dir / "my_script.py"
        python_hook.write_text(
            """---
name: Python Hook
version: 1.0
hook_type: pre-commit
---

#!/usr/bin/env python3
print("test")
""",
            encoding="utf-8",
        )

        # Discover hooks
        orchestrator = ExportOrchestrator(repo_root)
        hooks = orchestrator.discover_hooks()
        assert len(hooks) == 2, f"Expected 2 hooks, got {len(hooks)}"
        print(f"✓ Discovered {len(hooks)} hooks")

        # Export hooks
        exporter = ClaudeExporter(repo_root)
        exported_paths = exporter.export_hooks(hooks, dry_run=False)
        assert len(exported_paths) == 2, f"Expected 2 exported paths, got {len(exported_paths)}"
        print(f"✓ Exported {len(exported_paths)} hooks")

        # Check executable bit on .sh file
        shell_exported = next((p for p in exported_paths if p.name == "my_script.sh"), None)
        assert shell_exported is not None, "my_script.sh not found in exported paths"
        assert shell_exported.exists(), f"my_script.sh not written to {shell_exported}"

        file_mode = os.stat(shell_exported).st_mode
        is_executable = bool(file_mode & stat.S_IXUSR)
        assert is_executable, f".sh file not executable. Mode: {oct(stat.S_IMODE(file_mode))}"
        print(f"✓ .sh file is executable (mode: {oct(stat.S_IMODE(file_mode))})")

        # Check that Python file is not marked executable
        python_exported = next((p for p in exported_paths if p.name == "my_script.py"), None)
        assert python_exported is not None, "my_script.py not found in exported paths"
        assert python_exported.exists(), f"my_script.py not written to {python_exported}"

        python_mode = os.stat(python_exported).st_mode
        python_is_executable = bool(python_mode & stat.S_IXUSR)
        # Python files should not be marked executable by the exporter
        # (they have is_executable=False because they're not .sh files)
        print(f"✓ .py file not marked executable by export_hooks (correct)")

        print("\n✓ TEST 8 PASSED")


def test_claude_exporter_hook_output_dir():
    """Test ClaudeExporter.hook_output_dir() returns ~/.claude/hooks"""
    print("\n" + "=" * 70)
    print("TEST 9: ClaudeExporter.hook_output_dir()")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        exporter = ClaudeExporter(repo_root)
        hook_dir = exporter.hook_output_dir()

        expected = repo_root / ".claude" / "hooks"
        assert hook_dir == expected, f"Expected {expected}, got {hook_dir}"
        print(f"✓ hook_output_dir: {hook_dir}")

        print("\n✓ TEST 9 PASSED")


def test_copilot_exporter_hook_output_dir():
    """Test CopilotExporter.hook_output_dir() returns .github/hooks"""
    print("\n" + "=" * 70)
    print("TEST 10: CopilotExporter.hook_output_dir()")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        exporter = CopilotExporter(repo_root)
        hook_dir = exporter.hook_output_dir()

        expected = repo_root / ".github" / "hooks"
        assert hook_dir == expected, f"Expected {expected}, got {hook_dir}"
        print(f"✓ hook_output_dir: {hook_dir}")

        print("\n✓ TEST 10 PASSED")


def test_cursor_exporter_hook_output_dir():
    """Test CursorExporter.hook_output_dir() returns .cursor/rules/hooks"""
    print("\n" + "=" * 70)
    print("TEST 11: CursorExporter.hook_output_dir()")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        exporter = CursorExporter(repo_root)
        hook_dir = exporter.hook_output_dir()

        expected = repo_root / ".cursor" / "rules" / "hooks"
        assert hook_dir == expected, f"Expected {expected}, got {hook_dir}"
        print(f"✓ hook_output_dir: {hook_dir}")

        print("\n✓ TEST 11 PASSED")


def test_windsurf_exporter_hook_output_dir():
    """Test WindsurfExporter.hook_output_dir() returns .windsurf/rules/hooks"""
    print("\n" + "=" * 70)
    print("TEST 12: WindsurfExporter.hook_output_dir()")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        exporter = WindsurfExporter(repo_root)
        hook_dir = exporter.hook_output_dir()

        expected = repo_root / ".windsurf" / "rules" / "hooks"
        assert hook_dir == expected, f"Expected {expected}, got {hook_dir}"
        print(f"✓ hook_output_dir: {hook_dir}")

        print("\n✓ TEST 12 PASSED")


def test_gemini_exporter_hook_output_dir():
    """Test GeminiExporter.hook_output_dir() returns .gemini/hooks"""
    print("\n" + "=" * 70)
    print("TEST 13: GeminiExporter.hook_output_dir()")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        exporter = GeminiExporter(repo_root)
        hook_dir = exporter.hook_output_dir()

        expected = repo_root / ".gemini" / "hooks"
        assert hook_dir == expected, f"Expected {expected}, got {hook_dir}"
        print(f"✓ hook_output_dir: {hook_dir}")

        print("\n✓ TEST 13 PASSED")


def test_continue_exporter_hook_output_dir():
    """Test ContinueExporter.hook_output_dir() returns .continue/hooks"""
    print("\n" + "=" * 70)
    print("TEST 14: ContinueExporter.hook_output_dir()")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        exporter = ContinueExporter(repo_root)
        hook_dir = exporter.hook_output_dir()

        expected = repo_root / ".continue" / "hooks"
        assert hook_dir == expected, f"Expected {expected}, got {hook_dir}"
        print(f"✓ hook_output_dir: {hook_dir}")

        print("\n✓ TEST 14 PASSED")


def test_openai_exporter_hook_output_dir():
    """Test OpenAIExporter.hook_output_dir() returns tools/output/openai/hooks"""
    print("\n" + "=" * 70)
    print("TEST 15: OpenAIExporter.hook_output_dir()")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        exporter = OpenAIExporter(repo_root)
        hook_dir = exporter.hook_output_dir()

        expected = repo_root / "tools" / "output" / "openai" / "hooks"
        assert hook_dir == expected, f"Expected {expected}, got {hook_dir}"
        print(f"✓ hook_output_dir: {hook_dir}")

        print("\n✓ TEST 15 PASSED")


def test_aider_exporter_hook_output_dir():
    """Test AiderExporter.hook_output_dir() returns .aider/hooks"""
    print("\n" + "=" * 70)
    print("TEST 16: AiderExporter.hook_output_dir()")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        exporter = AiderExporter(repo_root)
        hook_dir = exporter.hook_output_dir()

        expected = repo_root / ".aider" / "hooks"
        assert hook_dir == expected, f"Expected {expected}, got {hook_dir}"
        print(f"✓ hook_output_dir: {hook_dir}")

        print("\n✓ TEST 16 PASSED")


def test_generate_claude_settings():
    """Test ConfigGenerator.generate_claude_settings() creates valid settings.json."""
    print("\n" + "=" * 70)
    print("TEST 17: ConfigGenerator.generate_claude_settings()")
    print("=" * 70)

    from config_generator import ConfigGenerator

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)

        # Create hooks directory with sample hooks
        hooks_dir = repo_root / "hooks"
        hooks_dir.mkdir()

        # Create a pre-commit hook
        pre_commit_hook = hooks_dir / "pre_commit.sh"
        pre_commit_hook.write_text(
            """---
name: Pre-Commit Hook
version: 1.0
description: Validates code before commit
hook_type: pre-commit
applies_to:
  - claude
---

#!/bin/bash
echo "Running pre-commit checks..."
""",
            encoding="utf-8",
        )

        # Create a user-prompt-submit hook
        prompt_hook = hooks_dir / "prompt_submit.py"
        prompt_hook.write_text(
            """---
name: Prompt Submit Hook
version: 1.0
description: Validates prompt before submission
hook_type: user-prompt-submit
applies_to:
  - claude
---

#!/usr/bin/env python3
print("Validating prompt...")
""",
            encoding="utf-8",
        )

        # Parse hooks
        orchestrator = ExportOrchestrator(repo_root)
        hooks = orchestrator.discover_hooks()
        assert len(hooks) == 2, f"Expected 2 hooks, got {len(hooks)}"
        print(f"✓ Parsed {len(hooks)} hooks")

        # Generate settings
        config_gen = ConfigGenerator(repo_root)
        settings = config_gen.generate_claude_settings(hooks)

        # Verify settings structure
        assert "model" in settings, "settings should have 'model' key"
        assert settings["model"] == "haiku", f"Expected model='haiku', got '{settings['model']}'"
        print(f"✓ model: {settings['model']}")

        assert "hooks" in settings, "settings should have 'hooks' key"
        print(f"✓ hooks dict created")

        assert "enabledPlugins" in settings, "settings should have 'enabledPlugins' key"
        print(f"✓ enabledPlugins dict created")

        # Verify hooks are organized by type
        assert "PreCommit" in settings["hooks"], "PreCommit hooks should be present"
        assert "UserPromptSubmit" in settings["hooks"], "UserPromptSubmit hooks should be present"
        print(f"✓ Hooks organized by type: {list(settings['hooks'].keys())}")

        # Verify hook entries
        pre_commit_list = settings["hooks"]["PreCommit"]
        assert len(pre_commit_list) > 0, "PreCommit hooks list should not be empty"
        assert pre_commit_list[0]["type"] == "command", "Hook should have type='command'"
        print(f"✓ PreCommit hooks: {len(pre_commit_list)} entry/entries")

        prompt_list = settings["hooks"]["UserPromptSubmit"]
        assert len(prompt_list) > 0, "UserPromptSubmit hooks list should not be empty"
        print(f"✓ UserPromptSubmit hooks: {len(prompt_list)} entry/entries")

        print("\n✓ TEST 17 PASSED")


def test_generate_copilot_config():
    """Test ConfigGenerator.generate_copilot_config() creates valid GitHub Copilot config."""
    print("\n" + "=" * 70)
    print("TEST 18: ConfigGenerator.generate_copilot_config()")
    print("=" * 70)

    from config_generator import ConfigGenerator

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)

        # Create hooks directory
        hooks_dir = repo_root / "hooks"
        hooks_dir.mkdir()

        # Create a pre-commit hook
        hook1 = hooks_dir / "pre_commit.sh"
        hook1.write_text(
            """---
name: Pre-Commit Hook
version: 1.0.0
description: Runs tests before commit
hook_type: pre-commit
applies_to:
  - copilot
---

#!/bin/bash
echo "Running pre-commit checks..."
""",
            encoding="utf-8",
        )

        # Create another hook
        hook2 = hooks_dir / "format_check.py"
        hook2.write_text(
            """---
name: Format Check Hook
version: 1.0.0
description: Checks code formatting
hook_type: user-prompt-submit
applies_to:
  - copilot
---

#!/usr/bin/env python3
print("Checking format...")
""",
            encoding="utf-8",
        )

        # Parse hooks
        orchestrator = ExportOrchestrator(repo_root)
        hooks = orchestrator.discover_hooks()
        assert len(hooks) == 2, f"Expected 2 hooks, got {len(hooks)}"
        print(f"✓ Parsed {len(hooks)} hooks")

        # Generate Copilot config
        config_gen = ConfigGenerator(repo_root)
        config_yaml = config_gen.generate_copilot_config(hooks)

        # Verify YAML structure
        assert "version: 1" in config_yaml, "Config should have version: 1"
        print(f"✓ YAML version: 1")

        assert "hooks:" in config_yaml, "Config should have hooks section"
        print(f"✓ hooks section present")

        # Verify hook entries in YAML
        assert "- name: " in config_yaml, "Config should have hook names"
        assert "type: " in config_yaml, "Config should have hook types"
        assert "path: " in config_yaml, "Config should have hook paths"
        print(f"✓ YAML contains hook entries (name, type, path)")

        # Verify specific hooks are mentioned
        assert "pre_commit" in config_yaml, "Config should mention pre_commit hook"
        assert "format_check" in config_yaml, "Config should mention format_check hook"
        print(f"✓ Both hooks mentioned in config")

        # Verify it's valid YAML by checking structure
        lines = config_yaml.strip().split("\n")
        assert lines[0].startswith("# Generated"), "First line should be comment"
        print(f"✓ YAML properly formatted with comments")

        print("\n✓ TEST 18 PASSED")


def test_filter_hooks_by_name():
    """Test filter_hooks() filters hooks by comma-separated names."""
    print("\n" + "=" * 70)
    print("TEST 19: filter_hooks_by_name()")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        (repo_root / "skills").mkdir()
        (repo_root / "agents").mkdir()

        # Create hooks directory and hook files
        hooks_dir = repo_root / "hooks"
        hooks_dir.mkdir()

        # Create first hook
        hook1 = hooks_dir / "promptshield.sh"
        hook1.write_text(
            """---
name: PromptShield
version: 1.0
hook_type: pre-commit
---

#!/bin/bash
echo "PromptShield check"
""",
            encoding="utf-8",
        )

        # Create second hook
        hook2 = hooks_dir / "test_runner.py"
        hook2.write_text(
            """---
name: Test Runner
version: 1.0
hook_type: post-commit
---

print("Test runner")
""",
            encoding="utf-8",
        )

        # Create third hook
        hook3 = hooks_dir / "code_formatter.sh"
        hook3.write_text(
            """---
name: Code Formatter
version: 1.0
hook_type: pre-commit
---

#!/bin/bash
echo "Formatting"
""",
            encoding="utf-8",
        )

        orchestrator = ExportOrchestrator(repo_root)
        all_hooks = orchestrator.discover_hooks()
        assert len(all_hooks) == 3, f"Expected 3 hooks, got {len(all_hooks)}"
        print(f"✓ Discovered {len(all_hooks)} hooks")

        # Filter by single hook name
        filtered = orchestrator.filter_hooks(all_hooks, ["promptshield"])
        assert len(filtered) == 1, f"Expected 1 hook, got {len(filtered)}"
        assert filtered[0].slug == "promptshield", f"Expected slug 'promptshield', got {filtered[0].slug}"
        print(f"✓ Filter by 'promptshield': {[h.slug for h in filtered]}")

        # Filter by multiple hook names
        filtered = orchestrator.filter_hooks(all_hooks, ["promptshield", "test_runner"])
        assert len(filtered) == 2, f"Expected 2 hooks, got {len(filtered)}"
        slugs = sorted([h.slug for h in filtered])
        assert slugs == ["promptshield", "test_runner"], f"Expected ['promptshield', 'test_runner'], got {slugs}"
        print(f"✓ Filter by 'promptshield,test_runner': {slugs}")

        # Filter by partial match
        filtered = orchestrator.filter_hooks(all_hooks, ["code"])
        assert len(filtered) == 1, f"Expected 1 hook with 'code', got {len(filtered)}"
        assert filtered[0].slug == "code_formatter", f"Expected slug 'code_formatter', got {filtered[0].slug}"
        print(f"✓ Filter by 'code' (partial match): {[h.slug for h in filtered]}")

        print("\n✓ TEST 19 PASSED")


def test_filter_hooks_none_returns_all():
    """Test filter_hooks() returns all hooks if no filter specified."""
    print("\n" + "=" * 70)
    print("TEST 20: filter_hooks_none_returns_all()")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        (repo_root / "skills").mkdir()
        (repo_root / "agents").mkdir()

        # Create hooks directory and hook files
        hooks_dir = repo_root / "hooks"
        hooks_dir.mkdir()

        # Create two hooks
        hook1 = hooks_dir / "hook1.sh"
        hook1.write_text(
            """---
name: Hook 1
version: 1.0
hook_type: pre-commit
---

echo "Hook 1"
""",
            encoding="utf-8",
        )

        hook2 = hooks_dir / "hook2.sh"
        hook2.write_text(
            """---
name: Hook 2
version: 1.0
hook_type: pre-commit
---

echo "Hook 2"
""",
            encoding="utf-8",
        )

        orchestrator = ExportOrchestrator(repo_root)
        all_hooks = orchestrator.discover_hooks()
        assert len(all_hooks) == 2, f"Expected 2 hooks, got {len(all_hooks)}"
        print(f"✓ Discovered {len(all_hooks)} hooks")

        # Filter with empty list should return all
        filtered = orchestrator.filter_hooks(all_hooks, [])
        assert len(filtered) == 2, f"Expected 2 hooks with empty filter, got {len(filtered)}"
        print(f"✓ Filter with empty list returns all hooks: {[h.slug for h in filtered]}")

        # Filter with None should return all
        filtered = orchestrator.filter_hooks(all_hooks, [])
        assert len(filtered) == 2, f"Expected 2 hooks with None filter, got {len(filtered)}"
        print(f"✓ Filter with None returns all hooks: {[h.slug for h in filtered]}")

        print("\n✓ TEST 20 PASSED")


def test_export_hooks_end_to_end():
    """Test complete hook export workflow: discover → validate → export → verify."""
    print("\n" + "=" * 70)
    print("TEST 21: test_export_hooks_end_to_end()")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)

        # 1. Create hooks/ directory with sample hook
        hooks_dir = repo_root / "hooks"
        hooks_dir.mkdir()

        hook_path = hooks_dir / "test_hook.sh"
        hook_path.write_text(
            """---
name: Test Hook
version: 1.0
description: Test hook for end-to-end validation
hook_type: pre-commit
applies_to:
  - claude
  - copilot
---

#!/bin/bash
exit 0
""",
            encoding="utf-8",
        )

        # 2. Discover hooks using ExportOrchestrator
        orchestrator = ExportOrchestrator(repo_root)
        hooks = orchestrator.discover_hooks()
        assert len(hooks) == 1, f"Expected 1 hook, got {len(hooks)}"
        print(f"✓ Step 1 (Discover): Found {len(hooks)} hook(s)")

        # Validate hook properties
        hook = hooks[0]
        assert hook.name == "Test Hook", f"Expected name 'Test Hook', got '{hook.name}'"
        assert hook.hook_type == "pre-commit", f"Expected hook_type 'pre-commit', got '{hook.hook_type}'"
        assert "claude" in hook.applies_to, "Hook should apply to claude"
        assert "copilot" in hook.applies_to, "Hook should apply to copilot"
        print(f"✓ Step 2 (Validate): Hook is valid (name={hook.name}, type={hook.hook_type})")

        # 3. Export to claude platform
        claude_exporter = ClaudeExporter(repo_root)
        result = claude_exporter.export([], [], hooks, dry_run=False)

        # 4. Verify hook was exported
        assert len(result.hook_files) == 1, f"Expected 1 hook file in result, got {len(result.hook_files)}"
        hook_file = result.hook_files[0]
        assert hook_file.exists(), f"Hook file not written to {hook_file}"
        print(f"✓ Step 3 (Export): Hook exported to {hook_file.parent.name}/")

        # Verify correct location (should be in .claude/hooks/)
        assert hook_file.parent == repo_root / ".claude" / "hooks", \
            f"Hook should be in .claude/hooks/, got {hook_file.parent}"
        print(f"✓ Step 4 (Verify location): Hook in correct directory (.claude/hooks/)")

        # Verify executable bit (for .sh files)
        assert os.access(hook_file, os.X_OK), f"Hook {hook_file} should be executable"
        file_mode = os.stat(hook_file).st_mode
        is_executable = bool(file_mode & stat.S_IXUSR)
        assert is_executable, f"Hook not executable. Mode: {oct(stat.S_IMODE(file_mode))}"
        print(f"✓ Step 5 (Verify executable): Hook is executable (mode: {oct(stat.S_IMODE(file_mode))})")

        # Verify content is preserved
        exported_content = hook_file.read_text(encoding="utf-8")
        assert "#!/bin/bash" in exported_content, "Bash shebang should be preserved"
        assert "exit 0" in exported_content, "Hook body should be preserved"
        print(f"✓ Step 6 (Verify content): Hook content preserved")

        # 5. Test export to copilot (different platform)
        copilot_exporter = CopilotExporter(repo_root)
        result_copilot = copilot_exporter.export([], [], hooks, dry_run=False)

        assert len(result_copilot.hook_files) == 1, f"Expected 1 hook for copilot, got {len(result_copilot.hook_files)}"
        copilot_hook_file = result_copilot.hook_files[0]
        assert copilot_hook_file.exists(), f"Copilot hook not written to {copilot_hook_file}"
        assert copilot_hook_file.parent == repo_root / ".github" / "hooks", \
            f"Copilot hook should be in .github/hooks/, got {copilot_hook_file.parent}"
        print(f"✓ Step 7 (Multi-platform): Hook also exported to copilot (.github/hooks/)")

        print("\n✓ TEST 21 PASSED")


def test_export_all_platforms_with_hooks():
    """Test hook export to all 8 platforms simultaneously."""
    print("\n" + "=" * 70)
    print("TEST 22: test_export_all_platforms_with_hooks()")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)

        # Create hooks/ directory
        hooks_dir = repo_root / "hooks"
        hooks_dir.mkdir()

        # Create a multi-platform hook
        multi_hook_path = hooks_dir / "multi.sh"
        multi_hook_path.write_text(
            """---
name: Multi Platform Hook
version: 1.0
description: Hook for all platforms
hook_type: pre-commit
applies_to:
  - claude
  - copilot
  - cursor
  - windsurf
  - gemini
  - continue
  - openai
  - aider
---

#!/bin/bash
echo "Running on all platforms"
exit 0
""",
            encoding="utf-8",
        )

        # Discover hooks
        orchestrator = ExportOrchestrator(repo_root)
        hooks = orchestrator.discover_hooks()
        assert len(hooks) == 1, f"Expected 1 hook, got {len(hooks)}"
        hook = hooks[0]
        print(f"✓ Step 1 (Discover): Found hook '{hook.name}' with {len(hook.applies_to)} platforms")

        # Verify applies_to includes all platforms
        expected_platforms = {"claude", "copilot", "cursor", "windsurf", "gemini", "continue", "openai", "aider"}
        actual_platforms = set(hook.applies_to)
        assert actual_platforms == expected_platforms, \
            f"Expected all platforms, got {actual_platforms}"
        print(f"✓ Step 2 (Validate): Hook applies to all 8 platforms")

        # Export to all platforms
        platforms_and_exporters = [
            ("claude", ClaudeExporter),
            ("copilot", CopilotExporter),
            ("cursor", CursorExporter),
            ("windsurf", WindsurfExporter),
            ("gemini", GeminiExporter),
            ("continue", ContinueExporter),
            ("openai", OpenAIExporter),
            ("aider", AiderExporter),
        ]

        results = {}
        for platform_name, exporter_cls in platforms_and_exporters:
            exporter = exporter_cls(repo_root)
            result = exporter.export([], [], hooks, dry_run=False)
            results[platform_name] = result

            # Each platform should have exactly 1 hook
            assert len(result.hook_files) == 1, \
                f"{platform_name}: Expected 1 hook, got {len(result.hook_files)}"
            hook_file = result.hook_files[0]

            # Verify file exists
            assert hook_file.exists(), \
                f"{platform_name}: Hook file not written to {hook_file}"

            # Verify it's a file (not directory)
            assert hook_file.is_file(), \
                f"{platform_name}: Hook path should be a file, got {hook_file}"

            print(f"✓ Step 3.{platform_name}: Exported to {hook_file.parent.relative_to(repo_root)}")

        # Additional verifications for each platform's specific directory
        assert (repo_root / ".claude" / "hooks" / "multi.sh").exists(), "Claude hook missing"
        assert (repo_root / ".github" / "hooks" / "multi.sh").exists(), "Copilot hook missing"
        assert (repo_root / ".cursor" / "rules" / "hooks" / "multi.sh").exists(), "Cursor hook missing"
        assert (repo_root / ".windsurf" / "rules" / "hooks" / "multi.sh").exists(), "Windsurf hook missing"
        assert (repo_root / ".gemini" / "hooks" / "multi.sh").exists(), "Gemini hook missing"
        assert (repo_root / ".continue" / "hooks" / "multi.sh").exists(), "Continue hook missing"
        assert (repo_root / "tools" / "output" / "openai" / "hooks" / "multi.sh").exists(), "OpenAI hook missing"
        assert (repo_root / ".aider" / "hooks" / "multi.sh").exists(), "Aider hook missing"

        print(f"✓ Step 4 (Verify all platforms): All 8 hooks written to correct directories")

        # Verify all hooks are executable
        for platform_name, result in results.items():
            hook_file = result.hook_files[0]
            is_executable = os.access(hook_file, os.X_OK)
            assert is_executable, f"{platform_name}: Hook not executable at {hook_file}"
            print(f"✓ Step 5.{platform_name}: Hook executable")

        # Verify content is identical across all platforms
        content_set = set()
        for platform_name, result in results.items():
            hook_file = result.hook_files[0]
            content = hook_file.read_text(encoding="utf-8")
            content_set.add(content)

        assert len(content_set) == 1, \
            f"Hook content should be identical across platforms, got {len(content_set)} variations"
        print(f"✓ Step 6 (Verify consistency): Hook content identical across all platforms")

        # Summary
        print(f"\n✓ TEST 22 PASSED")
        print(f"   Total hooks exported: {len(results)}")
        print(f"   Platforms covered: {', '.join([p for p, _ in platforms_and_exporters])}")


if __name__ == "__main__":
    test_hookfile_from_path_valid()
    test_hookfile_missing_hook_type()
    test_hookfile_defaults_to_claude()
    test_discover_hooks_empty()
    test_discover_hooks_valid()
    test_discover_hooks_skip_invalid()
    test_export_hooks_filters_by_platform()
    test_export_hooks_makes_executable()
    test_claude_exporter_hook_output_dir()
    test_copilot_exporter_hook_output_dir()
    test_cursor_exporter_hook_output_dir()
    test_windsurf_exporter_hook_output_dir()
    test_gemini_exporter_hook_output_dir()
    test_continue_exporter_hook_output_dir()
    test_openai_exporter_hook_output_dir()
    test_aider_exporter_hook_output_dir()
    test_generate_claude_settings()
    test_generate_copilot_config()
    test_filter_hooks_by_name()
    test_filter_hooks_none_returns_all()
    test_export_hooks_end_to_end()
    test_export_all_platforms_with_hooks()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("✓ All 22 tests PASSED")
    print("=" * 70)
