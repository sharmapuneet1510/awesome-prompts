"""Tests for tools/exporter.py"""
from pathlib import Path
import pytest


# ── Helpers ──────────────────────────────────────────────────────────────────

def write_skill(tmp_path: Path, filename: str, content: str) -> Path:
    p = tmp_path / filename
    p.write_text(content, encoding="utf-8")
    return p


def write_agent(tmp_path: Path, role: str, filename: str, content: str) -> Path:
    d = tmp_path / role
    d.mkdir(parents=True, exist_ok=True)
    p = d / filename
    p.write_text(content, encoding="utf-8")
    return p


# ── Test fixtures ─────────────────────────────────────────────────────────────

SKILL_MD = """\
---
name: Java Advanced Coding Skill
version: 2.0
description: >
  A reusable skill for Java coding.
applies_to: [java, spring-boot, maven]
tags: [java, spring, patterns]
---

# Java Advanced Skill

Some content here.
"""

SKILL_INLINE_LIST = """\
---
name: Test Skill
version: 1.0
description: Short description
applies_to:
  - python
  - fastapi
tags:
  - python
  - api
---

Body content.
"""

SKILL_NO_FRONTMATTER = "# Just a heading\n\nNo frontmatter here."


# ── SkillFile tests ───────────────────────────────────────────────────────────

def test_skill_file_parses_name(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    skill = SkillFile.from_path(path)
    assert skill.name == "Java Advanced Coding Skill"


def test_skill_file_parses_version(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    skill = SkillFile.from_path(path)
    assert skill.version == "2.0"


def test_skill_file_parses_block_scalar_description(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    skill = SkillFile.from_path(path)
    assert "reusable skill for Java" in skill.description


def test_skill_file_parses_inline_applies_to(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    skill = SkillFile.from_path(path)
    assert skill.applies_to == ["java", "spring-boot", "maven"]


def test_skill_file_parses_block_list_applies_to(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "test_skill.md", SKILL_INLINE_LIST)
    skill = SkillFile.from_path(path)
    assert skill.applies_to == ["python", "fastapi"]


def test_skill_file_parses_inline_tags(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    skill = SkillFile.from_path(path)
    assert "java" in skill.tags


def test_skill_file_slug_is_stem(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    skill = SkillFile.from_path(path)
    assert skill.slug == "java_advanced_skill"


def test_skill_file_content_strips_frontmatter(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    skill = SkillFile.from_path(path)
    assert "# Java Advanced Skill" in skill.content
    assert "applies_to:" not in skill.content


def test_skill_file_raises_on_missing_frontmatter(tmp_path):
    from tools.exporter import SkillFile
    path = write_skill(tmp_path, "bad.md", SKILL_NO_FRONTMATTER)
    with pytest.raises(ValueError, match="missing YAML frontmatter"):
        SkillFile.from_path(path)


# ── AgentFile parsing ─────────────────────────────────────────────────────────

AGENT_MD = """\
---
name: Java Senior Engineering Agent
version: 2.0
description: >
  Advanced Java coding agent for Spring Boot projects.
skills: [java_advanced_skill]
instruction_set: instructions/master_instruction_set.md
intake_form: instructions/java_project_intake.md
---

# Java Senior Engineering Agent

You are Jarvis.
"""

AGENT_MULTI_SKILLS = """\
---
name: Code Health Inspector Agent
version: 1.0
description: Step-by-step code scanning agent.
skills:
  - code_health_skill
  - java_advanced_skill
instruction_set: instructions/master_instruction_set.md
intake_form: instructions/java_project_intake.md
---

Inspector body.
"""


def test_agent_file_parses_name(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "java_advanced_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert agent.name == "Java Senior Engineering Agent"


def test_agent_file_parses_version(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "java_advanced_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert agent.version == "2.0"


def test_agent_file_parses_block_scalar_description(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "java_advanced_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert "Spring Boot" in agent.description


def test_agent_file_parses_inline_skills(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "java_advanced_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert agent.skills == ["java_advanced_skill"]


def test_agent_file_parses_block_list_skills(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "reviewer", "code_health_inspector_agent.md", AGENT_MULTI_SKILLS)
    agent = AgentFile.from_path(path)
    assert agent.skills == ["code_health_skill", "java_advanced_skill"]


def test_agent_file_parses_instruction_set(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "java_advanced_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert agent.instruction_set == "instructions/master_instruction_set.md"


def test_agent_file_role_derived_from_parent_dir(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "reviewer", "code_review_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert agent.role == "reviewer"


def test_agent_file_slug_is_stem(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "java_advanced_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert agent.slug == "java_advanced_agent"


def test_agent_file_content_strips_frontmatter(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "java_advanced_agent.md", AGENT_MD)
    agent = AgentFile.from_path(path)
    assert "You are Jarvis" in agent.content
    assert "instruction_set:" not in agent.content


def test_agent_file_raises_on_missing_frontmatter(tmp_path):
    from tools.exporter import AgentFile
    path = write_agent(tmp_path, "developer", "bad_agent.md", "# No frontmatter here")
    with pytest.raises(ValueError, match="missing YAML frontmatter"):
        AgentFile.from_path(path)


# ── PlatformExporter base ─────────────────────────────────────────────────────

def make_skill(tmp_path: Path) -> "SkillFile":
    from tools.exporter import SkillFile
    p = write_skill(tmp_path, "java_advanced_skill.md", SKILL_MD)
    return SkillFile.from_path(p)


def make_agent(tmp_path: Path, role: str = "developer") -> "AgentFile":
    from tools.exporter import AgentFile
    p = write_agent(tmp_path, role, "java_advanced_agent.md", AGENT_MD)
    return AgentFile.from_path(p)


def test_export_result_stores_fields(tmp_path):
    from tools.exporter import ExportResult
    result = ExportResult(
        target="claude",
        skill_files=[tmp_path / "skill.md"],
        agent_files=[tmp_path / "agent.md"],
        dry_run=False,
    )
    assert result.target == "claude"
    assert len(result.skill_files) == 1
    assert len(result.agent_files) == 1
    assert result.dry_run is False


def test_platform_exporter_export_writes_skill_file(tmp_path):
    from tools.exporter import ClaudeExporter
    skill = make_skill(tmp_path)
    exporter = ClaudeExporter(repo_root=tmp_path)
    exporter.export(skills=[skill], agents=[], dry_run=False)
    out = tmp_path / ".claude" / "skills" / "java_advanced_skill.md"
    assert out.exists()
    assert "Java Advanced" in out.read_text()


def test_platform_exporter_export_writes_agent_file(tmp_path):
    from tools.exporter import ClaudeExporter
    agent = make_agent(tmp_path)
    exporter = ClaudeExporter(repo_root=tmp_path)
    exporter.export(skills=[], agents=[agent], dry_run=False)
    out = tmp_path / ".claude" / "agents" / "java_advanced_agent.md"
    assert out.exists()


def test_platform_exporter_dry_run_does_not_write(tmp_path):
    from tools.exporter import ClaudeExporter
    skill = make_skill(tmp_path)
    exporter = ClaudeExporter(repo_root=tmp_path)
    result = exporter.export(skills=[skill], agents=[], dry_run=True)
    out = tmp_path / ".claude" / "skills" / "java_advanced_skill.md"
    assert not out.exists()
    assert result.dry_run is True


def test_platform_exporter_returns_correct_file_paths(tmp_path):
    from tools.exporter import ClaudeExporter
    skill = make_skill(tmp_path)
    agent = make_agent(tmp_path)
    exporter = ClaudeExporter(repo_root=tmp_path)
    result = exporter.export(skills=[skill], agents=[agent], dry_run=True)
    assert any("java_advanced_skill" in str(p) for p in result.skill_files)
    assert any("java_advanced_agent" in str(p) for p in result.agent_files)
