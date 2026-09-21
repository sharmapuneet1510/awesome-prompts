import re

from . import common as c

COVERS = ["N12"]

GATES = {
    "agents/quality/functions/review.md": ["critical_change", "security_change", "payment_change"],
    "agents/architect/functions/adr.md": ["architecture_change"],
    "agents/orchestrator_agent.md": ["production_release"],
}


def test_each_policy_gate_is_present_optional_and_reads_the_config():
    for path, rules in GATES.items():
        text = c.flat(c.read(c.ROOT / path))
        assert "NEMESIS gate (optional)" in text, path
        assert "docs/nemesis/nemesis.yml" in text and "orchestrator:nemesis" in text and "trigger=policy" in text, path
        assert all(rule in text for rule in rules), path
        assert "Without `nemesis.yml`, skip" in text, path


def test_the_gates_do_not_change_behaviour_without_the_file():
    for path in GATES:
        assert re.search(r"[Ii]f `docs/nemesis/nemesis\.yml` exists", c.flat(c.read(c.ROOT / path))), path


def test_the_adr_gate_never_replaces_human_approval():
    text = c.flat(c.read(c.ROOT / "agents/architect/functions/adr.md"))
    assert "never replaces the human approval" in text and "before** approval is requested" in text


def test_the_review_gate_makes_a_defeat_override_the_pass():
    assert "overrides the `PASS`" in c.flat(c.read(c.ROOT / "agents/quality/functions/review.md"))


def test_the_pr_gate_stops_on_a_defeat():
    text = c.flat(c.read(c.ROOT / "agents/orchestrator_agent.md"))
    assert "stop on a `DEFEATED` or `CHALLENGED` verdict" in text


def test_a_gate_only_exists_in_the_three_named_functions():
    hits = [p.relative_to(c.ROOT).as_posix() for p in (c.ROOT / "agents").rglob("*.md") if "NEMESIS gate (optional)" in p.read_text(encoding="utf-8")]
    assert sorted(hits) == sorted(GATES)
