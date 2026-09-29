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
