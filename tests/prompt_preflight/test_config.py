import ipaddress
import itertools
import json
import random
import urllib.parse
import urllib.request

import pytest

from prompt_preflight.config import DEFAULTS, host_only, is_loopback, load_config

COVERS = ["R8", "R9"]

# Module-level constants for host_only test cases
ACCEPT_HOSTS = {
    "127.0.0.1": "127.0.0.1",
    "127.0.0.1:11434": "127.0.0.1",
    "localhost": "localhost",
    "localhost:11434": "localhost",
    "[::1]:11434": "::1",
    "[::1]": "::1",
    "::1": "::1",
    "http://localhost:11434": "localhost",
    "http://localhost:11434/api/chat": "localhost",
    "https://[::1]:11434/": "::1",
    "HTTP://LocalHost:11434": "LocalHost",
}

REFUSE_HOSTS = {
    "http://localhost:11434@evil.com": "",
    "127.0.0.1:80@evil.com": "",
    "[::1]@evil.com": "",
    "http://[::1]:11434@evil.com": "",
    "user@localhost:11434": "",
    "http://evil.com?@localhost": "",
    "http://evil.com#@localhost": "",
    "http://evil.com:80?@127.0.0.1:11434": "",
    "localhost?x=1": "",
    "localhost#frag": "",
    "http://evil.com\\@localhost": "",
    "localhost:abc": "",
    "localhost:": "",
    "[::1": "",
    "ftp://localhost": "",
    "file:///etc/passwd": "",
    "loc alhost": "",
    "local%68ost": "",
    "": "",
    "   ": "",
    "http://": "",
    "[localhost]": "",
    "[127.0.0.1]": "",
    "localhost:65536": "",
    "localhost:99999999": "",
    "localhost:²": "",
}


def build_test_corpus():
    """Build comprehensive test corpus from token combinations."""
    schemes = ["", "http://", "https://", "HTTP://", "ftp://", "file://"]
    userinfo = ["", "u@", "localhost:1@", "a@b@", "evil.com@"]
    hosts = [
        "localhost", "LOCALHOST", "127.0.0.1", "127.0.0.2", "[::1]", "::1",
        "evil.com", "0.0.0.0", "127.1", "localhost.evil.com", "127.0.0.1.evil.com",
        "[::ffff:127.0.0.1]", "2130706433", "10.0.0.5"
    ]
    ports = ["", ":11434", ":80", ":", ":abc", ":99999999"]
    tails = [
        "", "/", "/api/chat", "?x", "#y", "?@localhost", "#@localhost",
        "?@127.0.0.1:11434", "/x@localhost", "\\@localhost", "\\",
        "%40localhost", " ", "\t", "\n", "@evil.com", ":11434@evil.com",
        ".", "%2f", ";@localhost"
    ]

    # Generate all combinations
    all_strings = [
        scheme + userinfo_part + host + port + tail
        for scheme, userinfo_part, host, port, tail in itertools.product(schemes, userinfo, hosts, ports, tails)
    ]

    # Sample if too many
    if len(all_strings) > 60000:
        rng = random.Random(1234)
        all_strings = rng.sample(all_strings, 6000)

    # Add all strings from accept/refuse tables
    all_strings.extend(ACCEPT_HOSTS.keys())
    all_strings.extend(REFUSE_HOSTS.keys())

    return list(set(all_strings))  # Deduplicate


def is_hostile(s):
    """Check if a string's host is intentionally hostile (not loopback)."""
    # Mark as hostile if:
    # - host token is in the hostile list
    # - AND userinfo token is "" (no "@")
    # - AND tail token is in ["", "/", "/api/chat"]
    hostile_hosts = ["evil.com", "0.0.0.0", "localhost.evil.com", "127.0.0.1.evil.com", "10.0.0.5"]

    # Extract tokens from s
    # This is a simplification: just check if any hostile host appears with no userinfo
    if "@" in s:
        return False  # Has userinfo

    for hostile_host in hostile_hosts:
        if hostile_host in s:
            # Check that the tail is simple (no query/fragment/path that changes meaning)
            authority_end = s.find("/") if "/" in s else len(s)
            authority = s[:authority_end]
            if hostile_host in authority:
                # Extract the tail after authority
                tail = s[authority_end:] if authority_end < len(s) else ""
                if tail in ["", "/", "/api/chat"]:
                    return True
    return False


def gate_violations(gate, corpus):
    """Check gate function against corpus. Returns list of (string, reason) violations."""
    violations = []

    for s in corpus:
        t = s.strip()
        gate_result = gate(s)

        # REVERSE: if s is hostile, gate must be False
        if is_hostile(s) and gate_result:
            violations.append((s, f"REVERSE: hostile host but gate returned True"))
            continue

        # FORWARD SAFETY: if gate is True, verify urllib agrees
        if gate_result:
            # Extract the host part that host_only extracted
            extracted_host = gate(s) if hasattr(gate, '__name__') and 'is_loopback' in str(gate) else None

            # Detect bare IPv6 (multiple colons, no brackets, no scheme, not host:port)
            # Bare IPv6 example: ::1, 2001:db8::1 (not localhost:80 or http://::1)
            t_no_scheme = t.split("://", 1)[-1].split("/", 1)[0]
            # Bare IPv6: has "://" in original? No. Starts with "["? No. Has 2+ colons? Yes.
            is_bare_ipv6 = "://" not in t and not t_no_scheme.startswith("[") and t_no_scheme.count(":") >= 2

            if is_bare_ipv6:
                # For bare IPv6, validate directly
                try:
                    ipaddress.IPv6Address(t_no_scheme)
                except ValueError:
                    violations.append((s, f"FORWARD: bare IPv6 '{t_no_scheme}' is not valid"))
            else:
                # Try urlsplit for non-bare-IPv6
                try:
                    url_for_urlsplit = t if "://" in t else "//" + t
                    parsed = urllib.parse.urlsplit(url_for_urlsplit)
                    hostname = parsed.hostname

                    if hostname is None:
                        violations.append((s, f"FORWARD: gate=True but urlsplit gave no hostname"))
                        continue

                    # Check if hostname is loopback
                    is_loopback_host = False
                    if hostname.lower() == "localhost":
                        is_loopback_host = True
                    else:
                        try:
                            is_loopback_host = ipaddress.ip_address(hostname).is_loopback
                        except ValueError:
                            pass

                    if not is_loopback_host:
                        violations.append((s, f"FORWARD: gate=True but urlsplit hostname '{hostname}' is not loopback"))
                        continue

                except ValueError as e:
                    violations.append((s, f"FORWARD: gate=True but urlsplit raised ValueError: {e}"))
                    continue

            # Try urllib.request.Request (skip for bare IPv6)
            if not is_bare_ipv6:
                try:
                    authority = t.split("://", 1)[-1].split("/", 1)[0]
                    url_for_request = "http://" + authority + "/api/chat"
                    req = urllib.request.Request(url_for_request)
                    req_host = req.host

                    # Strip port and brackets
                    if req_host.startswith("["):
                        req_host = req_host.split("]")[0][1:]
                    elif ":" in req_host:
                        req_host = req_host.rsplit(":", 1)[0]

                    # Check if req_host is loopback
                    is_loopback_req_host = False
                    if req_host.lower() == "localhost":
                        is_loopback_req_host = True
                    else:
                        try:
                            is_loopback_req_host = ipaddress.ip_address(req_host).is_loopback
                        except ValueError:
                            pass

                    if not is_loopback_req_host:
                        violations.append((s, f"FORWARD: gate=True but urllib.request host '{req_host}' is not loopback"))

                except Exception as e:
                    violations.append((s, f"FORWARD: gate=True but urllib.request raised {type(e).__name__}: {e}"))

    return violations


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
        ("override_window_s", 0),  # 0 would make every block permanent
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


@pytest.mark.parametrize("input_host,expected_host", list(ACCEPT_HOSTS.items()))
def test_host_only_accepts_valid_hosts(input_host, expected_host):
    assert host_only(input_host) == expected_host


@pytest.mark.parametrize("refused_host,expected_empty", list(REFUSE_HOSTS.items()))
def test_host_only_refuses_invalid_hosts(refused_host, expected_empty):
    assert host_only(refused_host) == expected_empty


@pytest.mark.parametrize("input_host", list(ACCEPT_HOSTS.keys()))
def test_is_loopback_accepts_valid_loopback_hosts(input_host):
    assert is_loopback(input_host) is True


@pytest.mark.parametrize("refused_host", list(REFUSE_HOSTS.keys()))
def test_is_loopback_refuses_invalid_or_remote_hosts(refused_host):
    assert is_loopback(refused_host) is False


def test_differential_is_loopback_vs_urllib():
    """Real differential test: gate_violations must return no violations for is_loopback."""
    corpus = build_test_corpus()
    violations = gate_violations(is_loopback, corpus)
    assert violations == [], f"Found {len(violations)} violations: {violations[:5]}"


def test_differential_vacuity_always_true_gate_fails():
    """Non-vacuity: an always-true gate must be caught by gate_violations."""
    corpus = build_test_corpus()
    violations = gate_violations(lambda s: True, corpus)
    assert len(violations) > 0, "gate_violations should catch an always-true gate"
    # Should have both forward and reverse violations
    forward_viols = [v for v in violations if "FORWARD" in v[1]]
    reverse_viols = [v for v in violations if "REVERSE" in v[1]]
    assert len(forward_viols) > 0, "Should have forward-safety violations"
    assert len(reverse_viols) > 0, "Should have reverse violations"


def test_differential_corpus_exercises_gate():
    """Non-vacuity: corpus must exercise the gate significantly."""
    corpus = build_test_corpus()
    true_count = sum(1 for s in corpus if is_loopback(s))
    false_count = sum(1 for s in corpus if not is_loopback(s))
    assert true_count >= 100, f"Corpus should have >=100 True cases, got {true_count}"
    assert false_count >= 100, f"Corpus should have >=100 False cases, got {false_count}"


def test_regression_round2_bypasses():
    """Regression: the 4 round-2 bypasses must be refused."""
    assert host_only("http://evil.com?@localhost") == ""
    assert host_only("http://evil.com#@localhost") == ""
    assert host_only("http://evil.com:80?@127.0.0.1:11434") == ""
    assert host_only("http://localhost:11434@evil.com") == ""
