"""tools/skill_validator.py validates skill files, not the directory's README (#61)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_validator_ignores_readme_and_passes_on_the_repo():
    result = subprocess.run([sys.executable, "tools/skill_validator.py"], cwd=ROOT,
                            capture_output=True, text=True)
    assert "README" not in result.stdout
    assert result.returncode == 0, result.stdout[-2000:]
