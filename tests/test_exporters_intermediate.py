"""Tests for IntermediateExporter JSON export functionality"""

import pytest
from datetime import datetime
from instructions_framework.exporters.intermediate import IntermediateExporter
from instructions_framework.exporters.base import BaseExporter
from instructions_framework.schema import (
    Instruction,
    InstructionMetadata,
    InstructionCategory,
    InstructionPrecedence,
    InstructionScope,
    InstructionSection,
)


@pytest.fixture
def sample_instruction():
    """Create a sample instruction for testing"""
    metadata = InstructionMetadata(
        version="1.0",
        description="Sample instruction",
        priority=5,
        applicability=["claude", "openai"],
        precedence=InstructionPrecedence.OVERRIDE,
        scope=InstructionScope.GLOBAL,
        tags=["test", "example"],
        author="test_author",
    )
    return Instruction(
        id="sample-001",
        name="Sample Instruction",
        category=InstructionCategory.CORE,
        metadata=metadata,
        content="This is sample content",
        sections=[
            InstructionSection(
                heading="Overview",
                content="This is an overview section",
                metadata={"type": "intro"},
            ),
            InstructionSection(
                heading="Details",
                content="This is the details section",
                metadata={"type": "body"},
            ),
        ],
    )


def test_intermediate_exporter_inherits_from_base():
    """IntermediateExporter inherits from BaseExporter"""
    exporter = IntermediateExporter()
    assert isinstance(exporter, BaseExporter)


def test_intermediate_exporter_exports_to_dict():
    """IntermediateExporter returns a dictionary"""
    exporter = IntermediateExporter()
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
        content="Test content",
    )

    result = exporter.export([instruction])
    assert isinstance(result, dict)


def test_intermediate_exporter_includes_version():
    """Exported dict includes version field"""
    exporter = IntermediateExporter()
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
        content="Test content",
    )

    result = exporter.export([instruction])
    assert "version" in result
    assert result["version"] == "1.0"


def test_intermediate_exporter_includes_metadata():
    """Exported dict includes metadata with export info"""
    exporter = IntermediateExporter()
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
        content="Test content",
    )

    result = exporter.export([instruction])
    assert "metadata" in result
    assert "export_date" in result["metadata"]
    assert "total_count" in result["metadata"]
    assert "valid_count" in result["metadata"]
    assert result["metadata"]["total_count"] == 1
    assert result["metadata"]["valid_count"] == 1


def test_intermediate_exporter_metadata_export_date_is_iso_format():
    """Metadata export_date is ISO format datetime string"""
    exporter = IntermediateExporter()
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
        content="Test content",
    )

    result = exporter.export([instruction])
    export_date = result["metadata"]["export_date"]
    # Should be parseable as ISO datetime
    parsed = datetime.fromisoformat(export_date)
    assert parsed is not None


def test_intermediate_exporter_includes_instructions():
    """Exported dict includes instructions list"""
    exporter = IntermediateExporter()
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
        content="Test content",
    )

    result = exporter.export([instruction])
    assert "instructions" in result
    assert isinstance(result["instructions"], list)
    assert len(result["instructions"]) == 1


def test_intermediate_exporter_handles_empty_list():
    """IntermediateExporter works with empty instruction list"""
    exporter = IntermediateExporter()
    result = exporter.export([])
    assert result["version"] == "1.0"
    assert result["metadata"]["total_count"] == 0
    assert result["metadata"]["valid_count"] == 0
    assert result["instructions"] == []


def test_intermediate_exporter_preserves_instruction_data(sample_instruction):
    """Instruction data is preserved in export"""
    exporter = IntermediateExporter()
    result = exporter.export([sample_instruction])

    exported_instruction = result["instructions"][0]
    assert exported_instruction["id"] == "sample-001"
    assert exported_instruction["name"] == "Sample Instruction"
    assert exported_instruction["category"] == "core"
    assert exported_instruction["content"] == "This is sample content"
    assert exported_instruction["priority"] == 5


def test_intermediate_exporter_preserves_metadata_fields(sample_instruction):
    """Instruction metadata is preserved in export"""
    exporter = IntermediateExporter()
    result = exporter.export([sample_instruction])

    exported_instr = result["instructions"][0]
    exported_metadata = exported_instr["metadata"]
    assert exported_metadata["version"] == "1.0"
    assert exported_metadata["description"] == "Sample instruction"
    assert exported_metadata["applicability"] == ["claude", "openai"]
    assert exported_metadata["tags"] == ["test", "example"]
    assert exported_metadata["author"] == "test_author"


def test_intermediate_exporter_preserves_sections(sample_instruction):
    """Instruction sections are preserved in export"""
    exporter = IntermediateExporter()
    result = exporter.export([sample_instruction])

    exported_instr = result["instructions"][0]
    assert "sections" in exported_instr
    assert len(exported_instr["sections"]) == 2
    assert exported_instr["sections"][0]["heading"] == "Overview"
    assert exported_instr["sections"][1]["heading"] == "Details"


def test_intermediate_exporter_multiple_instructions():
    """IntermediateExporter handles multiple instructions"""
    exporter = IntermediateExporter()

    instructions = []
    for i in range(3):
        metadata = InstructionMetadata(
            version="1.0",
            description=f"Test {i}",
            priority=5,
            applicability=["claude"],
            precedence=InstructionPrecedence.MERGE,
            scope=InstructionScope.GLOBAL,
        )
        instruction = Instruction(
            id=f"test-{i}",
            name=f"Test {i}",
            category=InstructionCategory.CORE,
            metadata=metadata,
            content=f"Test content {i}",
        )
        instructions.append(instruction)

    result = exporter.export(instructions)
    assert result["metadata"]["total_count"] == 3
    assert result["metadata"]["valid_count"] == 3
    assert len(result["instructions"]) == 3


def test_intermediate_exporter_handles_kwargs():
    """IntermediateExporter accepts and handles kwargs"""
    exporter = IntermediateExporter()
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
        content="Test content",
    )

    # Should not raise an error with arbitrary kwargs
    result = exporter.export([instruction], format="json", pretty=True, indent=2)
    assert isinstance(result, dict)
    assert "instructions" in result
