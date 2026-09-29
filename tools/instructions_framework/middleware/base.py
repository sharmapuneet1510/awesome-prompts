"""Base middleware class"""

from abc import ABC, abstractmethod
from typing import List
from ..schema import Instruction


class InstructionMiddleware(ABC):
    """Base class for instruction middleware"""

    @abstractmethod
    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """
        Process a list of instructions.
        Can add, modify, or filter instructions.

        Args:
            instructions: List of instructions to process

        Returns:
            Processed list of instructions
        """
        pass
