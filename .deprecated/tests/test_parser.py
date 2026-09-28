"""Tests for YAML+Markdown hybrid instruction parser"""

import pytest
from pathlib import Path
from instructions_framework import Instruction, InstructionMetadata
from instructions_framework.parser import parse_instruction_file


class TestParseInstructionFile:
    """Test suite for parse_instruction_file function"""

    @pytest.fixture
    def fixture_path(self):
        """Path to test fixture file"""
        return Path(__file__).parent / "fixtures" / "sample_instructions" / "global_core.md"

    def test_parse_instruction_file_success(self, fixture_path):
        """Test successful parsing of a valid instruction file with metadata extraction"""
        instruction = parse_instruction_file(fixture_path)

        # Verify Instruction object is returned
        assert isinstance(instruction, Instruction)

        # Verify metadata is extracted correctly
        assert instruction.metadata.version == "1.0.0"
        assert instruction.metadata.description == "Core global instruction set for all agents"
        assert instruction.metadata.priority == 10
        assert instruction.metadata.applicability == ["claude", "openai", "gemini"]
        assert instruction.metadata.scope.value == "global"
        assert instruction.metadata.deprecated is False
        assert instruction.metadata.author == "system"
        assert set(instruction.metadata.tags) == {"core", "behavioral", "global"}

    def test_parse_instruction_file_extracts_content(self, fixture_path):
        """Test that markdown body content is extracted correctly"""
        instruction = parse_instruction_file(fixture_path)

        # Verify content is not empty
        assert instruction.content
        assert len(instruction.content) > 0

        # Verify key content sections are present
        assert "# Global Core Instructions" in instruction.content
        assert "## Purpose" in instruction.content
        assert "## Core Rules" in instruction.content
        assert "Rule 1: Version Checking" in instruction.content
        assert "Rule 2: Test Naming" in instruction.content

    def test_parse_instruction_file_sections(self, fixture_path):
        """Test that markdown sections are extracted and parsed correctly"""
        instruction = parse_instruction_file(fixture_path)

        # Verify sections list is populated
        assert len(instruction.sections) > 0

        # Verify section structure
        section_headings = [s.heading for s in instruction.sections]
        assert "Purpose" in section_headings
        assert "Core Rules" in section_headings
        assert "Provider-Specific Behavior" in section_headings
        assert "Metadata Markers" in section_headings

        # Verify each section has content
        for section in instruction.sections:
            assert section.heading
            assert len(section.heading) > 0
            assert section.content
            assert len(section.content) > 0

    def test_parse_instruction_file_not_found(self):
        """Test error handling when file does not exist"""
        non_existent_path = Path("/non/existent/file.md")

        with pytest.raises(FileNotFoundError):
            parse_instruction_file(non_existent_path)

    def test_parse_instruction_file_invalid_format(self, tmp_path):
        """Test error handling for invalid YAML frontmatter format"""
        # Create a file with invalid YAML
        invalid_file = tmp_path / "invalid.md"
        invalid_file.write_text("""---
version: "1.0.0
description: unclosed string
---

# Content here
""")

        with pytest.raises(ValueError):
            parse_instruction_file(invalid_file)

    def test_parse_instruction_file_converts_hyphens_to_underscores(self, tmp_path):
        """Parser converts filename hyphens to underscores in ID"""
        # Create a temporary test file with hyphens
        test_file = tmp_path / "test-with-hyphens.md"

        content = """---
version: "1.0.0"
description: "Test Instruction"
priority: 5
applicability: ["claude"]
precedence: "merge"
scope: "global"
---

Test content with hyphens in filename
"""
        test_file.write_text(content)

        instruction = parse_instruction_file(test_file)
        assert instruction.id == "test_with_hyphens", f"Expected 'test_with_hyphens', got '{instruction.id}'"
