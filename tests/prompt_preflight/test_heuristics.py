import pytest

from prompt_preflight.heuristics import context_signals, tier1
from token_optimizer.models import Recommendation

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


# Fix 1: Task verb detection with lead-ins
@pytest.mark.parametrize(
    "prompt",
    [
        "can you implement rate limiting on the api",
        "could you please add pagination",
        "I need to add rate limiting",
        "we should refactor the client",
        "let's set up ci",
        "help me to write a script",
        "please show me the logs",
    ],
)
def test_task_verb_with_lead_ins(prompt):
    assert "task_verb" in context_signals(prompt)


# Fix 1: Task detection prevents google for task requests
@pytest.mark.parametrize(
    "prompt",
    [
        "can you implement rate limiting on the api",
        "I need to add rate limiting to the api",
        "show me the latest logs from staging",
        "what is the current status of the ticket",
        "what is the latest version of the server",
        "what changed in the latest release",
        "what are the latest failing jobs",
        "review the diff and tell me what is trending",
    ],
)
def test_tier1_never_says_google_for_task_requests(prompt):
    assert tier1(prompt).verdict is None


# Fix 1: New code nouns prevent google
@pytest.mark.parametrize(
    "prompt",
    [
        "what is in the file",
        "what do the logs say",
        "which server is down",
        "what is the ticket status",
        "which package failed",
        "what is in the release notes",
        "what is the project layout",
        "which service crashed",
        "which app crashed",
        "is staging down",
        "is production up",
        "what is the pipeline doing",
    ],
)
def test_new_code_nouns_prevent_google(prompt):
    result = tier1(prompt)
    assert result.verdict is None
    assert "code_noun" in result.signals


# Fix 1: Standalone lookup questions still get google
@pytest.mark.parametrize(
    "prompt",
    [
        "what is the capital of Australia",
        "what is the latest version of react",
        "what is the http status code for too many requests",
        "what is a foreign key in sql",
    ],
)
def test_standalone_lookups_still_get_google(prompt):
    assert tier1(prompt).verdict == "google"


# Fix 1: Positive evidence - analyzer recommendation alone is not enough
def test_tier1_requires_lookup_question_format_for_google():
    from prompt_preflight.heuristics import _analyzer

    # Find a prompt the analyzer recommends web search for, but isn't a lookup question
    # "latest react version" is a query the analyzer may recommend for web search
    prompt = "latest react version"
    result = _analyzer.analyze(prompt)
    # PRECONDITION: the analyzer must recommend web search
    assert result.feedback.recommendation == Recommendation.WEB_SEARCH, \
        f"Test precondition failed: analyzer doesn't recommend web search for '{prompt}'"
    # But tier1 should not say google because it's not written as a lookup question
    assert tier1(prompt).verdict is None
