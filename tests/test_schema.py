import pytest
from enum import Enum
from instructions_framework.schema import (
    InstructionCategory, InstructionPrecedence, InstructionScope,
    InstructionMetadata, Instruction, InstructionSection
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

def test_instruction_metadata_validate_author_required():
    """InstructionMetadata validation requires non-empty author"""
    metadata = InstructionMetadata(
        version="1.0",
        description="Test",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
        author="",
    )
    errors = metadata.validate()
    assert "author cannot be empty" in errors

def test_instruction_metadata_deprecation_notice_required():
    """InstructionMetadata requires deprecation_notice if deprecated=True"""
    metadata = InstructionMetadata(
        version="1.0",
        description="Test",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
        deprecated=True,
        deprecation_notice=None,  # Missing!
    )
    errors = metadata.validate()
    assert "deprecation_notice is required when deprecated=True" in errors

def test_instruction_priority_boundary_values():
    """Priority values at boundaries (1 and 10) are valid"""
    for priority in [1, 10]:
        metadata = InstructionMetadata(
            version="1.0",
            description="Test",
            priority=priority,
            applicability=["claude"],
            precedence=InstructionPrecedence.MERGE,
            scope=InstructionScope.GLOBAL,
        )
        errors = metadata.validate()
        assert len(errors) == 0

def test_instruction_section_validation():
    """Instruction validates sections (heading required)"""
    invalid_section = InstructionSection(heading="", content="content")

    metadata = InstructionMetadata(
        version="1.0",
        description="Test",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
    )
    instruction = Instruction(
        id="test",
        name="Test",
        category=InstructionCategory.CORE,
        metadata=metadata,
        content="Test",
        sections=[invalid_section],
    )
    errors = instruction.validate()
    assert any("heading" in error for error in errors)

def test_instruction_to_dict_includes_all_fields():
    """to_dict() exports all metadata fields including deprecated, tags, etc"""
    metadata = InstructionMetadata(
        version="1.0",
        description="Test",
        priority=5,
        applicability=["claude"],
        precedence=InstructionPrecedence.MERGE,
        scope=InstructionScope.GLOBAL,
        deprecated=True,
        deprecation_notice="Use new_instruction instead",
        tags=["old", "deprecated"],
    )
    instruction = Instruction(
        id="test",
        name="Test",
        category=InstructionCategory.CORE,
        metadata=metadata,
        content="Test",
        provider_variants={"claude": {"content": "Claude variant"}},
    )
    result = instruction.to_dict()

    # Check metadata fields are present
    assert result["metadata"]["deprecated"] == True
    assert result["metadata"]["deprecation_notice"] == "Use new_instruction instead"
    assert result["metadata"]["tags"] == ["old", "deprecated"]
    assert result["provider_variants"]["claude"]["content"] == "Claude variant"
