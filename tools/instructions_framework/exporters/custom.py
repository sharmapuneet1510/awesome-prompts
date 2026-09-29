"""Custom format exporter - Template-based"""

from typing import Any, List, Optional
import string
from .base import BaseExporter
from ..schema import Instruction


class SafeFormatter(string.Formatter):
    """A formatter that allows missing fields to pass through unchanged"""

    def get_value(self, key, args, kwargs):
        try:
            return super().get_value(key, args, kwargs)
        except (KeyError, IndexError):
            # Return placeholder unchanged if key not found
            return "{" + str(key) + "}"


class CustomExporter(BaseExporter):
    """
    Export instructions using a custom template format.

    This exporter allows users to provide a template string with placeholders
    that are replaced with instruction data. Placeholders include:
    - {id}, {name}, {category}, {content}, {priority}, {scope}, etc.
    """

    def export(
        self,
        instructions: List[Instruction],
        template: Optional[str] = None,
        separator: str = "\n",
        **kwargs,
    ) -> str:
        """
        Export instructions using a custom template.

        Args:
            instructions: List of instructions to export
            template: Template string with placeholders like {id}, {name}, {content}
            separator: Separator string between instructions (default: newline)
            **kwargs: Additional format-specific options

        Returns:
            Formatted string with template applied to all instructions

        Raises:
            ValueError: If template is not provided
        """
        if template is None:
            raise ValueError("template parameter is required for CustomExporter")

        if not instructions:
            return ""

        results = []
        for instruction in instructions:
            # Prepare substitution dict
            subs = {
                "id": instruction.id,
                "name": instruction.name,
                "category": instruction.category.value,
                "content": instruction.content,
                "priority": str(instruction.metadata.priority),
                "scope": instruction.metadata.scope.value,
                "version": instruction.metadata.version,
                "description": instruction.metadata.description,
                "applicability": ", ".join(instruction.metadata.applicability),
                "precedence": instruction.metadata.precedence.value,
                "deprecated": str(instruction.metadata.deprecated),
                "tags": ", ".join(instruction.metadata.tags),
                "author": instruction.metadata.author,
            }

            # Format template with available fields, keeping unknown placeholders
            formatter = SafeFormatter()
            formatted = formatter.format(template, **subs)
            results.append(formatted)

        return separator.join(results)
