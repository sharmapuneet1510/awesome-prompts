import pytest
from instructions_framework.middleware.validator import ValidationMiddleware
from instructions_framework.schema import (
    Instruction, InstructionMetadata, InstructionCategory,
    InstructionPrecedence, InstructionScope
)

def test_validation_middleware_rejects_invalid():
    """ValidationMiddleware filters out invalid instructions"""
    middleware = ValidationMiddleware()

    # Valid instruction
    valid_metadata = InstructionMetadata(
        version="1.0",
        description="Valid",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    valid_instruction = Instruction(
        id="valid",
        name="Valid",
        category=InstructionCategory.CORE,
        metadata=valid_metadata,
        content="Valid content",
    )

    # Invalid instruction (missing name)
    invalid_metadata = InstructionMetadata(
        version="1.0",
        description="Invalid",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    invalid_instruction = Instruction(
        id="invalid",
        name="",  # Missing
        category=InstructionCategory.CORE,
        metadata=invalid_metadata,
        content="Invalid content",
    )

    result = middleware.process([valid_instruction, invalid_instruction])

    # Should only have valid instruction
    assert len(result) == 1
    assert result[0].id == "valid"

def test_validation_middleware_collects_errors():
    """ValidationMiddleware tracks validation errors"""
    middleware = ValidationMiddleware()

    invalid_metadata = InstructionMetadata(
        version="1.0",
        description="",  # Missing
        priority=0,  # Invalid
        applicability=[],  # Empty
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    invalid_instruction = Instruction(
        id="invalid",
        name="",  # Missing
        category=InstructionCategory.CORE,
        metadata=invalid_metadata,
        content="",  # Missing
    )

    result = middleware.process([invalid_instruction])

    # Should have errors
    assert len(middleware.errors) > 0
    assert any("invalid" in error for error in middleware.errors)
