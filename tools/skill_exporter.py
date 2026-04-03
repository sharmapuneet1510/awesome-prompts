#!/usr/bin/env python3
"""
skill_exporter.py — Exports agent skills to AI assistant instruction formats.

Reads skill files from the skills/ directory and generates instruction files
compatible with GitHub Copilot, Claude Code, Cursor, Continue.dev, and OpenAI.

Usage:
    # Export ALL skills to ALL targets
    python tools/skill_exporter.py

    # Export specific skills to a specific target
    python tools/skill_exporter.py --skills java,camel,pulsar --target copilot

    # Export all skills to a specific target
    python tools/skill_exporter.py --target cursor

    # List all available skills
    python tools/skill_exporter.py --list

    # Dry run — show what would be generated without writing files
    python tools/skill_exporter.py --dry-run

Supported targets:
    copilot   → .github/copilot-instructions.md   (GitHub Copilot)
    claude    → .claude/skills_context.md          (Claude Code)
    cursor    → .cursorrules                        (Cursor IDE)
    continue  → .continue/config.json              (Continue.dev)
    openai    → tools/output/openai_system_prompt.txt (OpenAI / ChatGPT API)
    all       → All of the above (default)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar


# ─────────────────────────────────────────────────────────────────────────────
# Data Model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SkillFile:
    """Represents a single parsed skill markdown file.

    Attributes:
        path:        Absolute path to the source .md file.
        name:        Human-readable name from the YAML frontmatter.
        description: One-line summary from the frontmatter.
        tags:        List of topic tags (e.g. ['java', 'spring', 'camel']).
        applies_to:  List of technology areas this skill covers.
        content:     The full markdown body (frontmatter stripped).
        slug:        Short identifier derived from the file name (e.g. 'java_advanced').
    """

    path: Path
    name: str
    description: str
    tags: list[str]
    applies_to: list[str]
    content: str
    slug: str

    # Regex to match YAML frontmatter block (--- ... ---)
    _FRONTMATTER_RE: ClassVar[re.Pattern] = re.compile(
        r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL
    )

    @classmethod
    def from_path(cls, path: Path) -> "SkillFile":
        """Parses a skill markdown file and returns a SkillFile instance.

        Args:
            path: Path to the .md file to parse.

        Returns:
            A populated SkillFile instance.

        Raises:
            ValueError: If the file has no YAML frontmatter.
            FileNotFoundError: If the path does not exist.
        """
        raw_text = path.read_text(encoding="utf-8")

        # ── Extract YAML frontmatter ──────────────────────────────────────
        match = cls._FRONTMATTER_RE.match(raw_text)
        if not match:
            raise ValueError(
                f"Skill file '{path.name}' is missing YAML frontmatter (--- ... ---). "
                f"All skill files must start with a frontmatter block."
            )

        frontmatter_text = match.group(1)
        body_text = raw_text[match.end():]  # everything after the closing ---

        # ── Parse frontmatter fields ──────────────────────────────────────
        name        = cls._extract_scalar(frontmatter_text, "name",        default=path.stem)
        description = cls._extract_scalar(frontmatter_text, "description", default="")
        tags        = cls._extract_list(frontmatter_text,   "tags")
        applies_to  = cls._extract_list(frontmatter_text,   "applies_to")

        slug = path.stem  # e.g. "java_advanced_skill" → used in output headers

        return cls(
            path=path,
            name=name,
            description=description.strip(),
            tags=tags,
            applies_to=applies_to,
            content=body_text.strip(),
            slug=slug,
        )

    @staticmethod
    def _extract_scalar(text: str, key: str, default: str = "") -> str:
        """Extracts a scalar string value from plain YAML text.

        Handles multi-line values wrapped with > (block scalar).

        Args:
            text:    The raw YAML frontmatter text.
            key:     The key to look up.
            default: Value to return if the key is not found.

        Returns:
            The string value, or default if not found.
        """
        # Match: key: value  (single line)
        single = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE)
        if single:
            return single.group(1).strip().strip("'\"")

        # Match: key: >\n  value lines (block scalar)
        block = re.search(rf"^{key}:\s*>\s*\n((?:  .+\n?)+)", text, re.MULTILINE)
        if block:
            lines = [line.strip() for line in block.group(1).strip().splitlines()]
            return " ".join(lines)

        return default

    @staticmethod
    def _extract_list(text: str, key: str) -> list[str]:
        """Extracts a YAML list from plain YAML text.

        Handles inline lists: [item1, item2]
        and block lists:
          - item1
          - item2

        Args:
            text: The raw YAML frontmatter text.
            key:  The key to look up.

        Returns:
            A list of string values, or an empty list if not found.
        """
        # Inline list: key: [a, b, c]
        inline = re.search(rf"^{key}:\s*\[([^\]]*)\]", text, re.MULTILINE)
        if inline:
            items = [i.strip().strip("'\"") for i in inline.group(1).split(",")]
            return [i for i in items if i]

        # Block list: find the key, then collect "- item" lines that follow
        block_start = re.search(rf"^{key}:\s*$", text, re.MULTILINE)
        if block_start:
            rest  = text[block_start.end():]
            items = re.findall(r"^\s+-\s+(.+)$", rest, re.MULTILINE)
            return [i.strip().strip("'\"") for i in items]

        return []

    def __str__(self) -> str:
        return f"SkillFile(slug={self.slug!r}, name={self.name!r}, tags={self.tags})"


# ─────────────────────────────────────────────────────────────────────────────
# Exporter Base Class
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ExportResult:
    """The result of a single export operation.

    Attributes:
        target:        The target platform name (e.g. 'copilot').
        output_path:   The file that was written (or would be written in dry-run).
        skill_count:   How many skills were included.
        byte_size:     Size of the generated file in bytes.
        dry_run:       True if the file was NOT actually written.
    """
    target: str
    output_path: Path
    skill_count: int
    byte_size: int
    dry_run: bool


class SkillExporter(ABC):
    """Abstract base class for all skill exporters.

    Each subclass knows how to format skills for one AI assistant platform.
    Encapsulates the output file path, format logic, and any platform limits.

    Subclasses must implement:
        - target_name (str property)
        - output_path (Path property)
        - format(skills) -> str
    """

    def __init__(self, repo_root: Path) -> None:
        """Initialises the exporter with the repository root path.

        Args:
            repo_root: Absolute path to the root of the repository.
        """
        self._repo_root = repo_root

    @property
    @abstractmethod
    def target_name(self) -> str:
        """The short name of this target platform (e.g. 'copilot')."""

    @property
    @abstractmethod
    def output_path(self) -> Path:
        """Absolute path where the output file should be written."""

    @abstractmethod
    def format(self, skills: list[SkillFile]) -> str:
        """Formats the given skills into a string for this platform.

        Args:
            skills: The list of skill files to include.

        Returns:
            The full string content to write to the output file.
        """

    def export(self, skills: list[SkillFile], dry_run: bool = False) -> ExportResult:
        """Runs the export: formats skills and writes the output file.

        Args:
            skills:  The skill files to export.
            dry_run: If True, generate content but do not write the file.

        Returns:
            An ExportResult describing what was done.
        """
        content = self.format(skills)

        if not dry_run:
            # Ensure the parent directory exists before writing
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(content, encoding="utf-8")

        return ExportResult(
            target      = self.target_name,
            output_path = self.output_path,
            skill_count = len(skills),
            byte_size   = len(content.encode("utf-8")),
            dry_run     = dry_run,
        )

    # ── Shared formatting helpers ─────────────────────────────────────────

    @staticmethod
    def _build_header(title: str, subtitle: str = "") -> str:
        """Returns a standard comment header for generated files."""
        lines = [
            f"# {title}",
            f"# Generated by skill_exporter.py — do not edit manually.",
            f"# Re-run: python tools/skill_exporter.py",
        ]
        if subtitle:
            lines.insert(1, f"# {subtitle}")
        return "\n".join(lines) + "\n\n"

    @staticmethod
    def _build_skill_section(skill: SkillFile, level: int = 2) -> str:
        """Formats a single skill as a markdown section.

        Args:
            skill: The skill to format.
            level: The heading level (2 = ##, 3 = ###).

        Returns:
            A markdown string for this skill.
        """
        heading  = "#" * level
        applies  = ", ".join(skill.applies_to) if skill.applies_to else "general"
        section  = f"{heading} {skill.name}\n\n"
        section += f"> **Applies to:** {applies}\n\n"
        section += f"{skill.content}\n\n"
        section += "---\n\n"
        return section


# ─────────────────────────────────────────────────────────────────────────────
# Concrete Exporters
# ─────────────────────────────────────────────────────────────────────────────

class CopilotExporter(SkillExporter):
    """Exports skills to GitHub Copilot's instruction file.

    Output: .github/copilot-instructions.md

    GitHub Copilot reads this file automatically for all Copilot interactions
    in the repository. Recommended size: under 100KB.
    """

    @property
    def target_name(self) -> str:
        return "copilot"

    @property
    def output_path(self) -> Path:
        return self._repo_root / ".github" / "copilot-instructions.md"

    def format(self, skills: list[SkillFile]) -> str:
        """Formats skills as a GitHub Copilot instructions file.

        GitHub Copilot reads this and uses it to tailor all code suggestions.
        We structure it with a brief intro, then one section per skill.
        """
        parts: list[str] = []

        # File header
        parts.append(
            "# Copilot Instructions\n\n"
            "<!-- Generated by skill_exporter.py — do not edit manually. -->\n"
            "<!-- Re-run: python tools/skill_exporter.py --target copilot -->\n\n"
            "You are an expert software engineer assisting with this codebase. "
            "Apply the following technology-specific standards and patterns "
            "when generating, reviewing, or explaining code.\n\n"
        )

        # Table of contents
        parts.append("## Skill Index\n\n")
        for skill in skills:
            parts.append(f"- [{skill.name}](#{skill.slug.replace('_', '-')})\n")
        parts.append("\n---\n\n")

        # One section per skill
        for skill in skills:
            parts.append(self._build_skill_section(skill, level=2))

        return "".join(parts)


class ClaudeExporter(SkillExporter):
    """Exports skills to a Claude Code context file.

    Output: .claude/skills_context.md

    This file is loaded by Claude Code as additional context.
    Reference it from CLAUDE.md with a pointer so Claude knows to read it.
    """

    @property
    def target_name(self) -> str:
        return "claude"

    @property
    def output_path(self) -> Path:
        return self._repo_root / ".claude" / "skills_context.md"

    def format(self, skills: list[SkillFile]) -> str:
        """Formats skills as a Claude Code context file."""
        parts: list[str] = []

        parts.append(
            "# Agent Skills Context\n\n"
            "<!-- Generated by skill_exporter.py — do not edit manually. -->\n"
            "<!-- Re-run: python tools/skill_exporter.py --target claude -->\n\n"
            "This file contains advanced technology knowledge used by the coding agents "
            "in this repository. Claude should apply these patterns when helping with "
            "code in the relevant technology areas.\n\n"
        )

        # Skill summary table
        parts.append("## Available Skills\n\n")
        parts.append("| Skill | Applies To |\n")
        parts.append("|-------|------------|\n")
        for skill in skills:
            applies = ", ".join(skill.applies_to[:4]) + ("..." if len(skill.applies_to) > 4 else "")
            parts.append(f"| {skill.name} | `{applies}` |\n")
        parts.append("\n---\n\n")

        # Full content per skill
        for skill in skills:
            parts.append(self._build_skill_section(skill, level=2))

        return "".join(parts)


class CursorExporter(SkillExporter):
    """Exports skills to Cursor's .cursorrules file.

    Output: .cursorrules (repository root)

    Cursor reads this file and applies the rules to all AI interactions
    in the editor. Keep it focused and concise — Cursor works best with
    clear, direct rules rather than long documentation.
    """

    # Cursor works best when the rules file is under ~50KB
    MAX_CONTENT_LENGTH: ClassVar[int] = 50_000

    @property
    def target_name(self) -> str:
        return "cursor"

    @property
    def output_path(self) -> Path:
        return self._repo_root / ".cursorrules"

    def format(self, skills: list[SkillFile]) -> str:
        """Formats skills as a Cursor rules file.

        Cursor expects a plain-text rules file with concise instructions.
        We extract the key rules sections from each skill rather than
        dumping the full documentation.
        """
        parts: list[str] = []

        parts.append(
            "# Cursor Rules — AI Coding Assistant Instructions\n"
            "# Generated by skill_exporter.py — do not edit manually.\n"
            "# Re-run: python tools/skill_exporter.py --target cursor\n\n"
        )

        parts.append(
            "You are an expert software engineer. Follow these technology-specific "
            "standards when writing or reviewing code in this repository.\n\n"
        )

        for skill in skills:
            applies = ", ".join(skill.applies_to) if skill.applies_to else "general"

            # Extract only the "quick reference" / rules sections from each skill
            # These are typically at the end of each skill file
            rules_section = self._extract_rules_section(skill.content)

            parts.append(f"## {skill.name} ({applies})\n\n")
            if rules_section:
                parts.append(rules_section)
            else:
                # Fallback: first 1500 characters of the skill
                parts.append(skill.content[:1500].strip())
                parts.append("\n")
            parts.append("\n---\n\n")

        content = "".join(parts)

        # Warn if the file is too large for Cursor
        if len(content.encode("utf-8")) > self.MAX_CONTENT_LENGTH:
            print(
                f"  ⚠  WARNING: .cursorrules is large "
                f"({len(content.encode('utf-8')) // 1024}KB). "
                f"Consider exporting fewer skills with --skills flag."
            )

        return content

    @staticmethod
    def _extract_rules_section(content: str) -> str:
        """Extracts the Quick Reference / Code Quality Rules section from skill content.

        Args:
            content: The full skill markdown content.

        Returns:
            The extracted rules section, or empty string if not found.
        """
        # Look for sections like "## 7. Code Quality Rules" or "## Quick Reference"
        patterns = [
            r"(##[^#].*?(?:Quality Rules|Quick Reference|Rules|Standards|Checklist).*?\n)(.*?)(?=\n##|\Z)",
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return (match.group(1) + match.group(2)).strip()[:2000]
        return ""


class ContinueExporter(SkillExporter):
    """Exports skills to Continue.dev's configuration.

    Output: .continue/config.json

    Continue.dev uses a JSON config file. We add skills as system prompt
    context in the 'systemMessage' field of the default model config.
    """

    @property
    def target_name(self) -> str:
        return "continue"

    @property
    def output_path(self) -> Path:
        return self._repo_root / ".continue" / "config.json"

    def format(self, skills: list[SkillFile]) -> str:
        """Formats skills as a Continue.dev config.json file.

        Merges skills into the systemMessage of the Continue config.
        If a config.json already exists, preserves existing settings
        and only updates the systemMessage.
        """
        system_message = self._build_system_message(skills)

        config: dict = {}

        # If a config already exists, load it and preserve its settings
        if self.output_path.exists():
            try:
                existing = json.loads(self.output_path.read_text(encoding="utf-8"))
                config.update(existing)
            except json.JSONDecodeError:
                pass  # corrupted config — start fresh

        # Update the system message
        if "models" not in config:
            config["models"] = [
                {
                    "title": "Claude Sonnet",
                    "provider": "anthropic",
                    "model": "claude-sonnet-4-6",
                }
            ]

        config["systemMessage"] = system_message
        config["_generated_by"] = "skill_exporter.py — do not edit manually"

        return json.dumps(config, indent=2)

    def _build_system_message(self, skills: list[SkillFile]) -> str:
        """Builds the system message text from all skills."""
        lines = [
            "You are an expert software engineer assisting with this codebase.",
            "Apply the following technology standards when writing or reviewing code.",
            "",
        ]
        for skill in skills:
            applies = ", ".join(skill.applies_to) if skill.applies_to else "general"
            lines.append(f"--- {skill.name} ({applies}) ---")
            # Include a condensed version of each skill (first 2000 chars)
            condensed = skill.content[:2000].strip()
            lines.append(condensed)
            lines.append("")

        return "\n".join(lines)


class OpenAIExporter(SkillExporter):
    """Exports skills as an OpenAI API system prompt.

    Output: tools/output/openai_system_prompt.txt
            tools/output/openai_system_prompt.json  (with metadata)

    Use the .txt content as the system message when calling the OpenAI API
    or ChatGPT custom instructions. Also compatible with Anthropic Claude API.
    """

    @property
    def target_name(self) -> str:
        return "openai"

    @property
    def output_path(self) -> Path:
        return self._repo_root / "tools" / "output" / "openai_system_prompt.txt"

    def format(self, skills: list[SkillFile]) -> str:
        """Formats skills as an OpenAI system prompt string."""
        lines = [
            "You are an expert software engineer.",
            "Apply the following technology-specific standards when writing, "
            "reviewing, or explaining code.",
            "",
            "=" * 70,
            "",
        ]

        for skill in skills:
            applies = ", ".join(skill.applies_to) if skill.applies_to else "general"
            lines.append(f"SKILL: {skill.name.upper()}")
            lines.append(f"APPLIES TO: {applies}")
            lines.append("-" * 40)
            lines.append(skill.content.strip())
            lines.append("")
            lines.append("=" * 70)
            lines.append("")

        return "\n".join(lines)

    def export(self, skills: list[SkillFile], dry_run: bool = False) -> ExportResult:
        """Exports the system prompt in both .txt and .json formats."""
        result = super().export(skills, dry_run)

        # Also write a JSON version with metadata
        json_path = self.output_path.with_suffix(".json")
        json_content = json.dumps(
            {
                "_generated_by": "skill_exporter.py",
                "skill_count": len(skills),
                "skills": [
                    {"slug": s.slug, "name": s.name, "applies_to": s.applies_to}
                    for s in skills
                ],
                "system_prompt": self.format(skills),
            },
            indent=2,
        )

        if not dry_run:
            json_path.write_text(json_content, encoding="utf-8")
            print(f"  ✓  Also wrote: {json_path.relative_to(self._repo_root)}")

        return result


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class ExportOrchestrator:
    """Coordinates discovering skills, filtering, and running exporters.

    This is the main entry point for the export pipeline:
    1. Discover all skill .md files in the skills/ directory
    2. Parse each file into a SkillFile
    3. Filter by the requested skill slugs (if any)
    4. Run each requested exporter
    5. Print a summary report

    Attributes:
        repo_root:  The root of the repository.
        skills_dir: Path to the skills/ directory.
    """

    # Registry of all available exporters: slug → class
    EXPORTERS: ClassVar[dict[str, type[SkillExporter]]] = {
        "copilot":  CopilotExporter,
        "claude":   ClaudeExporter,
        "cursor":   CursorExporter,
        "continue": ContinueExporter,
        "openai":   OpenAIExporter,
    }

    def __init__(self, repo_root: Path) -> None:
        """Initialises the orchestrator.

        Args:
            repo_root: Absolute path to the repository root.
        """
        self._repo_root  = repo_root
        self._skills_dir = repo_root / "skills"

    def discover_skills(self) -> list[SkillFile]:
        """Discovers and parses all skill .md files in the skills/ directory.

        Returns:
            A list of SkillFile instances, sorted alphabetically by slug.

        Raises:
            FileNotFoundError: If the skills/ directory does not exist.
        """
        if not self._skills_dir.exists():
            raise FileNotFoundError(
                f"Skills directory not found: {self._skills_dir}\n"
                f"Run this script from the repository root."
            )

        skill_files = sorted(self._skills_dir.glob("*.md"))
        if not skill_files:
            raise FileNotFoundError(
                f"No .md skill files found in {self._skills_dir}"
            )

        skills: list[SkillFile] = []
        errors: list[str]       = []

        for path in skill_files:
            try:
                skill = SkillFile.from_path(path)
                skills.append(skill)
            except (ValueError, OSError) as err:
                errors.append(f"  ✗  Skipped {path.name}: {err}")

        if errors:
            print("Warnings during skill discovery:")
            for error in errors:
                print(error)

        return skills

    def filter_skills(
        self, skills: list[SkillFile], requested: list[str]
    ) -> list[SkillFile]:
        """Filters the skill list to only those matching the requested slugs.

        Matching is case-insensitive and checks slug, name, and tags.

        Args:
            skills:    All discovered skills.
            requested: The list of slugs/tags to filter by.

        Returns:
            The filtered list. If requested is empty, returns all skills.
        """
        if not requested:
            return skills

        requested_lower = [r.lower() for r in requested]
        filtered: list[SkillFile] = []

        for skill in skills:
            # Match against: slug, name, or any tag/applies_to entry
            search_targets = (
                [skill.slug.lower(), skill.name.lower()]
                + [t.lower() for t in skill.tags]
                + [t.lower() for t in skill.applies_to]
            )
            if any(req in " ".join(search_targets) for req in requested_lower):
                filtered.append(skill)

        if not filtered:
            print(f"⚠  No skills matched the filter: {requested}")
            print(f"   Available slugs: {[s.slug for s in skills]}")

        return filtered

    def run(
        self,
        targets: list[str],
        skill_filter: list[str],
        dry_run: bool = False,
    ) -> list[ExportResult]:
        """Runs the full export pipeline.

        Args:
            targets:      List of target platform names, or ['all'].
            skill_filter: List of skill slugs/tags to include, or [] for all.
            dry_run:      If True, generate content without writing files.

        Returns:
            A list of ExportResult objects, one per target.
        """
        # ── Step 1: Discover and filter skills ───────────────────────────
        all_skills = self.discover_skills()
        skills     = self.filter_skills(all_skills, skill_filter)

        print(f"\n{'DRY RUN — ' if dry_run else ''}Exporting {len(skills)} skills:")
        for skill in skills:
            print(f"  • {skill.name}  ({skill.slug})")

        # ── Step 2: Resolve target exporters ─────────────────────────────
        if "all" in targets or not targets:
            exporter_classes = list(self.EXPORTERS.values())
        else:
            exporter_classes = []
            for target in targets:
                if target not in self.EXPORTERS:
                    print(f"  ✗  Unknown target '{target}'. "
                          f"Valid: {list(self.EXPORTERS.keys())}")
                    continue
                exporter_classes.append(self.EXPORTERS[target])

        # ── Step 3: Run each exporter ─────────────────────────────────────
        results: list[ExportResult] = []
        print(f"\nExporting to {len(exporter_classes)} target(s)...\n")

        for exporter_class in exporter_classes:
            exporter = exporter_class(self._repo_root)
            try:
                result = exporter.export(skills, dry_run=dry_run)
                results.append(result)

                output_rel = result.output_path.relative_to(self._repo_root)
                size_kb    = result.byte_size / 1024
                action     = "Would write" if dry_run else "Wrote"
                print(f"  ✓  [{result.target:10}]  {action}: {output_rel}  "
                      f"({size_kb:.1f} KB,  {result.skill_count} skills)")

            except Exception as err:
                print(f"  ✗  [{exporter.target_name:10}]  FAILED: {err}")

        # ── Step 4: Print summary ─────────────────────────────────────────
        self._print_summary(results, dry_run)
        return results

    @staticmethod
    def _print_summary(results: list[ExportResult], dry_run: bool) -> None:
        """Prints a summary of the export results."""
        print("\n" + "─" * 60)
        print(f"{'DRY RUN ' if dry_run else ''}EXPORT SUMMARY")
        print("─" * 60)
        print(f"  Targets processed : {len(results)}")
        total_kb = sum(r.byte_size for r in results) / 1024
        print(f"  Total output size : {total_kb:.1f} KB")

        if not dry_run:
            print("\n  Generated files:")
            for result in results:
                print(f"    • {result.output_path}")

        print("─" * 60)


# ─────────────────────────────────────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def build_argument_parser() -> argparse.ArgumentParser:
    """Builds and returns the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="skill_exporter.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--target", "-t",
        nargs="+",
        default=["all"],
        choices=[*ExportOrchestrator.EXPORTERS.keys(), "all"],
        metavar="TARGET",
        help=(
            "Target platform(s) to export to. "
            f"Options: {', '.join(ExportOrchestrator.EXPORTERS.keys())}, all (default: all)"
        ),
    )

    parser.add_argument(
        "--skills", "-s",
        type=lambda v: [s.strip() for s in v.split(",") if s.strip()],
        default=[],
        metavar="SKILL[,SKILL...]",
        help=(
            "Comma-separated list of skill slugs or tags to include. "
            "E.g. --skills java,camel,pulsar  (default: all skills)"
        ),
    )

    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available skills and exit.",
    )

    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be generated without writing any files.",
    )

    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help=(
            "Path to the repository root. "
            "Defaults to the parent directory of this script's directory."
        ),
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
        # Script is at tools/skill_exporter.py → parent is the repo root
        script_dir = Path(__file__).resolve().parent
        root = script_dir.parent

    if not (root / "skills").exists():
        print(f"ERROR: Could not find skills/ directory under {root}")
        print("Run this script from the repository root, or use --repo-root.")
        sys.exit(1)

    return root


def main() -> None:
    """Main entry point for the skill exporter CLI."""
    parser = build_argument_parser()
    args   = parser.parse_args()

    repo_root    = resolve_repo_root(args.repo_root)
    orchestrator = ExportOrchestrator(repo_root)

    # ── --list mode ───────────────────────────────────────────────────────
    if args.list:
        print("\nAvailable skills:\n")
        try:
            skills = orchestrator.discover_skills()
            for skill in skills:
                applies = ", ".join(skill.applies_to[:5])
                print(f"  {skill.slug:<40} {skill.name}")
                print(f"  {'':40} Applies to: {applies}")
                print()
        except FileNotFoundError as err:
            print(f"ERROR: {err}")
            sys.exit(1)
        return

    # ── Export mode ───────────────────────────────────────────────────────
    try:
        orchestrator.run(
            targets      = args.target,
            skill_filter = args.skills,
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
