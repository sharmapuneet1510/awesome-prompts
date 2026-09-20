"""Verdict logic. Pure: the model is passed in as a callable, and this module does no I/O."""
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .heuristics import context_signals, tier1

ModelCall = Callable[[str], Dict[str, Any]]

MAX_MISSING = 5


@dataclass(frozen=True)
class Decision:
    verdict: str = "pass"  # pass | refine | clarify | google
    tier: int = 0  # 0 = nothing acted, 1 = heuristics, 2 = model
    confidence: float = 1.0
    google_query: str = ""
    missing: List[str] = field(default_factory=list)
    refined: str = ""
    reasons: List[str] = field(default_factory=list)


PASS = Decision()


def should_skip(prompt: str, cfg: Dict[str, Any]) -> bool:
    """True when the prompt must be left untouched by both tiers."""
    text = prompt.strip()
    if not text:
        return True
    if text[0] in "/!#":
        return True
    marker = cfg["bypass_marker"]
    if marker and marker in prompt:
        return True
    if len(prompt) > cfg["skip_over_chars"]:
        return True
    return len(text.split()) < cfg["min_words"]


def search_query(prompt: str, limit: int = 120) -> str:
    """A tidy web-search query taken from the prompt itself."""
    text = re.sub(r"\s+", " ", prompt).strip().rstrip("?.! ")
    return text[:limit]


def decide(
    prompt: str,
    cfg: Dict[str, Any],
    first_prompt: bool,
    model_call: Optional[ModelCall],
) -> Decision:
    """Return the verdict for `prompt`.

    `model_call` is None in heuristics-only mode. It may raise ModelUnavailable, which
    propagates so the caller can start the cooldown.
    """
    if should_skip(prompt, cfg):
        return PASS
    tier_one = tier1(prompt)
    if tier_one.verdict == "google":
        return Decision("google", 1, 1.0, google_query=search_query(prompt), reasons=["tier1:web_search"])
    if model_call is None:
        return PASS
    return _apply_guardrails(model_call(prompt), prompt, cfg, first_prompt)


def _apply_guardrails(raw: Dict[str, Any], prompt: str, cfg: Dict[str, Any], first_prompt: bool) -> Decision:
    try:
        verdict = raw.get("verdict")
        confidence = float(raw.get("confidence", 0.0))
    except (AttributeError, TypeError, ValueError):
        return PASS
    if confidence < cfg["min_confidence"]:
        return PASS
    if verdict == "google":
        if context_signals(prompt):
            return PASS
        query = raw.get("google_query") or search_query(prompt)
        return Decision("google", 2, confidence, google_query=search_query(query), reasons=["model"])
    if verdict in ("clarify", "refine") and not first_prompt:
        return PASS
    if verdict == "clarify":
        missing = [m for m in raw.get("missing", []) if isinstance(m, str) and m.strip()][:MAX_MISSING]
        if not missing:
            return PASS
        return Decision("clarify", 2, confidence, missing=missing, reasons=["model"])
    if verdict == "refine":
        refined = raw.get("refined_request", "")
        if not isinstance(refined, str) or not refined.strip():
            return PASS
        return Decision("refine", 2, confidence, refined=refined.strip(), reasons=["model"])
    return PASS
