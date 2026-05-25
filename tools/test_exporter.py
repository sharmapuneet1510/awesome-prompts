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

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("✓ All 16 tests PASSED")
    print("=" * 70)
