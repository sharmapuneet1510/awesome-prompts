"""Tests for instruction migration tool"""

import json
import pytest
import tempfile
from pathlib import Path
from tools.migrate_instructions import (
    migrate_instruction,
    migrate_file,
    create_migration_template,
)
from instructions_framework.schema import (
    Instruction,
    InstructionCategory,
    InstructionPrecedence,
)


class TestMigrateInstruction:
    """Test migrate_instruction function"""

    def test_migrate_basic_instruction(self):
        """Test migrating basic old format instruction"""
        old_format = {
            "id": "agent-001",
            "name": "Implementation Agent",
            "type": "core",
            "content": "You are an agent...",
            "priority": 5,
            "providers": ["claude"],
            "version": "1.0.0",
        }

        result = migrate_instruction(old_format)

        assert isinstance(result, Instruction)
        assert result.id == "agent-001"
        assert result.name == "Implementation Agent"
        assert result.category == InstructionCategory.CORE
        assert result.content == "You are an agent..."
        assert result.metadata.priority == 5
        assert "claude" in result.metadata.applicability

    def test_migrate_missing_id(self):
        """Test migration fails with missing id"""
        old_format = {
            "name": "Agent",
            "content": "Content",
        }

        with pytest.raises(KeyError):
            migrate_instruction(old_format)

    def test_migrate_missing_name(self):
        """Test migration fails with missing name"""
        old_format = {
            "id": "agent-001",
            "content": "Content",
        }

        with pytest.raises(KeyError):
            migrate_instruction(old_format)

    def test_migrate_missing_content(self):
        """Test migration fails with missing content"""
        old_format = {
            "id": "agent-001",
            "name": "Agent",
        }

        with pytest.raises(ValueError):
            migrate_instruction(old_format)

    def test_migrate_with_type_mapping(self):
        """Test type to category mapping"""
        test_cases = [
            ("core", InstructionCategory.CORE),
            ("behavioral", InstructionCategory.BEHAVIORAL),
            ("constraints", InstructionCategory.CONSTRAINTS),
            ("output-format", InstructionCategory.OUTPUT_FORMAT),
            ("output_format", InstructionCategory.OUTPUT_FORMAT),
        ]

        for old_type, expected_category in test_cases:
            old_format = {
                "id": "test-001",
                "name": "Test",
                "type": old_type,
                "content": "Content",
            }

            result = migrate_instruction(old_format)
            assert result.category == expected_category

    def test_migrate_with_default_values(self):
        """Test migration with minimal required fields"""
        old_format = {
            "id": "minimal-001",
            "name": "Minimal",
            "content": "Content",
        }

        result = migrate_instruction(old_format)

        assert result.metadata.priority == 5  # Default
        assert "claude" in result.metadata.applicability  # Default
        assert result.metadata.author == "migrated"  # Default author

    def test_migrate_with_invalid_priority(self):
        """Test migration normalizes invalid priority"""
        old_format = {
            "id": "bad-priority",
            "name": "Bad",
            "content": "Content",
            "priority": 15,  # Invalid, > 10
        }

        result = migrate_instruction(old_format)
        # Migration normalizes to default (5) if invalid
        assert result.metadata.priority == 5

    def test_migrate_with_dependencies(self):
        """Test migration preserves dependencies"""
        old_format = {
            "id": "with-deps",
            "name": "With Dependencies",
            "content": "Content",
            "dependencies": ["dep-001", "dep-002"],
        }

        result = migrate_instruction(old_format)

        assert len(result.metadata.depends_on) == 2
        assert "dep-001" in result.metadata.depends_on
        assert "dep-002" in result.metadata.depends_on

    def test_migrate_with_tags(self):
        """Test migration preserves tags"""
        old_format = {
            "id": "tagged",
            "name": "Tagged",
            "content": "Content",
            "tags": ["agent", "implementation", "coding"],
        }

        result = migrate_instruction(old_format)

        assert len(result.metadata.tags) == 3
        assert "agent" in result.metadata.tags

    def test_migrate_with_sections(self):
        """Test migration preserves sections"""
        old_format = {
            "id": "sections",
            "name": "With Sections",
            "content": "Main content",
            "sections": [
                {"heading": "Role", "content": "Role description"},
                {"heading": "Rules", "content": "Rules here"},
            ],
        }

        result = migrate_instruction(old_format)

        assert len(result.sections) == 2
        assert result.sections[0].heading == "Role"
        assert result.sections[1].heading == "Rules"

    def test_migrate_with_provider_variants(self):
        """Test migration preserves provider variants"""
        old_format = {
            "id": "variants",
            "name": "With Variants",
            "content": "Base content",
            "provider_variants": {
                "claude": {"content": "Claude specific"},
                "openai": "OpenAI specific",  # String format
            },
        }

        result = migrate_instruction(old_format)

        assert "claude" in result.provider_variants
        assert "openai" in result.provider_variants
        # String variants should be normalized to dict format
        assert isinstance(result.provider_variants["openai"], dict)

    def test_migrate_with_custom_author(self):
        """Test migration with custom author"""
        old_format = {
            "id": "authored",
            "name": "Authored",
            "content": "Content",
        }

        result = migrate_instruction(old_format, author="John Doe")

        assert result.metadata.author == "John Doe"

    def test_migrate_preserves_deprecated(self):
        """Test migration preserves deprecation info"""
        old_format = {
            "id": "deprecated-001",
            "name": "Old Feature",
            "content": "Content",
            "deprecated": True,
            "deprecation_notice": "Use new-feature instead",
        }

        result = migrate_instruction(old_format)

        assert result.metadata.deprecated is True
        assert result.metadata.deprecation_notice == "Use new-feature instead"


class TestMigrateFile:
    """Test migrate_file function"""

    def test_migrate_file_basic(self):
        """Test migrating a file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            output_file = Path(tmpdir) / "output.json"

            # Create input file
            old_format = {
                "id": "test-001",
                "name": "Test",
                "type": "core",
                "content": "Content",
                "priority": 5,
                "providers": ["claude"],
                "version": "1.0.0",
            }
            with open(input_file, "w") as f:
                json.dump(old_format, f)

            # Migrate
            result = migrate_file(input_file, output_file)

            assert result is True
            assert output_file.exists()

            # Verify output
            with open(output_file) as f:
                migrated = json.load(f)

            assert isinstance(migrated, list)
            assert len(migrated) == 1
            assert migrated[0]["id"] == "test-001"

    def test_migrate_file_array(self):
        """Test migrating file with array of instructions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            output_file = Path(tmpdir) / "output.json"

            # Create input file with array
            old_format = [
                {
                    "id": "test-001",
                    "name": "Test 1",
                    "type": "core",
                    "content": "Content 1",
                },
                {
                    "id": "test-002",
                    "name": "Test 2",
                    "type": "behavioral",
                    "content": "Content 2",
                },
            ]
            with open(input_file, "w") as f:
                json.dump(old_format, f)

            # Migrate
            migrate_file(input_file, output_file)

            # Verify output
            with open(output_file) as f:
                migrated = json.load(f)

            assert len(migrated) == 2
            assert migrated[0]["id"] == "test-001"
            assert migrated[1]["id"] == "test-002"

    def test_migrate_file_nonexistent_input(self):
        """Test migrating nonexistent input file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "nonexistent.json"
            output_file = Path(tmpdir) / "output.json"

            with pytest.raises(FileNotFoundError):
                migrate_file(input_file, output_file)

    def test_migrate_file_creates_output_directory(self):
        """Test that migrate_file creates output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            output_dir = Path(tmpdir) / "nested" / "output"
            output_file = output_dir / "output.json"

            # Create input
            with open(input_file, "w") as f:
                json.dump(
                    {
                        "id": "test-001",
                        "name": "Test",
                        "content": "Content",
                    },
                    f,
                )

            # Migrate
            migrate_file(input_file, output_file)

            # Verify output directory was created
            assert output_dir.exists()
            assert output_file.exists()


class TestMigrationTemplate:
    """Test create_migration_template function"""

    def test_create_migration_template(self):
        """Test creating migration template"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_file = Path(tmpdir) / "MIGRATION_TEMPLATE.md"

            create_migration_template(template_file)

            assert template_file.exists()

            # Verify content
            content = template_file.read_text()
            assert "Old Format" in content
            assert "New Format" in content
            assert "Migration Steps" in content

    def test_create_migration_template_creates_directory(self):
        """Test that template creation creates parent directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_file = Path(tmpdir) / "nested" / "dir" / "template.md"

            create_migration_template(template_file)

            assert template_file.exists()
            assert template_file.parent.exists()


class TestMigrationIntegration:
    """Integration tests for migration"""

    def test_end_to_end_migration(self):
        """Test complete migration workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create old format files
            old_dir = Path(tmpdir) / "old"
            old_dir.mkdir()

            for i in range(3):
                file = old_dir / f"instr-{i:03d}.json"
                old_format = {
                    "id": f"instr-{i:03d}",
                    "name": f"Instruction {i}",
                    "type": "core",
                    "content": f"Content {i}",
                    "priority": 5 + i,
                    "providers": ["claude"],
                }
                with open(file, "w") as f:
                    json.dump(old_format, f)

            # Migrate all files
            new_dir = Path(tmpdir) / "new"
            new_dir.mkdir()

            for old_file in old_dir.glob("*.json"):
                new_file = new_dir / old_file.name
                migrate_file(old_file, new_file)

            # Verify migration
            migrated_files = list(new_dir.glob("*.json"))
            assert len(migrated_files) == 3

            # Verify content
            for new_file in migrated_files:
                with open(new_file) as f:
                    migrated = json.load(f)

                assert isinstance(migrated, list)
                assert len(migrated) == 1
                assert "id" in migrated[0]
                assert "metadata" in migrated[0]

    def test_migration_preserves_data_integrity(self):
        """Test that migration preserves all data"""
        old_format = {
            "id": "comprehensive",
            "name": "Comprehensive Test",
            "type": "behavioral",
            "content": "Full content with all features",
            "priority": 9,
            "providers": ["claude", "openai", "gemini"],
            "version": "2.0.0",
            "description": "Detailed description",
            "deprecated": False,
            "tags": ["test", "comprehensive"],
            "dependencies": ["dep-001"],
        }

        result = migrate_instruction(old_format)

        # Verify all data is preserved
        assert result.id == "comprehensive"
        assert result.name == "Comprehensive Test"
        assert result.category == InstructionCategory.BEHAVIORAL
        assert result.content == "Full content with all features"
        assert result.metadata.priority == 9
        assert len(result.metadata.applicability) == 3
        assert result.metadata.version == "2.0.0"
        assert result.metadata.description == "Detailed description"
        assert result.metadata.deprecated is False
        assert len(result.metadata.tags) == 2
        assert len(result.metadata.depends_on) == 1
