import copy

import pytest

from prompt_preflight.config import DEFAULTS
from prompt_preflight.decide import PASS, decide, search_query, should_skip
from prompt_preflight.errors import ModelUnavailable

COVERS = ["R2", "R3", "R4", "R5", "R6"]

REAL_WORK = "write a python function that parses iso dates from log lines"


def cfg(**over):
    merged = copy.deepcopy(DEFAULTS)
    merged.update(over)
    return merged


def model(**reply):
    body = {"verdict": "pass", "confidence": 0.9}
    body.update(reply)
    calls = []

    def call(prompt):
        calls.append(prompt)
        return body

    call.calls = calls
    return call


def boom(prompt):
    raise AssertionError("the model must not be called")


@pytest.mark.parametrize(
    "prompt",
    ["", "   ", "/clear the screen now", "!ls -la the folder", "# remember this note please", "what is x [raw] please", "hi", "two words"],
)
def test_skipped_prompts_are_untouched_and_never_reach_the_model(prompt):
    assert should_skip(prompt, cfg())
    assert decide(prompt, cfg(), True, boom) == PASS


def test_over_length_prompts_are_skipped():
    assert should_skip("word " * 500, cfg(skip_over_chars=100))


def test_min_words_is_configurable():
    assert not should_skip("fix the login bug", cfg(min_words=3))
    assert should_skip("fix the login bug", cfg(min_words=5))


def test_tier1_google_is_decided_without_the_model():
    result = decide("what is the capital of France", cfg(), True, boom)
    assert (result.verdict, result.tier) == ("google", 1)
    assert result.google_query == "what is the capital of France"


def test_undecided_prompt_passes_silently_in_heuristics_only_mode():
    assert decide(REAL_WORK, cfg(), True, None) == PASS


def test_model_google_is_accepted_for_a_standalone_prompt():
    result = decide("how do I reverse a list in python", cfg(), True, model(verdict="google", google_query="python reverse list"))
    assert (result.verdict, result.tier, result.google_query) == ("google", 2, "python reverse list")


def test_model_google_is_downgraded_when_the_prompt_is_context_bound():
    result = decide("how do I reverse the list in my utils.py", cfg(), True, model(verdict="google"))
    assert result == PASS


def test_model_verdicts_below_min_confidence_pass():
    for verdict in ("google", "clarify", "refine"):
        reply = model(verdict=verdict, confidence=0.5, missing=["what"], refined_request="do x")
        assert decide(REAL_WORK, cfg(), True, reply) == PASS


def test_clarify_needs_missing_items_and_the_first_prompt():
    reply = model(verdict="clarify", missing=["which file", "what outcome", 7, "  "])
    first = decide("make the app work better please", cfg(), True, reply)
    assert (first.verdict, first.missing) == ("clarify", ["which file", "what outcome"])
    assert decide("make the app work better please", cfg(), False, reply) == PASS
    assert decide("make the app work better please", cfg(), True, model(verdict="clarify", missing=[])) == PASS


def test_refine_needs_text_and_the_first_prompt():
    reply = model(verdict="refine", refined_request="  Parse ISO-8601 dates from each log line.  ")
    first = decide(REAL_WORK, cfg(), True, reply)
    assert (first.verdict, first.refined) == ("refine", "Parse ISO-8601 dates from each log line.")
    assert decide(REAL_WORK, cfg(), False, reply) == PASS
    assert decide(REAL_WORK, cfg(), True, model(verdict="refine", refined_request="  ")) == PASS


def test_pass_and_unknown_verdicts_are_silent():
    assert decide(REAL_WORK, cfg(), True, model(verdict="pass")) == PASS
    assert decide(REAL_WORK, cfg(), True, model(verdict="shout")) == PASS


@pytest.mark.parametrize("reply", [{}, {"verdict": "google", "confidence": "high"}, None, ["x"]])
def test_malformed_model_replies_pass(reply):
    assert decide(REAL_WORK, cfg(), True, lambda prompt: reply) == PASS


def test_model_unavailable_propagates_so_the_caller_can_cool_down():
    def down(prompt):
        raise ModelUnavailable("down")

    with pytest.raises(ModelUnavailable):
        decide(REAL_WORK, cfg(), True, down)


def test_model_receives_the_original_prompt():
    reply = model()
    decide(REAL_WORK, cfg(), True, reply)
    assert reply.calls == [REAL_WORK]


def test_search_query_is_tidy_and_capped():
    assert search_query("  What   is\nthe capital of France?? ") == "What is the capital of France"
    assert len(search_query("x" * 500)) == 120
