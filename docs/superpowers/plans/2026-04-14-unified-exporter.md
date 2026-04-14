# Unified Agent & Skill Exporter — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `tools/skill_exporter.py` with `tools/exporter.py` — a unified exporter that writes one file per skill and one file per agent to 8 AI platform-native directories.

**Architecture:** Three data model classes (`BaseFile`, `SkillFile`, `AgentFile`) share a common YAML frontmatter parser. Eight `PlatformExporter` subclasses each know their output directories and file format. `ExportOrchestrator` discovers, filters, and drives all exporters. Single CLI entry point.

**Tech Stack:** Python 3.11+, stdlib only (`pathlib`, `argparse`, `re`, `abc`, `dataclasses`, `shutil`). Tests use `pytest` with `tmp_path` fixture.

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Create | `tools/exporter.py` | All data models, exporters, orchestrator, CLI |
| Create | `tests/tools/test_exporter.py` | All tests |
| Delete | `tools/skill_exporter.py` | Replaced by exporter.py |
| Update | `tools/README.md` | Replace skill_exporter docs |
| Update | `CLAUDE.md` | Update tool reference |

---

## Task 1: Test infrastructure and `BaseFile` parser

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/tools/__init__.py`
- Create: `tests/tools/test_exporter.py`
- Create: `tools/exporter.py` (skeleton + `BaseFile`)

- [ ] **Step 1: Create test directory structure**

```bash
mkdir -p tests/tools
touch tests/__init__.py tests/tools/__init__.py
```

- [ ] **Step 2: Write failing tests for `BaseFile` frontmatter parsing**

Create `tests/tools/test_exporter.py`:

```python
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


# ── BaseFile / SkillFile parsing ──────────────────────────────────────────────

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
```

- [ ] **Step 3: Run tests — expect ImportError (module doesn't exist yet)**

```bash
cd /path/to/repo && python -m pytest tests/tools/test_exporter.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'tools.exporter'`

- [ ] **Step 4: Create `tools/exporter.py` with `BaseFile` and `SkillFile`**

```python
#!/usr/bin/env python3
"""
exporter.py — Unified agent & skill exporter for AI assistant platforms.

Reads skill files from skills/ and agent files from agents/ and writes
one file per item to the platform-native directory for each target.

Usage:
    python tools/exporter.py                          # all → all platforms
    python tools/exporter.py --target copilot claude  # specific platforms
    python tools/exporter.py --skills java,spring     # filter skills
    python tools/exporter.py --agents developer       # filter agents by role
    python tools/exporter.py --list                   # list all items
    python tools/exporter.py --dry-run                # preview without writing
    python tools/exporter.py --clean                  # remove all exported files

Supported targets:
    copilot   → .github/instructions/ + .github/copilot/agents/
    claude    → .claude/skills/ + .claude/agents/
    cursor    → .cursor/rules/ + .cursor/rules/agents/
    windsurf  → .windsurf/rules/ + .windsurf/rules/agents/
    gemini    → .gemini/skills/ + .gemini/agents/
    continue  → .continue/prompts/ + .continue/prompts/agents/
    openai    → tools/output/openai/skills/ + tools/output/openai/agents/
    aider     → .aider/skills/ + .aider/agents/
    all       → All of the above (default)
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class BaseFile:
    """Shared base for skill and agent file data models.

    Attributes:
        path:        Absolute path to the source .md file.
        name:        Human-readable name from YAML frontmatter.
        version:     Version string from frontmatter.
        description: One-line summary from frontmatter.
        content:     Markdown body with frontmatter stripped.
        slug:        Identifier derived from the file stem.
    """

    path: Path
    name: str
    version: str
    description: str
    content: str
    slug: str

    _FRONTMATTER_RE: ClassVar[re.Pattern] = re.compile(
        r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL
    )

    @classmethod
    def _parse_frontmatter(cls, path: Path) -> tuple[str, str]:
        """Splits a markdown file into (frontmatter_text, body_text).

        Args:
            path: Path to the .md file.

        Returns:
            Tuple of (frontmatter YAML text, body markdown text).

        Raises:
            ValueError: If the file has no --- frontmatter block.
        """
        raw = path.read_text(encoding="utf-8")
        match = cls._FRONTMATTER_RE.match(raw)
        if not match:
            raise ValueError(
                f"'{path.name}' is missing YAML frontmatter (--- ... ---). "
                f"All skill and agent files must start with a frontmatter block."
            )
        return match.group(1), raw[match.end():].strip()

    @staticmethod
    def _extract_scalar(text: str, key: str, default: str = "") -> str:
        """Extracts a scalar string value from plain YAML text.

        Handles single-line values and > block scalar values.

        Args:
            text:    Raw YAML frontmatter text.
            key:     The key to look up.
            default: Returned if the key is not found.

        Returns:
            The string value, or default.
        """
        single = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE)
        if single:
            return single.group(1).strip().strip("'\"")

        block = re.search(rf"^{key}:\s*>\s*\n((?:  .+\n?)+)", text, re.MULTILINE)
        if block:
            return " ".join(line.strip() for line in block.group(1).strip().splitlines())

        return default

    @staticmethod
    def _extract_list(text: str, key: str) -> list[str]:
        """Extracts a YAML list from plain YAML text.

        Handles inline lists: [a, b] and block lists with - items.

        Args:
            text: Raw YAML frontmatter text.
            key:  The key to look up.

        Returns:
            A list of string values, or empty list.
        """
        inline = re.search(rf"^{key}:\s*\[([^\]]*)\]", text, re.MULTILINE)
        if inline:
            return [
                i.strip().strip("'\"")
                for i in inline.group(1).split(",")
                if i.strip()
            ]

        block_start = re.search(rf"^{key}:\s*$", text, re.MULTILINE)
        if block_start:
            items = re.findall(r"^\s+-\s+(.+)$", text[block_start.end():], re.MULTILINE)
            return [i.strip().strip("'\"") for i in items]

        return []


@dataclass
class SkillFile(BaseFile):
    """Parsed representation of a skill .md file from skills/.

    Attributes:
        applies_to: Technology areas this skill covers (e.g. ['java', 'spring-boot']).
        tags:       Topic tags for filtering (e.g. ['java', 'patterns']).
    """

    applies_to: list[str]
    tags: list[str]

    @classmethod
    def from_path(cls, path: Path) -> "SkillFile":
        """Parses a skill markdown file.

        Args:
            path: Path to the skills/*.md file.

        Returns:
            A populated SkillFile instance.

        Raises:
            ValueError: If the file has no YAML frontmatter.
        """
        fm, body = cls._parse_frontmatter(path)
        return cls(
            path=path,
            name=cls._extract_scalar(fm, "name", default=path.stem),
            version=cls._extract_scalar(fm, "version", default="1.0"),
            description=cls._extract_scalar(fm, "description"),
            applies_to=cls._extract_list(fm, "applies_to"),
            tags=cls._extract_list(fm, "tags"),
            content=body,
            slug=path.stem,
        )
```

- [ ] **Step 5: Run tests — expect failures only for AgentFile (not yet defined)**

```bash
python -m pytest tests/tools/test_exporter.py -v -k "skill"
```

Expected: All `test_skill_*` tests PASS.

- [ ] **Step 6: Commit**

```bash
git add tools/exporter.py tests/__init__.py tests/tools/__init__.py tests/tools/test_exporter.py
git commit -m "feat: add BaseFile parser and SkillFile data model with tests"
```

---

## Task 2: `AgentFile` data model

**Files:**
- Modify: `tools/exporter.py` — add `AgentFile` class
- Modify: `tests/tools/test_exporter.py` — add `AgentFile` tests

- [ ] **Step 1: Add `AgentFile` tests to `tests/tools/test_exporter.py`**

Append to the test file:

```python
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
```

- [ ] **Step 2: Run tests — expect failures for AgentFile**

```bash
python -m pytest tests/tools/test_exporter.py -v -k "agent"
```

Expected: `ImportError: cannot import name 'AgentFile'`

- [ ] **Step 3: Add `AgentFile` to `tools/exporter.py`**

Add after the `SkillFile` class:

```python
@dataclass
class AgentFile(BaseFile):
    """Parsed representation of an agent .md file from agents/**/.

    Attributes:
        skills:          Slugs of skills this agent references.
        instruction_set: Relative path to the master instruction set.
        intake_form:     Relative path to the intake form.
        role:            Derived from the parent directory name
                         (developer, reviewer, writer, integration).
    """

    skills: list[str]
    instruction_set: str
    intake_form: str
    role: str

    @classmethod
    def from_path(cls, path: Path) -> "AgentFile":
        """Parses an agent markdown file.

        Args:
            path: Path to the agents/**/*.md file.

        Returns:
            A populated AgentFile instance.

        Raises:
            ValueError: If the file has no YAML frontmatter.
        """
        fm, body = cls._parse_frontmatter(path)
        return cls(
            path=path,
            name=cls._extract_scalar(fm, "name", default=path.stem),
            version=cls._extract_scalar(fm, "version", default="1.0"),
            description=cls._extract_scalar(fm, "description"),
            skills=cls._extract_list(fm, "skills"),
            instruction_set=cls._extract_scalar(fm, "instruction_set"),
            intake_form=cls._extract_scalar(fm, "intake_form"),
            role=path.parent.name,
            content=body,
            slug=path.stem,
        )
```

- [ ] **Step 4: Run all tests**

```bash
python -m pytest tests/tools/test_exporter.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/exporter.py tests/tools/test_exporter.py
git commit -m "feat: add AgentFile data model with tests"
```

---

## Task 3: `ExportResult` and `PlatformExporter` abstract base

**Files:**
- Modify: `tools/exporter.py` — add `ExportResult`, `PlatformExporter`
- Modify: `tests/tools/test_exporter.py` — add abstract base tests

- [ ] **Step 1: Add `PlatformExporter` tests**

Append to `tests/tools/test_exporter.py`:

```python
# ── PlatformExporter base ─────────────────────────────────────────────────────

def make_skill(tmp_path: Path, slug: str = "java_advanced_skill") -> "SkillFile":
    from tools.exporter import SkillFile
    p = write_skill(tmp_path, f"{slug}.md", SKILL_MD)
    return SkillFile.from_path(p)


def make_agent(tmp_path: Path, role: str = "developer", slug: str = "java_advanced_agent") -> "AgentFile":
    from tools.exporter import AgentFile
    p = write_agent(tmp_path, role, f"{slug}.md", AGENT_MD)
    return AgentFile.from_path(p)


def test_export_result_stores_target_and_paths(tmp_path):
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
    from tools.exporter import ClaudeExporter, SkillFile
    skill = make_skill(tmp_path)
    exporter = ClaudeExporter(repo_root=tmp_path)
    result = exporter.export(skills=[skill], agents=[], dry_run=False)
    out = tmp_path / ".claude" / "skills" / "java_advanced_skill.md"
    assert out.exists()
    assert "Java Advanced" in out.read_text()


def test_platform_exporter_export_writes_agent_file(tmp_path):
    from tools.exporter import ClaudeExporter, AgentFile
    agent = make_agent(tmp_path)
    exporter = ClaudeExporter(repo_root=tmp_path)
    result = exporter.export(skills=[], agents=[agent], dry_run=False)
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
```

- [ ] **Step 2: Run — expect ImportError for `ClaudeExporter`**

```bash
python -m pytest tests/tools/test_exporter.py -v -k "export_result or platform_exporter"
```

Expected: `ImportError: cannot import name 'ClaudeExporter'`

- [ ] **Step 3: Add `ExportResult` and `PlatformExporter` to `tools/exporter.py`**

Add after `AgentFile`:

```python
# ─────────────────────────────────────────────────────────────────────────────
# Export Result
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ExportResult:
    """Result of one platform export run.

    Attributes:
        target:      Platform name (e.g. 'claude').
        skill_files: Paths of written (or would-be-written) skill files.
        agent_files: Paths of written (or would-be-written) agent files.
        dry_run:     True if files were NOT actually written.
    """

    target: str
    skill_files: list[Path]
    agent_files: list[Path]
    dry_run: bool


# ─────────────────────────────────────────────────────────────────────────────
# Abstract Platform Exporter
# ─────────────────────────────────────────────────────────────────────────────

class PlatformExporter(ABC):
    """Abstract base class for all platform exporters.

    Each subclass knows its output directories, file naming convention,
    and how to format skills and agents for its platform.

    Subclasses must implement:
        target_name, skill_output_dir, agent_output_dir,
        format_skill, format_agent
    """

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    @property
    @abstractmethod
    def target_name(self) -> str:
        """Short platform identifier (e.g. 'copilot')."""

    @abstractmethod
    def skill_output_dir(self) -> Path:
        """Directory where skill files are written."""

    @abstractmethod
    def agent_output_dir(self) -> Path:
        """Directory where agent files are written."""

    @abstractmethod
    def format_skill(self, skill: SkillFile) -> str:
        """Formats a skill for this platform."""

    @abstractmethod
    def format_agent(self, agent: AgentFile) -> str:
        """Formats an agent for this platform."""

    def skill_filename(self, skill: SkillFile) -> str:
        """Output filename for a skill. Override in subclasses for non-.md extensions."""
        return f"{skill.slug}.md"

    def agent_filename(self, agent: AgentFile) -> str:
        """Output filename for an agent. Override in subclasses for non-.md extensions."""
        return f"{agent.slug}.md"

    def export(
        self,
        skills: list[SkillFile],
        agents: list[AgentFile],
        dry_run: bool = False,
    ) -> ExportResult:
        """Writes one file per skill and one file per agent.

        Args:
            skills:  Skill files to export.
            agents:  Agent files to export.
            dry_run: If True, generate paths but do not write files.

        Returns:
            ExportResult with all written (or planned) file paths.
        """
        skill_paths: list[Path] = []
        agent_paths: list[Path] = []

        for skill in skills:
            out = self.skill_output_dir() / self.skill_filename(skill)
            skill_paths.append(out)
            if not dry_run:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(self.format_skill(skill), encoding="utf-8")

        for agent in agents:
            out = self.agent_output_dir() / self.agent_filename(agent)
            agent_paths.append(out)
            if not dry_run:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(self.format_agent(agent), encoding="utf-8")

        return ExportResult(
            target=self.target_name,
            skill_files=skill_paths,
            agent_files=agent_paths,
            dry_run=dry_run,
        )
```

- [ ] **Step 4: Run tests (ClaudeExporter not yet implemented — add stub to pass import)**

Add a temporary stub at the bottom of `tools/exporter.py` so the import works:

```python
class ClaudeExporter(PlatformExporter):
    @property
    def target_name(self) -> str: return "claude"
    def skill_output_dir(self) -> Path: return self._repo_root / ".claude" / "skills"
    def agent_output_dir(self) -> Path: return self._repo_root / ".claude" / "agents"
    def format_skill(self, skill: SkillFile) -> str: return skill.content
    def format_agent(self, agent: AgentFile) -> str: return agent.content
```

```bash
python -m pytest tests/tools/test_exporter.py -v -k "export_result or platform_exporter"
```

Expected: All 5 `test_platform_exporter_*` and `test_export_result_*` tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/exporter.py tests/tools/test_exporter.py
git commit -m "feat: add ExportResult and PlatformExporter abstract base with tests"
```

---

## Task 4: `CopilotExporter` and `ClaudeExporter`

**Files:**
- Modify: `tools/exporter.py` — replace stub `ClaudeExporter`, add `CopilotExporter`
- Modify: `tests/tools/test_exporter.py` — add format tests

- [ ] **Step 1: Add format tests for Copilot and Claude**

Append to `tests/tools/test_exporter.py`:

```python
# ── CopilotExporter ───────────────────────────────────────────────────────────

def test_copilot_skill_filename_has_instructions_suffix(tmp_path):
    from tools.exporter import CopilotExporter
    skill = make_skill(tmp_path)
    exporter = CopilotExporter(repo_root=tmp_path)
    assert exporter.skill_filename(skill) == "java_advanced_skill.instructions.md"


def test_copilot_skill_format_has_apply_to_frontmatter(tmp_path):
    from tools.exporter import CopilotExporter
    skill = make_skill(tmp_path)
    exporter = CopilotExporter(repo_root=tmp_path)
    output = exporter.format_skill(skill)
    assert "applyTo: '**'" in output


def test_copilot_skill_output_dir(tmp_path):
    from tools.exporter import CopilotExporter
    exporter = CopilotExporter(repo_root=tmp_path)
    assert exporter.skill_output_dir() == tmp_path / ".github" / "instructions"


def test_copilot_agent_output_dir(tmp_path):
    from tools.exporter import CopilotExporter
    exporter = CopilotExporter(repo_root=tmp_path)
    assert exporter.agent_output_dir() == tmp_path / ".github" / "copilot" / "agents"


def test_copilot_agent_format_has_name_in_frontmatter(tmp_path):
    from tools.exporter import CopilotExporter
    agent = make_agent(tmp_path)
    exporter = CopilotExporter(repo_root=tmp_path)
    output = exporter.format_agent(agent)
    assert "name:" in output
    assert "description:" in output


# ── ClaudeExporter ────────────────────────────────────────────────────────────

def test_claude_skill_output_dir(tmp_path):
    from tools.exporter import ClaudeExporter
    exporter = ClaudeExporter(repo_root=tmp_path)
    assert exporter.skill_output_dir() == tmp_path / ".claude" / "skills"


def test_claude_agent_output_dir(tmp_path):
    from tools.exporter import ClaudeExporter
    exporter = ClaudeExporter(repo_root=tmp_path)
    assert exporter.agent_output_dir() == tmp_path / ".claude" / "agents"


def test_claude_skill_format_has_generated_comment(tmp_path):
    from tools.exporter import ClaudeExporter
    skill = make_skill(tmp_path)
    exporter = ClaudeExporter(repo_root=tmp_path)
    output = exporter.format_skill(skill)
    assert "Generated by tools/exporter.py" in output


def test_claude_skill_format_preserves_content(tmp_path):
    from tools.exporter import ClaudeExporter
    skill = make_skill(tmp_path)
    exporter = ClaudeExporter(repo_root=tmp_path)
    output = exporter.format_skill(skill)
    assert "# Java Advanced Skill" in output


def test_claude_agent_format_has_generated_comment(tmp_path):
    from tools.exporter import ClaudeExporter
    agent = make_agent(tmp_path)
    exporter = ClaudeExporter(repo_root=tmp_path)
    output = exporter.format_agent(agent)
    assert "Generated by tools/exporter.py" in output
```

- [ ] **Step 2: Run — expect failures**

```bash
python -m pytest tests/tools/test_exporter.py -v -k "copilot or claude"
```

Expected: `CopilotExporter` tests fail with `ImportError`. `ClaudeExporter` format tests fail (stub returns raw content, no comment header).

- [ ] **Step 3: Replace the `ClaudeExporter` stub and add `CopilotExporter` in `tools/exporter.py`**

Replace the stub `ClaudeExporter` with:

```python
# ─────────────────────────────────────────────────────────────────────────────
# Platform Exporters
# ─────────────────────────────────────────────────────────────────────────────

class CopilotExporter(PlatformExporter):
    """GitHub Copilot — .github/instructions/ and .github/copilot/agents/

    Skills use the .instructions.md suffix and applyTo: '**' frontmatter
    so Copilot picks them up automatically in agent mode.
    Agents use name + description frontmatter for Copilot agent definitions.
    """

    @property
    def target_name(self) -> str:
        return "copilot"

    def skill_output_dir(self) -> Path:
        return self._repo_root / ".github" / "instructions"

    def agent_output_dir(self) -> Path:
        return self._repo_root / ".github" / "copilot" / "agents"

    def skill_filename(self, skill: SkillFile) -> str:
        return f"{skill.slug}.instructions.md"

    def format_skill(self, skill: SkillFile) -> str:
        applies = ", ".join(skill.applies_to) if skill.applies_to else "general"
        return (
            f"---\n"
            f"applyTo: '**'\n"
            f"---\n\n"
            f"<!-- Generated by tools/exporter.py from skills/{skill.slug}.md -->\n"
            f"<!-- Re-run: python tools/exporter.py --target copilot -->\n\n"
            f"# {skill.name}\n\n"
            f"> **Applies to:** {applies}\n\n"
            f"{skill.content}\n"
        )

    def format_agent(self, agent: AgentFile) -> str:
        return (
            f"---\n"
            f"name: {agent.name}\n"
            f"description: {agent.description or agent.name}\n"
            f"---\n\n"
            f"<!-- Generated by tools/exporter.py from agents/{agent.role}/{agent.slug}.md -->\n"
            f"<!-- Re-run: python tools/exporter.py --target copilot -->\n\n"
            f"{agent.content}\n"
        )


class ClaudeExporter(PlatformExporter):
    """Claude Code — .claude/skills/ and .claude/agents/

    Clean markdown files with a generated-by comment header.
    Referenced from CLAUDE.md so Claude loads them as context.
    """

    @property
    def target_name(self) -> str:
        return "claude"

    def skill_output_dir(self) -> Path:
        return self._repo_root / ".claude" / "skills"

    def agent_output_dir(self) -> Path:
        return self._repo_root / ".claude" / "agents"

    def _header(self, source_path: str) -> str:
        return (
            f"<!-- Generated by tools/exporter.py from {source_path} -->\n"
            f"<!-- Do not edit manually. Re-run: python tools/exporter.py -->\n\n"
        )

    def format_skill(self, skill: SkillFile) -> str:
        return self._header(f"skills/{skill.slug}.md") + skill.content + "\n"

    def format_agent(self, agent: AgentFile) -> str:
        return self._header(f"agents/{agent.role}/{agent.slug}.md") + agent.content + "\n"
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/tools/test_exporter.py -v -k "copilot or claude"
```

Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/exporter.py tests/tools/test_exporter.py
git commit -m "feat: add CopilotExporter and ClaudeExporter with tests"
```

---

## Task 5: `CursorExporter` and `WindsurfExporter`

**Files:**
- Modify: `tools/exporter.py`
- Modify: `tests/tools/test_exporter.py`

- [ ] **Step 1: Add tests**

Append to `tests/tools/test_exporter.py`:

```python
# ── CursorExporter ────────────────────────────────────────────────────────────

def test_cursor_skill_filename_has_mdc_extension(tmp_path):
    from tools.exporter import CursorExporter
    skill = make_skill(tmp_path)
    exporter = CursorExporter(repo_root=tmp_path)
    assert exporter.skill_filename(skill) == "java_advanced_skill.mdc"


def test_cursor_agent_filename_has_mdc_extension(tmp_path):
    from tools.exporter import CursorExporter
    agent = make_agent(tmp_path)
    exporter = CursorExporter(repo_root=tmp_path)
    assert exporter.agent_filename(agent) == "java_advanced_agent.mdc"


def test_cursor_skill_output_dir(tmp_path):
    from tools.exporter import CursorExporter
    exporter = CursorExporter(repo_root=tmp_path)
    assert exporter.skill_output_dir() == tmp_path / ".cursor" / "rules"


def test_cursor_agent_output_dir(tmp_path):
    from tools.exporter import CursorExporter
    exporter = CursorExporter(repo_root=tmp_path)
    assert exporter.agent_output_dir() == tmp_path / ".cursor" / "rules" / "agents"


def test_cursor_skill_format_has_required_frontmatter(tmp_path):
    from tools.exporter import CursorExporter
    skill = make_skill(tmp_path)
    exporter = CursorExporter(repo_root=tmp_path)
    output = exporter.format_skill(skill)
    assert "description:" in output
    assert "globs:" in output
    assert "alwaysApply:" in output


def test_cursor_agent_format_has_role_in_body(tmp_path):
    from tools.exporter import CursorExporter
    agent = make_agent(tmp_path, role="developer")
    exporter = CursorExporter(repo_root=tmp_path)
    output = exporter.format_agent(agent)
    assert "developer" in output


# ── WindsurfExporter ──────────────────────────────────────────────────────────

def test_windsurf_skill_output_dir(tmp_path):
    from tools.exporter import WindsurfExporter
    exporter = WindsurfExporter(repo_root=tmp_path)
    assert exporter.skill_output_dir() == tmp_path / ".windsurf" / "rules"


def test_windsurf_agent_output_dir(tmp_path):
    from tools.exporter import WindsurfExporter
    exporter = WindsurfExporter(repo_root=tmp_path)
    assert exporter.agent_output_dir() == tmp_path / ".windsurf" / "rules" / "agents"


def test_windsurf_skill_format_has_generated_comment(tmp_path):
    from tools.exporter import WindsurfExporter
    skill = make_skill(tmp_path)
    exporter = WindsurfExporter(repo_root=tmp_path)
    output = exporter.format_skill(skill)
    assert "Generated by tools/exporter.py" in output


def test_windsurf_agent_format_preserves_content(tmp_path):
    from tools.exporter import WindsurfExporter
    agent = make_agent(tmp_path)
    exporter = WindsurfExporter(repo_root=tmp_path)
    output = exporter.format_agent(agent)
    assert "You are Jarvis" in output
```

- [ ] **Step 2: Run — expect ImportError**

```bash
python -m pytest tests/tools/test_exporter.py -v -k "cursor or windsurf"
```

- [ ] **Step 3: Add `CursorExporter` and `WindsurfExporter` to `tools/exporter.py`**

```python
class CursorExporter(PlatformExporter):
    """Cursor IDE — .cursor/rules/ and .cursor/rules/agents/

    Files use the .mdc extension and require description, globs, and
    alwaysApply frontmatter fields. Cursor reads these automatically.
    """

    @property
    def target_name(self) -> str:
        return "cursor"

    def skill_output_dir(self) -> Path:
        return self._repo_root / ".cursor" / "rules"

    def agent_output_dir(self) -> Path:
        return self._repo_root / ".cursor" / "rules" / "agents"

    def skill_filename(self, skill: SkillFile) -> str:
        return f"{skill.slug}.mdc"

    def agent_filename(self, agent: AgentFile) -> str:
        return f"{agent.slug}.mdc"

    def format_skill(self, skill: SkillFile) -> str:
        applies = ", ".join(skill.applies_to) if skill.applies_to else "general"
        desc = skill.description or skill.name
        return (
            f"---\n"
            f"description: {desc}\n"
            f"globs: '**'\n"
            f"alwaysApply: false\n"
            f"---\n\n"
            f"<!-- Generated by tools/exporter.py from skills/{skill.slug}.md -->\n\n"
            f"# {skill.name}\n\n"
            f"> **Applies to:** {applies}\n\n"
            f"{skill.content}\n"
        )

    def format_agent(self, agent: AgentFile) -> str:
        desc = agent.description or agent.name
        return (
            f"---\n"
            f"description: {desc}\n"
            f"globs: '**'\n"
            f"alwaysApply: false\n"
            f"---\n\n"
            f"<!-- Generated by tools/exporter.py from agents/{agent.role}/{agent.slug}.md -->\n\n"
            f"# {agent.name}\n\n"
            f"> **Role:** {agent.role}\n\n"
            f"{agent.content}\n"
        )


class WindsurfExporter(PlatformExporter):
    """Windsurf IDE — .windsurf/rules/ and .windsurf/rules/agents/

    Clean markdown with a generated-by comment and skill/agent name heading.
    """

    @property
    def target_name(self) -> str:
        return "windsurf"

    def skill_output_dir(self) -> Path:
        return self._repo_root / ".windsurf" / "rules"

    def agent_output_dir(self) -> Path:
        return self._repo_root / ".windsurf" / "rules" / "agents"

    def _header(self, name: str, source_path: str) -> str:
        return (
            f"<!-- Generated by tools/exporter.py from {source_path} -->\n"
            f"<!-- Do not edit manually. Re-run: python tools/exporter.py -->\n\n"
            f"# {name}\n\n"
        )

    def format_skill(self, skill: SkillFile) -> str:
        return self._header(skill.name, f"skills/{skill.slug}.md") + skill.content + "\n"

    def format_agent(self, agent: AgentFile) -> str:
        return self._header(agent.name, f"agents/{agent.role}/{agent.slug}.md") + agent.content + "\n"
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/tools/test_exporter.py -v -k "cursor or windsurf"
```

Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/exporter.py tests/tools/test_exporter.py
git commit -m "feat: add CursorExporter and WindsurfExporter with tests"
```

---

## Task 6: `GeminiExporter` and `ContinueExporter`

**Files:**
- Modify: `tools/exporter.py`
- Modify: `tests/tools/test_exporter.py`

- [ ] **Step 1: Add tests**

Append to `tests/tools/test_exporter.py`:

```python
# ── GeminiExporter ────────────────────────────────────────────────────────────

def test_gemini_skill_output_dir(tmp_path):
    from tools.exporter import GeminiExporter
    exporter = GeminiExporter(repo_root=tmp_path)
    assert exporter.skill_output_dir() == tmp_path / ".gemini" / "skills"


def test_gemini_agent_output_dir(tmp_path):
    from tools.exporter import GeminiExporter
    exporter = GeminiExporter(repo_root=tmp_path)
    assert exporter.agent_output_dir() == tmp_path / ".gemini" / "agents"


def test_gemini_skill_format_has_generated_comment(tmp_path):
    from tools.exporter import GeminiExporter
    skill = make_skill(tmp_path)
    exporter = GeminiExporter(repo_root=tmp_path)
    output = exporter.format_skill(skill)
    assert "Generated by tools/exporter.py" in output


def test_gemini_agent_format_preserves_content(tmp_path):
    from tools.exporter import GeminiExporter
    agent = make_agent(tmp_path)
    exporter = GeminiExporter(repo_root=tmp_path)
    output = exporter.format_agent(agent)
    assert "You are Jarvis" in output


# ── ContinueExporter ──────────────────────────────────────────────────────────

def test_continue_skill_filename_has_prompt_extension(tmp_path):
    from tools.exporter import ContinueExporter
    skill = make_skill(tmp_path)
    exporter = ContinueExporter(repo_root=tmp_path)
    assert exporter.skill_filename(skill) == "java_advanced_skill.prompt"


def test_continue_agent_filename_has_prompt_extension(tmp_path):
    from tools.exporter import ContinueExporter
    agent = make_agent(tmp_path)
    exporter = ContinueExporter(repo_root=tmp_path)
    assert exporter.agent_filename(agent) == "java_advanced_agent.prompt"


def test_continue_skill_output_dir(tmp_path):
    from tools.exporter import ContinueExporter
    exporter = ContinueExporter(repo_root=tmp_path)
    assert exporter.skill_output_dir() == tmp_path / ".continue" / "prompts"


def test_continue_agent_output_dir(tmp_path):
    from tools.exporter import ContinueExporter
    exporter = ContinueExporter(repo_root=tmp_path)
    assert exporter.agent_output_dir() == tmp_path / ".continue" / "prompts" / "agents"


def test_continue_skill_format_has_name_and_description_frontmatter(tmp_path):
    from tools.exporter import ContinueExporter
    skill = make_skill(tmp_path)
    exporter = ContinueExporter(repo_root=tmp_path)
    output = exporter.format_skill(skill)
    assert "name:" in output
    assert "description:" in output


def test_continue_agent_format_has_frontmatter(tmp_path):
    from tools.exporter import ContinueExporter
    agent = make_agent(tmp_path)
    exporter = ContinueExporter(repo_root=tmp_path)
    output = exporter.format_agent(agent)
    assert "name:" in output
    assert "description:" in output
```

- [ ] **Step 2: Run — expect ImportError**

```bash
python -m pytest tests/tools/test_exporter.py -v -k "gemini or continue"
```

- [ ] **Step 3: Add `GeminiExporter` and `ContinueExporter` to `tools/exporter.py`**

```python
class GeminiExporter(PlatformExporter):
    """Gemini CLI — .gemini/skills/ and .gemini/agents/

    Clean markdown with a generated-by comment and heading.
    """

    @property
    def target_name(self) -> str:
        return "gemini"

    def skill_output_dir(self) -> Path:
        return self._repo_root / ".gemini" / "skills"

    def agent_output_dir(self) -> Path:
        return self._repo_root / ".gemini" / "agents"

    def _header(self, name: str, source_path: str) -> str:
        return (
            f"<!-- Generated by tools/exporter.py from {source_path} -->\n"
            f"<!-- Do not edit manually. Re-run: python tools/exporter.py -->\n\n"
            f"# {name}\n\n"
        )

    def format_skill(self, skill: SkillFile) -> str:
        return self._header(skill.name, f"skills/{skill.slug}.md") + skill.content + "\n"

    def format_agent(self, agent: AgentFile) -> str:
        return self._header(agent.name, f"agents/{agent.role}/{agent.slug}.md") + agent.content + "\n"


class ContinueExporter(PlatformExporter):
    """Continue.dev — .continue/prompts/ and .continue/prompts/agents/

    Files use the .prompt extension and require name + description
    frontmatter fields that Continue.dev reads for its prompt library.
    """

    @property
    def target_name(self) -> str:
        return "continue"

    def skill_output_dir(self) -> Path:
        return self._repo_root / ".continue" / "prompts"

    def agent_output_dir(self) -> Path:
        return self._repo_root / ".continue" / "prompts" / "agents"

    def skill_filename(self, skill: SkillFile) -> str:
        return f"{skill.slug}.prompt"

    def agent_filename(self, agent: AgentFile) -> str:
        return f"{agent.slug}.prompt"

    def format_skill(self, skill: SkillFile) -> str:
        desc = skill.description or skill.name
        return (
            f"---\n"
            f"name: {skill.name}\n"
            f"description: {desc}\n"
            f"---\n\n"
            f"{skill.content}\n"
        )

    def format_agent(self, agent: AgentFile) -> str:
        desc = agent.description or agent.name
        return (
            f"---\n"
            f"name: {agent.name}\n"
            f"description: {desc}\n"
            f"---\n\n"
            f"{agent.content}\n"
        )
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/tools/test_exporter.py -v -k "gemini or continue"
```

Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/exporter.py tests/tools/test_exporter.py
git commit -m "feat: add GeminiExporter and ContinueExporter with tests"
```

---

## Task 7: `OpenAIExporter` and `AiderExporter`

**Files:**
- Modify: `tools/exporter.py`
- Modify: `tests/tools/test_exporter.py`

- [ ] **Step 1: Add tests**

Append to `tests/tools/test_exporter.py`:

```python
# ── OpenAIExporter ────────────────────────────────────────────────────────────

def test_openai_skill_filename_has_txt_extension(tmp_path):
    from tools.exporter import OpenAIExporter
    skill = make_skill(tmp_path)
    exporter = OpenAIExporter(repo_root=tmp_path)
    assert exporter.skill_filename(skill) == "java_advanced_skill.txt"


def test_openai_agent_filename_has_txt_extension(tmp_path):
    from tools.exporter import OpenAIExporter
    agent = make_agent(tmp_path)
    exporter = OpenAIExporter(repo_root=tmp_path)
    assert exporter.agent_filename(agent) == "java_advanced_agent.txt"


def test_openai_skill_output_dir(tmp_path):
    from tools.exporter import OpenAIExporter
    exporter = OpenAIExporter(repo_root=tmp_path)
    assert exporter.skill_output_dir() == tmp_path / "tools" / "output" / "openai" / "skills"


def test_openai_agent_output_dir(tmp_path):
    from tools.exporter import OpenAIExporter
    exporter = OpenAIExporter(repo_root=tmp_path)
    assert exporter.agent_output_dir() == tmp_path / "tools" / "output" / "openai" / "agents"


def test_openai_skill_format_is_plain_text_with_header(tmp_path):
    from tools.exporter import OpenAIExporter
    skill = make_skill(tmp_path)
    exporter = OpenAIExporter(repo_root=tmp_path)
    output = exporter.format_skill(skill)
    assert "SKILL:" in output
    assert "APPLIES TO:" in output


def test_openai_skill_format_strips_markdown_headings(tmp_path):
    from tools.exporter import OpenAIExporter
    skill = make_skill(tmp_path)
    exporter = OpenAIExporter(repo_root=tmp_path)
    output = exporter.format_skill(skill)
    assert "## " not in output
    assert "# " not in output


def test_openai_agent_format_is_plain_text_with_header(tmp_path):
    from tools.exporter import OpenAIExporter
    agent = make_agent(tmp_path)
    exporter = OpenAIExporter(repo_root=tmp_path)
    output = exporter.format_agent(agent)
    assert "AGENT:" in output
    assert "ROLE:" in output


# ── AiderExporter ─────────────────────────────────────────────────────────────

def test_aider_skill_output_dir(tmp_path):
    from tools.exporter import AiderExporter
    exporter = AiderExporter(repo_root=tmp_path)
    assert exporter.skill_output_dir() == tmp_path / ".aider" / "skills"


def test_aider_agent_output_dir(tmp_path):
    from tools.exporter import AiderExporter
    exporter = AiderExporter(repo_root=tmp_path)
    assert exporter.agent_output_dir() == tmp_path / ".aider" / "agents"


def test_aider_skill_format_has_generated_comment(tmp_path):
    from tools.exporter import AiderExporter
    skill = make_skill(tmp_path)
    exporter = AiderExporter(repo_root=tmp_path)
    output = exporter.format_skill(skill)
    assert "Generated by tools/exporter.py" in output


def test_aider_agent_format_preserves_content(tmp_path):
    from tools.exporter import AiderExporter
    agent = make_agent(tmp_path)
    exporter = AiderExporter(repo_root=tmp_path)
    output = exporter.format_agent(agent)
    assert "You are Jarvis" in output
```

- [ ] **Step 2: Run — expect ImportError**

```bash
python -m pytest tests/tools/test_exporter.py -v -k "openai or aider"
```

- [ ] **Step 3: Add `OpenAIExporter` and `AiderExporter` to `tools/exporter.py`**

```python
class OpenAIExporter(PlatformExporter):
    """OpenAI API — tools/output/openai/skills/ and tools/output/openai/agents/

    Plain text files suitable for use as system prompts in the OpenAI API
    or any other LLM API. Markdown syntax is stripped for maximum portability.
    """

    _HEADING_RE: ClassVar[re.Pattern] = re.compile(r"^#{1,6}\s+", re.MULTILINE)
    _BOLD_RE: ClassVar[re.Pattern] = re.compile(r"\*{1,2}([^*\n]+)\*{1,2}")
    _INLINE_CODE_RE: ClassVar[re.Pattern] = re.compile(r"`([^`\n]+)`")

    @property
    def target_name(self) -> str:
        return "openai"

    def skill_output_dir(self) -> Path:
        return self._repo_root / "tools" / "output" / "openai" / "skills"

    def agent_output_dir(self) -> Path:
        return self._repo_root / "tools" / "output" / "openai" / "agents"

    def skill_filename(self, skill: SkillFile) -> str:
        return f"{skill.slug}.txt"

    def agent_filename(self, agent: AgentFile) -> str:
        return f"{agent.slug}.txt"

    def _to_plain_text(self, content: str) -> str:
        """Strips common markdown formatting from content."""
        text = self._HEADING_RE.sub("", content)
        text = self._BOLD_RE.sub(r"\1", text)
        text = self._INLINE_CODE_RE.sub(r"\1", text)
        return text.strip()

    def format_skill(self, skill: SkillFile) -> str:
        applies = ", ".join(skill.applies_to) if skill.applies_to else "general"
        body = self._to_plain_text(skill.content)
        return (
            f"SKILL: {skill.name.upper()}\n"
            f"APPLIES TO: {applies}\n"
            f"{'=' * 60}\n\n"
            f"{body}\n"
        )

    def format_agent(self, agent: AgentFile) -> str:
        body = self._to_plain_text(agent.content)
        return (
            f"AGENT: {agent.name.upper()}\n"
            f"ROLE: {agent.role}\n"
            f"{'=' * 60}\n\n"
            f"{body}\n"
        )


class AiderExporter(PlatformExporter):
    """Aider — .aider/skills/ and .aider/agents/

    Clean markdown with a generated-by comment and heading.
    Place .aider/ in your repo root; Aider can load these as context files.
    """

    @property
    def target_name(self) -> str:
        return "aider"

    def skill_output_dir(self) -> Path:
        return self._repo_root / ".aider" / "skills"

    def agent_output_dir(self) -> Path:
        return self._repo_root / ".aider" / "agents"

    def _header(self, name: str, source_path: str) -> str:
        return (
            f"<!-- Generated by tools/exporter.py from {source_path} -->\n"
            f"<!-- Do not edit manually. Re-run: python tools/exporter.py -->\n\n"
            f"# {name}\n\n"
        )

    def format_skill(self, skill: SkillFile) -> str:
        return self._header(skill.name, f"skills/{skill.slug}.md") + skill.content + "\n"

    def format_agent(self, agent: AgentFile) -> str:
        return self._header(agent.name, f"agents/{agent.role}/{agent.slug}.md") + agent.content + "\n"
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/tools/test_exporter.py -v -k "openai or aider"
```

Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/exporter.py tests/tools/test_exporter.py
git commit -m "feat: add OpenAIExporter and AiderExporter with tests"
```

---

## Task 8: `ExportOrchestrator`

**Files:**
- Modify: `tools/exporter.py` — add `ExportOrchestrator`
- Modify: `tests/tools/test_exporter.py` — add orchestrator tests

- [ ] **Step 1: Add orchestrator tests**

Append to `tests/tools/test_exporter.py`:

```python
# ── ExportOrchestrator ────────────────────────────────────────────────────────

def make_skills_dir(tmp_path: Path) -> Path:
    """Creates a skills/ directory with two skill files."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "java_advanced_skill.md").write_text(SKILL_MD, encoding="utf-8")
    (skills_dir / "test_skill.md").write_text(SKILL_INLINE_LIST, encoding="utf-8")
    return skills_dir


def make_agents_dir(tmp_path: Path) -> Path:
    """Creates an agents/ directory with one agent file and a README."""
    agents_dir = tmp_path / "agents"
    dev_dir = agents_dir / "developer"
    dev_dir.mkdir(parents=True)
    (dev_dir / "java_advanced_agent.md").write_text(AGENT_MD, encoding="utf-8")
    (agents_dir / "README.md").write_text("# Agents\n", encoding="utf-8")
    return agents_dir


def test_orchestrator_discovers_all_skills(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_skills_dir(tmp_path)
    orch = ExportOrchestrator(repo_root=tmp_path)
    skills = orch.discover_skills()
    assert len(skills) == 2
    assert any(s.slug == "java_advanced_skill" for s in skills)


def test_orchestrator_discover_skills_raises_when_dir_missing(tmp_path):
    from tools.exporter import ExportOrchestrator
    orch = ExportOrchestrator(repo_root=tmp_path)
    with pytest.raises(FileNotFoundError, match="skills/"):
        orch.discover_skills()


def test_orchestrator_skips_skill_without_frontmatter(tmp_path):
    from tools.exporter import ExportOrchestrator
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "bad.md").write_text("# No frontmatter", encoding="utf-8")
    orch = ExportOrchestrator(repo_root=tmp_path)
    skills = orch.discover_skills()
    assert len(skills) == 0


def test_orchestrator_discovers_all_agents(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_agents_dir(tmp_path)
    orch = ExportOrchestrator(repo_root=tmp_path)
    agents = orch.discover_agents()
    assert len(agents) == 1
    assert agents[0].slug == "java_advanced_agent"


def test_orchestrator_skips_readme_in_agents(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_agents_dir(tmp_path)
    orch = ExportOrchestrator(repo_root=tmp_path)
    agents = orch.discover_agents()
    assert not any(a.slug.lower() == "readme" for a in agents)


def test_orchestrator_filter_skills_by_slug(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_skills_dir(tmp_path)
    orch = ExportOrchestrator(repo_root=tmp_path)
    all_skills = orch.discover_skills()
    filtered = orch.filter_skills(all_skills, ["java"])
    assert len(filtered) == 1
    assert filtered[0].slug == "java_advanced_skill"


def test_orchestrator_filter_skills_empty_returns_all(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_skills_dir(tmp_path)
    orch = ExportOrchestrator(repo_root=tmp_path)
    all_skills = orch.discover_skills()
    filtered = orch.filter_skills(all_skills, [])
    assert filtered == all_skills


def test_orchestrator_filter_agents_by_role(tmp_path):
    from tools.exporter import ExportOrchestrator
    agents_dir = tmp_path / "agents"
    (agents_dir / "developer").mkdir(parents=True)
    (agents_dir / "reviewer").mkdir(parents=True)
    (agents_dir / "developer" / "java_advanced_agent.md").write_text(AGENT_MD, encoding="utf-8")
    (agents_dir / "reviewer" / "code_review_agent.md").write_text(AGENT_MD, encoding="utf-8")
    orch = ExportOrchestrator(repo_root=tmp_path)
    all_agents = orch.discover_agents()
    filtered = orch.filter_agents(all_agents, ["developer"])
    assert len(filtered) == 1
    assert filtered[0].role == "developer"


def test_orchestrator_run_writes_files_for_single_target(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_skills_dir(tmp_path)
    make_agents_dir(tmp_path)
    orch = ExportOrchestrator(repo_root=tmp_path)
    results = orch.run(targets=["claude"], skill_filter=[], agent_filter=[], dry_run=False)
    assert len(results) == 1
    assert results[0].target == "claude"
    assert (tmp_path / ".claude" / "skills" / "java_advanced_skill.md").exists()
    assert (tmp_path / ".claude" / "agents" / "java_advanced_agent.md").exists()


def test_orchestrator_run_dry_run_writes_nothing(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_skills_dir(tmp_path)
    make_agents_dir(tmp_path)
    orch = ExportOrchestrator(repo_root=tmp_path)
    results = orch.run(targets=["claude"], skill_filter=[], agent_filter=[], dry_run=True)
    assert not (tmp_path / ".claude").exists()


def test_orchestrator_clean_removes_export_dirs(tmp_path):
    from tools.exporter import ExportOrchestrator
    make_skills_dir(tmp_path)
    make_agents_dir(tmp_path)
    orch = ExportOrchestrator(repo_root=tmp_path)
    orch.run(targets=["claude"], skill_filter=[], agent_filter=[], dry_run=False)
    assert (tmp_path / ".claude").exists()
    orch.clean()
    assert not (tmp_path / ".claude" / "skills").exists()
    assert not (tmp_path / ".claude" / "agents").exists()
```

- [ ] **Step 2: Run — expect ImportError for `ExportOrchestrator`**

```bash
python -m pytest tests/tools/test_exporter.py -v -k "orchestrator"
```

- [ ] **Step 3: Add `ExportOrchestrator` to `tools/exporter.py`**

```python
# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class ExportOrchestrator:
    """Coordinates skill/agent discovery, filtering, and platform export.

    Pipeline:
        1. discover_skills() — scan skills/*.md
        2. discover_agents() — scan agents/**/*.md, skip README.md
        3. filter_skills() / filter_agents() — apply --skills / --agents flags
        4. run each platform exporter
        5. print summary

    Attributes:
        EXPORTERS: Registry mapping platform name → exporter class.
    """

    EXPORTERS: ClassVar[dict[str, type[PlatformExporter]]] = {
        "copilot":  CopilotExporter,
        "claude":   ClaudeExporter,
        "cursor":   CursorExporter,
        "windsurf": WindsurfExporter,
        "gemini":   GeminiExporter,
        "continue": ContinueExporter,
        "openai":   OpenAIExporter,
        "aider":    AiderExporter,
    }

    # Directories cleaned by --clean, one entry per platform skill/agent dir pair
    _CLEAN_DIRS: ClassVar[list[tuple[str, str]]] = [
        (".github/instructions",       "copilot skills"),
        (".github/copilot/agents",     "copilot agents"),
        (".claude/skills",             "claude skills"),
        (".claude/agents",             "claude agents"),
        (".cursor/rules",              "cursor rules"),
        (".windsurf/rules",            "windsurf rules"),
        (".gemini/skills",             "gemini skills"),
        (".gemini/agents",             "gemini agents"),
        (".continue/prompts",          "continue prompts"),
        ("tools/output/openai",        "openai output"),
        (".aider/skills",              "aider skills"),
        (".aider/agents",              "aider agents"),
    ]

    def __init__(self, repo_root: Path) -> None:
        self._repo_root  = repo_root
        self._skills_dir = repo_root / "skills"
        self._agents_dir = repo_root / "agents"

    # ── Discovery ─────────────────────────────────────────────────────────────

    def discover_skills(self) -> list[SkillFile]:
        """Scans skills/ for all .md files and parses them.

        Returns:
            Sorted list of SkillFile instances.

        Raises:
            FileNotFoundError: If the skills/ directory does not exist.
        """
        if not self._skills_dir.exists():
            raise FileNotFoundError(
                f"skills/ directory not found: {self._skills_dir}\n"
                f"Run this script from the repository root or use --repo-root."
            )

        skills: list[SkillFile] = []
        errors: list[str]       = []

        for path in sorted(self._skills_dir.glob("*.md")):
            try:
                skills.append(SkillFile.from_path(path))
            except (ValueError, OSError) as err:
                errors.append(f"  Skipped {path.name}: {err}")

        if errors:
            print("Skill warnings:")
            for msg in errors:
                print(msg)

        return skills

    def discover_agents(self) -> list[AgentFile]:
        """Scans agents/**/ for all .md files (excluding README.md) and parses them.

        Returns:
            Sorted list of AgentFile instances.

        Raises:
            FileNotFoundError: If the agents/ directory does not exist.
        """
        if not self._agents_dir.exists():
            raise FileNotFoundError(
                f"agents/ directory not found: {self._agents_dir}\n"
                f"Run this script from the repository root or use --repo-root."
            )

        agents: list[AgentFile] = []
        errors: list[str]       = []

        for path in sorted(self._agents_dir.rglob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            try:
                agents.append(AgentFile.from_path(path))
            except (ValueError, OSError) as err:
                errors.append(f"  Skipped {path.name}: {err}")

        if errors:
            print("Agent warnings:")
            for msg in errors:
                print(msg)

        return agents

    # ── Filtering ──────────────────────────────────────────────────────────────

    def filter_skills(
        self, skills: list[SkillFile], requested: list[str]
    ) -> list[SkillFile]:
        """Filters skills by slug, name, tags, or applies_to.

        Args:
            skills:    All discovered skills.
            requested: Terms to filter by. Empty list returns all skills.

        Returns:
            Filtered skill list.
        """
        if not requested:
            return skills

        req_lower = [r.lower() for r in requested]
        result = []
        for skill in skills:
            targets = " ".join(
                [skill.slug.lower(), skill.name.lower()]
                + [t.lower() for t in skill.tags]
                + [t.lower() for t in skill.applies_to]
            )
            if any(req in targets for req in req_lower):
                result.append(skill)

        if not result:
            print(f"  No skills matched filter: {requested}")
            print(f"  Available: {[s.slug for s in skills]}")

        return result

    def filter_agents(
        self, agents: list[AgentFile], requested: list[str]
    ) -> list[AgentFile]:
        """Filters agents by slug, name, or role.

        Args:
            agents:    All discovered agents.
            requested: Terms to filter by. Empty list returns all agents.

        Returns:
            Filtered agent list.
        """
        if not requested:
            return agents

        req_lower = [r.lower() for r in requested]
        result = []
        for agent in agents:
            targets = " ".join(
                [agent.slug.lower(), agent.name.lower(), agent.role.lower()]
            )
            if any(req in targets for req in req_lower):
                result.append(agent)

        if not result:
            print(f"  No agents matched filter: {requested}")
            print(f"  Available: {[a.slug for a in agents]}")

        return result

    # ── Clean ──────────────────────────────────────────────────────────────────

    def clean(self) -> None:
        """Removes all previously exported platform directories."""
        for rel_path, label in self._CLEAN_DIRS:
            target = self._repo_root / rel_path
            if target.exists():
                shutil.rmtree(target)
                print(f"  Removed: {rel_path}  ({label})")

    # ── Run ────────────────────────────────────────────────────────────────────

    def run(
        self,
        targets: list[str],
        skill_filter: list[str],
        agent_filter: list[str],
        dry_run: bool = False,
    ) -> list[ExportResult]:
        """Runs the full export pipeline.

        Args:
            targets:      Platform names to export to, or ['all'].
            skill_filter: Skill slugs/tags to include. Empty = all.
            agent_filter: Agent slugs/roles to include. Empty = all.
            dry_run:      If True, generate paths but do not write files.

        Returns:
            List of ExportResult, one per platform.
        """
        all_skills = self.discover_skills()
        all_agents = self.discover_agents()
        skills     = self.filter_skills(all_skills, skill_filter)
        agents     = self.filter_agents(all_agents, agent_filter)

        print(
            f"\n{'DRY RUN — ' if dry_run else ''}"
            f"Exporting {len(skills)} skill(s), {len(agents)} agent(s)"
        )

        if "all" in targets or not targets:
            exporter_classes = list(self.EXPORTERS.values())
        else:
            exporter_classes = []
            for name in targets:
                if name not in self.EXPORTERS:
                    print(f"  Unknown target '{name}'. Valid: {list(self.EXPORTERS)}")
                    continue
                exporter_classes.append(self.EXPORTERS[name])

        results: list[ExportResult] = []
        print(f"Exporting to {len(exporter_classes)} platform(s)...\n")

        for cls in exporter_classes:
            exporter = cls(self._repo_root)
            try:
                result = exporter.export(skills, agents, dry_run=dry_run)
                results.append(result)
                action = "Would write" if dry_run else "Wrote"
                print(
                    f"  [{result.target:10}] {action} "
                    f"{len(result.skill_files)} skill file(s), "
                    f"{len(result.agent_files)} agent file(s)"
                )
            except Exception as err:
                print(f"  [{exporter.target_name:10}] FAILED: {err}")

        self._print_summary(results, dry_run)
        return results

    @staticmethod
    def _print_summary(results: list[ExportResult], dry_run: bool) -> None:
        """Prints a summary table of all export results."""
        print("\n" + "─" * 60)
        print(f"{'DRY RUN ' if dry_run else ''}EXPORT SUMMARY")
        print("─" * 60)
        total_skills = sum(len(r.skill_files) for r in results)
        total_agents = sum(len(r.agent_files) for r in results)
        print(f"  Platforms : {len(results)}")
        print(f"  Skills    : {total_skills} file(s) written")
        print(f"  Agents    : {total_agents} file(s) written")
        print("─" * 60)
```

- [ ] **Step 4: Run all orchestrator tests**

```bash
python -m pytest tests/tools/test_exporter.py -v -k "orchestrator"
```

Expected: All PASS.

- [ ] **Step 5: Run full test suite**

```bash
python -m pytest tests/tools/test_exporter.py -v
```

Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add tools/exporter.py tests/tools/test_exporter.py
git commit -m "feat: add ExportOrchestrator with discovery, filtering, clean, and run"
```

---

## Task 9: CLI entry point

**Files:**
- Modify: `tools/exporter.py` — add `build_argument_parser`, `resolve_repo_root`, `main`
- Modify: `tests/tools/test_exporter.py` — add CLI smoke tests

- [ ] **Step 1: Add CLI tests**

Append to `tests/tools/test_exporter.py`:

```python
# ── CLI ───────────────────────────────────────────────────────────────────────

def test_cli_list_exits_cleanly(tmp_path, capsys):
    from tools.exporter import ExportOrchestrator, build_argument_parser, resolve_repo_root
    make_skills_dir(tmp_path)
    make_agents_dir(tmp_path)
    # Simulate --list by calling orchestrator discover directly
    orch = ExportOrchestrator(repo_root=tmp_path)
    skills = orch.discover_skills()
    agents = orch.discover_agents()
    assert len(skills) > 0
    assert len(agents) > 0


def test_resolve_repo_root_raises_when_no_skills_dir(tmp_path):
    from tools.exporter import resolve_repo_root
    with pytest.raises(SystemExit):
        resolve_repo_root(provided=tmp_path)


def test_resolve_repo_root_succeeds_with_skills_dir(tmp_path):
    from tools.exporter import resolve_repo_root
    (tmp_path / "skills").mkdir()
    result = resolve_repo_root(provided=tmp_path)
    assert result == tmp_path


def test_build_argument_parser_defaults(tmp_path):
    from tools.exporter import build_argument_parser
    parser = build_argument_parser()
    args = parser.parse_args([])
    assert args.target == ["all"]
    assert args.skills == []
    assert args.agents == []
    assert args.dry_run is False
    assert args.clean is False
    assert args.list is False
```

- [ ] **Step 2: Run — expect ImportError for CLI functions**

```bash
python -m pytest tests/tools/test_exporter.py -v -k "cli"
```

- [ ] **Step 3: Add CLI functions to `tools/exporter.py`**

```python
# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def build_argument_parser() -> argparse.ArgumentParser:
    """Builds the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="exporter.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    valid_targets = list(ExportOrchestrator.EXPORTERS.keys())

    parser.add_argument(
        "--target", "-t",
        nargs="+",
        default=["all"],
        choices=[*valid_targets, "all"],
        metavar="TARGET",
        help=(
            f"Platform(s) to export to. "
            f"Options: {', '.join(valid_targets)}, all (default: all)"
        ),
    )

    parser.add_argument(
        "--skills", "-s",
        type=lambda v: [x.strip() for x in v.split(",") if x.strip()],
        default=[],
        metavar="SKILL[,SKILL...]",
        help="Comma-separated skill slugs/tags to include (default: all).",
    )

    parser.add_argument(
        "--agents", "-a",
        type=lambda v: [x.strip() for x in v.split(",") if x.strip()],
        default=[],
        metavar="AGENT[,AGENT...]",
        help="Comma-separated agent slugs/roles to include (default: all).",
    )

    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all discovered skills and agents, then exit.",
    )

    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be exported without writing any files.",
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove all previously exported platform directories and exit.",
    )

    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root path. Auto-detected if omitted.",
    )

    return parser


def resolve_repo_root(provided: Path | None) -> Path:
    """Resolves the repository root path.

    Args:
        provided: Explicitly provided path, or None to auto-detect.

    Returns:
        Absolute path to the repository root.

    Raises:
        SystemExit: If the skills/ directory cannot be found.
    """
    if provided:
        root = provided.resolve()
    else:
        # Script lives at tools/exporter.py → parent of tools/ is the repo root
        root = Path(__file__).resolve().parent.parent

    if not (root / "skills").exists():
        print(f"ERROR: Could not find skills/ directory under {root}")
        print("Run this script from the repository root, or use --repo-root.")
        sys.exit(1)

    return root


def main() -> None:
    """Main entry point."""
    parser      = build_argument_parser()
    args        = parser.parse_args()
    repo_root   = resolve_repo_root(args.repo_root)
    orchestrator = ExportOrchestrator(repo_root)

    # ── --clean ───────────────────────────────────────────────────────────
    if args.clean:
        print("\nCleaning all exported platform files...\n")
        orchestrator.clean()
        print("\nDone.")
        return

    # ── --list ────────────────────────────────────────────────────────────
    if args.list:
        print("\nDiscovered skills:\n")
        try:
            for skill in orchestrator.discover_skills():
                applies = ", ".join(skill.applies_to[:5])
                print(f"  {skill.slug:<45} {skill.name}")
                print(f"  {'':45} applies_to: {applies}\n")
        except FileNotFoundError as err:
            print(f"ERROR: {err}")
            sys.exit(1)

        print("\nDiscovered agents:\n")
        try:
            for agent in orchestrator.discover_agents():
                print(f"  {agent.slug:<45} {agent.name}")
                print(f"  {'':45} role: {agent.role}\n")
        except FileNotFoundError as err:
            print(f"ERROR: {err}")
            sys.exit(1)

        return

    # ── Export ────────────────────────────────────────────────────────────
    try:
        orchestrator.run(
            targets      = args.target,
            skill_filter = args.skills,
            agent_filter = args.agents,
            dry_run      = args.dry_run,
        )
    except FileNotFoundError as err:
        print(f"\nERROR: {err}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExport cancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run all tests**

```bash
python -m pytest tests/tools/test_exporter.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Smoke test against the real repo**

```bash
python tools/exporter.py --dry-run --list
```

Expected: Lists all skills and agents from `skills/` and `agents/`, no errors.

```bash
python tools/exporter.py --dry-run
```

Expected: Prints dry-run summary showing all 8 platforms, no files written.

- [ ] **Step 6: Commit**

```bash
git add tools/exporter.py tests/tools/test_exporter.py
git commit -m "feat: add CLI entry point with --target, --skills, --agents, --list, --dry-run, --clean"
```

---

## Task 10: Delete `skill_exporter.py` and update docs

**Files:**
- Delete: `tools/skill_exporter.py`
- Update: `tools/README.md`
- Update: `CLAUDE.md`

- [ ] **Step 1: Delete `skill_exporter.py`**

```bash
rm tools/skill_exporter.py
```

- [ ] **Step 2: Verify no remaining references to `skill_exporter`**

```bash
grep -r "skill_exporter" . --include="*.md" --include="*.py" --include="*.json"
```

Expected: No matches. If any remain, update those files to reference `exporter.py`.

- [ ] **Step 3: Update `tools/README.md`**

Replace the entire content of `tools/README.md` with:

```markdown
# Tools — Exporter

This directory contains utility scripts for managing and exporting agent skills and agent definitions to various AI assistant platforms.

## exporter.py

Exports skills from `skills/` and agent definitions from `agents/` to platform-native
instruction files. Writes **one file per skill and one file per agent** — no merging.

### Supported Platforms

| Target | Skills output | Agents output | Format |
|--------|---------------|---------------|--------|
| `copilot` | `.github/instructions/<slug>.instructions.md` | `.github/copilot/agents/<slug>.md` | `applyTo: '**'` frontmatter |
| `claude` | `.claude/skills/<slug>.md` | `.claude/agents/<slug>.md` | Clean markdown |
| `cursor` | `.cursor/rules/<slug>.mdc` | `.cursor/rules/agents/<slug>.mdc` | `description/globs/alwaysApply` frontmatter |
| `windsurf` | `.windsurf/rules/<slug>.md` | `.windsurf/rules/agents/<slug>.md` | Clean markdown |
| `gemini` | `.gemini/skills/<slug>.md` | `.gemini/agents/<slug>.md` | Clean markdown |
| `continue` | `.continue/prompts/<slug>.prompt` | `.continue/prompts/agents/<slug>.prompt` | `name/description` frontmatter |
| `openai` | `tools/output/openai/skills/<slug>.txt` | `tools/output/openai/agents/<slug>.txt` | Plain text |
| `aider` | `.aider/skills/<slug>.md` | `.aider/agents/<slug>.md` | Clean markdown |

### Quick Start

```bash
# Export ALL skills and agents to ALL platforms
python tools/exporter.py

# Export to specific platforms only
python tools/exporter.py --target copilot claude

# Export only Java-related skills and developer agents to Cursor
python tools/exporter.py --target cursor --skills java,spring --agents developer

# Dry run — preview all output paths without writing
python tools/exporter.py --dry-run

# List all discovered skills and agents
python tools/exporter.py --list

# Remove all previously exported files
python tools/exporter.py --clean
```

### Arguments

```
--target, -t TARGET [TARGET ...]
  Platforms to export to. Options: copilot, claude, cursor, windsurf,
  gemini, continue, openai, aider, all. Default: all

--skills, -s SKILL[,SKILL...]
  Filter skills by slug, name, tag, or applies_to. Default: all skills.

--agents, -a AGENT[,AGENT...]
  Filter agents by slug, name, or role. Default: all agents.

--list, -l
  List all discovered skills and agents, then exit.

--dry-run, -n
  Show what would be exported without writing files.

--clean
  Remove all exported platform directories and exit.

--repo-root PATH
  Repository root. Auto-detected from script location if omitted.
```

### Source File Requirements

**Skills** (`skills/*.md`) must have YAML frontmatter:

```yaml
---
name: My Skill
version: 1.0
description: One-line summary
applies_to: [java, spring-boot]
tags: [java, patterns]
---
```

**Agents** (`agents/<role>/*.md`) must have YAML frontmatter:

```yaml
---
name: My Agent
version: 1.0
description: One-line summary
skills: [my_skill]
instruction_set: instructions/master_instruction_set.md
intake_form: instructions/my_intake.md
---
```

The `role` field is derived automatically from the agent's parent directory name
(e.g. `agents/developer/` → role is `developer`).

### Maintenance

Run after adding or modifying skills or agents:

```bash
python tools/exporter.py
```
```

- [ ] **Step 4: Update the tool reference in `CLAUDE.md`**

In `CLAUDE.md`, find the `Tools — Skill Exporter` section and update it:

Find:
```
`tools/skill_exporter.py` is a Python utility that exports skills to instruction files for multiple AI platforms:

```bash
# Export all skills to all platforms (GitHub Copilot, Claude, Cursor, etc.)
python tools/skill_exporter.py

# Export specific skills to a specific platform
python tools/skill_exporter.py --skills java,camel,spring --target copilot

# List all available skills
python tools/skill_exporter.py --list
```

**Supported targets:**
- GitHub Copilot: `.github/copilot-instructions.md`
- Claude Code: `.claude/skills_context.md`
- Cursor IDE: `.cursorrules`
- Continue.dev: `.continue/config.json`
- OpenAI API: `tools/output/openai_system_prompt.txt`

See `tools/README.md` for full documentation.
```

Replace with:
```
`tools/exporter.py` is a Python utility that exports skills and agent definitions to platform-native instruction files. Writes one file per skill and one file per agent — no merging.

```bash
# Export all skills and agents to all platforms
python tools/exporter.py

# Export specific skills/agents to specific platforms
python tools/exporter.py --target copilot claude --skills java,spring --agents developer

# List all available skills and agents
python tools/exporter.py --list

# Dry run — preview without writing
python tools/exporter.py --dry-run
```

**Supported platforms:** copilot, claude, cursor, windsurf, gemini, continue, openai, aider

See `tools/README.md` for full documentation.
```

- [ ] **Step 5: Run full test suite one final time**

```bash
python -m pytest tests/tools/test_exporter.py -v
```

Expected: All tests PASS.

- [ ] **Step 6: Run a real export to verify output**

```bash
python tools/exporter.py --dry-run
```

Expected: Lists all 8 platforms, shows skill and agent counts, no errors.

- [ ] **Step 7: Commit everything**

```bash
git add tools/exporter.py tools/README.md CLAUDE.md tests/
git rm tools/skill_exporter.py
git commit -m "feat: replace skill_exporter with unified exporter for skills and agents across 8 platforms"
```
