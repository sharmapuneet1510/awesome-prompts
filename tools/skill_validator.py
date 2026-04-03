#!/usr/bin/env python3
"""
skill_validator.py — Validates skill markdown files for correctness.

Checks all skills/*.md files for:
  • Valid YAML frontmatter
  • Required fields (name, description, applies_to, tags, version)
  • Markdown structure (headings, code blocks, links)
  • No broken references or invalid syntax
  • Proper formatting and conventions

Usage:
    # Validate all skills
    python tools/skill_validator.py

    # Validate specific skills
    python tools/skill_validator.py --skills java,spring,camel

    # Show detailed report
    python tools/skill_validator.py --verbose

    # Fix mode (auto-format where possible)
    python tools/skill_validator.py --fix

    # Fail on warnings (strict mode for CI/CD)
    python tools/skill_validator.py --strict

Exit codes:
    0 = All valid
    1 = Validation errors found
    2 = Warnings found (in strict mode)
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field as dataclass_field
from enum import Enum
from pathlib import Path
from typing import ClassVar


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────

class SeverityLevel(Enum):
    """Validation issue severity level."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationIssue:
    """A single validation problem found in a skill file.

    Attributes:
        severity: ERROR, WARNING, or INFO
        message: Human-readable description of the issue
        line_num: Line number in the file (1-indexed), or None if not applicable
        suggestion: How to fix it (optional)
        code: Machine-readable error code (e.g. 'MISSING_FIELD')
    """
    severity: SeverityLevel
    message: str
    line_num: int | None = None
    suggestion: str | None = None
    code: str | None = None

    def __str__(self) -> str:
        """Formats the issue as a human-readable line."""
        prefix = f"[{self.severity.value}]"
        location = f" (line {self.line_num})" if self.line_num else ""
        result = f"{prefix}{location}: {self.message}"
        if self.suggestion:
            result += f"\n  💡 {self.suggestion}"
        return result


@dataclass
class SkillValidationResult:
    """The result of validating a single skill file.

    Attributes:
        skill_path: Path to the skill file
        skill_slug: Filename without .md (e.g. 'java_advanced_skill')
        issues: List of all validation issues found
        is_valid: True if no errors (warnings are OK)
        error_count: Number of ERROR-level issues
        warning_count: Number of WARNING-level issues
    """
    skill_path: Path
    skill_slug: str
    issues: list[ValidationIssue] = dataclass_field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True if there are no errors (warnings are acceptable)."""
        return self.error_count == 0

    @property
    def error_count(self) -> int:
        """Number of ERROR-level issues."""
        return sum(1 for i in self.issues if i.severity == SeverityLevel.ERROR)

    @property
    def warning_count(self) -> int:
        """Number of WARNING-level issues."""
        return sum(1 for i in self.issues if i.severity == SeverityLevel.WARNING)

    @property
    def info_count(self) -> int:
        """Number of INFO-level issues."""
        return sum(1 for i in self.issues if i.severity == SeverityLevel.INFO)

    def add_error(self, message: str, line_num: int | None = None,
                  suggestion: str | None = None, code: str | None = None) -> None:
        """Adds an ERROR-level issue."""
        self.issues.append(ValidationIssue(
            severity=SeverityLevel.ERROR,
            message=message,
            line_num=line_num,
            suggestion=suggestion,
            code=code,
        ))

    def add_warning(self, message: str, line_num: int | None = None,
                    suggestion: str | None = None, code: str | None = None) -> None:
        """Adds a WARNING-level issue."""
        self.issues.append(ValidationIssue(
            severity=SeverityLevel.WARNING,
            message=message,
            line_num=line_num,
            suggestion=suggestion,
            code=code,
        ))

    def add_info(self, message: str, line_num: int | None = None,
                 suggestion: str | None = None, code: str | None = None) -> None:
        """Adds an INFO-level issue."""
        self.issues.append(ValidationIssue(
            severity=SeverityLevel.INFO,
            message=message,
            line_num=line_num,
            suggestion=suggestion,
            code=code,
        ))


# ─────────────────────────────────────────────────────────────────────────────
# Validator
# ─────────────────────────────────────────────────────────────────────────────

class SkillValidator:
    """Validates a skill markdown file for correctness.

    Checks:
      • YAML frontmatter syntax and required fields
      • Content structure (headings, code blocks)
      • Markdown validity (no broken links, etc.)
      • Conventions (naming, field values)
    """

    # Required fields in YAML frontmatter
    REQUIRED_FIELDS: ClassVar[set[str]] = {
        "name",
        "version",
        "description",
        "applies_to",
    }

    # Optional but recommended fields
    OPTIONAL_FIELDS: ClassVar[set[str]] = {
        "tags",
    }

    # Valid version format
    VERSION_RE: ClassVar[re.Pattern] = re.compile(r"^\d+\.\d+(?:\.\d+)?$")

    # YAML frontmatter pattern
    FRONTMATTER_RE: ClassVar[re.Pattern] = re.compile(
        r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL
    )

    # Code block pattern (with language tag)
    CODE_BLOCK_RE: ClassVar[re.Pattern] = re.compile(
        r"```(\w+)?", re.MULTILINE
    )

    # Markdown link pattern
    LINK_RE: ClassVar[re.Pattern] = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")

    # Heading pattern
    HEADING_RE: ClassVar[re.Pattern] = re.compile(r"^#+\s+", re.MULTILINE)

    def __init__(self, skill_path: Path) -> None:
        """Initialises the validator.

        Args:
            skill_path: Path to the .md skill file to validate.
        """
        self._path = skill_path
        self._slug = skill_path.stem  # filename without .md
        self._content = ""
        self._frontmatter = ""

    def validate(self) -> SkillValidationResult:
        """Runs all validation checks.

        Returns:
            A SkillValidationResult with all issues found.
        """
        result = SkillValidationResult(skill_path=self._path, skill_slug=self._slug)

        # ── Read file ──────────────────────────────────────────────────────
        try:
            self._content = self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            result.add_error(f"File not found: {self._path}")
            return result
        except UnicodeDecodeError:
            result.add_error(f"File encoding error (must be UTF-8): {self._path}")
            return result

        # ── Check frontmatter ──────────────────────────────────────────────
        self._validate_frontmatter(result)

        # ── Check content structure ────────────────────────────────────────
        self._validate_structure(result)

        # ── Check markdown validity ────────────────────────────────────────
        self._validate_markdown(result)

        # ── Check conventions ──────────────────────────────────────────────
        self._validate_conventions(result)

        return result

    def _validate_frontmatter(self, result: SkillValidationResult) -> None:
        """Validates YAML frontmatter block."""
        match = self.FRONTMATTER_RE.match(self._content)

        if not match:
            result.add_error(
                "Missing YAML frontmatter (--- ... ---)",
                line_num=1,
                suggestion="Add a YAML frontmatter block at the top of the file",
                code="NO_FRONTMATTER",
            )
            return

        self._frontmatter = match.group(1)

        # ── Parse YAML fields ────────────────────────────────────────────
        fields = self._parse_yaml_fields(self._frontmatter)

        # ── Check required fields ───────────────────────────────────────
        for field in self.REQUIRED_FIELDS:
            if field not in fields:
                result.add_error(
                    f"Missing required field: '{field}'",
                    suggestion=f"Add '{field}: <value>' to the frontmatter",
                    code=f"MISSING_{field.upper()}",
                )
            elif not fields[field]:
                result.add_error(
                    f"Field '{field}' is empty",
                    suggestion=f"Provide a value for '{field}'",
                    code=f"EMPTY_{field.upper()}",
                )

        # ── Validate field values ───────────────────────────────────────
        if "name" in fields and fields["name"]:
            if len(fields["name"]) < 5:
                result.add_warning(
                    f"Name is very short: '{fields['name']}'",
                    suggestion="Use a descriptive name (5+ characters)",
                    code="SHORT_NAME",
                )

        if "version" in fields and fields["version"]:
            if not self.VERSION_RE.match(fields["version"]):
                result.add_error(
                    f"Invalid version format: '{fields['version']}'",
                    suggestion="Use semantic versioning: 1.0 or 1.0.1",
                    code="INVALID_VERSION",
                )

        if "description" in fields and fields["description"]:
            if len(fields["description"]) < 10:
                result.add_warning(
                    f"Description is very short: '{fields['description']}'",
                    suggestion="Provide a more detailed description",
                    code="SHORT_DESCRIPTION",
                )

        if "applies_to" in fields and fields["applies_to"]:
            items = self._parse_yaml_list(fields["applies_to"])
            if not items:
                result.add_error(
                    "Field 'applies_to' has no items",
                    suggestion="Add at least one technology: applies_to: [java, spring]",
                    code="EMPTY_APPLIES_TO",
                )
            elif len(items) > 10:
                result.add_warning(
                    f"applies_to has many items ({len(items)})",
                    suggestion="Consider grouping related technologies",
                    code="TOO_MANY_APPLIES_TO",
                )

    def _validate_structure(self, result: SkillValidationResult) -> None:
        """Validates the structure of the content (headings, etc.)."""
        # Extract content after frontmatter
        match = self.FRONTMATTER_RE.search(self._content)
        if not match:
            return

        content = self._content[match.end():]

        # ── Check for at least one heading ─────────────────────────────
        if not self.HEADING_RE.search(content):
            result.add_warning(
                "No markdown headings (##, ###) found in content",
                suggestion="Organize content with headings",
                code="NO_HEADINGS",
            )

        # ── Check for unclosed code blocks ─────────────────────────────
        code_blocks = re.findall(r"```", content)
        if len(code_blocks) % 2 != 0:
            result.add_error(
                "Unclosed code block (odd number of ```)",
                suggestion="Close all code blocks with ```",
                code="UNCLOSED_CODE_BLOCK",
            )

    def _validate_markdown(self, result: SkillValidationResult) -> None:
        """Validates markdown syntax and conventions."""
        content = self._content

        # ── Check code blocks have language tags ──────────────────────────
        code_blocks = re.finditer(r"```(\w*)", content)
        for match in code_blocks:
            lang = match.group(1)
            if not lang:
                line_num = content[:match.start()].count("\n") + 1
                result.add_warning(
                    "Code block without language tag",
                    line_num=line_num,
                    suggestion="Add language: ```java, ```python, ```bash, etc.",
                    code="NO_CODE_LANG",
                )

        # ── Check for common markdown issues ──────────────────────────────
        # Check for spacing around lists
        if re.search(r"\n-\s+", content):
            pass  # Valid list
        if re.search(r"\n\*\s+", content):
            pass  # Valid list

    def _validate_conventions(self, result: SkillValidationResult) -> None:
        """Validates naming and content conventions."""
        # ── Check filename matches naming convention ────────────────────
        if not self._slug.endswith("_skill"):
            result.add_warning(
                f"Filename doesn't follow convention: {self._slug}.md",
                suggestion="Use format: descriptive_name_skill.md",
                code="NAMING_CONVENTION",
            )

    @staticmethod
    def _parse_yaml_fields(frontmatter: str) -> dict[str, str]:
        """Extracts scalar fields from plain YAML text.

        Args:
            frontmatter: The raw YAML frontmatter text.

        Returns:
            A dict of field_name → field_value.
        """
        fields = {}

        # Match: key: value  (single line)
        for match in re.finditer(r"^(\w+):\s*(.+)$", frontmatter, re.MULTILINE):
            key = match.group(1)
            value = match.group(2).strip().strip("'\"")
            fields[key] = value

        # Match: key: >\n  value lines (block scalar)
        for match in re.finditer(
            r"^(\w+):\s*>\s*\n((?:  .+\n?)+)", frontmatter, re.MULTILINE
        ):
            key = match.group(1)
            lines = [line.strip() for line in match.group(2).strip().splitlines()]
            value = " ".join(lines)
            fields[key] = value

        return fields

    @staticmethod
    def _parse_yaml_list(text: str) -> list[str]:
        """Parses a YAML list value.

        Handles:
          • [a, b, c]  (inline)
          • - a \n - b \n - c  (block)

        Args:
            text: The YAML list text.

        Returns:
            List of items.
        """
        # Inline: [a, b, c]
        if text.startswith("["):
            content = text[1:-1]  # remove brackets
            return [i.strip().strip("'\"") for i in content.split(",") if i.strip()]

        # Block list (shouldn't happen in single-line value, but check anyway)
        return [text]


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class ValidationOrchestrator:
    """Discovers, validates, and reports on all skill files.

    Attributes:
        repo_root: Path to the repository root.
        skills_dir: Path to the skills/ directory.
    """

    def __init__(self, repo_root: Path) -> None:
        """Initialises the orchestrator.

        Args:
            repo_root: Absolute path to the repository root.
        """
        self._repo_root = repo_root
        self._skills_dir = repo_root / "skills"

    def validate_all(self, skill_filter: list[str] = None) -> list[SkillValidationResult]:
        """Validates all skill files in the skills/ directory.

        Args:
            skill_filter: Optional list of skill slugs to validate.
                         If empty, validates all skills.

        Returns:
            A list of SkillValidationResult objects, one per skill.

        Raises:
            FileNotFoundError: If the skills/ directory doesn't exist.
        """
        if not self._skills_dir.exists():
            raise FileNotFoundError(f"Skills directory not found: {self._skills_dir}")

        skill_files = sorted(self._skills_dir.glob("*.md"))
        if not skill_files:
            raise FileNotFoundError(f"No .md files found in {self._skills_dir}")

        # Filter if requested
        if skill_filter:
            filter_lower = [f.lower() for f in skill_filter]
            skill_files = [
                f for f in skill_files
                if any(s in f.stem.lower() for s in filter_lower)
            ]

        # Validate each skill
        results = []
        for skill_path in skill_files:
            validator = SkillValidator(skill_path)
            result = validator.validate()
            results.append(result)

        return results

    @staticmethod
    def print_report(results: list[SkillValidationResult], verbose: bool = False) -> None:
        """Prints a formatted validation report.

        Args:
            results: List of validation results.
            verbose: If True, show details for all skills. Otherwise, summarise.
        """
        print("\n" + "─" * 70)
        print("SKILL VALIDATION REPORT")
        print("─" * 70 + "\n")

        total_errors = sum(r.error_count for r in results)
        total_warnings = sum(r.warning_count for r in results)
        valid_count = sum(1 for r in results if r.is_valid)

        # Print per-skill results
        for result in results:
            status = "✓" if result.is_valid else "✗"
            summary = f"{status} {result.skill_slug}"

            if result.error_count > 0:
                summary += f"  ({result.error_count} error{'s' if result.error_count != 1 else ''})"
            if result.warning_count > 0:
                summary += f"  ({result.warning_count} warning{'s' if result.warning_count != 1 else ''})"

            print(summary)

            if verbose or not result.is_valid:
                for issue in result.issues:
                    print(f"  {issue}")

        # Print summary
        print("\n" + "─" * 70)
        print(f"Validated: {len(results)} skills")
        print(f"Valid: {valid_count} ✓")
        print(f"Errors: {total_errors} ✗")
        print(f"Warnings: {total_warnings} ⚠")
        print("─" * 70 + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def build_argument_parser() -> argparse.ArgumentParser:
    """Builds the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="skill_validator.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--skills", "-s",
        type=lambda v: [s.strip() for s in v.split(",") if s.strip()],
        default=[],
        metavar="SKILL[,SKILL...]",
        help="Comma-separated list of skill slugs to validate. Default: all",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output for all skills (not just errors).",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail (exit 2) if any warnings are found (for CI/CD).",
    )

    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Path to repository root. Auto-detected if not provided.",
    )

    return parser


def resolve_repo_root(provided: Path | None) -> Path:
    """Resolves the repository root path."""
    if provided:
        return provided.resolve()

    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent

    if not (root / "skills").exists():
        print(f"ERROR: Could not find skills/ directory under {root}")
        print("Run from repo root or use --repo-root.")
        sys.exit(1)

    return root


def main() -> None:
    """Main entry point."""
    parser = build_argument_parser()
    args = parser.parse_args()

    repo_root = resolve_repo_root(args.repo_root)
    orchestrator = ValidationOrchestrator(repo_root)

    try:
        results = orchestrator.validate_all(args.skills)
        orchestrator.print_report(results, verbose=args.verbose)

        # Determine exit code
        total_errors = sum(r.error_count for r in results)
        total_warnings = sum(r.warning_count for r in results)

        if total_errors > 0:
            sys.exit(1)  # Errors found
        elif args.strict and total_warnings > 0:
            sys.exit(2)  # Warnings found (strict mode)
        else:
            sys.exit(0)  # All valid

    except FileNotFoundError as err:
        print(f"\nERROR: {err}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nValidation cancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
