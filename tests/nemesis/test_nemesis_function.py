import re

import yaml

from . import common as c

COVERS = ["N2", "N3", "N5", "N6", "N12", "N13"]

FUNCTION = c.read(c.FUNCTION)
STEPS = [
    "Resolve the target", "Select the persona", "Isolate", "Reverse hypothesis and challenge plan",
    "Collect independent evidence", "Attack requirement by requirement", "Challenge the evidence",
    "Failure-cause hypotheses and verdict", "Write the report and route", "Terminate",
]


def test_front_matter_and_entry_points():
    meta = c.front_matter(FUNCTION)
    assert meta["prefix"] == "orchestrator:nemesis"
    assert "/nemesis" in FUNCTION and "NEMESIS ACTIVATED" in FUNCTION and "target:" in FUNCTION


def test_it_is_declared_in_the_orchestrator_dispatch_table():
    table = c.read(c.ROOT / "agents" / "orchestrator_agent.md")
    assert re.search(r"^\| `orchestrator:nemesis` \|", table, re.M)


def test_the_ten_steps_run_in_order():
    headings = re.findall(r"^### Step (\d+) — (.+)$", FUNCTION, re.M)
    assert [int(n) for n, _ in headings] == list(range(1, 11))
    for (_, title), expected in zip(headings, STEPS):
        assert title.startswith(expected), (title, expected)


def test_resolution_yields_exactly_five_things():
    step = c.section(FUNCTION, "### Step 1")
    for word in ["artefact", "original conclusion", "original verdict", "evidence references", "identifiers"]:
        assert word in step


def test_the_persona_table_names_only_real_agents_functions_and_skills():
    rows = c.table_rows(c.section(FUNCTION, "### Step 2"))
    assert len(rows) >= 9
    for target, persona, skills in rows:
        for agent, name in re.findall(r"`(\w+):([\w-]+)`", persona):
            dispatch = c.read(c.ROOT / "agents" / c.AGENT_FILES[agent])
            assert re.search(r"^\| `%s:%s`" % (agent, name), dispatch, re.M), "%s:%s is not a declared function" % (agent, name)
        for skill in re.findall(r"`(\w+_skill)`", skills):
            assert (c.ROOT / "skills" / (skill + ".md")).exists(), skill


def test_the_persona_table_covers_every_supported_target():
    targets = " ".join(row[0] for row in c.table_rows(c.section(FUNCTION, "### Step 2"))).lower()
    for word in ["requirements", "architecture", "code", "test", "release", "rca", "documentation", "compliance", "recommendation"]:
        assert word in targets, word


def test_isolation_uses_a_fresh_sub_agent_with_a_recorded_fallback():
    step = c.flat(c.section(FUNCTION, "### Step 3"))
    assert "fresh sub-agent" in step and "only the five inputs" in step and "read-only" in step
    assert "clean-room pass" in step and "context_isolated: true|false" in step
    assert "Do not claim isolation that did not happen" in step


def test_it_is_read_only_and_writes_one_file():
    text = c.flat(FUNCTION)
    assert "read-only" in text and "This is the only write" in text and "NEMESIS is read-only" in text


def test_the_mcp_roles_fall_back_to_git_and_files():
    step = c.flat(c.section(FUNCTION, "### Step 5"))
    assert all(role in step for role in ["jira", "git", "ci_cd", "test_management", "evidence_store"])
    assert "fall back to git and files" in step


def test_routing_covers_every_verdict():
    rows = c.table_rows(c.section(FUNCTION, "### Step 9"))
    assert sorted(row[0].replace("`", "") .split(", ")[0] for row in rows) == sorted(["DEFEATED", "SURVIVED WITH CONDITIONS", "SURVIVED", "INSUFFICIENT EVIDENCE"])
    assert "whole report as task context" in c.flat(rows[0][1]) and "hypotheses first" in c.flat(rows[0][1])


def test_recursion_is_bounded_and_refused_beyond_the_limit():
    section = c.flat(c.section(FUNCTION, "## Recursion"))
    assert "maximum_depth" in section and "defaults to 2" in section and "refused" in section


def test_the_four_triggers_and_the_refusals():
    triggers = c.section(FUNCTION, "## Triggers")
    assert all("`%s`" % t in triggers for t in c.TRIGGERS)
    refusals = c.section(FUNCTION, "## Refusals")
    assert "enabled: false" in refusals and "maximum_depth" in refusals and "no conclusion" in refusals


def test_the_config_template_has_the_specified_keys_and_safe_defaults():
    cfg = yaml.safe_load(c.read(c.CONFIG_EXAMPLE))["nemesis"]
    assert cfg["enabled"] is True and cfg["default_trigger"] == "manual"
    assert sorted(cfg["auto_activate"]) == sorted(c.AUTO_ACTIVATE) and not any(cfg["auto_activate"].values())
    assert cfg["context_isolation"] is True and cfg["independent_source_validation"] is True
    assert cfg["default_access"] == "read_only" and cfg["maximum_depth"] == 2
    assert "policy_match" in cfg


def test_the_function_documents_the_config_and_its_defaults():
    section = c.flat(c.section(FUNCTION, "## Configuration"))
    for key in ["enabled: true", "default_trigger: manual", "auto_activate", "context_isolation: true",
                "independent_source_validation: true", "default_access: read_only", "maximum_depth: 2", "policy_match"]:
        assert key in section, key
    assert "manual-only" in section
