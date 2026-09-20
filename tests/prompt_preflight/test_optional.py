"""R1 / R14: the feature is optional by construction and leaves no trace unless it is configured."""
import subprocess
import sys
from pathlib import Path

COVERS = ["R1", "R14"]

TOOLS = Path(__file__).resolve().parents[2] / "tools"
REPO = TOOLS.parent
NAMES = ("prompt_preflight", "prompt-preflight", "PROMPT_PREFLIGHT", "Prompt Preflight")


def test_the_default_export_carries_nothing_of_the_feature(tmp_path):
    done = subprocess.run(
        [sys.executable, str(TOOLS / "exporter.py"), "--target", "claude", "--target-project", str(tmp_path)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert done.returncode == 0, done.stderr[-500:]
    files = [p for p in tmp_path.rglob("*") if p.is_file()]
    assert files, "the export must copy something, or this test proves nothing"
    assert [p.name for p in files if "preflight" in p.name.lower()] == []
    leaking = [p.name for p in files if any(name in p.read_text(encoding="utf-8", errors="ignore") for name in NAMES)]
    assert leaking == []
    assert not list(tmp_path.rglob("settings*.json"))  # the export never edits any settings file


def test_nothing_in_the_hooks_directory_belongs_to_the_feature():
    hooks = REPO / "hooks"
    names = [p.name for p in hooks.iterdir()] if hooks.exists() else []
    assert [n for n in names if "preflight" in n.lower()] == []


def test_only_the_interactive_exporter_mentions_the_feature_among_the_tools_scripts():
    mentions = sorted(p.name for p in TOOLS.glob("*.py") if "prompt_preflight" in p.read_text(encoding="utf-8", errors="ignore"))
    assert mentions == ["interactive_exporter.py"]
