import re

from . import common as c

COVERS = ["N12"]

GATES = {
    "agents/quality/functions/review.md": ["critical_change", "security_change", "payment_change"],
    "agents/architect/functions/adr.md": ["architecture_change"],
    "agents/orchestrator_agent.md": ["production_release"],
}


def gate_text(path):
    """The gate paragraph alone: from its heading to the end of that paragraph or section."""
    text = c.read(c.ROOT / path)
    start = text.index("NEMESIS gate (optional)")
    end_candidates = [i for i in (text.find("\n## ", start + 1), text.find("\n### ", start + 1), text.find("\n---", start + 1)) if i != -1]
    return c.flat(text[start:min(end_candidates) if end_candidates else len(text)])


def test_each_policy_gate_is_present_once_optional_and_reads_the_config():
    for path, rules in GATES.items():
        assert c.read(c.ROOT / path).count("NEMESIS gate (optional)") == 1, path
        text = gate_text(path)
        assert "docs/nemesis/nemesis.yml" in text and "orchestrator:nemesis" in text and "trigger=policy" in text, path
        assert all(rule in text for rule in rules), path
        assert re.search(r"[Ii]f `docs/nemesis/nemesis\.yml` exists", text), path
        assert "is not `enabled: false`" in text, path


def test_a_gate_changes_nothing_without_the_file_and_never_runs_inside_a_challenger():
    for path in GATES:
        text = gate_text(path)
        assert re.search(r"Skip this (section )?when the file is absent", text), path
        assert "when you are yourself running as a NEMESIS challenger" in text, path


def test_the_adr_gate_never_replaces_human_approval_and_sits_between_proposed_and_the_request():
    text = gate_text("agents/architect/functions/adr.md")
    assert "never replaces the human approval" in text
    assert "between setting `Status: Proposed` and presenting the approval request in step 7" in text
    assert all(v in text for v in ["DEFEATED", "CHALLENGED", "INSUFFICIENT EVIDENCE"])


def test_the_review_gate_handles_every_verdict_and_stops_a_fix_loop():
    text = gate_text("agents/quality/functions/review.md")
    assert "`DEFEATED`, `CHALLENGED` or `INSUFFICIENT EVIDENCE` overrides the `PASS`" in text
    assert "`SURVIVED WITH CONDITIONS` keeps the `PASS` and copies its conditions into your report" in text
    assert "two consecutive `DEFEATED` or `CHALLENGED` results for the same change" in text and "hand the decision to a human" in text
    assert "count the reports in `docs/nemesis/` that name it" in text


def test_the_pr_gate_stops_on_a_defeat_and_stops_a_fix_loop():
    text = gate_text("agents/orchestrator_agent.md")
    assert "stop on a `DEFEATED`, `CHALLENGED` or `INSUFFICIENT EVIDENCE` verdict" in text
    assert "on `SURVIVED WITH CONDITIONS`, put its conditions in the PR description" in text
    assert "two consecutive `DEFEATED` or `CHALLENGED` results for the same release" in text and "count the reports in `docs/nemesis/` that name it" in text


def test_the_pr_gate_sits_after_the_step_list_of_the_orchestrator_pr_section_and_says_before_step_1():
    text = c.read(c.ROOT / "agents/orchestrator_agent.md")
    section = text[text.index("### orchestrator:pr"):]
    section = section[: section.index("\n---", 10)]
    assert section.index("NEMESIS gate (optional)") > section.index("8. Generate completion report")
    assert "Before step 1" in section


def test_a_gate_only_exists_in_the_three_named_functions():
    hits = [p.relative_to(c.ROOT).as_posix() for p in (c.ROOT / "agents").rglob("*.md") if "NEMESIS gate (optional)" in p.read_text(encoding="utf-8")]
    assert sorted(hits) == sorted(GATES)
