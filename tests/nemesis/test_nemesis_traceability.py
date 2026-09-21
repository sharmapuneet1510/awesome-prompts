"""Traceability: every NEMESIS requirement in the approved spec is covered by at least one test module."""
import re
from pathlib import Path

from . import common as c

HERE = Path(__file__).resolve().parent


def spec_requirements():
    text = c.read(c.SPEC)
    section = text.split("## Requirements", 1)[1].split("**Non-goals.**", 1)[0]
    return set(re.findall(r"^\| \*\*(N\d+)\*\*", section, re.M))


def declared_coverage():
    covers = {}
    for path in sorted(HERE.glob("test_nemesis_*.py")):
        if path.name == "test_nemesis_traceability.py":
            continue
        match = re.search(r"^COVERS = \[(.*?)\]", path.read_text(encoding="utf-8"), re.M)
        ids = set(re.findall(r"N\d+", match.group(1))) if match else set()
        covers[path.name] = ids or None
    return covers


def test_the_spec_lists_fourteen_requirements():
    assert len(spec_requirements()) == 14


def test_every_requirement_is_covered_by_at_least_one_module():
    covered = set().union(*[ids for ids in declared_coverage().values() if ids])
    assert sorted(spec_requirements() - covered) == []


def test_every_module_declares_what_it_covers():
    assert [name for name, ids in declared_coverage().items() if ids is None] == []


def test_covers_lists_only_real_requirements():
    real = spec_requirements()
    bogus = {name: sorted(ids - real) for name, ids in declared_coverage().items() if ids and ids - real}
    assert bogus == {}
