#!/bin/bash
# python-detect.sh — Detect and run Python (cross-platform)
# Works with both 'python' and 'python3' depending on what's available

# Try python3 first, then python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 is required but not found."
    echo "Please install Python 3 from https://www.python.org/"
    exit 1
fi

# Run the requested script with the detected Python
"$PYTHON_CMD" "$@"
