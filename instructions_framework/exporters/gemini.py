"""Gemini format exporter - JSON structure"""

from typing import Any, List, Dict
from .base import BaseExporter
from ..schema import Instruction


class GeminiExporter(BaseExporter):
    """
    Export instructions to Gemini JSON format.

    This format creates a structured JSON object suitable for Gemini API
    with all instruction data preserved in a hierarchical structure.
    """

    def export(self, instructions: List[Instruction], **kwargs) -> Dict[str, Any]:
        """
        Export instructions to Gemini JSON format.

        Args:
            instructions: List of instructions to export
            **kwargs: Format-specific options

        Returns:
            Dictionary with 'instructions' key containing list of instruction dicts
        """
        result = {
            "instructions": [
                {
                    "id": instruction.id,
                    "name": instruction.name,
                    "category": instruction.category.value,
                    "priority": instruction.metadata.priority,
                    "content": instruction.content,
                    "metadata": {
                        "version": instruction.metadata.version,
                        "description": instruction.metadata.description,
                        "applicability": instruction.metadata.applicability,
                        "scope": instruction.metadata.scope.value,
                        "precedence": instruction.metadata.precedence.value,
                        "deprecated": instruction.metadata.deprecated,
                        "tags": instruction.metadata.tags,
                        "dependencies": instruction.metadata.depends_on,
                        "author": instruction.metadata.author,
                    },
                }
                for instruction in instructions
            ]
        }
        return result
