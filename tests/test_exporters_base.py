"""Tests for BaseExporter abstract class"""

import pytest
from abc import ABC
from instructions_framework.exporters.base import BaseExporter
from instructions_framework.schema import (
    Instruction,
    InstructionMetadata,
    InstructionCategory,
    InstructionPrecedence,
    InstructionScope,
)


def test_base_exporter_is_abstract():
    """BaseExporter is an abstract class and cannot be instantiated"""
    with pytest.raises(TypeError):
        BaseExporter()


def test_base_exporter_requires_export_method():
    """Subclasses must implement the export method"""

    class IncompleteExporter(BaseExporter):
        """Exporter without export method"""

        pass

    with pytest.raises(TypeError):
        IncompleteExporter()


def test_base_exporter_with_complete_implementation():
    """Subclasses with export method can be instantiated"""

    class CompleteExporter(BaseExporter):
        """Exporter with export method implemented"""

        def export(self, instructions, **kwargs):
            return {"exported": True}

    exporter = CompleteExporter()
    assert exporter is not None


def test_base_exporter_export_is_abstract_method():
    """BaseExporter.export is an abstract method"""
    assert hasattr(BaseExporter, "export")
    assert getattr(BaseExporter.export, "__isabstractmethod__", False)


def test_base_exporter_export_signature():
    """Export method signature accepts instructions and kwargs"""

    class TestExporter(BaseExporter):
        def export(self, instructions, **kwargs):
            return {
                "instructions": instructions,
                "kwargs": kwargs,
            }

    exporter = TestExporter()
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

    result = exporter.export([instruction], format="json", pretty=True)
    assert "instructions" in result
    assert "kwargs" in result
    assert result["kwargs"]["format"] == "json"
    assert result["kwargs"]["pretty"] is True


def test_base_exporter_isinstance_check():
    """Subclasses are instances of BaseExporter"""

    class MyExporter(BaseExporter):
        def export(self, instructions, **kwargs):
            return []

    exporter = MyExporter()
    assert isinstance(exporter, BaseExporter)
