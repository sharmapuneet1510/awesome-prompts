import os

from prompt_preflight.state import State

COVERS = ["R6", "R9"]


class Clock:
    def __init__(self, now=1000.0):
        self.now = now

    def __call__(self):
        return self.now


def make(tmp_path, clock=None):
    return State(str(tmp_path / "state.json"), clock or Clock())


def test_cooldown_lasts_only_as_long_as_asked(tmp_path):
    clock = Clock()
    state = make(tmp_path, clock)
    assert not state.in_cooldown()
    state.start_cooldown(300)
    assert state.in_cooldown()
    clock.now += 301
    assert not state.in_cooldown()


def test_state_persists_across_instances(tmp_path):
    clock = Clock()
    make(tmp_path, clock).start_cooldown(300)
    assert make(tmp_path, clock).in_cooldown()


def test_notice_is_due_once_per_day(tmp_path):
    clock = Clock()
    state = make(tmp_path, clock)
    assert state.notice_due("degraded")
    assert not state.notice_due("degraded")
    clock.now += 86401
    assert state.notice_due("degraded")


def test_notices_are_tracked_per_kind(tmp_path):
    state = make(tmp_path)
    assert state.notice_due("degraded")
    assert state.notice_due("other")


def test_first_prompt_of_a_session_is_detected_once(tmp_path):
    state = make(tmp_path)
    assert state.register_session("s1") is True
    assert state.register_session("s1") is False
    assert state.register_session("s2") is True


def test_missing_session_id_is_never_first(tmp_path):
    assert make(tmp_path).register_session("") is False


def test_sessions_are_capped(tmp_path):
    state = make(tmp_path)
    for i in range(80):
        state.register_session("s%d" % i)
    assert state.register_session("s0") is True  # aged out
    assert state.register_session("s79") is False  # still remembered


def test_block_override_within_window_only(tmp_path):
    clock = Clock()
    state = make(tmp_path, clock)
    state.remember_block("what is x")
    assert state.consume_override("what is x", 300) is True
    assert state.consume_override("what is x", 300) is False  # consumed
    state.remember_block("what is y")
    clock.now += 301
    assert state.consume_override("what is y", 300) is False


def test_override_is_exact_match_and_stores_no_prompt_text(tmp_path):
    state = make(tmp_path)
    state.remember_block("secret question about acme")
    assert state.consume_override("secret question about acme?", 300) is False
    content = (tmp_path / "state.json").read_text(encoding="utf-8")
    assert "secret" not in content and "acme" not in content


def test_corrupt_state_file_is_treated_as_empty(tmp_path):
    (tmp_path / "state.json").write_text("{broken", encoding="utf-8")
    state = make(tmp_path)
    assert not state.in_cooldown()
    assert state.register_session("s1") is True


def test_unwritable_location_never_raises(tmp_path):
    state = State(str(tmp_path / "missing_dir" / "state.json"))
    state.start_cooldown(10)
    assert state.in_cooldown()  # kept in memory even though the save failed
    assert not os.path.exists(str(tmp_path / "missing_dir"))


def test_notice_due_handles_malformed_notices_list(tmp_path):
    (tmp_path / "state.json").write_text('{"notices": []}', encoding="utf-8")
    state = make(tmp_path)
    assert state.notice_due("degraded") is True


def test_notice_due_handles_malformed_notices_string(tmp_path):
    (tmp_path / "state.json").write_text('{"notices": "a"}', encoding="utf-8")
    state = make(tmp_path)
    assert state.notice_due("degraded") is True


def test_notice_due_handles_malformed_notices_null(tmp_path):
    (tmp_path / "state.json").write_text('{"notices": null}', encoding="utf-8")
    state = make(tmp_path)
    assert state.notice_due("degraded") is True


def test_remember_block_says_whether_it_was_saved(tmp_path):
    assert make(tmp_path).remember_block("x") is True
    unwritable = State(str(tmp_path / "missing-dir" / "state.json"), Clock())
    assert unwritable.remember_block("x") is False


def test_remember_block_handles_malformed_blocks_null_value(tmp_path):
    (tmp_path / "state.json").write_text('{"blocks": {"a": null}}', encoding="utf-8")
    state = make(tmp_path)
    state.remember_block("x")
    assert state.consume_override("x", 300) is True


def test_remember_block_handles_malformed_blocks_string_value(tmp_path):
    (tmp_path / "state.json").write_text('{"blocks": {"a": "old", "b": 1.5}}', encoding="utf-8")
    state = make(tmp_path)
    state.remember_block("y")
    assert state.consume_override("y", 300) is True
