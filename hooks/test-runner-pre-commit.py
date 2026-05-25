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
