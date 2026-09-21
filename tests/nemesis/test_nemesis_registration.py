import re
import subprocess
import sys

from . import common as c

COVERS = ["N14", "N12"]

ROOT = c.ROOT


def dispatch_functions():
    names = set()
    for prefix, filename in c.AGENT_FILES.items():
        names |= {"%s:%s" % (prefix, n) for n in re.findall(r"^\| `%s:([\w-]+)`" % prefix, c.read(ROOT / "agents" / filename), re.M)}
    return names


def test_the_function_and_skill_counts_are_real():
    assert len(dispatch_functions()) == 43
    assert len(list((ROOT / "skills").glob("*_skill.md"))) == 37
    assert len(list((ROOT / "agents").glob("*/functions/*.md"))) == 35


def test_the_documents_state_the_real_counts():
    functions, skills = len(dispatch_functions()), len(list((ROOT / "skills").glob("*_skill.md")))
    badge = c.read(ROOT / "README.md")
    assert "functions-%d-" % functions in badge and "skills-%d-" % skills in badge
    assert "%d callable functions" % functions in c.read(ROOT / "CLAUDE.md") and "(%d skills" % skills in c.read(ROOT / "CLAUDE.md")
    assert "%d skills, %d callable functions" % (skills, functions) in c.read(ROOT / "agents" / "README.md")
    assert "All %d callable functions" % functions in c.read(ROOT / "docs" / "02-reference" / "functions.md")
    assert "**%d skills.**" % skills in c.read(ROOT / "docs" / "02-reference" / "skills.md")
    assert "%d functions, %d skills" % (functions, skills) in c.read(ROOT / "docs" / "README.md")
    assert "%d skills, zero orphans" % skills in c.read(ROOT / "skills" / "README.md")


def test_the_workflow_count_matches_the_workflow_files():
    files = [p for p in (ROOT / "docs" / "01-workflows").glob("[0-9][0-9]-*.md")]
    assert len(files) == 15
    assert "The 15 workflows" in c.read(ROOT / "README.md") and "15 use cases" in c.read(ROOT / "CLAUDE.md")


def test_the_function_and_skill_are_listed_in_the_reference_docs():
    assert "`orchestrator:nemesis`" in c.read(ROOT / "docs" / "02-reference" / "functions.md")
    assert "`nemesis_skill`" in c.read(ROOT / "docs" / "02-reference" / "skills.md")
    assert "nemesis_skill.md" in c.read(ROOT / "skills" / "README.md")
    assert "nemesis" in c.read(ROOT / "docs" / "02-reference" / "agents.md")
    assert "| `orchestrator:nemesis` |" in c.read(ROOT / "docs" / "01-workflows" / "sdlc-playbook.md")


def test_the_workflow_doc_exists_and_is_linked_everywhere():
    assert (ROOT / "docs" / "01-workflows" / "15-challenge-a-conclusion.md").exists()
    for path in ["README.md", "docs/README.md", "docs/01-workflows/README.md"]:
        assert "15-challenge-a-conclusion.md" in c.read(ROOT / path), path


def test_every_relative_link_in_the_new_documents_resolves():
    for path in [ROOT / "docs/01-workflows/15-challenge-a-conclusion.md", c.FUNCTION, c.SKILL, *c.EXAMPLES]:
        for target in re.findall(r"\]\(([^)\s#]+)", c.read(path)):
            if not target.startswith(("http://", "https://", "mailto:")):
                assert (path.parent / target).exists(), "%s -> %s" % (path.name, target)


def test_the_examples_and_the_config_template_are_indexed():
    index = c.read(ROOT / "docs" / "04-examples" / "README.md")
    assert "nemesis-defeated.md" in index and "nemesis-survived.md" in index and "nemesis-config.example.yml" in index


def test_the_changelog_records_it():
    text = c.read(ROOT / "CHANGELOG.md")
    assert "## [Unreleased]" in text and "NEMESIS" in text.split("## [5.1.0]")[0]


def test_the_exporter_lists_the_skill():
    done = subprocess.run([sys.executable, str(ROOT / "tools" / "exporter.py"), "--list"], cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    assert done.returncode == 0 and "nemesis_skill" in done.stdout
