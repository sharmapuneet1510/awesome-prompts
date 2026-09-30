#!/usr/bin/env python3
"""Run the behavioural eval suites and publish evals/RESULTS.md.

Runs `claude plugin eval` for each plugin that has an evals/ suite, with the
no-plugin baseline, a cost ceiling, and the tool grants its cases need; then
merges the results into evals/results.json and evals/RESULTS.md.

    python3 tools/run_evals.py                       # all suites, $20 ceiling
    python3 tools/run_evals.py --max-cost-usd 5 --plugins spec-gate --runs 1

Spends model credits: local runs use your Claude login, CI uses ANTHROPIC_API_KEY.
Spec: docs/superpowers/specs/2026-09-30-behavioural-evals-design.md
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ["spec-gate", "architect", "implementer"]
# Write/Edit/Bash can only be granted per run (a case's allowed_tools can't widen them).
GRANTS = {
    "spec-gate": ["Write", "Edit"],
    "architect": ["Write"],
    "implementer": ["Bash(python3 -m pytest*)", "Bash(pytest*)"],   # read-only: the case must not change files
}
RESULTS_MD = ROOT / "evals" / "RESULTS.md"
RESULTS_JSON = ROOT / "evals" / "results.json"
REPORTS = ROOT / "evals" / ".reports"


def eval_command(plugin: str, max_cost_usd: float, json_path: Path, runs: int | None = None,
                 model: str | None = None) -> list[str]:
    """The `claude plugin eval` command line for one plugin's suite."""
    cmd = ["claude", "plugin", "eval", f"plugins/{plugin}", "--scaffold", "--trust-plugin", "--no-publish",
           "--max-cost-usd", f"{max_cost_usd:.2f}", "--output-dir", str(REPORTS / plugin),
           "--json", str(json_path)]
    if runs:
        cmd += ["--runs", str(runs)]
    if model:
        cmd += ["--model", model]
    if GRANTS.get(plugin):
        cmd += ["--allow-tools", *GRANTS[plugin]]
    return cmd


def command_cases(plugin: str) -> set[str]:
    """Cases whose prompt is a slash command: the no-plugin arm can't run it, so Δ means nothing."""
    found = set()
    for prompt in (ROOT / "plugins" / plugin / "evals").glob("*/prompt.md"):
        body = prompt.read_text(encoding="utf-8").split("---", 2)[-1].strip()
        if body.startswith("/"):
            found.add(prompt.parent.name)
    return found


def expected_cases(plugin: str) -> set[str]:
    return {p.parent.name for p in (ROOT / "plugins" / plugin / "evals").glob("*/prompt.md")}


def _never_started(runs: list[dict]) -> bool:
    """Every run errored before doing anything (e.g. the Bash sandbox refused to start)."""
    return bool(runs) and all(r.get("error") and not r.get("turns") for r in runs)


def summarise(plugin: str, doc: dict, command_cases: set[str] = frozenset()) -> list[dict]:
    """One row per case from a `--json` result document (documented fields only)."""
    rows = []
    for case in doc.get("cases", []):
        agg = case.get("aggregates", {})
        with_runs = case.get("arms", {}).get("with", [])
        without_runs = case.get("arms", {}).get("without", [])
        score, delta = agg.get("score"), agg.get("delta")
        not_run = _never_started(with_runs)
        command = case.get("name") in command_cases
        if not_run:
            score = delta = None
        if command or (without_runs and all(r.get("error") for r in without_runs)):
            delta = None                   # no usable baseline: Δ would be an artefact
        errors = [r["error"] for r in with_runs if r.get("error")]
        errors += [f"(baseline) {r['error']}" for r in without_runs if r.get("error")]
        rows.append({
            "case": case.get("name"), "plugin": plugin, "with": score, "delta": delta,
            "without": None if score is None or delta is None else round(score - delta, 4),
            "errors": errors, "not_run": not_run, "command": command,
        })
    return rows


def _fmt(value: float | None, signed: bool = False) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.2f}" if signed else f"{value:.2f}"


def render_results(rows: list[dict], meta: dict) -> str:
    """evals/RESULTS.md."""
    lines = [
        "# Behavioural eval results",
        "",
        f"Run {meta['date']} · Claude Code {meta.get('claude_version') or 'unknown'} · "
        f"model: {meta.get('model') or 'default'} · estimated cost of these runs ${meta.get('cost_usd', 0):.2f}",
        "",
        "Each case runs with its plugin and without it; **Δ** is what the plugin contributes. "
        "A case passes when every grader passes in every with-plugin run (score 1.00). "
        "Cases driven by a slash command have no Δ: without the plugin the command doesn't exist.",
        "",
        "| Case | Plugin | With plugin | Without | Δ |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        if r.get("not_run"):
            lines.append(f"| {r['case']} | {r['plugin']} | not run | not run | n/a |")
        elif r.get("command"):
            lines.append(f"| {r['case']} | {r['plugin']} | {_fmt(r['with'])} | n/a (command) | n/a |")
        else:
            lines.append(f"| {r['case']} | {r['plugin']} | {_fmt(r['with'])} | {_fmt(r['without'])} | {_fmt(r['delta'], True)} |")
    notes = [f"- `{r['case']}`: {e}" for r in rows for e in dict.fromkeys(r["errors"])]
    notes += [f"- {reason}" for reason in meta.get("partial_reasons", [])]
    if meta.get("partial"):
        notes.append(f"- Partial run: {', '.join(meta['partial'])} did not complete — see the reasons above.")
    if notes:
        lines += ["", "## Notes", "", *notes]
    lines += ["", "Per-run grader detail is in each suite's HTML report (`evals/.reports/<plugin>/`, not committed).", ""]
    return "\n".join(lines)


def exit_status(rows: list[dict], partial: list[str]) -> int:
    """2 for a partial run, 1 if any case scored below 1.0, else 0."""
    if partial:
        return 2
    return 1 if any(r["with"] is None or r["with"] < 1.0 for r in rows) else 0


def run_plugin(plugin: str, share: float, runs: int | None, model: str | None) -> tuple[list[dict], dict | None, str | None]:
    """Run one suite. Returns (rows, doc, why-partial or None)."""
    json_path = REPORTS / f"{plugin}.json"
    json_path.unlink(missing_ok=True)                  # never re-publish an earlier run's result
    try:
        done = subprocess.run(eval_command(plugin, share, json_path, runs, model), cwd=ROOT)
    except FileNotFoundError:
        return [], None, f"{plugin}: the `claude` CLI was not found"
    if not json_path.exists():
        return [], None, f"{plugin}: no result written (exit {done.returncode})"
    try:
        doc = json.loads(json_path.read_text(encoding="utf-8"))
    except ValueError as err:
        return [], None, f"{plugin}: unreadable result ({err})"
    rows = summarise(plugin, doc, command_cases(plugin))
    missing = expected_cases(plugin) - {r["case"] for r in rows}
    if doc.get("partial") or done.returncode in (2, 130, 143):
        return rows, doc, f"{plugin}: stopped early ({doc.get('partialReason') or 'exit ' + str(done.returncode)})"
    if not rows:
        return rows, doc, f"{plugin}: no cases ran"
    if missing:
        return rows, doc, f"{plugin}: cases missing from the result: {', '.join(sorted(missing))}"
    if done.returncode == 1 and all(r["with"] is not None and r["with"] >= 1.0 for r in rows):
        return rows, doc, f"{plugin}: exit 1 although every case passed (a case file probably failed to load)"
    return rows, doc, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the behavioural eval suites.")
    parser.add_argument("--max-cost-usd", type=float, default=20.0, help="ceiling for the whole run (split evenly)")
    parser.add_argument("--plugins", default=",".join(PLUGINS), help="comma-separated plugins to run")
    parser.add_argument("--runs", type=int, help="runs per case per arm (default: each case's own, 3)")
    parser.add_argument("--model", help="model for the agent under test")
    args = parser.parse_args(argv)
    plugins = [p for p in args.plugins.split(",") if p]
    if not plugins:
        parser.error("--plugins names no plugin")
    rows, partial, reasons, cost, version = [], [], [], 0.0, None
    REPORTS.mkdir(parents=True, exist_ok=True)
    for index, plugin in enumerate(plugins):
        share = max(args.max_cost_usd - cost, 0.0) / (len(plugins) - index)   # unspent budget carries forward
        print(f"== {plugin}: up to ${share:.2f}", flush=True)
        plugin_rows, doc, why = run_plugin(plugin, share, args.runs, args.model)
        rows += plugin_rows
        if doc:
            cost += doc.get("costUsd") or 0.0
            version = doc.get("claudeVersion") or version
        if why:
            partial.append(plugin)
            reasons.append(why)
    meta = {"date": datetime.date.today().isoformat(), "claude_version": version, "model": args.model,
            "cost_usd": round(cost, 2), "partial": partial, "partial_reasons": reasons}
    RESULTS_JSON.write_text(json.dumps({"meta": meta, "cases": rows}, indent=2) + "\n", encoding="utf-8")
    RESULTS_MD.write_text(render_results(rows, meta), encoding="utf-8")
    print(RESULTS_MD.read_text(encoding="utf-8"))
    return exit_status(rows, partial)


if __name__ == "__main__":
    sys.exit(main())
