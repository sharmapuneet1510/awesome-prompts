#!/bin/bash
---
name: Promptshield Security Check
version: 1.0
description: Validates user prompts for security patterns and injection attempts
hook_type: user-prompt-submit
applies_to: [claude, copilot, cursor, windsurf, gemini, continue, openai, aider]
---

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
