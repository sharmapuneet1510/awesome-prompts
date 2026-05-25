#!/usr/bin/env python3
"""
test_exporter.py — Test suite for HookFile data class.

Tests:
1. test_hookfile_from_path_valid() — parse valid hook with all fields
2. test_hookfile_missing_hook_type() — raise error when hook_type missing
3. test_hookfile_defaults_to_claude() — applies_to defaults to ["claude"]
"""

import tempfile
from pathlib import Path

from exporter import HookFile


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


if __name__ == "__main__":
    test_hookfile_from_path_valid()
    test_hookfile_missing_hook_type()
    test_hookfile_defaults_to_claude()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("✓ All 3 tests PASSED")
    print("=" * 70)
