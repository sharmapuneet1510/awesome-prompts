"""The eval fixture and the scaffold scripts that recreate it (#60)."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

from tools.build_eval_scaffolds import FIXTURE, render_scaffold

ROOT = Path(__file__).resolve().parents[1]


def _files(folder: Path) -> dict[str, str]:
    return {p.relative_to(folder).as_posix(): p.read_text(encoding="utf-8")
            for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts
            and ".pytest_cache" not in p.parts}


def test_the_scaffold_recreates_the_fixture_exactly(tmp_path):
    script = tmp_path / "scaffold.sh"
    script.write_text(render_scaffold(FIXTURE), encoding="utf-8")
    work = tmp_path / "workspace"
    work.mkdir()
    subprocess.run(["bash", str(script)], cwd=work, check=True)
    assert _files(work) == _files(FIXTURE)


def test_the_fixture_has_exactly_one_failing_test(tmp_path):
    copy = tmp_path / "orders-service"
    shutil.copytree(FIXTURE, copy)
    done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=copy,
                          capture_output=True, text=True)
    assert "1 failed, 2 passed" in done.stdout, done.stdout


def test_the_fixture_opts_in_to_spec_gate_and_has_draft_specs():
    assert json.loads((FIXTURE / ".spec-gate.json").read_text())["source"] == ["src/**"]
    for name in ["requirements", "design", "tasks"]:
        assert "Status: Draft" in (FIXTURE / f"specs/checkout/{name}.md").read_text()


def test_the_fixture_never_names_the_bug():
    # Graders look for "idempoten" in Claude's own words; the fixture must not contain it.
    assert [p for p, text in _files(FIXTURE).items() if "idempoten" in text.lower()] == []


def test_every_scaffold_is_up_to_date():
    done = subprocess.run([sys.executable, "tools/build_eval_scaffolds.py", "--check"], cwd=ROOT,
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stdout
