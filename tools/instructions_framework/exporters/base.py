"""Base exporter class for instruction exporters"""

from abc import ABC, abstractmethod
from typing import Any, List
from ..schema import Instruction


class BaseExporter(ABC):
    """
    Base class for instruction exporters.

    Exporters convert Instructions to platform-specific formats.
    Subclasses must implement the export() method to return formatted output
    for their target platform (JSON, YAML, custom formats, etc.).
    """

    @abstractmethod
    def export(self, instructions: List[Instruction], **kwargs) -> Any:
        """
        Export instructions to a specific format.

        Args:
            instructions: List of instructions to export
            **kwargs: Format-specific options

        Returns:
            Exported instructions in format-specific structure
        """
        pass
