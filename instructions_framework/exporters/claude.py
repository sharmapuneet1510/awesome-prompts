"""Claude format exporter - XML tags"""

from typing import Any, List
import xml.etree.ElementTree as ET
from xml.dom import minidom
from .base import BaseExporter
from ..schema import Instruction


class ClaudeExporter(BaseExporter):
    """
    Export instructions to Claude-specific XML format.

    This format uses XML tags to structure instructions with metadata
    and content in a hierarchical format suitable for Claude system prompts.
    """

    def export(self, instructions: List[Instruction], **kwargs) -> str:
        """
        Export instructions to Claude XML format.

        Args:
            instructions: List of instructions to export
            **kwargs: Format-specific options (indent, pretty_print, etc.)

        Returns:
            XML string representation of instructions
        """
        # Create root element
        root = ET.Element("claude-instructions")

        # Add instructions
        for instruction in instructions:
            instr_elem = ET.SubElement(
                root,
                "instruction",
                {
                    "id": instruction.id,
                    "name": instruction.name,
                    "category": instruction.category.value,
                    "priority": str(instruction.metadata.priority),
                },
            )

            # Add content
            content_elem = ET.SubElement(instr_elem, "content")
            content_elem.text = instruction.content

            # Add metadata
            metadata_elem = ET.SubElement(instr_elem, "metadata")

            version_elem = ET.SubElement(metadata_elem, "version")
            version_elem.text = instruction.metadata.version

            applicability_elem = ET.SubElement(metadata_elem, "applicability")
            applicability_elem.text = ", ".join(instruction.metadata.applicability)

            scope_elem = ET.SubElement(metadata_elem, "scope")
            scope_elem.text = instruction.metadata.scope.value

        # Convert to string with pretty printing
        xml_str = ET.tostring(root, encoding="unicode")

        # Pretty print if requested
        if kwargs.get("pretty_print", True):
            try:
                dom = minidom.parseString(xml_str)
                xml_str = dom.toprettyxml(indent="  ")
                # Remove XML declaration
                lines = xml_str.split("\n")
                xml_str = "\n".join(lines[1:])
            except Exception:
                # Fall back to unpretty version if pretty print fails
                pass

        return xml_str
