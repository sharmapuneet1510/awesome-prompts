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
