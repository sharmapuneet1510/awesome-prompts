import pytest

from prompt_preflight.heuristics import context_signals, tier1

COVERS = ["R2", "R5"]


@pytest.mark.parametrize(
    "prompt,expected",
    [
        ("look at ```print(1)``` please", "code_fence"),
        ("why does src/app/main.py crash", "path"),
        ("see utils.js for details", "path"),
        ("Traceback (most recent call last):", "stack_trace"),
        ("it raises ModuleNotFoundError", "stack_trace"),
        ("what is wrong with my code", "ownership"),
        ("now do the same for orders", "reference_word"),
        ("what does this do", "reference_word"),
        ("what is the latest commit", "code_noun"),
        ("how do I fix the build", "code_noun"),
    ],
)
def test_each_context_signal_is_detected(prompt, expected):
    assert expected in context_signals(prompt)


@pytest.mark.parametrize(
    "prompt",
    [
        "implement rate limiting on the api",
        "Add pagination to the users endpoint",
        "please refactor the payment client",
        "set up ci with github actions",
    ],
)
def test_an_imperative_task_is_never_a_lookup(prompt):
    # Found by the eval baseline: tier 1 called "implement rate limiting on the api" a web search.
    assert "task_verb" in context_signals(prompt)
    assert tier1(prompt).verdict is None


@pytest.mark.parametrize("prompt", ["convert 72 fahrenheit to celsius", "how to install node on ubuntu"])
def test_lookup_style_requests_are_not_mistaken_for_tasks(prompt):
    assert "task_verb" not in context_signals(prompt)


@pytest.mark.parametrize(
    "prompt",
    ["what is the capital of France", "how do I reverse a list in python", "explain the difference between TCP and UDP"],
)
def test_standalone_questions_have_no_signals(prompt):
    assert context_signals(prompt) == []


@pytest.mark.parametrize(
    "prompt", ["what is the capital of France", "what is the latest version of react"]
)
def test_tier1_decides_google_for_standalone_lookups(prompt):
    assert tier1(prompt).verdict == "google"


@pytest.mark.parametrize(
    "prompt",
    [
        "now do the same for orders",  # 'now' trips the analyzer's temporal pattern
        "what is the latest commit in this repo",
        "what is the latest version of my package",
    ],
)
def test_tier1_never_says_google_when_the_prompt_is_context_bound(prompt):
    result = tier1(prompt)
    assert result.verdict is None
    assert result.signals


@pytest.mark.parametrize(
    "prompt", ["yes", "continue", "commit and push", "run the tests", "approve", "go ahead", "fix bug", "make it better"]
)
def test_tier1_never_calls_short_or_vague_prompts_anything(prompt):
    # Amendment A2: the analyzer marks these 'skip', which is NOT evidence they are vague.
    assert tier1(prompt).verdict is None


def test_tier1_leaves_real_work_undecided():
    assert tier1("Refactor OrderService.submit() to use idempotency keys and add tests").verdict is None
