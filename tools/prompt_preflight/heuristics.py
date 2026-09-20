"""Tier 1: deterministic checks. No model, no network, no I/O.

Tier 1 decides one thing only: a standalone prompt that a web search would answer.
Everything else is left undecided for the model tier (or passes silently).
"""
import re
from dataclasses import dataclass, field
from typing import List, Optional

from token_optimizer import QueryAnalyzer
from token_optimizer.models import Recommendation

_SIGNALS = (
    ("code_fence", re.compile(r"```")),
    (
        "path",
        re.compile(
            r"(?:^|\s)(?:\.{0,2}/|~/|[A-Za-z]:\\)[\w.\-/\\]+"
            r"|\b[\w\-]+\.(?:py|js|ts|tsx|java|kt|go|rs|rb|md|json|ya?ml|toml|sh|sql|xml|html|css)\b"
        ),
    ),
    (
        "stack_trace",
        re.compile(
            r"Traceback \(most recent call last\)|^\s+at .+\(.+:\d+(?::\d+)?\)|\b\w+(?:Error|Exception)\b",
            re.M,
        ),
    ),
    ("ownership", re.compile(r"\b(?:my|our|mine)\b", re.I)),
    (
        "reference_word",
        re.compile(
            r"\b(?:this|that|these|those|it|them|same|above|below|earlier|previous|"
            r"again|now|next|also|instead)\b",
            re.I,
        ),
    ),
    (
        "task_verb",  # an instruction to do work, never a search query
        re.compile(
            r"^\s*(?:please\s+)?(?:implement|add|write|create|build|refactor|fix|update|migrate|document|"
            r"generate|remove|rename|delete|deploy|set up|make|optimi[sz]e|improve|clean)\b",
            re.I,
        ),
    ),
    (
        "code_noun",
        re.compile(
            r"\b(?:repo|repository|branch|commit|codebase|function|method|class|endpoint|"
            r"module|pull request|PR|build|deploy(?:ment)?|tests?|bug|error)\b",
            re.I,
        ),
    ),
)

_analyzer = QueryAnalyzer()


@dataclass(frozen=True)
class Tier1:
    verdict: Optional[str]  # "google" or None (undecided)
    signals: List[str] = field(default_factory=list)


def context_signals(prompt: str) -> List[str]:
    """Names of the signals showing the prompt is not a standalone lookup.

    Either it depends on the user's own context (code, files, "my", earlier conversation),
    or it is an instruction to do work. Any signal forbids a `google` verdict.
    """
    return [name for name, pattern in _SIGNALS if pattern.search(prompt)]


def tier1(prompt: str) -> Tier1:
    signals = context_signals(prompt)
    if signals:
        return Tier1(None, signals)
    result = _analyzer.analyze(prompt)
    if result.feedback.recommendation == Recommendation.WEB_SEARCH:
        return Tier1("google", [])
    return Tier1(None, [])
