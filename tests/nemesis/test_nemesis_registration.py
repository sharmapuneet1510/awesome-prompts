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


def test_the_counts_include_nemesis():
    # A lower bound, not an exact tripwire: adding a function or skill later must not force an edit here.
    assert "orchestrator:nemesis" in dispatch_functions() and len(dispatch_functions()) >= 43
    assert (ROOT / "skills" / "nemesis_skill.md").exists() and len(list((ROOT / "skills").glob("*_skill.md"))) >= 37
    assert (ROOT / "agents" / "orchestrator" / "functions" / "nemesis.md").exists() and len(list((ROOT / "agents").glob("*/functions/*.md"))) >= 35


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
    assert "Quick Navigation (%d Skills)" % skills in c.read(ROOT / "skills" / "README.md")
    assert "**5 agents, %d functions, %d skills**" % (functions, skills) in c.read(ROOT / "docs" / "99-archive" / "README.md")
    functions_files = len(list((ROOT / "agents").glob("*/functions/*.md")))
    assert "| Skills | %d | `skills/*.md` |" % skills in c.read(ROOT / "docs" / "01-workflows" / "14-export-to-platforms.md")
    assert "| Functions | %d | `agents/*/functions/*.md` |" % functions_files in c.read(ROOT / "docs" / "01-workflows" / "14-export-to-platforms.md")
    assert "| Callable functions | %d |" % functions in c.read(ROOT / "docs" / "02-reference" / "README.md") and "| Skills | %d |" % skills in c.read(ROOT / "docs" / "02-reference" / "README.md")
    concepts = c.read(ROOT / "docs" / "00-getting-started" / "concepts.md")
    assert "| One callable capability of an agent | %d |" % functions in concepts and "| Implementation knowledge a function loads | %d |" % skills in concepts
    assert "implementation knowledge    (%d)" % skills in c.read(ROOT / "docs" / "02-reference" / "agents.md")


def test_the_workflow_count_matches_the_workflow_files():
    files = [p for p in (ROOT / "docs" / "01-workflows").glob("[0-9][0-9]-*.md")]
    assert len(files) == 15
    assert "The 15 workflows" in c.read(ROOT / "README.md") and "15 use cases" in c.read(ROOT / "CLAUDE.md")


def test_the_function_and_skill_are_listed_in_the_reference_docs():
    assert "`orchestrator:nemesis`" in c.read(ROOT / "docs" / "02-reference" / "functions.md")
    assert "`nemesis_skill`" in c.read(ROOT / "docs" / "02-reference" / "skills.md")
    assert "nemesis_skill.md" in c.read(ROOT / "skills" / "README.md")
    assert "· `nemesis`" in c.read(ROOT / "docs" / "02-reference" / "agents.md")
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


def test_the_skills_index_lists_the_new_skill_in_order():
    rows = re.findall(r"^\| (\d+) \| \[", c.read(ROOT / "skills" / "README.md"), re.M)
    assert [int(n) for n in rows] == sorted(int(n) for n in rows) and rows[-1] == str(len(list((ROOT / "skills").glob("*_skill.md"))))


def test_the_workflow_doc_states_each_trigger_point_and_the_guards():
    text = c.flat(c.read(ROOT / "docs" / "01-workflows" / "15-challenge-a-conclusion.md"))
    for phrase in ["after a `PASS`", "between `Status: Proposed` and the approval request", "before the release PR", "**two consecutive**", "`maximum_depth`", "A challenger never evaluates a gate", "even a manual `/nemesis`", "not `enabled: false`"]:
        assert phrase in text, phrase
    assert "target=PR-1839" in text and "CR-839" not in text
    assert "**two consecutive** blocking results" in text and "for the same change" in text
    assert "two rounds at most, see Limits" in text


def test_the_examples_and_the_config_template_are_indexed():
    index = c.read(ROOT / "docs" / "04-examples" / "README.md")
    assert "nemesis-defeated.md" in index and "nemesis-survived.md" in index and "nemesis-config.example.yml" in index


def test_the_changelog_records_it():
    text = c.read(ROOT / "CHANGELOG.md")
    unreleased = text.split("## [Unreleased]", 1)[1].split("\n## [", 1)[0]
    assert "NEMESIS" in unreleased


def test_the_exporter_lists_the_skill():
    done = subprocess.run([sys.executable, str(ROOT / "tools" / "exporter.py"), "--list"], cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    assert done.returncode == 0 and "nemesis_skill" in done.stdout
