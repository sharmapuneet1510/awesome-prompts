"""Load and validate the Prompt Preflight configuration. Loading never raises."""
import copy
import ipaddress
import json
from typing import Any, Dict

DEFAULTS: Dict[str, Any] = {
    "enabled": True,
    "mode": "advise",
    "model": "",
    "ollama_host": "127.0.0.1:11434",
    "budget_ms": 2500,
    "min_confidence": 0.7,
    "notify": {"google": True, "clarify": True, "refine": True},
    "skip_over_chars": 2000,
    "min_words": 3,
    "bypass_marker": "[raw]",
    "keep_alive": "10m",
    "cooldown_s": 300,
    "override_window_s": 300,
    "allow_remote": False,
    "log_prompts": False,
}

_RANGES = {
    "budget_ms": (100, 30000),
    "min_confidence": (0.0, 1.0),
    "skip_over_chars": (1, 1000000),
    "min_words": (0, 100),
    "cooldown_s": (0, 86400),
    "override_window_s": (0, 86400),
}


def _same_type(value: Any, default: Any) -> bool:
    if isinstance(default, bool):
        return isinstance(value, bool)
    if isinstance(default, (int, float)):
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, type(default))


def _acceptable(key: str, value: Any) -> bool:
    if key == "mode":
        return value in ("advise", "block")
    if key in _RANGES:
        low, high = _RANGES[key]
        return low <= value <= high
    return True


def load_config(path: str) -> Dict[str, Any]:
    """Return DEFAULTS overlaid with any valid values from the JSON file at `path`."""
    cfg = copy.deepcopy(DEFAULTS)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except (OSError, ValueError):
        return cfg
    if not isinstance(raw, dict):
        return cfg
    for key, default in DEFAULTS.items():
        if key not in raw:
            continue
        value = raw[key]
        if key == "notify":
            if isinstance(value, dict):
                for verdict in default:
                    if isinstance(value.get(verdict), bool):
                        cfg["notify"][verdict] = value[verdict]
        elif _same_type(value, default) and _acceptable(key, value):
            cfg[key] = value
    return cfg


def host_only(host: str) -> str:
    """Strip an optional scheme, path, and port: 'http://[::1]:11434/x' -> '::1'."""
    text = host.strip()
    if "://" in text:
        text = text.split("://", 1)[1]
    text = text.split("/", 1)[0]
    if text.startswith("["):
        end = text.find("]")
        return text[1:end] if end != -1 else text[1:]
    if text.count(":") == 1:
        return text.split(":", 1)[0]
    return text


def is_loopback(host: str) -> bool:
    """True for localhost, 127.0.0.0/8 and ::1, with an optional scheme and port."""
    name = host_only(host)
    if name.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(name).is_loopback
    except ValueError:
        return False
