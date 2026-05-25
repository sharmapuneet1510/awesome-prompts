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
"""

import tempfile
from pathlib import Path

from exporter import HookFile, ExportOrchestrator


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


if __name__ == "__main__":
    test_hookfile_from_path_valid()
    test_hookfile_missing_hook_type()
    test_hookfile_defaults_to_claude()
    test_discover_hooks_empty()
    test_discover_hooks_valid()
    test_discover_hooks_skip_invalid()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("✓ All 6 tests PASSED")
    print("=" * 70)
