import json
import os
import random
import subprocess
import sys

import pytest

from prompt_preflight import hook
from prompt_preflight.errors import ModelUnavailable

from .fake_ollama import FakeOllama

COVERS = ["R1", "R3", "R4", "R6", "R7", "R8", "R11", "R14"]

REAL_WORK = "write a python function that parses iso dates from log lines"


class Clock:
    def __init__(self, now=1_000_000.0):
        self.now = now

    def __call__(self):
        return self.now


def event(prompt, session="s1"):
    return json.dumps({"hook_event_name": "UserPromptSubmit", "session_id": session, "prompt": prompt})


def configure(root, **values):
    (root / "config.json").write_text(json.dumps(values), encoding="utf-8")


def call(root, prompt, session="s1", model_call=None, clock=None, env=None):
    if not (root / "config.json").exists():
        configure(root)  # a configured install with all defaults; the wizard always writes config.json
    return hook.run(event(prompt, session), str(root), env=env or {}, model_call=model_call, clock=clock or Clock())


def verdict(reply):
    return lambda text: dict({"verdict": "pass", "confidence": 0.9}, **reply)


# ---------- in-process behavior -------------------------------------------------------------


def test_tier1_google_speaks_to_the_user(tmp_path):
    out = call(tmp_path, "what is the capital of France")
    assert out == {"systemMessage": 'Prompt Preflight: quick lookup — try Google: "what is the capital of France"'}


def test_everything_is_silent_for_a_prompt_that_needs_no_advice(tmp_path):
    assert call(tmp_path, REAL_WORK) is None


@pytest.mark.parametrize("env,cfg", [({"PROMPT_PREFLIGHT": "off"}, {}), ({"PROMPT_PREFLIGHT": " OFF "}, {}), ({}, {"enabled": False})])
def test_kill_switches_disable_it_instantly(tmp_path, env, cfg):
    configure(tmp_path, **cfg)
    assert call(tmp_path, "what is the capital of France", env=env) is None


@pytest.mark.parametrize("stdin", ["", "not json", "[]", "{}", '{"prompt": 5}', '{"prompt": null}', "null"])
def test_bad_input_is_ignored(tmp_path, stdin):
    configure(tmp_path)  # without a config file run() returns at the bypass and never reads the input
    assert hook.run(stdin, str(tmp_path), env={}) is None


def test_clarify_and_refine_only_on_the_first_prompt_of_a_session(tmp_path):
    configure(tmp_path, model="tiny:1b")
    reply = verdict({"verdict": "clarify", "missing": ["which file"]})
    first = call(tmp_path, "make the app work better please", session="A", model_call=reply)
    second = call(tmp_path, "make the app work better please", session="A", model_call=reply)
    other = call(tmp_path, "make the app work better please", session="B", model_call=reply)
    assert first is not None and "which file" in first["systemMessage"]
    assert second is None
    assert other is not None


def test_a_failing_model_starts_a_cooldown_and_says_so_once(tmp_path):
    configure(tmp_path, model="tiny:1b", cooldown_s=300)
    clock = Clock()
    calls = []

    def down(text):
        calls.append(text)
        raise ModelUnavailable("down")

    first = call(tmp_path, REAL_WORK, session="A", model_call=down, clock=clock)
    assert "heuristics-only" in first["systemMessage"]
    assert call(tmp_path, REAL_WORK, session="A", model_call=down, clock=clock) is None
    assert len(calls) == 1  # the cooldown kept the second prompt away from the model
    clock.now += 301
    assert call(tmp_path, REAL_WORK, session="A", model_call=down, clock=clock) is None  # notice already shown today
    assert len(calls) == 2


def test_without_a_model_it_runs_heuristics_only_and_never_nags(tmp_path):
    configure(tmp_path, model="")
    assert call(tmp_path, REAL_WORK) is None
    assert call(tmp_path, "what is the capital of France") is not None


def test_block_mode_blocks_once_then_lets_the_identical_prompt_through(tmp_path):
    configure(tmp_path, mode="block")
    first = call(tmp_path, "what is the capital of France", session="s1")
    assert first["decision"] == "block"
    assert call(tmp_path, "what is the capital of France", session="s1") is None  # the resend goes through
    assert call(tmp_path, "what is the capital of France", session="s2")["decision"] == "block"  # override was single-use


def test_block_mode_never_traps_the_user_when_state_cannot_be_saved(tmp_path, monkeypatch):
    configure(tmp_path, mode="block")
    monkeypatch.setattr(hook.State, "_save", lambda self: False)  # e.g. a read-only install directory
    for _ in range(3):
        out = call(tmp_path, "what is the capital of France")
        assert "decision" not in out and "Google" in out["systemMessage"]  # advised, never blocked


def test_block_mode_only_ever_blocks_the_first_prompt_of_a_session(tmp_path):
    configure(tmp_path, mode="block")
    first = call(tmp_path, "what is the capital of France", session="A")
    later = call(tmp_path, "what is the current status", session="A")
    assert first["decision"] == "block"
    assert "decision" not in later and "Google" in later["systemMessage"]  # advised, never blocked, mid-session
    assert "decision" not in call(tmp_path, "what is the current status", session="")  # no session id: never blocked


def test_block_override_expires(tmp_path):
    configure(tmp_path, mode="block", override_window_s=60)
    clock = Clock()
    assert call(tmp_path, "what is the capital of France", session="s1", clock=clock)["decision"] == "block"
    clock.now += 61
    assert call(tmp_path, "what is the capital of France", session="s2", clock=clock)["decision"] == "block"  # too late to override


@pytest.mark.parametrize("configured,sent", [(8000, 4000), (30000, 4000), (1500, 1500)])
def test_the_model_budget_always_fits_inside_the_hook_timeout(tmp_path, monkeypatch, configured, sent):
    configure(tmp_path, model="tiny:1b", budget_ms=configured)
    seen = []
    monkeypatch.setattr(hook.ollama_client, "classify", lambda text, cfg: seen.append(cfg["budget_ms"]) or {"verdict": "pass", "confidence": 0.9})
    call(tmp_path, REAL_WORK)
    assert seen == [sent] and hook.MAX_MODEL_BUDGET_MS < 5000


def test_the_log_has_no_prompt_text_by_default(tmp_path):
    call(tmp_path, "what is the capital of Zanzibarland")
    log = (tmp_path / "preflight.log").read_text(encoding="utf-8")
    assert "Zanzibarland" not in log and '"verdict": "google"' in log


def test_the_log_includes_the_prompt_only_when_asked(tmp_path):
    configure(tmp_path, log_prompts=True)
    call(tmp_path, "what is the capital of Zanzibarland")
    assert "Zanzibarland" in (tmp_path / "preflight.log").read_text(encoding="utf-8")


def test_the_log_rotates_when_it_grows_too_large(tmp_path, monkeypatch):
    monkeypatch.setattr(hook, "MAX_LOG_BYTES", 200)
    for i in range(20):
        call(tmp_path, "what is the capital of France", session="s%d" % i)
    assert (tmp_path / "preflight.log.1").exists()


def test_a_real_model_reply_flows_end_to_end_through_the_fake_server(tmp_path):
    with FakeOllama(reply={"verdict": "google", "confidence": 0.95, "google_query": "python reverse list"}) as server:
        configure(tmp_path, model="tiny:1b", ollama_host=server.host, budget_ms=1000)
        out = hook.run(event("how do I reverse a list in python"), str(tmp_path), env={})
    assert out == {"systemMessage": 'Prompt Preflight: quick lookup — try Google: "python reverse list"'}


def test_run_survives_arbitrary_json_shapes_and_random_text(tmp_path):
    configure(tmp_path)
    rng = random.Random(7)
    shapes = ['{"prompt": "hello there general", "session_id": 5}', '{"prompt": ["a"]}', '{"session_id": "x"}', "[[[[", '"str"', "12"]
    for text in shapes + ["".join(chr(rng.randrange(1, 0x2FF)) for _ in range(rng.randrange(1, 300))) for _ in range(40)]:
        result = hook.run(text, str(tmp_path), env={})
        assert result is None or isinstance(result, dict)


def test_main_exits_zero_and_prints_nothing_even_if_run_explodes(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(hook, "run", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(sys, "stdin", type("S", (), {"buffer": type("B", (), {"read": staticmethod(lambda n: b"{}")})()})())
    with pytest.raises(SystemExit) as info:
        hook.main(str(tmp_path))
    assert info.value.code == 0
    assert capsys.readouterr().out == ""
    assert "RuntimeError" in (tmp_path / "preflight.log").read_text(encoding="utf-8")


def test_an_internal_error_never_puts_the_prompt_in_the_log(tmp_path, monkeypatch):
    monkeypatch.setattr(hook, "run", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("the prompt said zebra-token-91")))
    monkeypatch.setattr(sys, "stdin", type("S", (), {"buffer": type("B", (), {"read": staticmethod(lambda n: b"{}")})()})())
    with pytest.raises(SystemExit):
        hook.main(str(tmp_path))
    log = (tmp_path / "preflight.log").read_text(encoding="utf-8")
    assert "RuntimeError at test_hook.py" in log and "zebra-token-91" not in log


def test_main_reads_no_more_than_the_stdin_cap(tmp_path, monkeypatch):
    asked = []
    buffer = type("B", (), {"read": staticmethod(lambda n: asked.append(n) or b"")})()
    monkeypatch.setattr(sys, "stdin", type("S", (), {"buffer": buffer})())
    with pytest.raises(SystemExit):
        hook.main(str(tmp_path))
    assert asked == [hook.MAX_STDIN_BYTES]


def test_without_a_config_file_it_does_nothing_at_all(tmp_path):
    # R14: unconfigured means bypassed. No output, and no state, log, or any other file is written.
    assert hook.run(event("what is the capital of France"), str(tmp_path), env={}) is None
    assert os.listdir(tmp_path) == []


# ---------- the real contract: run the launcher as Claude Code does --------------------------


def run_launcher(root, stdin, env_extra=None, python_flags=()):
    env = {k: v for k, v in os.environ.items() if k != "PROMPT_PREFLIGHT"}
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, *python_flags, str(root / "hook.py")],
        input=stdin,
        capture_output=True,
        env=env,
        cwd=str(root.parent),
        timeout=60,
    )


def test_launcher_prints_exactly_one_json_object_for_a_google_prompt(installed_root):
    done = run_launcher(installed_root, event("what is the capital of France").encode())
    assert done.returncode == 0
    parsed = json.loads(done.stdout.decode())  # the whole of stdout is one JSON document
    assert list(parsed) == ["systemMessage"] and "try Google" in parsed["systemMessage"]


@pytest.mark.parametrize(
    "stdin",
    [b"", b"\xff\xfe\x00garbage\x80", b"not json at all", b"{}", event("").encode(), b"a" * 3_000_000, b'{"prompt": "' + b"x" * 2_000_000],
    ids=["empty", "binary", "text", "empty-object", "empty-prompt", "huge-text", "huge-truncated-json"],
)
def test_launcher_exits_zero_and_prints_nothing_on_hostile_input(installed_root, stdin):
    done = run_launcher(installed_root, stdin)
    assert done.returncode == 0
    assert done.stdout == b""


def test_launcher_honours_the_environment_kill_switch(installed_root):
    done = run_launcher(installed_root, event("what is the capital of France").encode(), {"PROMPT_PREFLIGHT": "off"})
    assert (done.returncode, done.stdout) == (0, b"")


def test_launcher_honours_enabled_false_in_config(installed_root):
    configure(installed_root, enabled=False)
    done = run_launcher(installed_root, event("what is the capital of France").encode())
    assert (done.returncode, done.stdout) == (0, b"")


def test_a_broken_install_still_exits_zero_silently(installed_root):
    import shutil

    shutil.rmtree(installed_root / "prompt_preflight")
    done = run_launcher(installed_root, event("what is the capital of France").encode())
    assert (done.returncode, done.stdout) == (0, b"")


def feature_modules(stderr):
    """Modules of the feature that Python imported, from `-X importtime` output (exact names only).

    Exact names matter: a machine with `pip install -e token_optimizer` imports a finder called
    `__editable___token_optimizer_..._finder` at every interpreter start, which is not the hook.
    """
    names = [
        line.rsplit("|", 1)[1].strip()
        for line in stderr.decode("utf-8", "replace").splitlines()
        if line.startswith("import time:") and "|" in line
    ]
    return [n for n in names if n.split(".")[0] in ("prompt_preflight", "token_optimizer")]


def test_launcher_is_a_complete_bypass_when_unconfigured(installed_root):
    # R14: with no config.json the launcher leaves before importing anything, and writes nothing.
    (installed_root / "config.json").unlink()
    before = sorted(os.listdir(installed_root))
    done = run_launcher(installed_root, event("what is the capital of France").encode(), python_flags=["-X", "importtime"])
    assert (done.returncode, done.stdout) == (0, b"")
    assert feature_modules(done.stderr) == []
    assert sorted(os.listdir(installed_root)) == before  # no state.json, no preflight.log


def test_the_import_probe_would_notice_if_a_configured_hook_loaded_its_modules(installed_root):
    # Guards the test above against passing vacuously: configured, the same probe DOES see the imports.
    done = run_launcher(installed_root, event("what is the capital of France").encode(), python_flags=["-X", "importtime"])
    assert done.returncode == 0
    assert "prompt_preflight.hook" in feature_modules(done.stderr) and "token_optimizer" in feature_modules(done.stderr)
