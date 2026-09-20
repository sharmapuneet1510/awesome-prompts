import json
import os
import re
import shutil
import subprocess
import sys

import pytest

from prompt_preflight import defaults, setup

COVERS = ["R1", "R10", "R11"]


class ScriptedIO:
    """Answers the wizard's questions from queues, and records what it was asked."""

    def __init__(self, yes=(), choices=()):
        self.yes, self.choices = list(yes), list(choices)
        self.said, self.asked = [], []

    def say(self, text=""):
        self.said.append(text)

    def ask_yes_no(self, question, default=False):
        self.asked.append(question)
        return self.yes.pop(0) if self.yes else default

    def choose(self, question, options, default=0):
        self.asked.append(question)
        self.options = list(options)
        return self.choices.pop(0) if self.choices else default

    @property
    def text(self):
        return "\n".join(self.said)


class FakeAdmin:
    def __init__(self, installed=True, running=True, models=None, pull_ok=True, start_ok=True):
        self.is_installed, self.running, self.pull_ok, self.start_ok = installed, running, pull_ok, start_ok
        self._models = models if models is not None else [{"name": "llama3:latest", "size": 4.66e9}]
        self.pulled, self.started = [], 0

    def installed(self):
        return self.is_installed

    def is_running(self):
        return self.running

    def models(self):
        return self._models

    def pull(self, name):
        self.pulled.append(name)
        return self.pull_ok

    def start(self):
        self.started += 1
        if self.start_ok:
            self.running = True
        return self.start_ok


@pytest.fixture
def env(tmp_path):
    home, project = tmp_path / "home", tmp_path / "proj"
    home.mkdir()
    project.mkdir()
    return home, project


def flags(env, *extra):
    home, project = env
    return ["--home", str(home), "--project", str(project), *extra]


def local_settings(env):
    return env[1] / ".claude" / "settings.local.json"


def user_settings(env):
    return env[0] / ".claude" / "settings.json"


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def entries(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return [h for g in data["hooks"]["UserPromptSubmit"] for h in g["hooks"]]


# ---------- consent: nothing without a yes ----------------------------------------------------


def test_declining_the_first_question_changes_nothing(env, tmp_path):
    before = snapshot(tmp_path)
    io = ScriptedIO(yes=[False])
    assert setup.main(flags(env), io=io, ollama=FakeAdmin()) == 0
    assert snapshot(tmp_path) == before
    assert io.asked == ["Set up the Prompt Preflight?"] and "Nothing was installed" in io.text


def test_declining_the_final_confirmation_writes_downloads_and_starts_nothing(env, tmp_path):
    admin = FakeAdmin(running=False)
    before = snapshot(tmp_path)
    io = ScriptedIO(yes=[True, True, False], choices=[0])  # consent, start Ollama, ...install? no
    assert setup.main(flags(env, "--model", "tiny:1b"), io=io, ollama=admin) == 0
    assert snapshot(tmp_path) == before
    assert admin.pulled == [] and admin.started == 0


def test_dry_run_writes_nothing_and_shows_the_diff(env, tmp_path):
    admin = FakeAdmin(models=[])
    before = snapshot(tmp_path)
    assert setup.main(flags(env, "--yes", "--scope", "local", "--model", "tiny:1b", "--dry-run"), io=(io := ScriptedIO()), ollama=admin) == 0
    assert snapshot(tmp_path) == before
    assert admin.pulled == [] and admin.started == 0
    assert "Dry run" in io.text and "+" in io.text and "prompt-preflight/hook.py" in io.text
    assert "download the model tiny:1b" in io.text


@pytest.fixture(autouse=True)
def no_model_traffic(request, monkeypatch):
    """The real self-test runs the installed hook, which calls a real local Ollama when a model is configured.
    Tests must never reach one, so the self-test is stubbed unless a test asks for `real_self_test`."""
    if "real_self_test" not in request.fixturenames:
        monkeypatch.setattr(setup, "_self_test", lambda install_dir, io: True)


@pytest.fixture
def real_self_test():
    return None


# ---------- install ---------------------------------------------------------------------------


def test_install_local_writes_the_layout_and_one_hook_entry(env):
    assert setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin()) == 0
    root = env[1] / ".claude" / "prompt-preflight"
    assert {p.name for p in root.iterdir()} == {"hook.py", "prompt_preflight", "token_optimizer", "config.json", ".gitignore"}
    assert (root / ".gitignore").read_text() == "*\n"
    config = json.loads((root / "config.json").read_text())
    assert config["model"] == "" and config["installed_version"]
    [entry] = entries(local_settings(env))
    assert entry == {"type": "command", "command": 'python3 "%s" || true' % (root / "hook.py"), "timeout": 5}


def test_copy_files_ships_only_what_the_hook_needs(tmp_path):
    source_cache = setup.TOOLS_DIR / "prompt_preflight" / "__pycache__"
    junk = source_cache / "junk.pyc"
    source_cache.mkdir(exist_ok=True)  # make sure the source tree really has bytecode to leave out
    junk.write_bytes(b"x")
    target = tmp_path / "out"
    try:
        setup.copy_files(target)
    finally:
        junk.unlink()
    names = {p.relative_to(target).as_posix() for p in target.rglob("*")}
    assert {"hook.py", "prompt_preflight/decide.py", "prompt_preflight/hook.py", "token_optimizer/analyzer.py", ".gitignore"} <= names
    assert not [n for n in names if "__pycache__" in n or n.endswith(".pyc")]
    assert "prompt_preflight/eval" not in names and "prompt_preflight/setup.py" not in names
    assert "token_optimizer/README.md" not in names and "token_optimizer/setup.py" not in names


def test_local_scope_never_touches_the_committed_project_settings_or_the_user_file(env):
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin())
    assert not (env[1] / ".claude" / "settings.json").exists()
    assert not user_settings(env).exists()


def test_user_scope_installs_under_the_home_directory(env):
    setup.main(flags(env, "--yes", "--scope", "user", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin())
    assert (env[0] / ".claude" / "prompt-preflight" / "hook.py").exists()
    assert len(entries(user_settings(env))) == 1
    assert not (env[1] / ".claude").exists()


def test_yes_without_a_scope_defaults_to_local(env):
    setup.main(flags(env, "--yes", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin())
    assert local_settings(env).exists() and not user_settings(env).exists()


def test_the_scope_question_is_asked_when_no_flag_is_given(env):
    io = ScriptedIO(yes=[True, True], choices=[1])  # consent, then scope=user, then confirm
    setup.main(flags(env, "--no-model"), io=io, ollama=FakeAdmin())
    assert user_settings(env).exists() and not local_settings(env).exists()
    assert "Where should it be installed?" in io.asked


def test_existing_settings_are_preserved_and_backed_up(env):
    path = local_settings(env)
    path.parent.mkdir(parents=True)
    original = {"model": "sonnet", "hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": "lint.sh"}]}]}}
    path.write_text(json.dumps(original), encoding="utf-8")
    io = ScriptedIO()
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=io, ollama=FakeAdmin())
    assert json.loads(path.read_text())["model"] == "sonnet"
    assert {h["command"] for h in entries(path)} >= {"lint.sh"}
    backups = [p for p in path.parent.iterdir() if ".bak-" in p.name]
    assert len(backups) == 1 and json.loads(backups[0].read_text()) == original
    assert "Backed up" in io.text


def test_invalid_settings_json_stops_before_any_change(env):
    path = local_settings(env)
    path.parent.mkdir(parents=True)
    path.write_text("{ this is not json", encoding="utf-8")
    io = ScriptedIO()
    assert setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=io, ollama=FakeAdmin()) == 1
    assert path.read_text() == "{ this is not json"
    assert not (path.parent / "prompt-preflight").exists()
    assert "Nothing was changed" in io.text


def test_installing_twice_keeps_one_entry_and_the_users_config_edits(env):
    args = flags(env, "--yes", "--scope", "local", "--no-model")
    setup.main(args, io=ScriptedIO(), ollama=FakeAdmin())
    config = env[1] / ".claude" / "prompt-preflight" / "config.json"
    edited = json.loads(config.read_text())
    edited["mode"], edited["min_confidence"] = "block", 0.95
    config.write_text(json.dumps(edited), encoding="utf-8")
    setup.main(args, io=ScriptedIO(), ollama=FakeAdmin())
    assert len(entries(local_settings(env))) == 1
    kept = json.loads(config.read_text())
    assert (kept["mode"], kept["min_confidence"]) == ("block", 0.95)


@pytest.mark.parametrize("scope", ["local", "user"])
def test_relative_project_and_home_paths_still_produce_an_absolute_hook_command(env, monkeypatch, scope):
    monkeypatch.chdir(env[0].parent)  # so "proj" and "home" are relative to here
    setup.main(["--project", "proj", "--home", "home", "--yes", "--scope", scope, "--no-model"], io=ScriptedIO(), ollama=FakeAdmin())
    [entry] = entries(local_settings(env) if scope == "local" else user_settings(env))
    path = re.search(r'"(.+)"', entry["command"]).group(1)
    assert os.path.isabs(path) and os.path.exists(path)


def test_yes_alone_never_chooses_a_model_from_the_menu(env):
    admin, io = FakeAdmin(), ScriptedIO()
    setup.main(flags(env, "--yes", "--scope", "local"), io=io, ollama=admin)
    assert config_of(env)["model"] == "" and admin.pulled == [] and admin.started == 0
    assert not any("model" in question.lower() for question in io.asked)


def test_a_named_model_without_ollama_installed_means_heuristics_only_everywhere(env):
    admin = FakeAdmin(installed=False)
    io = ScriptedIO()
    setup.main(flags(env, "--yes", "--scope", "local", "--model", "tiny:1b"), io=io, ollama=admin)
    assert config_of(env)["model"] == "" and admin.pulled == [] and "heuristics-only" in io.text


def test_an_unparsable_config_is_copied_aside_on_install_not_silently_replaced(env):
    args = flags(env, "--yes", "--scope", "local", "--no-model")
    setup.main(args, io=ScriptedIO(), ollama=FakeAdmin())
    config = env[1] / ".claude" / "prompt-preflight" / "config.json"
    config.write_text('{"mode": "block",}', encoding="utf-8")  # a trailing comma
    io = ScriptedIO()
    setup.main(args, io=io, ollama=FakeAdmin())
    [saved] = list(config.parent.glob("config.json.bak-*"))
    assert saved.read_text(encoding="utf-8") == '{"mode": "block",}' and str(saved) in io.text
    assert json.loads(config.read_text())["mode"] == "advise"


def test_update_never_rewrites_an_unparsable_config_and_never_creates_one(env):
    args = flags(env, "--yes", "--scope", "local", "--no-model")
    setup.main(args, io=ScriptedIO(), ollama=FakeAdmin())
    config = env[1] / ".claude" / "prompt-preflight" / "config.json"
    config.write_text('{"mode": "block",}', encoding="utf-8")
    io = ScriptedIO()
    setup.main(flags(env, "--update", "--scope", "local"), io=io, ollama=FakeAdmin())
    assert config.read_text(encoding="utf-8") == '{"mode": "block",}' and "config kept" not in io.text and "not a valid JSON object" in io.text
    config.unlink()
    io = ScriptedIO()
    setup.main(flags(env, "--update", "--scope", "local"), io=io, ollama=FakeAdmin())
    assert not config.exists() and "switched off" in io.text  # an update must not turn a bypassed install back on


def test_a_failure_while_copying_stops_cleanly_and_leaves_the_settings_alone(env, monkeypatch):
    def full_disk(install_dir):
        raise OSError("No space left on device")

    monkeypatch.setattr(setup, "copy_files", full_disk)
    io = ScriptedIO()
    assert setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=io, ollama=FakeAdmin()) == 1
    assert "Stopped: No space left on device" in io.text and not local_settings(env).exists()


def test_remove_says_where_the_settings_backup_went(env):
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin())
    io = ScriptedIO()
    setup.main(flags(env, "--remove", "--yes", "--scope", "local"), io=io, ollama=FakeAdmin())
    assert "Backed up your settings to" in io.text


def test_remove_deletes_a_symlinked_install_folder_link_not_its_target(env, tmp_path):
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin())
    install = env[1] / ".claude" / "prompt-preflight"
    moved = tmp_path / "elsewhere"
    install.rename(moved)
    try:
        install.symlink_to(moved, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not available here")
    assert setup.main(flags(env, "--remove", "--yes", "--scope", "local"), io=ScriptedIO(), ollama=FakeAdmin()) == 0
    assert not install.exists() and not install.is_symlink() and moved.exists()


def test_the_installed_hook_really_answers_as_claude_code_would_call_it(env):
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin())
    hook = env[1] / ".claude" / "prompt-preflight" / "hook.py"
    payload = json.dumps({"session_id": "x", "prompt": "what is the capital of France"}).encode()
    done = subprocess.run([sys.executable, str(hook)], input=payload, capture_output=True, timeout=30)
    assert done.returncode == 0 and "try Google" in json.loads(done.stdout)["systemMessage"]


@pytest.mark.skipif(os.name == "nt", reason="the guard is a POSIX shell construct")
def test_a_settings_entry_whose_files_are_gone_can_never_block_a_prompt(env):
    # Deleting the install folder by hand leaves the entry behind. `python3 <missing file>` exits 2, and exit 2
    # rejects the user's prompt, so the entry must swallow that.
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin())
    root = env[1] / ".claude" / "prompt-preflight"
    [entry] = entries(local_settings(env))
    shutil.rmtree(root)
    assert subprocess.run([sys.executable, str(root / "hook.py")], capture_output=True).returncode == 2
    assert subprocess.run(entry["command"], shell=True, input=b"{}", capture_output=True).returncode == 0


@pytest.mark.skipif(os.name == "nt", reason="PATH lookup semantics differ")
def test_the_self_test_runs_the_exact_command_written_to_settings(env, tmp_path, monkeypatch, real_self_test):
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin())
    root = env[1] / ".claude" / "prompt-preflight"
    monkeypatch.setenv("PATH", str(tmp_path / "no-python-here"))  # `python3` cannot be found, as in a broken setup
    assert setup._self_test(root, ScriptedIO()) is False


def test_a_kept_config_that_switches_advice_off_does_not_fail_the_self_test(env, real_self_test):
    args = flags(env, "--yes", "--scope", "local", "--no-model")
    setup.main(args, io=ScriptedIO(), ollama=FakeAdmin())
    config = env[1] / ".claude" / "prompt-preflight" / "config.json"
    edited = json.loads(config.read_text())
    edited["enabled"] = False  # the documented way to switch it off without uninstalling
    config.write_text(json.dumps(edited), encoding="utf-8")
    io = ScriptedIO()
    assert setup.main(args, io=io, ollama=FakeAdmin()) == 0
    assert "switched off in config.json" in io.text and "self-test failed" not in io.text


@pytest.mark.parametrize("advice", [True, False])
@pytest.mark.parametrize("damage", ["package", "launcher"])
def test_the_self_test_notices_a_broken_install_whether_or_not_advice_is_on(env, real_self_test, advice, damage):
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin())
    root = env[1] / ".claude" / "prompt-preflight"
    config = json.loads((root / "config.json").read_text())
    config["enabled"] = advice
    (root / "config.json").write_text(json.dumps(config), encoding="utf-8")
    shutil.rmtree(root / "prompt_preflight") if damage == "package" else (root / "hook.py").unlink()
    assert setup._self_test(root, ScriptedIO()) is False


def install_with_advice_off(env):
    """An install whose kept config silences the lookup advice, so only the install's health can fail the self-test."""
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin())
    root = env[1] / ".claude" / "prompt-preflight"
    config = json.loads((root / "config.json").read_text())
    config["enabled"] = False
    (root / "config.json").write_text(json.dumps(config), encoding="utf-8")
    return root


def test_a_self_test_that_times_out_fails_cleanly_instead_of_raising(env, monkeypatch, real_self_test):
    root = install_with_advice_off(env)

    def hang(*args, **kwargs):
        raise subprocess.TimeoutExpired("hook", 30)

    monkeypatch.setattr(setup.subprocess, "run", hang)
    io = ScriptedIO()
    assert setup._self_test(root, io) is False and "TIMED OUT" in io.text


def test_a_self_test_fails_when_the_hook_prints_anything_but_one_json_object(env, monkeypatch, real_self_test):
    root = install_with_advice_off(env)
    for garbage in (b"plain text", b"[1, 2]"):
        monkeypatch.setattr(setup.subprocess, "run", lambda *a, _g=garbage, **k: subprocess.CompletedProcess(a, 0, _g, b""))
        io = ScriptedIO()
        assert setup._self_test(root, io) is False and "INVALID OUTPUT" in io.text


@pytest.mark.skipif(os.name == "nt", reason="PATH lookup semantics differ")
def test_a_self_test_fails_without_python3_on_the_path_even_when_advice_is_off(env, tmp_path, monkeypatch, real_self_test):
    root = install_with_advice_off(env)
    monkeypatch.setenv("PATH", str(tmp_path / "no-python-here"))
    assert setup._self_test(root, ScriptedIO()) is False


def test_the_self_test_reports_and_leaves_no_state_behind(env, real_self_test):
    io = ScriptedIO()
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=io, ollama=FakeAdmin())
    root = env[1] / ".claude" / "prompt-preflight"
    assert not (root / "state.json").exists() and not (root / "preflight.log").exists()
    assert "Self-test:" in io.text and "try Google" in io.text and "Restart Claude Code" in io.text


def test_a_failing_self_test_is_reported_with_a_nonzero_exit(env, monkeypatch):
    monkeypatch.setattr(setup, "_self_test", lambda install_dir, io: False)
    io = ScriptedIO()
    assert setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=io, ollama=FakeAdmin()) == 3
    assert "self-test failed" in io.text and "--remove" in io.text


@pytest.mark.skipif(not shutil.which("git"), reason="git not installed")
def test_it_warns_when_the_local_settings_file_is_not_git_ignored(env, tmp_path, monkeypatch):
    # Isolate git from the developer's global ignore file, which may already ignore this path.
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "no-xdg"))
    subprocess.run(["git", "init", "-q", str(env[1])], check=True)
    io = ScriptedIO()
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=io, ollama=FakeAdmin())
    assert "is not git-ignored" in io.text
    (env[1] / ".gitignore").write_text(".claude/settings.local.json\n", encoding="utf-8")
    io2 = ScriptedIO()
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=io2, ollama=FakeAdmin())
    assert "is not git-ignored" not in io2.text


# ---------- the model steps -------------------------------------------------------------------


def config_of(env, scope="local"):
    base = env[1] if scope == "local" else env[0]
    return json.loads((base / ".claude" / "prompt-preflight" / "config.json").read_text())


def test_explicit_model_is_downloaded_only_after_confirmation(env):
    admin = FakeAdmin(models=[])
    setup.main(flags(env, "--yes", "--scope", "local", "--model", "tiny:1b"), io=ScriptedIO(), ollama=admin)
    assert admin.pulled == ["tiny:1b"] and config_of(env)["model"] == "tiny:1b"


def test_a_model_that_is_already_downloaded_is_not_pulled_again(env):
    admin = FakeAdmin(models=[{"name": "tiny:1b", "size": 1e9}])
    setup.main(flags(env, "--yes", "--scope", "local", "--model", "tiny:1b"), io=ScriptedIO(), ollama=admin)
    assert admin.pulled == [] and config_of(env)["model"] == "tiny:1b"


def test_a_failed_download_falls_back_to_heuristics_only(env):
    io = ScriptedIO()
    setup.main(flags(env, "--yes", "--scope", "local", "--model", "tiny:1b"), io=io, ollama=FakeAdmin(models=[], pull_ok=False))
    assert config_of(env)["model"] == "" and "heuristics-only" in io.text


def test_yes_never_starts_ollama_by_itself(env):
    admin = FakeAdmin(running=False)
    setup.main(flags(env, "--yes", "--scope", "local", "--model", "tiny:1b"), io=ScriptedIO(), ollama=admin)
    assert admin.started == 0 and admin.pulled == []
    assert config_of(env)["model"] == "tiny:1b"  # will work once Ollama runs and the model is pulled


def test_ollama_is_started_only_when_the_user_says_yes(env):
    admin = FakeAdmin(running=False, models=[])
    io = ScriptedIO(yes=[True, True, True], choices=[0])  # consent, start Ollama, confirm install
    setup.main(flags(env, "--scope", "local", "--model", "tiny:1b"), io=io, ollama=admin)
    assert admin.started == 1 and admin.pulled == ["tiny:1b"]
    assert "Start it now?" in " ".join(io.asked)


def test_a_failed_start_falls_back_to_heuristics_only(env):
    admin = FakeAdmin(running=False, start_ok=False)
    setup.main(flags(env, "--scope", "local", "--model", "tiny:1b"), io=ScriptedIO(yes=[True, True, True]), ollama=admin)
    assert config_of(env)["model"] == ""


def test_ollama_not_installed_gives_an_install_hint_and_heuristics_only(env):
    io = ScriptedIO()
    setup.main(flags(env, "--yes", "--scope", "local"), io=io, ollama=FakeAdmin(installed=False))
    assert "ollama.com/download" in io.text and config_of(env)["model"] == ""


def test_interactive_choice_lists_existing_models_and_defaults_to_heuristics_only(env):
    io = ScriptedIO(yes=[True, True])
    setup.main(flags(env, "--scope", "local"), io=io, ollama=FakeAdmin())
    assert io.options == ["Use llama3:latest (already downloaded, 4.7 GB)", "Heuristics only (no model)"]
    assert config_of(env)["model"] == ""  # default = heuristics-only when nothing is recommended


def test_interactive_choice_can_pick_an_existing_model_without_any_download(env):
    admin = FakeAdmin()
    setup.main(flags(env, "--scope", "local"), io=ScriptedIO(yes=[True, True], choices=[0]), ollama=admin)
    assert config_of(env)["model"] == "llama3:latest" and admin.pulled == []


def test_a_recommended_model_is_offered_as_a_download_and_is_the_default(env, monkeypatch):
    monkeypatch.setattr(defaults, "RECOMMENDED_MODEL", "tiny:1b")
    monkeypatch.setattr(defaults, "RECOMMENDED_MODEL_SIZE_GB", 1.3)
    admin = FakeAdmin()
    io = ScriptedIO(yes=[True, True])
    setup.main(flags(env, "--scope", "local"), io=io, ollama=admin)
    assert "Download tiny:1b (recommended, 1.3 GB)" in io.options
    assert admin.pulled == ["tiny:1b"] and config_of(env)["model"] == "tiny:1b"


def test_ollama_host_is_seeded_from_the_environment_only_when_loopback():
    assert setup.build_config("m", env={"OLLAMA_HOST": "localhost:9999"})["ollama_host"] == "localhost:9999"
    assert setup.build_config("m", env={"OLLAMA_HOST": "10.1.1.1:11434"})["ollama_host"] == "127.0.0.1:11434"


# ---------- remove and update -----------------------------------------------------------------


def test_remove_deletes_only_preflight_and_keeps_other_hooks(env):
    path = local_settings(env)
    path.parent.mkdir(parents=True)
    original = {"model": "sonnet", "hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": "lint.sh"}]}]}}
    path.write_text(json.dumps(original), encoding="utf-8")
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin())
    assert setup.main(flags(env, "--remove", "--yes", "--scope", "local"), io=ScriptedIO(), ollama=FakeAdmin()) == 0
    assert json.loads(path.read_text()) == original
    assert not (path.parent / "prompt-preflight").exists()


def test_remove_dry_run_and_declined_removal_change_nothing(env, tmp_path):
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin())
    before = snapshot(tmp_path)
    setup.main(flags(env, "--remove", "--dry-run", "--scope", "local"), io=ScriptedIO(), ollama=FakeAdmin())
    setup.main(flags(env, "--remove", "--scope", "local"), io=ScriptedIO(yes=[False]), ollama=FakeAdmin())
    assert snapshot(tmp_path) == before


def test_remove_with_nothing_installed_says_so(env):
    io = ScriptedIO()
    assert setup.main(flags(env, "--remove", "--yes"), io=io, ollama=FakeAdmin()) == 0
    assert "Nothing to remove" in io.text


def test_remove_without_a_scope_finds_either_install(env):
    setup.main(flags(env, "--yes", "--scope", "user", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin())
    setup.main(flags(env, "--remove", "--yes"), io=ScriptedIO(), ollama=FakeAdmin())
    assert not (env[0] / ".claude" / "prompt-preflight").exists()
    assert "hooks" not in json.loads(user_settings(env).read_text())


def test_update_refreshes_the_code_and_keeps_the_config(env):
    setup.main(flags(env, "--yes", "--scope", "local", "--no-model"), io=ScriptedIO(), ollama=FakeAdmin())
    root = env[1] / ".claude" / "prompt-preflight"
    cfg = json.loads((root / "config.json").read_text())
    cfg["mode"], cfg["installed_version"] = "block", "0.0.1"
    (root / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
    (root / "prompt_preflight" / "decide.py").write_text("# corrupted\n", encoding="utf-8")
    assert setup.main(flags(env, "--update", "--scope", "local"), io=ScriptedIO(), ollama=FakeAdmin()) == 0
    assert "corrupted" not in (root / "prompt_preflight" / "decide.py").read_text()
    kept = json.loads((root / "config.json").read_text())
    assert kept["mode"] == "block" and kept["installed_version"] != "0.0.1"


def test_update_with_no_install_says_so(env):
    io = ScriptedIO()
    assert setup.main(flags(env, "--update"), io=io, ollama=FakeAdmin()) == 0
    assert "Nothing to update" in io.text


def test_running_setup_as_a_script_works(env):
    script = os.path.join(os.path.dirname(setup.__file__), "setup.py")
    done = subprocess.run([sys.executable, script, *flags(env, "--remove", "--dry-run")], capture_output=True, text=True, timeout=60)
    assert done.returncode == 0 and "Nothing to remove" in done.stdout
