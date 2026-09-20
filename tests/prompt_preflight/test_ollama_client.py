import copy
import http.client
import json
import socket
import urllib.request

import pytest

from prompt_preflight.config import DEFAULTS
from prompt_preflight.errors import ModelUnavailable
from prompt_preflight.ollama_client import SCHEMA, build_request, classify, parse_reply

from .fake_ollama import GOOD, FakeOllama

COVERS = ["R3", "R6", "R8"]


def cfg(host, **over):
    merged = copy.deepcopy(DEFAULTS)
    merged.update({"model": "tiny:1b", "ollama_host": host, "budget_ms": 800})
    merged.update(over)
    return merged


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_valid_reply_is_parsed_and_normalized():
    with FakeOllama() as server:
        assert classify("how do I reverse a list", cfg(server.host)) == dict(GOOD, confidence=0.9)


def test_request_carries_schema_keep_alive_model_and_delimited_prompt():
    with FakeOllama() as server:
        classify("secret question", cfg(server.host, keep_alive="15m"))
    request = server.requests[0]
    body = request["body"]
    assert request["path"] == "/api/chat"
    assert body["format"] == SCHEMA and body["keep_alive"] == "15m" and body["model"] == "tiny:1b"
    assert body["stream"] is False and body["options"] == {"temperature": 0}
    assert body["messages"][1]["content"] == "<prompt>\nsecret question\n</prompt>"
    assert "DATA" in body["messages"][0]["content"]


@pytest.mark.parametrize("mode", ["bad_json", "off_schema", "http_500"])
def test_bad_replies_raise_model_unavailable(mode):
    with FakeOllama(mode=mode) as server:
        with pytest.raises(ModelUnavailable):
            classify("anything at all here", cfg(server.host))


def test_a_slow_model_is_abandoned_at_the_budget():
    with FakeOllama(mode="slow", delay=2.0) as server:
        with pytest.raises(ModelUnavailable):
            classify("anything at all here", cfg(server.host, budget_ms=300))


def test_a_closed_port_fails_fast():
    with pytest.raises(ModelUnavailable):
        classify("anything at all here", cfg("127.0.0.1:%d" % free_port()))


def test_no_model_configured_means_unavailable_without_any_network_call():
    def never(*args, **kwargs):
        raise AssertionError("network must not be touched")

    with pytest.raises(ModelUnavailable):
        classify("anything at all here", cfg("127.0.0.1:1", model=""), opener=never)


@pytest.mark.parametrize("host", ["10.0.0.5:11434", "ollama.internal:11434", "http://example.com"])
def test_non_loopback_hosts_are_refused_before_any_network_call(host):
    def never(*args, **kwargs):
        raise AssertionError("network must not be touched")

    with pytest.raises(ModelUnavailable, match="non-loopback"):
        classify("anything at all here", cfg(host), opener=never)


def test_allow_remote_lifts_the_loopback_restriction():
    seen = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return json.dumps({"message": {"content": json.dumps(GOOD)}}).encode()

    def opener(request, timeout):
        seen.append(request.full_url)
        return Response()

    classify("anything at all here", cfg("10.0.0.5:11434", allow_remote=True), opener=opener)
    assert seen == ["http://10.0.0.5:11434/api/chat"]


def test_environment_proxies_are_never_used(monkeypatch):
    # urllib.request.urlopen caches a global opener the first time anything uses it, which would
    # hide the proxy variables below. Clear the cache so this test really exercises the proxy path.
    monkeypatch.setattr(urllib.request, "_opener", None, raising=False)
    # A proxy that nothing listens on: if urllib honored it, the request to the fake server would fail.
    monkeypatch.setenv("http_proxy", "http://127.0.0.1:%d" % free_port())
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:%d" % free_port())
    monkeypatch.delenv("no_proxy", raising=False)
    monkeypatch.delenv("NO_PROXY", raising=False)
    with FakeOllama() as server:
        assert classify("how do I reverse a list", cfg(server.host))["verdict"] == "google"


@pytest.mark.parametrize(
    "body",
    [
        None,
        {},
        {"message": {}},
        {"message": {"content": "[]"}},
        {"message": {"content": json.dumps({"verdict": "google"})}},
        {"message": {"content": json.dumps({"verdict": "google", "confidence": True})}},
        {"message": {"content": json.dumps({"verdict": "google", "confidence": 1.5})}},
        {"message": {"content": json.dumps({"verdict": "other", "confidence": 0.5})}},
    ],
)
def test_parse_reply_rejects_anything_off_schema(body):
    with pytest.raises(ModelUnavailable):
        parse_reply(body)


def test_parse_reply_drops_wrongly_typed_optional_fields():
    reply = {"verdict": "clarify", "confidence": 1, "missing": ["a", 3, "b"], "refined_request": 7, "google_query": None}
    out = parse_reply({"message": {"content": json.dumps(reply)}})
    assert out == {"verdict": "clarify", "confidence": 1.0, "missing": ["a", "b"]}


def test_build_request_does_not_leak_the_prompt_into_the_system_message():
    body = build_request(cfg("127.0.0.1:1"), "UNIQUE-PROMPT-TEXT")
    assert "UNIQUE-PROMPT-TEXT" not in body["messages"][0]["content"]


# ---------- the address the request really goes to ------------------------------------------


class _Ok:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return json.dumps({"message": {"content": json.dumps(GOOD)}}).encode()


def requested_url(host, **over):
    seen = []

    def opener(request, timeout):
        seen.append(request.full_url)
        return _Ok()

    classify("anything at all here", cfg(host, **over), opener=opener)
    return seen[0]


@pytest.mark.parametrize(
    "host,url",
    [
        ("127.0.0.1:11434", "http://127.0.0.1:11434/api/chat"),
        ("localhost", "http://localhost/api/chat"),
        ("[::1]:11434", "http://[::1]:11434/api/chat"),
        ("::1", "http://[::1]/api/chat"),  # a bare IPv6 host must be bracketed, or http.client mis-parses it
        ("http://localhost:11434", "http://localhost:11434/api/chat"),
        ("https://localhost:11434/ignored/path", "https://localhost:11434/api/chat"),
    ],
)
def test_the_request_is_built_from_the_validated_host_and_port(host, url):
    assert requested_url(host) == url


@pytest.mark.parametrize(
    "host",
    [
        "http://evil.com?@localhost",
        "http://evil.com#@localhost",
        "http://localhost:11434@evil.com",
        "localhost:abc",
        "localhost:99999",
        "ftp://localhost",
        "localhost?x=1",
    ],
)
def test_a_host_that_is_not_plain_host_and_port_is_refused_before_any_network_call(host):
    def never(*args, **kwargs):
        raise AssertionError("network must not be touched")

    with pytest.raises(ModelUnavailable, match="invalid host"):
        classify("anything at all here", cfg(host), opener=never)


def test_allow_remote_still_requires_a_plain_host():
    def never(*args, **kwargs):
        raise AssertionError("network must not be touched")

    with pytest.raises(ModelUnavailable, match="invalid host"):
        classify("anything at all here", cfg("evil.com?@localhost", allow_remote=True), opener=never)
    assert requested_url("ollama.internal:11434", allow_remote=True) == "http://ollama.internal:11434/api/chat"


@pytest.mark.parametrize("error", [http.client.InvalidURL("x"), http.client.IncompleteRead(b""), http.client.BadStatusLine("x")])
def test_http_client_errors_become_model_unavailable(error):
    def broken(request, timeout):
        raise error

    with pytest.raises(ModelUnavailable):
        classify("anything at all here", cfg("127.0.0.1:11434"), opener=broken)
