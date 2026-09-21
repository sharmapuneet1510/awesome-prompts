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
    assert "clean-room pass" in step and "context_isolated: false" in step and "context_isolated: true" in step
    assert "Do not claim isolation that did not happen" in step


def test_it_is_read_only_and_writes_one_file():
    text = c.flat(FUNCTION)
    assert "read-only" in text and "**only write** NEMESIS ever makes" in text and "NEMESIS is read-only" in text


def test_the_mcp_roles_fall_back_to_git_and_files():
    step = c.flat(c.section(FUNCTION, "### Step 5"))
    assert all(role in step for role in ["jira", "git", "ci_cd", "test_management", "evidence_store"])
    assert "fall back to git and files" in step


def test_routing_covers_every_verdict():
    rows = c.table_rows(c.section(FUNCTION, "### Step 9"))
    routed = [verdict.strip().strip("`") for row in rows for verdict in row[0].split(", ")]
    assert sorted(routed) == sorted(c.VERDICTS)  # each of the five exactly once
    assert "whole report as task context" in c.flat(rows[0][1]) and "hypotheses first" in c.flat(rows[0][1])


def test_the_two_roles_are_split_and_every_step_has_an_owner():
    section = c.flat(c.section(FUNCTION, "## Process").split("### Step 1")[0])
    assert "**caller**" in section and "**challenger**" in section
    assert "1 Resolve, 2 Select, 3 Isolate" in section and "4 Reverse hypothesis, 5 Evidence, 6 Attack, 7 Challenge the evidence, 8 Hypotheses and verdict" in section
    assert "the caller sets `context_isolated`" in section and "**Two roles.**" in section
    assert "8 Hypotheses and verdict, and **writing the report**" in section and "the routing half of step 9, and 10 Terminate | the **caller**" in section


def test_the_caller_allocates_the_report_before_spawning_and_hands_the_challenger_everything_it_needs():
    step = c.section(FUNCTION, "### Step 3")
    assert step.index("allocate the report") < step.index("spawn a fresh sub-agent")
    block = c.fenced(step, "text")[0]
    for needed in ["skills/nemesis_skill.md", "nemesis_id:", "nemesis_persona:", "original_agent:", "trigger:", "depth:", "parent_nemesis:", "context_isolated: true", "access: read_only", "<path>"]:
        assert needed in block, needed
    assert "context_isolated: false" in step


def test_depth_is_computed_and_a_rerun_is_a_new_challenge():
    step = c.flat(c.section(FUNCTION, "### Step 3"))
    assert "parent's `depth` plus 1" in step and "new depth-1 challenge" in step
    assert "parent's `depth` plus 1" in c.flat(c.section(FUNCTION, "## Recursion"))


def test_a_challenger_never_evaluates_a_gate_and_the_fix_loop_is_guarded():
    block = c.fenced(c.section(FUNCTION, "### Step 3"), "text")[0]
    assert "Do not evaluate any NEMESIS policy gate and do not start another NEMESIS" in block
    guard = c.flat(c.section(FUNCTION, "## Loop guard"))
    assert "new depth-1 challenge" in guard and "two consecutive" in guard and "hand the decision to a human" in guard
    assert "count them from the reports in `docs/nemesis/`" in guard and "`architect:adr` gate is advice-only" in guard
    assert "A challenger never evaluates a gate" in guard


def test_without_a_config_workflow_and_agent_runs_are_explicit_invocations():
    assert "still explicit invocations: nothing fires on its own" in c.flat(c.section(FUNCTION, "## Triggers"))
    assert "`original_agent`" in c.flat(c.section(FUNCTION, "### Step 1"))


def test_a_refusal_writes_nothing():
    recursion = c.flat(c.section(FUNCTION, "## Recursion"))
    assert "write nothing" in recursion and "refusal note" not in c.flat(FUNCTION)
    assert "no refusal, note or scratch file" in c.flat(c.section(FUNCTION, "### Step 9"))


def test_disabled_config_refuses_every_trigger_including_manual():
    assert "refuse every trigger, including a manual `/nemesis`" in c.flat(c.section(FUNCTION, "## Configuration"))


def test_the_function_names_every_status_string():
    text = c.flat(FUNCTION)
    for status in ["NEMESIS ACTIVATED", "NEMESIS IS CHALLENGING THE CONCLUSION", "COUNTEREXAMPLE DETECTED", "CONCLUSION COMPROMISED", "NEMESIS SURVIVED", "NEMESIS DEFEATED THE CONCLUSION"]:
        assert status in text, status


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


def test_the_challenger_is_told_the_target_type_and_the_change():
    step3 = c.flat(c.section(FUNCTION, "### Step 3"))
    assert "target: {type:" in step3 and "change:" in step3
    step1 = c.flat(c.section(FUNCTION, "### Step 1"))
    assert "original_agent" in step1 and "target type" in step1 and "change" in step1


def test_the_loop_guard_counts_by_change_and_blocking_results():
    guard = c.flat(c.section(FUNCTION, "## Loop guard"))
    assert "two consecutive blocking results" in guard and "`change` header" in guard
    for verdict in ["DEFEATED", "CHALLENGED", "INSUFFICIENT EVIDENCE"]:
        assert verdict in guard


def test_the_configuration_has_one_root_key_and_the_release_persona_is_an_existing_function():
    assert "one root key, `nemesis:`" in c.flat(c.section(FUNCTION, "## Configuration"))
    assert "| Release approval, deployment readiness | `quality:observe`, `orchestrator:risk` |" in c.flat(c.section(FUNCTION, "### Step 2"))


def test_the_function_says_how_to_extend_it():
    extending = c.flat(c.section(FUNCTION, "## Extending"))
    for item in ["A persona", "A gate", "A verdict, category or cause class"]:
        assert item in extending, item
