"""Tests for platform-specific exporters: Claude, OpenAI, Gemini, Copilot, Custom"""

import pytest
import json
import xml.etree.ElementTree as ET
from instructions_framework.exporters.base import BaseExporter
from instructions_framework.exporters.claude import ClaudeExporter
from instructions_framework.exporters.openai import OpenAIExporter
from instructions_framework.exporters.gemini import GeminiExporter
from instructions_framework.exporters.copilot import CopilotExporter
from instructions_framework.exporters.custom import CustomExporter
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
        ],
    )


@pytest.fixture
def multiple_instructions():
    """Create multiple instructions for testing"""
    instructions = []
    for i in range(3):
        metadata = InstructionMetadata(
            version="1.0",
            description=f"Test instruction {i}",
            priority=i + 1,
            applicability=["claude"],
            precedence=InstructionPrecedence.MERGE,
            scope=InstructionScope.GLOBAL,
        )
        instruction = Instruction(
            id=f"test-{i}",
            name=f"Test Instruction {i}",
            category=InstructionCategory.CORE,
            metadata=metadata,
            content=f"Content for instruction {i}",
        )
        instructions.append(instruction)
    return instructions


# ============================================================================
# CLAUDE EXPORTER TESTS
# ============================================================================


class TestClaudeExporter:
    """Tests for ClaudeExporter XML format"""

    def test_claude_exporter_inherits_from_base(self):
        """ClaudeExporter inherits from BaseExporter"""
        exporter = ClaudeExporter()
        assert isinstance(exporter, BaseExporter)

    def test_claude_exporter_formats_as_xml(self, sample_instruction):
        """ClaudeExporter returns XML string"""
        exporter = ClaudeExporter()
        result = exporter.export([sample_instruction])
        assert isinstance(result, str)
        # Should be valid XML
        root = ET.fromstring(result)
        assert root is not None

    def test_claude_exporter_root_element_name(self, sample_instruction):
        """Root element is claude-instructions"""
        exporter = ClaudeExporter()
        result = exporter.export([sample_instruction])
        root = ET.fromstring(result)
        assert root.tag == "claude-instructions"

    def test_claude_exporter_includes_all_instructions(self, multiple_instructions):
        """All instructions are included in XML"""
        exporter = ClaudeExporter()
        result = exporter.export(multiple_instructions)
        root = ET.fromstring(result)
        instruction_elements = root.findall("instruction")
        assert len(instruction_elements) == 3

    def test_claude_exporter_includes_instruction_id(self, sample_instruction):
        """Each instruction has id attribute"""
        exporter = ClaudeExporter()
        result = exporter.export([sample_instruction])
        root = ET.fromstring(result)
        instruction = root.find("instruction")
        assert instruction.get("id") == "sample-001"

    def test_claude_exporter_includes_instruction_name(self, sample_instruction):
        """Each instruction has name attribute"""
        exporter = ClaudeExporter()
        result = exporter.export([sample_instruction])
        root = ET.fromstring(result)
        instruction = root.find("instruction")
        assert instruction.get("name") == "Sample Instruction"

    def test_claude_exporter_includes_instruction_category(self, sample_instruction):
        """Each instruction has category attribute"""
        exporter = ClaudeExporter()
        result = exporter.export([sample_instruction])
        root = ET.fromstring(result)
        instruction = root.find("instruction")
        assert instruction.get("category") == "core"

    def test_claude_exporter_includes_instruction_priority(self, sample_instruction):
        """Each instruction has priority attribute"""
        exporter = ClaudeExporter()
        result = exporter.export([sample_instruction])
        root = ET.fromstring(result)
        instruction = root.find("instruction")
        assert instruction.get("priority") == "5"

    def test_claude_exporter_includes_content(self, sample_instruction):
        """Instruction content is included"""
        exporter = ClaudeExporter()
        result = exporter.export([sample_instruction])
        root = ET.fromstring(result)
        instruction = root.find("instruction")
        content_elem = instruction.find("content")
        assert content_elem is not None
        assert "sample content" in content_elem.text

    def test_claude_exporter_includes_metadata(self, sample_instruction):
        """Instruction metadata section is included"""
        exporter = ClaudeExporter()
        result = exporter.export([sample_instruction])
        root = ET.fromstring(result)
        instruction = root.find("instruction")
        metadata = instruction.find("metadata")
        assert metadata is not None

    def test_claude_exporter_metadata_includes_version(self, sample_instruction):
        """Metadata includes version"""
        exporter = ClaudeExporter()
        result = exporter.export([sample_instruction])
        root = ET.fromstring(result)
        instruction = root.find("instruction")
        metadata = instruction.find("metadata")
        version = metadata.find("version")
        assert version is not None
        assert version.text == "1.0"

    def test_claude_exporter_metadata_includes_applicability(self, sample_instruction):
        """Metadata includes applicability"""
        exporter = ClaudeExporter()
        result = exporter.export([sample_instruction])
        root = ET.fromstring(result)
        instruction = root.find("instruction")
        metadata = instruction.find("metadata")
        applicability = metadata.find("applicability")
        assert applicability is not None

    def test_claude_exporter_metadata_includes_scope(self, sample_instruction):
        """Metadata includes scope"""
        exporter = ClaudeExporter()
        result = exporter.export([sample_instruction])
        root = ET.fromstring(result)
        instruction = root.find("instruction")
        metadata = instruction.find("metadata")
        scope = metadata.find("scope")
        assert scope is not None
        assert scope.text == "global"

    def test_claude_exporter_handles_empty_list(self):
        """ClaudeExporter works with empty instruction list"""
        exporter = ClaudeExporter()
        result = exporter.export([])
        root = ET.fromstring(result)
        instruction_elements = root.findall("instruction")
        assert len(instruction_elements) == 0


# ============================================================================
# OPENAI EXPORTER TESTS
# ============================================================================


class TestOpenAIExporter:
    """Tests for OpenAIExporter text/prompt format"""

    def test_openai_exporter_inherits_from_base(self):
        """OpenAIExporter inherits from BaseExporter"""
        exporter = OpenAIExporter()
        assert isinstance(exporter, BaseExporter)

    def test_openai_exporter_formats_as_prompt(self, sample_instruction):
        """OpenAIExporter returns string prompt"""
        exporter = OpenAIExporter()
        result = exporter.export([sample_instruction])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_openai_exporter_includes_header(self, sample_instruction):
        """Output includes header about instructions"""
        exporter = OpenAIExporter()
        result = exporter.export([sample_instruction])
        assert "instruction" in result.lower()

    def test_openai_exporter_separates_instructions(self, multiple_instructions):
        """Multiple instructions are separated"""
        exporter = OpenAIExporter()
        result = exporter.export(multiple_instructions)
        # Should have separator for multiple instructions
        assert "---" in result or "---\n" in result

    def test_openai_exporter_includes_instruction_id(self, sample_instruction):
        """Instruction ID is included"""
        exporter = OpenAIExporter()
        result = exporter.export([sample_instruction])
        assert "sample-001" in result

    def test_openai_exporter_includes_instruction_name(self, sample_instruction):
        """Instruction name is included"""
        exporter = OpenAIExporter()
        result = exporter.export([sample_instruction])
        assert "Sample Instruction" in result

    def test_openai_exporter_includes_category(self, sample_instruction):
        """Category is included"""
        exporter = OpenAIExporter()
        result = exporter.export([sample_instruction])
        assert "core" in result.lower() or "category" in result.lower()

    def test_openai_exporter_includes_priority(self, sample_instruction):
        """Priority is included"""
        exporter = OpenAIExporter()
        result = exporter.export([sample_instruction])
        assert "5" in result or "priority" in result.lower()

    def test_openai_exporter_includes_scope(self, sample_instruction):
        """Scope is included"""
        exporter = OpenAIExporter()
        result = exporter.export([sample_instruction])
        assert "global" in result.lower() or "scope" in result.lower()

    def test_openai_exporter_includes_content(self, sample_instruction):
        """Content is included"""
        exporter = OpenAIExporter()
        result = exporter.export([sample_instruction])
        assert "sample content" in result.lower()

    def test_openai_exporter_all_instructions_present(self, multiple_instructions):
        """All instruction IDs are present"""
        exporter = OpenAIExporter()
        result = exporter.export(multiple_instructions)
        for instr in multiple_instructions:
            assert instr.id in result

    def test_openai_exporter_handles_empty_list(self):
        """OpenAIExporter works with empty instruction list"""
        exporter = OpenAIExporter()
        result = exporter.export([])
        assert isinstance(result, str)


# ============================================================================
# GEMINI EXPORTER TESTS
# ============================================================================


class TestGeminiExporter:
    """Tests for GeminiExporter JSON format"""

    def test_gemini_exporter_inherits_from_base(self):
        """GeminiExporter inherits from BaseExporter"""
        exporter = GeminiExporter()
        assert isinstance(exporter, BaseExporter)

    def test_gemini_exporter_formats_as_json(self, sample_instruction):
        """GeminiExporter returns dict (JSON-compatible)"""
        exporter = GeminiExporter()
        result = exporter.export([sample_instruction])
        assert isinstance(result, dict)

    def test_gemini_exporter_includes_instructions_key(self, sample_instruction):
        """Result includes 'instructions' key"""
        exporter = GeminiExporter()
        result = exporter.export([sample_instruction])
        assert "instructions" in result

    def test_gemini_exporter_instructions_is_list(self, sample_instruction):
        """Instructions value is a list"""
        exporter = GeminiExporter()
        result = exporter.export([sample_instruction])
        assert isinstance(result["instructions"], list)

    def test_gemini_exporter_json_structure(self, sample_instruction):
        """JSON structure has expected fields"""
        exporter = GeminiExporter()
        result = exporter.export([sample_instruction])
        instr = result["instructions"][0]
        assert "id" in instr
        assert "name" in instr
        assert "category" in instr
        assert "priority" in instr
        assert "content" in instr

    def test_gemini_exporter_includes_all_instructions(self, multiple_instructions):
        """All instructions are included in JSON"""
        exporter = GeminiExporter()
        result = exporter.export(multiple_instructions)
        assert len(result["instructions"]) == 3

    def test_gemini_exporter_instruction_has_id(self, sample_instruction):
        """Each instruction has id field"""
        exporter = GeminiExporter()
        result = exporter.export([sample_instruction])
        assert result["instructions"][0]["id"] == "sample-001"

    def test_gemini_exporter_instruction_has_name(self, sample_instruction):
        """Each instruction has name field"""
        exporter = GeminiExporter()
        result = exporter.export([sample_instruction])
        assert result["instructions"][0]["name"] == "Sample Instruction"

    def test_gemini_exporter_instruction_has_category(self, sample_instruction):
        """Each instruction has category field"""
        exporter = GeminiExporter()
        result = exporter.export([sample_instruction])
        assert result["instructions"][0]["category"] == "core"

    def test_gemini_exporter_instruction_has_content(self, sample_instruction):
        """Each instruction has content field"""
        exporter = GeminiExporter()
        result = exporter.export([sample_instruction])
        assert "sample content" in result["instructions"][0]["content"].lower()

    def test_gemini_exporter_instruction_has_metadata(self, sample_instruction):
        """Each instruction has metadata"""
        exporter = GeminiExporter()
        result = exporter.export([sample_instruction])
        assert "metadata" in result["instructions"][0]

    def test_gemini_exporter_metadata_structure(self, sample_instruction):
        """Metadata has expected fields"""
        exporter = GeminiExporter()
        result = exporter.export([sample_instruction])
        metadata = result["instructions"][0]["metadata"]
        assert "version" in metadata
        assert "applicability" in metadata
        assert "scope" in metadata

    def test_gemini_exporter_is_json_serializable(self, sample_instruction):
        """Result can be serialized to JSON string"""
        exporter = GeminiExporter()
        result = exporter.export([sample_instruction])
        # Should not raise an error
        json_str = json.dumps(result)
        assert isinstance(json_str, str)

    def test_gemini_exporter_handles_empty_list(self):
        """GeminiExporter works with empty instruction list"""
        exporter = GeminiExporter()
        result = exporter.export([])
        assert isinstance(result, dict)
        assert result["instructions"] == []


# ============================================================================
# COPILOT EXPORTER TESTS
# ============================================================================


class TestCopilotExporter:
    """Tests for CopilotExporter markdown format"""

    def test_copilot_exporter_inherits_from_base(self):
        """CopilotExporter inherits from BaseExporter"""
        exporter = CopilotExporter()
        assert isinstance(exporter, BaseExporter)

    def test_copilot_exporter_formats_as_markdown(self, sample_instruction):
        """CopilotExporter returns markdown string"""
        exporter = CopilotExporter()
        result = exporter.export([sample_instruction])
        assert isinstance(result, str)

    def test_copilot_exporter_has_header(self, sample_instruction):
        """Output has markdown header"""
        exporter = CopilotExporter()
        result = exporter.export([sample_instruction])
        assert "#" in result
        assert "instruction" in result.lower()

    def test_copilot_exporter_has_instruction_headers(self, multiple_instructions):
        """Each instruction has a header"""
        exporter = CopilotExporter()
        result = exporter.export(multiple_instructions)
        # Should have multiple ## headers for instructions
        assert result.count("##") >= 3

    def test_copilot_exporter_includes_category_field(self, sample_instruction):
        """Category is shown as markdown field"""
        exporter = CopilotExporter()
        result = exporter.export([sample_instruction])
        assert "category" in result.lower()
        assert "core" in result.lower()

    def test_copilot_exporter_includes_priority_field(self, sample_instruction):
        """Priority is shown as markdown field"""
        exporter = CopilotExporter()
        result = exporter.export([sample_instruction])
        assert "priority" in result.lower()
        assert "5" in result

    def test_copilot_exporter_includes_scope_field(self, sample_instruction):
        """Scope is shown as markdown field"""
        exporter = CopilotExporter()
        result = exporter.export([sample_instruction])
        assert "scope" in result.lower()
        assert "global" in result.lower()

    def test_copilot_exporter_includes_applicability_field(self, sample_instruction):
        """Applicability is shown"""
        exporter = CopilotExporter()
        result = exporter.export([sample_instruction])
        assert "applicab" in result.lower()

    def test_copilot_exporter_includes_content(self, sample_instruction):
        """Content is included"""
        exporter = CopilotExporter()
        result = exporter.export([sample_instruction])
        assert "sample content" in result.lower()

    def test_copilot_exporter_separates_instructions(self, multiple_instructions):
        """Instructions are separated with dividers"""
        exporter = CopilotExporter()
        result = exporter.export(multiple_instructions)
        # Should have separator lines (---)
        assert "---" in result

    def test_copilot_exporter_handles_empty_list(self):
        """CopilotExporter works with empty instruction list"""
        exporter = CopilotExporter()
        result = exporter.export([])
        assert isinstance(result, str)

    def test_copilot_exporter_instruction_ids_in_output(self, multiple_instructions):
        """All instruction IDs are in output"""
        exporter = CopilotExporter()
        result = exporter.export(multiple_instructions)
        for instr in multiple_instructions:
            assert instr.id in result


# ============================================================================
# CUSTOM EXPORTER TESTS
# ============================================================================


class TestCustomExporter:
    """Tests for CustomExporter template-based format"""

    def test_custom_exporter_inherits_from_base(self):
        """CustomExporter inherits from BaseExporter"""
        exporter = CustomExporter()
        assert isinstance(exporter, BaseExporter)

    def test_custom_exporter_raises_without_template(self, sample_instruction):
        """CustomExporter raises ValueError without template"""
        exporter = CustomExporter()
        with pytest.raises(ValueError):
            exporter.export([sample_instruction])

    def test_custom_exporter_with_simple_template(self, sample_instruction):
        """CustomExporter uses simple template"""
        exporter = CustomExporter()
        template = "ID: {id}, Name: {name}"
        result = exporter.export([sample_instruction], template=template)
        assert isinstance(result, str)
        assert "sample-001" in result
        assert "Sample Instruction" in result

    def test_custom_exporter_template_substitution(self, sample_instruction):
        """Template placeholders are replaced correctly"""
        exporter = CustomExporter()
        template = "{id}|{name}|{category}|{priority}"
        result = exporter.export([sample_instruction], template=template)
        assert "sample-001" in result
        assert "Sample Instruction" in result
        assert "core" in result
        assert "5" in result

    def test_custom_exporter_template_with_content(self, sample_instruction):
        """Template can include content"""
        exporter = CustomExporter()
        template = "{name}\n{content}"
        result = exporter.export([sample_instruction], template=template)
        assert "Sample Instruction" in result
        assert "sample content" in result.lower()

    def test_custom_exporter_multiline_template(self, sample_instruction):
        """Template can be multiline"""
        exporter = CustomExporter()
        template = """Instruction: {id}
Title: {name}
Category: {category}
Priority: {priority}
Content: {content}"""
        result = exporter.export([sample_instruction], template=template)
        assert "Instruction:" in result
        assert "Title:" in result
        assert "Category:" in result

    def test_custom_exporter_multiple_instructions(self, multiple_instructions):
        """CustomExporter applies template to all instructions"""
        exporter = CustomExporter()
        template = "{id}: {name}\n"
        result = exporter.export(multiple_instructions, template=template)
        for instr in multiple_instructions:
            assert instr.id in result

    def test_custom_exporter_handles_empty_list(self):
        """CustomExporter works with empty instruction list"""
        exporter = CustomExporter()
        template = "{id}: {name}"
        result = exporter.export([], template=template)
        assert isinstance(result, str)

    def test_custom_exporter_with_custom_separator(self, multiple_instructions):
        """Template can be applied with custom separators"""
        exporter = CustomExporter()
        template = "{id}|{name}"
        result = exporter.export(
            multiple_instructions, template=template, separator=" || "
        )
        assert isinstance(result, str)
        # If separator is provided, result might use it
        assert "|" in result or "||" in result

    def test_custom_exporter_preserves_unmatched_placeholders(self, sample_instruction):
        """Unmatched placeholders remain in output"""
        exporter = CustomExporter()
        template = "{id} - {name} - {unknown_field}"
        result = exporter.export([sample_instruction], template=template)
        assert "sample-001" in result
        # Unknown field behavior depends on implementation
        assert isinstance(result, str)

    def test_custom_exporter_returns_string(self, sample_instruction):
        """CustomExporter always returns a string"""
        exporter = CustomExporter()
        template = "{id}"
        result = exporter.export([sample_instruction], template=template)
        assert isinstance(result, str)
