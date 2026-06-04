"""Conflict detection middleware for instructions"""

from typing import List, Dict
from ..schema import Instruction
from .base import InstructionMiddleware


class ConflictDetectorMiddleware(InstructionMiddleware):
    """Detects conflicting instructions (duplicate IDs, version conflicts)"""

    def __init__(self) -> None:
        """Initialize conflict detector with empty conflicts list."""
        self.conflicts: List[str] = []

    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """
        Detect conflicts and filter out duplicates.

        Keeps the first occurrence of each ID and reports conflicts
        for any subsequent instructions with the same ID.

        Args:
            instructions: List of instructions to process

        Returns:
            Filtered list with duplicates removed (keeps first of each ID)
        """
        self.conflicts = []

        if not instructions:
            return instructions

        # Track seen IDs and their first occurrence
        seen_ids: Dict[str, Instruction] = {}
        result: List[Instruction] = []

        for instr in instructions:
            if instr.id in seen_ids:
                # Conflict: duplicate ID
                first_version = seen_ids[instr.id].metadata.version
                current_version = instr.metadata.version
                self.conflicts.append(
                    f"Duplicate ID '{instr.id}': "
                    f"version {current_version} conflicts with version {first_version}"
                )
            else:
                # No conflict, add to result and track
                seen_ids[instr.id] = instr
                result.append(instr)

        return result
