"""Centralized Instructions Framework"""

__version__ = "1.0.0"
__author__ = "Awesome Prompts"

from .schema import (
    InstructionCategory,
    InstructionPrecedence,
    InstructionScope,
    InstructionMetadata,
    Instruction,
)

__all__ = [
    "InstructionCategory",
    "InstructionPrecedence",
    "InstructionScope",
    "InstructionMetadata",
    "Instruction",
]
