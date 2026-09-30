"""plugins/spec-gate/scripts/gate.py — real hook JSON in, decision out (#54)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "plugins" / "spec-gate" / "scripts" / "gate.py"
CONFIG = {"source": ["src/**"], "exempt": ["specs/**", "docs/**", "tests/**"]}


def run(project: Path, event: dict) -> dict | None:
    event = {"session_id": "s1", "cwd": str(project), **event}
    done = subprocess.run([sys.executable, str(GATE)], input=json.dumps(event), capture_output=True,
                          text=True, env={"PATH": "/usr/bin:/bin"}, timeout=30)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout) if done.stdout.strip() else None


def prompt(project: Path, text: str, session: str = "s1") -> str | None:
    out = run(project, {"hook_event_name": "UserPromptSubmit", "prompt": text, "session_id": session})
    return out["hookSpecificOutput"]["additionalContext"] if out else None


def tool(project: Path, name: str, tool_input: dict, session: str = "s1") -> str | None:
    """The deny reason, or None when the call is allowed."""
    out = run(project, {"hook_event_name": "PreToolUse", "tool_name": name, "tool_input": tool_input,
                        "session_id": session})
    return out["hookSpecificOutput"]["permissionDecisionReason"] if out else None


def write(project: Path, rel: str, text: str = "x\n") -> Path:
    p = project / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


@pytest.fixture
def project(tmp_path: Path) -> Path:
    write(tmp_path, ".spec-gate.json", json.dumps(CONFIG))
    for name in ["requirements", "design", "tasks"]:
        write(tmp_path, f"specs/checkout/{name}.md", f"# {name}\n\nStatus: Draft\n")
    return tmp_path


def approve_chain(project: Path) -> None:
    for name in ["requirements", "design", "tasks"]:
        assert "is Approved" in prompt(project, f"/spec-gate:approve specs/checkout/{name}.md")


def edit_src(project: Path, session: str = "s1") -> str | None:
    return tool(project, "Write", {"file_path": str(project / "src/app.py"), "content": "print(1)\n"}, session)


def test_without_config_everything_is_allowed(tmp_path):
    assert tool(tmp_path, "Write", {"file_path": str(tmp_path / "src/app.py"), "content": "x"}) is None
    assert tool(tmp_path, "Bash", {"command": "echo hi > src/app.py"}) is None
    assert prompt(tmp_path, "/spec-gate:approve specs/x/tasks.md") is None


def test_unapproved_source_edit_is_denied_with_the_command_to_type(project):
    reason = edit_src(project)
    assert "Blocked by spec-gate" in reason and "/spec-gate:approve" in reason


def test_approved_chain_allows_source_edits(project):
    approve_chain(project)
    assert edit_src(project) is None


def test_exempt_and_unlisted_paths_are_allowed(project):
    assert tool(project, "Write", {"file_path": str(project / "tests/test_app.py"), "content": "x"}) is None
    assert tool(project, "Write", {"file_path": str(project / "README.md"), "content": "x"}) is None


def test_relative_file_paths_are_resolved_against_the_project(project):
    assert tool(project, "Edit", {"file_path": "src/app.py", "old_string": "a", "new_string": "b"}) is not None


def test_the_chain_must_be_approved_in_order(project):
    assert "approve specs/checkout/requirements.md first" in prompt(project, "/spec-gate:approve specs/checkout/design.md")


def test_approval_writes_the_marker_and_binds_the_hash(project):
    prompt(project, "/spec-gate:approve specs/checkout/requirements.md")
    text = (project / "specs/checkout/requirements.md").read_text()
    assert "Status: Approved" in text and "Status: Draft" not in text
    state = json.loads((project / ".spec-gate/approvals.json").read_text())
    assert state["approvals"]["specs/checkout/requirements.md"]["prompt"].startswith("/spec-gate:approve")


def test_editing_an_approved_file_voids_the_approval(project):
    approve_chain(project)
    write(project, "specs/checkout/tasks.md", "# tasks\n\nchanged\n\nStatus: Approved\n")
    assert "tasks.md is not approved" in edit_src(project)


def test_the_model_cannot_write_an_approval_marker(project):
    path = str(project / "specs/checkout/requirements.md")
    assert tool(project, "Write", {"file_path": path, "content": "# r\n\nStatus: Approved\n"})
    assert tool(project, "Edit", {"file_path": path, "old_string": "Status: Draft", "new_string": "Status: Approved"})
    assert tool(project, "MultiEdit", {"file_path": path, "edits": [
        {"old_string": "Status: Draft", "new_string": "Status: In review"},
        {"old_string": "# requirements", "new_string": "# requirements\n\n**Status:** Approved"}]})
    adr = write(project, "docs/adr/ADR-0001-x.md", "# ADR\n\nStatus: Proposed\n")
    assert tool(project, "Edit", {"file_path": str(adr), "old_string": "Proposed", "new_string": "Accepted"})  # word-only edit
    assert tool(project, "Edit", {"file_path": str(adr), "old_string": "Status: Proposed", "new_string": "Status: Accepted"})


def test_a_marker_already_in_the_file_does_not_block_other_edits(project):
    approve_chain(project)
    path = str(project / "specs/checkout/tasks.md")
    assert tool(project, "Edit", {"file_path": path, "old_string": "# tasks", "new_string": "# tasks\n\nStatus: Approved"}) is None


def test_marker_text_outside_specs_and_adrs_is_not_blocked(project):
    assert tool(project, "Write", {"file_path": str(project / "docs/guide.md"), "content": "Status: Approved\n"}) is None


def test_the_approval_record_and_config_are_off_limits(project):
    for rel in [".spec-gate/approvals.json", ".spec-gate.json", ".spec-gate/log.jsonl"]:
        assert tool(project, "Write", {"file_path": str(project / rel), "content": "{}"})
    assert tool(project, "Bash", {"command": "cat .spec-gate/approvals.json"})


def test_adr_approval_writes_accepted(project):
    write(project, "docs/adr/ADR-0012-idempotency.md", "# ADR-0012\n\nStatus: Proposed\n")
    assert "is Accepted" in prompt(project, "/spec-gate:approve docs/adr/ADR-0012-idempotency.md")
    assert "Status: Accepted" in (project / "docs/adr/ADR-0012-idempotency.md").read_text()


def test_approve_refuses_other_paths_and_missing_files(project):
    write(project, "notes.md")
    assert "neither a spec file" in prompt(project, "/spec-gate:approve notes.md")
    assert "is not a file" in prompt(project, "/spec-gate:approve specs/nope/tasks.md")


def test_trivial_bypass_lasts_until_the_next_message(project):
    prompt(project, "/spec-gate:trivial fix typo in error message")
    assert edit_src(project) is None
    assert edit_src(project, session="other") is not None        # another session is still gated
    assert prompt(project, "thanks, now add a feature") is None
    assert edit_src(project) is not None
    assert "fix typo" in (project / ".spec-gate/log.jsonl").read_text()


def test_status_reports_approvals(project):
    approve_chain(project)
    report = prompt(project, "/spec-gate:status")
    assert "active feature: checkout" in report and "gated edits: allowed" in report


@pytest.mark.parametrize("command", [
    "echo x > src/app.py", "echo x >> src/app.py", "printf x | tee src/app.py", "sed -i 's/a/b/' src/app.py",
    "perl -pi -e 's/a/b/' src/app.py", "cp /tmp/x src/app.py", "mv /tmp/x src/app.py", "rm src/app.py",
    "truncate -s 0 src/app.py",
])
def test_recognisable_shell_writes_to_source_are_denied(project, command):
    assert tool(project, "Bash", {"command": command})


@pytest.mark.parametrize("command", [
    "cat src/app.py", "grep -r foo src/ > /tmp/out.txt", "python -m pytest 2>&1", "ls src", "git status",
])
def test_reads_and_unrelated_commands_are_allowed(project, command):
    assert tool(project, "Bash", {"command": command}) is None


def test_shell_writes_are_allowed_once_approved(project):
    approve_chain(project)
    assert tool(project, "Bash", {"command": "echo x > src/app.py"}) is None


def test_shell_cannot_write_an_approval_marker(project):
    assert tool(project, "Bash", {"command": "echo 'Status: Approved' >> specs/checkout/tasks.md"})


def test_a_broken_config_denies_instead_of_opening_the_gate(tmp_path):
    write(tmp_path, ".spec-gate.json", "{not json")
    assert "does not parse" in tool(tmp_path, "Write", {"file_path": str(tmp_path / "src/a.py"), "content": "x"})
    write(tmp_path, ".spec-gate.json", "{}")
    assert "source" in tool(tmp_path, "Write", {"file_path": str(tmp_path / "src/a.py"), "content": "x"})


def test_an_internal_error_denies(project):
    write(project, ".spec-gate/approvals.json", "{broken")
    assert "internal error" in edit_src(project)
