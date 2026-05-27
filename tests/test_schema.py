import pytest
from enum import Enum
from instructions_framework.schema import (
    InstructionCategory, InstructionPrecedence, InstructionScope,
    InstructionMetadata, Instruction
)

def test_instruction_category_values():
    """InstructionCategory enum has required values"""
    assert InstructionCategory.CORE.value == "core"
    assert InstructionCategory.BEHAVIORAL.value == "behavioral"
    assert InstructionCategory.CONSTRAINTS.value == "constraints"
    assert InstructionCategory.OUTPUT_FORMAT.value == "output-format"

def test_instruction_precedence_values():
    """InstructionPrecedence enum has required values"""
    assert InstructionPrecedence.MERGE.value == "merge"
    assert InstructionPrecedence.OVERRIDE.value == "override"

def test_instruction_scope_values():
    """InstructionScope enum has required values"""
    assert InstructionScope.GLOBAL.value == "global"
    assert InstructionScope.PROVIDER.value == "provider"
    assert InstructionScope.AGENT.value == "agent"

def test_instruction_metadata_validate_success():
    """InstructionMetadata validates successfully with valid data"""
    metadata = InstructionMetadata(
        version="1.0",
        description="Test instruction",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    errors = metadata.validate()
    assert len(errors) == 0

def test_instruction_metadata_validate_missing_fields():
    """InstructionMetadata validation catches missing fields"""
    metadata = InstructionMetadata(
        version="",
        description="",
        priority=0,
        applicability=[],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    errors = metadata.validate()
    assert "version is required" in errors
    assert "description is required" in errors
    assert "priority must be 1-10" in errors
    assert "applicability cannot be empty" in errors

def test_instruction_to_dict():
    """Instruction converts to dictionary correctly"""
    metadata = InstructionMetadata(
        version="1.0",
        description="Test",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    instruction = Instruction(
        id="test-instruction",
        name="Test Instruction",
        category=InstructionCategory.CORE,
        metadata=metadata,
        content="Test content",
    )
    result = instruction.to_dict()
    assert result["id"] == "test-instruction"
    assert result["name"] == "Test Instruction"
    assert result["category"] == "core"
    assert result["content"] == "Test content"
