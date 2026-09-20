"""Tier 1: deterministic checks. No model, no network, no I/O.

Tier 1 decides one thing only: a standalone prompt that a web search would answer.
Everything else is left undecided for the model tier (or passes silently).
"""
import re
from dataclasses import dataclass, field
from typing import List, Optional

from token_optimizer import QueryAnalyzer
from token_optimizer.models import Recommendation

_LEAD_IN = r"(?:(?:please|kindly|just)\s+)?(?:(?:can|could|would|will)\s+you\s+(?:please\s+)?|(?:i|we)\s+(?:need|want|would\s+like|have|got)\s+to\s+|(?:i|we|you)\s+should\s+|let'?s\s+|help\s+me\s+(?:to\s+)?)?"
_TASK_VERBS = r"(?:implement|add|write|create|build|refactor|fix|update|migrate|document|generate|remove|rename|delete|deploy|set\s+up|make|optimi[sz]e|improve|clean|show|tell|give|list|find|fetch|get|check|review|summari[sz]e|run|open|read)"
_LOOKUP_QUESTION = re.compile(r"^\s*(?:what|what's|who|whom|whose|when|where|which|why|how|is|are|was|were|does|do|did|convert|define|explain|difference|meaning)\b", re.I)

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
            r"^\s*" + _LEAD_IN + _TASK_VERBS + r"\b",
            re.I,
        ),
    ),
    (
        "code_noun",
        re.compile(
            r"\b(?:repo|repository|branch|commit|codebase|function|method|class|endpoint|"
            r"module|pull request|PR|build|deploy(?:ment)?|tests?|bug|error|files?|logs?|servers?|tickets?|packages?|jobs?|releases?|diffs?|schemas?|configs?|configuration|projects?|services?|apps?|application|staging|production|prod|pipelines?|deployments?)\b",
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
        # Only return google if the prompt is written as a lookup question
        if _LOOKUP_QUESTION.search(prompt):
            return Tier1("google", [])
    return Tier1(None, [])
