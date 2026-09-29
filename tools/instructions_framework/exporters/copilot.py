"""Copilot format exporter - Markdown"""

from typing import Any, List
from .base import BaseExporter
from ..schema import Instruction


class CopilotExporter(BaseExporter):
    """
    Export instructions to Copilot markdown format.

    This format creates markdown-formatted instructions suitable for use
    with GitHub Copilot and other markdown-based instruction systems.
    """

    def export(self, instructions: List[Instruction], **kwargs) -> str:
        """
        Export instructions to Copilot markdown format.

        Args:
            instructions: List of instructions to export
            **kwargs: Format-specific options

        Returns:
            Markdown string with formatted instructions
        """
        lines = ["# Instructions for Copilot\n"]

        for i, instruction in enumerate(instructions):
            if i > 0:
                lines.append("\n---\n")

            # Instruction header
            lines.append(f"## {instruction.id} - {instruction.name}\n")

            # Metadata fields
            lines.append(f"- **Category:** {instruction.category.value}")
            lines.append(f"- **Priority:** {instruction.metadata.priority}")
            lines.append(f"- **Scope:** {instruction.metadata.scope.value}")

            if instruction.metadata.applicability:
                lines.append(
                    f"- **Applicability:** {', '.join(instruction.metadata.applicability)}"
                )

            lines.append("")
            lines.append(instruction.content)

        return "\n".join(lines)
