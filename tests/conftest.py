"""Pytest configuration and fixtures"""

import sys
import os

# Add repo root to path for module imports
repo_root = os.path.dirname(os.path.dirname(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Add tools/token-optimizer to path for package imports
token_opt_dir = os.path.join(repo_root, "tools", "token-optimizer")
if token_opt_dir not in sys.path:
    sys.path.insert(0, token_opt_dir)

# Also add tools directory
tools_dir = os.path.join(repo_root, "tools")
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
