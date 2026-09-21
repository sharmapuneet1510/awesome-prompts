"""Shared helpers for the NEMESIS contract tests. The enumerations below are the spec's source of truth."""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "nemesis_skill.md"
FUNCTION = ROOT / "agents" / "orchestrator" / "functions" / "nemesis.md"
CONFIG_EXAMPLE = ROOT / "docs" / "04-examples" / "nemesis-config.example.yml"
EXAMPLES = [ROOT / "docs" / "04-examples" / "nemesis-defeated.md", ROOT / "docs" / "04-examples" / "nemesis-survived.md"]
SPEC = ROOT / "docs" / "superpowers" / "specs" / "2026-09-21-nemesis-design.md"

CATEGORIES = [
    "REQUIREMENT_GAP", "IMPLEMENTATION_DEFECT", "ARCHITECTURE_RISK", "DESIGN_RISK", "TEST_GAP", "EVIDENCE_GAP",
    "SECURITY_RISK", "PERFORMANCE_RISK", "DATA_RISK", "INTEGRATION_RISK", "REGRESSION_RISK", "OPERATIONAL_RISK",
    "ASSUMPTION", "AMBIGUOUS_REQUIREMENT", "CONTRADICTORY_EVIDENCE", "FALSE_POSITIVE", "FALSE_NEGATIVE",
]
SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"]
CONFIDENCES = ["CONFIRMED", "HIGH_CONFIDENCE", "PLAUSIBLE", "SPECULATIVE", "DISPROVEN"]
VERDICTS = ["SURVIVED", "SURVIVED WITH CONDITIONS", "CHALLENGED", "DEFEATED", "INSUFFICIENT EVIDENCE"]
EVIDENCE_CLASSES = ["STRONG", "PARTIAL", "WEAK", "MISSING", "IRRELEVANT", "CONTRADICTORY"]
CAUSE_CLASSES = [
    "REQUIREMENT_MISUNDERSTOOD", "ASSUMPTION_UNTESTED", "EVIDENCE_INADEQUATE", "CHECK_SCOPE_TOO_NARROW", "DESIGN_FLAW",
    "IMPLEMENTATION_SLIP", "INTEGRATION_MISMATCH", "ENVIRONMENT_DIFFERENCE", "PROCESS_GAP", "FALSE_CONFIDENCE",
]
LAYERS = ["defect", "miss"]
STATUS_STRINGS = [
    "NEMESIS ACTIVATED", "NEMESIS IS CHALLENGING THE CONCLUSION", "COUNTEREXAMPLE DETECTED",
    "CONCLUSION COMPROMISED", "NEMESIS SURVIVED", "NEMESIS DEFEATED THE CONCLUSION",
]
HEADER_KEYS = [
    "nemesis_id", "created", "target", "original_agent", "original_verdict", "nemesis_persona", "verdict", "findings",
    "hypotheses", "sources", "context_isolated", "access", "trigger", "depth", "parent_nemesis",
]
FINDING_KEYS = ["id", "category", "severity", "confidence", "traces_to", "evidence", "counterexample", "impact", "required_action"]
HYPOTHESIS_KEYS = ["id", "layer", "statement", "mechanism", "explains", "cause_class", "confidence", "rank", "discriminating_check"]
BODY_HEADINGS = [
    "# NEMESIS VERDICT:", "## Failure-cause hypotheses", "## Original conclusion", "## Reverse hypothesis",
    "## Challenge paths executed", "## Findings", "## Evidence assessment", "## Required actions",
]
TRIGGERS = ["manual", "workflow", "policy", "agent"]
AUTO_ACTIVATE = [
    "critical_change", "production_release", "architecture_change", "security_change", "regulatory_change", "payment_change",
]
AGENT_FILES = {
    "orchestrator": "orchestrator_agent.md", "architect": "architect_agent.md", "implementer": "implementer_agent.md",
    "quality": "quality_agent.md", "ba": "business_analyst_agent.md",
}


def flat(text):
    """Collapse whitespace so a phrase that wraps across lines still matches."""
    return " ".join(text.split())


def read(path):
    return Path(path).read_text(encoding="utf-8")


def section(text, heading, level=None):
    """The text of the section that starts at `heading` and runs to the next heading of the same or a higher level."""
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(heading))
    depth = level or len(lines[start]) - len(lines[start].lstrip("#"))
    end = len(lines)
    for i in range(start + 1, len(lines)):
        stripped = lines[i]
        if stripped.startswith("#") and len(stripped) - len(stripped.lstrip("#")) <= depth and stripped.lstrip("#").startswith(" "):
            end = i
            break
    return "\n".join(lines[start:end])


def fenced(text, language=None):
    pattern = r"```%s\n(.*?)```" % (re.escape(language) if language else r"[a-z]*")
    return re.findall(pattern, text, re.S)


def table_rows(text):
    rows = []
    for line in text.splitlines():
        if line.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", line):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return rows[1:] if rows else rows  # drop the header row


def front_matter(text):
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert match, "no front matter"
    return yaml.safe_load(match.group(1))


def load_report(path):
    text = read(path)
    header = front_matter(text)
    blocks = fenced(text, "yaml")
    hypotheses = yaml.safe_load(blocks[0])
    findings = yaml.safe_load(blocks[1])
    return text, header, findings or [], hypotheses or []


def permitted(verdict, findings):
    """The documented verdict rules (skill §10), as a predicate over a report's findings."""
    def defeating(f):
        return f["severity"] in ("CRITICAL", "HIGH") and f["confidence"] in ("CONFIRMED", "HIGH_CONFIDENCE") and str(f["counterexample"]).strip().lower() != "none"

    def challenging(f):
        return f["severity"] == "HIGH" and f["confidence"] in ("CONFIRMED", "HIGH_CONFIDENCE", "PLAUSIBLE")

    if verdict == "DEFEATED":
        return any(defeating(f) for f in findings)
    if any(defeating(f) for f in findings):
        return False  # a defeating finding leaves no other verdict open
    if verdict == "CHALLENGED":
        return any(challenging(f) for f in findings) or sum(1 for f in findings if f["severity"] == "MEDIUM") >= 2
    if verdict == "SURVIVED":
        return not findings
    if verdict == "SURVIVED WITH CONDITIONS":
        return not any(challenging(f) for f in findings) and sum(1 for f in findings if f["severity"] == "MEDIUM" and f["confidence"] != "SPECULATIVE") < 2
    if verdict == "INSUFFICIENT EVIDENCE":
        return True
    raise ValueError(verdict)
