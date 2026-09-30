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


def _gitignored(rels: list[str]) -> set[str]:
    """Which of these repo-relative paths git ignores (empty outside a git checkout)."""
    if not rels or shutil.which("git") is None or not (ROOT / ".git").exists():
        return set()
    out = subprocess.run(["git", "check-ignore", "--no-index", "--stdin"], cwd=ROOT, input="\n".join(rels),
                         capture_output=True, text=True).stdout
    return set(out.split())


def _expected() -> dict[str, str]:
    orch = ExportOrchestrator(ROOT)
    agents = orch.discover_agents()
    return ClaudeExporter(ROOT).plan_files(orch.discover_skills(), agents, orch.discover_modules(),
                                           orch.discover_functions(), orch.discover_referenced_instructions(agents))


def _skills(plugin: str) -> list[Path]:
    return sorted((PLUGINS / plugin / "skills").glob("*/SKILL.md"))


def test_committed_plugins_are_fresh():
    expected = _expected()
    # Files git ignores (e.g. a Finder .DS_Store) are never committed, so they don't count as stale.
    owned = {rel.split("/")[1] for rel in expected
             if rel.startswith("plugins/") and not rel.endswith("/.claude-plugin/plugin.json")}
    paths = [p for p in PLUGINS.rglob("*") if p.is_file() and p.relative_to(PLUGINS).parts[0] in owned
             and p.relative_to(PLUGINS).parts[1:2] != ("evals",)]
    paths += [ROOT / rel for rel in expected if (ROOT / rel).is_file() and ROOT / rel not in paths]
    rels = [p.relative_to(ROOT).as_posix() for p in paths]
    ignored = _gitignored(rels)
    on_disk = {rel: p.read_text(encoding="utf-8") for rel, p in zip(rels, paths) if rel not in ignored}
    assert sorted(on_disk) == sorted(expected), "run: python3 tools/exporter.py --target claude"
    stale = [rel for rel, text in expected.items() if on_disk[rel] != text]
    assert stale == [], "run: python3 tools/exporter.py --target claude"


def test_every_skill_has_valid_front_matter():
    for plugin in ROLES + ["engineering-skills"]:
        names = []
        assert _skills(plugin), f"no skills in plugins/{plugin}"
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
    pages = list(PLUGINS.rglob("*.md"))
    assert pages, "no plugin pages to check"
    for path in pages:
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", path.read_text(encoding="utf-8")):
            if "://" not in target and not target.startswith("mailto:") and not (path.parent / target).exists():
                broken.append(f"{path.relative_to(ROOT)} -> {target}")
    assert broken == []


@pytest.mark.skipif(shutil.which("claude") is None, reason="Claude Code CLI not installed")
@pytest.mark.parametrize("target", [".claude-plugin/marketplace.json"] + [f"plugins/{p}" for p in ROLES + ["engineering-skills", "spec-gate"]])
def test_claude_plugin_validate_strict(target):
    result = subprocess.run(["claude", "plugin", "validate", "--strict", target], cwd=ROOT,
                            capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr


def test_no_generated_plugin_file_is_gitignored():
    # A generated file that .gitignore hides is on disk locally but missing from every clone.
    if shutil.which("git") is None or not (ROOT / ".git").exists():
        pytest.skip("not a git checkout")
    assert sorted(_gitignored(list(_expected()))) == []
