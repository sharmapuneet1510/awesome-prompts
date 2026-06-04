"""Precedence Applier Middleware"""

from typing import List, Dict
from ..schema import Instruction, InstructionPrecedence
from .base import InstructionMiddleware


class PrecedenceApplierMiddleware(InstructionMiddleware):
    """Applies precedence rules to consolidate instructions by category"""

    def process(self, instructions: List[Instruction]) -> List[Instruction]:
        """
        Apply precedence rules to consolidate instructions.

        Groups instructions by category. For each group:
        - If OVERRIDE precedence: keep only the last instruction
        - If MERGE precedence: merge all content into single instruction

        Args:
            instructions: List of instructions to process

        Returns:
            Consolidated list with fewer total instructions
        """
        if not instructions:
            return []

        # Group instructions by category
        by_category: Dict[str, List[Instruction]] = {}
        for instr in instructions:
            cat_key = instr.category.value
            if cat_key not in by_category:
                by_category[cat_key] = []
            by_category[cat_key].append(instr)

        result = []

        # Process each category
        for category_key, instrs in by_category.items():
            if len(instrs) == 1:
                # Single instruction in category, keep as-is
                result.append(instrs[0])
            else:
                # Multiple instructions in category, apply precedence
                precedence = instrs[0].metadata.precedence

                if precedence == InstructionPrecedence.OVERRIDE:
                    # Keep only the last instruction
                    result.append(instrs[-1])
                else:  # MERGE
                    # Merge all instructions
                    merged = self._merge_instructions(instrs)
                    result.append(merged)

        return result

    def _merge_instructions(self, instrs: List[Instruction]) -> Instruction:
        """
        Merge multiple instructions into one.

        Takes the first instruction as base and concatenates content from all.
        Maintains original metadata except for merged content.

        Args:
            instrs: List of instructions to merge (at least 2)

        Returns:
            Single merged instruction
        """
        if not instrs:
            raise ValueError("Cannot merge empty instruction list")

        # Use the first instruction as base
        base = instrs[0]

        # Concatenate content from all instructions
        merged_content = "\n\n".join([instr.content for instr in instrs])

        # Create new instruction with merged content
        merged = Instruction(
            id=base.id,
            name=base.name,
            category=base.category,
            metadata=base.metadata,
            content=merged_content,
            sections=base.sections,
            provider_variants=base.provider_variants,
            source_path=base.source_path,
        )

        return merged
