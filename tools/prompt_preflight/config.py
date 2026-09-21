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
    "override_window_s": (1, 86400),
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
    """Parse a plain [http(s)://]host[:port][/path] grammar, fail-closed.

    Returns the bare host name, or "" if the string is not a plain
    [http(s)://]host[:port][/path], contains userinfo, query, fragment,
    invalid characters, invalid IPv6, or port out of range.
    """
    text = host.strip()
    had_scheme = False

    # Step 1: Handle scheme
    if "://" in text:
        scheme, rest = text.split("://", 1)
        if scheme.lower() not in ("http", "https"):
            return ""
        text = rest
        had_scheme = True

    # Step 2: Extract authority (up to first "/" is path, ignored)
    authority = text.split("/", 1)[0]

    # Step 3: Reject if authority contains forbidden characters
    if not authority:
        return ""
    forbidden_chars = {"@", "?", "#", "\\", "%"}
    if any(c in authority for c in forbidden_chars):
        return ""
    # Also reject if contains space, any whitespace, or control chars
    for char in authority:
        if char.isspace() or ord(char) < 32 or ord(char) == 127:
            return ""

    # Step 4: Parse host and port from authority
    if authority.startswith("["):
        # Bracketed IPv6: [::1] or [::1]:port
        close_bracket = authority.find("]")
        if close_bracket == -1:
            return ""
        host_part = authority[1:close_bracket]
        remainder = authority[close_bracket + 1:]

        # Validate that bracketed part is a valid IPv6 address
        try:
            ipaddress.IPv6Address(host_part)
        except ValueError:
            return ""

        if not remainder:
            return host_part
        if remainder.startswith(":"):
            port = remainder[1:]
            if not port or not (port.isascii() and port.isdigit()):
                return ""
            try:
                if int(port) > 65535:
                    return ""
            except ValueError:
                return ""
            return host_part
        # Invalid format
        return ""
    else:
        # Non-bracketed: host or host:port
        # IPv6 without brackets like "::1" should not have a port (multiple colons)
        colon_count = authority.count(":")
        if colon_count == 0:
            # Just host
            return authority
        elif colon_count == 1:
            # host:port
            host_part, port = authority.split(":", 1)
            if not port or not (port.isascii() and port.isdigit()):
                return ""
            try:
                if int(port) > 65535:
                    return ""
            except ValueError:
                return ""
            return host_part
        else:
            # Multiple colons: bare IPv6 address (no port allowed)
            # Bare IPv6 is only allowed without a scheme
            if had_scheme:
                return ""
            # Validate it parses as IPv6
            try:
                ipaddress.IPv6Address(authority)
            except ValueError:
                return ""
            return authority


def is_loopback(host: str) -> bool:
    """True for localhost, 127.0.0.0/8 and ::1, with an optional scheme and port."""
    name = host_only(host)
    if name.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(name).is_loopback
    except ValueError:
        return False
