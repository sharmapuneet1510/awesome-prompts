# tests/tools/test_claude_plugins.py
"""tools/claude_plugins.py: sources -> Claude Code plugin files (#53)."""
import json
from pathlib import Path

import yaml

from tools.claude_plugins import MARKETPLACE, argument_hint, build_plugins, skill_name, use_when
from tools.exporter import AgentFile, FunctionFile, InstructionFile, ModuleFile, SkillFile

SKILL = """---
name: ADR Skill
version: 1.0
description: >
  Records decisions. Longer text follows here.
applies_to: [all]
tags: [adr]
---

# ADR Skill

## Quick Card

| | |
|---|---|
| **Use when** | A change alters a contract or `architect:adr` runs |
| **Skip when** | Nothing is decided |

See [traceability](traceability_skill.md#quick-card) and [docs](../docs/guide.md).
"""

SKILL_NO_CARD = """---
name: Traceability Skill
version: 1.0
description: Checks the chain end to end. Second sentence.
applies_to: [all]
tags: [trace]
---

# Traceability
"""

FUNCTION = """---
name: architect:adr Function
version: 1.0
description: Mint an Engineering Decision Record
prefix: architect:adr
---

# architect:adr

## Inputs

```
architect:adr jira=PROJ-123 [path=./src]
```

Uses [the ADR skill](../../../skills/adr_skill.md), [analysis](analyse.md),
[review](../../quality/functions/review.md) and [a site](https://example.com/x.md).
"""

FUNCTION_NO_INPUTS = """---
name: architect:analyse Function
version: 1.0
description: Analyse a Jira item
prefix: architect:analyse
---

# architect:analyse

No inputs block here. Back to [adr](adr.md).
"""

REVIEW = """---
name: quality:review Function
version: 1.0
description: Review a pull request
prefix: quality:review
---

# quality:review

Follow the [rules](../../../instructions/master_instruction_set.md).

## Inputs

```
quality:review
```
"""

AGENT = """---
name: AP: Architect Agent
version: 3.0
description: >
  Systems architect. Designs things.
---

# Architect Agent

Functions: [adr](architect/functions/adr.md). Rules: [rules](../instructions/master_instruction_set.md).
"""

RULES = """---
name: Master Rules
description: Rules.
applies_to: [all]
---

# Rules
"""


def _repo(tmp_path: Path):
    def write(rel, text):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    write("docs/guide.md", "# guide\n")
    skills = [SkillFile.from_path(write("skills/adr_skill.md", SKILL)),
              SkillFile.from_path(write("skills/traceability_skill.md", SKILL_NO_CARD))]
    functions = [FunctionFile.from_path(write("agents/architect/functions/adr.md", FUNCTION)),
                 FunctionFile.from_path(write("agents/architect/functions/analyse.md", FUNCTION_NO_INPUTS)),
                 FunctionFile.from_path(write("agents/quality/functions/review.md", REVIEW))]
    agents = [AgentFile.from_path(write("agents/architect_agent.md", AGENT))]
    instructions = [InstructionFile.from_path(write("instructions/master_instruction_set.md", RULES))]
    return build_plugins(tmp_path, skills, agents, [], functions, instructions, version="9.9.9")


def _front(text: str) -> dict:
    assert text.startswith("---\n")
    return yaml.safe_load(text.split("---", 2)[1])


def test_skill_name_is_kebab_without_suffix():
    assert skill_name("java_advanced_skill") == "java-advanced"
    assert skill_name("adr_skill") == "adr"


def test_use_when_reads_the_quick_card():
    assert use_when(SKILL.split("---", 2)[2], "x") == "A change alters a contract or `architect:adr` runs"


def test_description_falls_back_to_first_sentence(tmp_path):
    files = _repo(tmp_path)
    fm = _front(files["plugins/engineering-skills/skills/traceability/SKILL.md"])
    assert fm["description"] == "Checks the chain end to end."


def test_argument_hint_from_inputs_block():
    assert argument_hint(FUNCTION.split("---", 2)[2], "architect:adr") == "jira=PROJ-123 [path=./src]"


def test_argument_hint_absent_without_inputs():
    assert argument_hint(FUNCTION_NO_INPUTS.split("---", 2)[2], "architect:analyse") is None
    assert argument_hint(REVIEW.split("---", 2)[2], "quality:review") is None


def test_function_skill_front_matter(tmp_path):
    files = _repo(tmp_path)
    text = files["plugins/architect/skills/adr/SKILL.md"]
    fm = _front(text)
    assert fm == {"name": "adr", "description": "Mint an Engineering Decision Record",
                  "argument-hint": "jira=PROJ-123 [path=./src]", "disable-model-invocation": True}
    assert "${CLAUDE_PLUGIN_ROOT}/reference/agent.md" in text
    assert "${CLAUDE_PLUGIN_ROOT}/reference/rules.md" in text


def test_reference_skill_front_matter(tmp_path):
    fm = _front(_repo(tmp_path)["plugins/engineering-skills/skills/adr/SKILL.md"])
    assert fm == {"name": "adr", "description": "A change alters a contract or `architect:adr` runs"}


def test_links_are_rewritten_for_the_plugin_layout(tmp_path):
    files = _repo(tmp_path)
    adr = files["plugins/architect/skills/adr/SKILL.md"]
    assert "the ADR skill (`engineering-skills:adr` skill)" in adr          # other plugin's skill
    assert "[analysis](../analyse/SKILL.md)" in adr                          # same plugin
    assert "review (`/quality:review`)" in adr                               # other plugin's function
    assert "[a site](https://example.com/x.md)" in adr                       # URL untouched
    skill = files["plugins/engineering-skills/skills/adr/SKILL.md"]
    assert "[traceability](../traceability/SKILL.md#quick-card)" in skill    # same plugin, anchor kept
    assert ("[docs](https://github.com/sharmapuneet1510/awesome-prompts/blob/main/docs/guide.md)"
            in skill)                                                        # not shipped -> GitHub
    agent = files["plugins/architect/reference/agent.md"]
    assert "[adr](../skills/adr/SKILL.md)" in agent
    assert "[rules](rules.md)" in agent
    review = files["plugins/quality/skills/review/SKILL.md"]
    assert "[rules](../../reference/rules.md)" in review                     # each role plugin has its own copy


def test_manifests(tmp_path):
    files = _repo(tmp_path)
    plugin = json.loads(files["plugins/architect/.claude-plugin/plugin.json"])
    assert plugin["name"] == "architect" and plugin["version"].startswith("9.9.9+")
    assert plugin["description"] == "Systems architect."
    market = json.loads(files[MARKETPLACE])
    assert market["name"] == "awesome-prompts" and market["owner"]["name"]
    entries = {p["name"]: p["source"] for p in market["plugins"]}
    assert entries == {"architect": "./plugins/architect", "quality": "./plugins/quality",
                       "engineering-skills": "./plugins/engineering-skills"}


def test_rules_ship_in_every_role_plugin(tmp_path):
    files = _repo(tmp_path)
    assert "plugins/architect/reference/rules.md" in files
    assert "plugins/quality/reference/rules.md" in files
    assert "plugins/engineering-skills/reference/rules.md" not in files


def test_plugin_version_tracks_its_own_content(tmp_path, monkeypatch):
    # Claude Code pins installs to `version`, so it must change whenever a plugin's content does.
    import tests.tools.test_claude_plugins as fixtures
    version = lambda files, p: json.loads(files[f"plugins/{p}/.claude-plugin/plugin.json"])["version"]
    first = _repo(tmp_path / "a")
    assert version(first, "architect").startswith("9.9.9+")
    assert version(_repo(tmp_path / "b"), "architect") == version(first, "architect")    # deterministic
    monkeypatch.setattr(fixtures, "FUNCTION", FUNCTION + "\nOne more line.\n")
    changed = _repo(tmp_path / "c")
    assert version(changed, "architect") != version(first, "architect")
    assert version(changed, "quality") == version(first, "quality")                    # other plugins untouched
