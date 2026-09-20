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
    "host",
    ["127.0.0.1", "127.0.0.1:11434", "localhost", "localhost:11434", "[::1]:11434", "::1", "http://localhost:11434", "127.5.5.5"],
)
def test_loopback_hosts_are_accepted(host):
    assert is_loopback(host)


@pytest.mark.parametrize("host", [
    "10.0.0.5",
    "192.168.1.2:11434",
    "example.com",
    "0.0.0.0",
    "http://ollama.internal:11434",
    "",
    "http://localhost:11434@evil.com",
    "127.0.0.1:80@evil.com",
    "[::1]@evil.com",
    "http://[::1]:11434@evil.com",
])
def test_other_hosts_are_refused(host):
    assert not is_loopback(host)


def test_host_only_strips_scheme_port_and_brackets():
    assert host_only("http://[::1]:11434/api") == "::1"
    assert host_only("localhost:11434") == "localhost"


def test_host_only_strips_userinfo():
    assert host_only("user@localhost:11434") == "localhost"
    assert is_loopback("user@localhost:11434") is True
