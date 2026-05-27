"""Validation middleware for instructions"""

from typing import List
from ..schema import Instruction
from .base import InstructionMiddleware


class ValidationMiddleware(InstructionMiddleware):
    """Validates instructions and filters out invalid ones"""

    def __init__(self) -> None:
        """Initialize validation middleware with empty errors list."""
        self.errors: List[str] = []

    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """Validate all instructions, filter out invalid ones"""
        self.errors = []
        valid = []

        for instruction in instructions:
            instruction_errors = instruction.validate()

            if instruction_errors:
                for error in instruction_errors:
                    self.errors.append(f"{instruction.id}: {error}")
            else:
                valid.append(instruction)

        return valid
