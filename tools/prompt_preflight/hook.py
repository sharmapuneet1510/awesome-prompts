"""Hook entry: hook JSON on stdin -> at most one JSON object on stdout. Always exits 0.

Claude Code treats plain stdout as context and shows a "hook error" for bad output, so this
module writes exactly one valid JSON object or nothing, and sends diagnostics to a log file.
"""
import json
import os
import sys
import time
import traceback
from typing import Any, Callable, Dict, Mapping, Optional

from . import ollama_client
from .config import load_config
from .decide import PASS, ModelCall, decide
from .errors import ModelUnavailable
from .output import build_output, degraded_notice
from .state import State

MAX_STDIN_BYTES = 1000000
MAX_LOG_BYTES = 1000000


def _log(root: str, line: Dict[str, Any]) -> None:
    path = os.path.join(root, "preflight.log")
    try:
        if os.path.getsize(path) > MAX_LOG_BYTES:
            os.replace(path, path + ".1")
    except OSError:
        pass
    try:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(line) + "\n")
    except OSError:
        pass


def run(
    stdin_text: str,
    root: str,
    env: Optional[Mapping[str, str]] = None,
    model_call: Optional[ModelCall] = None,
    clock: Callable[[], float] = time.time,
) -> Optional[Dict[str, Any]]:
    """Return the hook's JSON output, or None to say nothing. `model_call` is injectable for tests.

    With no config.json in `root` the feature is not configured, and this returns None having
    written nothing (no state, no log).
    """
    env = os.environ if env is None else env
    if env.get("PROMPT_PREFLIGHT", "").strip().lower() == "off":
        return None
    config_path = os.path.join(root, "config.json")
    if not os.path.exists(config_path):
        return None  # not configured: a complete bypass, and nothing is written
    cfg = load_config(config_path)
    if not cfg["enabled"]:
        return None
    try:
        event = json.loads(stdin_text)
    except ValueError:
        return None
    prompt = event.get("prompt") if isinstance(event, dict) else None
    if not isinstance(prompt, str):
        return None

    state = State(os.path.join(root, "state.json"), clock)
    session_id = event.get("session_id")
    first_prompt = state.register_session(session_id if isinstance(session_id, str) else "")

    call: Optional[ModelCall] = None
    if cfg["model"] and not state.in_cooldown():
        call = model_call or (lambda text: ollama_client.classify(text, cfg))

    started = time.perf_counter()
    model_failed = False
    try:
        decision = decide(prompt, cfg, first_prompt, call)
    except ModelUnavailable:
        model_failed = True
        decision = PASS
        state.start_cooldown(cfg["cooldown_s"])
    latency_ms = round((time.perf_counter() - started) * 1000, 1)

    out = build_output(decision, cfg)
    if out is not None and out.get("decision") == "block":
        if state.consume_override(prompt, cfg["override_window_s"]):
            out = None
        else:
            state.remember_block(prompt)
    if out is None and model_failed and state.notice_due("degraded"):
        out = degraded_notice()

    entry: Dict[str, Any] = {
        "ts": round(clock(), 1),
        "verdict": decision.verdict,
        "tier": decision.tier,
        "confidence": decision.confidence,
        "latency_ms": latency_ms,
        "first_prompt": first_prompt,
        "model_failed": model_failed,
    }
    if cfg["log_prompts"]:
        entry["prompt"] = prompt
    _log(root, entry)
    return out


def main(root: str) -> None:
    """Process one hook call. Never raises, never exits non-zero."""
    try:
        text = sys.stdin.buffer.read(MAX_STDIN_BYTES).decode("utf-8", "replace")
        out = run(text, root)
        if out is not None:
            sys.stdout.write(json.dumps(out))
            sys.stdout.flush()
    except Exception:  # fail open by design: Preflight must never get in the way
        try:
            _log(root, {"ts": round(time.time(), 1), "error": traceback.format_exc()[-2000:]})
        except Exception:
            pass
    sys.exit(0)
