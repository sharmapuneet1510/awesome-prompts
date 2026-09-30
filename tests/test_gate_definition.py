# tests/test_gate_definition.py
"""The spec gate is defined once and referenced everywhere else (#54)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "spec_driven_development_skill.md#the-gate"
REFERENCES = [
    "instructions/master_instruction_set.md",
    "agents/implementer_agent.md",
    "agents/architect_agent.md",
    "agents/orchestrator_agent.md",
    "agents/implementer/functions/build.md",
    "agents/implementer/functions/full.md",
    "agents/README.md",
]
RESTATEMENTS = [
    "`design.md` and `tasks.md` must both be",
    "confirm `specs/<feature-name>/design.md` is `Status: Approved`",
    "until the user sets `Status: Approved`",
    "the agent may write the marker into the file",
]


def test_the_gate_is_defined_once():
    skill = (ROOT / "skills/spec_driven_development_skill.md").read_text(encoding="utf-8")
    assert skill.count("\n## The Gate\n") == 1
    for term in ["/spec-gate:approve", "/spec-gate:trivial", "Status: Accepted", "requirements.md", "design.md", "tasks.md"]:
        assert term in skill.split("\n## The Gate\n")[1].split("\n## ")[0], term


def test_every_gate_mention_points_to_the_definition():
    missing = [p for p in REFERENCES if ANCHOR not in (ROOT / p).read_text(encoding="utf-8")]
    assert missing == []


def test_no_file_restates_the_gate():
    hits = [(p, s) for p in REFERENCES for s in RESTATEMENTS if s in (ROOT / p).read_text(encoding="utf-8")]
    assert hits == []


def test_free_text_requirements_go_through_planning():
    text = (ROOT / "agents/implementer_agent.md").read_text(encoding="utf-8")
    assert "Whichever option, the requirement goes to `orchestrator:plan`" in text


def test_readme_says_what_is_enforced():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "refusal, not a warning" not in readme and "all refusals, none warnings" not in readme
    assert "spec-gate" in readme and "enforced by hooks" in readme
