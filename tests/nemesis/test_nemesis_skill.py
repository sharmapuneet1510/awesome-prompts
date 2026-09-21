import yaml

from . import common as c

COVERS = ["N1", "N4", "N7", "N8", "N9", "N10"]

SKILL = c.read(c.SKILL)


def test_the_skill_has_front_matter():
    meta = c.front_matter(SKILL)
    assert meta["name"] == "NEMESIS Skill" and str(meta["version"]) and meta["description"]


def test_it_is_a_mode_not_an_agent():
    assert "*execution mode*, not an agent" in c.flat(SKILL) and "NEMESIS Architect" in SKILL and "Specialist persona + NEMESIS" in SKILL


def test_the_finding_categories_are_exactly_the_seventeen():
    block = c.fenced(c.section(SKILL, "### Categories"), "text")[0]
    assert block.split() == c.CATEGORIES


def test_severity_confidence_and_evidence_classes_are_pinned():
    severity = c.section(SKILL, "### Severity")
    confidence = c.section(SKILL, "### Confidence")
    evidence = c.section(SKILL, "## 8. Evidence challenge")
    assert all("`%s`" % s in severity for s in c.SEVERITIES)
    assert all("`%s`" % s in confidence for s in c.CONFIDENCES)
    assert all("`%s`" % s in evidence for s in c.EVIDENCE_CLASSES)


def test_severity_and_confidence_are_separate():
    assert "Severity and confidence are separate" in SKILL and "Severity: CRITICAL, Confidence: SPECULATIVE" in SKILL
    assert "can never by itself raise the verdict above SURVIVED WITH CONDITIONS" in SKILL


def test_the_five_verdicts_and_their_rules():
    section = c.section(SKILL, "## 10. Verdict")
    rows = c.table_rows(section)
    assert [row[0].strip("`") for row in rows] == ["DEFEATED", "CHALLENGED", "SURVIVED WITH CONDITIONS", "SURVIVED", "INSUFFICIENT EVIDENCE"]
    assert sorted(row[0].strip("`") for row in rows) == sorted(c.VERDICTS)
    assert "HIGH" in rows[0][1] and "CONFIRMED" in rows[0][1] and "counterexample" in rows[0][1]


def test_it_never_invents_a_defect():
    assert "Never invent a defect" in SKILL and "NEMESIS never has to find a defect" in SKILL and "Do not manufacture faults" in SKILL


def test_the_reverse_hypothesis_comes_before_any_investigation():
    assert SKILL.index("## 3. Reverse hypothesis") < SKILL.index("## 5. Independent evidence") < SKILL.index("## 6. Requirement-by-requirement attack")
    assert "**first** thing NEMESIS writes" in SKILL and "It is **not** the verdict" in SKILL


def test_independence_lists_five_inputs_and_excludes_the_original_reasoning():
    section = c.section(SKILL, "## 2. Independence")
    assert all(f"{n}. " in section for n in range(1, 6))
    assert "does **not** receive" in section and "reasoning chain" in section


def test_it_is_source_first_and_read_only():
    section = c.section(SKILL, "## 5. Independent evidence")
    assert "read-only" in section and "The only file NEMESIS writes is its own report" in section


def test_counterexamples_say_whether_they_were_executed_or_derived():
    section = c.section(SKILL, "## 7. Counterexamples")
    assert "**executed**" in section and "**derived**" in section and "never CONFIRMED" in section


def test_false_confidence_signals_are_listed():
    section = c.section(SKILL, "### False-confidence signals")
    assert all(phrase in c.flat(section) for phrase in ["no issues found", "fully tested", "safe to release", "production ready"])


def test_hypotheses_have_the_pinned_fields_layers_and_causes():
    section = c.section(SKILL, "## 11. Failure-cause hypotheses")
    assert all("`%s`" % key in section for key in c.HYPOTHESIS_KEYS if key != "cause_class") and "`cause_class`" in section
    assert "`discriminating_check`" in section and "defect" in section and "miss" in section
    assert c.fenced(section, "text")[0].split() == c.CAUSE_CLASSES
    assert "INFERENCE" in section


def test_hypotheses_by_verdict():
    rows = c.table_rows(c.section(SKILL, "### By verdict"))
    assert len(rows) == 3 and "Required" in rows[0][1] and "never padded" in rows[2][1]


def test_the_report_template_carries_every_header_key():
    header = yaml.safe_load(c.fenced(c.section(SKILL, "## 12. Report"), "yaml")[0])
    assert list(header) == c.HEADER_KEYS and header["access"] == "read_only"
    for heading in c.BODY_HEADINGS[1:]:
        assert heading.lstrip("# ") in c.section(SKILL, "## 12. Report")
    assert all(key in c.section(SKILL, "## 12. Report") for key in c.FINDING_KEYS)


def test_the_status_vocabulary_is_defined():
    section = c.section(SKILL, "## 13. Status vocabulary")
    assert all("`%s`" % s in section for s in c.STATUS_STRINGS)


def test_the_limits_are_stated_plainly():
    section = c.section(SKILL, "## 15. Limits")
    assert "cannot technically enforce" in section and "context_isolated" in section
