import copy
import json
from collections import Counter

import pytest

from prompt_preflight.config import DEFAULTS
from prompt_preflight.decide import should_skip
from prompt_preflight.errors import ModelUnavailable
from prompt_preflight.eval import run_eval as ev

COVERS = ["R12"]

ITEMS = ev.load_items()
LABEL_TO_REPLY = {
    "google": {"verdict": "google", "confidence": 0.95, "google_query": "search"},
    "clarify": {"verdict": "clarify", "confidence": 0.95, "missing": ["the goal"]},
    "refine": {"verdict": "refine", "confidence": 0.95, "refined_request": "A sharper request."},
    "pass": {"verdict": "pass", "confidence": 0.95},
}


def oracle(items):
    by_prompt = {item["prompt"]: item["label"] for item in items}
    return lambda prompt: dict(LABEL_TO_REPLY[by_prompt[prompt]])


def result(label="pass", predicted="pass", guardrail=False, model_ms=None, failed=False):
    return ev.Result("p", label, guardrail, predicted, model_ms, failed)


# ---------- the eval set itself ---------------------------------------------------------------


def test_eval_set_is_balanced_across_the_four_verdicts():
    assert len(ITEMS) == 60
    assert Counter(i["label"] for i in ITEMS) == {"google": 15, "clarify": 15, "refine": 15, "pass": 15}


def test_eval_set_has_guardrail_traps_and_none_is_labelled_google():
    traps = [i for i in ITEMS if i["guardrail"]]
    assert len(traps) >= 8
    assert all(i["label"] != "google" for i in traps)


def test_eval_prompts_are_unique_and_actually_reach_the_pipeline():
    prompts = [i["prompt"] for i in ITEMS]
    assert len(set(prompts)) == len(prompts)
    assert not [p for p in prompts if should_skip(p, DEFAULTS)]


def test_load_items_rejects_an_unknown_label(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text(json.dumps({"prompt": "do the thing please", "label": "maybe"}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError):
        ev.load_items(str(path))


# ---------- the metrics -----------------------------------------------------------------------


def test_baseline_is_safe_but_not_good_enough_on_its_own():
    summary = ev.summarize(ev.evaluate(ITEMS, copy.deepcopy(DEFAULTS), None))
    assert summary["n"] == 60 and summary["model_calls"] == 0
    assert summary["guardrail_google"] == 0 and summary["false_google_rate"] <= 0.05
    assert summary["accuracy"] < ev.THRESHOLDS["accuracy"]  # this gap is why a model tier exists


def test_a_perfect_oracle_model_meets_every_threshold_and_the_guardrail_cost_is_known():
    cfg = dict(copy.deepcopy(DEFAULTS), model="oracle")
    results = ev.evaluate(ITEMS, cfg, oracle(ITEMS))
    summary = ev.summarize(results, startup_ms=100.0)
    assert summary["false_google_rate"] == 0.0 and ev.check(summary) == []
    # The guardrails deliberately trade a little recall for safety: 'commit' is a code noun, so even a
    # perfect model cannot get this legitimate lookup through. This is the whole known ceiling cost.
    misses = [r.prompt for r in results if r.predicted != r.label]
    assert misses == ["how do I undo the last git commit"]
    assert summary["accuracy"] == pytest.approx(59 / 60)


def test_a_model_that_always_says_google_is_caught_by_the_accuracy_threshold():
    cfg = dict(copy.deepcopy(DEFAULTS), model="eager")
    always = lambda prompt: dict(LABEL_TO_REPLY["google"])  # noqa: E731
    summary = ev.summarize(ev.evaluate(ITEMS, cfg, always))
    assert any("accuracy" in failure for failure in ev.check(summary))
    # The decision guardrails refuse `google` for every prompt carrying a context signal, so even an
    # eager model gets very few non-lookups through (2 of 45 vague prompts) and trips no guardrail trap.
    assert summary["guardrail_google"] == 0
    assert summary["false_google_rate"] <= 0.10


def test_check_names_every_failed_threshold():
    worst = {
        "accuracy": 0.5,
        "false_google_rate": 0.2,
        "guardrail_google": 1,
        "reply_ok_rate": 0.5,
        "model_calls": 10,
        "p95_wall_ms": 9000.0,
    }
    failures = " | ".join(ev.check(worst))
    for needle in ("accuracy", "false-google", "guardrail", "reply-ok", "p95"):
        assert needle in failures, needle


def test_reply_failures_lower_reply_ok_rate_and_count_as_pass():
    cfg = dict(copy.deepcopy(DEFAULTS), model="flaky")

    def flaky(prompt):
        raise ModelUnavailable("bad json")

    summary = ev.summarize(ev.evaluate(ITEMS, cfg, flaky))
    assert summary["reply_ok_rate"] < 1.0 and summary["model_calls"] > 0
    assert any("reply-ok" in failure for failure in ev.check(summary))


def test_p95_uses_nearest_rank_and_adds_interpreter_startup():
    results = [result(model_ms=float(ms)) for ms in range(1, 101)]
    summary = ev.summarize(results, startup_ms=50.0)
    assert summary["p95_model_ms"] == 95.0 and summary["p95_wall_ms"] == 145.0


def test_latency_threshold_applies_only_when_a_model_was_called():
    fast = ev.summarize([result(model_ms=100.0)], startup_ms=100.0)
    slow = ev.summarize([result(model_ms=2500.0)], startup_ms=100.0)
    assert not [f for f in ev.check(fast) if "p95" in f]
    assert [f for f in ev.check(slow) if "p95" in f]
    assert not [f for f in ev.check(ev.summarize([result()])) if "p95" in f]


def test_false_google_rate_counts_only_non_google_labels():
    results = [result("google", "google"), result("pass", "google"), result("refine", "pass"), result("clarify", "pass")]
    assert ev.summarize(results)["false_google_rate"] == pytest.approx(1 / 3)


def test_guardrail_google_counts_only_flagged_prompts():
    results = [result("pass", "google", guardrail=True), result("refine", "google", guardrail=False)]
    assert ev.summarize(results)["guardrail_google"] == 1


# ---------- the decision rule -----------------------------------------------------------------


def summary_with(accuracy, **over):
    base = {"accuracy": accuracy, "false_google_rate": 0.0, "guardrail_google": 0, "reply_ok_rate": 1.0, "model_calls": 10, "p95_wall_ms": 500.0}
    base.update(over)
    return base


def test_recommend_picks_the_most_accurate_qualifying_model():
    baseline = summary_with(0.32)
    assert ev.recommend(baseline, {"a": summary_with(0.85), "b": summary_with(0.92)}) == "b"


def test_recommend_says_heuristics_only_when_nothing_qualifies():
    baseline = summary_with(0.32)
    assert ev.recommend(baseline, {}) is None
    assert ev.recommend(baseline, {"slow": summary_with(0.95, p95_wall_ms=5000.0)}) is None
    assert ev.recommend(baseline, {"sloppy": summary_with(0.95, false_google_rate=0.2)}) is None
    assert ev.recommend(baseline, {"weak": summary_with(0.60)}) is None


def test_recommend_requires_a_clear_win_over_the_baseline_even_if_thresholds_are_met():
    loose = dict(ev.THRESHOLDS, accuracy=0.30)
    baseline = summary_with(0.82)
    candidate = summary_with(0.85)  # meets a loose bar but is only +3 points over tier 1 alone
    assert ev.check(candidate, loose) == []
    assert ev.recommend(baseline, {"marginal": candidate}) is None


# ---------- the comparison table and the recommendation ---------------------------------------


def saved(tmp_path, name, summary):
    path = tmp_path / ("%s.json" % name.replace(" ", "_"))
    path.write_text(json.dumps({"name": name, "summary": summary, "failures": ev.check(summary)}), encoding="utf-8")
    return str(path)


def test_results_table_has_one_row_per_candidate_and_states_the_threshold_outcome():
    baseline = summary_with(0.32, model_calls=0, p95_model_ms=0.0, p95_wall_ms=0.0)
    good = summary_with(0.9, p95_model_ms=400.0, p95_wall_ms=500.0)
    table = ev.results_table({"baseline": baseline, "tiny:1b": good})
    lines = table.splitlines()
    assert lines[0].startswith("| Candidate |") and len(lines) == 4
    assert "| baseline |" in lines[2] and "32.0%" in lines[2] and "| n/a |" in lines[2]
    assert "| tiny:1b |" in lines[3] and "90.0%" in lines[3] and "all met" in lines[3]


def test_table_mode_prints_the_comparison_and_names_the_winner(tmp_path, capsys):
    files = [
        saved(tmp_path, "baseline", summary_with(0.32, model_calls=0)),
        saved(tmp_path, "tiny:1b", summary_with(0.9)),
        saved(tmp_path, "big:8b", summary_with(0.95, p95_wall_ms=5000.0)),
    ]
    assert ev.main(["--table", *files]) == 0
    out = capsys.readouterr().out
    assert "| tiny:1b |" in out and "| big:8b |" in out
    assert "Recommendation: tiny:1b" in out


def test_table_mode_falls_back_to_heuristics_only_when_no_model_qualifies(tmp_path, capsys):
    files = [saved(tmp_path, "baseline", summary_with(0.32, model_calls=0)), saved(tmp_path, "weak:1b", summary_with(0.5))]
    ev.main(["--table", *files])
    assert "Recommendation: heuristics-only" in capsys.readouterr().out


def test_table_mode_needs_a_baseline_file(tmp_path):
    with pytest.raises(SystemExit) as info:
        ev.main(["--table", saved(tmp_path, "tiny:1b", summary_with(0.9))])
    assert "baseline" in str(info.value.code)


def test_choose_exactly_one_of_baseline_or_model(capsys):
    with pytest.raises(SystemExit):
        ev.main([])
    assert "exactly one of --baseline or --model" in capsys.readouterr().err
