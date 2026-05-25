---
name: Test Hook
version: 1.0.0
description: A test hook for validation
hook_type: pre-commit
applies_to:
  - claude
  - copilot
---

#!/bin/bash
# Test hook script
echo "Running test hook..."
