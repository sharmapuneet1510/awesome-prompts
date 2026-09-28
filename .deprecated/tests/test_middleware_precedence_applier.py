import pytest
from instructions_framework.middleware.precedence_applier import PrecedenceApplierMiddleware
from instructions_framework.schema import (
    Instruction, InstructionMetadata, InstructionCategory,
    InstructionPrecedence, InstructionScope
)


def create_instruction(
    id: str,
    name: str,
    category: InstructionCategory,
    precedence: InstructionPrecedence,
    content: str = "Default content",
) -> Instruction:
    """Helper to create test instructions"""
    metadata = InstructionMetadata(
        version="1.0",
        description=f"Instruction {name}",
        priority=5,
        applicability=["claude"],
        precedence=precedence,
        scope=InstructionScope.GLOBAL,
    )
    return Instruction(
        id=id,
        name=name,
        category=category,
        metadata=metadata,
        content=content,
    )


class TestPrecedenceApplierMiddleware:
    """Tests for PrecedenceApplierMiddleware"""

    def test_precedence_applier_override(self):
        """OVERRIDE precedence keeps latest instruction"""
        middleware = PrecedenceApplierMiddleware()

        # Create two instructions in same category with OVERRIDE precedence
        instr1 = create_instruction(
            id="core-1",
            name="Core Rule 1",
            category=InstructionCategory.CORE,
            precedence=InstructionPrecedence.OVERRIDE,
            content="Original content",
        )
        instr2 = create_instruction(
            id="core-2",
            name="Core Rule 2",
            category=InstructionCategory.CORE,
            precedence=InstructionPrecedence.OVERRIDE,
            content="Updated content",
        )

        result = middleware.process([instr1, instr2])

        # Should only have the latest instruction (instr2)
        assert len(result) == 1
        assert result[0].id == "core-2"
        assert result[0].content == "Updated content"

    def test_precedence_applier_merge(self):
        """MERGE precedence merges instruction content"""
        middleware = PrecedenceApplierMiddleware()

        # Create two instructions in same category with MERGE precedence
        instr1 = create_instruction(
            id="behavior-1",
            name="Behavior Rule 1",
            category=InstructionCategory.BEHAVIORAL,
            precedence=InstructionPrecedence.MERGE,
            content="Rule A: Always validate inputs",
        )
        instr2 = create_instruction(
            id="behavior-2",
            name="Behavior Rule 2",
            category=InstructionCategory.BEHAVIORAL,
            precedence=InstructionPrecedence.MERGE,
            content="Rule B: Always log errors",
        )

        result = middleware.process([instr1, instr2])

        # Should have one instruction with merged content
        assert len(result) == 1
        # Content should contain both rules
        assert "Rule A" in result[0].content
        assert "Rule B" in result[0].content

    def test_precedence_applier_mixed(self):
        """Handles mixed precedence rules"""
        middleware = PrecedenceApplierMiddleware()

        # CORE category with OVERRIDE
        core1 = create_instruction(
            id="core-1",
            name="Core 1",
            category=InstructionCategory.CORE,
            precedence=InstructionPrecedence.OVERRIDE,
            content="Core v1",
        )
        core2 = create_instruction(
            id="core-2",
            name="Core 2",
            category=InstructionCategory.CORE,
            precedence=InstructionPrecedence.OVERRIDE,
            content="Core v2",
        )

        # BEHAVIORAL category with MERGE
        behav1 = create_instruction(
            id="behav-1",
            name="Behavioral 1",
            category=InstructionCategory.BEHAVIORAL,
            precedence=InstructionPrecedence.MERGE,
            content="Behavior A",
        )
        behav2 = create_instruction(
            id="behav-2",
            name="Behavioral 2",
            category=InstructionCategory.BEHAVIORAL,
            precedence=InstructionPrecedence.MERGE,
            content="Behavior B",
        )

        result = middleware.process([core1, core2, behav1, behav2])

        # Should have 2 instructions (one per category, consolidated)
        assert len(result) == 2

        # Find by category
        core_result = [r for r in result if r.category == InstructionCategory.CORE][0]
        behav_result = [r for r in result if r.category == InstructionCategory.BEHAVIORAL][0]

        # CORE should be the latest (OVERRIDE)
        assert core_result.id == "core-2"
        assert core_result.content == "Core v2"

        # BEHAVIORAL should be merged
        assert "Behavior A" in behav_result.content
        assert "Behavior B" in behav_result.content

    def test_precedence_applier_no_consolidation(self):
        """Different categories not consolidated"""
        middleware = PrecedenceApplierMiddleware()

        # Single instruction per category (no duplicates)
        core = create_instruction(
            id="core",
            name="Core",
            category=InstructionCategory.CORE,
            precedence=InstructionPrecedence.MERGE,
            content="Core content",
        )
        behavioral = create_instruction(
            id="behav",
            name="Behavioral",
            category=InstructionCategory.BEHAVIORAL,
            precedence=InstructionPrecedence.MERGE,
            content="Behavioral content",
        )
        constraints = create_instruction(
            id="constraint",
            name="Constraints",
            category=InstructionCategory.CONSTRAINTS,
            precedence=InstructionPrecedence.MERGE,
            content="Constraints content",
        )

        result = middleware.process([core, behavioral, constraints])

        # All three should be returned unchanged
        assert len(result) == 3
        assert {r.id for r in result} == {"core", "behav", "constraint"}

    def test_precedence_applier_empty_list(self):
        """Handles empty list"""
        middleware = PrecedenceApplierMiddleware()

        result = middleware.process([])

        # Should return empty list
        assert len(result) == 0
        assert result == []

    def test_precedence_applier_single_instruction(self):
        """Single instruction returned unchanged"""
        middleware = PrecedenceApplierMiddleware()

        instr = create_instruction(
            id="single",
            name="Single",
            category=InstructionCategory.CORE,
            precedence=InstructionPrecedence.MERGE,
            content="Single content",
        )

        result = middleware.process([instr])

        # Should return the single instruction unchanged
        assert len(result) == 1
        assert result[0].id == "single"
        assert result[0].content == "Single content"

    def test_precedence_applier_three_way_override(self):
        """OVERRIDE with three instructions keeps the latest"""
        middleware = PrecedenceApplierMiddleware()

        instr1 = create_instruction(
            id="v1",
            name="V1",
            category=InstructionCategory.CONSTRAINTS,
            precedence=InstructionPrecedence.OVERRIDE,
            content="Version 1",
        )
        instr2 = create_instruction(
            id="v2",
            name="V2",
            category=InstructionCategory.CONSTRAINTS,
            precedence=InstructionPrecedence.OVERRIDE,
            content="Version 2",
        )
        instr3 = create_instruction(
            id="v3",
            name="V3",
            category=InstructionCategory.CONSTRAINTS,
            precedence=InstructionPrecedence.OVERRIDE,
            content="Version 3",
        )

        result = middleware.process([instr1, instr2, instr3])

        # Should only have the last one
        assert len(result) == 1
        assert result[0].id == "v3"
        assert result[0].content == "Version 3"

    def test_precedence_applier_three_way_merge(self):
        """MERGE with three instructions merges all content"""
        middleware = PrecedenceApplierMiddleware()

        instr1 = create_instruction(
            id="rule1",
            name="Rule 1",
            category=InstructionCategory.OUTPUT_FORMAT,
            precedence=InstructionPrecedence.MERGE,
            content="Rule 1: Use markdown",
        )
        instr2 = create_instruction(
            id="rule2",
            name="Rule 2",
            category=InstructionCategory.OUTPUT_FORMAT,
            precedence=InstructionPrecedence.MERGE,
            content="Rule 2: Use examples",
        )
        instr3 = create_instruction(
            id="rule3",
            name="Rule 3",
            category=InstructionCategory.OUTPUT_FORMAT,
            precedence=InstructionPrecedence.MERGE,
            content="Rule 3: Use headers",
        )

        result = middleware.process([instr1, instr2, instr3])

        # Should have one instruction with all rules
        assert len(result) == 1
        assert "Rule 1" in result[0].content
        assert "Rule 2" in result[0].content
        assert "Rule 3" in result[0].content
