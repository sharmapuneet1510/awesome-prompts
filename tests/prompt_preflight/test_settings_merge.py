import copy
import json
import os

import pytest

from prompt_preflight import settings_merge as sm

COVERS = ["R10", "R11"]

CMD = 'python3 "/home/u/.claude/prompt-preflight/hook.py"'
OTHER = {"type": "command", "command": "/usr/local/bin/lint-prompt.sh"}


def existing():
    return {
        "model": "sonnet",
        "permissions": {"allow": ["Bash(ls)"]},
        "hooks": {
            "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "check.sh"}]}],
            "UserPromptSubmit": [{"hooks": [dict(OTHER)]}],
        },
    }


def test_add_creates_the_documented_shape_without_a_matcher():
    result = sm.add_hook({}, CMD)
    assert result == {"hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": CMD, "timeout": 5}]}]}}
    assert "matcher" not in result["hooks"]["UserPromptSubmit"][0]


def test_add_preserves_everything_else():
    result = sm.add_hook(existing(), CMD)
    assert result["model"] == "sonnet" and result["permissions"] == {"allow": ["Bash(ls)"]}
    assert result["hooks"]["PreToolUse"] == existing()["hooks"]["PreToolUse"]
    handlers = [h for g in result["hooks"]["UserPromptSubmit"] for h in g["hooks"]]
    assert OTHER in handlers and any(h["command"] == CMD for h in handlers)


def test_add_does_not_mutate_its_input():
    original = existing()
    sm.add_hook(original, CMD)
    assert original == existing()


def test_installing_twice_leaves_exactly_one_entry():
    once = sm.add_hook(existing(), CMD)
    twice = sm.add_hook(once, CMD)
    assert twice == once
    assert sum(sm._ours(h) for g in twice["hooks"]["UserPromptSubmit"] for h in g["hooks"]) == 1


def test_reinstalling_from_a_new_location_replaces_the_old_entry():
    moved = 'python3 "/elsewhere/.claude/prompt-preflight/hook.py"'
    result = sm.add_hook(sm.add_hook({}, CMD), moved)
    commands = [h["command"] for g in result["hooks"]["UserPromptSubmit"] for h in g["hooks"]]
    assert commands == [moved]


def test_windows_style_paths_are_recognised():
    win = 'python3 "C:\\Users\\u\\.claude\\prompt-preflight\\hook.py"'
    assert sm.has_hook(sm.add_hook({}, win))
    assert sm.remove_hook(sm.add_hook({}, win)) == {}


def test_remove_deletes_only_preflight_and_restores_the_original():
    assert sm.remove_hook(sm.add_hook(existing(), CMD)) == existing()


def test_remove_tidies_containers_it_empties():
    assert sm.remove_hook(sm.add_hook({}, CMD)) == {}
    assert sm.remove_hook(sm.add_hook({"model": "x"}, CMD)) == {"model": "x"}


def test_remove_when_absent_is_a_no_op():
    assert sm.remove_hook(existing()) == existing()
    assert not sm.has_hook(existing())


def test_a_group_shared_with_another_handler_keeps_the_other():
    shared = {"hooks": {"UserPromptSubmit": [{"hooks": [dict(OTHER), {"type": "command", "command": CMD}]}]}}
    assert sm.remove_hook(shared) == {"hooks": {"UserPromptSubmit": [{"hooks": [OTHER]}]}}


@pytest.mark.parametrize("bad", [{"hooks": []}, {"hooks": {"UserPromptSubmit": "x"}}])
def test_malformed_hook_containers_are_refused(bad):
    with pytest.raises(sm.SettingsError):
        sm.add_hook(bad, CMD)


def test_reading_a_missing_file_is_an_empty_object(tmp_path):
    assert sm.read_settings(str(tmp_path / "nope.json")) == {}


@pytest.mark.parametrize("content", ["{broken", "[1,2]", '"text"', ""])
def test_invalid_files_are_refused_and_left_untouched(tmp_path, content):
    path = tmp_path / "settings.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(sm.SettingsError):
        sm.read_settings(str(path))
    assert path.read_text(encoding="utf-8") == content


def test_write_backs_up_the_existing_file_first(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"model": "sonnet"}), encoding="utf-8")
    backup = sm.write_settings(str(path), {"model": "opus"})
    assert json.loads(open(backup, encoding="utf-8").read()) == {"model": "sonnet"}
    assert json.loads(path.read_text(encoding="utf-8")) == {"model": "opus"}


def test_write_creates_parent_directories_and_needs_no_backup_for_a_new_file(tmp_path):
    path = tmp_path / "deep" / "dir" / "settings.local.json"
    assert sm.write_settings(str(path), {"a": 1}) is None
    assert json.loads(path.read_text(encoding="utf-8")) == {"a": 1}


def test_write_leaves_no_temp_files_behind(tmp_path):
    sm.write_settings(str(tmp_path / "settings.json"), {"a": 1})
    assert sorted(os.listdir(tmp_path)) == ["settings.json"]


def test_a_failed_write_keeps_the_original_and_cleans_up(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text('{"keep": true}', encoding="utf-8")
    with pytest.raises(TypeError):
        sm.write_settings(str(path), {"bad": object()}, backup=False)
    assert json.loads(path.read_text(encoding="utf-8")) == {"keep": True}
    assert sorted(os.listdir(tmp_path)) == ["settings.json"]


def test_adding_or_removing_never_shares_structure_with_the_input():
    before = existing()
    after = sm.add_hook(before, CMD)
    after["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"] = "changed-by-caller"
    assert before == existing()
    with_hook = sm.add_hook(existing(), CMD)
    snapshot = copy.deepcopy(with_hook)
    stripped = sm.remove_hook(with_hook)
    stripped["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"] = "changed-by-caller"
    assert with_hook == snapshot


def test_a_symlinked_settings_file_is_written_through_not_replaced(tmp_path):
    real = tmp_path / "dotfiles" / "settings.json"
    real.parent.mkdir()
    real.write_text('{"old": true}', encoding="utf-8")
    link = tmp_path / "settings.json"
    try:
        os.symlink(real, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not available here")
    sm.write_settings(str(link), {"new": True})
    assert os.path.islink(link)
    assert json.loads(real.read_text(encoding="utf-8")) == {"new": True}


@pytest.mark.skipif(os.name == "nt", reason="POSIX permission bits")
def test_the_file_keeps_its_permissions(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text("{}", encoding="utf-8")
    os.chmod(path, 0o644)
    sm.write_settings(str(path), {"a": 1})
    assert (os.stat(path).st_mode & 0o777) == 0o644


def test_two_backups_in_the_same_second_never_overwrite_each_other(tmp_path, monkeypatch):
    class Frozen(sm.datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 9, 21, 12, 0, 0)

    monkeypatch.setattr(sm.datetime, "datetime", Frozen)
    path = tmp_path / "settings.json"
    path.write_text('{"original": true}', encoding="utf-8")
    first = sm.write_settings(str(path), {"v": 1})
    second = sm.write_settings(str(path), {"v": 2})
    assert first != second
    assert json.loads(open(first, encoding="utf-8").read()) == {"original": True}
    assert json.loads(open(second, encoding="utf-8").read()) == {"v": 1}


def test_non_ascii_text_is_kept_as_written(tmp_path):
    path = tmp_path / "settings.json"
    sm.write_settings(str(path), {"note": "café ✓"})
    assert "café ✓" in path.read_text(encoding="utf-8")


def test_diff_shows_exactly_the_added_hook():
    text = sm.diff_text({}, sm.add_hook({}, CMD))
    assert "+" in text and "prompt-preflight/hook.py" in text and "(before)" in text
    assert sm.diff_text({"a": 1}, {"a": 1}) == ""
