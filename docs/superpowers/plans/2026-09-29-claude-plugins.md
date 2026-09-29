# Claude Code Plugins Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `python3 tools/exporter.py --target claude` produces a Claude Code marketplace of six plugins, so `/architect:adr` and the other 42 functions become real slash commands and the 44 skills load in Claude Code.

**Architecture:** A new pure module `tools/claude_plugins.py` turns the parsed sources (the `SkillFile`/`FunctionFile`/… objects `tools/exporter.py` already builds) into a `dict` of relative path → file text. `ClaudeExporter` writes that dict under `plugins/` and `.claude-plugin/`, prunes stale files there, and still exports hooks. Tests check the output structurally, check that the committed output is fresh, and run `claude plugin validate --strict` when the CLI is present.

**Tech Stack:** Python 3.11, PyYAML (already a runtime dependency), pytest, Claude Code CLI ≥ 2.1.284 for validation.

**Spec:** `docs/superpowers/specs/2026-09-29-claude-plugins-design.md`

## Global Constraints

- Branch `feat/53-claude-plugins`; commits have **no** `Co-Authored-By` trailer (user preference).
- Plugin names: `orchestrator`, `architect`, `implementer`, `quality`, `ba`, `engineering-skills`. Marketplace name: `awesome-prompts`.
- Every function `SKILL.md` has `disable-model-invocation: true`. Reference skills have no invocation restriction.
- `name`: kebab-case, ≤ 64 characters, unique within its plugin. `description` + `when_to_use` ≤ 1,536 characters.
- Reference-skill `description` = the Quick Card **Use when** row; fallback = first sentence of the front matter `description`.
- Front matter is the file's first line (`---`), rendered with `yaml.safe_dump`.
- Links: same plugin → relative path; other plugin's skill → `` `engineering-skills:<name>` skill ``; other plugin's function → `` `/<plugin>:<fn>` ``; any other existing repo file → `https://github.com/sharmapuneet1510/awesome-prompts/blob/main/<path>`; URLs, anchors-only and already-broken links unchanged.
- `plugin.json` version = `pyproject.toml` `[project] version` (currently `5.0.1`).
- The Claude target always exports the **full** set, ignoring `--skills/--agents/...` filters (a partial plugin set would delete the others).
- Suite must stay green after every task: `python3 -m pytest -q`.

## Review Focus

1. **Filtered runs** (`--target claude --skills java`) must not delete or thin out the other plugins — Task 3 test `test_claude_target_ignores_filters`.
2. **A function with no `## Inputs` block** or an Inputs block with no arguments gets no `argument-hint`, not an empty or garbage one — Task 2 test `test_argument_hint_absent_without_inputs`.
3. **A skill whose Quick Card has no "Use when" row** still gets a non-empty, one-sentence description — Task 2 test `test_description_falls_back_to_first_sentence`.
4. **Re-exporting after a skill is renamed or deleted** removes the old `skills/<old>/` folder, and never touches files outside `plugins/` — Task 3 tests `test_export_prunes_stale_plugin_files` and `test_export_prunes_only_inside_plugins`.
5. **`--target-project ~/app --target claude`** must not silently copy the old non-loading flat files — Task 3 test `test_target_project_claude_points_to_marketplace`.

---

### Task 1: Every dispatch-table function has a function file

Seven orchestrator functions live only as sections of `agents/orchestrator_agent.md`, and `ba:create` has no file. Move them into function files so all 43 functions can become commands.

**Files:**
- Create: `agents/orchestrator/functions/{plan,context,build,pr,review,tradeoff,risk}.md`, `agents/business_analyst/functions/create.md`
- Modify: `agents/orchestrator_agent.md` (the `## Function Details` section, currently lines ~944–1130), `docs/01-workflows/14-export-to-platforms.md` (What gets exported table + the paragraph under it)
- Test: `tests/test_function_files.py`

**Interfaces:**
- Produces: 43 files `agents/<dir>/functions/<fn>.md`, each with front matter `name`, `version`, `description`, `prefix: <plugin>:<fn>`. Task 2 derives the plugin name from `prefix`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_function_files.py
"""Every function in an agent's dispatch table has its own function file (#53)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = {
    "orchestrator": ("orchestrator_agent.md", "orchestrator"),
    "architect": ("architect_agent.md", "architect"),
    "implementer": ("implementer_agent.md", "implementer"),
    "quality": ("quality_agent.md", "quality"),
    "ba": ("business_analyst_agent.md", "business_analyst"),
}


def test_every_dispatch_function_has_a_file():
    missing = []
    for prefix, (agent_file, folder) in AGENTS.items():
        table = (ROOT / "agents" / agent_file).read_text(encoding="utf-8")
        for fn in set(re.findall(r"^\| `%s:([\w-]+)`" % prefix, table, re.M)):
            path = ROOT / "agents" / folder / "functions" / f"{fn}.md"
            if not path.exists():
                missing.append(f"{prefix}:{fn}")
    assert sorted(missing) == []


def test_every_function_file_declares_its_prefix():
    for path in sorted((ROOT / "agents").glob("*/functions/*.md")):
        head = path.read_text(encoding="utf-8").split("---", 2)[1]
        assert re.search(r"^prefix: [a-z]+:%s$" % re.escape(path.stem), head, re.M), path
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 -m pytest tests/test_function_files.py -q`
Expected: FAIL — `missing` lists `ba:create` and `orchestrator:{build,context,plan,pr,review,risk,tradeoff}`.

- [ ] **Step 3: Extract the seven orchestrator sections**

Run this once. It writes each `### orchestrator:<fn>` section (up to the next `---` line) into its own file, using the dispatch-table text as `description`, then replaces the `## Function Details` section with a link table.

```bash
python3 - <<'EOF'
import re
from pathlib import Path
agent = Path("agents/orchestrator_agent.md")
text = agent.read_text(encoding="utf-8")
table = dict(re.findall(r"^\| `orchestrator:([\w-]+)` \| ([^|]+?) \|", text, re.M))
start = text.index("## Function Details")
end = text.index("\n## ", start + 5)
section = text[start:end]
rows = []
for fn in ["plan", "context", "build", "pr", "review", "tradeoff", "risk"]:
    m = re.search(r"### orchestrator:%s\n(.*?)(?=\n---\n|\Z)" % fn, section, re.S)
    body = m.group(1).strip()
    desc = table[fn].strip().replace('"', "'")
    Path(f"agents/orchestrator/functions/{fn}.md").write_text(
        f'---\nname: orchestrator:{fn} Function\nversion: 1.0\ndescription: "{desc}"\n'
        f"prefix: orchestrator:{fn}\n---\n\n# orchestrator:{fn}\n\n{body}\n", encoding="utf-8")
    rows.append(f"| `orchestrator:{fn}` | [functions/{fn}.md](orchestrator/functions/{fn}.md) |")
new = ("## Function Details\n\nEach function's inputs, outputs and steps live in its own file:\n\n"
       "| Function | Definition |\n|---|---|\n" + "\n".join(rows) + "\n\n"
       "`ideate`, `solve` and `nemesis` are in the same folder.\n\n---\n")
agent.write_text(text[:start] + new + text[end:], encoding="utf-8")
EOF
```

Then open `agents/orchestrator/functions/plan.md` and check it reads as a complete function: front matter, `# orchestrator:plan`, then **Input**, **Output** and **Steps**.

- [ ] **Step 4: Write `agents/business_analyst/functions/create.md`**

````markdown
---
name: ba:create Function
version: 1.0
description: "Parse a plain-text requirements file into Jira issues with BDD acceptance criteria, plus HTML requirement cards"
prefix: ba:create
---

# ba:create

Turns a plain-text requirements file into structured Jira issues with
Given/When/Then acceptance criteria, and renders them as HTML requirement cards.

## Inputs

```
ba:create path=./requirements.txt
```

- `path` (string, required) — the requirements file (plain text, Markdown, or one requirement per line)

## Outputs

```
✓ requirements.json            — Jira-ready issues with BDD acceptance criteria
✓ requirements-cards.html      — one card per requirement
```

## Workflow

Follow [ba_create_skill](../../../skills/ba_create_skill.md): detect the input
format, extract requirements, write acceptance criteria that a test can assert,
and render the cards. Ask about any requirement that has no testable outcome
instead of inventing one.
````

- [ ] **Step 5: Update the export doc counts**

In `docs/01-workflows/14-export-to-platforms.md`, change the table row to `| Functions | 43 | \`agents/*/functions/*.md\` |` and replace the paragraph starting "Function *files* number 35" with:

```markdown
Each of the 43 callable functions has its own file.
```

- [ ] **Step 6: Run the tests**

Run: `python3 -m pytest -q`
Expected: PASS, including `tests/test_function_files.py` and `tests/nemesis/test_nemesis_registration.py` (it checks the `| Functions | 43 |` row against the file count).

- [ ] **Step 7: Commit**

```bash
git add agents docs/01-workflows/14-export-to-platforms.md tests/test_function_files.py
git commit -m "refactor(agents): give every dispatch-table function its own file (#53)"
```

---

### Task 2: Pure plugin builder

**Files:**
- Create: `tools/claude_plugins.py`
- Test: `tests/tools/test_claude_plugins.py`

**Interfaces:**
- Consumes: objects with the attributes of `tools.exporter.SkillFile` (`path`, `slug`, `name`, `description`, `content`), `FunctionFile` (`path`, `slug`, `name`, `description`, `prefix`, `content`), `AgentFile` (`path`, `slug`, `description`, `content`), `ModuleFile` (`path`, `slug`, `agent_type`, `content`), `InstructionFile` (`path`, `slug`, `content`). `content` is the body without front matter.
- Produces:
  - `build_plugins(repo_root: Path, skills, agents, modules, functions, instructions, version: str) -> dict[str, str]` — keys are POSIX paths relative to `repo_root` (`"plugins/architect/skills/adr/SKILL.md"`, `".claude-plugin/marketplace.json"`), values are file text.
  - `PLUGIN_ROOT = "plugins"`, `MARKETPLACE = ".claude-plugin/marketplace.json"`, `SKILLS_PLUGIN = "engineering-skills"`.
  - Helpers used by tests: `skill_name(slug) -> str`, `use_when(skill_content, fallback) -> str`, `argument_hint(function_content, prefix) -> str | None`.

- [ ] **Step 1: Write the failing tests**

````python
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
    assert plugin["name"] == "architect" and plugin["version"] == "9.9.9"
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
````

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest tests/tools/test_claude_plugins.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.claude_plugins'`.

- [ ] **Step 3: Write `tools/claude_plugins.py`**

```python
"""Build Claude Code plugins from this repository's sources.

Pure: takes the parsed source objects that tools/exporter.py builds and returns
{relative path: file text}. tools/exporter.py's ClaudeExporter writes the result.
Spec: docs/superpowers/specs/2026-09-29-claude-plugins-design.md
"""
from __future__ import annotations

import json
import posixpath
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import yaml

PLUGIN_ROOT = "plugins"
MARKETPLACE = ".claude-plugin/marketplace.json"
SKILLS_PLUGIN = "engineering-skills"
MARKETPLACE_NAME = "awesome-prompts"
OWNER = "Puneet Sharma"
REPO_URL = "https://github.com/sharmapuneet1510/awesome-prompts"
BLOB_URL = REPO_URL + "/blob/main/"
RULES_SLUG = "master_instruction_set"

_USE_WHEN = re.compile(r"^\|\s*\*\*Use when\*\*\s*\|\s*(.+?)\s*\|\s*$", re.M)
_INPUTS = re.compile(r"^## Inputs\s*\n+`{3}[^\n]*\n(?P<first>[^\n]*)", re.M)   # `{3} = a code fence
_LINK = re.compile(r"\[(?P<label>[^\]]*)\]\((?P<target>[^)\s#]+)(?P<anchor>#[^)\s]*)?\)")


@dataclass(frozen=True)
class _Shipped:
    plugin: str
    rel: PurePosixPath      # path inside the plugin, e.g. skills/adr/SKILL.md
    kind: str               # skill | function | agent | rules | module
    name: str               # skill or function name, for cross-plugin references


def skill_name(slug: str) -> str:
    """adr_skill -> adr; java_advanced_skill -> java-advanced."""
    return re.sub(r"_skill$", "", slug).replace("_", "-")


def first_sentence(text: str) -> str:
    text = " ".join(text.split())
    return re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0]


def use_when(content: str, fallback: str) -> str:
    """The Quick Card 'Use when' row, else the first sentence of the fallback."""
    match = _USE_WHEN.search(content)
    return match.group(1).strip() if match else first_sentence(fallback)


def argument_hint(content: str, prefix: str) -> str | None:
    """Arguments from the first line of the function's '## Inputs' code block."""
    match = _INPUTS.search(content)
    if not match:
        return None
    first = match.group("first").strip()
    if not first.startswith(prefix):
        return None
    rest = first[len(prefix):].strip()
    return rest or None


def _front_matter(fields: dict) -> str:
    body = yaml.safe_dump(fields, sort_keys=False, allow_unicode=True, width=10**6)
    return f"---\n{body}---\n\n"


def _plugin_of_agent_type(functions) -> dict[str, str]:
    """agents/<folder>/functions/*.md -> plugin name from each function's prefix."""
    return {f.path.parent.parent.name: f.prefix.split(":")[0] for f in functions}


def _plan(repo_root: Path, skills, agents, modules, functions, instructions):
    """Where every shipped source lands: {resolved source: _Shipped}."""
    plugins = _plugin_of_agent_type(functions)
    rules = [i for i in instructions if i.slug == RULES_SLUG]
    shipped: dict[Path, _Shipped] = {}
    for s in skills:
        name = skill_name(s.slug)
        shipped[s.path.resolve()] = _Shipped(SKILLS_PLUGIN, PurePosixPath(f"skills/{name}/SKILL.md"), "skill", name)
    for f in functions:
        plugin = f.prefix.split(":")[0]
        shipped[f.path.resolve()] = _Shipped(plugin, PurePosixPath(f"skills/{f.slug}/SKILL.md"), "function", f.slug)
    for a in agents:
        plugin = plugins.get(re.sub(r"_agent$", "", a.slug))
        if plugin:
            shipped[a.path.resolve()] = _Shipped(plugin, PurePosixPath("reference/agent.md"), "agent", a.slug)
    for m in modules:
        plugin = plugins.get(m.agent_type)
        if plugin:
            shipped[m.path.resolve()] = _Shipped(plugin, PurePosixPath(f"reference/modules/{m.slug}.md"), "module", m.slug)
    return plugins, rules, shipped


def _rewrite(text: str, source: Path, here: _Shipped, shipped: dict[Path, _Shipped], repo_root: Path,
             roles: frozenset[str] = frozenset()) -> str:
    root = repo_root.resolve()

    def repoint(match: re.Match[str]) -> str:
        label, target, anchor = match.group("label"), match.group("target"), match.group("anchor") or ""
        if "://" in target or target.startswith(("/", "mailto:")):
            return match.group(0)
        resolved = (source.parent / target).resolve()
        dest = shipped.get(resolved)
        if dest and dest.kind == "rules" and here.plugin in roles:    # every role plugin ships rules.md
            dest = _Shipped(here.plugin, PurePosixPath("reference/rules.md"), "rules", RULES_SLUG)
        if dest and dest.plugin == here.plugin:
            return f"[{label}]({posixpath.relpath(dest.rel, here.rel.parent)}{anchor})"
        if dest and dest.kind == "skill":
            return f"{label} (`{dest.plugin}:{dest.name}` skill)"
        if dest and dest.kind == "function":
            return f"{label} (`/{dest.plugin}:{dest.name}`)"
        if resolved.exists() and resolved.is_relative_to(root):
            return f"[{label}]({BLOB_URL}{resolved.relative_to(root).as_posix()}{anchor})"
        return match.group(0)

    return _LINK.sub(repoint, text)


def build_plugins(repo_root: Path, skills, agents, modules, functions, instructions, version: str) -> dict[str, str]:
    """All plugin and marketplace files, keyed by path relative to repo_root."""
    plugins, rules, shipped = _plan(repo_root, skills, agents, modules, functions, instructions)
    role_plugins = sorted(set(plugins.values()))
    files: dict[str, str] = {}

    def put(here: _Shipped, text: str) -> None:
        files[f"{PLUGIN_ROOT}/{here.plugin}/{here.rel}"] = text

    roles = frozenset(role_plugins)
    for rule in rules if role_plugins else []:   # one entry is enough: _rewrite re-points it into each role plugin
        shipped[rule.path.resolve()] = _Shipped(role_plugins[0], PurePosixPath("reference/rules.md"), "rules", RULES_SLUG)
    for source_list in (skills, functions, agents, modules):
        for item in source_list:
            here = shipped.get(item.path.resolve())
            if not here:
                continue
            body = _rewrite(item.content.strip() + "\n", item.path, here, shipped, repo_root, roles)
            if here.kind == "skill":
                put(here, _front_matter({"name": here.name, "description": use_when(item.content, item.description)}) + body)
            elif here.kind == "function":
                fields = {"name": item.slug, "description": " ".join(item.description.split()) or item.name}
                hint = argument_hint(item.content, item.prefix)
                if hint:
                    fields["argument-hint"] = hint
                fields["disable-model-invocation"] = True
                pointer = ("Role and rules: read ${CLAUDE_PLUGIN_ROOT}/reference/agent.md"
                           + (" and ${CLAUDE_PLUGIN_ROOT}/reference/rules.md" if rules else "")
                           + " for the sections this function needs.\n\n")
                put(here, _front_matter(fields) + pointer + body)
            else:
                put(here, body)
    for rule in rules:
        for plugin in role_plugins:
            here = _Shipped(plugin, PurePosixPath("reference/rules.md"), "rules", RULES_SLUG)
            put(here, _rewrite(rule.content.strip() + "\n", rule.path, here, shipped, repo_root, roles))

    descriptions = {SKILLS_PLUGIN: "Reference skills — language, framework, data, and process standards Claude loads when relevant"}
    for a in agents:
        plugin = plugins.get(re.sub(r"_agent$", "", a.slug))
        if plugin:
            descriptions[plugin] = first_sentence(a.description)
    all_plugins = role_plugins + ([SKILLS_PLUGIN] if skills else [])
    for plugin in all_plugins:
        manifest = {"name": plugin, "version": version, "description": descriptions.get(plugin, plugin),
                    "author": {"name": OWNER}, "repository": REPO_URL, "license": "MIT"}
        files[f"{PLUGIN_ROOT}/{plugin}/.claude-plugin/plugin.json"] = json.dumps(manifest, indent=2) + "\n"
    market = {"name": MARKETPLACE_NAME, "owner": {"name": OWNER},
              "description": "Spec-driven engineering for Claude Code: role plugins with /agent:function commands, and reference skills",
              "plugins": [{"name": p, "source": f"./{PLUGIN_ROOT}/{p}", "description": descriptions.get(p, p)}
                          for p in all_plugins]}
    files[MARKETPLACE] = json.dumps(market, indent=2) + "\n"
    return dict(sorted(files.items()))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m pytest tests/tools/test_claude_plugins.py -q`
Expected: PASS (10 tests). If `test_links_are_rewritten_for_the_plugin_layout` fails on a `rules` link, check that the rules entry is added to `shipped` before any file is rewritten, and that `roles` is passed to every `_rewrite` call.

- [ ] **Step 5: Commit**

```bash
git add tools/claude_plugins.py tests/tools/test_claude_plugins.py
git commit -m "feat(exporter): pure builder for Claude Code plugins and marketplace (#53)"
```

---

### Task 3: ClaudeExporter writes the plugins

**Files:**
- Modify: `tools/exporter.py` — `ClaudeExporter` (class at ~line 1055), `ExportOrchestrator._CLEAN_DIRS`, `ExportOrchestrator.run` (~line 1767), `copy_to_target_project` (`platform_dirs["claude"]`, ~line 1990)
- Modify: `tests/tools/test_exporter.py` — tests that used `ClaudeExporter` as a stand-in for the base class
- Test: `tests/tools/test_claude_exporter.py`

**Interfaces:**
- Consumes: `build_plugins`, `PLUGIN_ROOT`, `MARKETPLACE` from Task 2.
- Produces: `ClaudeExporter.plan_files(skills, agents, modules, functions, instructions) -> dict[str, str]` (Task 4 uses it for the freshness test); `ClaudeExporter.export(...) -> ExportResult` with `skill_files` = reference-skill paths, `function_files` = function `SKILL.md` paths, `agent_files` = `reference/agent.md` paths, `removed_files` = pruned paths.

- [ ] **Step 1: Write the failing tests**

```python
# tests/tools/test_claude_exporter.py
"""ClaudeExporter writes Claude Code plugins (#53)."""
from pathlib import Path

from tools.exporter import ClaudeExporter, ExportOrchestrator, FunctionFile, SkillFile

SKILL = "---\nname: A\nversion: 1\ndescription: Does a. More.\napplies_to: [x]\ntags: [x]\n---\n\n# A\n"
FUNC = "---\nname: architect:adr Function\nversion: 1\ndescription: Mint an ADR\nprefix: architect:adr\n---\n\n# adr\n"


def _write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _sources(root: Path):
    _write(root, "pyproject.toml", '[project]\nname = "x"\nversion = "1.2.3"\n')
    skills = [SkillFile.from_path(_write(root, "skills/a_skill.md", SKILL))]
    functions = [FunctionFile.from_path(_write(root, "agents/architect/functions/adr.md", FUNC))]
    return skills, functions


def test_export_writes_plugins_and_marketplace(tmp_path):
    skills, functions = _sources(tmp_path)
    result = ClaudeExporter(tmp_path).export(skills=skills, agents=[], modules=[], functions=functions,
                                             instructions=[], hooks=[])
    assert (tmp_path / "plugins/architect/skills/adr/SKILL.md").exists()
    assert (tmp_path / "plugins/engineering-skills/skills/a/SKILL.md").exists()
    assert (tmp_path / ".claude-plugin/marketplace.json").exists()
    assert '"version": "1.2.3"' in (tmp_path / "plugins/architect/.claude-plugin/plugin.json").read_text()
    assert [p.name for p in result.function_files] == ["SKILL.md"]
    assert not (tmp_path / ".claude/skills").exists()


def test_dry_run_writes_nothing(tmp_path):
    skills, functions = _sources(tmp_path)
    ClaudeExporter(tmp_path).export(skills=skills, agents=[], modules=[], functions=functions,
                                    instructions=[], hooks=[], dry_run=True)
    assert not (tmp_path / "plugins").exists()


def test_export_prunes_stale_plugin_files(tmp_path):
    skills, functions = _sources(tmp_path)
    stale = _write(tmp_path, "plugins/engineering-skills/skills/old/SKILL.md", "old")
    result = ClaudeExporter(tmp_path).export(skills=skills, agents=[], modules=[], functions=functions,
                                             instructions=[], hooks=[])
    assert not stale.exists() and not stale.parent.exists()
    assert stale in result.removed_files


def test_export_prunes_only_inside_plugins(tmp_path):
    skills, functions = _sources(tmp_path)
    keep = _write(tmp_path, "docs/keep.md", "keep")
    ClaudeExporter(tmp_path).export(skills=skills, agents=[], modules=[], functions=functions,
                                    instructions=[], hooks=[])
    assert keep.exists()


def test_claude_target_ignores_filters(tmp_path):
    _sources(tmp_path)
    _write(tmp_path, "skills/b_skill.md", SKILL.replace("name: A", "name: B"))
    (tmp_path / "instructions").mkdir()
    orchestrator = ExportOrchestrator(tmp_path)
    orchestrator.run(targets=["claude"], skill_filter=["a_skill"], agent_filter=[])
    assert (tmp_path / "plugins/engineering-skills/skills/b/SKILL.md").exists()


def test_target_project_claude_points_to_marketplace(tmp_path, capsys):
    from tools.exporter import copy_to_target_project
    copy_to_target_project([], [], [], [], [], [], tmp_path / "app", ["claude"])
    assert not (tmp_path / "app/.claude/skills").exists()
    assert "/plugin marketplace add sharmapuneet1510/awesome-prompts" in capsys.readouterr().out
```

`copy_to_target_project(skills, agents, modules, functions, instructions, hooks, target_project, platforms, prompts=None)` is the existing function at ~line 1958.

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest tests/tools/test_claude_exporter.py -q`
Expected: FAIL — the export still writes `.claude/skills/...` and has no `plugins/`.

- [ ] **Step 3: Replace `ClaudeExporter`**

Replace the whole `class ClaudeExporter(PlatformExporter):` body in `tools/exporter.py` with:

```python
class ClaudeExporter(PlatformExporter):
    """Claude Code — a marketplace of plugins under plugins/ (see tools/claude_plugins.py).

    Always exports the full set: plugins are installed whole, so a filtered run
    would otherwise delete the plugins it did not list.
    """

    @property
    def target_name(self) -> str:
        return "claude"

    def skill_output_dir(self) -> Path:
        return self._repo_root / "plugins" / "engineering-skills" / "skills"

    def agent_output_dir(self) -> Path:
        return self._repo_root / "plugins"

    def hook_output_dir(self) -> Path:
        return self._repo_root / ".claude" / "hooks"

    def format_skill(self, skill: SkillFile) -> str:
        return skill.content

    def format_agent(self, agent: AgentFile) -> str:
        return agent.content

    def _version(self) -> str:
        import tomllib
        pyproject = self._repo_root / "pyproject.toml"
        if not pyproject.exists():
            return "0.0.0"
        return tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"]

    def plan_files(self, skills, agents, modules, functions, instructions) -> dict[str, str]:
        """Every plugin and marketplace file, keyed by path relative to the repo root."""
        try:
            from tools.claude_plugins import build_plugins
        except ImportError:                       # run as a script: python3 tools/exporter.py
            from claude_plugins import build_plugins
        return build_plugins(self._repo_root, skills, agents, modules, functions, instructions, self._version())

    def export(self, skills, agents, modules, functions, instructions, hooks,
               dry_run: bool = False, prompts=None) -> ExportResult:
        files = self.plan_files(skills, agents, modules, functions, instructions)
        paths = {self._repo_root / rel: text for rel, text in files.items()}
        plugins_dir = self._repo_root / "plugins"
        stale = [p for p in plugins_dir.rglob("*") if p.is_file() and p not in paths] if plugins_dir.exists() else []
        if not dry_run:
            for path, text in paths.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            for path in stale:
                path.unlink()
            for folder in sorted((d for d in plugins_dir.rglob("*") if d.is_dir()), reverse=True):
                if not any(folder.iterdir()):
                    folder.rmdir()
        written = list(paths)
        return ExportResult(
            target=self.target_name,
            skill_files=[p for p in written if "/engineering-skills/skills/" in p.as_posix()],
            agent_files=[p for p in written if p.as_posix().endswith("/reference/agent.md")],
            module_files=[p for p in written if "/reference/modules/" in p.as_posix()],
            function_files=[p for p in written if p.name == "SKILL.md" and "/engineering-skills/" not in p.as_posix()],
            instruction_files=[p for p in written if p.as_posix().endswith("/reference/rules.md")],
            hook_files=self.export_hooks(hooks, dry_run=dry_run),
            removed_files=stale,
            dry_run=dry_run,
        )
```

- [ ] **Step 4: Make `run()` pass the full lists to the Claude target**

In `ExportOrchestrator.run`, inside `for cls in exporter_classes:`, replace the `result = exporter.export(...)` call with:

```python
                if cls is ClaudeExporter:
                    result = exporter.export(all_skills, all_agents, all_modules, all_functions,
                                             all_instructions, hooks, dry_run=dry_run, prompts=prompts)
                else:
                    result = exporter.export(skills, agents, modules, functions, instructions, hooks,
                                             dry_run=dry_run, prompts=prompts)
```

- [ ] **Step 5: `--clean` and `--target-project`**

In `_CLEAN_DIRS`, replace `".claude/skills"`, `".claude/agents"` and `".claude/prompts"` with `"plugins"` and `".claude-plugin"`.

In `copy_to_target_project`, before the loop that copies per platform, add:

```python
    if "claude" in platforms:
        print("  Claude Code: plugins are installed from the marketplace, not copied.\n"
              "    /plugin marketplace add sharmapuneet1510/awesome-prompts\n"
              "    /plugin install architect@awesome-prompts   (also: orchestrator, implementer,"
              " quality, ba, engineering-skills)")
        platforms = [p for p in platforms if p != "claude"]
```

and delete the `"claude": (...)` entry from `platform_dirs`.

- [ ] **Step 6: Move the base-class tests off `ClaudeExporter`**

In `tests/tools/test_exporter.py`:
- In `test_platform_exporter_export_writes_skill_file`, `..._writes_agent_file`, `..._dry_run_does_not_write`, `..._returns_correct_file_paths`, `test_export_leaves_absolute_urls_untouched` and `test_cleanup_never_deletes_outside_the_repo`, replace `ClaudeExporter` with `WindsurfExporter`, and change expected paths from `.claude/skills/<f>` to `.windsurf/rules/<f>` and from `.claude/agents/<f>` to `.windsurf/rules/agents/<f>`.
- Remove `"ClaudeExporter"` from the parametrize list of `test_export_rewrites_links_to_exported_copies` (plugins have their own link rules, tested in Task 2).
- Delete the `# ── ClaudeExporter ──` block (`test_claude_skill_output_dir` through `test_claude_exporter_hook_output_dir`) and add in its place:

```python
def test_claude_exporter_hook_output_dir(tmp_path):
    from tools.exporter import ClaudeExporter
    assert ClaudeExporter(repo_root=tmp_path).hook_output_dir() == tmp_path / ".claude" / "hooks"
```

- [ ] **Step 7: Run the tests**

Run: `python3 -m pytest -q`
Expected: PASS — the 6 new tests in `tests/tools/test_claude_exporter.py` and every existing test.

- [ ] **Step 8: Commit**

```bash
git add tools/exporter.py tests/tools/test_exporter.py tests/tools/test_claude_exporter.py
git commit -m "feat(exporter): claude target writes a plugin marketplace (#53)"
```

---

### Task 4: Generate the plugins and prove they load

**Files:**
- Create: `plugins/**`, `.claude-plugin/marketplace.json` (generated)
- Create: `tests/test_plugins_repo.py`
- Modify: `.github/workflows/ci.yml` (new `plugin-validation` job; add it to `status-check.needs`)

**Interfaces:**
- Consumes: `ClaudeExporter.plan_files` (Task 3), `ExportOrchestrator.discover_*` (existing).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_plugins_repo.py
"""The committed Claude Code plugins are complete, valid and fresh (#53)."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from tools.exporter import ClaudeExporter, ExportOrchestrator

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
ROLES = ["architect", "ba", "implementer", "orchestrator", "quality"]
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _front(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), path
    return yaml.safe_load(text.split("---", 2)[1])


def _skills(plugin: str) -> list[Path]:
    return sorted((PLUGINS / plugin / "skills").glob("*/SKILL.md"))


def test_committed_plugins_are_fresh():
    orch = ExportOrchestrator(ROOT)
    agents = orch.discover_agents()
    expected = ClaudeExporter(ROOT).plan_files(orch.discover_skills(), agents, orch.discover_modules(),
                                               orch.discover_functions(), orch.discover_referenced_instructions(agents))
    on_disk = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8")
               for p in list(PLUGINS.rglob("*")) + [ROOT / ".claude-plugin/marketplace.json"] if p.is_file()}
    assert sorted(on_disk) == sorted(expected), "run: python3 tools/exporter.py --target claude"
    stale = [rel for rel, text in expected.items() if on_disk[rel] != text]
    assert stale == [], "run: python3 tools/exporter.py --target claude"


def test_every_skill_has_valid_front_matter():
    for plugin in ROLES + ["engineering-skills"]:
        names = []
        for path in _skills(plugin):
            fm = _front(path)
            assert NAME.match(fm["name"]) and len(fm["name"]) <= 64, path
            assert fm["name"] == path.parent.name, path
            assert fm.get("description"), path
            assert len(fm["description"]) + len(fm.get("when_to_use", "")) <= 1536, path
            names.append(fm["name"])
        assert len(names) == len(set(names)), plugin


def test_counts_and_invocation():
    functions = [p for plugin in ROLES for p in _skills(plugin)]
    assert len(functions) == 43
    assert all(_front(p)["disable-model-invocation"] is True for p in functions)
    assert len(_skills("engineering-skills")) == len(list((ROOT / "skills").glob("*_skill.md")))


def test_manifests_match_directories():
    market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    assert market["name"] == "awesome-prompts"
    for entry in market["plugins"]:
        folder = ROOT / entry["source"]
        manifest = json.loads((folder / ".claude-plugin/plugin.json").read_text())
        assert manifest["name"] == entry["name"] == folder.name


def test_no_broken_relative_links_in_plugins():
    broken = []
    for path in PLUGINS.rglob("*.md"):
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", path.read_text(encoding="utf-8")):
            if "://" not in target and not target.startswith("mailto:") and not (path.parent / target).exists():
                broken.append(f"{path.relative_to(ROOT)} -> {target}")
    assert broken == []


@pytest.mark.skipif(shutil.which("claude") is None, reason="Claude Code CLI not installed")
@pytest.mark.parametrize("target", ["."] + [f"plugins/{p}" for p in ROLES + ["engineering-skills"]])
def test_claude_plugin_validate_strict(target):
    result = subprocess.run(["claude", "plugin", "validate", "--strict", target], cwd=ROOT,
                            capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest tests/test_plugins_repo.py -q`
Expected: FAIL — `plugins/` does not exist yet.

- [ ] **Step 3: Generate**

Run: `python3 tools/exporter.py --target claude`
Expected: a line `[claude    ] Wrote 44 skill(s), 5 agent(s), 3 module(s), 43 function(s), 5 instruction(s), ...`.

- [ ] **Step 4: Run the tests and the validator**

Run: `python3 -m pytest tests/test_plugins_repo.py -q`
Expected: PASS, including the 7 `claude plugin validate --strict` cases (the CLI is installed locally).

If a validate case fails, read its message against the spec's layout, fix `tools/claude_plugins.py` (not the generated file), regenerate, and re-run. Warnings count as failures under `--strict`; a warning about a missing field in `plugin.json` is fixed in `build_plugins`.

- [ ] **Step 5: Record the acceptance evidence**

Run: `claude plugin details ./plugins/architect` and `claude plugin details ./plugins/engineering-skills`
Expected: the architect inventory lists 9 skills (`adr`, `analyse`, …); engineering-skills lists 44. Save both outputs for the PR description.

- [ ] **Step 6: Add the CI job**

In `.github/workflows/ci.yml`, add this job and append `plugin-validation` to the `needs:` list of `status-check` and to its failure condition:

```yaml
  plugin-validation:
    name: Claude Code Plugin Validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22.x'
      - name: Install Claude Code CLI
        run: npm install -g @anthropic-ai/claude-code
      - name: Validate marketplace and plugins
        run: |
          claude plugin validate --strict .
          for p in plugins/*/; do claude plugin validate --strict "$p"; done
```

and in `status-check`'s script add `|| [[ "${{ needs.plugin-validation.result }}" == "failure" ]]`.

- [ ] **Step 7: Commit and check CI**

```bash
git add plugins .claude-plugin tests/test_plugins_repo.py .github/workflows/ci.yml
git commit -m "feat(plugins): generate the awesome-prompts marketplace and six plugins (#53)"
git push -u origin feat/53-claude-plugins
gh run watch "$(gh run list --branch feat/53-claude-plugins --limit 1 --json databaseId -q '.[0].databaseId')" --exit-status
```

Expected: all jobs green. If only `plugin-validation` fails because the CLI needs authentication, remove that job, keep the pytest-level check (it skips without the CLI), and say so in the PR — as the spec allows.

---

### Task 5: Retire the dead `.claude/` exports, dogfood the marketplace, update docs

**Files:**
- Delete: `.claude/skills/`, `.claude/agents/`, `.claude/prompts/`, `.claude/.claude-export-manifest.json`
- Modify: `.claude/settings.json`, `README.md` (Quick start step 3), `docs/01-workflows/14-export-to-platforms.md`, `docs/00-getting-started/quick-start.md`, `CLAUDE.md` (Generated line), `CHANGELOG.md` ([Unreleased])
- Test: `tests/test_claude_md.py` (existing, must stay green), `tests/test_plugins_repo.py`

- [ ] **Step 1: Delete the dead exports**

```bash
git rm -r -q .claude/skills .claude/agents .claude/prompts .claude/.claude-export-manifest.json
```

- [ ] **Step 2: Register the repo's own marketplace**

Set `.claude/settings.json` to:

```json
{
  "hooks": {},
  "extraKnownMarketplaces": {
    "awesome-prompts": {
      "source": { "source": "directory", "path": "." }
    }
  }
}
```

Verify it resolves: run `claude plugin marketplace list` from the repo root.
Expected: `awesome-prompts` listed with the repo path. If it isn't listed or errors on the relative path, try `"path": "./"`; if neither works, restore `{"hooks": {}}` and use the fallback in Step 3's docs text (`claude plugin marketplace add ./`), noting it in the PR.

- [ ] **Step 3: README Quick start step 3**

Replace the step-3 block (from `**3. Install it into your project**` to the `<sub>Targets…</sub>` line) with:

````markdown
**3. Install it into your project** — pick your assistant

Claude Code — in any project, run:

```text
/plugin marketplace add sharmapuneet1510/awesome-prompts
/plugin install architect@awesome-prompts
```

Install the others the same way: `orchestrator`, `implementer`, `quality`, `ba`, and
`engineering-skills` (the 44 reference skills). Commands then appear as `/architect:adr`,
`/quality:review`, and so on.

Other assistants:

```bash
python3 tools/exporter.py --target cursor --target-project ~/code/my-app
```

<sub>Targets: `copilot` · `cursor` · `windsurf` · `gemini` · `continue` · `openai` · `aider` · `all`. `--dry-run` previews an in-repo export; it has no effect together with `--target-project`.</sub>
````

- [ ] **Step 4: `docs/01-workflows/14-export-to-platforms.md`**

Under `## Platforms`, add:

```markdown
**Claude Code** is different: `--target claude` writes a plugin marketplace
(`.claude-plugin/marketplace.json` and `plugins/`), which users install with
`/plugin marketplace add sharmapuneet1510/awesome-prompts`. The other seven
targets write instruction files.
```

In `## Artifacts`, replace `` `.claude/`, `` with `` `plugins/` and `.claude-plugin/` (Claude Code), `.claude/hooks/`, ``.

- [ ] **Step 5: `CLAUDE.md` Generated line**

Replace these three lines:

```markdown
**Generated — do not edit by hand:** `.claude/` (committed) and `.cursor/`,
`.windsurf/`, `.gemini/`, `.continue/`, `.github/instructions/` (gitignored).
Edit the sources, then re-run the exporter.
```

with:

```markdown
**Generated — do not edit by hand:** `plugins/` and `.claude-plugin/` (committed;
`tests/test_plugins_repo.py` fails when they are stale), `.claude/hooks/`, and
`.cursor/`, `.windsurf/`, `.gemini/`, `.continue/`, `.github/instructions/` (gitignored).
Edit the sources, then re-run the exporter.
```

Then run `python3 -m pytest tests/test_claude_md.py -q` — Expected: PASS (paths exist; file stays under 6,000 characters).

- [ ] **Step 5b: `docs/00-getting-started/quick-start.md`**

It describes the old output in four places. Change them to:
- line ~33: `- Updates \`.github/instructions/\`, \`.github/agents/\`, \`plugins/\` (Claude Code), etc.`
- line ~52: `**Output:** \`plugins/\` and \`.claude-plugin/marketplace.json\` — a plugin marketplace.` and replace the next line with `Install it in Claude Code with \`/plugin marketplace add sharmapuneet1510/awesome-prompts\`, then \`/plugin install <plugin>@awesome-prompts\`.`
- lines ~129–132: replace the three numbered steps with `Install the plugins (see above). Commands such as \`/architect:adr\` then appear in the \`/\` menu, and Claude loads the reference skills when relevant.`
- line ~212: `**Claude Code:** run \`/plugin\` and check the awesome-prompts plugins are installed and enabled.`

Then run `grep -rn "\.claude/skills\|\.claude/agents" README.md docs --include=*.md | grep -v "superpowers\|99-archive"` — Expected: no output.

- [ ] **Step 6: CHANGELOG**

Under `## [Unreleased]` → `### Added`, add:

```markdown
- **Claude Code plugins** (#53): `--target claude` now writes a marketplace of six plugins —
  `orchestrator`, `architect`, `implementer`, `quality`, `ba` (all 43 functions as
  `/agent:function` commands, user-invoked only) and `engineering-skills` (44 skills Claude loads
  when relevant). Install: `/plugin marketplace add sharmapuneet1510/awesome-prompts`. The old
  flat `.claude/skills` and `.claude/agents` exports, which Claude Code never loaded, are removed.
```

- [ ] **Step 7: Run everything**

Run: `python3 -m pytest -q && python3 tools/skill_validator.py && python3 tools/exporter.py --dry-run`
Expected: all pass; the dry run reports 8 targets with no `FAILED`.

- [ ] **Step 8: Commit and open the PR**

```bash
git add -A .claude README.md docs/01-workflows/14-export-to-platforms.md docs/00-getting-started/quick-start.md CLAUDE.md CHANGELOG.md
git commit -m "chore(claude): remove unloadable flat exports; install via the plugin marketplace (#53)"
git push
```

Open the PR with `Closes #53 · Part of #68`, the `claude plugin details` output from Task 4 Step 5, the CI run link, and one unchecked item for the user: *after `/plugin install architect@awesome-prompts`, `/architect:adr` appears in the `/` menu.*
