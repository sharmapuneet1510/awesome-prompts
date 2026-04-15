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
        raw = path.read_text(encoding="utf-8-sig")
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
        # Check for block scalar (>) first, before single-line match, so that
        # `description: >` is not incorrectly captured as the literal string ">".
        block = re.search(rf"^{key}:\s*>\s*\n((?:[ \t]+.+\n?)+)", text, re.MULTILINE)
        if block:
            return " ".join(line.strip() for line in block.group(1).strip().splitlines())

        single = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE)
        if single:
            return single.group(1).strip().strip("'\"")

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
            # Only capture lines that start with whitespace (YAML list items),
            # stopping at the first non-indented line (next key).
            after = text[block_start.end():]
            items: list[str] = []
            for line in after.splitlines():
                if not line:
                    # Skip blank lines (e.g. the newline right after the key)
                    continue
                if not line[0].isspace():
                    # Reached the next top-level key or end of frontmatter
                    break
                stripped = line.lstrip()
                if stripped.startswith("- "):
                    value = stripped[2:].strip().strip("'\"")
                    if value:
                        items.append(value)
            return items

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
        """Output filename for a skill. Override for non-.md extensions."""
        return f"{skill.slug}.md"

    def agent_filename(self, agent: AgentFile) -> str:
        """Output filename for an agent. Override for non-.md extensions."""
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


# ─────────────────────────────────────────────────────────────────────────────
# Platform Exporters
# ─────────────────────────────────────────────────────────────────────────────

class CopilotExporter(PlatformExporter):
    """GitHub Copilot — .github/instructions/ and .github/copilot/agents/"""

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
    """Claude Code — .claude/skills/ and .claude/agents/"""

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


class CursorExporter(PlatformExporter):
    """Cursor IDE — .cursor/rules/*.mdc and .cursor/rules/agents/*.mdc"""

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
    """Windsurf IDE — .windsurf/rules/ and .windsurf/rules/agents/"""

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


class GeminiExporter(PlatformExporter):
    """Gemini CLI — .gemini/skills/ and .gemini/agents/"""

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
    """Continue.dev — .continue/prompts/*.prompt and .continue/prompts/agents/*.prompt"""

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


class OpenAIExporter(PlatformExporter):
    """OpenAI API — tools/output/openai/skills/*.txt and tools/output/openai/agents/*.txt"""

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
    """Aider — .aider/skills/ and .aider/agents/"""

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


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class ExportOrchestrator:
    """Coordinates skill/agent discovery, filtering, and platform export."""

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

    _CLEAN_DIRS: ClassVar[list[str]] = [
        ".github/instructions",
        ".github/copilot/agents",
        ".claude/skills",
        ".claude/agents",
        ".cursor/rules",
        ".windsurf/rules",
        ".gemini/skills",
        ".gemini/agents",
        ".continue/prompts",
        "tools/output/openai",
        ".aider/skills",
        ".aider/agents",
    ]

    def __init__(self, repo_root: Path) -> None:
        self._repo_root  = repo_root
        self._skills_dir = repo_root / "skills"
        self._agents_dir = repo_root / "agents"

    def discover_skills(self) -> list[SkillFile]:
        if not self._skills_dir.exists():
            raise FileNotFoundError(
                f"skills/ directory not found: {self._skills_dir}\n"
                f"Run from the repository root or use --repo-root."
            )
        skills: list[SkillFile] = []
        errors: list[str] = []
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
        if not self._agents_dir.exists():
            raise FileNotFoundError(
                f"agents/ directory not found: {self._agents_dir}\n"
                f"Run from the repository root or use --repo-root."
            )
        agents: list[AgentFile] = []
        errors: list[str] = []
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

    def filter_skills(self, skills: list[SkillFile], requested: list[str]) -> list[SkillFile]:
        if not requested:
            return skills
        req_lower = [r.lower() for r in requested]
        result = [
            s for s in skills
            if any(
                req in " ".join(
                    [s.slug.lower(), s.name.lower()]
                    + [t.lower() for t in s.tags]
                    + [t.lower() for t in s.applies_to]
                )
                for req in req_lower
            )
        ]
        if not result:
            print(f"  No skills matched: {requested}. Available: {[s.slug for s in skills]}")
        return result

    def filter_agents(self, agents: list[AgentFile], requested: list[str]) -> list[AgentFile]:
        if not requested:
            return agents
        req_lower = [r.lower() for r in requested]
        result = [
            a for a in agents
            if any(
                req in " ".join([a.slug.lower(), a.name.lower(), a.role.lower()])
                for req in req_lower
            )
        ]
        if not result:
            print(f"  No agents matched: {requested}. Available: {[a.slug for a in agents]}")
        return result

    def clean(self) -> None:
        for rel in self._CLEAN_DIRS:
            target = self._repo_root / rel
            if target.exists():
                shutil.rmtree(target)
                print(f"  Removed: {rel}")

    def run(
        self,
        targets: list[str],
        skill_filter: list[str],
        agent_filter: list[str],
        dry_run: bool = False,
    ) -> list[ExportResult]:
        all_skills = self.discover_skills()
        all_agents = self.discover_agents()
        skills = self.filter_skills(all_skills, skill_filter)
        agents = self.filter_agents(all_agents, agent_filter)

        print(f"\n{'DRY RUN — ' if dry_run else ''}Exporting {len(skills)} skill(s), {len(agents)} agent(s)")

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
                    f"{len(result.skill_files)} skill(s), "
                    f"{len(result.agent_files)} agent(s)"
                )
            except Exception as err:
                print(f"  [{exporter.target_name:10}] FAILED: {err}")

        self._print_summary(results, dry_run)
        return results

    @staticmethod
    def _print_summary(results: list[ExportResult], dry_run: bool) -> None:
        print("\n" + "─" * 60)
        print(f"{'DRY RUN ' if dry_run else ''}EXPORT SUMMARY")
        print("─" * 60)
        print(f"  Platforms : {len(results)}")
        print(f"  Skills    : {sum(len(r.skill_files) for r in results)} file(s)")
        print(f"  Agents    : {sum(len(r.agent_files) for r in results)} file(s)")
        print("─" * 60)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def build_argument_parser() -> argparse.ArgumentParser:
    valid_targets = list(ExportOrchestrator.EXPORTERS.keys())
    parser = argparse.ArgumentParser(
        prog="exporter.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--target", "-t",
        nargs="+",
        default=["all"],
        choices=[*valid_targets, "all"],
        metavar="TARGET",
        help=f"Platform(s): {', '.join(valid_targets)}, all (default: all)",
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
    parser.add_argument("--list", "-l", action="store_true",
                        help="List all discovered skills and agents, then exit.")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="Preview without writing files.")
    parser.add_argument("--clean", action="store_true",
                        help="Remove all exported platform directories and exit.")
    parser.add_argument("--repo-root", type=Path, default=None,
                        help="Repository root. Auto-detected if omitted.")
    return parser


def resolve_repo_root(provided: Path | None) -> Path:
    if provided:
        root = provided.resolve()
    else:
        root = Path(__file__).resolve().parent.parent
    if not (root / "skills").exists():
        print(f"ERROR: Could not find skills/ directory under {root}")
        print("Run from the repository root or use --repo-root.")
        sys.exit(1)
    return root


def main() -> None:
    parser       = build_argument_parser()
    args         = parser.parse_args()
    repo_root    = resolve_repo_root(args.repo_root)
    orchestrator = ExportOrchestrator(repo_root)

    if args.clean:
        print("\nCleaning all exported platform files...\n")
        orchestrator.clean()
        print("\nDone.")
        return

    if args.list:
        print("\nSkills:\n")
        try:
            for s in orchestrator.discover_skills():
                print(f"  {s.slug:<45} {s.name}")
        except FileNotFoundError as err:
            print(f"ERROR: {err}"); sys.exit(1)
        print("\nAgents:\n")
        try:
            for a in orchestrator.discover_agents():
                print(f"  {a.slug:<45} {a.name}  [{a.role}]")
        except FileNotFoundError as err:
            print(f"ERROR: {err}"); sys.exit(1)
        return

    try:
        orchestrator.run(
            targets      = args.target,
            skill_filter = args.skills,
            agent_filter = args.agents,
            dry_run      = args.dry_run,
        )
    except FileNotFoundError as err:
        print(f"\nERROR: {err}"); sys.exit(1)
    except KeyboardInterrupt:
        print("\nExport cancelled."); sys.exit(0)


if __name__ == "__main__":
    main()
