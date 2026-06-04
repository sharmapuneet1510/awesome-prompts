"""OpenAI format exporter - system message prompt"""

from typing import Any, List
from .base import BaseExporter
from ..schema import Instruction


class OpenAIExporter(BaseExporter):
    """
    Export instructions to OpenAI system message prompt format.

    This format creates a natural language prompt that can be used
    as a system message for OpenAI chat models.
    """

    def export(self, instructions: List[Instruction], **kwargs) -> str:
        """
        Export instructions to OpenAI prompt format.

        Args:
            instructions: List of instructions to export
            **kwargs: Format-specific options

        Returns:
            System prompt string with all instructions
        """
        lines = ["You are an AI assistant. Follow these instructions:\n"]

        for i, instruction in enumerate(instructions):
            if i > 0:
                lines.append("\n---\n")

            # Instruction header
            lines.append(f"[{instruction.id} - {instruction.name}]")
            lines.append(f"Category: {instruction.category.value}")
            lines.append(f"Priority: {instruction.metadata.priority}")
            lines.append(f"Scope: {instruction.metadata.scope.value}")

            if instruction.metadata.applicability:
                lines.append(
                    f"Applicability: {', '.join(instruction.metadata.applicability)}"
                )

            lines.append("")
            lines.append(instruction.content)

        return "\n".join(lines)
