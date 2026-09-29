"""The exporter's own docs and first-time flow describe what it actually does for Claude Code (#53)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STALE = [".claude/skills", ".claude/agents", ".claude/prompts", "autonomous-developer",
         "AUTONOMOUS_DEVELOPER_README"]
MARKETPLACE = "/plugin marketplace add sharmapuneet1510/awesome-prompts"


def test_exporter_docstring_and_tools_readme_describe_plugins():
    for path in ["tools/exporter.py", "tools/README.md"]:
        text = (ROOT / path).read_text(encoding="utf-8")
        assert [s for s in STALE if s in text] == [], path
    assert "plugins/" in (ROOT / "tools/exporter.py").read_text(encoding="utf-8")
    assert MARKETPLACE in (ROOT / "tools/README.md").read_text(encoding="utf-8")


def test_interactive_next_steps_point_at_the_marketplace(capsys):
    sys.path.insert(0, str(ROOT / "tools"))
    import interactive_exporter as ie
    ie.print_next_steps(Path("/tmp/app"))
    out = capsys.readouterr().out
    assert MARKETPLACE in out
    assert [s for s in STALE if s in out] == []
    source = (ROOT / "tools/interactive_exporter.py").read_text(encoding="utf-8")
    claude_option = next(line for line in source.splitlines() if line.strip().startswith('("claude",'))
    assert ".claude/" not in claude_option and "marketplace" in claude_option
