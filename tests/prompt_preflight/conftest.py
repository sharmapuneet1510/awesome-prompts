import shutil
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[2] / "tools"


@pytest.fixture
def installed_root(tmp_path):
    """A Prompt Preflight install laid out exactly as the setup wizard lays it out."""
    root = tmp_path / "prompt-preflight"
    root.mkdir()
    shutil.copytree(TOOLS / "prompt_preflight", root / "prompt_preflight", ignore=shutil.ignore_patterns("__pycache__", "eval"))
    shutil.copytree(TOOLS / "token_optimizer", root / "token_optimizer", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(TOOLS / "prompt_preflight" / "launcher.py", root / "hook.py")
    (root / "config.json").write_text("{}\n", encoding="utf-8")  # the wizard always writes one
    return root
