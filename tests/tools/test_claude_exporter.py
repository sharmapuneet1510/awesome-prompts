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
    assert '"version": "1.2.3+' in (tmp_path / "plugins/architect/.claude-plugin/plugin.json").read_text()
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
