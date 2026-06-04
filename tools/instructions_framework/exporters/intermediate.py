"""Universal intermediate JSON format exporter"""

from typing import Any, List, Dict
from datetime import datetime
from .base import BaseExporter
from ..schema import Instruction


class IntermediateExporter(BaseExporter):
    """
    Export instructions to universal intermediate JSON format.

    This format serves as a bridge between instruction sources and platform-specific
    exporters. It preserves all instruction data in a standardized structure.
    """

    def export(self, instructions: List[Instruction], **kwargs) -> Dict[str, Any]:
        """
        Export instructions to intermediate JSON format.

        Args:
            instructions: List of instructions to export
            **kwargs: Format-specific options (accepted but not used by this exporter)

        Returns:
            Dictionary with version, metadata, and instructions list
        """
        return {
            "version": "1.0",
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "total_count": len(instructions),
                "valid_count": len(instructions),
            },
            "instructions": [instr.to_dict() for instr in instructions],
        }
