"""The behavioural eval suites are well-formed and load in `claude plugin eval` (#60)."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"spec-gate": {"gate", "pressure", "self-approval"},
            "architect": {"citations", "fabrication"},
            "implementer": {"verification"}}
PROMPT_KEYS = {"schema_version", "name", "description", "tags", "plugins", "runs", "expected_outcome", "model",
               "max_turns", "timeout_seconds", "allowed_tools", "append_system_prompt", "env"}
GRADER_TYPES = {"regex", "tool_used", "tool_order", "file_exists", "llm", "baseline"}


def _front(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), path
    return yaml.safe_load(text.split("---", 2)[1]) or {}


def _cases():
    return [ROOT / "plugins" / p / "evals" / c for p, cases in EXPECTED.items() for c in sorted(cases)]


def test_the_six_cases_exist():
    for plugin, cases in EXPECTED.items():
        found = {p.parent.name for p in (ROOT / "plugins" / plugin / "evals").glob("*/prompt.md")}
        assert found == cases, plugin


def test_prompt_front_matter_uses_documented_keys():
    for case in _cases():
        fm = _front(case / "prompt.md")
        assert set(fm) <= PROMPT_KEYS, (case, set(fm) - PROMPT_KEYS)
        assert fm["runs"] == 3 and fm["max_turns"] >= 20
        assert case.joinpath("prompt.md").read_text(encoding="utf-8").split("---", 2)[2].strip()


def test_every_case_has_graders_of_known_types():
    for case in _cases():
        graders = sorted((case / "graders").glob("*.md"))
        assert graders, case
        for grader in graders:
            assert _front(grader)["type"] in GRADER_TYPES, grader


def test_every_case_builds_the_fixture():
    for case in _cases():
        spec = yaml.safe_load((case / "case.yaml").read_text(encoding="utf-8"))
        assert spec["schema_version"] == "1.1" and spec["name"] == case.name
        assert spec["context"]["scaffold_script"] == "scaffold.sh"
        assert os.access(case / "scaffold.sh", os.X_OK), case


@pytest.mark.skipif(shutil.which("claude") is None, reason="Claude Code CLI not installed")
@pytest.mark.parametrize("plugin", sorted(EXPECTED))
def test_the_suite_loads_without_spending(plugin, tmp_path):
    # A $0 ceiling loads and validates every case, then stops before the first run.
    done = subprocess.run(["claude", "plugin", "eval", f"plugins/{plugin}", "--trust-plugin", "--no-publish",
                           "--max-cost-usd", "0", "--output-dir", str(tmp_path)],
                          cwd=ROOT, capture_output=True, text=True, timeout=120)
    output = done.stdout + done.stderr
    assert "failed to load" not in output and "$0.00" in output, output[-1500:]


def test_ci_job_runs_only_on_the_label_or_by_hand():
    workflow = yaml.safe_load((ROOT / ".github/workflows/evals.yml").read_text(encoding="utf-8"))
    triggers = workflow[True] if True in workflow else workflow["on"]   # PyYAML reads `on:` as True
    assert set(triggers) == {"pull_request", "workflow_dispatch"}
    assert triggers["pull_request"]["types"] == ["labeled"]
    job = workflow["jobs"]["evals"]
    assert "run-evals" in job["if"]
    run_steps = " ".join(step.get("run", "") for step in job["steps"])
    assert "tools/run_evals.py" in run_steps and "--max-cost-usd" in run_steps


def test_readme_and_contributing_point_to_the_results():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "## Behavioural evals" in readme and "evals/RESULTS.md" in readme
    assert "run-evals" in (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")


def test_trace_graders_cannot_match_the_plugins_own_text():
    # In the with-plugin arm the trace contains the plugin's skills and reference docs, so a trace regex
    # that matches those files passes without Claude doing anything (found in the first baseline).
    import re
    for case in _cases():
        plugin = case.parent.parent
        shipped = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in plugin.rglob("*")
                            if p.is_file() and "evals" not in p.relative_to(plugin).parts)
        for grader in (case / "graders").glob("*.md"):
            fm = _front(grader)
            if fm["type"] == "regex" and fm.get("target") == "trace":
                flags = re.I if "i" in str(fm.get("flags", "")) else 0
                assert not re.search(fm["pattern"], shipped, flags), grader


def test_the_citation_judge_is_given_the_real_source():
    judge = (ROOT / "plugins/architect/evals/citations/graders/facts-match-code.md").read_text(encoding="utf-8")
    source = (ROOT / "evals/fixtures/orders-service/src/orders.py").read_text(encoding="utf-8").splitlines()
    assert all(f"{n:>2}: {line}".rstrip() in judge for n, line in enumerate(source, 1))
    assert "focus: trace" not in judge
