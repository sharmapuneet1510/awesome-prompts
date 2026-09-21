#!/usr/bin/env python3
"""Prompt Preflight launcher. Installed as <scope>/prompt-preflight/hook.py by the setup wizard.

Claude Code runs this file. It puts its own folder on the import path (so the bundled
`prompt_preflight` and `token_optimizer` packages are found) and hands over to prompt_preflight.hook.
A broken install must still exit 0 and print nothing.

Not configured means completely bypassed: with no config.json beside this file it exits
immediately, before importing or writing anything.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))

if not os.path.exists(os.path.join(_ROOT, "config.json")):
    sys.exit(0)

sys.path.insert(0, _ROOT)

try:
    from prompt_preflight.hook import main

    main(_ROOT)
except Exception:  # noqa: BLE001 - never fail the user's prompt
    pass
sys.exit(0)
