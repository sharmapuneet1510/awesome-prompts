"""Traceability: every requirement in the approved spec is covered by at least one test module.

Each test module declares `COVERS = ["R1", ...]` near its top. R13 (docs) is covered by test_docs.py
and R12 (acceptance thresholds) by the eval tooling tests plus the bake-off itself.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = HERE.parents[1] / "docs" / "superpowers" / "specs" / "2026-09-20-prompt-preflight-hook-design.md"


def spec_requirements():
    text = SPEC.read_text(encoding="utf-8")
    section = text.split("## Requirements", 1)[1].split("### Non-goals", 1)[0]
    return set(re.findall(r"^\| \*\*(R\d+)\*\*", section, re.M))


def declared_coverage():
    covers = {}
    for path in sorted(HERE.glob("test_*.py")):
        if path.name == "test_traceability.py":
            continue
        match = re.search(r"^COVERS = \[(.*?)\]", path.read_text(encoding="utf-8"), re.M)
        covers[path.name] = set(re.findall(r"R\d+", match.group(1))) if match else None
    return covers


def test_the_spec_lists_requirements():
    assert len(spec_requirements()) == 14


def test_every_requirement_is_covered_by_at_least_one_test_module():
    covered = set().union(*[c for c in declared_coverage().values() if c])
    assert sorted(spec_requirements() - covered) == []


def test_every_test_module_declares_what_it_covers():
    assert [name for name, c in declared_coverage().items() if c is None] == []


def test_covers_lists_only_real_requirements():
    real = spec_requirements()
    bogus = {name: sorted(c - real) for name, c in declared_coverage().items() if c and c - real}
    assert bogus == {}
