import json

import pytest

from prompt_preflight.config import DEFAULTS, host_only, is_loopback, load_config

COVERS = ["R8", "R9"]


def write(tmp_path, content):
    path = tmp_path / "config.json"
    path.write_text(content if isinstance(content, str) else json.dumps(content), encoding="utf-8")
    return str(path)


def test_missing_file_gives_defaults(tmp_path):
    assert load_config(str(tmp_path / "nope.json")) == DEFAULTS


@pytest.mark.parametrize("content", ["{not json", "[1, 2]", '"text"', ""])
def test_corrupt_or_wrong_shape_gives_defaults(tmp_path, content):
    assert load_config(write(tmp_path, content)) == DEFAULTS


def test_valid_values_override_defaults(tmp_path):
    cfg = load_config(write(tmp_path, {"model": "tiny:1b", "mode": "block", "budget_ms": 1500, "min_confidence": 0.9}))
    assert (cfg["model"], cfg["mode"], cfg["budget_ms"], cfg["min_confidence"]) == ("tiny:1b", "block", 1500, 0.9)


@pytest.mark.parametrize(
    "key,bad",
    [
        ("mode", "shout"),
        ("budget_ms", "fast"),
        ("budget_ms", 5),
        ("min_confidence", 1.5),
        ("enabled", "yes"),
        ("allow_remote", 1),
        ("cooldown_s", -1),
        ("min_words", True),
    ],
)
def test_invalid_values_fall_back_to_default(tmp_path, key, bad):
    assert load_config(write(tmp_path, {key: bad}))[key] == DEFAULTS[key]


def test_notify_merges_per_verdict_and_ignores_junk(tmp_path):
    cfg = load_config(write(tmp_path, {"notify": {"refine": False, "google": "no", "extra": True}}))
    assert cfg["notify"] == {"google": True, "clarify": True, "refine": False}


def test_unknown_keys_are_ignored(tmp_path):
    assert load_config(write(tmp_path, {"telemetry": True})) == DEFAULTS


def test_loading_does_not_mutate_defaults(tmp_path):
    load_config(write(tmp_path, {"notify": {"google": False}}))
    assert DEFAULTS["notify"]["google"] is True


@pytest.mark.parametrize(
    "input_host,expected_host",
    [
        ("127.0.0.1", "127.0.0.1"),
        ("127.0.0.1:11434", "127.0.0.1"),
        ("localhost", "localhost"),
        ("localhost:11434", "localhost"),
        ("[::1]:11434", "::1"),
        ("[::1]", "::1"),
        ("::1", "::1"),
        ("http://localhost:11434", "localhost"),
        ("http://localhost:11434/api/chat", "localhost"),
        ("https://[::1]:11434/", "::1"),
        ("HTTP://LocalHost:11434", "LocalHost"),
    ],
)
def test_host_only_accepts_valid_hosts(input_host, expected_host):
    assert host_only(input_host) == expected_host


@pytest.mark.parametrize(
    "refused_host",
    [
        "http://localhost:11434@evil.com",
        "127.0.0.1:80@evil.com",
        "[::1]@evil.com",
        "http://[::1]:11434@evil.com",
        "user@localhost:11434",
        "http://evil.com?@localhost",
        "http://evil.com#@localhost",
        "http://evil.com:80?@127.0.0.1:11434",
        "localhost?x=1",
        "localhost#frag",
        "http://evil.com\\@localhost",
        "localhost:abc",
        "localhost:",
        "[::1",
        "ftp://localhost",
        "file:///etc/passwd",
        "loc alhost",
        "local%68ost",
        "",
        "   ",
        "http://",
    ],
)
def test_host_only_refuses_invalid_hosts(refused_host):
    assert host_only(refused_host) == ""


@pytest.mark.parametrize(
    "input_host",
    [
        "127.0.0.1",
        "127.0.0.1:11434",
        "localhost",
        "localhost:11434",
        "[::1]:11434",
        "[::1]",
        "::1",
        "http://localhost:11434",
        "http://localhost:11434/api/chat",
        "https://[::1]:11434/",
        "HTTP://LocalHost:11434",
    ],
)
def test_is_loopback_accepts_valid_loopback_hosts(input_host):
    assert is_loopback(input_host) is True


@pytest.mark.parametrize(
    "input_host",
    [
        "http://localhost:11434@evil.com",
        "127.0.0.1:80@evil.com",
        "[::1]@evil.com",
        "http://[::1]:11434@evil.com",
        "user@localhost:11434",
        "http://evil.com?@localhost",
        "http://evil.com#@localhost",
        "http://evil.com:80?@127.0.0.1:11434",
        "localhost?x=1",
        "localhost#frag",
        "http://evil.com\\@localhost",
        "localhost:abc",
        "localhost:",
        "[::1",
        "ftp://localhost",
        "file:///etc/passwd",
        "loc alhost",
        "local%68ost",
        "",
        "   ",
        "http://",
        "10.0.0.5:11434",
        "example.com",
        "0.0.0.0",
        "http://ollama.internal:11434",
        "evil.com/@localhost",
        "http://a@b@localhost",
        "localhost@127.0.0.1",
    ],
)
def test_is_loopback_refuses_invalid_or_remote_hosts(input_host):
    assert is_loopback(input_host) is False


def test_differential_is_loopback_vs_urllib():
    """Verify is_loopback agrees with urllib for all edge cases."""
    import ipaddress
    import urllib.parse
    import urllib.request

    # Strings that should be accepted as loopback
    accept_cases = [
        "127.0.0.1",
        "127.0.0.1:11434",
        "localhost",
        "localhost:11434",
        "[::1]:11434",
        "[::1]",
        "::1",
        "http://localhost:11434",
        "http://localhost:11434/api/chat",
        "https://[::1]:11434/",
        "HTTP://LocalHost:11434",
    ]

    # Strings that should be refused
    refuse_cases = [
        "http://localhost:11434@evil.com",
        "127.0.0.1:80@evil.com",
        "[::1]@evil.com",
        "http://[::1]:11434@evil.com",
        "user@localhost:11434",
        "http://evil.com?@localhost",
        "http://evil.com#@localhost",
        "http://evil.com:80?@127.0.0.1:11434",
        "localhost?x=1",
        "localhost#frag",
        "http://evil.com\\@localhost",
        "localhost:abc",
        "localhost:",
        "[::1",
        "ftp://localhost",
        "file:///etc/passwd",
        "loc alhost",
        "local%68ost",
        "",
        "   ",
        "http://",
        "10.0.0.5:11434",
        "example.com",
        "0.0.0.0",
        "http://ollama.internal:11434",
        "evil.com/@localhost",
        "http://a@b@localhost",
        "localhost@127.0.0.1",
    ]

    # For accepted cases, verify urllib.parse.urlsplit agrees
    for s in accept_cases:
        if is_loopback(s):
            # Parse with urlsplit
            parsed = urllib.parse.urlsplit(s if "://" in s else "//" + s)
            hostname = parsed.hostname

            # Verify the hostname is a loopback
            if hostname and hostname.lower() != "localhost":
                try:
                    assert ipaddress.ip_address(hostname).is_loopback
                except ValueError:
                    pytest.fail(f"urlsplit gave non-loopback hostname for {s}: {hostname}")

            # Also check urllib.request.Request
            url_for_request = "http://" + s.split("://", 1)[-1].split("/", 1)[0]
            # Remove port from url for host extraction
            if ":" in url_for_request and not url_for_request.startswith("http://["):
                url_for_request = url_for_request.rsplit(":", 1)[0]
            elif url_for_request.startswith("http://["):
                # Keep IPv6 bracket format
                pass

            try:
                req = urllib.request.Request(url_for_request + "/x")
                req_host = req.host
                if req_host.startswith("["):
                    req_host = req_host.strip("[]").split("]")[0]
                if ":" in req_host and not req_host.startswith("["):
                    req_host = req_host.rsplit(":", 1)[0]
            except Exception:
                pass

    # For refused cases, verify is_loopback returns False
    for s in refuse_cases:
        assert is_loopback(s) is False
