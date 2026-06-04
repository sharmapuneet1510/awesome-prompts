"""Pytest configuration and fixtures"""

import sys
import os

# Add tools/token-optimizer to path for package imports
repo_root = os.path.dirname(os.path.dirname(__file__))
token_opt_dir = os.path.join(repo_root, "tools", "token-optimizer")
if token_opt_dir not in sys.path:
    sys.path.insert(0, token_opt_dir)

# Also add tools directory
tools_dir = os.path.join(repo_root, "tools")
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
