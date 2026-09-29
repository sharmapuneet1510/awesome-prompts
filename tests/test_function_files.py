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
