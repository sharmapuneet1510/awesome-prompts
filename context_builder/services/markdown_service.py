"""MarkdownService: Markdown generation and formatting utilities for RAG and documentation."""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class MarkdownService:
    """Generate and format markdown documents."""

    def __init__(self):
        """Initialize MarkdownService."""
        self.logger = logging.getLogger(__name__)

    def create_document(
        self,
        title: str,
        sections: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Create a markdown document with title and sections.

        Args:
            title: Document title
            sections: List of section dicts with 'heading', 'level', 'content'
            metadata: Optional metadata dict for front matter

        Returns:
            Markdown document as string
        """
        lines = []

        # Add front matter if metadata provided
        if metadata:
            lines.append("---")
            for key, value in metadata.items():
                lines.append(f"{key}: {value}")
            lines.append("---")
            lines.append("")

        # Add title
        lines.append(f"# {title}")
        lines.append("")

        # Add sections
        if sections:
            for section in sections:
                heading = section.get("heading", "")
                level = section.get("level", 2)
                content = section.get("content", "")

                heading_markdown = "#" * level + " " + heading
                lines.append(heading_markdown)
                lines.append("")
                lines.append(content)
                lines.append("")

        return "\n".join(lines)

    def add_table_of_contents(self, document: str) -> str:
        """
        Add table of contents to markdown document.

        Args:
            document: Markdown document

        Returns:
            Document with TOC added after title
        """
        lines = document.split("\n")
        toc_lines = []

        # Find all headings and build TOC
        for line in lines:
            if line.startswith("##"):
                # Extract heading level and text
                level = len(line) - len(line.lstrip("#"))
                text = line.lstrip("#").strip()
                indent = "  " * (level - 2)
                anchor = text.lower().replace(" ", "-")
                toc_lines.append(f"{indent}- [{text}](#{anchor})")

        if not toc_lines:
            return document

        # Find position to insert TOC (after title and first empty line)
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith("# "):
                insert_pos = i + 2
                break

        # Insert TOC
        lines.insert(insert_pos, "## Table of Contents")
        lines.insert(insert_pos + 1, "")
        for toc_line in toc_lines:
            lines.insert(insert_pos + 2, toc_line)
            insert_pos += 1
        lines.insert(insert_pos + 1, "")

        return "\n".join(lines)

    def create_table(
        self,
        headers: List[str],
        rows: List[List[str]],
        align: Optional[List[str]] = None,
    ) -> str:
        """
        Create a markdown table.

        Args:
            headers: List of column headers
            rows: List of rows, each a list of cell values
            align: Optional alignment for each column ('left', 'center', 'right')

        Returns:
            Markdown table as string
        """
        if not headers or not rows:
            return ""

        lines = []

        # Header row
        lines.append("| " + " | ".join(headers) + " |")

        # Separator row
        align = align or ["left"] * len(headers)
        separators = []
        for alignment in align:
            if alignment == "center":
                separators.append(":---:")
            elif alignment == "right":
                separators.append("---:")
            else:
                separators.append(":---")
        lines.append("| " + " | ".join(separators) + " |")

        # Data rows
        for row in rows:
            # Pad row with empty cells if needed
            padded_row = row + [""] * (len(headers) - len(row))
            lines.append("| " + " | ".join(padded_row[: len(headers)]) + " |")

        return "\n".join(lines)

    def create_code_block(
        self, code: str, language: str = "python", title: Optional[str] = None
    ) -> str:
        """
        Create a markdown code block.

        Args:
            code: Code content
            language: Programming language for syntax highlighting
            title: Optional title for code block

        Returns:
            Markdown code block as string
        """
        lines = []

        if title:
            lines.append(f"**{title}**")
            lines.append("")

        lines.append(f"```{language}")
        lines.append(code)
        lines.append("```")

        return "\n".join(lines)

    def create_list(
        self, items: List[str], ordered: bool = False, level: int = 0
    ) -> str:
        """
        Create a markdown list.

        Args:
            items: List of items
            ordered: If True, create ordered list; else unordered
            level: Indentation level

        Returns:
            Markdown list as string
        """
        indent = "  " * level
        lines = []

        for i, item in enumerate(items):
            if ordered:
                lines.append(f"{indent}{i + 1}. {item}")
            else:
                lines.append(f"{indent}- {item}")

        return "\n".join(lines)

    def create_callout(
        self, content: str, callout_type: str = "note"
    ) -> str:
        """
        Create a markdown callout/admonition.

        Args:
            content: Callout content
            callout_type: Type of callout ('note', 'warning', 'info', 'danger')

        Returns:
            Markdown callout as string
        """
        icons = {
            "note": "📝",
            "warning": "⚠️",
            "info": "ℹ️",
            "danger": "🚨",
        }

        icon = icons.get(callout_type, "📝")
        lines = []
        lines.append(f"> **{callout_type.upper()}** {icon}")
        lines.append(f"> ")

        for line in content.split("\n"):
            lines.append(f"> {line}")

        return "\n".join(lines)

    def create_link(self, text: str, url: str) -> str:
        """Create a markdown link."""
        return f"[{text}]({url})"

    def write_to_file(self, content: str, file_path: Path) -> bool:
        """
        Write markdown content to file.

        Args:
            content: Markdown content
            file_path: Output file path

        Returns:
            True if successful
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            self.logger.info(f"Wrote markdown file: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write markdown file: {e}")
            return False

    def read_from_file(self, file_path: Path) -> Optional[str]:
        """
        Read markdown content from file.

        Args:
            file_path: Input file path

        Returns:
            Markdown content or None if failed
        """
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception as e:
            self.logger.error(f"Failed to read markdown file: {e}")
            return None

    def add_timestamp(self, document: str) -> str:
        """
        Add generation timestamp to document.

        Args:
            document: Markdown document

        Returns:
            Document with timestamp added
        """
        timestamp = datetime.now().isoformat()
        lines = document.split("\n")
        # Find end of front matter or first heading
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith("# "):
                insert_pos = i + 2
                break

        lines.insert(insert_pos, f"> Generated: {timestamp}")
        lines.insert(insert_pos + 1, "")

        return "\n".join(lines)
