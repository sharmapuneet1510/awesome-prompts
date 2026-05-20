#!/usr/bin/env python3
"""
python_detect.py — Python runtime detection utility

Detects available Python executable and handles cross-platform compatibility.

Usage:
    from python_detect import get_python_cmd, run_script

    # Get the Python command
    python_cmd = get_python_cmd()

    # Or run a script directly
    run_script("exporter.py", ["--interactive"])
"""

import subprocess
import sys
import shutil
from pathlib import Path
from typing import Optional, List


def get_python_cmd() -> str:
    """
    Detect available Python executable.

    Returns:
        Command to use for Python: 'python3', 'python', or 'py' (Windows)

    Raises:
        RuntimeError: If no Python 3 executable found
    """
    # Try python3 first (standard on Unix/Linux/macOS)
    if shutil.which("python3"):
        return "python3"

    # Try python (Windows, or system aliased to Python 3)
    if shutil.which("python"):
        return "python"

    # Try py (Windows launcher)
    if shutil.which("py"):
        return "py"

    # No Python found
    raise RuntimeError(
        "Python 3 is required but not found.\n"
        "Please install Python 3 from https://www.python.org/"
    )


def run_script(
    script: str,
    args: Optional[List[str]] = None,
    cwd: Optional[Path] = None,
) -> int:
    """
    Run a Python script with detected Python executable.

    Args:
        script: Name of script to run (e.g., 'exporter.py')
        args: Optional list of arguments to pass to script
        cwd: Optional working directory

    Returns:
        Exit code from the script
    """
    python_cmd = get_python_cmd()
    cmd = [python_cmd, script]

    if args:
        cmd.extend(args)

    try:
        result = subprocess.run(cmd, cwd=cwd)
        return result.returncode
    except Exception as e:
        print(f"Error running script: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    # Print detected Python command
    try:
        python_cmd = get_python_cmd()
        print(f"Detected Python: {python_cmd}")
        print(f"Version: ", end="", flush=True)
        subprocess.run([python_cmd, "--version"])
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
