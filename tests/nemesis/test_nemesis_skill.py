import re

import pytest
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


def test_the_five_verdicts_are_ordered_rules_and_the_first_match_decides():
    section = c.section(SKILL, "## 10. Verdict")
    rows = c.table_rows(section)
    assert [row[1].strip("`") for row in rows] == ["DEFEATED", "INSUFFICIENT EVIDENCE", "CHALLENGED", "SURVIVED WITH CONDITIONS", "SURVIVED"]
    assert [row[0] for row in rows] == ["1", "2", "3", "4", "5"]
    assert sorted(row[1].strip("`") for row in rows) == sorted(c.VERDICTS)
    assert "first one that matches decides" in c.flat(section) and "exactly one verdict" in c.flat(section)


def test_each_verdict_row_states_its_condition():
    rows = {row[1].strip("`"): c.flat(row[2]) for row in c.table_rows(c.section(SKILL, "## 10. Verdict"))}
    assert all(word in rows["DEFEATED"] for word in ["`HIGH` or `CRITICAL`", "`CONFIRMED` or `HIGH_CONFIDENCE`", "counterexample", "CONTRADICTORY_EVIDENCE"])
    assert "has category `EVIDENCE_GAP`" in rows["INSUFFICIENT EVIDENCE"] and "cannot be verified" in rows["INSUFFICIENT EVIDENCE"]
    assert "there is at least one counting" in rows["INSUFFICIENT EVIDENCE"]  # not vacuously true for an empty or LOW-only report
    assert "`PLAUSIBLE`" in rows["CHALLENGED"] and "two or more" in rows["CHALLENGED"] and "`MEDIUM`" in rows["CHALLENGED"]
    assert "`SPECULATIVE`" in rows["SURVIVED WITH CONDITIONS"] and "at most one" in rows["SURVIVED WITH CONDITIONS"]
    assert "no counting findings" in rows["SURVIVED"]


def test_disproven_findings_are_recorded_but_do_not_count():
    section = c.flat(c.section(SKILL, "## 10. Verdict"))
    assert "Counting findings" in section and "not `DISPROVEN`" in section and "never counts toward the verdict" in section
    assert "does not count toward the verdict" in c.flat(c.section(SKILL, "### Confidence"))


@pytest.mark.parametrize(
    "findings,expected",
    [
        ([], "SURVIVED"),
        ([("CRITICAL", "CONFIRMED", "steps", "IMPLEMENTATION_DEFECT")], "DEFEATED"),
        ([("HIGH", "HIGH_CONFIDENCE", "none", "CONTRADICTORY_EVIDENCE")], "DEFEATED"),  # backed by contradictory evidence
        ([("HIGH", "CONFIRMED", "none", "IMPLEMENTATION_DEFECT")], "CHALLENGED"),  # not backed: no counterexample
        ([("CRITICAL", "PLAUSIBLE", "none", "SECURITY_RISK")], "CHALLENGED"),  # a CRITICAL finding is never softened
        ([("CRITICAL", "CONFIRMED", "none", "SECURITY_RISK")], "CHALLENGED"),
        ([("CRITICAL", "SPECULATIVE", "steps", "SECURITY_RISK")], "SURVIVED WITH CONDITIONS"),  # the speculative cap
        ([("MEDIUM", "SPECULATIVE", "none", "DESIGN_RISK")] * 2, "SURVIVED WITH CONDITIONS"),  # speculative mediums do not add up
        ([("MEDIUM", "PLAUSIBLE", "none", "DESIGN_RISK")], "SURVIVED WITH CONDITIONS"),  # one medium is a condition
        ([("MEDIUM", "PLAUSIBLE", "none", "DESIGN_RISK")] * 2, "CHALLENGED"),
        ([("LOW", "CONFIRMED", "none", "TEST_GAP")], "SURVIVED WITH CONDITIONS"),
        ([("HIGH", "DISPROVEN", "none", "IMPLEMENTATION_DEFECT")], "SURVIVED"),  # a disproven path leaves a clean survive
        ([("HIGH", "PLAUSIBLE", "none", "EVIDENCE_GAP")], "INSUFFICIENT EVIDENCE"),
        ([("HIGH", "PLAUSIBLE", "none", "EVIDENCE_GAP"), ("HIGH", "PLAUSIBLE", "none", "DESIGN_RISK")], "CHALLENGED"),  # another strong finding wins
        ([("HIGH", "PLAUSIBLE", "none", "EVIDENCE_GAP"), ("CRITICAL", "CONFIRMED", "steps", "IMPLEMENTATION_DEFECT")], "DEFEATED"),
        ([("CRITICAL", "CONFIRMED", "steps", "EVIDENCE_GAP")], "DEFEATED"),  # an evidence gap that carries a counterexample still defeats
        ([("HIGH", "PLAUSIBLE", "none", "EVIDENCE_GAP")] + [("MEDIUM", "PLAUSIBLE", "none", "DESIGN_RISK")] * 2, "INSUFFICIENT EVIDENCE"),  # the mediums are ignored
        ([("LOW", "CONFIRMED", "none", "EVIDENCE_GAP")], "SURVIVED WITH CONDITIONS"),  # a low gap is a condition, not insufficiency
    ],
)
def test_the_verdict_rules_give_every_set_of_findings_exactly_one_verdict(findings, expected):
    built = [{"severity": s, "confidence": conf, "counterexample": ce, "category": cat} for s, conf, ce, cat in findings]
    assert c.expected_verdict(built) == expected
    assert [v for v in c.VERDICTS if c.permitted(v, built)] == [expected]  # exactly one, so total and exclusive


def test_it_never_invents_a_defect():
    assert "Never invent a defect" in SKILL and "NEMESIS never has to find a defect" in SKILL and "Do not manufacture faults" in SKILL


def test_the_reverse_hypothesis_comes_before_any_investigation():
    order = ["## 3. Reverse hypothesis", "## 4. Challenge plan", "## 5. Independent evidence", "## 6. Requirement-by-requirement attack"]
    assert [SKILL.index(h) for h in order] == sorted(SKILL.index(h) for h in order)
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
    assert "`DEFEATED`" in rows[0][0] and "`CHALLENGED`" in rows[0][0] and "`INSUFFICIENT EVIDENCE`" in rows[1][0] and "`SURVIVED`" in rows[2][0]


def test_the_report_template_carries_every_header_key():
    header = yaml.safe_load(c.fenced(c.section(SKILL, "## 12. Report"), "yaml")[0])
    assert list(header) == c.HEADER_KEYS and header["access"] == "read_only"
    listed = re.findall(r"^\d+\. `([^`]+)`", c.section(SKILL, "## 12. Report"), re.M)
    assert listed == ["# NEMESIS VERDICT: <verdict>"] + c.BODY_HEADINGS[1:]
    assert all(key in c.section(SKILL, "## 12. Report") for key in c.FINDING_KEYS)


def test_the_status_vocabulary_is_defined():
    section = c.section(SKILL, "## 13. Status vocabulary")
    assert all("`%s`" % s in section for s in c.STATUS_STRINGS)


def test_the_limits_are_stated_plainly():
    section = c.section(SKILL, "## 15. Limits")
    assert "cannot technically enforce" in section and "context_isolated" in section
