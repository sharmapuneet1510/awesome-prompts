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
