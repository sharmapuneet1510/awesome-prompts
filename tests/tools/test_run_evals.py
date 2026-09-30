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
    assert cmd[cmd.index("--allow-tools") + 1:] == ["Bash(python3 -m pytest*)", "Bash(pytest*)"]
    assert "--allow-tools" not in eval_command("unknown", 1, tmp_path / "x.json")


def test_summarise_reads_documented_fields_only():
    rows = summarise("spec-gate", SAMPLE)
    assert rows[0] == {"case": "gate", "plugin": "spec-gate", "with": 1.0, "delta": 1.0, "without": 0.0, "errors": [], "not_run": False, "command": False}
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
    monkeypatch.setattr(run_evals, "expected_cases", lambda plugin: {"gate", "pressure"})   # the fake's cases
    monkeypatch.setattr(run_evals, "command_cases", lambda plugin: set())
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


# ── review fixes (#60 final review) ────────────────────────────────────────────

def _fake_claude(tmp_path, body: str):
    fake = tmp_path / "bin" / "claude"
    fake.parent.mkdir(exist_ok=True)
    fake.write_text("#!/usr/bin/env python3\nimport json, sys\na = sys.argv\nout = a[a.index('--json') + 1]\n" + body,
                    encoding="utf-8")
    fake.chmod(0o755)
    return fake


def _point_outputs(tmp_path, monkeypatch, fake):
    monkeypatch.setenv("PATH", f"{fake.parent}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setattr(run_evals, "RESULTS_MD", tmp_path / "RESULTS.md")
    monkeypatch.setattr(run_evals, "RESULTS_JSON", tmp_path / "results.json")
    monkeypatch.setattr(run_evals, "REPORTS", tmp_path / ".reports")


def test_a_stale_result_is_never_republished(tmp_path, monkeypatch):
    fake = _fake_claude(tmp_path, "sys.exit(1)\n")                     # crashes, writes nothing
    _point_outputs(tmp_path, monkeypatch, fake)
    (tmp_path / ".reports").mkdir()
    (tmp_path / ".reports" / "spec-gate.json").write_text(json.dumps(SAMPLE))   # left over from an earlier run
    assert run_evals.main(["--plugins", "spec-gate"]) == 2
    assert "Partial run" in (tmp_path / "RESULTS.md").read_text()


def test_exit_1_with_every_case_passing_means_a_case_failed_to_load(tmp_path, monkeypatch):
    passing = {**SAMPLE, "cases": SAMPLE["cases"][:1]}
    fake = _fake_claude(tmp_path, f"json.dump({passing!r}, open(out, 'w'))\nsys.exit(1)\n")
    _point_outputs(tmp_path, monkeypatch, fake)
    assert run_evals.main(["--plugins", "spec-gate"]) == 2


def test_an_empty_suite_is_partial(tmp_path, monkeypatch):
    empty = {**SAMPLE, "cases": []}
    fake = _fake_claude(tmp_path, f"json.dump({empty!r}, open(out, 'w'))\n")
    _point_outputs(tmp_path, monkeypatch, fake)
    assert run_evals.main(["--plugins", "spec-gate"]) == 2


def test_a_missing_claude_or_bad_json_is_partial_not_a_crash(tmp_path, monkeypatch):
    fake = _fake_claude(tmp_path, "open(out, 'w').write('{not json')\n")
    _point_outputs(tmp_path, monkeypatch, fake)
    assert run_evals.main(["--plugins", "spec-gate"]) == 2
    monkeypatch.setenv("PATH", str(tmp_path / "empty-bin"))           # no claude at all
    assert run_evals.main(["--plugins", "spec-gate"]) == 2


def test_baseline_errors_are_not_counted_as_a_plugin_effect():
    doc = {"cases": [{"name": "gate", "aggregates": {"score": 1.0, "delta": 1.0},
                      "arms": {"with": [{"error": None, "turns": 5}],
                               "without": [{"error": "rate limit", "turns": 0}] * 3}}]}
    row = summarise("spec-gate", doc)[0]
    assert row["without"] is None and row["delta"] is None
    assert "rate limit" in render_results([row], {"date": "d", "cost_usd": 0, "partial": []})


def test_runs_that_started_and_hit_a_limit_keep_their_score():
    doc = {"cases": [{"name": "gate", "aggregates": {"score": 0.33, "delta": 0.0},
                      "arms": {"with": [{"error": "reached max_turns", "turns": 20}] * 3, "without": []}}]}
    row = summarise("spec-gate", doc)[0]
    assert row["not_run"] is False and row["with"] == 0.33


def test_command_cases_report_no_delta():
    doc = {"cases": [{"name": "citations", "aggregates": {"score": 1.0, "delta": 0.67},
                      "arms": {"with": [{"error": None, "turns": 9}], "without": [{"error": None, "turns": 4}]}}]}
    row = summarise("architect", doc, command_cases={"citations"})[0]
    assert row["with"] == 1.0 and row["delta"] is None and row["command"] is True
    md = render_results([row], {"date": "d", "cost_usd": 0, "partial": []})
    assert "| citations | architect | 1.00 | n/a (command) | n/a |" in md


def test_unspent_budget_carries_to_the_next_suite(tmp_path, monkeypatch):
    fake = _fake_claude(tmp_path, "a2 = sys.argv\nceiling = a2[a2.index('--max-cost-usd') + 1]\n"
                                  "open(out + '.ceiling', 'w').write(ceiling)\n"
                                  f"json.dump({{**{SAMPLE!r}, 'costUsd': 0.0}}, open(out, 'w'))\n")
    _point_outputs(tmp_path, monkeypatch, fake)
    monkeypatch.setattr(run_evals, "expected_cases", lambda plugin: {"gate", "pressure"})
    run_evals.main(["--plugins", "implementer,spec-gate", "--max-cost-usd", "6"])
    ceilings = [(tmp_path / ".reports" / f"{p}.json.ceiling").read_text() for p in ["implementer", "spec-gate"]]
    assert ceilings == ["3.00", "6.00"]              # the first suite spent nothing, so the second gets it all
