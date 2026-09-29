"""Parser for YAML+Markdown hybrid instruction format"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from .schema import (
    Instruction,
    InstructionMetadata,
    InstructionSection,
    InstructionCategory,
    InstructionPrecedence,
    InstructionScope,
)


def parse_instruction_file(file_path: Path) -> Instruction:
    """
    Parse a YAML+Markdown hybrid instruction file.

    Expects format:
    ---
    version: "1.0.0"
    description: "..."
    priority: 10
    applicability: ["claude", "openai"]
    precedence: "override"
    scope: "global"
    author: "system"
    deprecated: false
    deprecation_notice: null
    tags: ["core"]
    depends_on: []
    ---

    # Markdown Content Here

    Provider-specific blocks:
    <!-- if: provider=claude -->
    Claude-specific content
    <!-- endif -->

    Args:
        file_path: Path to the instruction file

    Returns:
        Instruction object with parsed metadata, content, and sections

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If YAML frontmatter is invalid or required fields missing
    """
    file_path = Path(file_path)

    # Check file exists
    if not file_path.exists():
        raise FileNotFoundError(f"Instruction file not found: {file_path}")

    # Read file content
    content = file_path.read_text(encoding="utf-8")

    # Extract YAML frontmatter and markdown body
    frontmatter, body = _extract_frontmatter(content)

    # Parse YAML metadata
    try:
        metadata_dict = yaml.safe_load(frontmatter) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML frontmatter: {e}")

    # Create InstructionMetadata with proper defaults
    metadata = _build_metadata(metadata_dict)

    # Parse markdown sections
    sections = _parse_markdown_sections(body)

    # Extract provider variants
    provider_variants = _extract_provider_variants(body)

    # Build Instruction ID from filename and extract name
    instruction_id = file_path.stem.replace("-", "_")
    name = metadata_dict.get("description", instruction_id)

    # Determine category - default to CORE
    category = InstructionCategory.CORE

    # Create and return Instruction object
    instruction = Instruction(
        id=instruction_id,
        name=name,
        category=category,
        metadata=metadata,
        content=body,
        sections=sections,
        provider_variants=provider_variants,
        source_path=str(file_path),
    )

    return instruction


def _extract_frontmatter(content: str) -> Tuple[str, str]:
    """
    Extract YAML frontmatter and markdown body from hybrid format.

    Args:
        content: Full file content with optional YAML frontmatter

    Returns:
        Tuple of (frontmatter, body) strings

    Raises:
        ValueError: If frontmatter is malformed
    """
    # Check if content starts with YAML frontmatter marker
    if not content.startswith("---"):
        # No frontmatter, entire content is body
        return "{}", content.strip()

    # Find closing --- marker
    lines = content.split("\n", 1)
    if len(lines) < 2:
        raise ValueError("Malformed frontmatter: opening --- without closing ---")

    rest = lines[1]
    parts = rest.split("\n---\n", 1)

    if len(parts) != 2:
        raise ValueError("Malformed frontmatter: missing closing ---")

    frontmatter = parts[0]
    body = parts[1].strip()

    return frontmatter, body


def _build_metadata(metadata_dict: Dict[str, Any]) -> InstructionMetadata:
    """
    Build InstructionMetadata from parsed YAML dictionary.

    Args:
        metadata_dict: Parsed YAML metadata

    Returns:
        InstructionMetadata object with proper defaults

    Raises:
        ValueError: If required fields are missing
    """
    version = metadata_dict.get("version", "1.0.0")
    description = metadata_dict.get("description", "")
    priority = metadata_dict.get("priority", 5)
    applicability = metadata_dict.get("applicability", ["claude"])
    precedence_str = metadata_dict.get("precedence", "merge")
    scope_str = metadata_dict.get("scope", "global")
    deprecated = metadata_dict.get("deprecated", False)
    deprecation_notice = metadata_dict.get("deprecation_notice")
    tags = metadata_dict.get("tags", [])
    depends_on = metadata_dict.get("depends_on", [])
    author = metadata_dict.get("author", "system")

    # Convert string enums to enum values
    try:
        precedence = InstructionPrecedence(precedence_str)
    except ValueError:
        precedence = InstructionPrecedence.MERGE

    try:
        scope = InstructionScope(scope_str)
    except ValueError:
        scope = InstructionScope.GLOBAL

    metadata = InstructionMetadata(
        version=version,
        description=description,
        priority=int(priority),
        applicability=list(applicability) if applicability else ["claude"],
        precedence=precedence,
        scope=scope,
        deprecated=bool(deprecated),
        deprecation_notice=deprecation_notice,
        tags=list(tags) if tags else [],
        depends_on=list(depends_on) if depends_on else [],
        author=author,
    )

    return metadata


def _parse_markdown_sections(content: str) -> List[InstructionSection]:
    """
    Extract sections from markdown content using ## (double hash) headings.

    Args:
        content: Markdown body content

    Returns:
        List of InstructionSection objects
    """
    sections = []
    current_heading = None
    current_content_lines = []

    for line in content.split("\n"):
        # Check for section heading (## Level 2)
        if line.startswith("## "):
            # Save previous section if exists
            if current_heading is not None:
                section_content = "\n".join(current_content_lines).strip()
                if section_content:
                    sections.append(
                        InstructionSection(
                            heading=current_heading,
                            content=section_content,
                            metadata=_extract_section_metadata(section_content),
                        )
                    )

            # Start new section
            current_heading = line[3:].strip()  # Remove "## " prefix
            current_content_lines = []
        elif current_heading is not None:
            # Accumulate content for current section
            current_content_lines.append(line)

    # Don't forget the last section
    if current_heading is not None:
        section_content = "\n".join(current_content_lines).strip()
        if section_content:
            sections.append(
                InstructionSection(
                    heading=current_heading,
                    content=section_content,
                    metadata=_extract_section_metadata(section_content),
                )
            )

    return sections


def _extract_section_metadata(content: str) -> Dict[str, Any]:
    """
    Extract metadata comments from section content.

    Metadata comments format: <!-- meta: key = value -->

    Args:
        content: Section content to scan for metadata

    Returns:
        Dictionary of extracted metadata key-value pairs
    """
    metadata = {}

    # Pattern for metadata comments: <!-- meta: key = value -->
    pattern = r"<!--\s*meta:\s*(\w+)\s*=\s*(.+?)\s*-->"
    matches = re.finditer(pattern, content)

    for match in matches:
        key = match.group(1)
        value = match.group(2).strip()

        # Try to parse value as Python literal
        if value.lower() in ("true", "false"):
            metadata[key] = value.lower() == "true"
        elif value.isdigit():
            metadata[key] = int(value)
        else:
            metadata[key] = value

    return metadata


def _extract_provider_variants(content: str) -> Dict[str, Dict[str, Any]]:
    """
    Extract provider-specific variants from markdown.

    Format: <!-- if: provider=X -->...<!-- endif -->

    Args:
        content: Markdown content with provider blocks

    Returns:
        Dictionary mapping provider names to variant data
    """
    variants = {}

    # Pattern for provider blocks: <!-- if: provider=X -->...<!-- endif -->
    pattern = r"<!--\s*if:\s*provider=(\w+)\s*-->(.*?)<!--\s*endif\s*-->"
    matches = re.finditer(pattern, content, re.DOTALL)

    for match in matches:
        provider = match.group(1)
        block_content = match.group(2).strip()

        variants[provider] = {
            "content": block_content,
            "enabled": True,
        }

    return variants
