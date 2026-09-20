"""Turn a Decision into the hook's JSON output. Everything injected is capped and sanitized."""
import re
import unicodedata
from typing import Any, Dict, Optional

from .decide import Decision

MAX_CONTEXT = 600
MAX_REFINED = 400
MAX_QUERY = 120
MAX_GAP = 80

_EVENT = "UserPromptSubmit"


def sanitize(text: Any, limit: int) -> str:
    """Drop control characters, convert all whitespace to spaces, and cap length (ending in ellipsis).

    Result is always a single line. Treats tab, newline, CR, VT, FF, NEL and all Zs/Zl/Zp
    characters as single spaces. Drops all Cc, Cf, Cs, Co, Cn characters. Collapses runs of
    spaces to one and strips.
    """
    text_str = str(text)
    result = []
    for char in text_str:
        # Convert to space: tab, newline, CR, VT, FF, NEL and line/paragraph separators
        if char in "\t\n\r\x0b\x0c\x85":
            result.append(" ")
            continue

        cat = unicodedata.category(char)
        # Also convert line/paragraph separators to space
        if cat in ("Zs", "Zl", "Zp"):
            result.append(" ")
        # Drop: Cc (control), Cf (format), Cs (surrogate), Co (private), Cn (not assigned)
        elif cat in ("Cc", "Cf", "Cs", "Co", "Cn"):
            continue
        else:
            result.append(char)

    # Collapse runs of spaces and strip
    cleaned = re.sub(r" +", " ", "".join(result)).strip()

    # Cap with ellipsis
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def _context(text: str) -> Dict[str, Any]:
    return {"hookSpecificOutput": {"hookEventName": _EVENT, "additionalContext": sanitize(text, MAX_CONTEXT)}}


def build_output(decision: Decision, cfg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """The hook JSON for `decision`, or None when nothing should be said."""
    if decision.verdict == "pass" or not cfg["notify"].get(decision.verdict, False):
        return None

    if decision.verdict == "google":
        message = 'Prompt Preflight: quick lookup — try Google: "%s"' % sanitize(decision.google_query, MAX_QUERY)
        if cfg["mode"] == "block":
            return {"decision": "block", "reason": message + ". Send the same prompt again to override."}
        return {"systemMessage": message}

    if decision.verdict == "clarify":
        gaps = "; ".join(sanitize(item, MAX_GAP) for item in decision.missing)
        out = _context(
            "Prompt Preflight (advisory): the request may be under-specified. Possible gaps: %s. "
            "Ask the user to clarify before acting." % gaps
        )
        out["systemMessage"] = "Prompt Preflight: this may be too vague to act on. Missing: %s" % gaps
        return out

    if decision.verdict == "refine":
        refined = sanitize(decision.refined, MAX_REFINED)
        return _context(
            "Prompt Preflight (advisory, from a small local model; the user's original prompt is "
            "authoritative): a sharper restatement of the request: %s" % refined
        )
    return None


def degraded_notice() -> Dict[str, Any]:
    return {"systemMessage": "Prompt Preflight: the local model is unavailable, so it is running heuristics-only."}
