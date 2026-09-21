import re

import pytest

from . import common as c

COVERS = ["N9", "N10", "N11"]


@pytest.fixture(params=c.EXAMPLES, ids=lambda p: p.stem)
def report(request):
    return c.load_report(request.param)


def test_the_header_has_every_key_and_a_valid_id(report):
    text, header, findings, hypotheses = report
    assert list(header) == c.HEADER_KEYS
    assert re.fullmatch(r"NMS-\d{4}-\d{5}", header["nemesis_id"])
    assert header["verdict"] in c.VERDICTS and header["access"] == "read_only" and header["trigger"] in c.TRIGGERS
    assert isinstance(header["context_isolated"], bool) and header["depth"] >= 1


def test_the_body_sections_are_present_and_in_order(report):
    text = report[0]
    positions = [text.index(heading) for heading in c.BODY_HEADINGS]
    assert positions == sorted(positions)
    assert "# NEMESIS VERDICT: %s" % report[1]["verdict"] in text


def test_the_header_counts_match_the_lists(report):
    _, header, findings, hypotheses = report
    counts = {name: sum(1 for f in findings if f["severity"] == name.upper()) for name in header["findings"]}
    assert counts == header["findings"]
    assert header["hypotheses"] == len(hypotheses)


def test_every_finding_uses_the_pinned_enumerations(report):
    for finding in report[2]:
        assert list(finding) == c.FINDING_KEYS
        assert finding["category"] in c.CATEGORIES and finding["severity"] in c.SEVERITIES and finding["confidence"] in c.CONFIDENCES
        assert finding["traces_to"], "a finding must trace to a requirement, criterion, constraint, risk, evidence item or invariant"


def test_every_hypothesis_is_ranked_typed_and_testable(report):
    _, header, findings, hypotheses = report
    finding_ids = {f["id"] for f in findings}
    assert sorted(h["rank"] for h in hypotheses) == list(range(1, len(hypotheses) + 1))
    for h in hypotheses:
        assert list(h) == c.HYPOTHESIS_KEYS
        assert h["layer"] in c.LAYERS and h["cause_class"] in c.CAUSE_CLASSES and h["confidence"] in c.CONFIDENCES
        assert str(h["discriminating_check"]).strip() and str(h["mechanism"]).strip()
        assert set(h["explains"]) <= finding_ids


def test_the_verdict_is_consistent_with_the_rules(report):
    _, header, findings, hypotheses = report
    assert c.permitted(header["verdict"], findings)


def report_with(verdict):
    for path in c.EXAMPLES:
        loaded = c.load_report(path)
        if loaded[1]["verdict"] == verdict:
            return loaded
    raise AssertionError("no example report has the verdict %s" % verdict)


def test_the_stated_number_of_challenge_paths_matches_the_numbered_list(report):
    section = c.section(report[0], "## Challenge paths executed")
    stated = re.search(r"^(\d+) paths", section, re.M)
    listed = re.findall(r"^\d+\. ", section, re.M)
    assert stated and int(stated.group(1)) == len(listed) >= 1, (stated and stated.group(0), len(listed))


def test_a_derived_counterexample_is_never_confirmed(report):
    for finding in report[2]:
        if "derived" in str(finding["counterexample"]).lower():
            assert finding["confidence"] != "CONFIRMED", finding["id"]


def test_defeated_and_challenged_reports_carry_hypotheses_of_both_layers_when_they_can():
    _, header, findings, hypotheses = report_with("DEFEATED")
    assert header["verdict"] == "DEFEATED" and {h["layer"] for h in hypotheses} == {"defect", "miss"}
    assert hypotheses[0]["rank"] == 1 and set(hypotheses[0]["explains"]) & {f["id"] for f in findings}


def test_the_survived_example_lists_the_challenge_paths_and_invents_nothing():
    text, header, findings, hypotheses = report_with("SURVIVED")
    assert header["verdict"] == "SURVIVED" and findings == []
    assert all(h["confidence"] == "SPECULATIVE" for h in hypotheses)  # conditions, not defects
