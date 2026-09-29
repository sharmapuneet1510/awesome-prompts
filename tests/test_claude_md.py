"""CLAUDE.md is loaded into every Claude Code session in this repo, so every path and
command in it must be real, and it must stay small (#61)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
PATHISH = re.compile(r"`([\w.\-]+/[\w.\-/*]*|[\w\-]+\.(?:md|py|json|toml|yml|yaml|sh|mjs|ts))`")


IGNORED = {line.strip() for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()}


def test_every_backticked_path_exists():
    # Generated, gitignored folders are absent from a fresh clone but must be listed in .gitignore.
    missing = [p for p in PATHISH.findall(TEXT) if not list(ROOT.glob(p.rstrip("/"))) and p not in IGNORED]
    assert missing == []


def test_every_relative_link_exists():
    links = re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", TEXT)
    missing = [link for link in links if "://" not in link and not (ROOT / link).exists()]
    assert missing == []


def test_every_script_in_a_command_exists():
    blocks = "\n".join(re.findall(r"```[\w-]*\n(.*?)```", TEXT, re.S))
    scripts = re.findall(r"(?:python3?|node)\s+(?:-m\s+)?([\w./\-]+\.(?:py|mjs))", blocks)
    assert scripts, "expected commands that run scripts"
    assert [s for s in scripts if not (ROOT / s).exists()] == []


def test_no_removed_agents():
    removed = ["implementation_agent", "test_case_generator_agent", "autonomous_dev_agent",
               "developer_agent", "parser/orcastrator.py"]
    assert [name for name in removed if name in TEXT] == []


def test_stays_small():
    # ~1.5k tokens at ~4 characters per token
    assert len(TEXT) < 6000, f"CLAUDE.md is {len(TEXT)} characters"
