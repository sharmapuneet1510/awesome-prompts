"""Bake-off runner: score the whole pipeline (tier 1 + optional model) on the labeled eval set.

    python3 tools/prompt_preflight/eval/run_eval.py --baseline
    python3 tools/prompt_preflight/eval/run_eval.py --model <ollama-model> --json out.json
    python3 tools/prompt_preflight/eval/run_eval.py --table baseline.json out.json

Every eval prompt is scored as the FIRST prompt of a session (clarify and refine are allowed).
Not installed with the hook; it only measures.
"""
import argparse
import copy
import json
import math
import os
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

_TOOLS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

from prompt_preflight import ollama_client  # noqa: E402
from prompt_preflight.config import DEFAULTS  # noqa: E402
from prompt_preflight.decide import decide  # noqa: E402
from prompt_preflight.errors import ModelUnavailable  # noqa: E402

LABELS = ("google", "clarify", "refine", "pass")
ITEMS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts.jsonl")

# Approved with the spec (2026-09-20). p95_wall_ms is an estimate: measured model time + interpreter start.
THRESHOLDS = {
    "accuracy": 0.80,
    "false_google_rate": 0.05,
    "guardrail_google": 0,
    "reply_ok_rate": 0.99,
    "p95_wall_ms": 2000.0,
}
MIN_GAIN_OVER_BASELINE = 0.10  # "clearly beats tier 1 alone" = at least +10 percentage points accuracy


@dataclass
class Result:
    prompt: str
    label: str
    guardrail: bool
    predicted: str
    model_ms: Optional[float]  # None when the model was not called
    reply_failed: bool


def load_items(path: str = ITEMS_PATH) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        items = [json.loads(line) for line in handle if line.strip()]
    for item in items:
        if item.get("label") not in LABELS or not isinstance(item.get("prompt"), str):
            raise ValueError("bad eval item: %r" % (item,))
        item["guardrail"] = bool(item.get("guardrail", False))
    return items


def evaluate(items: Sequence[Dict[str, Any]], cfg: Dict[str, Any], model_call: Optional[Any]) -> List[Result]:
    results: List[Result] = []
    for item in items:
        timing: Dict[str, float] = {}

        def timed(prompt: str, _timing: Dict[str, float] = timing) -> Dict[str, Any]:
            started = time.perf_counter()
            try:
                return model_call(prompt)  # type: ignore[misc]
            finally:
                _timing["ms"] = (time.perf_counter() - started) * 1000

        failed = False
        try:
            decision = decide(item["prompt"], cfg, True, timed if model_call else None)
            predicted = decision.verdict
        except ModelUnavailable:
            failed, predicted = True, "pass"
        results.append(Result(item["prompt"], item["label"], item["guardrail"], predicted, timing.get("ms"), failed))
    return results


def _p95(values: List[float]) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)] if ordered else 0.0


def summarize(results: Sequence[Result], startup_ms: float = 0.0) -> Dict[str, Any]:
    total = len(results)
    not_google = [r for r in results if r.label != "google"]
    called = [r for r in results if r.model_ms is not None]
    p95 = _p95([r.model_ms for r in called if r.model_ms is not None])
    return {
        "n": total,
        "accuracy": sum(r.predicted == r.label for r in results) / total if total else 0.0,
        "false_google_rate": (sum(r.predicted == "google" for r in not_google) / len(not_google)) if not_google else 0.0,
        "guardrail_google": sum(r.guardrail and r.predicted == "google" for r in results),
        "reply_ok_rate": (1 - sum(r.reply_failed for r in called) / len(called)) if called else 1.0,
        "model_calls": len(called),
        "p95_model_ms": round(p95, 1),
        "p95_wall_ms": round(p95 + startup_ms, 1) if called else 0.0,
        "startup_ms": round(startup_ms, 1),
    }


def check(summary: Dict[str, Any], thresholds: Dict[str, float] = THRESHOLDS) -> List[str]:
    """Human-readable list of failed thresholds; empty means every threshold is met."""
    failures = []
    if summary["accuracy"] < thresholds["accuracy"]:
        failures.append("accuracy %.0f%% < %.0f%%" % (summary["accuracy"] * 100, thresholds["accuracy"] * 100))
    if summary["false_google_rate"] > thresholds["false_google_rate"]:
        failures.append("false-google %.1f%% > %.0f%%" % (summary["false_google_rate"] * 100, thresholds["false_google_rate"] * 100))
    if summary["guardrail_google"] > thresholds["guardrail_google"]:
        failures.append("%d google verdict(s) on guardrail cases (must be 0)" % summary["guardrail_google"])
    if summary["reply_ok_rate"] < thresholds["reply_ok_rate"]:
        failures.append("reply-ok %.1f%% < %.0f%%" % (summary["reply_ok_rate"] * 100, thresholds["reply_ok_rate"] * 100))
    if summary["model_calls"] and summary["p95_wall_ms"] > thresholds["p95_wall_ms"]:
        failures.append("p95 wall %.0f ms > %.0f ms" % (summary["p95_wall_ms"], thresholds["p95_wall_ms"]))
    return failures


def recommend(baseline: Dict[str, Any], candidates: Dict[str, Dict[str, Any]]) -> Optional[str]:
    """Best candidate that meets every threshold AND clearly beats tier 1 alone; None = heuristics-only."""
    qualified = [
        (summary["accuracy"], name)
        for name, summary in candidates.items()
        if not check(summary) and summary["accuracy"] - baseline["accuracy"] >= MIN_GAIN_OVER_BASELINE
    ]
    return max(qualified)[1] if qualified else None


def measure_startup_ms(runs: int = 5) -> float:
    """Median wall time of starting Python and importing the decision code, as the hook must."""
    code = "from prompt_preflight.decide import decide"
    samples = []
    for _ in range(runs):
        started = time.perf_counter()
        subprocess.run([sys.executable, "-c", code], cwd=_TOOLS, capture_output=True, check=True, env=dict(os.environ, PYTHONPATH=_TOOLS))
        samples.append((time.perf_counter() - started) * 1000)
    return statistics.median(samples)


def results_table(named: Dict[str, Dict[str, Any]]) -> str:
    """A markdown comparison table, one row per candidate, ready to paste into the spec."""
    lines = [
        "| Candidate | Accuracy | False-google | Guardrail google | Reply OK | p95 model (ms) | p95 wall (ms) | Thresholds |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name, s in named.items():
        timed = s["model_calls"] > 0
        failures = check(s)
        lines.append(
            "| %s | %.1f%% | %.1f%% | %d | %.1f%% | %s | %s | %s |"
            % (
                name,
                s["accuracy"] * 100,
                s["false_google_rate"] * 100,
                s["guardrail_google"],
                s["reply_ok_rate"] * 100,
                "%.0f" % s.get("p95_model_ms", 0) if timed else "n/a",
                "%.0f" % s["p95_wall_ms"] if timed else "n/a",
                "; ".join(failures) if failures else "all met",
            )
        )
    return "\n".join(lines)


def _print_comparison(paths: Sequence[str]) -> int:
    named: Dict[str, Dict[str, Any]] = {}
    for path in paths:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        named[data["name"]] = data["summary"]
    if "baseline" not in named:
        raise SystemExit("--table needs the baseline results too: run with --baseline --json first")
    print(results_table(named))
    winner = recommend(named["baseline"], {k: v for k, v in named.items() if k != "baseline"})
    print("\nRecommendation: %s" % (winner or "heuristics-only default (no model met every threshold and clearly beat tier 1)"))
    return 0


def _print_table(name: str, summary: Dict[str, Any], failures: List[str]) -> None:
    print("\n== %s ==" % name)
    for key in ("n", "accuracy", "false_google_rate", "guardrail_google", "reply_ok_rate", "model_calls", "p95_model_ms", "startup_ms", "p95_wall_ms"):
        print("  %-18s %s" % (key, summary[key]))
    print("  thresholds:        %s" % ("ALL MET" if not failures else "; ".join(failures)))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Score the Prompt Preflight pipeline on the eval set.")
    parser.add_argument("--baseline", action="store_true", help="tier 1 only (no model)")
    parser.add_argument("--model", help="Ollama model to evaluate")
    parser.add_argument("--host", default=DEFAULTS["ollama_host"])
    parser.add_argument("--budget-ms", type=int, default=30000, help="per-call limit while measuring (default generous)")
    parser.add_argument("--items", default=ITEMS_PATH)
    parser.add_argument("--json", help="write the summary here")
    parser.add_argument("--table", nargs="+", metavar="JSON", help="compare saved --json results and print the recommendation")
    args = parser.parse_args(argv)
    if args.table:
        return _print_comparison(args.table)
    if bool(args.baseline) == bool(args.model):
        parser.error("choose exactly one of --baseline or --model NAME")

    items = load_items(args.items)
    cfg = copy.deepcopy(DEFAULTS)
    if args.model:
        cfg.update({"model": args.model, "ollama_host": args.host, "budget_ms": args.budget_ms})
        _warm_up(cfg)
        call = lambda prompt: ollama_client.classify(prompt, cfg)  # noqa: E731
        startup = measure_startup_ms()
    else:
        call, startup = None, 0.0
    results = evaluate(items, cfg, call)
    summary = summarize(results, startup)
    failures = check(summary)
    _print_table(args.model or "baseline (tier 1 only)", summary, failures)
    for r in results:
        if r.predicted != r.label:
            print("  MISS  expected=%-8s got=%-8s %s" % (r.label, r.predicted, r.prompt[:70]))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump({"name": args.model or "baseline", "summary": summary, "failures": failures}, handle, indent=2)
    return 0


def _warm_up(cfg: Dict[str, Any]) -> None:
    """Load the model once so the measured latencies are warm, as they would be in daily use."""
    try:
        ollama_client.classify("warm up the model please", cfg)
    except ModelUnavailable:
        pass


if __name__ == "__main__":
    sys.exit(main())
