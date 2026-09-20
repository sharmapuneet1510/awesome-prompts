import builtins
import subprocess
import sys
from pathlib import Path

import pytest

import interactive_exporter as ie

COVERS = ["R1"]

TOOLS = Path(ie.__file__).resolve().parent


def answer(monkeypatch, *replies):
    queue = list(replies)

    def fake_input(*args):
        if not queue:
            raise EOFError
        return queue.pop(0)

    monkeypatch.setattr(builtins, "input", fake_input)


@pytest.fixture
def spy(monkeypatch):
    calls = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: calls.append((a, k)))
    return calls


@pytest.mark.parametrize("reply", ["", "n", "N", "no", "  ", "maybe"])
def test_anything_but_yes_installs_nothing(monkeypatch, spy, capsys, reply):
    answer(monkeypatch, reply)
    ie.offer_prompt_preflight(Path("/tmp/proj"))
    assert spy == []
    assert "Skipped" in capsys.readouterr().out


def test_the_skip_hint_is_a_command_for_this_project_not_the_current_directory(monkeypatch, spy, capsys):
    answer(monkeypatch, "n")
    ie.offer_prompt_preflight(Path("/tmp/proj"))
    out = capsys.readouterr().out
    assert str(TOOLS / "prompt_preflight" / "setup.py") in out and '--project "/tmp/proj"' in out


def test_a_closed_stdin_counts_as_no(monkeypatch, spy):
    answer(monkeypatch)  # input() raises EOFError
    ie.offer_prompt_preflight(Path("/tmp/proj"))
    assert spy == []


@pytest.mark.parametrize("reply", ["y", "Y", "yes", " YES "])
def test_yes_hands_over_to_the_wizard_for_this_project(monkeypatch, spy, reply):
    answer(monkeypatch, reply)
    ie.offer_prompt_preflight(Path("/tmp/proj"))
    [(args, _)] = spy
    command = args[0]
    assert command[0] == sys.executable and command[2:] == ["--project", "/tmp/proj"]
    assert Path(command[1]) == TOOLS / "prompt_preflight" / "setup.py" and Path(command[1]).exists()


def test_the_offer_explains_privacy_and_that_nothing_is_installed_by_default(monkeypatch, spy, capsys):
    answer(monkeypatch, "n")
    ie.offer_prompt_preflight(Path("/tmp/proj"))
    out = capsys.readouterr().out
    assert "never leave this machine" in out and "unless you say yes" in out and "(y/N)" in out


def stub_main(monkeypatch, confirm=True, export=True):
    calls = []
    for name, value in {
        "print_header": None,
        "get_project_root": Path("/tmp/proj"),
        "resolve_repo_root": Path("/tmp/repo"),
        "get_platforms": ["claude"],
        "get_skills_and_agents": ([], []),
        "confirm_setup": confirm,
        "run_exporter": export,
        "print_next_steps": None,
    }.items():
        monkeypatch.setattr(ie, name, lambda *a, _n=name, _v=value, **k: calls.append(_n) or _v)
    monkeypatch.setattr(ie, "offer_prompt_preflight", lambda root: calls.append(("offer", root)))
    return calls


def test_the_offer_comes_last_after_a_successful_export(monkeypatch):
    calls = stub_main(monkeypatch)
    ie.main()
    assert calls[-2:] == ["print_next_steps", ("offer", Path("/tmp/proj"))]


def test_no_offer_when_the_user_cancels_or_the_export_fails(monkeypatch):
    calls = stub_main(monkeypatch, confirm=False)
    ie.main()
    assert not [c for c in calls if isinstance(c, tuple)]
    calls = stub_main(monkeypatch, export=False)
    ie.main()
    assert not [c for c in calls if isinstance(c, tuple)]


def test_the_plain_non_interactive_exporter_never_mentions_preflight():
    # R1: a plain `exporter.py` run must never ask about, or install, the hook.
    assert "prompt_preflight" not in (TOOLS / "exporter.py").read_text(encoding="utf-8")
