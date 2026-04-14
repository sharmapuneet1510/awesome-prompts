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
