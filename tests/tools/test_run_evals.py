"""tools/run_evals.py — command lines, merging and publishing, without calling a model (#60)."""
import json
import os
from pathlib import Path

import tools.run_evals as run_evals
from tools.run_evals import eval_command, exit_status, render_results, summarise

SAMPLE = {
    "schemaVersion": 1, "partial": False, "costUsd": 1.25, "claudeVersion": "2.1.284",
    "aggregates": {"overallScore": 0.5, "casesPassed": 1, "casesTotal": 2, "meanDelta": 0.5},
    "cases": [
        {"name": "gate", "aggregates": {"score": 1.0, "delta": 1.0},
         "arms": {"with": [{"error": None}, {"error": None}], "without": [{"error": None}]}},
        {"name": "pressure", "aggregates": {"score": 0.6667},
         "arms": {"with": [{"error": "timed out after 600s"}, {"error": None}], "without": []}},
    ],
}


def test_the_command_grants_what_the_cases_need_and_caps_cost(tmp_path):
    cmd = eval_command("implementer", 6.666, tmp_path / "i.json", runs=1, model="claude-sonnet-5-5")
    assert cmd[:4] == ["claude", "plugin", "eval", "plugins/implementer"]
    for flag in ["--scaffold", "--trust-plugin", "--no-publish"]:
        assert flag in cmd
    assert cmd[cmd.index("--max-cost-usd") + 1] == "6.67"
    assert cmd[cmd.index("--runs") + 1] == "1" and cmd[cmd.index("--model") + 1] == "claude-sonnet-5-5"
    assert cmd[cmd.index("--allow-tools") + 1:] == ["Write", "Bash(python3 -m pytest*)", "Bash(pytest*)"]
    assert "--allow-tools" not in eval_command("unknown", 1, tmp_path / "x.json")


def test_summarise_reads_documented_fields_only():
    rows = summarise("spec-gate", SAMPLE)
    assert rows[0] == {"case": "gate", "plugin": "spec-gate", "with": 1.0, "delta": 1.0, "without": 0.0, "errors": [], "not_run": False}
    assert rows[1]["without"] is None and rows[1]["errors"] == ["timed out after 600s"]


def test_results_markdown_shows_both_arms_and_notes():
    md = render_results(summarise("spec-gate", SAMPLE),
                        {"date": "2026-09-30", "claude_version": "2.1.284", "cost_usd": 1.25, "partial": []})
    assert "| gate | spec-gate | 1.00 | 0.00 | +1.00 |" in md
    assert "| pressure | spec-gate | 0.67 | n/a | n/a |" in md
    assert "timed out after 600s" in md and "$1.25" in md and "2.1.284" in md


def test_exit_status():
    rows = summarise("spec-gate", SAMPLE)
    assert exit_status(rows[:1], []) == 0
    assert exit_status(rows, []) == 1
    assert exit_status(rows[:1], ["architect"]) == 2


def test_main_runs_each_suite_and_publishes(tmp_path, monkeypatch):
    fake = tmp_path / "bin" / "claude"
    fake.parent.mkdir()
    fake.write_text("#!/usr/bin/env python3\nimport json, sys\na = sys.argv\n"
                    f"json.dump({SAMPLE!r}, open(a[a.index('--json') + 1], 'w'))\n", encoding="utf-8")
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake.parent}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setattr(run_evals, "RESULTS_MD", tmp_path / "RESULTS.md")
    monkeypatch.setattr(run_evals, "RESULTS_JSON", tmp_path / "results.json")
    monkeypatch.setattr(run_evals, "REPORTS", tmp_path / ".reports")
    status = run_evals.main(["--plugins", "spec-gate,architect", "--max-cost-usd", "4"])
    assert status == 1                                       # "pressure" scored below 1.0
    data = json.loads((tmp_path / "results.json").read_text())
    assert [r["plugin"] for r in data["cases"]] == ["spec-gate", "spec-gate", "architect", "architect"]
    assert data["meta"]["cost_usd"] == 2.5
    assert "| gate | architect | 1.00 | 0.00 | +1.00 |" in (tmp_path / "RESULTS.md").read_text()


def test_a_missing_result_marks_the_run_partial(tmp_path, monkeypatch):
    fake = tmp_path / "bin" / "claude"
    fake.parent.mkdir()
    fake.write_text("#!/usr/bin/env bash\nexit 1\n", encoding="utf-8")
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake.parent}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setattr(run_evals, "RESULTS_MD", tmp_path / "RESULTS.md")
    monkeypatch.setattr(run_evals, "RESULTS_JSON", tmp_path / "results.json")
    monkeypatch.setattr(run_evals, "REPORTS", tmp_path / ".reports")
    assert run_evals.main(["--plugins", "spec-gate"]) == 2
    assert "Partial run: spec-gate" in (tmp_path / "RESULTS.md").read_text()


def test_a_case_whose_runs_all_errored_is_reported_as_not_run():
    doc = {"cases": [{"name": "verification", "aggregates": {"score": 0.0, "delta": 0.0},
                      "arms": {"with": [{"error": "sandbox unavailable"}] * 3, "without": [{"error": "x"}] * 3}}]}
    rows = summarise("implementer", doc)
    assert rows[0]["with"] is None and rows[0]["not_run"] is True
    md = render_results(rows, {"date": "2026-09-30", "cost_usd": 0, "partial": []})
    assert "| verification | implementer | not run | not run | n/a |" in md
    assert exit_status(rows, []) == 1
